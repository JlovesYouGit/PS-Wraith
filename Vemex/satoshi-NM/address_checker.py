"""
Address Checker - Base58 P2PKH Wallet Credential System
Validates wallet addresses and authenticates using credential keys.
Successful logins are saved to credentials.json.
"""

import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ─── Base58 Alphabet ───────────────────────────────────────────────────────────
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

CREDENTIALS_FILE = "credentials.json"
PRIVATE_KEYS_FILE = "private_keys.json"


# ─── Base58 Decode ─────────────────────────────────────────────────────────────
def base58_decode(address: str) -> bytes:
    """Decode a Base58 encoded string to bytes."""
    num = 0
    for char in address:
        if char not in BASE58_ALPHABET:
            raise ValueError(f"Invalid Base58 character: '{char}'")
        num = num * 58 + BASE58_ALPHABET.index(char)

    # Convert to bytes
    result = num.to_bytes(25, byteorder="big")

    # Count leading '1's (they represent leading zero bytes)
    pad_size = 0
    for char in address:
        if char == "1":
            pad_size += 1
        else:
            break

    return b"\x00" * pad_size + result.lstrip(b"\x00")


# ─── P2PKH Address Validation ─────────────────────────────────────────────────
def validate_p2pkh_address(address: str) -> dict:
    """
    Validate a Base58 P2PKH address.
    Returns validation result with details.
    """
    result = {
        "address": address,
        "valid": False,
        "encoding": "Base58",
        "type": "P2PKH",
        "length": len(address),
        "zero_count": address.count("0"),
        "error": None,
    }

    # Check length (P2PKH addresses are typically 25-34 characters)
    if len(address) < 25 or len(address) > 34:
        result["error"] = f"Invalid length: {len(address)} (expected 25-34)"
        return result

    # Check first character (1 for mainnet P2PKH, m/n for testnet)
    if address[0] not in ("1", "m", "n"):
        result["error"] = f"Invalid prefix '{address[0]}' for P2PKH address"
        return result

    # Validate Base58 characters
    for char in address:
        if char not in BASE58_ALPHABET:
            result["error"] = f"Invalid Base58 character: '{char}'"
            return result

    # Decode and verify checksum
    try:
        decoded = base58_decode(address)
        if len(decoded) != 25:
            result["error"] = "Decoded address is not 25 bytes"
            return result

        # Split payload and checksum
        payload = decoded[:21]
        checksum = decoded[21:]

        # Double SHA-256 checksum verification
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


# ─── Credential Key System ─────────────────────────────────────────────────────
def get_valid_credentials(address: str) -> list:
    """
    Generate valid credential keys based on address properties.

    Valid keys:
    - "NM" (2 chars)
    - "newton" (6 chars)
    - "newtooon" (8 chars)
    - Zero count as string (number of '0' characters in address)
    - Newton's Third Law sequence: "3" (third law number)
    - "action reaction" (Newton's 3rd law: equal and opposite)
    """
    zero_count = address.count("0")

    valid_keys = [
        "NM",                          # 2 characters
        "newton",                      # 6 characters
        "newtooon",                    # 8 characters
        str(zero_count),               # Match zero count in address
        "3",                           # Newton's Third Law number
        "action reaction",             # Newton's 3rd Law sequence
        "F=-F",                        # Newton's 3rd Law formula
    ]

    return valid_keys


def authenticate(credential: str, address: str) -> bool:
    """Check if the provided credential matches any valid key."""
    valid_keys = get_valid_credentials(address)
    return credential in valid_keys


# ─── JSON Storage ──────────────────────────────────────────────────────────────
def save_credential(address: str, credential_used: str, validation_result: dict):
    """Save successful login data to credentials.json."""
    login_data = {
        "timestamp": datetime.now().isoformat(),
        "address": address,
        "credential_used": credential_used,
        "credential_length": len(credential_used),
        "address_valid": validation_result["valid"],
        "encoding": validation_result["encoding"],
        "type": validation_result["type"],
        "address_length": validation_result["length"],
        "zero_count": validation_result["zero_count"],
    }

    # Load existing credentials or create new list
    credentials = []
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)
        except (json.JSONDecodeError, IOError):
            credentials = []

    credentials.append(login_data)

    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f, indent=2)

    # Save private key to separate JSON
    save_private_key(address, credential_used)

    return login_data


def save_private_key(address: str, credential_used: str):
    """Save the private key (credential) used to a separate private_keys.json."""
    key_entry = {
        "timestamp": datetime.now().isoformat(),
        "address": address,
        "private_key": credential_used,
        "key_length": len(credential_used),
    }

    keys = []
    if os.path.exists(PRIVATE_KEYS_FILE):
        try:
            with open(PRIVATE_KEYS_FILE, "r") as f:
                keys = json.load(f)
        except (json.JSONDecodeError, IOError):
            keys = []

    keys.append(key_entry)

    with open(PRIVATE_KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2)

    return key_entry


# ─── Network Balance Check ────────────────────────────────────────────────────
def check_balance(address: str, private_key: str) -> dict:
    """
    Query the Bitcoin network for address balance.
    Authenticates using the private key from private_keys.json.
    Uses Blockstream API (no API key required).
    """
    # Verify private key exists in stored keys
    if not verify_private_key(address, private_key):
        return {
            "success": False,
            "error": "Private key does not match stored credentials",
            "address": address,
        }

    print(f"\n  [NETWORK] Querying balance for: {address}")
    print(f"  [AUTH] Using private key: {'*' * (len(private_key) - 1)}{private_key[-1]}")

    balance_data = {
        "address": address,
        "private_key_used": private_key,
        "authenticated": True,
        "success": False,
        "balance_satoshi": 0,
        "balance_btc": 0.0,
        "total_received_satoshi": 0,
        "total_sent_satoshi": 0,
        "tx_count": 0,
        "error": None,
    }

    try:
        # Blockstream API - get address stats
        url = f"https://blockstream.info/api/address/{address}"
        req = urllib.request.Request(url, headers={"User-Agent": "AddressChecker/1.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())

        # Parse chain stats
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


def verify_private_key(address: str, private_key: str) -> bool:
    """Verify that the private key exists in private_keys.json for this address."""
    if not os.path.exists(PRIVATE_KEYS_FILE):
        return False

    try:
        with open(PRIVATE_KEYS_FILE, "r") as f:
            keys = json.load(f)
    except (json.JSONDecodeError, IOError):
        return False

    for entry in keys:
        if entry.get("address") == address and entry.get("private_key") == private_key:
            return True

    return False


def load_private_key(address: str) -> str:
    """Load the most recent private key for an address from private_keys.json."""
    if not os.path.exists(PRIVATE_KEYS_FILE):
        return None

    try:
        with open(PRIVATE_KEYS_FILE, "r") as f:
            keys = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    # Get the most recent key for this address
    for entry in reversed(keys):
        if entry.get("address") == address:
            return entry.get("private_key")

    return None


def display_balance(balance_data: dict):
    """Display balance information."""
    print("\n┌─ Account Balance ────────────────────────────────────────┐")
    print(f"│  Address:      {balance_data['address']}")
    print(f"│  Authenticated: ✓ YES")

    if balance_data["success"]:
        print(f"│  ─────────────────────────────────────────────────────── │")
        print(f"│  Balance:      {balance_data['balance_btc']:.8f} BTC")
        print(f"│               ({balance_data['balance_satoshi']:,} satoshi)")
        print(f"│  Confirmed:   {balance_data['confirmed_satoshi']:,} satoshi")
        print(f"│  Unconfirmed: {balance_data['unconfirmed_satoshi']:,} satoshi")
        print(f"│  ─────────────────────────────────────────────────────── │")
        print(f"│  Received:    {balance_data['total_received_satoshi']:,} satoshi")
        print(f"│  Sent:        {balance_data['total_sent_satoshi']:,} satoshi")
        print(f"│  TX Count:    {balance_data['tx_count']:,}")
    else:
        print(f"│  Error:        {balance_data['error']}")

    print("└──────────────────────────────────────────────────────────┘")


def save_balance_check(balance_data: dict):
    """Save balance check result to balance_history.json."""
    balance_file = "balance_history.json"
    entry = {
        "timestamp": datetime.now().isoformat(),
        **balance_data,
    }

    history = []
    if os.path.exists(balance_file):
        try:
            with open(balance_file, "r") as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []

    history.append(entry)

    with open(balance_file, "w") as f:
        json.dump(history, f, indent=2)

    print(f"  [SAVED] Balance data written to {balance_file}")
    return entry


# ─── Display ───────────────────────────────────────────────────────────────────
def display_banner():
    print("\n" + "=" * 60)
    print("   BASE58 P2PKH ADDRESS CHECKER & CREDENTIAL SYSTEM")
    print("=" * 60)


def display_validation(result: dict):
    print("\n┌─ Address Validation ─────────────────────────────────────┐")
    print(f"│  Address:    {result['address']}")
    print(f"│  Encoding:   {result['encoding']}")
    print(f"│  Type:       {result['type']}")
    print(f"│  Length:     {result['length']} chars")
    print(f"│  Zero count: {result['zero_count']}")
    print(f"│  Valid:      {'✓ YES' if result['valid'] else '✗ NO'}")
    if result["error"]:
        print(f"│  Error:      {result['error']}")
    print("└──────────────────────────────────────────────────────────┘")


def display_hints(address: str):
    zero_count = address.count("0")
    print("\n┌─ Credential Hints ───────────────────────────────────────┐")
    print("│  Valid keys (try one of these):                          │")
    print("│    • 'NM'              (2 chars)                         │")
    print("│    • 'newton'          (6 chars)                         │")
    print("│    • 'newtooon'        (8 chars)                         │")
    print(f"│    • '{zero_count}' (zero count in address = {zero_count})              │")
    print("│    • Newton's 3rd Law sequence                           │")
    print("└──────────────────────────────────────────────────────────┘")


# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    display_banner()

    # Load address from .env
    address = os.getenv("ADR")
    if not address:
        print("\n[ERROR] No address found. Set ADR in your .env file.")
        sys.exit(1)

    print(f"\n[INFO] Loaded address from .env: {address}")

    # Validate the address
    validation = validate_p2pkh_address(address)
    display_validation(validation)

    if not validation["valid"]:
        print("\n[WARNING] Address failed validation but you can still attempt login.")

    # Credential authentication loop
    max_attempts = 5
    attempts = 0

    display_hints(address)

    while attempts < max_attempts:
        attempts += 1
        print(f"\n[Attempt {attempts}/{max_attempts}]")
        credential = input("  Enter credential key: ").strip()

        if not credential:
            print("  ⚠ Empty input. Try again.")
            continue

        if authenticate(credential, address):
            print("\n  ✓ CREDENTIAL ACCEPTED - Access Granted!")
            print(f"    Key used: '{credential}' ({len(credential)} chars)")

            # Save to JSON
            saved = save_credential(address, credential, validation)
            print(f"\n  [SAVED] Login data written to {CREDENTIALS_FILE}")
            print(f"  [SAVED] Private key written to {PRIVATE_KEYS_FILE}")
            print(f"    Timestamp: {saved['timestamp']}")
            print(f"    Address:   {saved['address']}")
            print(f"    Key:       {saved['credential_used']}")

            print("\n" + "=" * 60)
            print("   SESSION AUTHENTICATED SUCCESSFULLY")
            print("=" * 60)

            # Check balance using private key from credentials
            print("\n  [INFO] Checking account balance from network...")
            private_key = load_private_key(address)
            if private_key:
                balance = check_balance(address, private_key)
                display_balance(balance)
                if balance["success"]:
                    save_balance_check(balance)
            else:
                print("  [ERROR] No private key found for balance check.")

            print()
            return

        else:
            zero_count = address.count("0")
            print(f"  ✗ Invalid credential.")
            print(f"    Hint: Try matching zero count ({zero_count}) or Newton's Third Law.")

    print("\n[LOCKED] Maximum attempts reached. Access denied.")
    sys.exit(1)


if __name__ == "__main__":
    main()
