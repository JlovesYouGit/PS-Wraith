import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

# Create the figure and axis
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)

# Initial parameters
t = np.arange(0.0, 1.0, 0.001)
M = 4e6
S = 1e15
F = 1e-5
B = 1e10
MSFB = M * S * F * B

# Create initial plot (using sine wave as visualization)
s = np.sin(2 * np.pi * t)
l, = plt.plot(t, s, lw=2)
ax.set_xlim(0, 1)
ax.set_ylim(-2, 2)

# Add text display
text_display = ax.text(0.02, 0.95, f'MSFB = {MSFB:.2e}', transform=ax.transAxes, 
                       fontsize=12, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Create axes for slider
ax_M = plt.axes([0.1, 0.1, 0.8, 0.03])
slider_M = Slider(ax_M, 'Mass (M)', 1e5, 1e7, valinit=M, valfmt='%1.1e')

# Update function
def update(val):
    M_val = slider_M.val
    # Recalculate MSFB with new M value (keeping S, F, B constant for this example)
    new_MSFB = M_val * S * F * B
    
    # Update the visualization (changing amplitude of sine wave)
    amplitude = np.log10(new_MSFB) - 25  # Scale for visualization
    l.set_ydata(amplitude * np.sin(2 * np.pi * t))
    
    # Update text display
    text_display.set_text(f'MSFB = {new_MSFB:.2e}')
    
    fig.canvas.draw_idle()

# Connect slider to update function
slider_M.on_changed(update)

# Add title
plt.suptitle('Interactive MSFB Sandbox')

plt.show()