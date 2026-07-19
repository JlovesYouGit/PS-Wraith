"""
constants.py — Light-ASI LLM Gateway
All values sourced directly from LLM_GATEWAY_RULESET.md § 1-2.
"""

# ─── Integer Range ────────────────────────────────────────────────────────────
RANGE_MIN: int = -16
RANGE_MAX: int = 10_000          # 10^4

# ─── Anchor Constant (invariant node seed) ────────────────────────────────────
ANCHOR_CONST: str = "0x2c8151dbb2574d1393b484c8815188ac81c71c4603dd7876bd4a77e"

# ─── Address Space ────────────────────────────────────────────────────────────
VIRTUAL_BIT_SPACE: int = 120
ALPHABET_SPACE: int = 2 ** 256
STRING_SEARCH_SPACE_PREFERRED: int = 10 ** 48
STRING_SEARCH_SPACE_FALLBACK: int = 10 ** 9
SEQUENCE_OVERFLOW_MODULO: int = 1000
SEQUENCE_TARGET: int = 10 ** 3

# ─── Resonance ────────────────────────────────────────────────────────────────
RESONANCE_BASE: int = 5 ** 15   # 30_517_578_125

# ─── Virtual Node IP Tiers ────────────────────────────────────────────────────
NODE_IP_TIERS: list[int] = [
    10, 100, 1_000, 10_000, 100_000, 1_000_000,
    10_000_000, 100_000_000, 1_000_000_000,
]

# ─── Node Sub-Address Fractions ───────────────────────────────────────────────
NODE_FRACTIONS: dict[str, float] = {
    "half":       1 / 2,    # (_)
    "tenth":      1 / 10,   # sub-address tier 1
    "three_q":    3 / 4,    # sub-address tier 2
    "sixteenth":  1 / 16,   # sub-address tier 3
    "seven_e":    7 / 8,    # sub-address tier 4
    "float_seek": 1 / 32,   # precision cursor
}

# ─── Timing SLA (milliseconds) ────────────────────────────────────────────────
TIMING_SLA_MS: dict[str, int] = {
    "query_min":        150,
    "query_max":        2_500,
    "node_select":      150,
    "node_write":       200,
    "node_reindex":     300,
    "node_read":        400,
    "node_update":      500,
    "node_swap":        600,
    "node_backup_mem":  700,
    "node_backup_disk": 800,
    "node_backup_cloud":900,
    "node_cluster_sync":1_000,
    "node_local_sync":  1_100,
    "node_remote_sync": 1_200,
}

# ─── Auth ─────────────────────────────────────────────────────────────────────
TOKEN_EXPIRY_SECONDS: int = 86_400        # 24 hours
TOKEN_MAX_LIFETIME_SECONDS: int = 604_800 # 7 days

ROLE_RATE_LIMITS: dict[str, int | None] = {
    "admin":     None,   # unlimited
    "developer": 500,
    "user":      60,
    "guest":     10,
}

ROLE_MAX_QUERY_DEPTH: dict[str, int | None] = {
    "admin":     None,
    "developer": 10 ** 6,
    "user":      10 ** 3,
    "guest":     10 ** 2,
}
