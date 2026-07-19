import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Create figure and axis
fig, ax = plt.subplots(figsize=(12, 8))

# Define the MSFB components
M = 4e6    # Mass factor
S = 1e15   # Space curvature
F = 1e-5   # Felt perception
B = 1e10   # Bending deviation

MSFB = M * S * F * B

# Set up the static elements
ax.set_xlim(0, 12)
ax.set_ylim(0, 10)
ax.axis('off')

# Add title
title = ax.text(6, 9.5, 'Animated MSFB Calculation', fontsize=20, ha='center', weight='bold')

# Draw component positions
pos_M = (2, 7)
pos_S = (4, 7)
pos_F = (6, 7)
pos_B = (8, 7)
pos_result = (6, 3)

# Draw static components
ax.text(pos_M[0], pos_M[1], f'M = {M:.1e}', fontsize=14, ha='center', va='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor="red", alpha=0.5))
ax.text(pos_S[0], pos_S[1], f'S = {S:.1e}', fontsize=14, ha='center', va='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor="blue", alpha=0.5))
ax.text(pos_F[0], pos_F[1], f'F = {F:.1e}', fontsize=14, ha='center', va='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor="green", alpha=0.5))
ax.text(pos_B[0], pos_B[1], f'B = {B:.1e}', fontsize=14, ha='center', va='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor="orange", alpha=0.5))

# Draw static operators
ax.text(3, 7, '×', fontsize=20, ha='center', va='center')
ax.text(5, 7, '×', fontsize=20, ha='center', va='center')
ax.text(7, 7, '×', fontsize=20, ha='center', va='center')
ax.text(6, 5, '=', fontsize=20, ha='center', va='center')

# Create dynamic text elements for calculation steps
step1_text = ax.text(6, 6, '', fontsize=12, ha='center')
step2_text = ax.text(6, 5.5, '', fontsize=12, ha='center')
step3_text = ax.text(6, 5, '', fontsize=12, ha='center')
final_result = ax.text(6, 3, '', fontsize=16, ha='center', weight='bold',
                       bbox=dict(boxstyle="round,pad=0.5", facecolor="purple", alpha=0.7))

# Animation function
def animate(frame):
    # Animate the calculation steps
    if frame < 20:
        step1_text.set_text('')
        step2_text.set_text('')
        step3_text.set_text('')
        final_result.set_text('')
    elif frame < 40:
        step1 = M * S
        step1_text.set_text(f'M × S = {M:.1e} × {S:.1e} = {step1:.1e}')
        step2_text.set_text('')
        step3_text.set_text('')
        final_result.set_text('')
    elif frame < 60:
        step1 = M * S
        step2 = step1 * F
        step1_text.set_text(f'M × S = {M:.1e} × {S:.1e} = {step1:.1e}')
        step2_text.set_text(f'(M × S) × F = {step1:.1e} × {F:.1e} = {step2:.1e}')
        step3_text.set_text('')
        final_result.set_text('')
    elif frame < 80:
        step1 = M * S
        step2 = step1 * F
        step3 = step2 * B
        step1_text.set_text(f'M × S = {M:.1e} × {S:.1e} = {step1:.1e}')
        step2_text.set_text(f'(M × S) × F = {step1:.1e} × {F:.1e} = {step2:.1e}')
        step3_text.set_text(f'((M × S) × F) × B = {step2:.1e} × {B:.1e} = {step3:.1e}')
        final_result.set_text('')
    else:
        step1_text.set_text(f'M × S = {M*S:.1e}')
        step2_text.set_text(f'(M × S) × F = {M*S*F:.1e}')
        step3_text.set_text(f'((M × S) × F) × B = {MSFB:.1e}')
        final_result.set_text(f'MSFB = {MSFB:.1e}')
    
    return step1_text, step2_text, step3_text, final_result

# Create animation
anim = FuncAnimation(fig, animate, frames=100, interval=200, repeat=True)

plt.tight_layout()
plt.show()