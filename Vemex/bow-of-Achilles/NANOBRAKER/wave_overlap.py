"""
WAVE OVERLAP METRIC
===================
Intelligence-program-level layer for comparing calculation outputs.

Core idea:
  Two independent calculations produce signals s1(t), s2(t).
  Success = both converge to zero (or near-zero) at the same points.
  This is the "synergistic point" where outputs agree at the null state.
"""
import numpy as np


def _normalize(sig: np.ndarray) -> np.ndarray:
    if len(sig) == 0:
        return sig
    mn = np.min(sig)
    mx = np.max(sig)
    rng = mx - mn
    if rng < 1e-15:
        return np.zeros_like(sig)
    return (sig - mn) / rng


def _zero_mask(sig: np.ndarray, threshold: float = 0.01) -> np.ndarray:
    return np.abs(sig) < threshold


def overlap_score(s1: np.ndarray, s2: np.ndarray) -> float:
    """
    Wave-function overlap score between two signals.
    
    Computes the fraction of time steps where BOTH signals are near zero,
    weighted by their mutual proximity to exact zero.
    
    Returns value in [0, 1]. Higher = better synergistic match.
    """
    if len(s1) == 0 or len(s2) == 0:
        return 0.0
    
    # Pad shorter array
    n = max(len(s1), len(s2))
    a = np.pad(s1, (0, n - len(s1)), mode='edge')
    b = np.pad(s2, (0, n - len(s2)), mode='edge')
    
    # Normalize to comparable scale
    an = _normalize(a)
    bn = _normalize(b)
    
    # Proximity to zero: 1.0 when exactly zero, 0.0 when at max
    pz_a = 1.0 - an
    pz_b = 1.0 - bn
    
    # Joint proximity (both near zero simultaneously)
    joint = pz_a * pz_b
    
    # Overlap score = mean joint proximity
    score = float(np.mean(joint))
    return score


def synergistic_match(s1: np.ndarray, s2: np.ndarray, threshold: float = 0.05) -> bool:
    """
    Returns True if both signals synergistically match at the zero-state.
    
    Criteria:
      - Overlap score exceeds threshold
      - Both signals hit near-zero at least once
      - The zero-hit indices overlap within a window
    """
    if len(s1) == 0 or len(s2) == 0:
        return False
    
    score = overlap_score(s1, s2)
    if score < threshold:
        return False
    
    # Find zero-crossing regions for each
    mask1 = _zero_mask(s1)
    mask2 = _zero_mask(s2)
    
    if not np.any(mask1) or not np.any(mask2):
        return False
    
    # Check if zero regions overlap
    n = max(len(s1), len(s2))
    m1 = np.pad(mask1, (0, n - len(mask1)), mode='constant')
    m2 = np.pad(mask2, (0, n - len(mask2)), mode='constant')
    
    overlap_count = np.sum(m1 & m2)
    return overlap_count > 0


def overlap_metric_series(signals: list, threshold: float = 0.05) -> dict:
    """
    Compute pairwise overlap for a list of signals.
    Returns matrix and best-match pair.
    """
    n = len(signals)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            score = overlap_score(signals[i], signals[j])
            matrix[i, j] = score
            matrix[j, i] = score
    
    # Find best matching pair
    best_i, best_j = 0, 1
    best_score = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i, j] > best_score:
                best_score = matrix[i, j]
                best_i, best_j = i, j
    
    matched = best_score >= threshold
    return {
        "matrix": matrix,
        "best_pair": (best_i, best_j),
        "best_score": float(best_score),
        "synergistic_match": matched
    }


def convergence_to_zero(sig: np.ndarray, window: int = 10) -> bool:
    """
    Check if a signal converges to near-zero in its final window.
    """
    if len(sig) < window:
        return np.all(np.abs(sig) < 0.01)
    tail = sig[-window:]
    return bool(np.all(np.abs(tail) < 0.01))
