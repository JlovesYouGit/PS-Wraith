import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Create figure
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# Define the MSFB components
M = 4e6    # Mass factor
S = 1e15   # Space curvature
F = 1e-5   # Felt perception
B = 1e10   # Bending deviation

MSFB = M * S * F * B

# Create spheres for each component (using parametric equations)
u = np.linspace(0, 2 * np.pi, 20)
v = np.linspace(0, np.pi, 20)

# Scale spheres based on component values (log scale for better visualization)
scale_M = np.log10(M) / 10
scale_S = np.log10(S) / 20
scale_F = np.log10(F) * 2 + 10  # Adjust for small values
scale_B = np.log10(B) / 15

# Position spheres in 3D space
x_M, y_M, z_M = 0, 0, 0
x_S, y_S, z_S = 4, 0, 0
x_F, y_F, z_F = 0, 4, 0
x_B, y_B, z_B = 0, 0, 4

# Draw spheres
# Mass (Red)
x_sphere = scale_M * np.outer(np.cos(u), np.sin(v))
y_sphere = scale_M * np.outer(np.sin(u), np.sin(v))
z_sphere = scale_M * np.outer(np.ones(np.size(u)), np.cos(v))
ax.plot_surface(x_sphere + x_M, y_sphere + y_M, z_sphere + z_M, color='red', alpha=0.7)

# Space curvature (Blue)
x_sphere = scale_S * np.outer(np.cos(u), np.sin(v))
y_sphere = scale_S * np.outer(np.sin(u), np.sin(v))
z_sphere = scale_S * np.outer(np.ones(np.size(u)), np.cos(v))
ax.plot_surface(x_sphere + x_S, y_sphere + y_S, z_sphere + z_S, color='blue', alpha=0.7)

# Felt perception (Green)
x_sphere = scale_F * np.outer(np.cos(u), np.sin(v))
y_sphere = scale_F * np.outer(np.sin(u), np.sin(v))
z_sphere = scale_F * np.outer(np.ones(np.size(u)), np.cos(v))
ax.plot_surface(x_sphere + x_F, y_sphere + y_F, z_sphere + z_F, color='green', alpha=0.7)

# Bending deviation (Orange)
x_sphere = scale_B * np.outer(np.cos(u), np.sin(v))
y_sphere = scale_B * np.outer(np.sin(u), np.sin(v))
z_sphere = scale_B * np.outer(np.ones(np.size(u)), np.cos(v))
ax.plot_surface(x_sphere + x_B, y_sphere + y_B, z_sphere + z_B, color='orange', alpha=0.7)

# Add labels
ax.text(x_M, y_M, z_M + scale_M + 0.5, f'Mass\nM = {M:.1e}', color='red', fontsize=10, ha='center')
ax.text(x_S, y_S, z_S + scale_S + 0.5, f'Space\nS = {S:.1e}', color='blue', fontsize=10, ha='center')
ax.text(x_F, y_F, z_F + scale_F + 0.5, f'Felt\nF = {F:.1e}', color='green', fontsize=10, ha='center')
ax.text(x_B, y_B, z_B + scale_B + 0.5, f'Bend\nB = {B:.1e}', color='orange', fontsize=10, ha='center')

# Draw connections between components
ax.plot([x_M, x_S], [y_M, y_S], [z_M, z_S], 'k--', alpha=0.5)
ax.plot([x_S, x_F], [y_S, y_F], [z_S, z_F], 'k--', alpha=0.5)
ax.plot([x_F, x_B], [y_F, y_B], [z_F, z_B], 'k--', alpha=0.5)

# Add the final result in the center
ax.text(2, 2, 2, f'MSFB Result\n{MSFB:.1e}', color='purple', fontsize=12, ha='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor="purple", alpha=0.3))

# Set labels and title
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')
ax.set_title('MSFB Sandbox Environment - 3D Visualization', fontsize=14)

# Set equal aspect ratio
ax.set_xlim(-6, 6)
ax.set_ylim(-6, 6)
ax.set_zlim(-6, 6)

# Add information text
info_text = f'''MSFB Calculation:
M × S × F × B
{M:.1e} × {S:.1e} × {F:.1e} × {B:.1e}
= {MSFB:.1e}'''

ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
          verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Add legend
legend_text = '''Color Legend:
Red: Mass Factor (M)
Blue: Space Curvature (S)
Green: Felt Perception (F)
Orange: Bending Deviation (B)'''

ax.text2D(0.02, 0.02, legend_text, transform=ax.transAxes, fontsize=9,
          verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

plt.tight_layout()
plt.savefig('msfb_3d_sandbox.png', dpi=300, bbox_inches='tight')
print("3D sandbox visualization saved as 'msfb_3d_sandbox.png'")
plt.show()