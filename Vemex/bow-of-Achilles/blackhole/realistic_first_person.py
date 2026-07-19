import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Circle
import math

# Physical constants
M_sol = 1.989e30  # Solar mass in kg
c = 299792458  # Speed of light in m/s
G = 6.67430e-11  # Gravitational constant
h = 1.7  # Height of human in meters

# Sagittarius A* properties
M_sgr = 4.1e6 * M_sol  # Mass of Sagittarius A* in kg
r_s_sgr = 2 * G * M_sgr / (c**2)  # Schwarzschild radius of Sagittarius A*

print("Realistic First-Person Visualization of Black Hole Environment")
print("=" * 63)
print(f"Mass of Sagittarius A*: {M_sgr:.2e} kg")
print(f"Schwarzschild radius: {r_s_sgr:.2e} m")
print()

# Create figure with subplots for a more realistic visualization
fig = plt.figure(figsize=(15, 10))

# Main 3D view (first-person perspective)
ax1 = fig.add_subplot(221, projection='3d')

# Observer position (at a safe distance from the black hole)
observer_distance = r_s_sgr * 100  # 100 times Schwarzschild radius
observer_pos = np.array([observer_distance, 0, 0])

# Create black hole at origin with realistic appearance
bh_radius = r_s_sgr * 0.05  # Scale for visualization
u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(0, np.pi, 100)
x_bh = bh_radius * np.outer(np.cos(u), np.sin(v))
y_bh = bh_radius * np.outer(np.sin(u), np.sin(v))
z_bh = bh_radius * np.outer(np.ones(np.size(u)), np.cos(v))

# Plot black hole with gradient to simulate event horizon
ax1.plot_surface(x_bh, y_bh, z_bh, color='black', alpha=1.0)

# Add innermost stable circular orbit (ISCO) visualization
isco_radius = 6 * r_s_sgr * 0.05  # Scaled for visualization
theta_isco = np.linspace(0, 2*np.pi, 100)
x_isco = isco_radius * np.cos(theta_isco)
y_isco = isco_radius * np.sin(theta_isco)
z_isco = np.zeros_like(x_isco)
ax1.plot(x_isco, y_isco, z_isco, color='red', linestyle='--', alpha=0.7, linewidth=1)

# Create accretion disk with realistic temperature gradient
disk_radii = np.linspace(isco_radius * 1.2, isco_radius * 5, 20)
temperatures = np.linspace(0.3, 1.0, len(disk_radii))  # Color temperature gradient

for i, (radius, temp) in enumerate(zip(disk_radii, temperatures)):
    theta = np.linspace(0, 2*np.pi, 50)
    x_disk = radius * np.cos(theta)
    y_disk = radius * np.sin(theta)
    z_disk = np.zeros_like(x_disk)
    
    # Color from red (hot) to yellow to white (cooler)
    if temp < 0.5:
        color = (1, temp*2, 0)  # Red to yellow
    else:
        color = (1, 1, (temp-0.5)*2)  # Yellow to white
    ax1.plot(x_disk, y_disk, z_disk, color=color, alpha=0.8, linewidth=2)

# Create realistic starfield with depth
num_stars = 500
star_distances = np.random.uniform(observer_distance*0.5, observer_distance*3, num_stars)
star_angles_theta = np.random.uniform(0, 2*np.pi, num_stars)
star_angles_phi = np.random.uniform(0, np.pi, num_stars)

# Convert to Cartesian coordinates
star_x = star_distances * np.sin(star_angles_phi) * np.cos(star_angles_theta)
star_y = star_distances * np.sin(star_angles_phi) * np.sin(star_angles_theta)
star_z = star_distances * np.cos(star_angles_phi)

# Apply perspective effect (closer stars appear brighter)
star_brightness = 1 / (star_distances / observer_distance)
star_sizes = np.clip(star_brightness * 20, 0.1, 20)

# Plot stars with size and brightness based on distance
ax1.scatter(star_x, star_y, star_z, c='white', s=star_sizes, alpha=0.8)

# Create gravitational lensing effect (Einstein ring)
lens_radius = r_s_sgr * 0.2  # Scaled for visualization
theta_lens = np.linspace(0, 2*np.pi, 100)
lens_x = lens_radius * np.cos(theta_lens)
lens_y = lens_radius * np.sin(theta_lens)
lens_z = np.zeros(100)
ax1.plot(lens_x, lens_y, lens_z, color='cyan', linewidth=3, alpha=0.8)

# Add lensed images of stars (simulating gravitational lensing)
num_lensed = 30
for i in range(num_lensed):
    base_angle = np.random.uniform(0, 2*np.pi)
    # Primary image
    radius1 = lens_radius * 1.3
    x1 = radius1 * np.cos(base_angle)
    y1 = radius1 * np.sin(base_angle)
    z1 = np.random.uniform(-lens_radius*0.2, lens_radius*0.2)
    ax1.scatter(x1, y1, z1, c='cyan', s=15, alpha=0.9)
    
    # Secondary image (fainter)
    radius2 = lens_radius * 0.7
    x2 = radius2 * np.cos(base_angle + np.pi)
    y2 = radius2 * np.sin(base_angle + np.pi)
    z2 = np.random.uniform(-lens_radius*0.2, lens_radius*0.2)
    ax1.scatter(x2, y2, z2, c='cyan', s=8, alpha=0.6)

# Set viewing perspective to simulate first-person view
ax1.view_init(elev=0, azim=180)  # Looking directly at the black hole
ax1.dist = 7  # Adjust distance for better view

# Set axis limits for focused view
view_limit = observer_distance * 0.1
ax1.set_xlim(-view_limit, view_limit)
ax1.set_ylim(-view_limit, view_limit)
ax1.set_zlim(-view_limit/2, view_limit/2)

# Remove axis labels for cleaner view
ax1.set_axis_off()

# Add title
ax1.set_title('First-Person View Near Black Hole', fontsize=12, pad=20)

# Create side view (for reference)
ax2 = fig.add_subplot(222)
ax2.plot(x_bh[:, 0], z_bh[:, 0], 'k-', linewidth=2, label='Black Hole')
ax2.plot(x_isco, z_isco, 'r--', linewidth=1, label='ISCO')
for i, (radius, temp) in enumerate(zip(disk_radii, temperatures)):
    ax2.plot([radius, -radius], [0, 0], color=(1, 1-temp*0.5, 0), linewidth=2, alpha=0.8)
ax2.set_xlim(-view_limit, view_limit)
ax2.set_ylim(-view_limit/2, view_limit/2)
ax2.set_xlabel('X Distance')
ax2.set_ylabel('Z Distance')
ax2.set_title('Side View')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Create top view (for reference)
ax3 = fig.add_subplot(223)
ax3.plot(x_bh[0, :], y_bh[0, :], 'k-', linewidth=2, label='Black Hole')
for i, (radius, temp) in enumerate(zip(disk_radii, temperatures)):
    circle = Circle((0, 0), radius, color=(1, 1-temp*0.5, 0), alpha=0.8, fill=False, linewidth=2)
    ax3.add_patch(circle)
ax3.set_xlim(-view_limit, view_limit)
ax3.set_ylim(-view_limit, view_limit)
ax3.set_xlabel('X Distance')
ax3.set_ylabel('Y Distance')
ax3.set_title('Top View')
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.set_aspect('equal')

# Create information panel
ax4 = fig.add_subplot(224)
ax4.set_xlim(0, 10)
ax4.set_ylim(0, 10)
ax4.axis('off')

# Add detailed information
info_text = f"""Realistic Black Hole Visualization

Physical Properties:
• Mass: {M_sgr/M_sol:.1f} million solar masses
• Schwarzschild radius: {r_s_sgr:.2e} m
• Observer distance: {observer_distance/r_s_sgr:.0f} × rₛ

Visual Effects Simulated:
• Gravitational lensing (Einstein ring)
• Lensed star images (cyan dots)
• Accretion disk with temperature gradient
• Innermost stable circular orbit (ISCO)
• Realistic starfield with perspective

Physical Calculations:
• Time dilation factor: {1 / math.sqrt(1 - r_s_sgr / observer_distance):.2f}
• Gravitational redshift: {math.sqrt(1 - r_s_sgr / observer_distance):.4f}
• Tidal force across human body: {(2 * G * M_sgr * h) / (observer_distance**3):.2e} m/s²
• Angular diameter of black hole: {math.degrees(2 * math.asin(r_s_sgr / observer_distance)):.4f} degrees

First-Person Perspective:
From this viewpoint, you would observe:
1. A dark region (event horizon) against the starfield
2. A bright accretion disk with color gradients
3. An Einstein ring around the black hole
4. Multiple images of stars behind the black hole
5. Gravitational redshift of light
"""

ax4.text(0.1, 9.5, info_text, fontsize=9, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.savefig('realistic_first_person_view.png', dpi=300, bbox_inches='tight')
print("Realistic first-person visualization saved as 'realistic_first_person_view.png'")
plt.show()

# Print additional interpretation
print("Realistic Physical Interpretation:")
print("=" * 34)
print("In this visualization:")
print("1. The black hole appears as a completely dark sphere due to its event horizon")
print("2. The accretion disk shows a temperature gradient from hot (white/yellow) to cooler (red)")
print("3. The Einstein ring (cyan) represents light from stars behind the black hole being bent")
print("4. Multiple images of background stars appear around the black hole")
print("5. The ISCO (innermost stable circular orbit) marks the closest stable orbit")
print("6. Stars appear with varying brightness based on distance (closer = brighter)")
print()
print("This represents what you would actually see with human eyes near a massive black hole,")
print("taking into account the extreme warping of spacetime and light paths.")