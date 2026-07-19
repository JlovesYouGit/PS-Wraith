import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math

# Physical constants
M_sol = 1.989e30  # Solar mass in kg
c = 299792458  # Speed of light in m/s
G = 6.67430e-11  # Gravitational constant

# Sagittarius A* properties
M_sgr = 4.1e6 * M_sol  # Mass of Sagittarius A* in kg
r_s_sgr = 2 * G * M_sgr / (c**2)  # Schwarzschild radius of Sagittarius A*

print("Sagittarius A* Physics-Based Model")
print("=" * 40)
print(f"Mass of Sagittarius A*: {M_sgr:.2e} kg")
print(f"Schwarzschild radius: {r_s_sgr:.2e} m")
print()

# Define the MSFB model parameters based on your equation
# MSFB = M.S.F.B where:
# M = Mass/Schwarzschild radius
# S = Space Curvature
# F = Felt/Perception
# B = Bending/Deviation

# Using your values:
M_ratio = 4e6  # Mass ratio (4 × 10⁶)
S_value = 1e15  # Space curvature (10¹⁵)
F_value = 1e-5  # Felt perception (10⁻⁵)
B_value = 1e10  # Bending deviation (10¹⁰)

# Calculate MSFB
MSFB = M_ratio * S_value * F_value * B_value

print("MSFB Model Calculation:")
print("=" * 25)
print(f"M (Mass/Schwarzschild radius): {M_ratio:.1e}")
print(f"S (Space Curvature): {S_value:.1e}")
print(f"F (Felt/Perception): {F_value:.1e}")
print(f"B (Bending/Deviation): {B_value:.1e}")
print()
print(f"MSFB = M × S × F × B")
print(f"MSFB = {M_ratio:.1e} × {S_value:.1e} × {F_value:.1e} × {B_value:.1e}")
print(f"MSFB = {MSFB:.1e}")
print()

# Verification using exponents
exp_result = 6 + 15 - 5 + 10  # 6+15-5+10 = 26
print("Exponent verification:")
print("=" * 20)
print("MSFB = (4 × 10⁶) × (10¹⁵) × (10⁻⁵) × (10¹⁰)")
print(f"MSFB = 4 × 10^({6}+{15}+{-5}+{10}) = 4 × 10^{exp_result}")
print(f"MSFB = 4 × 10^{exp_result} = {MSFB:.1e}")
print()

# Create a more realistic visualization of spacetime curvature around a black hole
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# Create a sphere to represent the black hole event horizon
u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(0, np.pi, 100)
x_bh = r_s_sgr * np.outer(np.cos(u), np.sin(v))
y_bh = r_s_sgr * np.outer(np.sin(u), np.sin(v))
z_bh = r_s_sgr * np.outer(np.ones(np.size(u)), np.cos(v))

# Plot the black hole
ax.plot_surface(x_bh, y_bh, z_bh, color='black', alpha=0.8)

# Visualize spacetime curvature using a more realistic embedding diagram
# This represents the Flamm's paraboloid which is a proper embedding of the
# spatial geometry of the Schwarzschild metric
r_min = r_s_sgr * 1.1  # Start just outside the event horizon
r_max = r_s_sgr * 10   # Extend to 10 times the Schwarzschild radius
r = np.linspace(r_min, r_max, 100)
theta = np.linspace(0, 2*np.pi, 100)
R, Theta = np.meshgrid(r, theta)

# Convert to Cartesian coordinates for embedding diagram
X_flat = R * np.cos(Theta)
Y_flat = R * np.sin(Theta)

# Calculate the embedding function for the Flamm's paraboloid
# Z = 2*sqrt(r*r_s) where r_s is Schwarzschild radius
Z_curved = 2 * np.sqrt(R * r_s_sgr)

# Plot the curved spacetime
ax.plot_surface(X_flat, Y_flat, Z_curved, color='blue', alpha=0.3)

# Add geodesic deviation vectors to show tidal forces
# These represent the relative acceleration between nearby geodesics
origin = np.array([[2*r_s_sgr, 0, 0], [-2*r_s_sgr, 0, 0], [0, 2*r_s_sgr, 0], [0, -2*r_s_sgr, 0]])
directions = np.array([[-r_s_sgr/4, 0, 0], [r_s_sgr/4, 0, 0], [0, -r_s_sgr/4, 0], [0, r_s_sgr/4, 0]])

# Plot tidal force vectors
ax.quiver(origin[:,0], origin[:,1], origin[:,2], 
          directions[:,0], directions[:,1], directions[:,2], 
          color='red', arrow_length_ratio=0.1)

# Labels and title
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.set_zlabel('Z (m)')
ax.set_title('Sagittarius A* Physics-Based Model\nSpacetime Curvature and Tidal Forces')

# Add text annotations
ax.text(0, 0, r_s_sgr, f'Event Horizon\n(Radius: {r_s_sgr:.1e} m)', 
        color='white', fontsize=10, ha='center')
ax.text(3*r_s_sgr, 3*r_s_sgr, 2*np.sqrt(3*r_s_sgr*r_s_sgr), 
        f'Spacetime Curvature\n(Embedding Diagram)', 
        color='blue', fontsize=10)
ax.text(2.5*r_s_sgr, 0, 0, f'Tidal Forces\n(Geodesic Deviation)', 
        color='red', fontsize=10)

plt.tight_layout()

# Create a second figure showing the mathematical relationship
fig2, ax2 = plt.subplots(figsize=(10, 6))

# Show the MSFB relationship as a bar chart
parameters = ['Mass/Schwarzschild\nRadius (M)', 'Space Curvature\n(S)', 'Felt Perception\n(F)', 'Bending Deviation\n(B)']
values = [M_ratio, S_value, F_value, B_value]
log_values = [np.log10(v) for v in values]

bars = ax2.bar(parameters, log_values, color=['black', 'blue', 'orange', 'red'], alpha=0.7)
ax2.set_ylabel('Log Scale')
ax2.set_title('MSFB Model Parameters (Log Scale)')
ax2.set_ylim(0, max(log_values) + 2)

# Add value labels on bars
for bar, value in zip(bars, values):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{value:.1e}', ha='center', va='bottom')

# Add the final result
ax2.text(1.5, max(log_values) + 1, f'MSFB = {MSFB:.1e}', 
         fontsize=14, ha='center', va='center', 
         bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

plt.tight_layout()
plt.show()

# Additional physics calculations
print("Additional Physics Calculations:")
print("=" * 30)

# Calculate surface gravity at event horizon
surface_gravity = G * M_sgr / (r_s_sgr**2)
print(f"Surface gravity at event horizon: {surface_gravity:.2e} m/s²")

# Calculate Hawking temperature
hbar = 1.054571817e-34  # Reduced Planck constant
k_B = 1.380649e-23  # Boltzmann constant
T_hawking = hbar * c**3 / (8 * np.pi * G * M_sgr * k_B)
print(f"Hawking temperature: {T_hawking:.2e} K")

# Calculate the Kretschmann scalar at the event horizon
# K = 48 * G^2 * M^2 / c^4 / r^6
K_eh = 48 * G**2 * M_sgr**2 / (c**4 * r_s_sgr**6)
print(f"Kretschmann scalar at event horizon: {K_eh:.2e} m⁻⁴")

print()
print("Final Results:")
print("=" * 15)
print(f"MSFB ≈ {MSFB:.1e}")
print(f"Exponent form: 4 × 10^{exp_result}")