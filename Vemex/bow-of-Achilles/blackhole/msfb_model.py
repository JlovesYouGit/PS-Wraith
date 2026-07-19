import numpy as np
import matplotlib.pyplot as plt
import math

print("MSFB Model: Visualizing the Equation")
print("=" * 35)

# MSFB calculation as requested
# MSFB = M.S.F.B where:
# M = Mass factor = 4 × 10⁶
# S = Space curvature = 10¹⁵
# F = Felt perception = 10⁻⁵
# B = Bending deviation = 10¹⁰

M_ratio = 4e6     # Mass factor
S_value = 1e15    # Space curvature
F_value = 1e-5    # Felt perception
B_value = 1e10    # Bending deviation

MSFB = M_ratio * S_value * F_value * B_value

print("Given Values:")
print("=" * 12)
print(f"M (Mass factor): {M_ratio:.1e}")
print(f"S (Space curvature): {S_value:.1e}")
print(f"F (Felt perception): {F_value:.1e}")
print(f"B (Bending deviation): {B_value:.1e}")
print()

print("Calculation:")
print("=" * 11)
print(f"MSFB = M × S × F × B")
print(f"MSFB = {M_ratio:.1e} × {S_value:.1e} × {F_value:.1e} × {B_value:.1e}")
print()

# Step by step calculation
step1 = M_ratio * S_value
print(f"Step 1: M × S = {M_ratio:.1e} × {S_value:.1e} = {step1:.1e}")

step2 = step1 * F_value
print(f"Step 2: (M × S) × F = {step1:.1e} × {F_value:.1e} = {step2:.1e}")

final_result = step2 * B_value
print(f"Step 3: ((M × S) × F) × B = {step2:.1e} × {B_value:.1e} = {final_result:.1e}")
print()

# Verification using exponents
exp_M = math.log10(M_ratio)
exp_S = math.log10(S_value)
exp_F = math.log10(F_value)
exp_B = math.log10(B_value)

total_exp = exp_M + exp_S + exp_F + exp_B

print("Exponent Verification:")
print("=" * 20)
print(f"M exponent: log₁₀({M_ratio:.1e}) = {exp_M:.0f}")
print(f"S exponent: log₁₀({S_value:.1e}) = {exp_S:.0f}")
print(f"F exponent: log₁₀({F_value:.1e}) = {exp_F:.0f}")
print(f"B exponent: log₁₀({B_value:.1e}) = {exp_B:.0f}")
print(f"Total exponent: {exp_M:.0f} + {exp_S:.0f} + {exp_F:.0f} + {exp_B:.0f} = {total_exp:.0f}")
print()

print("Final Results:")
print("=" * 13)
print(f"MSFB = {final_result:.1e}")
print(f"MSFB ≈ 4 × 10^{total_exp:.0f}")
print()

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Left plot: Bar chart of components
parameters = ['Mass\nFactor\n(M)', 'Space\nCurvature\n(S)', 'Felt\nPerception\n(F)', 'Bending\nDeviation\n(B)']
values = [M_ratio, S_value, F_value, B_value]
log_values = [np.log10(v) for v in values]

bars = ax1.bar(parameters, log_values, color=['red', 'blue', 'green', 'orange'], alpha=0.7)
ax1.set_ylabel('Log Scale')
ax1.set_title('MSFB Components (Log Scale)')
ax1.set_ylim(min(log_values) - 1, max(log_values) + 1)

# Add value labels on bars
for bar, value in zip(bars, values):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5 if height > 0 else height - 0.5,
             f'{value:.1e}', ha='center', va='bottom' if height > 0 else 'top')

# Right plot: Calculation steps
steps = ['M × S', '(M × S) × F', 'MSFB']
step_values = [step1, step2, final_result]
log_step_values = [np.log10(v) for v in step_values]

bars2 = ax2.bar(steps, log_step_values, color=['purple', 'cyan', 'gold'], alpha=0.7)
ax2.set_ylabel('Log Scale')
ax2.set_title('MSFB Calculation Steps (Log Scale)')
ax2.set_ylim(0, max(log_step_values) + 1)

# Add value labels on bars
for bar, value in zip(bars2, step_values):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{value:.1e}', ha='center', va='bottom')

# Add the final result as text
ax2.text(1, max(log_step_values) + 0.5, f'MSFB = {final_result:.1e}', 
         fontsize=14, ha='center', va='center', 
         bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

plt.tight_layout()
plt.show()

# Physical interpretation
print("Physical Interpretation:")
print("=" * 22)
print("In the context of Sagittarius A*:")
print(f"• M represents the mass factor (4 × 10⁶ solar masses)")
print(f"• S represents spacetime curvature effects (10¹⁵ m⁻⁴)")
print(f"• F represents felt perception/tidal forces (10⁻⁵ m/s²)")
print(f"• B represents bending/deviation of geodesics (10¹⁰ m⁻²)")
print()
print(f"The resulting MSFB value of {final_result:.1e} represents")
print("the combined effect of these factors near the black hole.")
print()
print("This model demonstrates how the massive gravitational field of")
print("Sagittarius A* affects spacetime curvature, tidal forces, and")
print("the bending of light paths in its vicinity.")