import numpy as np
import matplotlib.pyplot as plt

# Create static visualization of the MSFB model
fig, ax = plt.subplots(figsize=(12, 10))

# Define the MSFB components
M = 4e6    # Mass factor
S = 1e15   # Space curvature
F = 1e-5   # Felt perception
B = 1e10   # Bending deviation

MSFB = M * S * F * B

# Add title
ax.text(6, 9.5, 'MSFB Model: Visual Representation', fontsize=20, ha='center', va='center', weight='bold')

# Create a flow diagram showing the calculation
# Positions for elements
pos_M = (2, 8)
pos_S = (4, 8)
pos_F = (6, 8)
pos_B = (8, 8)
pos_result = (5, 5)

# Draw components with colors
components = [
    (pos_M, f'M\n{M:.1e}', 'red'),
    (pos_S, f'S\n{S:.1e}', 'blue'),
    (pos_F, f'F\n{F:.1e}', 'green'),
    (pos_B, f'B\n{B:.1e}', 'orange')
]

for pos, label, color in components:
    ax.text(pos[0], pos[1], label, fontsize=14, ha='center', va='center', 
            bbox=dict(boxstyle="round,pad=0.5", facecolor=color, alpha=0.7), weight='bold')

# Draw multiplication symbols
ax.text(3, 8, '×', fontsize=24, ha='center', va='center', weight='bold')
ax.text(5, 8, '×', fontsize=24, ha='center', va='center', weight='bold')
ax.text(7, 8, '×', fontsize=24, ha='center', va='center', weight='bold')
ax.text(5, 6.5, '=', fontsize=24, ha='center', va='center', weight='bold')

# Draw result
ax.text(pos_result[0], pos_result[1], f'MSFB = {MSFB:.1e}', fontsize=18, ha='center', va='center', 
        bbox=dict(boxstyle="round,pad=0.7", facecolor="purple", alpha=0.8, edgecolor='black'), 
        weight='bold', color='white')

# Draw arrows showing the flow
ax.annotate('', xy=(3, 8), xytext=(2.7, 8), arrowprops=dict(arrowstyle='->', lw=3, color='black'))
ax.annotate('', xy=(5, 8), xytext=(4.7, 8), arrowprops=dict(arrowstyle='->', lw=3, color='black'))
ax.annotate('', xy=(7, 8), xytext=(6.7, 8), arrowprops=dict(arrowstyle='->', lw=3, color='black'))
ax.annotate('', xy=(5, 5.7), xytext=(5, 7.3), arrowprops=dict(arrowstyle='->', lw=3, color='black'))

# Add step-by-step calculation
ax.text(10, 9, 'Calculation Steps:', fontsize=16, ha='center', va='center', weight='bold')
ax.text(10, 8.3, f'1. M × S = {M:.1e} × {S:.1e}', fontsize=12, ha='left')
ax.text(10, 7.8, f'   = {M*S:.1e}', fontsize=12, ha='left')
ax.text(10, 7.0, f'2. (M × S) × F = {M*S:.1e} × {F:.1e}', fontsize=12, ha='left')
ax.text(10, 6.5, f'   = {M*S*F:.1e}', fontsize=12, ha='left')
ax.text(10, 5.7, f'3. ((M × S) × F) × B = {M*S*F:.1e} × {B:.1e}', fontsize=12, ha='left')
ax.text(10, 5.2, f'   = {MSFB:.1e}', fontsize=12, ha='left')

# Add physical interpretation
ax.text(1, 3, 'Physical Interpretation:', fontsize=16, ha='left', va='center', weight='bold')
ax.text(1, 2.4, f'• M: Mass factor (4 × 10⁶ solar masses)', fontsize=12, ha='left')
ax.text(1, 2.0, f'• S: Space curvature effects (10¹⁵ m⁻⁴)', fontsize=12, ha='left')
ax.text(1, 1.6, f'• F: Felt perception/tidal forces (10⁻⁵ m/s²)', fontsize=12, ha='left')
ax.text(1, 1.2, f'• B: Bending/deviation of geodesics (10¹⁰ m⁻²)', fontsize=12, ha='left')

# Add final result interpretation
ax.text(6, 3, f'Final Result:', fontsize=16, ha='center', va='center', weight='bold')
ax.text(6, 2.4, f'MSFB = {MSFB:.1e}', fontsize=14, ha='center', weight='bold')
ax.text(6, 1.9, f'= 4 × 10²⁶', fontsize=14, ha='center', weight='bold')
ax.text(6, 1.3, 'This represents the combined effect', fontsize=12, ha='center')
ax.text(6, 0.9, 'of mass, curvature, perception,', fontsize=12, ha='center')
ax.text(6, 0.5, 'and bending near a massive', fontsize=12, ha='center')
ax.text(6, 0.1, 'black hole like Sagittarius A*', fontsize=12, ha='center')

# Set axis properties
ax.set_xlim(0, 12)
ax.set_ylim(0, 10)
ax.axis('off')  # Turn off axis for cleaner look

# Save the figure
plt.tight_layout()
plt.savefig('msfb_model_visualization.png', dpi=300, bbox_inches='tight')
print("Visualization saved as 'msfb_model_visualization.png'")

# Display the figure
plt.show()

print("MSFB Model Summary:")
print("=" * 20)
print(f"M (Mass factor): {M:.1e}")
print(f"S (Space curvature): {S:.1e}")
print(f"F (Felt perception): {F:.1e}")
print(f"B (Bending deviation): {B:.1e}")
print()
print(f"MSFB = M × S × F × B")
print(f"MSFB = {M:.1e} × {S:.1e} × {F:.1e} × {B:.1e}")
print(f"MSFB = {MSFB:.1e}")
print()
print("The visualization shows how these four components")
print("combine to produce the final MSFB value, representing")
print("the complex gravitational effects near a supermassive black hole.")