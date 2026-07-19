import numpy as np
import matplotlib.pyplot as plt
import math

print("MSFB Model: Exact Representation of Your Equation")
print("=" * 50)

# Your original equation:
# (3.4×10³⁶) × (10⁻⁶) × (10⁻⁴) × (10⁻⁶) ≈ 3.4×10²⁰

# But you also mentioned:
# MSFB = M.S.F.B where:
# M = Mass/Schwarzschild radius = (4 × 10⁶)
# S = Space Curvature = 10¹⁵
# F = Felt Perception = 10⁻⁵
# B = Bending Deviation = 10¹⁰

# And your calculation:
# MSFB = (4 × 10⁶) × (10¹⁵) × (10⁻⁵) × (10¹⁰)
# MSFB = 4 × 10⁶⁺¹⁵⁻⁵⁺¹⁰ = 4 × 10²⁶

print("Your Original Equation:")
print("=" * 22)
print("(3.4×10³⁶) × (10⁻⁶) × (10⁻⁴) × (10⁻⁶) ≈ 3.4×10²⁰")
print()

# Calculate the original equation
mass = 3.4e36
curvature = 1e-6
perception = 1e-4
bending = 1e-6

original_result = mass * curvature * perception * bending

print("Step-by-step calculation:")
print("=" * 25)
print(f"Mass: {mass:.1e}")
print(f"Curvature: {curvature:.1e}")
print(f"Perception: {perception:.1e}")
print(f"Bending: {bending:.1e}")
print()
print(f"Result: {mass:.1e} × {curvature:.1e} × {perception:.1e} × {bending:.1e}")
print(f"Result: {original_result:.1e}")
print()

# Exponent verification for original equation
exp_mass = 36
exp_curvature = -6
exp_perception = -4
exp_bending = -6
total_exp_original = exp_mass + exp_curvature + exp_perception + exp_bending

print("Exponent verification for original equation:")
print("=" * 42)
print(f"36 + (-6) + (-4) + (-6) = {total_exp_original}")
print(f"Therefore: {mass:.1e} × {curvature:.1e} × {perception:.1e} × {bending:.1e} = 3.4×10^{total_exp_original}")
print()

print("Your MSFB Equation:")
print("=" * 18)
print("MSFB = M × S × F × B")
print("MSFB = (4 × 10⁶) × (10¹⁵) × (10⁻⁵) × (10¹⁰)")
print()

# Calculate the MSFB equation
M = 4e6    # Mass factor
S = 1e15   # Space curvature
F = 1e-5   # Felt perception
B = 1e10   # Bending deviation

MSFB_result = M * S * F * B

print("Step-by-step calculation:")
print("=" * 25)
print(f"M (Mass factor): {M:.1e}")
print(f"S (Space curvature): {S:.1e}")
print(f"F (Felt perception): {F:.1e}")
print(f"B (Bending deviation): {B:.1e}")
print()
print(f"MSFB = {M:.1e} × {S:.1e} × {F:.1e} × {B:.1e}")
print(f"MSFB = {MSFB_result:.1e}")
print()

# Exponent verification for MSFB equation
exp_M = 6
exp_S = 15
exp_F = -5
exp_B = 10
total_exp_MSFB = exp_M + exp_S + exp_F + exp_B

print("Exponent verification for MSFB equation:")
print("=" * 38)
print(f"6 + 15 + (-5) + 10 = {total_exp_MSFB}")
print(f"Therefore: MSFB = 4×10^{total_exp_MSFB}")
print()

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Left plot: Original equation components
original_params = ['Mass\n(3.4×10³⁶)', 'Curvature\n(10⁻⁶)', 'Perception\n(10⁻⁴)', 'Bending\n(10⁻⁶)']
original_values = [mass, curvature, perception, bending]
original_log_values = [np.log10(v) if v > 0 else -20 for v in original_values]  # Handle negative exponents

bars1 = ax1.bar(original_params, original_log_values, color=['red', 'blue', 'green', 'orange'], alpha=0.7)
ax1.set_ylabel('Log Scale')
ax1.set_title('Original Equation Components\n(Log Scale)')
ax1.set_ylim(-10, 40)

# Add value labels on bars
for bar, value in zip(bars1, original_values):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 1 if height > 0 else height - 1,
             f'{value:.1e}', ha='center', va='bottom' if height > 0 else 'top', fontsize=8)

# Right plot: MSFB equation components
msfb_params = ['Mass\n(4×10⁶)', 'Curvature\n(10¹⁵)', 'Perception\n(10⁻⁵)', 'Bending\n(10¹⁰)']
msfb_values = [M, S, F, B]
msfb_log_values = [np.log10(v) if v > 0 else -10 for v in msfb_values]  # Handle negative exponents

bars2 = ax2.bar(msfb_params, msfb_log_values, color=['purple', 'cyan', 'gold', 'pink'], alpha=0.7)
ax2.set_ylabel('Log Scale')
ax2.set_title('MSFB Equation Components\n(Log Scale)')
ax2.set_ylim(-10, 20)

# Add value labels on bars
for bar, value in zip(bars2, msfb_values):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5 if height > 0 else height - 0.5,
             f'{value:.1e}', ha='center', va='bottom' if height > 0 else 'top', fontsize=8)

# Add results as text
ax1.text(1.5, 35, f'Result = {original_result:.1e}', 
         fontsize=12, ha='center', va='center', 
         bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))

ax2.text(1.5, 18, f'MSFB = {MSFB_result:.1e}', 
         fontsize=12, ha='center', va='center', 
         bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))

plt.tight_layout()
plt.show()

print("Summary:")
print("=" * 8)
print(f"Original equation result: {original_result:.1e} ≈ 3.4×10^{total_exp_original}")
print(f"MSFB equation result: {MSFB_result:.1e} = 4×10^{total_exp_MSFB}")
print()
print("Both equations demonstrate how different physical quantities")
print("combine to describe the extreme gravitational environment")
print("around massive objects like Sagittarius A*.")