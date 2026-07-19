import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

# Create figure and axis
fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(bottom=0.35)

# Initial values for MSFB components
initial_M = 4e6    # Mass factor
initial_S = 1e15   # Space curvature
initial_F = 1e-5   # Felt perception
initial_B = 1e10   # Bending deviation

# Calculate initial MSFB
initial_MSFB = initial_M * initial_S * initial_F * initial_B

# Create the plot
t = np.arange(0.0, 1.0, 0.001)
s = np.sin(2 * np.pi * t)
l, = plt.plot(t, s, lw=2)

# Set axis limits
ax.set_xlim(0, 1)
ax.set_ylim(-1.5, 1.5)

# Add text display for values
text_display = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=12, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Initialize text
text_display.set_text(f'M: {initial_M:.1e}\nS: {initial_S:.1e}\nF: {initial_F:.1e}\nB: {initial_B:.1e}\nMSFB: {initial_MSFB:.1e}')

# Create axes for sliders
ax_M = plt.axes([0.1, 0.2, 0.8, 0.03])
ax_S = plt.axes([0.1, 0.15, 0.8, 0.03])
ax_F = plt.axes([0.1, 0.1, 0.8, 0.03])
ax_B = plt.axes([0.1, 0.05, 0.8, 0.03])

# Create sliders
slider_M = Slider(ax_M, 'Mass (M)', 1e5, 1e7, valinit=initial_M, valfmt='%1.1e')
slider_S = Slider(ax_S, 'Space (S)', 1e14, 1e16, valinit=initial_S, valfmt='%1.1e')
slider_F = Slider(ax_F, 'Felt (F)', 1e-6, 1e-4, valinit=initial_F, valfmt='%1.1e')
slider_B = Slider(ax_B, 'Bend (B)', 1e9, 1e11, valinit=initial_B, valfmt='%1.1e')

# Create reset button
reset_ax = plt.axes([0.02, 0.3, 0.1, 0.04])
button = Button(reset_ax, 'Reset', color='0.85', hovercolor='0.95')

# Update function
def update(val):
    M = slider_M.val
    S = slider_S.val
    F = slider_F.val
    B = slider_B.val
    MSFB = M * S * F * B
    
    # Update text display
    text_display.set_text(f'M: {M:.1e}\nS: {S:.1e}\nF: {F:.1e}\nB: {B:.1e}\nMSFB: {MSFB:.1e}')
    
    # Change the sine wave amplitude based on MSFB value (for visualization)
    # Using log scale for better visualization
    log_MSFB = np.log10(MSFB) if MSFB > 0 else 0
    amplitude = (log_MSFB - 20) / 10  # Scale for visualization
    l.set_ydata(amplitude * np.sin(2 * np.pi * t))
    
    fig.canvas.draw_idle()

# Reset function
def reset(event):
    slider_M.reset()
    slider_S.reset()
    slider_F.reset()
    slider_B.reset()

# Connect sliders to update function
slider_M.on_changed(update)
slider_S.on_changed(update)
slider_F.on_changed(update)
slider_B.on_changed(update)

# Connect reset button
button.on_clicked(reset)

# Add title
plt.suptitle('Interactive MSFB Sandbox Environment', fontsize=16)

# Add labels
ax.set_xlabel('Position')
ax.set_ylabel('Amplitude (Visualization)')

plt.show()