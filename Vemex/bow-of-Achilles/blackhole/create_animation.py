import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Create figure and axis
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Add title
ax.text(5, 9, 'MSFB Calculation Animation', fontsize=16, ha='center', weight='bold')

# Define the MSFB components
M = 4e6    # Mass factor
S = 1e15   # Space curvature
F = 1e-5   # Felt perception
B = 1e10   # Bending deviation

MSFB = M * S * F * B

# Draw static elements
ax.text(2, 7, f'M = {M:.1e}', fontsize=12, ha='center', 
        bbox=dict(boxstyle="round,pad=0.3", facecolor="red", alpha=0.7))
ax.text(4, 7, f'S = {S:.1e}', fontsize=12, ha='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor="blue", alpha=0.7))
ax.text(6, 7, f'F = {F:.1e}', fontsize=12, ha='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor="green", alpha=0.7))
ax.text(8, 7, f'B = {B:.1e}', fontsize=12, ha='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor="orange", alpha=0.7))

# Draw multiplication symbols
ax.text(3, 7, '×', fontsize=16, ha='center', va='center')
ax.text(5, 7, '×', fontsize=16, ha='center', va='center')
ax.text(7, 7, '×', fontsize=16, ha='center', va='center')

# Create dynamic text elements
step_text = ax.text(5, 5, '', fontsize=12, ha='center')
result_text = ax.text(5, 3, '', fontsize=14, ha='center', weight='bold',
                      bbox=dict(boxstyle="round,pad=0.5", facecolor="purple", alpha=0.7))

# Animation function
def animate(frame):
    if frame < 25:
        step_text.set_text('')
        result_text.set_text('')
    elif frame < 50:
        step1 = M * S
        step_text.set_text(f'Step 1: M × S = {step1:.1e}')
        result_text.set_text('')
    elif frame < 75:
        step1 = M * S
        step2 = step1 * F
        step_text.set_text(f'Step 2: (M × S) × F = {step2:.1e}')
        result_text.set_text('')
    else:
        step_text.set_text(f'Final Step: ((M × S) × F) × B')
        result_text.set_text(f'MSFB = {MSFB:.1e}')
    
    return step_text, result_text

# Create animation
anim = FuncAnimation(fig, animate, frames=100, interval=100, blit=True, repeat=True)

# Save animation as GIF (this will work if you have the required dependencies)
try:
    anim.save('msfb_calculation.gif', writer='pillow', fps=10)
    print("Animation saved as 'msfb_calculation.gif'")
except Exception as e:
    print(f"Could not save animation as GIF: {e}")
    print("Displaying animation instead...")
    plt.show()

# Also save a static version
plt.savefig('msfb_calculation_static.png', dpi=300, bbox_inches='tight')
print("Static version saved as 'msfb_calculation_static.png'")