import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Create figure
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)

# Define the MSFB components
M = 4e6    # Mass factor
S = 1e15   # Space curvature
F = 1e-5   # Felt perception
B = 1e10   # Bending deviation

# MSFB calculation
MSFB = M * S * F * B

# Create static text elements
title = ax.text(5, 9, 'MSFB Model Animation', fontsize=16, ha='center', weight='bold')
equation = ax.text(5, 8, 'MSFB = M × S × F × B', fontsize=14, ha='center')
m_text = ax.text(2, 7, f'M = {M:.1e}', fontsize=12, color='red')
s_text = ax.text(2, 6, f'S = {S:.1e}', fontsize=12, color='blue')
f_text = ax.text(2, 5, f'F = {F:.1e}', fontsize=12, color='green')
b_text = ax.text(2, 4, f'B = {B:.1e}', fontsize=12, color='orange')

# Create dynamic text elements
step1_text = ax.text(5, 6, '', fontsize=12, ha='center')
step2_text = ax.text(5, 5, '', fontsize=12, ha='center')
result_text = ax.text(5, 4, '', fontsize=14, ha='center', weight='bold', color='purple')

# Create a simple black hole visualization
bh_circle = plt.Circle((8, 2), 0.3, color='black')
ax.add_patch(bh_circle)
ax.text(8, 2, 'BH', ha='center', va='center', color='white', fontsize=8)

# Animation function
def animate(frame):
    # Animate calculation steps
    if frame < 30:
        step1_text.set_text('')
        step2_text.set_text('')
        result_text.set_text('')
    elif frame < 60:
        step1 = M * S
        step1_text.set_text(f'M × S = {M:.1e} × {S:.1e} = {step1:.1e}')
        step2_text.set_text('')
        result_text.set_text('')
    elif frame < 90:
        step1 = M * S
        step2 = step1 * F
        step1_text.set_text(f'M × S = {M:.1e} × {S:.1e} = {step1:.1e}')
        step2_text.set_text(f'(M × S) × F = {step1:.1e} × {F:.1e} = {step2:.1e}')
        result_text.set_text('')
    else:
        step1 = M * S
        step2 = step1 * F
        step1_text.set_text(f'M × S = {M:.1e} × {S:.1e} = {step1:.1e}')
        step2_text.set_text(f'(M × S) × F = {step1:.1e} × {F:.1e} = {step2:.1e}')
        result_text.set_text(f'MSFB = {MSFB:.1e}')
    
    return step1_text, step2_text, result_text

# Create animation
anim = FuncAnimation(fig, animate, frames=120, interval=200, repeat=True)

ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')  # Turn off axis for cleaner look

plt.tight_layout()
plt.show()