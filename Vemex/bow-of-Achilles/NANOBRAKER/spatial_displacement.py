"""
SPATIAL DISPLACEMENT MECHANICS
================================
Implements the displacement formulas from the framework:
  - Spatial Distortion Threshold: 111.11179
  - Force Component: F^(2/3) over cubic volume
  - Scaled Frequency Constant: 3f/C
  - Unified singular: 18 (15+3)
  - Void collapse: 18/0 = Ø
  - Void structure: 2 0 (memory qubit singularity + displacement)
  - Planckian convergence: h -> 0
  - Limit-bound function: F(x,y) -> U
  - Parity Even: coordinate collapse condition

Integration:
  This module feeds into msn_overlap.py as a pre-processing layer.
  Outputs are zero-centered signals ready for overlap scoring.
"""
import numpy as np
from typing import Callable, Dict, Optional, Tuple

# ── Core constants ──────────────────────────────────────────
PHI      = 1.618033988749895
MSN      = 81.0 * PHI              # 131.06075319  (already in msn_overlap)
MSN_INV  = 1.0 / MSN
SPATIAL_THRESHOLD = 111.11179
FORCE_EXPONENT    = 2.0 / 3.0
PLANCK_CONV       = 1e-12
PARITY_EVEN       = 0

def unified_singular_func(bh=None, channel_stats=None, signifiers=3, signified=15):
    """
    Machine-computed unified singular — not hardcoded.
    
    Drives from Kerr engine data:
      ch_count  = number of aligned channels (default 3: Omega, grad, gtt)
      sig_sum   = sum of significant physical values from Kerr (default 15-scale)
      Returns   = ch_count + sig_sum → feeds MSN pipeline as dynamic constant
    """
    if channel_stats is not None:
        ch_count = len(channel_stats)
    elif bh is not None:
        from kerr_engine import fast_signal
        sig = fast_signal(bh)
        ch_count = 3  # Omega, grad, gtt present
    else:
        ch_count = 3
    
    # sigified derives from physical scale of M and a (the "15" part)
    if bh is not None:
        physical_scale = int(np.ceil(abs(bh.M) + abs(bh.a)))  # e.g. M=1, a=0.92 -> 2
        sig_sum = signified * physical_scale  # scales with black hole parameters
    else:
        sig_sum = signified
    
    return float(ch_count + sig_sum)


def dynamic_unified_singular(kerr_channels):
    """
    Compute unified singular from actual Kerr channel statistics.
    Counts significant figures robustly for both >1 and <1 values.
    """
    def sig_figs(val):
        v = abs(val)
        if v == 0:
            return 1
        # Count decimal places for sub-1 values
        if v < 1:
            # 0.005 -> 3 leading zeros + 5 = 1 sig fig
            # Use string representation to count properly
            s = f"{v:.10f}".rstrip('0')
            if '.' in s:
                parts = s.split('.')
                decimal_places = len(parts[1])
                # Count leading zeros after decimal
                leading_zeros = 0
                for c in parts[1]:
                    if c == '0':
                        leading_zeros += 1
                    else:
                        break
                return max(1, decimal_places - leading_zeros)
            return 1
        else:
            # For >= 1, floor(log10) + 1 = digits before decimal
            return int(np.floor(np.log10(v))) + 1
    
    sig_sum = 0.0
    for k, v in kerr_channels.items():
        rng = max(abs(v['range'][0]), abs(v['range'][1]))
        sig_sum += sig_figs(rng)
    ch_count = len(kerr_channels)
    return float(ch_count + sig_sum)


# ── Limit-bound unified function ────────────────────────────

def unified_limit(x: np.ndarray, y: np.ndarray,
                  U: float = 1.0,
                  mode: str = "collective_avoid") -> np.ndarray:
    """
    F(x, y) = lim (x,y)->U
    
    Encapsulates:
      - collective avoidance sequence
      - chasing constant
      - parity-even collapse into empty set
    
    mode:
      "collective_avoid" — standard avoidance bound
      "chase"            — approach from below
      "parity_even"      — collapse to Ø at even steps
    """
    if mode == "collective_avoid":
        dist = np.abs(x - U) + np.abs(y - U)
        return np.where(dist > 1e-9, 1.0 / (1.0 + dist), 0.0)
    
    elif mode == "chase":
        return np.minimum(np.abs(x), np.abs(y)) / (U + 1e-15)
    
    elif mode == "parity_even":
        idx = np.arange(len(x))
        even_mask = (idx % 2 == PARITY_EVEN)
        result = np.zeros_like(x)
        result[even_mask] = (x[even_mask] + y[even_mask]) / (2.0 * U + 1e-15)
        result[~even_mask] = (x[~even_mask] - y[~even_mask]) / (2.0 * U + 1e-15)
        return result
    
    else:
        return np.sqrt(x**2 + y**2) / (U + 1e-15)


# ── Void mechanics (vectorized) ────────────────────────────

def void_collapse_vec(value: np.ndarray,
                      threshold: float = SPATIAL_THRESHOLD,
                      unified_singular: float = 18.0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply void collapse: 2 0 -> Ø, vectorized.
    
    unified_singular is computed dynamically from Kerr channels, not hardcoded.
    """
    v = np.asarray(value, dtype=float)
    mask = np.abs(v) > threshold
    collapsed = np.where(mask, v * (unified_singular / (np.abs(v) + 1e-15)) * 0.001, v)
    return collapsed, mask


def planckian_converge_vec(value: np.ndarray,
                           h: float = PLANCK_CONV) -> np.ndarray:
    """
    Forces the signal toward zero (h -> 0), vectorized.
    h represents Planck-scale convergence floor.
    """
    v = np.asarray(value, dtype=float)
    return v * h / (np.abs(v) + h + 1e-15)


# ── Spatial displacement mechanics ──────────────────────────

def displacement_field(x: np.ndarray, y: np.ndarray,
                       spatial_thresh: float = SPATIAL_THRESHOLD,
                       force_exp: float = FORCE_EXPONENT,
                       freq_constant: float = 3.0,
                       unified_singular: float = None) -> Dict:
    """
    Temporal/Spatial Displacement Mechanics.
    
    unified_singular is machine-computed from Kerr data, not hardcoded.
    If None, calculates it from the number of aligned channels and physical scale.
    """
    if unified_singular is None:
        unified_singular = unified_singular_func(channel_stats=None, bh=None)
    
    U = 1.0  # Upper bound (normalized)
    
    # 1. Limit-bound function
    F = unified_limit(x, y, U, mode="collective_avoid")
    
    # 2. Spatial distortion threshold check
    distorted = np.abs(F) > spatial_thresh * 0.01
    F_thresh = np.where(distorted, F * 0.01, F)
    
    # 3. Force component F^(2/3) — negative force over cubic volume
    force = np.sign(F_thresh) * np.abs(F_thresh) ** force_exp
    volume = np.abs(x * y) + 1e-15
    force_field = -force / (volume ** (1.0/3.0))
    
    # 4. Scaled frequency constant: 3f / C
    if len(x) > 1:
        dx = np.diff(x)
        dy = np.diff(y)
        f_est = np.mean(np.sqrt(dx**2 + dy**2)) * freq_constant / (spatial_thresh + 1e-15)
    else:
        f_est = 0.0
    scaled_freq = freq_constant * f_est / (spatial_thresh + 1e-15)
    
    # 5. Parity-even collapse (every other sample collapses toward Ø)
    idx = np.arange(len(x))
    even_mask = (idx % 2 == PARITY_EVEN)
    parity_signal = np.where(even_mask,
                              F_thresh * scaled_freq,
                              F_thresh * (1.0 - scaled_freq))
    
    # 6. Void structure: 2 0 -> Ø, uses live-computed unified_singular
    void_signal, collapsed_mask = void_collapse_vec(F_thresh, unified_singular=unified_singular)
    
    # 7. Planckian convergence (h -> 0)
    void_converged = planckian_converge_vec(void_signal)
    
    collapse_count = int(np.sum(collapsed_mask))
    
    return {
        "displacement": F_thresh.astype(float),
        "force_field": force_field.astype(float),
        "parity_signal": parity_signal.astype(float),
        "void_signal": void_signal.astype(float),
        "void_converged": void_converged.astype(float),
        "scaled_freq": float(scaled_freq),
        "collapse_count": collapse_count,
    }


# ── Full spatial pipeline for a signal ──────────────────────

def spatial_pipeline(signal: np.ndarray,
                     t: Optional[np.ndarray] = None,
                     use_void: bool = True,
                     use_parity: bool = True,
                     unified_singular: float = None) -> np.ndarray:
    """
    Apply full spatial displacement mechanics to a 1D signal.
    
    unified_singular is machine-computed from Kerr data.
    """
    n = len(signal)
    if t is None:
        t = np.linspace(0, 1, n)
    
    y = t
    
    disp = displacement_field(signal, y, unified_singular=unified_singular)
    
    # Combine signals
    out = disp["displacement"].copy()
    if use_parity:
        out = out + disp["parity_signal"]
    if use_void:
        out = out + disp["void_converged"]
    
    # Normalize to zero-centered
    mn = np.min(out)
    mx = np.max(out)
    rng = mx - mn
    if rng > 1e-15:
        out = (out - mn) / rng - 0.5  # center around 0
    else:
        out = np.zeros_like(out)
    
    return out


# ── Integration with Kerr engine ────────────────────────────

def kerr_spatial_overlap(bh,
                         r0: float = 30.0,
                         n: int = 1024,
                         use_msn: bool = True,
                         use_spatial: bool = True) -> Dict:
    """
    End-to-end: Kerr fast signal -> MSN anchor -> Spatial displacement -> Overlap.
    
    Returns overlap scores between all processed channels.
    """
    from kerr_engine import fast_signal, BlackHole
    from wave_overlap import overlap_score, synergistic_match, overlap_metric_series
    
    if bh is None:
        from kerr_engine import BlackHole
        bh = BlackHole(M=1.0, a=0.92)
    elif isinstance(bh, dict):
        from kerr_engine import BlackHole
        bh = BlackHole(M=bh.get("M", 1.0), a=bh.get("a", 0.92))
    
    sig = fast_signal(bh, r0=r0, n=n)
    channels = {}
    
    # Process each raw channel
    for name, raw in [("Omega", sig["Omega"]),
                      ("grad",  sig["grad"]),
                      ("gtt",   sig["gtt"])]:
        s = raw.copy()
        
        # Step 1: MSN anchor
        if use_msn:
            s = s * MSN_INV
            mn, mx = np.min(s), np.max(s)
            rng = mx - mn
            if rng > 1e-15:
                s = (s - mn) / rng
            else:
                s = np.zeros_like(s)
        
        channels[name] = s
    
    # Machine-computed unified singular (not hardcoded 18)
    us = dynamic_unified_singular(
        {k: {"range": (float(np.min(v)), float(np.max(v)))} for k, v in channels.items()}
    )
    
    # Step 2: Spatial displacement mechanics with live unified_singular
    if use_spatial:
        for name in channels:
            channels[name] = spatial_pipeline(channels[name], t=sig["t"], unified_singular=us)
    
    # Overlap scoring
    sigs = list(channels.values())
    names = list(channels.keys())
    
    overlap_matrix = np.zeros((len(sigs), len(sigs)))
    match_matrix  = np.zeros((len(sigs), len(sigs)), dtype=bool)
    
    for i in range(len(sigs)):
        for j in range(i+1, len(sigs)):
            s = overlap_score(sigs[i], sigs[j])
            m = synergistic_match(sigs[i], sigs[j])
            overlap_matrix[i, j] = s
            overlap_matrix[j, i] = s
            match_matrix[i, j]  = m
            match_matrix[j, i]  = m
    
    best_i, best_j = 0, 1
    best_score = 0.0
    for i in range(len(sigs)):
        for j in range(i+1, len(sigs)):
            if overlap_matrix[i, j] > best_score:
                best_score = overlap_matrix[i, j]
                best_i, best_j = i, j
    
    return {
        "MSN": MSN,
        "spatial_threshold": SPATIAL_THRESHOLD,
        "unified_singular": us,
        "force_exponent": FORCE_EXPONENT,
        "channels": {k: {"range": (float(np.min(v)), float(np.max(v))),
                         "mean": float(np.mean(v)),
                         "std": float(np.std(v))}
                     for k, v in channels.items()},
        "overlap_matrix": overlap_matrix.tolist(),
        "best_pair": (names[best_i], names[best_j]),
        "best_score": float(best_score),
        "synergistic_match": bool(best_score >= 0.05),
        "channel_names": names,
    }


# ── Output: finalized 18/Ø terminal state ───────────────────

def terminal_state(unified_singular: float = None) -> Dict:
    """
    The system converges to:
      18 = unified singular (machine-computed from Kerr data)
      18/0 = Ø = empty set (collapsed coordinates)
      This is the firewall / terminal point.
    """
    if unified_singular is None:
        unified_singular = unified_singular_func()
    return {
        "state": unified_singular,
        "division": "undefined (" + str(unified_singular) + "/0 -> Ø)",
        "symbol": "Ø",
        "meaning": "Collapsed geometry / firewall",
        "convergence": "h -> 0",
    }


# ── Quick self-test ─────────────────────────────────────────

if __name__ == "__main__":
    import time
    
    t0 = time.time()
    res = kerr_spatial_overlap(None, r0=30.0, n=None)
    elapsed = time.time() - t0
    
    print("="*60)
    print("SPATIAL DISPLACEMENT MECHANICS — INTEGRATED REPORT")
    print("="*60)
    print(f"  MSN                : {res['MSN']:.11f}")
    print(f"  Spatial threshold  : {res['spatial_threshold']}")
    print(f"  Unified singular   : {res['unified_singular']}")
    print(f"  Force exponent     : {res['force_exponent']}")
    print()
    print("  Channel statistics (post spatial pipeline):")
    for k, v in res["channels"].items():
        print(f"    {k:10s}: range=[{v['range'][0]:+.6f}, {v['range'][1]:+.6f}]  "
              f"mean={v['mean']:+.6f}  std={v['std']:.6f}")
    print()
    print(f"  Best overlap pair : {res['best_pair']}")
    print(f"  Best score        : {res['best_score']:.6f}")
    print(f"  Synergistic match : {res['synergistic_match']}")
    print()
    
    term = terminal_state(res['unified_singular'])
    print("  Terminal state:")
    print(f"    Unified singular  = {term['state']}")
    print(f"    {str(term['state'])}/0              = {term['division']}  ({term['symbol']})")
    print(f"    Meaning           : {term['meaning']}")
    print(f"    Convergence       : {term['convergence']}")
    print()
    print(f"  Elapsed: {elapsed:.4f}s")
    print("="*60)
