import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import math

# Physical constants
M_sol = 1.989e30  # Solar mass in kg
c = 299792458  # Speed of light in m/s
G = 6.67430e-11  # Gravitational constant
h = 1.7  # Height of human in meters (approx. 5'7")

# Sagittarius A* properties
M_sgr = 4.1e6 * M_sol  # Mass of Sagittarius A* in kg
r_s_sgr = 2 * G * M_sgr / (c**2)  # Schwarzschild radius of Sagittarius A*

print("Human First-Person Perception Near Sagittarius A*")
print("=" * 50)
print(f"Mass of Sagittarius A*: {M_sgr:.2e} kg")
print(f"Schwarzschild radius: {r_s_sgr:.2e} m")
print()

# Human perception model
print("Human Perception Model:")
print("=" * 22)

# Distance from black hole where human would start to feel significant effects
# Let's calculate the distance where tidal forces become noticeable
# Tidal force difference across a human body: Δg = (2 * G * M * h) / r^3

# For a noticeable effect, let's say Δg = 1 m/s^2 (1/10th of Earth's gravity)
# Solving for r: r = ((2 * G * M * h) / Δg)^(1/3)

delta_g_noticeable = 1.0  # m/s^2
r_noticeable = ((2 * G * M_sgr * h) / delta_g_noticeable)**(1/3)
print(f"Distance for noticeable tidal forces: {r_noticeable:.2e} m ({r_noticeable/r_s_sgr:.1f} × rₛ)")

# For extreme effects (spaghettification), let's use Δg = 100 m/s^2
delta_g_extreme = 100.0  # m/s^2
r_extreme = ((2 * G * M_sgr * h) / delta_g_extreme)**(1/3)
print(f"Distance for extreme tidal forces: {r_extreme:.2e} m ({r_extreme/r_s_sgr:.1f} × rₛ)")

# Time dilation effects
# Time dilation factor: γ = 1/sqrt(1 - rₛ/r)
def time_dilation_factor(r):
    if r <= r_s_sgr:
        return float('inf')  # Inside event horizon
    return 1 / math.sqrt(1 - r_s_sgr / r)

# Calculate time dilation at different distances
# Let's use a safe distance for observation (1000 times the Schwarzschild radius)
r_observation = r_s_sgr * 1000  # Observer's distance
gamma = time_dilation_factor(r_observation)
print(f"Time dilation factor at {r_observation/r_s_sgr:.0f} × rₛ: {gamma:.2f}")
print(f"1 hour of observer time = {gamma:.2f} hours of distant time")

print()

# Visual perception - how light would be affected
print("Visual Perception:")
print("=" * 16)

# Gravitational redshift: λ_observed/λ_emitted = sqrt(1 - rₛ/r)
def redshift_factor(r):
    if r <= r_s_sgr:
        return 0  # Inside event horizon, no light escapes
    return math.sqrt(1 - r_s_sgr / r)

z_factor = redshift_factor(r_observation)
print(f"Redshift factor at {r_observation/r_s_sgr:.0f} × rₛ: {z_factor:.4f}")
if z_factor > 0:
    print(f"Visible light (500 nm) would appear as: {500e-9 / z_factor * 1e9:.0f} nm")

# If the redshift factor is small, visible light would be shifted to infrared
if z_factor < 0.5 and z_factor > 0:
    print("Visible light would be shifted to infrared - everything would appear dark")

print()

# First-person narrative description
print("First-Person Human Experience:")
print("=" * 30)
print("As you approach Sagittarius A*, you would notice several strange effects:")
print()
print("1. Time Dilation: Your watch seems to run normally, but when you look back")
print("   at Earth through your telescope, you see people moving in fast-forward.")
print(f"   At {r_observation/r_s_sgr:.0f} times the Schwarzschild radius, time on Earth")
print(f"   passes {gamma:.2f} times faster than for you.")
print()
print("2. Visual Distortion: The black hole appears to bend light around it,")
print("   creating a distorted view of the stars behind it. Stars that are")
print("   actually behind the black hole appear as rings or arcs around it.")
print()
print("3. Color Shift: Light from Earth and your ship's lights appear redder")
print(f"   due to gravitational redshift. At {r_observation/r_s_sgr:.0f} × rₛ, visible")
print("   light is stretched, making everything look dimmer and redder.")
print()
print("4. Tidal Forces: You feel a slight stretching sensation as the gravity")
print("   pulls more strongly on your feet than your head. This 'spaghettification'")
print(f"   effect becomes dangerous at {r_extreme/r_s_sgr:.1f} × rₛ from the black hole.")
print()
print("5. Event Horizon: As you approach the point of no return, you realize")
print("   that escape becomes impossible. Time and space become so warped that")
print("   all possible futures lead toward the singularity at the center.")

# MSFB calculation as requested
print("\nMSFB Model (Based on Your Equation):")
print("=" * 35)

# M = Mass/Schwarzschild radius = (4.1 × 10⁶ M☉) / r_s_sgr
# But we'll use your simplified version where M = 4 × 10⁶
M_ratio = 4e6
S_value = 1e15    # Space curvature
F_value = 1e-5    # Felt perception
B_value = 1e10    # Bending deviation

MSFB = M_ratio * S_value * F_value * B_value
print(f"M (Mass factor): {M_ratio:.1e}")
print(f"S (Space curvature): {S_value:.1e}")
print(f"F (Felt perception): {F_value:.1e}")
print(f"B (Bending deviation): {B_value:.1e}")
print()
print(f"MSFB = {M_ratio:.1e} × {S_value:.1e} × {F_value:.1e} × {B_value:.1e}")
print(f"MSFB = {MSFB:.1e}")

# Verification using exponents
exp_result = math.log10(M_ratio) + math.log10(S_value) + math.log10(F_value) + math.log10(B_value)
print(f"\nExponent verification: {math.log10(M_ratio):+.0f} + {math.log10(S_value):+.0f} + {math.log10(F_value):+.0f} + {math.log10(B_value):+.0f} = {exp_result:.0f}")
print(f"Therefore: MSFB ≈ 4 × 10^{exp_result:.0f}")

# Create a simple visualization of the MSFB model
fig, ax = plt.subplots(figsize=(10, 6))

# Show the MSFB relationship as a bar chart
parameters = ['Mass/Schwarzschild\nRadius (M)', 'Space Curvature\n(S)', 'Felt Perception\n(F)', 'Bending Deviation\n(B)']
values = [M_ratio, S_value, F_value, B_value]
log_values = [np.log10(v) for v in values]

bars = ax.bar(parameters, log_values, color=['black', 'blue', 'orange', 'red'], alpha=0.7)
ax.set_ylabel('Log Scale')
ax.set_title('MSFB Model Parameters (Log Scale)')
ax.set_ylim(0, max(log_values) + 2)

# Add value labels on bars
for bar, value in zip(bars, values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{value:.1e}', ha='center', va='bottom')

# Add the final result
ax.text(1.5, max(log_values) + 1, f'MSFB = {MSFB:.1e}', 
         fontsize=14, ha='center', va='center', 
         bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

plt.tight_layout()
plt.show()