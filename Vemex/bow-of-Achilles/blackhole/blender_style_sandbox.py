import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as patches

# Create figure and subplots
fig = plt.figure(figsize=(12, 10))
ax3d = fig.add_subplot(221, projection='3d')  # 3D view
ax2d = fig.add_subplot(222)                   # Top view
ax_side = fig.add_subplot(223)                # Side view
ax_controls = fig.add_subplot(224)            # Controls panel

# Adjust subplot positions to make room for controls
plt.subplots_adjust(left=0.05, bottom=0.3, right=0.95, top=0.95, wspace=0.3, hspace=0.3)

# Initial values for MSFB components
initial_M = 4e6    # Mass factor
initial_S = 1e15   # Space curvature
initial_F = 1e-5   # Felt perception
initial_B = 1e10   # Bending deviation

# Create sliders for each component
axcolor = 'lightgoldenrodyellow'
ax_M = plt.axes([0.1, 0.15, 0.8, 0.03], facecolor=axcolor)
ax_S = plt.axes([0.1, 0.10, 0.8, 0.03], facecolor=axcolor)
ax_F = plt.axes([0.1, 0.05, 0.8, 0.03], facecolor=axcolor)
ax_B = plt.axes([0.1, 0.00, 0.8, 0.03], facecolor=axcolor)

slider_M = Slider(ax_M, 'Mass (M)', 1e5, 1e7, valinit=initial_M, valfmt='%1.1e')
slider_S = Slider(ax_S, 'Space (S)', 1e14, 1e16, valinit=initial_S, valfmt='%1.1e')
slider_F = Slider(ax_F, 'Felt (F)', 1e-6, 1e-4, valinit=initial_F, valfmt='%1.1e')
slider_B = Slider(ax_B, 'Bend (B)', 1e9, 1e11, valinit=initial_B, valfmt='%1.1e')

# Create reset button
reset_ax = plt.axes([0.02, 0.2, 0.1, 0.04])
button_reset = Button(reset_ax, 'Reset', color=axcolor, hovercolor='0.975')

# Create radio buttons for view modes
view_ax = plt.axes([0.8, 0.2, 0.15, 0.08], facecolor=axcolor)
radio_view = RadioButtons(view_ax, ('Normal', 'Expanded', 'Compact'), active=0)

# Function to update the visualization
def update_plot(M, S, F, B):
    # Calculate MSFB
    MSFB = M * S * F * B
    
    # Clear all axes
    ax3d.clear()
    ax2d.clear()
    ax_side.clear()
    ax_controls.clear()
    
    # 3D Visualization
    # Create spheres for each component
    u = np.linspace(0, 2 * np.pi, 20)
    v = np.linspace(0, np.pi, 20)
    
    # Scale spheres based on component values (log scale for better visualization)
    scale_M = np.log10(M) / 10
    scale_S = np.log10(S) / 20
    scale_F = np.log10(F) * 2 + 10  # Adjust for small values
    scale_B = np.log10(B) / 15
    
    # Position spheres
    x_M, y_M, z_M = 0, 0, 0
    x_S, y_S, z_S = 3, 0, 0
    x_F, y_F, z_F = 0, 3, 0
    x_B, y_B, z_B = 0, 0, 3
    
    # Draw spheres
    x_sphere = scale_M * np.outer(np.cos(u), np.sin(v))
    y_sphere = scale_M * np.outer(np.sin(u), np.sin(v))
    z_sphere = scale_M * np.outer(np.ones(np.size(u)), np.cos(v))
    ax3d.plot_surface(x_sphere + x_M, y_sphere + y_M, z_sphere + z_M, color='red', alpha=0.7)
    
    x_sphere = scale_S * np.outer(np.cos(u), np.sin(v))
    y_sphere = scale_S * np.outer(np.sin(u), np.sin(v))
    z_sphere = scale_S * np.outer(np.ones(np.size(u)), np.cos(v))
    ax3d.plot_surface(x_sphere + x_S, y_sphere + y_S, z_sphere + z_S, color='blue', alpha=0.7)
    
    x_sphere = scale_F * np.outer(np.cos(u), np.sin(v))
    y_sphere = scale_F * np.outer(np.sin(u), np.sin(v))
    z_sphere = scale_F * np.outer(np.ones(np.size(u)), np.cos(v))
    ax3d.plot_surface(x_sphere + x_F, y_sphere + y_F, z_sphere + z_F, color='green', alpha=0.7)
    
    x_sphere = scale_B * np.outer(np.cos(u), np.sin(v))
    y_sphere = scale_B * np.outer(np.sin(u), np.sin(v))
    z_sphere = scale_B * np.outer(np.ones(np.size(u)), np.cos(v))
    ax3d.plot_surface(x_sphere + x_B, y_sphere + y_B, z_sphere + z_B, color='orange', alpha=0.7)
    
    # Add labels
    ax3d.text(x_M, y_M, z_M, f'M\n{M:.1e}', color='red', fontsize=8)
    ax3d.text(x_S, y_S, z_S, f'S\n{S:.1e}', color='blue', fontsize=8)
    ax3d.text(x_F, y_F, z_F, f'F\n{F:.1e}', color='green', fontsize=8)
    ax3d.text(x_B, y_B, z_B, f'B\n{B:.1e}', color='orange', fontsize=8)
    
    # Draw connections
    ax3d.plot([x_M, x_S], [y_M, y_S], [z_M, z_S], 'k--', alpha=0.5)
    ax3d.plot([x_S, x_F], [y_S, y_F], [z_S, z_F], 'k--', alpha=0.5)
    ax3d.plot([x_F, x_B], [y_F, y_B], [z_F, z_B], 'k--', alpha=0.5)
    
    # Center result
    ax3d.text(1.5, 1.5, 1.5, f'MSFB\n{MSFB:.1e}', color='purple', fontsize=10, 
              bbox=dict(boxstyle="round,pad=0.3", facecolor="purple", alpha=0.3))
    
    ax3d.set_title('3D MSFB Sandbox Environment')
    ax3d.set_xlim(-5, 5)
    ax3d.set_ylim(-5, 5)
    ax3d.set_zlim(-5, 5)
    
    # 2D Top View
    ax2d.add_patch(patches.Circle((x_M, y_M), scale_M, color='red', alpha=0.7))
    ax2d.add_patch(patches.Circle((x_S, y_S), scale_S, color='blue', alpha=0.7))
    ax2d.add_patch(patches.Circle((x_F, y_F), scale_F, color='green', alpha=0.7))
    ax2d.add_patch(patches.Circle((x_B, y_B), scale_B, color='orange', alpha=0.7))
    
    ax2d.text(x_M, y_M, f'M\n{M:.1e}', color='red', ha='center', va='center')
    ax2d.text(x_S, y_S, f'S\n{S:.1e}', color='blue', ha='center', va='center')
    ax2d.text(x_F, y_F, f'F\n{F:.1e}', color='green', ha='center', va='center')
    ax2d.text(x_B, y_B, f'B\n{B:.1e}', color='orange', ha='center', va='center')
    
    # Draw connections
    ax2d.plot([x_M, x_S], [y_M, y_S], 'k--', alpha=0.5)
    ax2d.plot([x_S, x_F], [y_S, y_F], 'k--', alpha=0.5)
    ax2d.plot([x_F, x_B], [y_F, y_B], 'k--', alpha=0.5)
    
    ax2d.set_title('Top View')
    ax2d.set_xlim(-5, 5)
    ax2d.set_ylim(-5, 5)
    ax2d.grid(True, alpha=0.3)
    
    # Side View
    ax_side.add_patch(patches.Circle((x_M, z_M), scale_M, color='red', alpha=0.7))
    ax_side.add_patch(patches.Circle((x_S, z_S), scale_S, color='blue', alpha=0.7))
    ax_side.add_patch(patches.Circle((x_F, z_F), scale_F, color='green', alpha=0.7))
    ax_side.add_patch(patches.Circle((x_B, z_B), scale_B, color='orange', alpha=0.7))
    
    ax_side.text(x_M, z_M, f'M\n{M:.1e}', color='red', ha='center', va='center')
    ax_side.text(x_S, z_S, f'S\n{S:.1e}', color='blue', ha='center', va='center')
    ax_side.text(x_F, z_F, f'F\n{F:.1e}', color='green', ha='center', va='center')
    ax_side.text(x_B, z_B, f'B\n{B:.1e}', color='orange', ha='center', va='center')
    
    # Draw connections
    ax_side.plot([x_M, x_S], [z_M, z_S], 'k--', alpha=0.5)
    ax_side.plot([x_S, x_F], [z_S, z_F], 'k--', alpha=0.5)
    ax_side.plot([x_F, x_B], [z_F, z_B], 'k--', alpha=0.5)
    
    ax_side.set_title('Side View')
    ax_side.set_xlim(-5, 5)
    ax_side.set_ylim(-5, 5)
    ax_side.grid(True, alpha=0.3)
    
    # Controls panel
    ax_controls.set_title('MSFB Calculation')
    ax_controls.text(0.1, 0.8, f'M = {M:.1e}', fontsize=10, color='red')
    ax_controls.text(0.1, 0.7, f'S = {S:.1e}', fontsize=10, color='blue')
    ax_controls.text(0.1, 0.6, f'F = {F:.1e}', fontsize=10, color='green')
    ax_controls.text(0.1, 0.5, f'B = {B:.1e}', fontsize=10, color='orange')
    ax_controls.text(0.1, 0.3, f'MSFB = {MSFB:.1e}', fontsize=12, color='purple', weight='bold')
    
    # Step by step calculation
    step1 = M * S
    step2 = step1 * F
    ax_controls.text(0.1, 0.1, f'Step 1: M × S = {step1:.1e}', fontsize=8)
    ax_controls.text(0.1, 0.05, f'Step 2: × F = {step2:.1e}', fontsize=8)
    ax_controls.text(0.1, 0.0, f'Step 3: × B = {MSFB:.1e}', fontsize=8)
    
    ax_controls.set_xlim(0, 1)
    ax_controls.set_ylim(0, 1)
    ax_controls.axis('off')

# Initial update
update_plot(initial_M, initial_S, initial_F, initial_B)

# Define update function for sliders
def update(val):
    M = slider_M.val
    S = slider_S.val
    F = slider_F.val
    B = slider_B.val
    update_plot(M, S, F, B)
    fig.canvas.draw_idle()

# Define reset function
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
button_reset.on_clicked(reset)

# Add title to the entire figure
fig.suptitle('MSFB Sandbox Environment - Interactive Visualization', fontsize=16)

plt.show()