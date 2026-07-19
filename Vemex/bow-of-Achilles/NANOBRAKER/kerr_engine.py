"""
KERR SPACETIME ENGINE v3
========================
Fast implementation using analytical Christoffel symbols.
"""
import numpy as np
from scipy.integrate import solve_ivp
from dataclasses import dataclass
from typing import Dict, List, Optional

MSN = 81.0 * 1.618033988749895  # 131.060753 — spatial anchor / frequency divisor


@dataclass
class BlackHole:
    M: float = 1.0
    a: float = 0.92


def metric_components(r, theta, bh):
    a, M = bh.a, bh.M
    a_cost = a * np.cos(theta)
    S = r**2 + a_cost**2
    D = r**2 - 2.0*M*r + a**2
    if D <= 0 or S <= 0:
        return None
    invS = 1.0/S
    s2 = np.sin(theta)**2
    cost = np.cos(theta)
    gtt = -(1.0 - 2.0*M*r*invS)
    gtp = -(2.0*M*a*r*s2*invS)
    grr = S/D
    gth = S
    gpp = (r**2 + a**2 + 2.0*M*a**2*r*s2*invS)*s2
    return {"tt": gtt, "tphi": gtp, "rr": grr, "thth": gth, "phiphi": gpp,
            "det": gtt*gpp - gtp**2, "S": S, "D": D, "invS": invS, "s2": s2, "cost": cost}


def metric_matrix(r, theta, bh):
    g = metric_components(r, theta, bh)
    if g is None: return None
    return np.array([
        [g["tt"], 0, 0, g["tphi"]],
        [0, g["rr"], 0, 0],
        [0, 0, g["thth"], 0],
        [g["tphi"], 0, 0, g["phiphi"]]
    ])


def inverse_metric_matrix(r, theta, bh):
    g = metric_components(r, theta, bh)
    if g is None or abs(g["det"]) < 1e-15: return None
    det = g["det"]
    inv = np.zeros((4,4))
    inv[0,0] = g["phiphi"]/det
    inv[0,3] = inv[3,0] = -g["tphi"]/det
    inv[1,1] = 1.0/g["rr"]
    inv[2,2] = 1.0/g["thth"]
    inv[3,3] = g["tt"]/det
    return inv


def christoffel(r, theta, bh):
    a = bh.a; M = bh.M
    g = metric_components(r, theta, bh)
    if g is None: return np.zeros((4,4,4))
    S, D = g["S"], g["D"]
    invS, invD = g["invS"], 1.0/D
    invS2 = invS*invS
    s2, cost = g["s2"], g["cost"]
    sint = np.sin(theta)
    ds2_dt = 2.0*sint*cost
    dS_dr = 2.0*r
    dS_dt = -2.0*a**2*cost*sint
    dD_dr = 2.0*r - 2.0*M
    dgtt_dr = 2.0*M*(r*invS2*dS_dr - invS)
    dgtt_dt = 2.0*M*r*invS2*(-dS_dt)
    dgtp_dr = -2.0*M*a*s2*(r*invS2*dS_dr - invS)
    dgtp_dt = -2.0*M*a*r*(s2*invS2*(-dS_dt) + ds2_dt*invS)
    dgrr_dr = (dS_dr*D - S*dD_dr)*invD*invD
    dgrr_dt = dS_dt*invD
    dgth_dr = dS_dr; dgth_dt = dS_dt
    dgpp_dr = (2.0*r + 2.0*M*a**2*s2*(r*invS2*dS_dr - invS))*s2
    dgpp_dt = (2.0*M*a**2*r*s2*invS2*(-dS_dt) + 4.0*sint*cost*(r**2+a**2+2.0*M*a**2*r*s2*invS))*s2

    ginv = inverse_metric_matrix(r, theta, bh)
    if ginv is None: return np.zeros((4,4,4))

    dg = np.zeros((4,4,4))
    dg[0,0,1] = dgtt_dr; dg[0,0,2] = dgtt_dt
    dg[0,3,0] = dg[3,0,0] = dgtp_dr
    dg[0,3,2] = dg[3,0,2] = dgtp_dt
    dg[1,1,1] = dgrr_dr; dg[1,1,2] = dgrr_dt
    dg[2,2,1] = dgth_dr; dg[2,2,2] = dgth_dt
    dg[3,3,1] = dgpp_dr; dg[3,3,2] = dgpp_dt

    Gamma = np.zeros((4,4,4))
    for mu in range(4):
        for nu in range(4):
            for si in range(4):
                val = 0.0
                for al in range(4):
                    val += 0.5*ginv[mu,al]*(dg[al,nu,si] + dg[al,si,nu] - dg[nu,si,al])
                Gamma[mu,nu,si] = val
    return 0.5*(Gamma + Gamma.transpose(0,2,1))


def _ode(t, s, bh):
    u = s[4:]
    r, th = s[1], s[2]
    G = christoffel(r, th, bh)
    du = np.zeros(4)
    for mu in range(4):
        for nu in range(4):
            for si in range(4):
                du[mu] -= G[mu,nu,si]*u[nu]*u[si]
    return np.concatenate([u, du])


def _init_state(bh, r0, th0, E, L, direction="outward"):
    g = metric_components(r0, th0, bh)
    gtt = g["tt"]; gtp = g["tphi"]; gpp = g["phiphi"]; grr = g["rr"]
    det = g["det"]
    ut = (gpp*(-E) - gtp*L)/det
    uph = (-gtp*(-E) + gtt*L)/det
    ur_sq = -(gtt*ut**2 + 2*gtp*ut*uph + gpp*uph**2 + 1.0)/grr
    ur_sq = max(ur_sq, 0.0)
    ur = np.sqrt(ur_sq)*(1.0 if direction=="outward" else -1.0)
    u = np.array([ut, ur, 0.0, uph])
    x = np.array([0.0, r0, th0, 0.0])
    return np.concatenate([x, u])


class _HorEv:
    def __init__(self, rh): self.rh=rh; self.terminal=True; self.direction=-1
    def __call__(self, t, y, *a): return y[1] - self.rh*0.99

class _EscEv:
    def __init__(self, rmx): self.rmx=rmx; self.terminal=True; self.direction=1
    def __call__(self, t, y, *a): return self.rmx - y[1]


def integrate(bh, r0=30.0, th0=np.pi/2, E=0.995, L=4.0, t_max=200.0, r_esc=600.0):
    s0 = _init_state(bh, r0, th0, E, L)
    rh = bh.M + np.sqrt(bh.M**2 - bh.a**2)
    events = [_HorEv(rh), _EscEv(r_esc)]
    sol = solve_ivp(_ode, (0, t_max), s0, args=(bh,), events=events,
                    max_step=0.5, rtol=1e-9, atol=1e-12)
    traj = sol.y[:4].T if sol.y.size else np.empty((0,4))
    meta = {"success": sol.success, "nfev": sol.nfev, "tf": float(sol.t[-1]) if sol.t.size else 0.0,
            "rf": float(sol.y[1,-1]) if sol.y.size else r0,
            "phif": float(sol.y[3,-1])%(2*np.pi) if sol.y.size else 0.0}
    for i, te in enumerate(sol.t_events):
        if te.size:
            meta["event"] = i; meta["event_t"] = float(te[0]); break
    return traj, meta


def ergosphere_r(theta, bh):
    return bh.M + np.sqrt(bh.M**2 - (bh.a*np.cos(theta))**2)

def horizon_r(bh):
    return bh.M + np.sqrt(bh.M**2 - bh.a**2)

def frame_drag(r, theta, bh):
    g = metric_matrix(r, theta, bh)
    if g is None or abs(g[3,3])<1e-15: return 0.0
    return -g[0,3]/g[3,3]

def tunnel_profile(r, theta, bh):
    Omega = frame_drag(r, theta, bh)
    eps = 1e-4
    Op = frame_drag(r+eps, theta, bh)
    Om = frame_drag(r-eps, theta, bh)
    dOdr = (Op-Om)/(2*eps)
    rh = horizon_r(bh); re = ergosphere_r(theta, bh)
    rs = np.linspace(rh*1.01, re*0.99, 500)
    grads = np.array([abs((frame_drag(rr+eps,theta,bh)-frame_drag(rr-eps,theta,bh))/(2*eps)) for rr in rs])
    return {"Omega": float(Omega), "v_drag": float(r*Omega), "dOmega_dr": float(dOdr),
            "torus_r": float(rs[np.argmax(grads)]), "max_grad": float(np.max(grads))}


def penrose_eta(bh, r_breakup, theta=np.pi/2):
    astar = bh.a/bh.M if bh.M>0 else 0.0
    re = ergosphere_r(theta, bh)
    if r_breakup >= re: return 0.0
    return max(0.0, min(1.0 - np.sqrt(1.0 - 2.0*astar/(3.0*np.sqrt(3.0))*np.sqrt(re/r_breakup)), 0.5))


def dyson_shells(bh, n=5):
    rh = horizon_r(bh)
    re = ergosphere_r(np.pi/2, bh)
    shells = []
    depths = np.linspace(0.15, 0.85, n)
    for d in depths:
        r_i = re - d*(re-rh)
        tvd = tunnel_profile(r_i, np.pi/2, bh)
        eta = penrose_eta(bh, r_i)
        shells.append({"r_M": r_i, "depth": d, "Omega": tvd["Omega"],
                       "v_drag": tvd["v_drag"], "eta": eta})
    shells.sort(key=lambda x: x["eta"], reverse=True)
    return shells


def fast_signal(bh, r0=30.0, n=None):
    """
    Generate fast analytical signals from Kerr engine without ODE integration.
    
    N is derived from M and a: n = int(MSN * max(|M|, |a|)) if not provided.
    This ensures the grid resolves the metric scale set by the black hole.
    
    Returns dict with time-series arrays derived from:
      - frame_drag Omega_LT
      - tunnel_profile gradient
      - penrose_eta
      - metric component g_tt
    """
    M = bh.M
    a = bh.a
    if n is None:
        n = max(64, int(np.ceil(MSN * max(abs(M), abs(a), 0.01))))
    
    rh = horizon_r(bh)
    re = ergosphere_r(np.pi/2, bh)
    rs = np.linspace(r0, max(rh*1.005, 1.01), n)
    t  = np.linspace(0.0, 1.0, n)
    
    # Vectorize full sweep
    a_val = a
    M_val = M
    a_cost = a_val * np.cos(np.pi/2)  # 0 for equator
    S = rs**2 + a_cost**2
    D = rs**2 - 2.0*M_val*rs + a_val**2
    invS = 1.0 / np.where(S > 1e-15, S, 1e15)
    s2 = 1.0  # sin(pi/2)^2
    
    gtt = -(1.0 - 2.0*M_val*rs*invS)
    gtp = -(2.0*M_val*a_val*rs*s2*invS)
    grr = np.where(np.abs(D) > 1e-15, S/D, 1e15)
    gth = S
    gpp = (rs**2 + a_val**2 + 2.0*M_val*a_val**2*rs*s2*invS)*s2
    
    # Frame drag: Omega = -g_tphi / g_phiphi
    Omega = np.where(np.abs(gpp) > 1e-15, -gtp/gpp, 0.0)
    
    # Penrose extractable energy (vectorized)
    astar = a_val/M_val if M_val > 0 else 0.0
    re_local = M_val + np.sqrt(M_val**2 - (a_val*np.cos(np.pi/2))**2)
    in_ergo = rs < re_local
    pen = np.zeros(n)
    if np.any(in_ergo):
        pen[in_ergo] = np.clip(
            1.0 - np.sqrt(1.0 - 2.0*astar/(3.0*np.sqrt(3.0))*np.sqrt(re_local/rs[in_ergo])),
            0.0, 0.5
        )
    
    # Gradient via central differences on Omega
    grad = np.zeros(n)
    if n > 2:
        grad[1:-1] = (Omega[2:] - Omega[:-2]) / (rs[2:] - rs[:-2])
        grad[0] = (Omega[1] - Omega[0]) / (rs[1] - rs[0])
        grad[-1] = (Omega[-1] - Omega[-2]) / (rs[-1] - rs[-2])
    
    return {
        "r": rs,
        "t": t,
        "Omega": Omega,
        "grad": grad,
        "penrose": pen,
        "gtt": gtt,
        "n": n
    }


def main():
    np.set_printoptions(precision=6, suppress=True)
    bh = BlackHole(M=1.0, a=0.92)
    rh = horizon_r(bh)
    re = ergosphere_r(np.pi/2, bh)
    print(f"BH M={bh.M} a={bh.a} a*={bh.a/bh.M:.4f}")
    print(f"Horizon {rh:.6f} M  Ergosphere {re:.6f} M")

    print("\n-- Dyson Shells --")
    for s in dyson_shells(bh, 7):
        print(f"  r={s['r_M']:.4f}  Omega={s['Omega']:.4f}  v_drag={s['v_drag']:.4f}c  eta={s['eta']*100:.2f}%")

    print("\n-- Tunnel Profile --")
    for r in np.linspace(rh*1.01, re, 8):
        t = tunnel_profile(r, np.pi/2, bh)
        print(f"  r={r:.4f}  Omega={t['Omega']:.5f}  dOmega/dr={t['dOmega_dr']:.5f}  torus@r={t['torus_r']:.4f}")

    print("\n-- Fast Signal Generation (no ODE) --")
    sig = fast_signal(bh, r0=30.0, n=500)
    print(f"  Generated {len(sig['t'])} samples")
    print(f"  Omega range: [{sig['Omega'].min():.6f}, {sig['Omega'].max():.6f}]")
    print(f"  Grad range:  [{sig['grad'].min():.6e}, {sig['grad'].max():.6e}]")
    print(f"  Penrose range: [{sig['penrose'].min():.6f}, {sig['penrose'].max():.6f}]")

    print("\n-- Intelligence Overlap Layer --")
    from wave_overlap import overlap_score, synergistic_match, convergence_to_zero, overlap_metric_series
    
    # Demo: compare two fast signals with slightly different parameters
    bh1 = BlackHole(M=1.0, a=0.92)
    bh2 = BlackHole(M=1.0, a=0.90)
    
    sig1 = fast_signal(bh1, r0=30.0, n=500)
    sig2 = fast_signal(bh2, r0=30.0, n=500)
    
    # Test overlap on Omega channel
    score_omega = overlap_score(sig1["Omega"], sig2["Omega"])
    match_omega = synergistic_match(sig1["Omega"], sig2["Omega"], threshold=0.01)
    
    # Test overlap on gradient channel
    score_grad = overlap_score(sig1["grad"], sig2["grad"])
    match_grad = synergistic_match(sig1["grad"], sig2["grad"], threshold=0.01)
    
    # Test convergence
    conv1 = convergence_to_zero(sig1["Omega"])
    conv2 = convergence_to_zero(sig2["Omega"])
    
    print(f"  Omega overlap score: {score_omega:.6f}  match: {match_omega}")
    print(f"  Grad overlap score: {score_grad:.6f}  match: {match_grad}")
    print(f"  Sig1 Omega converges to zero: {conv1}")
    print(f"  Sig2 Omega converges to zero: {conv2}")
    
    # Multi-signal overlap
    metrics = overlap_metric_series([sig1["Omega"], sig2["Omega"], sig1["grad"]])
    print(f"  Best pair score: {metrics['best_score']:.6f}  match: {metrics['synergistic_match']}")

    print("\n[DONE]")


if __name__ == "__main__":
    main()
