"""BIP32 xpub (extended public key) address derivation.

Implements HD wallet child address derivation from an xpub key without
requiring the private key. Derives sequential receive addresses at path
m/0/index (external chain) following BIP44 convention.

Pure Python — stdlib only (no third-party dependencies).

Supports:
  - Base58Check xpub decoding
  - BIP32 public child key derivation (non-hardened only)
  - secp256k1 elliptic curve point operations
  - P2PKH (1...) address generation
"""

from __future__ import annotations

import hashlib
import hmac
import struct
from dataclasses import dataclass

# ─── secp256k1 curve parameters ──────────────────────────────────────────────

# Prime field
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
# Curve order
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
# Generator point
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (Gx, Gy)

# Base58 alphabet
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


# ─── Elliptic curve arithmetic on secp256k1 ──────────────────────────────────

def _modinv(a: int, m: int) -> int:
    """Modular inverse using extended Euclidean algorithm."""
    if a < 0:
        a = a % m
    g, x, _ = _extended_gcd(a, m)
    if g != 1:
        raise ValueError("No modular inverse")
    return x % m


def _extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    if a == 0:
        return b, 0, 1
    g, x, y = _extended_gcd(b % a, a)
    return g, y - (b // a) * x, x


def point_add(p1: tuple[int, int] | None, p2: tuple[int, int] | None) -> tuple[int, int] | None:
    """Add two points on secp256k1. None represents the point at infinity."""
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2

    if x1 == x2 and y1 != y2:
        return None  # Point at infinity

    if x1 == x2 and y1 == y2:
        # Point doubling
        lam = (3 * x1 * x1 * _modinv(2 * y1, P)) % P
    else:
        # Point addition
        lam = ((y2 - y1) * _modinv(x2 - x1, P)) % P

    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


def point_multiply(k: int, point: tuple[int, int] | None) -> tuple[int, int] | None:
    """Scalar multiplication using double-and-add."""
    result: tuple[int, int] | None = None
    addend = point
    while k > 0:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result


# ─── Key serialization helpers ───────────────────────────────────────────────

def _compress_pubkey(x: int, y: int) -> bytes:
    """Compress a public key point to 33 bytes."""
    prefix = b'\x02' if y % 2 == 0 else b'\x03'
    return prefix + x.to_bytes(32, 'big')


def _decompress_pubkey(data: bytes) -> tuple[int, int]:
    """Decompress a 33-byte compressed public key to (x, y)."""
    if len(data) != 33:
        raise ValueError(f"Invalid compressed pubkey length: {len(data)}")
    prefix = data[0]
    x = int.from_bytes(data[1:], 'big')

    # y² = x³ + 7 (mod P)
    y_sq = (pow(x, 3, P) + 7) % P
    y = pow(y_sq, (P + 1) // 4, P)

    # Verify
    if pow(y, 2, P) != y_sq:
        raise ValueError("Invalid point: not on curve")

    # Choose correct y based on prefix
    if prefix == 0x02 and y % 2 != 0:
        y = P - y
    elif prefix == 0x03 and y % 2 == 0:
        y = P - y
    elif prefix not in (0x02, 0x03):
        raise ValueError(f"Invalid pubkey prefix: 0x{prefix:02x}")

    return (x, y)


def _parse_pubkey_bytes(data: bytes) -> tuple[int, int]:
    """Parse a public key from bytes (compressed or uncompressed)."""
    if len(data) == 33:
        return _decompress_pubkey(data)
    elif len(data) == 65 and data[0] == 0x04:
        x = int.from_bytes(data[1:33], 'big')
        y = int.from_bytes(data[33:], 'big')
        return (x, y)
    else:
        raise ValueError(f"Invalid public key format (length={len(data)})")


# ─── Base58Check ─────────────────────────────────────────────────────────────

def _base58_decode(s: str) -> bytes:
    """Decode a Base58Check string to raw bytes (without checksum)."""
    num = 0
    for char in s:
        idx = BASE58_ALPHABET.find(char)
        if idx < 0:
            raise ValueError(f"Invalid Base58 character: '{char}'")
        num = num * 58 + idx

    # Convert to bytes — determine length from the number
    byte_length = (num.bit_length() + 7) // 8
    raw = num.to_bytes(byte_length, 'big') if num > 0 else b''

    # Count leading '1's (zero bytes)
    pad = 0
    for c in s:
        if c == '1':
            pad += 1
        else:
            break
    full = b'\x00' * pad + raw

    # Verify checksum (last 4 bytes)
    if len(full) < 5:
        raise ValueError("Base58Check data too short")
    payload, checksum = full[:-4], full[-4:]
    check = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    if check != checksum:
        raise ValueError("Base58Check checksum mismatch")

    return payload


def _base58check_encode(payload: bytes) -> str:
    """Encode bytes with Base58Check (adds 4-byte checksum)."""
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    full = payload + checksum

    # Count leading zero bytes
    pad = 0
    for b in full:
        if b == 0:
            pad += 1
        else:
            break

    num = int.from_bytes(full, 'big')
    result: list[str] = []
    while num > 0:
        num, rem = divmod(num, 58)
        result.append(BASE58_ALPHABET[rem])

    return '1' * pad + ''.join(reversed(result))


# ─── Hash helpers ────────────────────────────────────────────────────────────

def _hash160(data: bytes) -> bytes:
    """RIPEMD-160(SHA-256(data)) — standard Bitcoin hash160."""
    sha = hashlib.sha256(data).digest()
    try:
        ripemd = hashlib.new('ripemd160', sha).digest()
    except ValueError:
        # Fallback: pure Python RIPEMD-160 if OpenSSL doesn't support it
        ripemd = _ripemd160_pure(sha)
    return ripemd


def _ripemd160_pure(data: bytes) -> bytes:
    """Minimal pure-Python RIPEMD-160 implementation (fallback)."""
    # Constants
    def _f(j, x, y, z):
        if j < 16: return x ^ y ^ z
        if j < 32: return (x & y) | (~x & z)
        if j < 48: return (x | ~y) ^ z
        if j < 64: return (x & z) | (y & ~z)
        return x ^ (y | ~z)

    def _k_left(j):
        if j < 16: return 0x00000000
        if j < 32: return 0x5A827999
        if j < 48: return 0x6ED9EBA1
        if j < 64: return 0x8F1BBCDC
        return 0xA953FD4E

    def _k_right(j):
        if j < 16: return 0x50A28BE6
        if j < 32: return 0x5C4DD124
        if j < 48: return 0x6D703EF3
        if j < 64: return 0x7A6D76E9
        return 0x00000000

    RL = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
          7,4,13,1,10,6,15,3,12,0,9,5,2,14,11,8,
          3,10,14,4,9,15,8,1,2,7,0,6,13,11,5,12,
          1,9,11,10,0,8,12,4,13,3,7,15,14,5,6,2,
          4,0,5,9,7,12,2,10,14,1,3,8,11,6,15,13]
    RR = [5,14,7,0,9,2,11,4,13,6,15,8,1,10,3,12,
          6,11,3,7,0,13,5,10,14,15,8,12,4,9,1,2,
          15,5,1,3,7,14,6,9,11,8,12,2,10,0,4,13,
          8,6,4,1,3,11,15,0,5,12,2,13,9,7,10,14,
          12,15,10,4,1,5,8,7,6,2,13,14,0,3,9,11]
    SL = [11,14,15,12,5,8,7,9,11,13,14,15,6,7,9,8,
          7,6,8,13,11,9,7,15,7,12,15,9,11,7,13,12,
          11,13,6,7,14,9,13,15,14,8,13,6,5,12,7,5,
          11,12,14,15,14,15,9,8,9,14,5,6,8,6,5,12,
          9,15,5,11,6,8,13,12,5,12,13,14,11,8,5,6]
    SR = [8,9,9,11,13,15,15,5,7,7,8,11,14,14,12,6,
          9,13,15,7,12,8,9,11,7,7,12,7,6,15,13,11,
          9,7,15,11,8,6,6,14,12,13,5,14,13,13,7,5,
          15,5,8,11,14,14,6,14,6,9,12,9,12,5,15,8,
          8,5,12,9,12,5,14,6,8,13,6,5,15,13,11,11]

    MASK = 0xFFFFFFFF

    def _rotl(x, n):
        return ((x << n) | (x >> (32 - n))) & MASK

    # Padding
    msg = bytearray(data)
    ml = len(data) * 8
    msg.append(0x80)
    while len(msg) % 64 != 56:
        msg.append(0x00)
    msg += struct.pack('<Q', ml)

    h0, h1, h2, h3, h4 = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0

    for i in range(0, len(msg), 64):
        X = [int.from_bytes(msg[i+j*4:i+j*4+4], 'little') for j in range(16)]

        al, bl, cl, dl, el = h0, h1, h2, h3, h4
        ar, br, cr, dr, er = h0, h1, h2, h3, h4

        for j in range(80):
            t = (_rotl((al + _f(j, bl, cl, dl) + X[RL[j]] + _k_left(j)) & MASK, SL[j]) + el) & MASK
            al = el; el = dl; dl = _rotl(cl, 10); cl = bl; bl = t

            t = (_rotl((ar + _f(79-j, br, cr, dr) + X[RR[j]] + _k_right(j)) & MASK, SR[j]) + er) & MASK
            ar = er; er = dr; dr = _rotl(cr, 10); cr = br; br = t

        t = (h1 + cl + dr) & MASK
        h1 = (h2 + dl + er) & MASK
        h2 = (h3 + el + ar) & MASK
        h3 = (h4 + al + br) & MASK
        h4 = (h0 + bl + cr) & MASK
        h0 = t

    return struct.pack('<5I', h0, h1, h2, h3, h4)


# ─── BIP32 Extended Public Key ───────────────────────────────────────────────

@dataclass
class ExtendedPubKey:
    """Parsed BIP32 extended public key."""
    version: bytes          # 4 bytes (0x0488B21E for mainnet xpub)
    depth: int              # 1 byte
    fingerprint: bytes      # 4 bytes (parent fingerprint)
    child_number: int       # 4 bytes
    chain_code: bytes       # 32 bytes
    key_data: bytes         # 33 bytes (compressed public key)

    @property
    def point(self) -> tuple[int, int]:
        return _decompress_pubkey(self.key_data)

    def derive_child(self, index: int) -> "ExtendedPubKey":
        """Derive a non-hardened child public key (index < 2^31)."""
        if index >= 0x80000000:
            raise ValueError("Cannot derive hardened child from xpub")

        # Data = serP(key) || ser32(index)
        data = self.key_data + struct.pack('>I', index)

        # HMAC-SHA512
        I = hmac.new(self.chain_code, data, hashlib.sha512).digest()
        IL, IR = I[:32], I[32:]

        # IL as integer (parse256)
        il_int = int.from_bytes(IL, 'big')

        if il_int >= N:
            raise ValueError("Invalid child key: IL >= curve order")

        # Child public key = point(IL) + parent_key
        parent_point = self.point
        il_point = point_multiply(il_int, G)
        child_point = point_add(il_point, parent_point)

        if child_point is None:
            raise ValueError("Invalid child key: point at infinity")

        child_key = _compress_pubkey(child_point[0], child_point[1])

        # Parent fingerprint for child = hash160(parent_key)[:4]
        parent_fp = _hash160(self.key_data)[:4]

        return ExtendedPubKey(
            version=self.version,
            depth=self.depth + 1,
            fingerprint=parent_fp,
            child_number=index,
            chain_code=IR,
            key_data=child_key,
        )

    def to_address(self) -> str:
        """Generate P2PKH address from this key."""
        h = _hash160(self.key_data)
        # Version byte: 0x00 for mainnet
        payload = b'\x00' + h
        return _base58check_encode(payload)


def parse_xpub(xpub_str: str) -> ExtendedPubKey:
    """Parse a Base58Check-encoded xpub string into an ExtendedPubKey."""
    raw = _base58_decode(xpub_str)

    if len(raw) != 78:
        raise ValueError(f"Invalid xpub length: {len(raw)} (expected 78)")

    version = raw[0:4]
    depth = raw[4]
    fingerprint = raw[5:9]
    child_number = struct.unpack('>I', raw[9:13])[0]
    chain_code = raw[13:45]
    key_data = raw[45:78]

    # Validate version (mainnet xpub = 0x0488B21E, testnet tpub = 0x043587CF)
    valid_versions = (b'\x04\x88\xb2\x1e', b'\x04\x35\x87\xcf')
    if version not in valid_versions:
        raise ValueError(f"Unknown xpub version: {version.hex()}")

    # Validate key_data starts with 0x02 or 0x03 (compressed pubkey)
    if key_data[0] not in (0x02, 0x03):
        raise ValueError(f"Invalid pubkey prefix in xpub: 0x{key_data[0]:02x}")

    return ExtendedPubKey(
        version=version,
        depth=depth,
        fingerprint=fingerprint,
        child_number=child_number,
        chain_code=chain_code,
        key_data=key_data,
    )


# ─── Address derivation interface ────────────────────────────────────────────

def derive_addresses(xpub_str: str, count: int, start_index: int = 0,
                     chain: int = 0) -> list[dict]:
    """Derive `count` receive addresses from an xpub.

    Args:
        xpub_str: Base58Check-encoded xpub string.
        count: Number of addresses to derive.
        start_index: Starting child index (default 0).
        chain: 0 = external/receive, 1 = internal/change.

    Returns:
        List of dicts with {index, path, address, pubkey_hex}.
    """
    master = parse_xpub(xpub_str)

    # Derive the chain-level key (m/.../chain)
    chain_key = master.derive_child(chain)

    addresses: list[dict] = []
    for i in range(start_index, start_index + count):
        child = chain_key.derive_child(i)
        addr = child.to_address()
        addresses.append({
            "index": i,
            "path": f"m/{chain}/{i}",
            "address": addr,
            "pubkey_hex": child.key_data.hex(),
        })

    return addresses


def derive_single(xpub_str: str, index: int, chain: int = 0) -> dict:
    """Derive a single address at the given index.

    Returns:
        Dict with {index, path, address, pubkey_hex}.
    """
    results = derive_addresses(xpub_str, count=1, start_index=index, chain=chain)
    return results[0]


def validate_xpub(xpub_str: str) -> dict:
    """Validate an xpub string and return parsed metadata.

    Returns:
        Dict with {valid, version, depth, fingerprint, error}.
    """
    result = {
        "valid": False,
        "xpub": xpub_str[:12] + "..." if len(xpub_str) > 12 else xpub_str,
        "version": None,
        "depth": None,
        "fingerprint": None,
        "network": None,
        "error": None,
    }
    try:
        key = parse_xpub(xpub_str)
        result["valid"] = True
        result["version"] = key.version.hex()
        result["depth"] = key.depth
        result["fingerprint"] = key.fingerprint.hex()
        result["network"] = "mainnet" if key.version == b'\x04\x88\xb2\x1e' else "testnet"
    except Exception as e:
        result["error"] = str(e)
    return result
