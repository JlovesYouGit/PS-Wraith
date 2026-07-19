import hashlib
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any

# Wire in SeedGate xpub derivation
_SEEDGATE_PYTHON = Path(__file__).resolve().parent.parent / "SeedGate" / "python"
if str(_SEEDGATE_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SEEDGATE_PYTHON))


BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def base58_decode(address: str) -> bytes:
    num = 0
    for char in address:
        if char not in BASE58_ALPHABET:
            raise ValueError(f"Invalid Base58 character: '{char}'")
        num = num * 58 + BASE58_ALPHABET.index(char)

    result = num.to_bytes(25, byteorder="big")
    pad_size = 0
    for char in address:
        if char == "1":
            pad_size += 1
        else:
            break

    return b"\x00" * pad_size + result.lstrip(b"\x00")


def validate_p2pkh_address(address: str) -> dict[str, Any]:
    result = {
        "address": address,
        "valid": False,
        "encoding": "Base58",
        "type": "P2PKH",
        "length": len(address),
        "zero_count": address.count("0"),
        "error": None,
    }

    if len(address) < 25 or len(address) > 34:
        result["error"] = f"Invalid length: {len(address)} (expected 25-34)"
        return result

    if address[0] not in ("1", "m", "n"):
        result["error"] = f"Invalid prefix '{address[0]}' for P2PKH address"
        return result

    for char in address:
        if char not in BASE58_ALPHABET:
            result["error"] = f"Invalid Base58 character: '{char}'"
            return result

    try:
        decoded = base58_decode(address)
        if len(decoded) != 25:
            result["error"] = "Decoded address is not 25 bytes"
            return result

        payload = decoded[:21]
        checksum = decoded[21:]

        hash1 = hashlib.sha256(payload).digest()
        hash2 = hashlib.sha256(hash1).digest()
        expected_checksum = hash2[:4]

        if checksum != expected_checksum:
            result["error"] = "Checksum verification failed"
            return result

    except Exception as e:
        result["error"] = f"Decode error: {str(e)}"
        return result

    result["valid"] = True
    return result


def check_balance(address: str) -> dict[str, Any]:
    balance_data = {
        "address": address,
        "success": False,
        "balance_satoshi": 0,
        "balance_btc": 0.0,
        "confirmed_satoshi": 0,
        "unconfirmed_satoshi": 0,
        "total_received_satoshi": 0,
        "total_sent_satoshi": 0,
        "tx_count": 0,
        "error": None,
    }

    try:
        url = f"https://blockstream.info/api/address/{address}"
        req = urllib.request.Request(url, headers={"User-Agent": "virtual-probe-X/1.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())

        chain_stats = data.get("chain_stats", {})
        mempool_stats = data.get("mempool_stats", {})

        funded = chain_stats.get("funded_txo_sum", 0)
        spent = chain_stats.get("spent_txo_sum", 0)
        mempool_funded = mempool_stats.get("funded_txo_sum", 0)
        mempool_spent = mempool_stats.get("spent_txo_sum", 0)

        confirmed_balance = funded - spent
        unconfirmed_balance = mempool_funded - mempool_spent
        total_balance = confirmed_balance + unconfirmed_balance

        balance_data["success"] = True
        balance_data["balance_satoshi"] = total_balance
        balance_data["balance_btc"] = total_balance / 100_000_000
        balance_data["confirmed_satoshi"] = confirmed_balance
        balance_data["unconfirmed_satoshi"] = unconfirmed_balance
        balance_data["total_received_satoshi"] = funded
        balance_data["total_sent_satoshi"] = spent
        balance_data["tx_count"] = chain_stats.get("tx_count", 0)

    except urllib.error.HTTPError as e:
        balance_data["error"] = f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        balance_data["error"] = f"Network error: {str(e.reason)}"
    except Exception as e:
        balance_data["error"] = f"Error: {str(e)}"

    return balance_data


# ─── .env Loader ─────────────────────────────────────────────────────────────

def _load_env() -> dict[str, str]:
    """Load .env from workspace root."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    env_vars: dict[str, str] = {}
    if not env_path.is_file():
        return env_vars
    try:
        with env_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    if key:
                        env_vars[key] = value
                        os.environ.setdefault(key, value)
    except OSError:
        pass
    return env_vars


# ─── Mainnet Cast ────────────────────────────────────────────────────────────

def cast_to_xpub(sender: str | None = None,
                 xpub: str | None = None,
                 btc_amount: float | None = None,
                 derivation_count: int = 1,
                 start_index: int = 0) -> dict[str, Any]:
    """Cast BTC value from sender (ADR) to xpub-derived addresses (ADR2).

    Loads ADR, ADR2, BTC_AMOUNT from .env if not provided.
    Validates sender, derives destination(s) from xpub, checks mainnet
    balance, and produces a routing cast record.

    Args:
        sender: Sender P2PKH address (defaults to ADR from .env)
        xpub: Extended public key (defaults to ADR2 from .env)
        btc_amount: Amount in BTC (defaults to BTC_AMOUNT from .env)
        derivation_count: Number of destination addresses to derive
        start_index: Starting derivation index (m/0/<index>)

    Returns:
        Cast record with validation, balance check, and routing details.
    """
    env = _load_env()

    # Resolve parameters from .env
    sender = sender or env.get("ADR") or os.getenv("ADR")
    xpub = xpub or env.get("ADR2") or os.getenv("ADR2")
    if btc_amount is None:
        raw_amt = env.get("BTC_AMOUNT") or os.getenv("BTC_AMOUNT")
        btc_amount = float(raw_amt) if raw_amt else None

    cast_record: dict[str, Any] = {
        "timestamp": time.time(),
        "network": "mainnet",
        "status": "pending",
        "sender": sender,
        "xpub": (xpub[:20] + "...") if xpub and len(xpub) > 20 else xpub,
        "btc_amount": btc_amount,
        "satoshi_amount": int(btc_amount * 100_000_000) if btc_amount else 0,
        "derivation_count": derivation_count,
        "start_index": start_index,
        "sender_validation": None,
        "sender_balance": None,
        "destinations": [],
        "cast_hash": None,
        "error": None,
    }

    # ── Validate inputs ──
    if not sender:
        cast_record["status"] = "failed"
        cast_record["error"] = "No sender address (ADR not set in .env)"
        return cast_record

    if not xpub:
        cast_record["status"] = "failed"
        cast_record["error"] = "No xpub key (ADR2 not set in .env)"
        return cast_record

    if not btc_amount or btc_amount <= 0:
        cast_record["status"] = "failed"
        cast_record["error"] = "Invalid BTC amount (BTC_AMOUNT not set or <= 0)"
        return cast_record

    # ── Validate sender address ──
    sender_validation = validate_p2pkh_address(sender)
    cast_record["sender_validation"] = sender_validation
    if not sender_validation["valid"]:
        cast_record["status"] = "failed"
        cast_record["error"] = f"Sender address invalid: {sender_validation['error']}"
        return cast_record

    # ── Check sender balance on mainnet ──
    balance = check_balance(sender)
    cast_record["sender_balance"] = balance
    if not balance["success"]:
        cast_record["status"] = "failed"
        cast_record["error"] = f"Balance check failed: {balance['error']}"
        return cast_record

    available_btc = balance["balance_btc"]
    if available_btc < btc_amount:
        cast_record["status"] = "insufficient_funds"
        cast_record["error"] = (
            f"Insufficient balance: {available_btc:.8f} BTC available, "
            f"{btc_amount:.8f} BTC required"
        )
        return cast_record

    # ── Derive destination addresses from xpub ──
    try:
        from seed_sampler.xpub_derivation import derive_addresses, validate_xpub

        xpub_validation = validate_xpub(xpub)
        if not xpub_validation["valid"]:
            cast_record["status"] = "failed"
            cast_record["error"] = f"Invalid xpub: {xpub_validation['error']}"
            return cast_record

        destinations = derive_addresses(xpub, count=derivation_count,
                                        start_index=start_index, chain=0)
    except Exception as e:
        cast_record["status"] = "failed"
        cast_record["error"] = f"xpub derivation error: {e}"
        return cast_record

    # ── Build per-destination cast entries ──
    per_dest_amount = btc_amount / derivation_count
    per_dest_satoshi = int(per_dest_amount * 100_000_000)

    for dest in destinations:
        dest_entry = {
            "address": dest["address"],
            "derivation_path": dest["path"],
            "derivation_index": dest["index"],
            "pubkey_hex": dest["pubkey_hex"],
            "btc_amount": per_dest_amount,
            "satoshi_amount": per_dest_satoshi,
        }
        cast_record["destinations"].append(dest_entry)

    # ── Generate cast hash (deterministic fingerprint of this cast) ──
    cast_payload = json.dumps({
        "sender": sender,
        "destinations": [d["address"] for d in cast_record["destinations"]],
        "total_satoshi": cast_record["satoshi_amount"],
        "timestamp": cast_record["timestamp"],
    }, sort_keys=True)
    cast_record["cast_hash"] = hashlib.sha256(cast_payload.encode()).hexdigest()

    cast_record["status"] = "cast_ready"
    return cast_record


# ─── Transaction Completion (Sign + Broadcast) ───────────────────────────────

def _fetch_utxos(address: str) -> list[dict[str, Any]]:
    """Fetch confirmed UTXOs for an address from blockstream.info."""
    url = f"https://blockstream.info/api/address/{address}/utxo"
    req = urllib.request.Request(url, headers={"User-Agent": "virtual-probe-X/1.0"})
    with urllib.request.urlopen(req, timeout=15) as response:
        utxos = json.loads(response.read().decode())
    # Only confirmed UTXOs
    return [u for u in utxos if u.get("status", {}).get("confirmed", False)]


def _string_to_wif(key_string: str) -> str:
    """Convert an arbitrary string to a valid WIF private key.

    Flow: string → SHA-256 hex (32 bytes) → WIF encode (compressed, mainnet).
    """
    # String to hex bytes via SHA-256 hash
    key_hex = hashlib.sha256(key_string.encode('utf-8')).hexdigest()
    key_bytes = bytes.fromhex(key_hex)  # 32 bytes

    # WIF encode: 0x80 + key_bytes + 0x01 (compressed) + checksum
    payload = b'\x80' + key_bytes + b'\x01'
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    full = payload + checksum

    # Base58 encode
    pad = 0
    for b in full:
        if b == 0:
            pad += 1
        else:
            break
    num = int.from_bytes(full, 'big')
    result = []
    while num > 0:
        num, rem = divmod(num, 58)
        result.append(BASE58_ALPHABET[rem])
    return '1' * pad + ''.join(reversed(result))


def _is_valid_wif(s: str) -> bool:
    """Check if a string is a valid WIF private key."""
    if not s:
        return False
    # WIF starts with 5 (uncompressed) or K/L (compressed) for mainnet
    if s[0] not in ('5', 'K', 'L'):
        return False
    if len(s) < 51 or len(s) > 52:
        return False
    try:
        _base58check_decode_raw(s)
        return True
    except (ValueError, Exception):
        return False


def _decode_wif(wif: str) -> tuple[bytes, bool]:
    """Decode a WIF private key. Returns (32-byte key, compressed)."""
    raw = _base58check_decode_raw(wif)
    if raw[0] == 0x80:  # mainnet
        key_bytes = raw[1:]
    elif raw[0] == 0xEF:  # testnet
        key_bytes = raw[1:]
    else:
        raise ValueError(f"Unknown WIF version: 0x{raw[0]:02x}")

    if len(key_bytes) == 33 and key_bytes[-1] == 0x01:
        return key_bytes[:32], True  # compressed
    elif len(key_bytes) == 32:
        return key_bytes, False  # uncompressed
    else:
        raise ValueError(f"Invalid WIF key length: {len(key_bytes)}")


def _base58check_decode_raw(s: str) -> bytes:
    """Decode Base58Check to raw payload bytes."""
    num = 0
    for char in s:
        idx = BASE58_ALPHABET.find(char)
        if idx < 0:
            raise ValueError(f"Invalid Base58 character: '{char}'")
        num = num * 58 + idx

    byte_length = (num.bit_length() + 7) // 8
    raw = num.to_bytes(byte_length, 'big') if num > 0 else b''

    pad = 0
    for c in s:
        if c == '1':
            pad += 1
        else:
            break
    full = b'\x00' * pad + raw

    if len(full) < 5:
        raise ValueError("Data too short for Base58Check")
    payload, checksum = full[:-4], full[-4:]
    check = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    if check != checksum:
        raise ValueError("WIF checksum mismatch")
    return payload


def _privkey_to_pubkey(privkey: bytes, compressed: bool = True) -> bytes:
    """Derive public key from private key using secp256k1."""
    from seed_sampler.xpub_derivation import point_multiply, G, _compress_pubkey, P

    k = int.from_bytes(privkey, 'big')
    point = point_multiply(k, G)
    if point is None:
        raise ValueError("Invalid private key")

    if compressed:
        return _compress_pubkey(point[0], point[1])
    else:
        return b'\x04' + point[0].to_bytes(32, 'big') + point[1].to_bytes(32, 'big')


def _pubkey_to_address(pubkey: bytes) -> str:
    """Convert public key bytes to P2PKH address."""
    sha = hashlib.sha256(pubkey).digest()
    try:
        ripe = hashlib.new('ripemd160', sha).digest()
    except ValueError:
        from seed_sampler.xpub_derivation import _ripemd160_pure
        ripe = _ripemd160_pure(sha)
    payload = b'\x00' + ripe
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    full = payload + checksum
    # Base58 encode
    pad = 0
    for b in full:
        if b == 0:
            pad += 1
        else:
            break
    num = int.from_bytes(full, 'big')
    result = []
    while num > 0:
        num, rem = divmod(num, 58)
        result.append(BASE58_ALPHABET[rem])
    return '1' * pad + ''.join(reversed(result))


def _sign_input(privkey: bytes, sighash: bytes) -> bytes:
    """ECDSA sign a sighash with the private key (DER encoded + SIGHASH_ALL)."""
    from seed_sampler.xpub_derivation import N, G, point_multiply
    import secrets

    k_int = int.from_bytes(privkey, 'big')
    z = int.from_bytes(sighash, 'big')

    # RFC6979-like deterministic k (simplified)
    while True:
        k = int.from_bytes(secrets.token_bytes(32), 'big') % N
        if k == 0:
            continue
        R = point_multiply(k, G)
        if R is None:
            continue
        r = R[0] % N
        if r == 0:
            continue
        k_inv = pow(k, N - 2, N)
        s = (k_inv * (z + r * k_int)) % N
        if s == 0:
            continue
        # Low-S normalization (BIP62)
        if s > N // 2:
            s = N - s
        break

    # DER encode
    def _der_int(val: int) -> bytes:
        b = val.to_bytes(32, 'big').lstrip(b'\x00') or b'\x00'
        if b[0] & 0x80:
            b = b'\x00' + b
        return bytes([0x02, len(b)]) + b

    r_der = _der_int(r)
    s_der = _der_int(s)
    der_sig = bytes([0x30, len(r_der) + len(s_der)]) + r_der + s_der
    return der_sig + b'\x01'  # SIGHASH_ALL


def _build_raw_tx(privkey: bytes, compressed: bool,
                  utxos: list[dict], destinations: list[dict],
                  fee_satoshi: int) -> str:
    """Build and sign a raw Bitcoin transaction. Returns hex."""
    pubkey = _privkey_to_pubkey(privkey, compressed)
    sender_address = _pubkey_to_address(pubkey)

    # Select UTXOs (simple: use all until we have enough)
    total_needed = sum(d["satoshi_amount"] for d in destinations) + fee_satoshi
    selected: list[dict] = []
    total_in = 0
    for utxo in utxos:
        selected.append(utxo)
        total_in += utxo["value"]
        if total_in >= total_needed:
            break

    if total_in < total_needed:
        raise ValueError(f"Insufficient UTXOs: have {total_in}, need {total_needed}")

    change = total_in - total_needed

    # Build unsigned TX
    version = (1).to_bytes(4, 'little')
    n_inputs = _varint(len(selected))

    # Outputs: destinations + change
    outputs_data = []
    for dest in destinations:
        outputs_data.append((dest["satoshi_amount"], dest["address"]))
    if change > 546:  # dust threshold
        outputs_data.append((change, sender_address))

    n_outputs = _varint(len(outputs_data))
    locktime = (0).to_bytes(4, 'little')

    # For each input, sign with SIGHASH_ALL
    signed_inputs = []
    for i, utxo in enumerate(selected):
        # Build the sighash preimage
        preimage = version + n_inputs
        for j, u in enumerate(selected):
            txid = bytes.fromhex(u["txid"])[::-1]  # little-endian
            vout = u["vout"].to_bytes(4, 'little')
            if j == i:
                # scriptPubKey of the UTXO being signed
                script_pub = _p2pkh_script(pubkey)
                script_len = _varint(len(script_pub))
                preimage += txid + vout + script_len + script_pub + b'\xff\xff\xff\xff'
            else:
                preimage += txid + vout + b'\x00' + b'\xff\xff\xff\xff'

        preimage += n_outputs
        for amount, addr in outputs_data:
            preimage += amount.to_bytes(8, 'little')
            out_script = _p2pkh_script_from_address(addr)
            preimage += _varint(len(out_script)) + out_script
        preimage += locktime
        preimage += (1).to_bytes(4, 'little')  # SIGHASH_ALL

        sighash = hashlib.sha256(hashlib.sha256(preimage).digest()).digest()
        sig = _sign_input(privkey, sighash)

        # scriptSig = <sig> <pubkey>
        script_sig = bytes([len(sig)]) + sig + bytes([len(pubkey)]) + pubkey
        signed_inputs.append((utxo, script_sig))

    # Assemble final TX
    raw_tx = version + n_inputs
    for utxo, script_sig in signed_inputs:
        txid = bytes.fromhex(utxo["txid"])[::-1]
        vout = utxo["vout"].to_bytes(4, 'little')
        raw_tx += txid + vout + _varint(len(script_sig)) + script_sig + b'\xff\xff\xff\xff'

    raw_tx += n_outputs
    for amount, addr in outputs_data:
        raw_tx += amount.to_bytes(8, 'little')
        out_script = _p2pkh_script_from_address(addr)
        raw_tx += _varint(len(out_script)) + out_script
    raw_tx += locktime

    return raw_tx.hex()


def _varint(n: int) -> bytes:
    if n < 0xFD:
        return bytes([n])
    elif n <= 0xFFFF:
        return b'\xfd' + n.to_bytes(2, 'little')
    elif n <= 0xFFFFFFFF:
        return b'\xfe' + n.to_bytes(4, 'little')
    else:
        return b'\xff' + n.to_bytes(8, 'little')


def _p2pkh_script(pubkey: bytes) -> bytes:
    """Standard P2PKH scriptPubKey from pubkey bytes."""
    sha = hashlib.sha256(pubkey).digest()
    try:
        h160 = hashlib.new('ripemd160', sha).digest()
    except ValueError:
        from seed_sampler.xpub_derivation import _ripemd160_pure
        h160 = _ripemd160_pure(sha)
    # OP_DUP OP_HASH160 <20 bytes> OP_EQUALVERIFY OP_CHECKSIG
    return b'\x76\xa9\x14' + h160 + b'\x88\xac'


def _p2pkh_script_from_address(address: str) -> bytes:
    """P2PKH scriptPubKey from a Base58 address."""
    decoded = base58_decode(address)
    h160 = decoded[1:21]  # skip version byte
    return b'\x76\xa9\x14' + h160 + b'\x88\xac'


def _broadcast_tx(raw_hex: str) -> dict[str, Any]:
    """Broadcast a raw transaction to mainnet via blockstream.info."""
    url = "https://blockstream.info/api/tx"
    req = urllib.request.Request(
        url,
        data=raw_hex.encode(),
        headers={"Content-Type": "text/plain"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            txid = response.read().decode().strip()
            return {"success": True, "txid": txid}
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return {"success": False, "error": f"HTTP {e.code}: {body[:500]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def complete_cast(cast_record: dict[str, Any] | None = None,
                  private_key_wif: str | None = None,
                  fee_sat: int = 1000) -> dict[str, Any]:
    """Complete a cast by signing and broadcasting the transaction.

    If cast_record is None, runs cast_to_xpub() first.
    Loads KEY from .env if private_key_wif not provided.

    Returns updated cast_record with tx details.
    """
    env = _load_env()

    # Get or build the cast
    if cast_record is None:
        cast_record = cast_to_xpub()

    if cast_record.get("status") != "cast_ready":
        return cast_record  # Already failed upstream

    # Load private key
    wif = private_key_wif or env.get("KEY") or os.getenv("KEY") or ""
    wif = wif.strip()
    if not wif:
        cast_record["status"] = "incomplete"
        cast_record["error"] = "No private key (KEY not set in .env)"
        return cast_record

    # Auto-convert: if KEY is not valid WIF, convert string → hex → WIF
    if not _is_valid_wif(wif):
        original_key = wif
        wif = _string_to_wif(wif)
        cast_record["key_conversion"] = {
            "source": original_key,
            "hex": hashlib.sha256(original_key.encode('utf-8')).hexdigest(),
            "wif": wif,
        }

    try:
        privkey, compressed = _decode_wif(wif)
    except Exception as e:
        cast_record["status"] = "failed"
        cast_record["error"] = f"Invalid private key: {e}"
        return cast_record

    # KEY corresponds to ADR (sender signing key) - sender stays from .env
    pubkey = _privkey_to_pubkey(privkey, compressed)
    key_address = _pubkey_to_address(pubkey)
    cast_record["key_address"] = key_address

    # Fetch UTXOs
    try:
        utxos = _fetch_utxos(cast_record["sender"])
    except Exception as e:
        cast_record["status"] = "failed"
        cast_record["error"] = f"UTXO fetch failed: {e}"
        return cast_record

    if not utxos:
        cast_record["status"] = "failed"
        cast_record["error"] = "No confirmed UTXOs available"
        return cast_record

    # Build + sign raw transaction
    try:
        raw_hex = _build_raw_tx(
            privkey, compressed, utxos,
            cast_record["destinations"], fee_sat
        )
    except Exception as e:
        cast_record["status"] = "failed"
        cast_record["error"] = f"TX build error: {e}"
        return cast_record

    cast_record["raw_tx"] = raw_hex
    cast_record["fee_satoshi"] = fee_sat

    # Broadcast
    broadcast = _broadcast_tx(raw_hex)
    cast_record["broadcast"] = broadcast

    if broadcast["success"]:
        cast_record["status"] = "complete"
        cast_record["txid"] = broadcast["txid"]
    else:
        cast_record["status"] = "broadcast_failed"
        cast_record["error"] = broadcast["error"]

    return cast_record
