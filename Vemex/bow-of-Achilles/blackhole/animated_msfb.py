import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Create figure and axis
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_title('Animated MSFB Model', fontsize=16)

# Define the MSFB components
M = 4e6    # Mass factor
S = 1e15   # Space curvature
F = 1e-5   # Felt perception
B = 1e10   # Bending deviation

# Create text elements
component_text = ax.text(2, 8, f'M = {M:.1e}', fontsize=12, color='red')
space_text = ax.text(2, 7, f'S = {S:.1e}', fontsize=12, color='blue')
felt_text = ax.text(2, 6, f'F = {F:.1e}', fontsize=12, color='green')
bending_text = ax.text(2, 5, f'B = {B:.1e}', fontsize=12, color='orange')

# Create calculation steps
step1_text = ax.text(2, 3, '', fontsize=12)
step2_text = ax.text(2, 2.5, '', fontsize=12)
result_text = ax.text(2, 2, '', fontsize=14, weight='bold', color='purple')

# Create a visual representation of the black hole
bh_circle = plt.Circle((7, 5), 0.5, color='black')
ax.add_patch(bh_circle)
bh_label = ax.text(7, 5, 'BH', ha='center', va='center', color='white', fontsize=10)

# Animation variables
step = 0

def animate(frame):
    global step
    
    # Calculate intermediate steps
    step1 = M * S
    step2 = step1 * F
    result = step2 * B
    
    # Animate the calculation steps
    if frame < 50:
        step1_text.set_text('')
        step2_text.set_text('')
        result_text.set_text('')
    elif frame < 100:
        step1_text.set_text(f'Step 1: M × S = {M:.1e} × {S:.1e} = {step1:.1e}')
        step2_text.set_text('')
        result_text.set_text('')
    elif frame < 150:
        step1_text.set_text(f'Step 1: M × S = {M:.1e} × {S:.1e} = {step1:.1e}')
        step2_text.set_text(f'Step 2: (M × S) × F = {step1:.1e} × {F:.1e} = {step2:.1e}')
        result_text.set_text('')
    else:
        step1_text.set_text(f'Step 1: M × S = {M:.1e} × {S:.1e} = {step1:.1e}')
        step2_text.set_text(f'Step 2: (M × S) × F = {step1:.1e} × {F:.1e} = {step2:.1e}')
        result_text.set_text(f'Final Result: MSFB = {result:.1e}')
    
    # Make the components pulse
    pulse = 0.1 * np.sin(frame * 0.1) + 1
    component_text.set_size(12 * pulse)
    space_text.set_size(12 * pulse)
    felt_text.set_size(12 * pulse)
    bending_text.set_size(12 * pulse)
    
    return component_text, space_text, felt_text, bending_text, step1_text, step2_text, result_text

# Create animation
anim = FuncAnimation(fig, animate, frames=200, interval=100, blit=True, repeat=True)

# Add explanation
explanation = ax.text(5, 9, 'MSFB = M × S × F × B', ha='center', va='center', fontsize=16, weight='bold')

# Add legend
legend_text = [
    'M: Mass factor (4×10⁶)',
    'S: Space curvature (10¹⁵)',
    'F: Felt perception (10⁻⁵)',
    'B: Bending deviation (10¹⁰)'
]

for i, text in enumerate(legend_text):
    ax.text(7, 8 - i*0.5, text, fontsize=10, ha='left')

ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')  # Turn off axis

plt.tight_layout()
plt.show()