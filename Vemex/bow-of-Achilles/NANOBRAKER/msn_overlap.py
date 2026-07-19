"""
MSN WAVE OVERLAP ENGINE v4
===========================
Fast wave-function overlap using analytical Kerr signals + MSN frequency anchor.

Core constants:
  MSN = 81 * 1.61803399 = 131.06075319
  This is the primary spatial/frequency anchor for continuous displacement.

Speed modes:
  FAST  = analytical field sweep (no ODE)
  MED   = analytical + simple RK4 on reduced grid
  FULL  = scipy solve_ivp (accurate, slow)
"""
import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple

# ── Core constants ──────────────────────────────────────────
PHI = 1.618033988749895
MSN = 81.0 * PHI              # 131.06075319 — spatial anchor / frequency divisor
MSN_INV = 1.0 / MSN           # 0.00762706...
DEC_HORIZON_LO = 0.60
DEC_HORIZON_HI = 0.70
DEC_BOUNDARY    = 0.99765625  # near-perfect efficiency threshold


# ── Kerr metric helpers (inline for speed) ──────────────────

@dataclass
class BH:
    M: float = 1.0
    a: float = 0.92

def _metric(r: float, theta: float, bh: BH):
    a, M = bh.a, bh.M
    ac = a * np.cos(theta)
    S = r*r + ac*ac
    D = r*r - 2.0*M*r + a*a
    if D <= 0 or S <= 0:
        return None
    invS = 1.0/S
    s2 = np.sin(theta)**2
    gtt = -(1.0 - 2.0*M*r*invS)
    gtp = -(2.0*M*a*r*s2*invS)
    grr = S/D
    gth = S
    gpp = (r*r + a*a + 2.0*M*a*a*r*s2*invS)*s2
    det = gtt*gpp - gtp*gtp
    return gtt, gtp, grr, gth, gpp, det, S, D, invS, s2

def frame_drag(r: float, theta: float, bh: BH) -> float:
    m = _metric(r, theta, bh)
    if m is None or abs(m[4]) < 1e-15:
        return 0.0
    return -m[1]/m[4]

def penrose_eta(bh: BH, r_breakup: float) -> float:
    astar = bh.a/bh.M if bh.M > 0 else 0.0
    re = bh.M + np.sqrt(bh.M**2 - (bh.a * np.cos(np.pi/2))**2)
    if r_breakup >= re:
        return 0.0
    return max(0.0, min(1.0 - np.sqrt(1.0 - 2.0*astar/(3.0*np.sqrt(3.0))*np.sqrt(re/r_breakup)), 0.5))


# ── Fast analytical signal generation ───────────────────────

def fast_signal(bh: BH, r0: float = 30.0, n: int = 1024) -> Dict:
    """
    Analytical sweep toward horizon. No ODE integration.
    Returns dict of 1D signals aligned to same time base.
    """
    rh = bh.M + np.sqrt(bh.M**2 - bh.a**2)
    re = bh.M + np.sqrt(bh.M**2 - (bh.a * np.cos(np.pi/2))**2)
    rs = np.linspace(r0, rh*1.005, n)
    t  = np.linspace(0.0, 1.0, n)

    omega = np.zeros(n)
    grad  = np.zeros(n)
    pen   = np.zeros(n)
    gtt   = np.zeros(n)

    for i, r in enumerate(rs):
        omega[i] = frame_drag(r, np.pi/2, bh)
        pen[i]   = penrose_eta(bh, r)
        m = _metric(r, np.pi/2, bh)
        gtt[i] = m[0] if m else 0.0

    # Gradient via central difference on omega
    eps = max(1e-4, (r0 - rh*1.005)/n)
    for i in range(n):
        r = rs[i]
        Op = frame_drag(r+eps, np.pi/2, bh)
        Om = frame_drag(r-eps, np.pi/2, bh)
        grad[i] = (Op - Om)/(2.0*eps)

    return {"r": rs, "t": t, "Omega": omega, "grad": grad,
            "penrose": pen, "gtt": gtt, "n": n}


# ── MSN wave modulation ─────────────────────────────────────

def msn_modulate(signal: np.ndarray, mode: str = "anchor") -> np.ndarray:
    """
    Apply MSN frequency anchor to a signal.
    
    Modes:
      anchor  = divide by MSN (scales tiny to manageable)
      scale   = multiply by MSN_INV (same, explicit)
      wrap    = modulo MSN to force into [0, MSN) band
      phi_mod = golden-ratio phase shift per sample
    """
    if mode == "anchor" or mode == "scale":
        return signal * MSN_INV
    elif mode == "wrap":
        return np.mod(signal, MSN)
    elif mode == "phi_mod":
        phase = np.linspace(0, 2.0*np.pi*PHI, len(signal))
        return signal * np.cos(phase)
    else:
        return signal / MSN


def msn_decimal_fix(value: float) -> float:
    """
    Apply MSN-based decimal expansion to break 0.6-0.7 / 0.9-1.0 limits.
    
    Logic:
      - Normalize value into [0, 1]
      - If in 0.6-0.7 emergence band, map to higher precision via MSN fractional part
      - If in 0.9-1.0 boundary band, fold back using MSN to prevent collapse
    """
    v = float(np.clip(value, 0.0, 1.0))
    
    # Emergence zone expansion
    if DEC_HORIZON_LO <= v <= DEC_HORIZON_HI:
        v = v + MSN_INV * (v - DEC_HORIZON_LO)
    
    # Boundary collapse prevention
    if v >= DEC_BOUNDARY:
        # Fold back using fractional part of MSN
        frac = MSN - np.floor(MSN)
        v = v * (1.0 - MSN_INV) + frac * MSN_INV
    
    return float(np.clip(v, 0.0, 1.0 - 1e-9))


# ── Intelligence Overlap Layer ──────────────────────────────

def overlap_score(a: np.ndarray, b: np.ndarray, use_msn: bool = True) -> float:
    """
    Wave-function overlap score. Both signals converge to zero -> score -> 1.
    
    if use_msn: pre-modulate both signals by MSN anchor before scoring.
    """
    if len(a) == 0 or len(b) == 0:
        return 0.0
    
    if use_msn:
        a = msn_modulate(a, "anchor")
        b = msn_modulate(b, "anchor")
    
    # Pad to equal length
    n = max(len(a), len(b))
    A = np.pad(a, (0, n-len(a)), mode='edge')
    B = np.pad(b, (0, n-len(b)), mode='edge')
    
    # Proximity to zero
    pz = (1.0 - np.abs(A)) * (1.0 - np.abs(B))
    return float(np.mean(np.clip(pz, 0.0, 1.0)))


def synergistic_match(a: np.ndarray, b: np.ndarray,
                      threshold: float = 0.05,
                      use_msn: bool = True) -> bool:
    """
    True if both signals synergistic-match at zero-state.
    """
    score = overlap_score(a, b, use_msn=use_msn)
    if score < threshold:
        return False
    
    # Both must hit near-zero at some point
    mask_a = np.abs(a) < threshold
    mask_b = np.abs(b) < threshold
    if not np.any(mask_a) or not np.any(mask_b):
        return False
    
    # Check for simultaneous zero-hits (within 5-sample window)
    n = max(len(a), len(b))
    ma = np.pad(mask_a, (0, n-len(mask_a)), mode='constant').astype(bool)
    mb = np.pad(mask_b, (0, n-len(mask_b)), mode='constant').astype(bool)
    
    window = 5
    for i in range(n):
        if ma[i] and np.any(mb[max(0,i-window):min(n,i+window+1)]):
            return True
    return False


def overlap_metric_series(signals: list, use_msn: bool = True) -> dict:
    n = len(signals)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            s = overlap_score(signals[i], signals[j], use_msn=use_msn)
            matrix[i, j] = s
            matrix[j, i] = s
    best_i, best_j = 0, 1
    best = 0.0
    for i in range(n):
        for j in range(i+1, n):
            if matrix[i,j] > best:
                best = matrix[i,j]
                best_i, best_j = i, j
    return {
        "matrix": matrix,
        "best_pair": (best_i, best_j),
        "best_score": float(best),
        "synergistic_match": bool(best >= 0.05)
    }


# ── MSN decimal-fix applied to signals ──────────────────────

def msn_signal_pipeline(signal: np.ndarray, normalize_first: bool = True) -> np.ndarray:
    """
    Full MSN pipeline:
      1. Normalize to [0,1] if requested
      2. Apply decimal fix (expand emergence, prevent boundary collapse)
      3. Modulate by MSN anchor
    """
    s = signal.copy()
    if normalize_first:
        mn = np.min(s)
        mx = np.max(s)
        rng = mx - mn
        if rng > 1e-15:
            s = (s - mn) / rng
        else:
            s = np.zeros_like(s)
    
    # Apply decimal fix point-by-point
    fixed = np.array([msn_decimal_fix(v) for v in s])
    return msn_modulate(fixed, "anchor")


# ── Unified fast computation ────────────────────────────────

def compute_overlap_fast(bh: BH = None,
                         r0: float = 30.0,
                         n: int = 1024,
                         compare_modes: bool = True) -> dict:
    """
    One-call overlap computation. Returns full result dict.
    """
    if bh is None:
        bh = BH(M=1.0, a=0.92)
    
    sig = fast_signal(bh, r0=r0, n=n)
    omega = sig["Omega"]
    grad  = sig["grad"]
    pen   = sig["penrose"]
    
    # Apply MSN pipeline
    omega_msn = msn_signal_pipeline(omega)
    grad_msn  = msn_signal_pipeline(grad)
    pen_msn   = msn_signal_pipeline(pen)
    
    result = {
        "MSN": MSN,
        "MSN_INV": MSN_INV,
        "PHI": PHI,
        "horizon_limits": (DEC_HORIZON_LO, DEC_HORIZON_HI),
        "boundary_threshold": DEC_BOUNDARY,
        "n_samples": n,
        "raw": {
            "Omega_range": (float(np.min(omega)), float(np.max(omega))),
            "grad_range":  (float(np.min(grad)),  float(np.max(grad))),
            "penrose_range": (float(np.min(pen)), float(np.max(pen))),
        },
        "msn_applied": {
            "Omega_range": (float(np.min(omega_msn)), float(np.max(omega_msn))),
            "grad_range":  (float(np.min(grad_msn)),  float(np.max(grad_msn))),
            "penrose_range": (float(np.min(pen_msn)), float(np.max(pen_msn))),
        }
    }
    
    if compare_modes:
        modes = [
            ("Omega_vs_Grad",   omega_msn, grad_msn),
            ("Omega_vs_Penrose", omega_msn, pen_msn),
            ("Grad_vs_Penrose",  grad_msn,  pen_msn),
            ("Raw_Omega_vs_MSN_Omega", omega, omega_msn),
        ]
        scores = {}
        for name, a, b in modes:
            s = overlap_score(a, b)
            m = synergistic_match(a, b)
            scores[name] = {"score": s, "match": m}
        result["overlaps"] = scores
        
        series = overlap_metric_series([omega_msn, grad_msn, pen_msn])
        result["series_best"] = {
            "best_score": series["best_score"],
            "best_pair": series["best_pair"],
            "synergistic_match": series["synergistic_match"]
        }
    
    return result


# ── Quick print ─────────────────────────────────────────────

def print_report(res: dict):
    print("="*60)
    print("MSN WAVE OVERLAP ENGINE — REPORT")
    print("="*60)
    print(f"  MSN constant       : {res['MSN']:.11f}")
    print(f"  MSN inverse        : {res['MSN_INV']:.11f}")
    print(f"  PHI                : {res['PHI']:.11f}")
    print(f"  Horizon band       : {res['horizon_limits']}")
    print(f"  Boundary threshold : {res['boundary_threshold']}")
    print(f"  Samples            : {res['n_samples']}")
    print()
    print("  Raw signal ranges:")
    for k, (lo, hi) in res["raw"].items():
        print(f"    {k}: [{lo:.6e}, {hi:.6e}]")
    print()
    print("  MSN-applied ranges:")
    for k, (lo, hi) in res["msn_applied"].items():
        print(f"    {k}: [{lo:.6e}, {hi:.6e}]")
    print()
    if "overlaps" in res:
        print("  Overlap scores (MSN-anchored):")
        for name, v in res["overlaps"].items():
            print(f"    {name}: {v['score']:.6f}  match={v['match']}")
        print()
    if "series_best" in res:
        sb = res["series_best"]
        print(f"  Series best pair: {sb['best_pair']}  score={sb['best_score']:.6f}  match={sb['synergistic_match']}")
    print("="*60)


# ── Demo / entry ────────────────────────────────────────────

if __name__ == "__main__":
    import time
    t0 = time.time()
    res = compute_overlap_fast(BH(M=1.0, a=0.92), r0=30.0, n=1024)
    print_report(res)
    print(f"  Elapsed: {time.time()-t0:.4f}s")
