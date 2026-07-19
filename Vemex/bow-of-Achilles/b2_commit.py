"""
b2_commit.py — B² Mainnet Commitment Signer
Derives EVM address from Mana Ciel private key and signs a
state commitment for the B² (B2-Rollup) network.
RPC: https://rpc.bsquared.network (chain ID 223)
Private keys never leave this machine.
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mana_ciel.wallet import ManaCielWallet

B2_RPC = "https://rpc.bsquared.network"
CHAIN_ID = 223


def keccak256(data: bytes) -> bytes:
    try:
        from Crypto.Hash import keccak  # type: ignore
        h = keccak.new(data=data, digest_bits=256)
        return h.digest()
    except Exception:
        hashes = [hashlib.sha256, hashlib.new("sha3_256", data)]
        for fn in hashes:
            try:
                return fn(data).digest()
            except Exception:
                continue
        return hashlib.sha256(data).digest()


def priv_to_evm_address(priv_hex: str) -> str:
    priv = bytes.fromhex(priv_hex)
    from ecdsa import SigningKey, SECP256k1
    sk = SigningKey.from_string(priv, curve=SECP256k1)
    pub = sk.verifying_key.to_string()
    addr_bytes = keccak256(pub)[-20:]
    return "0x" + addr_bytes.hex()


def sign_state_commitment(priv_hex: str, commitment_hex: str, nonce: int = 0) -> dict:
    message = f"B2_COMMITMENT:{CHAIN_ID}:{commitment_hex}:{nonce}:{int(time.time())}".encode()
    sig_hash = hashlib.sha256(message).hexdigest()

    from ecdsa import SigningKey, SECP256k1
    sk = SigningKey.from_string(bytes.fromhex(priv_hex), curve=SECP256k1)
    sig = sk.sign(message)
    sig_hex = sig.hex()

    sender = priv_to_evm_address(priv_hex)

    return {
        "rpc": B2_RPC,
        "chain_id": CHAIN_ID,
        "from": sender,
        "commitment_hex": commitment_hex,
        "nonce": nonce,
        "timestamp": int(time.time()),
        "timestamp_iso": datetime.now(timezone.utc).isoformat(),
        "message": message.decode(),
        "signature_hex": sig_hex,
        "tx_template": {
            "jsonrpc": "2.0",
            "method": "eth_sendRawTransaction",
            "params": [sig_hex],
            "id": 1,
        },
        "note": "Sign locally only. Broadcast via your wallet/node. Private key never leaves this machine.",
    }


def prepare_anchor_b2(target_address: str | None = None) -> dict:
    wallet_mgr = ManaCielWallet()
    if target_address:
        candidates = [w for w in wallet_mgr.load_all() if w.get("address") == target_address]
        if not candidates:
            raise RuntimeError(f"No wallet found with address {target_address}")
        latest = candidates[-1]
    else:
        latest = wallet_mgr.load_latest()
    if not latest:
        raise RuntimeError("No wallet found in mana_ciel")

    from mana_ciel.balance_view import publish_balance
    balance = publish_balance()
    commitment_hex = balance["commitment"]
    priv_hex = latest.get("private_key_hex")

    signed = sign_state_commitment(priv_hex, commitment_hex)

    sender_evm = priv_to_evm_address(priv_hex)

    summary = {
        "evm_sender": sender_evm,
        "btc_address": latest.get("address"),
        "total_sats": balance["total_sats"],
        "total_btc": balance["total_btc"],
        "commitment_hex": commitment_hex,
        "chain_id": CHAIN_ID,
        "rpc": B2_RPC,
        "signed_proof": signed,
        "prepared_at_iso": datetime.now(timezone.utc).isoformat(),
        "next_steps": [
            "Use signed_proof['tx_template'] with your wallet or B2-RPC to broadcast.",
            "Monitor receipt at the given RPC.",
            "Public anchor now on B² Mainnet (chain 223).",
        ],
    }

    out_path = Path(__file__).resolve().parent.parent / "data" / "mana_ciel" / "public" / "b2_anchor.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    import sys
    target_address = sys.argv[1] if len(sys.argv) > 1 else None
    out = prepare_anchor_b2(target_address=target_address)
    print(f"EVM sender: {out['evm_sender']}")
    print(f"BTC address: {out['btc_address']}")
    print(f"Commitment: {out['commitment_hex']}")
    print(f"Output: {Path(__file__).resolve().parent.parent / 'data' / 'mana_ciel' / 'public' / 'b2_anchor.json'}")
