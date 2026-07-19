import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math

# Physical constants
M_sol = 1.989e30  # Solar mass in kg
c = 299792458  # Speed of light in m/s
G = 6.67430e-11  # Gravitational constant
h = 1.7  # Height of human in meters

# Sagittarius A* properties
M_sgr = 4.1e6 * M_sol  # Mass of Sagittarius A* in kg
r_s_sgr = 2 * G * M_sgr / (c**2)  # Schwarzschild radius of Sagittarius A*

print("First-Person 3D Visualization of Black Hole Environment")
print("=" * 55)
print(f"Mass of Sagittarius A*: {M_sgr:.2e} kg")
print(f"Schwarzschild radius: {r_s_sgr:.2e} m")
print()

# Create figure with 3D projection
fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

# Observer position (at a safe distance from the black hole)
observer_distance = r_s_sgr * 1000  # 1000 times Schwarzschild radius
observer_pos = np.array([observer_distance, 0, 0])

# Create black hole at origin
bh_radius = r_s_sgr * 0.1  # Scale for visualization
u = np.linspace(0, 2 * np.pi, 50)
v = np.linspace(0, np.pi, 50)
x_bh = bh_radius * np.outer(np.cos(u), np.sin(v))
y_bh = bh_radius * np.outer(np.sin(u), np.sin(v))
z_bh = bh_radius * np.outer(np.ones(np.size(u)), np.cos(v))

# Plot black hole
ax.plot_surface(x_bh, y_bh, z_bh, color='black', alpha=0.9)

# Create accretion disk (simplified as a series of rings)
disk_radii = np.linspace(r_s_sgr * 1.5, r_s_sgr * 5, 10)
for i, radius in enumerate(disk_radii):
    theta = np.linspace(0, 2*np.pi, 50)
    x_disk = radius * np.cos(theta)
    y_disk = radius * np.sin(theta)
    z_disk = np.zeros_like(x_disk)
    
    # Color based on distance from center (red = closer, yellow = farther)
    norm_dist = i / len(disk_radii)
    color = (1, 1-norm_dist*0.5, 0)  # From red to orange
    ax.plot(x_disk, y_disk, z_disk, color=color, alpha=0.6)

# Create starfield background
num_stars = 200
star_x = np.random.uniform(-observer_distance*2, observer_distance*2, num_stars)
star_y = np.random.uniform(-observer_distance*2, observer_distance*2, num_stars)
star_z = np.random.uniform(-observer_distance, observer_distance, num_stars)

# Filter out stars too close to the black hole
distances = np.sqrt(star_x**2 + star_y**2 + star_z**2)
mask = distances > r_s_sgr * 10
star_x = star_x[mask]
star_y = star_y[mask]
star_z = star_z[mask]

# Plot stars
ax.scatter(star_x, star_y, star_z, c='white', s=1, alpha=0.8)

# Create gravitational lensing effect
# This simulates how light bends around the black hole
lens_points = 50
lens_radius = r_s_sgr * 3
theta_lens = np.linspace(0, 2*np.pi, lens_points)
lens_x = lens_radius * np.cos(theta_lens)
lens_y = lens_radius * np.sin(theta_lens)
lens_z = np.zeros(lens_points)

# Create a ring showing the Einstein ring effect
ax.plot(lens_x, lens_y, lens_z, color='cyan', linewidth=2, alpha=0.7)

# Add some lensed star images
# These are distorted images of stars behind the black hole
for i in range(20):
    angle = np.random.uniform(0, 2*np.pi)
    radius = r_s_sgr * 2.5
    x = radius * np.cos(angle)
    y = radius * np.sin(angle)
    z = np.random.uniform(-r_s_sgr, r_s_sgr)
    ax.scatter(x, y, z, c='cyan', s=5, alpha=0.6)

# Create observer representation (simplified)
observer_size = r_s_sgr * 0.05
ax.scatter(observer_pos[0], observer_pos[1], observer_pos[2], 
           c='blue', s=100, marker='^', alpha=0.8, label='Observer')

# Draw line of sight to black hole
ax.plot([observer_pos[0], 0], [observer_pos[1], 0], [observer_pos[2], 0], 
        'b--', alpha=0.5, linewidth=1)

# Add visual effects for gravitational redshift and time dilation
# This is represented by color changes in the visualization

# Create info panel
info_text = f"""First-Person View Near Sagittarius A*
Observer Distance: {observer_distance/r_s_sgr:.0f} × rₛ
Black Hole Mass: {M_sgr/M_sol:.1f} million solar masses
Schwarzschild Radius: {r_s_sgr:.2e} m

Visual Effects:
• Gravitational lensing (cyan ring)
• Lensed star images (cyan dots)
• Accretion disk (orange/red rings)
• Starfield background
• Event horizon (black sphere)"""

# Add text box
ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=9,
          verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Set labels and title
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.set_zlabel('Z (m)')
ax.set_title('First-Person 3D View Near Sagittarius A*', fontsize=14)

# Set viewing angle to simulate first-person perspective
ax.view_init(elev=0, azim=180)  # Looking directly at the black hole

# Set axis limits
limit = observer_distance * 0.5
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)
ax.set_zlim(-limit/2, limit/2)

# Add legend
ax.legend(loc='upper right')

plt.tight_layout()
plt.savefig('first_person_blackhole_view.png', dpi=300, bbox_inches='tight')
print("First-person 3D visualization saved as 'first_person_blackhole_view.png'")
plt.show()

# Print physical calculations for validation
print("Physical Calculations for Validation:")
print("=" * 40)

# Calculate gravitational effects at observer position
r_obs = observer_distance
# Time dilation factor: γ = 1/sqrt(1 - rₛ/r)
time_dilation = 1 / math.sqrt(1 - r_s_sgr / r_obs)
print(f"Time dilation factor at observer position: {time_dilation:.2f}")

# Gravitational redshift: λ_observed/λ_emitted = sqrt(1 - rₛ/r)
redshift = math.sqrt(1 - r_s_sgr / r_obs)
print(f"Gravitational redshift factor: {redshift:.4f}")

# Tidal force difference across human body
# Tidal force difference: Δg = (2 * G * M * h) / r³
tidal_force = (2 * G * M_sgr * h) / (r_obs**3)
print(f"Tidal force across human body: {tidal_force:.2e} m/s²")

# Angular size of black hole
# Angular diameter: δ = 2 * arcsin(rₛ / r_obs)
angular_diameter = 2 * math.asin(r_s_sgr / r_obs)
print(f"Angular diameter of black hole: {math.degrees(angular_diameter):.4f} degrees")

print()
print("Interpretation:")
print("-" * 15)
print("From this first-person perspective:")
print("1. The black hole would appear as a dark sphere against the starfield")
print("2. An Einstein ring would be visible around the black hole")
print("3. Stars behind the black hole would appear as multiple images")
print("4. The accretion disk would be visible with color gradients")
print("5. Time would appear to slow down compared to distant observers")
print("6. Light from distant sources would be redshifted")