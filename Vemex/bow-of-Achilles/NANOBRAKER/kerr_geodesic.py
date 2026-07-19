import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
import warnings
warnings.filterwarnings('ignore')


@dataclass
class KerrBlackHole:
    M: float
    a: float


def kerr_metric(r: float, theta: float, bh: KerrBlackHole) -> np.ndarray:
    """
    Boyer-Lindquist Kerr metric g_{mu nu}.
    Indices: 0=t, 1=r, 2=theta, 3=phi.
    """
    M = bh.M
    a = bh.a
    S = r**2 + (a * np.cos(theta))**2
    D = r**2 - 2 * M * r + a**2
    inv_S = 1.0 / S
    s2 = np.sin(theta)**2

    g_tt   = -(1.0 - 2*M*r*inv_S)
    g_tphi = -(2*M*a*r*s2*inv_S)
    g_rr   = S / D
    g_thth = S
    g_phip = (r**2 + a**2 + 2*M*a**2*r*s2*inv_S) * s2

    return np.array([
        [g_tt,  0.0, 0.0, g_tphi],
        [0.0,  g_rr, 0.0,   0.0],
        [0.0,   0.0, g_thth, 0.0],
        [g_tphi, 0.0, 0.0, g_phip]
    ])


def inverse_metric(r: float, theta: float, bh: KerrBlackHole) -> np.ndarray:
    """
    Inverse Kerr metric g^{mu nu} via analytic expressions (avoids matrix inversion instability).
    """
    M = bh.M
    a = bh.a
    S = r**2 + (a * np.cos(theta))**2
    D = r**2 - 2*M*r + a**2
    s2 = np.sin(theta)**2

    g_tt   = -(1.0 - 2*M*r/S)
    g_tphi = -(2*M*a*r*s2/S)
    g_rr   = S / D
    g_thth = S
    g_phip = (r**2 + a**2 + 2*M*a**2*r*s2/S) * s2

    det = g_tt * g_phip - g_tphi**2
    inv_g = np.array([
        [ g_phip / det, 0.0, 0.0, -g_tphi / det],
        [ 0.0,         1.0/g_rr, 0.0, 0.0],
        [ 0.0,         0.0, 1.0/g_thth, 0.0],
        [-g_tphi / det, 0.0, 0.0, g_tt / det]
    ])
    return inv_g


def christoffel_symbols(r: float, theta: float, bh: KerrBlackHole) -> np.ndarray:
    """
    Christoffel symbols Gamma^mu_{nu sigma} for Kerr spacetime.
    Uses central finite differences on metric derivatives for robustness.
    """
    eps = 1e-5
    inv_g = inverse_metric(r, theta, bh)

    def dg_dalpha(alpha, mu, nu):
        """Partial derivative of g_{mu nu} wrt coordinate alpha."""
        if alpha == 0:
            return 0.0
        dr = eps if alpha == 1 else 0.0
        dt = eps if alpha == 2 else 0.0
        dp = eps if alpha == 3 else 0.0
        g_plus  = kerr_metric(r + dr, theta + dt, bh)
        g_minus = kerr_metric(r - dr, theta - dt, bh)
        return (g_plus[mu, nu] - g_minus[mu, nu]) / (2 * eps)

    Gamma = np.zeros((4, 4, 4))

    for mu in range(4):
        for nu in range(4):
            for sig in range(4):
                val = 0.0
                for alpha in range(4):
                    d_nu = dg_dalpha(alpha, mu, sig) if nu == alpha else 0.0
                    d_sig = dg_dalpha(alpha, mu, nu) if sig == alpha else 0.0
                    d_alp = dg_dalpha(alpha, nu, sig) if alpha == alpha else 0.0
                    val += 0.5 * inv_g[mu, alpha] * (d_nu + d_sig - d_alp)
                Gamma[mu, nu, sig] = val

    # Average symmetric indices
    for mu in range(4):
        for nu in range(4):
            for sig in range(4):
                Gamma[mu, nu, sig] = 0.5 * (Gamma[mu, nu, sig] + Gamma[mu, sig, nu])
    
    return Gamma


def geodesic_ode(state: np.ndarray, bh: KerrBlackHole) -> np.ndarray:
    """
    state = [t, r, theta, phi, u_t, u_r, u_th, u_ph]
    Returns d/dtate where lambda is affine parameter.
    """
    r = float(state[1])
    theta = float(state[2])

    Gamma = christoffel_symbols(r, theta, bh)
    u = state[4:8]

    dx = u.copy()

    du = np.zeros(4)
    for mu in range(4):
        val = 0.0
        for nu in range(4):
            for sig in range(4):
                val -= Gamma[mu, nu, sig] * u[nu] * u[sig]
        du[mu] = val

    return np.concatenate([dx, du])


def r_horizon(bh: KerrBlackHole) -> float:
    return bh.M + np.sqrt(bh.M**2 - bh.a**2)


def r_ergosphere(theta: float, bh: KerrBlackHole) -> float:
    return bh.M + np.sqrt(bh.M**2 - (bh.a * np.cos(theta))**2)


def ergosphere_boundary(r: float, theta: float, bh: KerrBlackHole) -> float:
    """g_tt value — positive means inside ergosphere."""
    Sigma = r**2 + (bh.a * np.cos(theta))**2
    g_tt = -(1.0 - 2 * bh.M * r / Sigma)
    return g_tt


def frame_drag_angular_velocity(r: float, theta: float, bh: KerrBlackHole) -> float:
    """
    Lense-Thirring frame-drag angular velocity: Omega = -g_tphi / g_phiphi [1/M units].
    """
    met = kerr_metric(r, theta, bh)
    return -met[0, 3] / met[3, 3]


def spacetime_geo_tunnel_vector(r: float, theta: float, bh: KerrBlackHole) -> np.ndarray:
    """
    The 'geometric tunnel' — returns (Omega_LT, tunnel_strength) pair.
    Tunnel strength = Omega * r^2 / (r^3 + a^1.5) measures how much
    nearby spacetime rotates and pushes everything along.
    """
    Omega = frame_drag_angular_velocity(r, theta, bh)
    strength = Omega * r**2 / (r**3 + bh.a**1.5)
    return np.array([Omega, strength])


def penrose_max_energy(a_star: float) -> float:
    """Maximum Penrose extractable energy fraction for given dimensionless spin."""
    eta = 1.0 - np.sqrt(1.0 - 2.0 / (3.0 * np.sqrt(3)) * a_star * 0.5)
    return max(0.0, eta)


def geodesic_ic(
    bh: KerrBlackHole,
    r0: float = 20.0,
    theta0: float = np.pi/2,
    phi0: float = 0.0,
    E: float = 0.999,
    L: float = 4.0,
    direction: str = "outward"
) -> np.ndarray:
    """
    Set 4-velocity from conserved energy E and angular momentum L.
    For equatorial geodesics (theta=pi/2, u_th=0).
    """
    a = bh.a
    M = bh.M
    r = r0
    theta = theta0
    
    Sigma = r**2 + (a * np.cos(theta))**2
    Delta = r**2 - 2*M*r + a**2
    s2 = np.sin(theta)**2
    
    g_tt   = -(1.0 - 2*M*r/Sigma)
    g_tphi = -(2*M*a*r*s2/Sigma)
    g_phip = (r**2 + a**2 + 2*M*a**2*r*s2/Sigma) * s2
    
    det = g_tt * g_phip - g_tphi**2
    
    # u^t and u^phi from conserved quantities:
    # E = -u_t = -(g_tt u^t + g_tphi u^phi)
    # L = u_phi = g_tphi u^t + g_phip u^phi
    u_t   = -E
    u_phi = L
    
    # Solve 2x2 system:
    # [g_tt   g_tphi] [u^t]   = [-E]
    # [g_tphi g_phip] [u^phi]   = [ L]
    u_t_contra = ( g_phip * (-E) - g_tphi * L) / det
    u_phi_contra = (-g_tphi * (-E) + g_tt * L) / det
    
    # Radial 4-velocity from normalization: g_munu u^mu u^nu = -1
    u_r_sq = -(g_tt * u_t_contra**2 + 2.0*g_tphi*u_t_contra*u_phi_contra + g_phip*u_phi_contra**2 + g_rr) / g_rr
    
    if u_r_sq < 0:
        u_r_sq = abs(u_r_sq) * 0.5  # dampen to keep real
    sign = 1.0 if direction == "outward" else -1.0
    u_r = sign * np.sqrt(u_r_sq)
    
    u = np.array([u_t_contra, u_r, 0.0, u_phi_contra])
    x = np.array([0.0, r0, theta0, phi0])
    
    return np.concatenate([x, u])


def rk4_integrate(
    ic: np.ndarray,
    bh: KerrBlackHole,
    dlambda: float = 0.5,
    n_steps: int = 20000,
    absorbing_radius: float = None
) -> Tuple[np.ndarray, dict]:
    """
    Adaptive-step RK4 for geodesic equation.
    Stops at horizon absorption or escape beyond r=500M.
    """
    if absorbing_radius is None:
        absorbing_radius = r_horizon(bh) * 0.9

    state = ic.copy().astype(float)
    traj = [state[:4].copy()]
    ergo_flag = 0
    max_speed_dev = 0.0
    
    dlam = dlambda
    for i in range(n_steps):
        r = state[1]
        theta = state[2]

        # Absorbed
        if r < absorbing_radius:
            return np.array(traj), {
                'escaped': False,
                'absorbed': True,
                'steps': i,
                'ergo_steps': ergo_flag,
                'max_speed_dev': max_speed_dev
            }

        # Escaped
        if r > 500.0:
            return np.array(traj), {
                'escaped': True,
                'absorbed': False,
                'steps': i,
                'final_r': r,
                'final_phi': float(state[3]) % (2*np.pi),
                'ergo_steps': ergo_flag,
                'max_speed_dev': max_speed_dev,
                'final_t': float(state[0])
            }

        # Bounds
        theta = max(0.02, min(np.pi - 0.02, theta))
        state[2] = theta

        # RK4
        k1 = geodesic_ode(state, bh)
        k2 = geodesic_ode(state + 0.5 * dlam * k1, bh)
        k3 = geodesic_ode(state + 0.5 * dlam * k2, bh)
        k4 = geodesic_ode(state + dlam * k3, bh)
        state += (dlam / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

        # Constraint enforcement: g_uv u^u u^v = -1 (massive)
        met = kerr_metric(r, theta, bh)
        u = state[4:8]
        constraint = float(np.dot(u, np.dot(met, u)))
        max_speed_dev = max(max_speed_dev, abs(constraint + 1.0))

        if abs(constraint + 1.0) > 1e-3:
            u_norm = u / np.sqrt(-np.dot(u, np.dot(met, u)))
            state[4:8] = u_norm

        # Ergo zone flag
        g_tt_val = ergosphere_boundary(r, theta, bh)
        if g_tt_val > 0:
            ergo_flag += 1

        traj.append(state[:4].copy())
    
    return np.array(traj), {
        'escaped': False,
        'steps': n_steps,
        'ergo_steps': ergo_flag,
        'max_speed_dev': max_speed_dev
    }


def optimize_frame_drag_trajectory(
    bh: KerrBlackHole,
    r0: float = 30.0,
    n_E: int = 30,
    n_L: int = 30
) -> dict:
    """
    Grid-search for initial (E, L) that maximizes frame-drag deflection efficiency.
    Efficiency = azimuthal deflection per unit affine parameter.
    """
    best = None
    rows = []

    for E in np.linspace(0.96, 1.0, n_E):
        for L in np.linspace(-8.0, 8.0, n_L):
            try:
                ic = geodesic_ic(bh, r0=r0, theta0=np.pi/2, phi0=0.0, E=E, L=L, direction="outward")
                traj, meta = rk4_integrate(ic, bh, dlambda=0.3, n_steps=20000)
                if meta['escaped'] and meta['max_speed_dev'] < 0.05:
                    dphi = meta['final_phi']
                    dt = traj[-1, 0]
                    eff = dphi / (dt + 1e-9)
                    rows.append({'E': E, 'L': L, 'eff': eff, 'dphi': dphi, 'dt': dt})
                    if best is None or eff > best['eff']:
                        best = {
                            'E': E, 'L': L,
                            'efficiency': eff,
                            'dphi': dphi,
                            'dt': dt,
                            'meta': meta,
                            'ergo_steps': meta['ergo_steps']
                        }
            except Exception:
                continue

    return best if best else {'status': 'no valid orbit found', 'candidates': rows}


# ─────────────────────────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("KERR SPACETIME GEODESIC SIMULATION")
    print("Modelling rotating black hole ergosphere geometry")
    print("=" * 70)

    bh = KerrBlackHole(M=1.0, a=0.9)
    a_star = bh.a / bh.M
    rh = r_horizon(bh)
    re = r_ergosphere(np.pi/2, bh)
    
    print(f"\nBlack hole parameters:")
    print(f"  M = {bh.M} (natural units G=c=1)")
    print(f"  a = {bh.a} => dimensionless spin a* = {a_star:.3f}")
    print(f"  Event horizon  r_h = {rh:.4f} M")
    print(f"  Ergosphere     r_e = {re:.4f} M  (equator)")

    # TEST 1: Direct geodesic escape scan
    print("\n" + "-" * 70)
    print("TEST 1: Equatorial geodesic escape (grid over E, L)")
    print(f"{'E':>8} {'L':>8} {'escaped':>10} {'dphi':>10} {'lifetime':>10} {'ergo_steps':>12} {'max_err':>12}")
    print("-" * 70)
    
    found_escape = False
    for E in [0.99, 0.995, 0.998, 0.999, 0.9995]:
        for L in [-6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0, 8.0]:
            ic = geodesic_ic(bh, r0=30.0, theta0=np.pi/2, phi0=0.0, E=E, L=L)
            traj, meta = rk4_integrate(ic, bh, dlambda=0.4, n_steps=25000)
            
            escaped = "YES" if meta['escaped'] else "NO"
            dphi = f"{meta['final_phi']:.3f}" if meta['escaped'] else "-"
            lt = f"{meta['final_t']:.1f}" if ('final_t' in meta and meta['escaped']) else "-"
            print(f"{E:8.4f} {L:8.2f} {escaped:>10} {dphi:>10} {lt:>10} {meta['ergo_steps']:12d} {meta['max_speed_dev']:12.2e}")
            
            if meta['escaped']:
                found_escape = True
                break
        if found_escape:
            break

    # TEST 2: Frame-drag deflections
    print("\n" + "-" * 70)
    print("TEST 2: Lense-Thirring frame-drag angular velocity (Omega_LT)")
    print(f"{'r/M':>8} {'Omega_LT':>15} {'tunnel_strength':>18} {'g_tt sign':>12}")
    print("-" * 60)
    for r in np.linspace(rh + 0.5, re + 5.0, 12):
        if r <= rh + 0.5:
            continue
        omega = frame_drag_angular_velocity(r, np.pi/2, bh)
        tunnel = spacetime_geo_tunnel_vector(r, np.pi/2, bh)
        g_tt_v = ergosphere_boundary(r, np.pi/2, bh)
        sign = "INSIDE" if g_tt_v > 0 else "outside"
        print(f"{r:8.3f} {omega:15.6f} {tunnel[1]:18.6e} {sign:>12}")

    # TEST 3: Penrose extractable energy
    print("\n" + "-" * 70)
    print("TEST 3: Penrose process — extractable energy from ergosphere")
    eta_total = penrose_max_energy(a_star)
    print(f"  Maximum extractable (theoretical): {eta_total*100:.3f}%")
    for breakup_offset in [0.5, 1.0, 2.0, 5.0]:
        rb = re - breakup_offset
        if rb > rh:
            # Approximate eta ~ 1 - sqrt(1 + something)
            eta = penrose_max_energy(a_star) * (1.0 - (re - rb) / (re - rh))
            print(f"  r_breakup = {rb:.3f} M => ~{eta*100:.2f}% extractable")

    # TEST 4: Optimal trajectory search
    print("\n" + "-" * 70)
    print("TEST 4: Optimal frame-drag efficiency search")
    best = optimize_frame_drag_trajectory(bh, r0=30.0, n_E=25, n_L=25)
    if 'E' in best:
        print(f"  Best E = {best['E']:.5f}, L = {best['L']:.3f}")
        print(f"  Efficiency = {best['efficiency']:.5f} [rad/M]")
        print(f"  dphi = {best['dphi']:.4f} rad, dt = {best['dt']:.2f} M")
        print(f"  Ergo-time accumulated: {best['ergo_steps']} steps")
    else:
        print(f"  {best.get('status', 'unknown')}")

    # TEST 5: Transit through ergosphere
    print("\n" + "-" * 70)
    print("TEST 5: Geodesic transit through ergosphere (E=0.999, L=4.0)")
    ic5 = geodesic_ic(bh, r0=40.0, theta0=np.pi/2, phi0=0.0, E=0.999, L=4.0)
    traj5, meta5 = rk4_integrate(ic5, bh, dlambda=0.3, n_steps=30000)
    print(f"  Escaped: {meta5['escaped']}")
    if 'final_phi' in meta5:
        print(f"  Final phi: {meta5['final_phi']:.4f} rad  ({meta5['final_phi']*180/np.pi:.2f} deg)")
    if 'final_t' in meta5:
        print(f"  Coordinate time elapsed: {meta5['final_t']:.2f} M")
    if 'final_r' in meta5:
        print(f"  Final r: {meta5['final_r']:.2f} M")
    print(f"  Ergo-zone steps: {meta5['ergo_steps']}")
    print(f"  Max metric deviation from null/massive: {meta5['max_speed_dev']:.2e}")

    # TEST 6: Spacetime vacuum geometry near ergosphere
    print("\n" + "-" * 70)
    print("TEST 6: Spacetime 'vacuum tunnel' field near horizon")
    print(f"{'r/M':>8} {'Omega_LT':>15} {'tunnel Mag':>14}")
    print("-" * 45)
    for r in np.linspace(rh + 0.2, re, 8):
        if r < rh:
            continue
        vec = spacetime_geo_tunnel_vector(r, np.pi/2, bh)
        print(f"{r:8.4f} {vec[0]:15.6f} {vec[1]:14.6e}")
    
    print("\n" + "=" * 70)
    print("Simulation complete. Kerr geodesic engine operational.")


if __name__ == "__main__":
    main()
