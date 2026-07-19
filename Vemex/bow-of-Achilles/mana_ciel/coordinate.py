"""
coordinate.py — Mana Ciel Synergy Coordinate System
Integer space from -16 to 1000. Maps to virtual node ID space.
"""

from engine.core.constants import RANGE_MIN, RANGE_MAX, ANCHOR_CONST, VIRTUAL_BIT_SPACE


class SynergyCoordinate:
    def __init__(self, value: int | None = None):
        if value is None:
            import random
            value = random.randint(RANGE_MIN, RANGE_MAX)
        self.value = self._clamp(value)

    def _clamp(self, v: int) -> int:
        return max(RANGE_MIN, min(v, RANGE_MAX))

    def to_dict(self) -> dict:
        import hashlib
        raw = f"{ANCHOR_CONST}:coord:{self.value}"
        h = hashlib.sha256(raw.encode()).hexdigest()
        return {
            "value": self.value,
            "min": RANGE_MIN,
            "max": RANGE_MAX,
            "hex": hex(self.value),
            "virtual_hash": h[:16],
            "virtual_bit_space": VIRTUAL_BIT_SPACE,
        }

    def is_valid(self) -> bool:
        return RANGE_MIN <= self.value <= RANGE_MAX

    def __repr__(self) -> str:
        return f"SynergyCoordinate(value={self.value})"
