#!/usr/bin/env python3
"""
Particle Extraction System - Main Simulation Runner
Auto-converter using complex equations for GPU computation of particle extraction sequences
"""

import numpy as np
import time
from typing import List, Dict
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Import all system components
from particle_extraction_system import (
    ParticleExtractionSystem, Particle, ParticleState, ParticleType,
    GravitationalField, DimensionalPlate, VoidZone, CrystalGeometryProcessor
)
from gravitational_field_controller import GravitationalFieldController
from dimensional_plate_void_controller import PlateVoidIntegrationController
from crystal_geometry_processor import CrystalGeometryProcessor
from dense_dark_matter_converter import DenseDarkMatterConverter

class ParticleExtractionSimulation:
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self.simulation_time = 0.0
        self.dt = 0.01  # Time step
        self.max_particles = 100
        
        # Initialize main system
        self.extraction_system = ParticleExtractionSystem(use_gpu=use_gpu)
        self.field_controller = GravitationalFieldController(use_gpu=use_gpu)
        self.dark_matter_converter = DenseDarkMatterConverter(use_gpu=use_gpu)
        
        # System components (will be initialized in setup)
        self.dimensional_plate = None
        self.void_zone = None
        self.crystal_processor = None
        self.plate_void_controller = None
        
        # Simulation data
        self.particle_trajectories = {}
        self.system_status_history = []
        
        # Setup the system
        self._setup_system()
    
    def _setup_system(self):
        """Setup the complete particle extraction system"""
        print("Setting up Particle Extraction System...")
        
        # Create dimensional plate
        plate_vertices = self._create_dimensional_plate_vertices()
        self.dimensional_plate = DimensionalPlate(plate_vertices, self.use_gpu)
        self.extraction_system.set_dimensional_plate(self.dimensional_plate)
        
        # Create void zone
        void_center = np.array([0.0, 0.0, -5.0])
        void_radius = 2.0
        self.void_zone = VoidZone(void_center, void_radius)
        self.extraction_system.set_void_zone(self.void_zone)
        
        # Create crystal geometry processor
        crystal_vertices = self._create_crystal_vertices()
        electrode_configs = self._create_electrode_configs()
        self.crystal_processor = CrystalGeometryProcessor(crystal_vertices, electrode_configs, self.use_gpu)
        self.extraction_system.set_crystal_processor(self.crystal_processor)
        
        # Create plate-void integration controller
        self.plate_void_controller = PlateVoidIntegrationController(
            self.dimensional_plate, self.void_zone, self.use_gpu
        )
        
        # Add gravitational fields
        self._setup_gravitational_fields()
        
        # Add initial particles
        self._add_initial_particles()
        
        print("System setup complete!")
    
    def _create_dimensional_plate_vertices(self) -> np.ndarray:
        """Create vertices for dimensional plate"""
        # Create a rectangular plate
        width, height = 4.0, 4.0
        vertices = np.array([
            [-width/2, -height/2, 0.0],
            [width/2, -height/2, 0.0],
            [width/2, height/2, 0.0],
            [-width/2, height/2, 0.0]
        ])
        return vertices
    
    def _create_crystal_vertices(self) -> np.ndarray:
        """Create vertices for crystal geometry"""
        # Create hexagonal prism crystal
        radius = 1.5
        height = 3.0
        
        vertices = []
        # Bottom hexagon
        for i in range(6):
            angle = i * np.pi / 3
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            vertices.append([x, y, -height/2])
        
        # Top hexagon
        for i in range(6):
            angle = i * np.pi / 3
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            vertices.append([x, y, height/2])
        
        return np.array(vertices)
    
    def _create_electrode_configs(self) -> List[Dict]:
        """Create electrode configurations"""
        configs = [
            # Entry electrodes
            {'position': [0.0, -1.5, -1.5], 'orientation': [0, 1, 0], 'max_charge': 100.0},
            {'position': [0.0, 1.5, -1.5], 'orientation': [0, -1, 0], 'max_charge': 100.0},
            
            # Processing electrodes
            {'position': [-1.5, 0.0, 0.0], 'orientation': [1, 0, 0], 'max_charge': 150.0},
            {'position': [1.5, 0.0, 0.0], 'orientation': [-1, 0, 0], 'max_charge': 150.0},
            {'position': [0.0, 0.0, -1.5], 'orientation': [0, 0, 1], 'max_charge': 150.0},
            {'position': [0.0, 0.0, 1.5], 'orientation': [0, 0, -1], 'max_charge': 150.0},
            
            # Exit electrodes
            {'position': [0.0, -1.5, 1.5], 'orientation': [0, 1, 0], 'max_charge': 120.0},
            {'position': [0.0, 1.5, 1.5], 'orientation': [0, -1, 0], 'max_charge': 120.0},
        ]
        
        return configs
    
    def _setup_gravitational_fields(self):
        """Setup gravitational fields in the system"""
        # Core gravitational field
        core_field = GravitationalField(
            field_strength=50.0,
            field_center=np.array([0.0, 0.0, 2.0])
        )
        self.extraction_system.add_gravitational_field(core_field)
        
        # Surrounding fields
        for i in range(4):
            angle = i * np.pi / 2
            field_pos = np.array([
                3.0 * np.cos(angle),
                3.0 * np.sin(angle),
                1.0
            ])
            surrounding_field = GravitationalField(
                field_strength=20.0,
                field_center=field_pos
            )
            self.extraction_system.add_gravitational_field(surrounding_field)
    
    def _add_initial_particles(self):
        """Add initial particles to the system"""
        print("Adding initial particles...")
        
        for i in range(20):  # Start with 20 particles
            particle = self._create_particle(i)
            self.extraction_system.add_particle(particle)
            self.particle_trajectories[particle.id] = [particle.position.copy()]
        
        print(f"Added {len(self.extraction_system.particles)} particles")
    
    def _create_particle(self, particle_id: int) -> Particle:
        """Create a single particle with random properties"""
        # Random position above the system
        position = np.array([
            np.random.uniform(-3, 3),
            np.random.uniform(-3, 3),
            np.random.uniform(5, 8)
        ])
        
        # Random velocity (generally downward)
        velocity = np.array([
            np.random.uniform(-1, 1),
            np.random.uniform(-1, 1),
            np.random.uniform(-3, -1)
        ])
        
        # Random properties
        mass = np.random.uniform(0.5, 3.0)
        density = np.random.uniform(100, 800)
        charge = np.random.uniform(-5, 5)
        
        # Particle type (70% red, 30% blue)
        particle_type = ParticleType.RED_PARTICLE if np.random.random() < 0.7 else ParticleType.BLUE_PARTICLE
        
        # Initial trajectory vector
        trajectory_vector = velocity / np.linalg.norm(velocity)
        
        return Particle(
            id=particle_id,
            position=position,
            velocity=velocity,
            mass=mass,
            density=density,
            charge=charge,
            particle_type=particle_type,
            state=ParticleState.ACTIVE,
            trajectory_vector=trajectory_vector,
            gravitational_strength=mass * 9.81
        )
    
    def run_simulation_step(self):
        """Run a single simulation step"""
        # Count red particles for field destabilization
        red_particle_count = sum(1 for p in self.extraction_system.particles 
                               if p.particle_type == ParticleType.RED_PARTICLE)
        
        # Apply gravitational field destabilization
        if red_particle_count > 5:
            self.field_controller.apply_sequence_forcing(
                self.extraction_system.gravitational_fields,
                red_particle_count
            )
        
        # Update main extraction system
        self.extraction_system.update_system(self.dt)
        
        # Update crystal processor
        self.crystal_processor.update_processing_system(self.dt)
        
        # Process plate-void integration
        for particle in self.extraction_system.particles:
            self.plate_void_controller.process_particle_extraction_sequence(particle)
        
        # Apply dark matter physics
        for particle in self.extraction_system.particles:
            if particle.state == ParticleState.DENSE_DARK_MATTER:
                self.dark_matter_converter.apply_dark_matter_physics(particle, self.dt)
        
        # Calculate dark matter interactions
        self.dark_matter_converter.calculate_dark_matter_interactions(self.extraction_system.particles)
        
        # Record particle trajectories
        for particle in self.extraction_system.particles:
            if particle.id not in self.particle_trajectories:
                self.particle_trajectories[particle.id] = []
            self.particle_trajectories[particle.id].append(particle.position.copy())
        
        # Record system status
        status = self.extraction_system.get_system_status()
        status['simulation_time'] = self.simulation_time
        self.system_status_history.append(status)
        
        # Add new particles occasionally
        if len(self.extraction_system.particles) < self.max_particles and np.random.random() < 0.1:
            new_particle = self._create_particle(max(self.particle_trajectories.keys()) + 1)
            self.extraction_system.add_particle(new_particle)
            self.particle_trajectories[new_particle.id] = [new_particle.position.copy()]
        
        # Remove particles that have gone too far
        particles_to_remove = []
        for particle in self.extraction_system.particles:
            if np.linalg.norm(particle.position) > 20.0:
                particles_to_remove.append(particle)
        
        for particle in particles_to_remove:
            self.extraction_system.particles.remove(particle)
        
        # Update simulation time
        self.simulation_time += self.dt
    
    def run_simulation(self, duration: float = 10.0, print_interval: float = 1.0):
        """Run the complete simulation"""
        print(f"Starting simulation for {duration} seconds...")
        print(f"Using GPU: {self.use_gpu}")
        print("-" * 50)
        
        steps = int(duration / self.dt)
        print_steps = int(print_interval / self.dt)
        
        start_time = time.time()
        
        for step in range(steps):
            self.run_simulation_step()
            
            # Print status periodically
            if step % print_steps == 0:
                status = self.extraction_system.get_system_status()
                print(f"Time: {self.simulation_time:.2f}s | "
                      f"Particles: {status['total_particles']} | "
                      f"Red: {status['red_particles']} | "
                      f"Processed: {status['particle_states']['processed']} | "
                      f"Dark Matter: {status['particle_states']['dense_dark_matter']}")
        
        end_time = time.time()
        print(f"\nSimulation completed in {end_time - start_time:.2f} seconds")
        self.print_final_statistics()
    
    def print_final_statistics(self):
        """Print final simulation statistics"""
        print("\n" + "="*60)
        print("FINAL SIMULATION STATISTICS")
        print("="*60)
        
        status = self.extraction_system.get_system_status()
        conversion_stats = self.dark_matter_converter.get_conversion_statistics()
        integration_status = self.plate_void_controller.get_integration_status()
        crystal_status = self.crystal_processor.get_processing_status()
        
        print(f"\nParticle Statistics:")
        print(f"  Total Particles: {status['total_particles']}")
        print(f"  Red Particles: {status['red_particles']}")
        print(f"  Blue Particles: {status['blue_particles']}")
        print(f"  Processed: {status['particle_states']['processed']}")
        print(f"  Dense Dark Matter: {status['particle_states']['dense_dark_matter']}")
        print(f"  Active: {status['particle_states']['active']}")
        
        print(f"\nGravitational Field Statistics:")
        print(f"  Active Fields: {status['gravitational_fields_active']}")
        field_stability = self.field_controller.monitor_field_stability(
            self.extraction_system.gravitational_fields
        )
        print(f"  Destabilized Fields: {field_stability['destabilized_fields']}")
        print(f"  Critical Fields: {field_stability['critical_fields']}")
        
        print(f"\nDark Matter Conversion:")
        print(f"  Total Conversions: {conversion_stats['total_conversions']}")
        print(f"  Average Conversion Probability: {conversion_stats['average_conversion_probability']:.3f}")
        print(f"  Average Stability Index: {conversion_stats['average_stability_index']:.3f}")
        
        print(f"\nCrystal Processing:")
        print(f"  Active Electrodes: {crystal_status['active_electrodes']}")
        print(f"  Charging Electrodes: {crystal_status['charging_electrodes']}")
        print(f"  Crystal Resonance: {crystal_status['crystal_resonance_active']}")
        
        print(f"\nPlate-Void Integration:")
        print(f"  Processed Particles: {integration_status['processed_particles']}")
        print(f"  Watchdog Alerts: {integration_status['watchdog_counts']}")
        print(f"  Void Destruction Active: {integration_status['void_destruction_active']}")
    
    def visualize_simulation(self):
        """Create visualization of the simulation"""
        fig = plt.figure(figsize=(15, 10))
        
        # 3D trajectory plot
        ax1 = fig.add_subplot(221, projection='3d')
        self._plot_particle_trajectories(ax1)
        
        # Particle state distribution
        ax2 = fig.add_subplot(222)
        self._plot_particle_states(ax2)
        
        # System status over time
        ax3 = fig.add_subplot(223)
        self._plot_system_status(ax3)
        
        # Dark matter conversion statistics
        ax4 = fig.add_subplot(224)
        self._plot_conversion_stats(ax4)
        
        plt.tight_layout()
        plt.show()
    
    def _plot_particle_trajectories(self, ax):
        """Plot particle trajectories in 3D"""
        for particle_id, trajectory in self.particle_trajectories.items():
            if len(trajectory) > 1:
                trajectory_array = np.array(trajectory)
                ax.plot(trajectory_array[:, 0], 
                       trajectory_array[:, 1], 
                       trajectory_array[:, 2], 
                       alpha=0.6, linewidth=1)
        
        # Plot system components
        if self.dimensional_plate:
            plate_vertices = self.dimensional_plate.plate_vertices
            ax.plot(plate_vertices[:, 0], plate_vertices[:, 1], plate_vertices[:, 2], 
                   'k-', linewidth=2, label='Dimensional Plate')
        
        if self.void_zone:
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 20)
            x = self.void_zone.void_radius * np.outer(np.cos(u), np.sin(v)) + self.void_zone.void_center[0]
            y = self.void_zone.void_radius * np.outer(np.sin(u), np.sin(v)) + self.void_zone.void_center[1]
            z = self.void_zone.void_radius * np.outer(np.ones(np.size(u)), np.cos(v)) + self.void_zone.void_center[2]
            ax.plot_surface(x, y, z, alpha=0.3, color='red', label='Void Zone')
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Particle Trajectories')
        ax.legend()
    
    def _plot_particle_states(self, ax):
        """Plot particle state distribution"""
        status = self.extraction_system.get_system_status()
        states = list(status['particle_states'].keys())
        counts = list(status['particle_states'].values())
        
        bars = ax.bar(states, counts, color=['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'black'])
        ax.set_xlabel('Particle State')
        ax.set_ylabel('Count')
        ax.set_title('Particle State Distribution')
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{count}', ha='center', va='bottom')
    
    def _plot_system_status(self, ax):
        """Plot system status over time"""
        if not self.system_status_history:
            return
        
        times = [status['simulation_time'] for status in self.system_status_history]
        total_particles = [status['total_particles'] for status in self.system_status_history]
        processed_particles = [status['particle_states']['processed'] for status in self.system_status_history]
        dark_matter_particles = [status['particle_states']['dense_dark_matter'] for status in self.system_status_history]
        
        ax.plot(times, total_particles, label='Total Particles', linewidth=2)
        ax.plot(times, processed_particles, label='Processed', linewidth=2)
        ax.plot(times, dark_matter_particles, label='Dark Matter', linewidth=2)
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Count')
        ax.set_title('System Status Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_conversion_stats(self, ax):
        """Plot dark matter conversion statistics"""
        conversion_stats = self.dark_matter_converter.get_conversion_statistics()
        
        if conversion_stats['total_conversions'] > 0:
            # Create pie chart of conversion efficiency
            labels = ['Converted', 'Not Converted']
            sizes = [conversion_stats['total_conversions'], 
                    conversion_stats['total_conversions'] / max(conversion_stats['average_conversion_probability'], 0.01) - conversion_stats['total_conversions']]
            colors = ['gold', 'lightgray']
            
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.set_title(f'Dark Matter Conversion\n(Efficiency: {conversion_stats["average_conversion_probability"]:.3f})')
        else:
            ax.text(0.5, 0.5, 'No Dark Matter Conversions', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Dark Matter Conversion Statistics')

def main():
    """Main function to run the simulation"""
    print("="*60)
    print("PARTICLE EXTRACTION SYSTEM")
    print("Auto-Converter with GPU Computation")
    print("="*60)
    
    # Force CPU mode due to CUDA driver issues
    use_gpu = True
    print("GPU acceleration disabled - using CPU computation")
    
    # Create and run simulation
    sim = ParticleExtractionSimulation(use_gpu=use_gpu)
    
    # Run simulation for 10 seconds
    sim.run_simulation(duration=10.0, print_interval=1.0)
    
    # Visualize results
    print("\nGenerating visualization...")
    sim.visualize_simulation()

if __name__ == "__main__":
    main()
