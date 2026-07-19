import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import math

class MassVelocitySystem:
    def __init__(self):
        self.G = 6.67430e-11  # Gravitational constant
        self.c = 299792458    # Speed of light (m/s)
        self.dt = 0.01        # Time step
        self.pi_squared = np.pi**2  # π² for calculations
        
    def calculate_masvelocity(self, light_intensity, mass, x4_factor=4):
        """Calculate MASVECLOCITY: Light L × MASVECLOCITY × X4 / π² of ± states"""
        return (light_intensity * mass * x4_factor) / self.pi_squared
    
    def calculate_frcms(self, mass, velocity, radius, resistance_coeff, encounter_radius=6):
        """Calculate FRCMS: Force Resistance Circular Mass System"""
        centripetal_force = self.calculate_circular_force(mass, velocity, radius)
        resistance_force = self.calculate_resistance_force(velocity, resistance_coeff)
        
        # Encounter radius effect (6D as specified)
        encounter_factor = encounter_radius / radius
        
        # FRCMS combines circular motion with resistance and encounter effects
        frcms_force = (centripetal_force + resistance_force) * encounter_factor
        return frcms_force
    
    def calculate_hz_cons_velocity(self, angular_velocity, frequency_multiplier=1):
        """Calculate HZCONS VELOCITY: Hz constant velocity relationship"""
        frequency = self.calculate_hz_frequency(angular_velocity)
        return angular_velocity * frequency_multiplier * 2 * np.pi
    
    def calculate_light_density_intensity(self, energy, volume, mass_threshold):
        """Calculate FRCDENSITY: Force Resistance Circular Density"""
        base_density = energy / volume
        
        # Set to mass above HZ circumference threshold
        if mass_threshold > 2 * np.pi:  # HZ circumference condition
            return base_density * mass_threshold
        return base_density
    
    def calculate_mass_momentum(self, mass, velocity):
        """Calculate mass momentum: p = mv"""
        return mass * velocity
    
    def calculate_interleving_energy(self, mass, velocity, light_intensity):
        """Calculate interleving energy between mass and light"""
        # Kinetic energy + light interaction energy
        kinetic_energy = 0.5 * mass * velocity**2
        light_energy = light_intensity * velocity * 0.01  # Light coupling factor
        return kinetic_energy + light_energy
    
    def calculate_force_of_movement(self, mass, velocity, light_intensity, radius):
        """Calculate force of movement with light interactions"""
        # Base movement force from momentum change
        momentum = self.calculate_mass_momentum(mass, velocity)
        
        # Light pressure contribution
        light_pressure = light_intensity / (self.c * 4 * np.pi * radius**2)
        
        # Total force of movement
        movement_force = momentum * light_pressure * 0.001  # Scaling factor
        return movement_force
    
    def calculate_rshzvlc_state(self, velocity, light_density, resonance_factor=np.pi):
        """Calculate RSHZVLC STATE: Resonance State with velocity and light density"""
        # Resonance at mass object with positive volume
        resonance_amplitude = resonance_factor * light_density * velocity
        
        # Dissipate resonance based on velocity matching light density
        if abs(velocity - light_density) < 0.1:  # Matching condition
            resonance_amplitude *= 0.5  # Dissipation factor
            
        return resonance_amplitude
    
    def calculate_conformal_angular_velocity(self, base_angular_velocity, velocity, surface_factor=6):
        """Calculate conformal angular velocity with cos(v) transformation"""
        # Create cos(v) to conformal 6 of angular velocity in surface
        cos_v = np.cos(velocity / self.c)  # Normalized by speed of light
        conformal_factor = surface_factor * cos_v
        
        return base_angular_velocity * conformal_factor
    
    def simulate_light_mass_collision(self, light_intensity, mass, velocity, radius):
        """Simulate collision of light with mass object"""
        # Calculate MASVECLOCITY
        masvelocity = self.calculate_masvelocity(light_intensity, mass)
        
        # Check if velocities match light density condition
        light_density = self.calculate_light_density_intensity(light_intensity, 4/3*np.pi*radius**3, mass)
        velocity_match = abs(velocity - light_density) < 0.1
        
        # Calculate resonance
        resonance = self.calculate_rshzvlc_state(velocity, light_density)
        
        # Update to new metric if conditions met
        if velocity_match:
            new_velocity = masvelocity * resonance
        else:
            new_velocity = velocity
            
        return new_velocity, resonance, velocity_match
        
    def calculate_circular_force(self, mass, velocity, radius):
        """Calculate centripetal force for circular motion"""
        return (mass * velocity**2) / radius
    
    def calculate_angular_velocity(self, velocity, radius):
        """Calculate angular velocity from linear velocity"""
        return velocity / radius
    
    def calculate_circumference(self, radius):
        """Calculate circumference of circular path"""
        return 2 * np.pi * radius
    
    def calculate_resistance_force(self, velocity, resistance_coefficient):
        """Calculate resistance force opposing motion"""
        return -resistance_coefficient * velocity**2
    
    def calculate_hz_frequency(self, angular_velocity):
        """Calculate frequency in Hz from angular velocity"""
        return angular_velocity / (2 * np.pi)
    
    def calculate_relativistic_mass(self, rest_mass, velocity):
        """Calculate relativistic mass increase"""
        if velocity >= self.c:
            return float('inf')
        gamma = 1 / np.sqrt(1 - (velocity/self.c)**2)
        return rest_mass * gamma
    
    def calculate_light_density_intensity(self, energy, volume, mass_threshold):
        """Calculate FRCDENSITY: Force Resistance Circular Density"""
        base_density = energy / volume
        
        # Set to mass above HZ circumference threshold
        if mass_threshold > 2 * np.pi:  # HZ circumference condition
            return base_density * mass_threshold
        return base_density
    
    def calculate_mass_momentum(self, mass, velocity):
        """Calculate mass momentum: p = mv"""
        return mass * velocity
    
    def calculate_interleving_energy(self, mass, velocity, light_intensity):
        """Calculate interleving energy between mass and light"""
        # Kinetic energy + light interaction energy
        kinetic_energy = 0.5 * mass * velocity**2
        light_energy = light_intensity * velocity * 0.01  # Light coupling factor
        return kinetic_energy + light_energy
    
    def calculate_force_of_movement(self, mass, velocity, light_intensity, radius):
        """Calculate force of movement with light interactions"""
        # Base movement force from momentum change
        momentum = self.calculate_mass_momentum(mass, velocity)
        
        # Light pressure contribution
        light_pressure = light_intensity / (self.c * 4 * np.pi * radius**2)
        
        # Total force of movement
        movement_force = momentum * light_pressure * 0.001  # Scaling factor
        return movement_force
    
    def simulate_advanced_circular_motion(self, mass, initial_velocity, radius, resistance_coeff, 
                                         light_intensity, duration):
        """Advanced simulation with light-mass interactions and conformal physics"""
        time_steps = int(duration / self.dt)
        time = np.linspace(0, duration, time_steps)
        
        # Initialize arrays
        velocity = np.zeros(time_steps)
        angular_velocity = np.zeros(time_steps)
        conformal_angular_velocity = np.zeros(time_steps)
        force = np.zeros(time_steps)
        resistance = np.zeros(time_steps)
        frcms_force = np.zeros(time_steps)
        resonance = np.zeros(time_steps)
        light_density = np.zeros(time_steps)
        
        velocity[0] = initial_velocity
        angular_velocity[0] = self.calculate_angular_velocity(initial_velocity, radius)
        
        for i in range(1, time_steps):
            # Calculate light density and intensity
            volume = 4/3 * np.pi * radius**3
            light_density[i] = self.calculate_light_density_intensity(light_intensity, volume, mass)
            
            # Light-mass collision effects with bounds checking
            new_velocity, resonance_amplitude, velocity_match = self.simulate_light_mass_collision(
                light_intensity, mass, velocity[i-1], radius
            )
            resonance[i] = resonance_amplitude
            
            # Update velocity based on collision with bounds
            if velocity_match and np.isfinite(new_velocity):
                velocity[i] = np.clip(new_velocity, 0, 100)  # Limit max velocity
            else:
                # Traditional force calculations with overflow protection
                velocity_clipped = np.clip(velocity[i-1], 0, 50)  # Prevent overflow
                centripetal_force = self.calculate_circular_force(mass, velocity_clipped, radius)
                resistance_force = self.calculate_resistance_force(velocity_clipped, resistance_coeff)
                
                # FRCMS calculation with bounds
                if np.isfinite(centripetal_force) and np.isfinite(resistance_force):
                    frcms_force[i] = self.calculate_frcms(mass, velocity_clipped, radius, resistance_coeff)
                    net_force = np.clip(frcms_force[i], -1000, 1000)  # Limit force
                else:
                    net_force = 0
                    frcms_force[i] = 0
                
                # Update velocity
                acceleration = net_force / mass
                velocity[i] = velocity[i-1] + acceleration * self.dt
                velocity[i] = max(0, velocity[i])
            
            # Calculate angular velocities with bounds
            angular_velocity[i] = self.calculate_angular_velocity(velocity[i], radius)
            conformal_angular_velocity[i] = self.calculate_conformal_angular_velocity(
                angular_velocity[i], velocity[i]
            )
            
            # Store traditional forces for comparison
            force[i] = self.calculate_circular_force(mass, velocity[i], radius)
            resistance[i] = self.calculate_resistance_force(velocity[i], resistance_coeff)
        
        return time, velocity, angular_velocity, conformal_angular_velocity, force, resistance, frcms_force, resonance, light_density

class PhysicsVisualizer:
    def __init__(self, system):
        self.system = system
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
    def plot_advanced_physics(self, mass, initial_velocity, radius, resistance_coeff, light_intensity):
        """Plot advanced physics simulation with light-mass interactions"""
        duration = 10.0
        time, velocity, angular_velocity, conformal_angular_velocity, force, resistance, frcms_force, resonance, light_density = self.system.simulate_advanced_circular_motion(
            mass, initial_velocity, radius, resistance_coeff, light_intensity, duration
        )
        
        # Create subplot layout
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Plot 1: Velocity comparison
        ax1.plot(time, velocity, 'b-', label='Linear Velocity (m/s)', linewidth=2)
        ax1.plot(time, angular_velocity, 'r-', label='Angular Velocity (rad/s)', linewidth=2)
        ax1.plot(time, conformal_angular_velocity, 'g--', label='Conformal Angular Velocity', linewidth=2)
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Velocity')
        ax1.set_title('Velocity Components vs Time')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Force comparison
        ax2.plot(time, force, 'b-', label='Centripetal Force (N)', linewidth=2)
        ax2.plot(time, np.abs(resistance), 'orange', label='Resistance Force (N)', linewidth=2)
        ax2.plot(time, frcms_force, 'purple', label='FRCMS Force (N)', linewidth=2)
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Force (N)')
        ax2.set_title('Force Components vs Time')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Light-mass interactions
        ax3.plot(time, light_density, 'yellow', label='Light Density', linewidth=2)
        ax3.plot(time, resonance, 'red', label='Resonance Amplitude', linewidth=2)
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Intensity')
        ax3.set_title('Light-Mass Interactions')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Phase space (velocity vs angular velocity)
        ax4.plot(velocity, angular_velocity, 'b-', linewidth=2)
        ax4.scatter(velocity[0], angular_velocity[0], color='green', s=100, label='Start', zorder=5)
        ax4.scatter(velocity[-1], angular_velocity[-1], color='red', s=100, label='End', zorder=5)
        ax4.set_xlabel('Linear Velocity (m/s)')
        ax4.set_ylabel('Angular Velocity (rad/s)')
        ax4.set_title('Phase Space Trajectory')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        return time, velocity, angular_velocity, conformal_angular_velocity, force, resistance, frcms_force, resonance, light_density
    
    def animate_circular_motion(self, mass, velocity, radius):
        """Animate circular motion"""
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_xlim(-radius*1.5, radius*1.5)
        ax.set_ylim(-radius*1.5, radius*1.5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        # Draw circular path
        circle = Circle((0, 0), radius, fill=False, edgecolor='gray', linestyle='--')
        ax.add_patch(circle)
        
        # Initialize mass point
        mass_point, = ax.plot([], [], 'ro', markersize=10, label=f'Mass: {mass} kg')
        trail, = ax.plot([], [], 'b-', alpha=0.3, linewidth=1)
        
        # Trail data
        trail_x, trail_y = [], []
        
        angular_velocity = self.system.calculate_angular_velocity(velocity, radius)
        
        def init():
            mass_point.set_data([], [])
            trail.set_data([], [])
            return mass_point, trail
        
        def animate(frame):
            angle = angular_velocity * frame * 0.1
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            mass_point.set_data([x], [y])
            
            # Update trail
            trail_x.append(x)
            trail_y.append(y)
            if len(trail_x) > 50:  # Keep trail length limited
                trail_x.pop(0)
                trail_y.pop(0)
            trail.set_data(trail_x, trail_y)
            
            return mass_point, trail
        
        anim = FuncAnimation(fig, animate, init_func=init, frames=200, 
                           interval=50, blit=True, repeat=True)
        
        ax.legend()
        ax.set_title(f'Circular Motion Animation\nVelocity: {velocity} m/s, Radius: {radius} m')
        plt.show()
        
        return anim

def main():
    # Initialize physics system
    system = MassVelocitySystem()
    visualizer = PhysicsVisualizer(system)
    
    # Simulation parameters
    mass = 10.0  # kg
    initial_velocity = 33333.0  # m/s - set to 33333 as requested
    radius = 2.0  # m
    resistance_coeff = 0.1  # resistance coefficient
    light_intensity = 8.0  # light intensity for MASVECLOCITY calculations
    
    print("=== Advanced Mass-Velocity-Light Physics Simulation ===")
    print(f"Mass: {mass} kg")
    print(f"Initial Velocity: {initial_velocity} m/s")
    print(f"Radius: {radius} m")
    print(f"Resistance Coefficient: {resistance_coeff}")
    print(f"Light Intensity: {light_intensity}")
    print()
    
    # Calculate initial values
    circumference = system.calculate_circumference(radius)
    angular_velocity = system.calculate_angular_velocity(initial_velocity, radius)
    centripetal_force = system.calculate_circular_force(mass, initial_velocity, radius)
    frequency = system.calculate_hz_frequency(angular_velocity)
    
    # New physics calculations
    masvelocity = system.calculate_masvelocity(light_intensity, mass)
    frcms_force = system.calculate_frcms(mass, initial_velocity, radius, resistance_coeff)
    hz_cons_velocity = system.calculate_hz_cons_velocity(angular_velocity)
    volume = 4/3 * np.pi * radius**3
    light_density = system.calculate_light_density_intensity(light_intensity, volume, mass)
    resonance = system.calculate_rshzvlc_state(initial_velocity, light_density)
    conformal_angular_velocity = system.calculate_conformal_angular_velocity(angular_velocity, initial_velocity)
    
    # Additional calculations for mass momentum and interleving energy
    mass_momentum = system.calculate_mass_momentum(mass, initial_velocity)
    interleving_energy = system.calculate_interleving_energy(mass, initial_velocity, light_intensity)
    force_of_movement = system.calculate_force_of_movement(mass, initial_velocity, light_intensity, radius)
    
    print("=== Initial Calculations ===")
    print(f"Circumference: {circumference:.2f} m")
    print(f"Angular Velocity: {angular_velocity:.2f} rad/s")
    print(f"Frequency: {frequency:.2f} Hz")
    print(f"Centripetal Force: {centripetal_force:.2f} N")
    print()
    print("=== Advanced Physics Calculations ===")
    print(f"MASVECLOCITY: {masvelocity:.4f}")
    print(f"FRCMS Force: {frcms_force:.2f} N")
    print(f"HZCONS Velocity: {hz_cons_velocity:.2f}")
    print(f"Light Density: {light_density:.4f}")
    print(f"Resonance Amplitude: {resonance:.4f}")
    print(f"Conformal Angular Velocity: {conformal_angular_velocity:.4f} rad/s")
    print()
    print("=== Mass Momentum & Energy Calculations ===")
    print(f"Mass Momentum: {mass_momentum:.2f} kg⋅m/s")
    print(f"Interleving Energy: {interleving_energy:.2e} J")
    print(f"Force of Movement: {force_of_movement:.2e} N")
    print()
    
    # Run advanced simulation
    print("Running advanced simulation with light-mass interactions...")
    time, velocity, angular_vel, conformal_angular_vel, force, resistance, frcms_forces, resonance_values, light_density_values = visualizer.plot_advanced_physics(
        mass, initial_velocity, radius, resistance_coeff, light_intensity
    )
    
    # Show animation
    print("Showing animation...")
    anim = visualizer.animate_circular_motion(mass, initial_velocity, radius)
    
    # Final statistics
    print("\n=== Advanced Simulation Results ===")
    print(f"Final Velocity: {velocity[-1]:.2f} m/s")
    print(f"Final Angular Velocity: {angular_vel[-1]:.2f} rad/s")
    print(f"Final Conformal Angular Velocity: {conformal_angular_vel[-1]:.4f} rad/s")
    print(f"Final Resonance: {resonance_values[-1]:.4f}")
    print(f"Final Light Density: {light_density_values[-1]:.4f}")
    print(f"Velocity Loss: {((initial_velocity - velocity[-1]) / initial_velocity * 100):.1f}%")
    print(f"Peak Resonance: {np.max(resonance_values):.4f}")
    print(f"Average FRCMS Force: {np.mean(frcms_forces):.2f} N")

if __name__ == "__main__":
    main()
