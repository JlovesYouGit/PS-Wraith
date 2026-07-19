import numpy as np
import matplotlib.pyplot as plt

# Create static visualization of the MSFB model
fig, ax = plt.subplots(figsize=(12, 8))

# Define the MSFB components
M = 4e6    # Mass factor
S = 1e15   # Space curvature
F = 1e-5   # Felt perception
B = 1e10   # Bending deviation

MSFB = M * S * F * B

# Create a flow diagram showing the calculation
# Positions for elements
pos_M = (2, 7)
pos_S = (4, 7)
pos_F = (6, 7)
pos_B = (8, 7)
pos_result = (5, 3)

# Draw components
ax.text(pos_M[0], pos_M[1], f'M = {M:.1e}', fontsize=14, ha='center', va='center', 
        bbox=dict(boxstyle="round,pad=0.3", facecolor="red", alpha=0.7))
ax.text(pos_S[0], pos_S[1], f'S = {S:.1e}', fontsize=14, ha='center', va='center', 
        bbox=dict(boxstyle="round,pad=0.3", facecolor="blue", alpha=0.7))
ax.text(pos_F[0], pos_F[1], f'F = {F:.1e}', fontsize=14, ha='center', va='center', 
        bbox=dict(boxstyle="round,pad=0.3", facecolor="green", alpha=0.7))
ax.text(pos_B[0], pos_B[1], f'B = {B:.1e}', fontsize=14, ha='center', va='center', 
        bbox=dict(boxstyle="round,pad=0.3", facecolor="orange", alpha=0.7))

# Draw multiplication symbols
ax.text(3, 7, '×', fontsize=20, ha='center', va='center')
ax.text(5, 7, '×', fontsize=20, ha='center', va='center')
ax.text(7, 7, '×', fontsize=20, ha='center', va='center')
ax.text(5, 5, '=', fontsize=20, ha='center', va='center')

# Draw result
ax.text(pos_result[0], pos_result[1], f'MSFB = {MSFB:.1e}', fontsize=16, ha='center', va='center', 
        bbox=dict(boxstyle="round,pad=0.5", facecolor="purple", alpha=0.7))

# Draw arrows showing the flow
ax.annotate('', xy=(3, 7), xytext=(2.5, 7), arrowprops=dict(arrowstyle='->', lw=2))
ax.annotate('', xy=(5, 7), xytext=(4.5, 7), arrowprops=dict(arrowstyle='->', lw=2))
ax.annotate('', xy=(7, 7), xytext=(6.5, 7), arrowprops=dict(arrowstyle='->', lw=2))
ax.annotate('', xy=(5, 4), xytext=(5, 6), arrowprops=dict(arrowstyle='->', lw=2))

# Add step-by-step calculation on the right
ax.text(9.5, 8, 'Calculation Steps:', fontsize=14, ha='center', va='center', weight='bold')
ax.text(9.5, 7, f'1. M × S = {M:.1e} × {S:.1e}', fontsize=12, ha='center')
ax.text(9.5, 6.5, f'   = {M*S:.1e}', fontsize=12, ha='center')
ax.text(9.5, 5.5, f'2. (M × S) × F = {M*S:.1e} × {F:.1e}', fontsize=12, ha='center')
ax.text(9.5, 5, f'   = {M*S*F:.1e}', fontsize=12, ha='center')
ax.text(9.5, 4, f'3. ((M × S) × F) × B = {M*S*F:.1e} × {B:.1e}', fontsize=12, ha='center')
ax.text(9.5, 3.5, f'   = {MSFB:.1e}', fontsize=12, ha='center')

# Add title
ax.text(6, 9, 'MSFB Model: M × S × F × B', fontsize=18, ha='center', va='center', weight='bold')

# Add physical interpretation
ax.text(1, 1.5, 'Physical Interpretation:', fontsize=14, ha='left', va='center', weight='bold')
ax.text(1, 1.0, f'• M: Mass factor (4 × 10⁶ solar masses)', fontsize=12, ha='left')
ax.text(1, 0.5, f'• S: Space curvature effects (10¹⁵ m⁻⁴)', fontsize=12, ha='left')
ax.text(1, 0.0, f'• F: Felt perception/tidal forces (10⁻⁵ m/s²)', fontsize=12, ha='left')
ax.text(1, -0.5, f'• B: Bending/deviation of geodesics (10¹⁰ m⁻²)', fontsize=12, ha='left')

# Add final result interpretation
ax.text(6, 1.5, f'The resulting MSFB value of {MSFB:.1e}', fontsize=12, ha='center')
ax.text(6, 1.0, 'represents the combined effect of these', fontsize=12, ha='center')
ax.text(6, 0.5, 'factors near a massive black hole like', fontsize=12, ha='center')
ax.text(6, 0.0, 'Sagittarius A*.', fontsize=12, ha='center')

# Set axis properties
ax.set_xlim(0, 12)
ax.set_ylim(-1, 10)
ax.axis('off')  # Turn off axis for cleaner look

plt.tight_layout()
plt.show()