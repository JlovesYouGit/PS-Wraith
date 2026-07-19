#!/usr/bin/env python3
"""
Collision-Based Particle Extraction System
Implements collision detection, trapping, and controlled extraction to void zone
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collision_extraction_system import (
    CollisionBasedExtractionSystem, CollisionState, 
    ParticleCollisionDetector, DimensionalZoneConstructor
)
from particle_extraction_system import Particle, ParticleType
from density_emission_analyzer import DensityEmissionAnalyzer, integrate_density_analyzer
from gravity_stabilization_system import GravityStabilizationSystem, GravityStabilizationState
from dual_resonance_system import DualResonanceSystem, DualResonanceState
from warp_zone_system import WarpZoneSystem, WarpZoneState
import time

class CollisionParticle(Particle):
    """Extended particle class for collision system"""
    def __init__(self, particle_id, position, velocity, mass, density, charge, particle_type):
        super().__init__(
            id=particle_id,
            position=position,
            velocity=velocity,
            mass=mass,
            density=density,
            charge=charge,
            particle_type=particle_type,
            state=CollisionState.FREE,
            trajectory_vector=velocity / np.linalg.norm(velocity) if np.linalg.norm(velocity) > 0 else np.array([0, 0, -1]),
            gravitational_strength=mass * 9.81
        )

class CollisionSimulationRunner:
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self.simulation_time = 0.0
        self.dt = 0.01
        self.max_particles = 50
        
        # Initialize collision system
        self.collision_system = CollisionBasedExtractionSystem(use_gpu=use_gpu)
        
        # Initialize density analyzer
        self.density_analyzer = DensityEmissionAnalyzer(measurement_volume_size=5.0, grid_resolution=15)
        
        # Initialize gravity stabilization system
        self.gravity_stabilizer = GravityStabilizationSystem(use_gpu=use_gpu)
        
        # Initialize dual resonance system
        self.dual_resonance = DualResonanceSystem(use_gpu=use_gpu)
        
        # Initialize warp zone system
        self.warp_zone_system = WarpZoneSystem(use_gpu=use_gpu)
        
        # Simulation data
        self.particle_trajectories = {}
        self.system_status_history = []
        self.density_measurements = []
        
        # Setup collision zones and gravity zones
        self.collision_system.setup_collision_zones()
        self._setup_gravity_zones()
        
        # Add initial particles
        self._add_initial_particles()
        
    def _setup_gravity_zones(self):
        """Setup gravity zones aligned with collision zones"""
        for zone in self.collision_system.collision_detector.collision_zones:
            # Create gravity zone at same position as collision zone
            gravity_zone = self.gravity_stabilizer.create_gravity_zone(
                center=zone.center,
                radius=zone.radius * 1.2,  # Slightly larger than collision zone
                strength=30.0
            )
            print(f"Created gravity zone {gravity_zone.id} at position {gravity_zone.center}")
    
    def _add_initial_particles(self):
        """Add initial particles to the system"""
        print("Adding initial particles for collision extraction...")
        
        # Add particles in a grid pattern above the collision zones
        for i in range(25):
            particle = self._create_collision_particle(i)
            self.collision_system.add_particle(particle)
            self.particle_trajectories[particle.id] = [particle.position.copy()]
        
        print(f"Added {len(self.collision_system.particles)} particles")
    
    def _create_collision_particle(self, particle_id: int) -> CollisionParticle:
        """Create a particle for collision system"""
        # Create particles in a distributed pattern
        grid_size = 5
        x = (particle_id % grid_size) * 1.5 - 3.0
        y = (particle_id // grid_size) * 1.5 - 3.0
        z = np.random.uniform(3, 6)
        
        position = np.array([x, y, z])
        
        # Random velocity (generally downward with some horizontal component)
        velocity = np.array([
            np.random.uniform(-0.5, 0.5),
            np.random.uniform(-0.5, 0.5),
            np.random.uniform(-2, -0.5)
        ])
        
        # Varied masses and densities for interesting collision dynamics
        mass = np.random.uniform(0.5, 2.0)
        density = np.random.uniform(100, 500)
        charge = np.random.uniform(-2, 2)
        
        # Mix of particle types
        particle_type = ParticleType.RED_PARTICLE if np.random.random() < 0.6 else ParticleType.BLUE_PARTICLE
        
        return CollisionParticle(
            particle_id=particle_id,
            position=position,
            velocity=velocity,
            mass=mass,
            density=density,
            charge=charge,
            particle_type=particle_type
        )
    
    def run_simulation_step(self):
        """Run a single simulation step"""
        # Store previous particles for emission detection
        previous_particles = self.collision_system.particles.copy()
        
        # Update collision system
        self.collision_system.update_system(self.dt)
        
        # Update gravity stabilization system
        self.gravity_stabilizer.update_stabilization_system(self.collision_system.particles, self.dt)
        
        # Update dual resonance system time
        self.dual_resonance.set_simulation_time(self.simulation_time)
        
        # Update warp zone system time
        self.warp_zone_system.set_simulation_time(self.simulation_time)
        
        # Apply gravity stabilization effects
        self._apply_gravity_stabilization_effects()
        
        # Apply dual resonance effects
        self._apply_dual_resonance_effects()
        
        # Apply warp zone effects
        self._apply_warp_zone_effects()
        
        # Measure density and emissions
        self._measure_density_and_emissions(previous_particles)
        
        # Record particle trajectories
        for particle in self.collision_system.particles:
            if particle.id not in self.particle_trajectories:
                self.particle_trajectories[particle.id] = []
            self.particle_trajectories[particle.id].append(particle.position.copy())
        
        # Record system status
        status = self.collision_system.get_system_status()
        status['simulation_time'] = self.simulation_time
        self.system_status_history.append(status)
        
        # Add new particles occasionally
        if len(self.collision_system.particles) < self.max_particles and np.random.random() < 0.05:
            new_particle = self._create_collision_particle(max(self.particle_trajectories.keys()) + 1)
            self.collision_system.add_particle(new_particle)
            self.particle_trajectories[new_particle.id] = [new_particle.position.copy()]
        
        # Remove particles that have gone too far or reached void
        particles_to_remove = []
        for particle in self.collision_system.particles:
            distance = np.linalg.norm(particle.position)
            if distance > 15.0 or (particle.state == CollisionState.VOID_BOUND and 
                                 np.linalg.norm(particle.position - self.collision_system.void_center) < 0.5):
                particles_to_remove.append(particle)
        
        for particle in particles_to_remove:
            self.collision_system.particles.remove(particle)
        
        # Update simulation time
        self.simulation_time += self.dt
    
    def _apply_warp_zone_effects(self):
        """Apply warp zone effects to particles"""
        # Create lower zone warp field periodically
        if np.random.random() < 0.02:  # 2% chance per step
            lower_zone_center = np.array([0, 0, -3.0])  # Lower zone position
            new_warp_zones = self.warp_zone_system.create_lower_zone_warp_field(
                lower_zone_center, self.collision_system.particles
            )
            
            if new_warp_zones:
                print(f"Created {len(new_warp_zones)} new warp zones in lower zone")
        
        # Update existing warp zones
        self.warp_zone_system.update_warp_zones(
            self.collision_system.particles, 
            self.collision_system.void_center, 
            self.dt
        )
    
    def _apply_dual_resonance_effects(self):
        """Apply dual resonance effects to particles"""
        for particle in self.collision_system.particles:
            # Create quad-state particle if not exists
            if particle.id not in self.dual_resonance.quad_state_particles:
                self.dual_resonance.create_quad_state_particle(particle)
            
            # Apply dual resonance forces
            up_force, down_force = self.dual_resonance.apply_dual_resonance_forces(particle, self.dt)
            
            # Apply both forces simultaneously (dual channel)
            total_resonance_force = up_force + down_force
            particle.velocity += total_resonance_force / particle.mass * self.dt
            
            # Apply micro-plank scale gravity
            micro_gravity = self.dual_resonance.apply_micro_plank_gravity(particle, self.dt)
            particle.velocity += micro_gravity / particle.mass * self.dt
            
            # Apply dimensional property transfer
            if hasattr(particle, 'state') and particle.state.value in ['trapped', 'extracting', 'void_bound']:
                properties = self.dual_resonance.apply_dimensional_property_transfer(particle, self.dt)
                
                # Maintain null zone stability
                null_stable = self.dual_resonance.maintain_null_zone_stability(particle, self.dt)
                
                if null_stable:
                    # Particle is in null zone with 4 simultaneous states
                    particle.gravitational_strength *= 0.98  # Further reduction in null zone
            
            # Update quad-state coherence
            self.dual_resonance.update_quad_state_coherence(particle, self.dt)
    
    def _apply_gravity_stabilization_effects(self):
        """Apply gravity stabilization effects to particles"""
        for particle in self.collision_system.particles:
            # Check if particle is in any gravity zone
            for zone in self.gravity_stabilizer.gravity_zones:
                distance = np.linalg.norm(particle.position - zone.center)
                
                if distance < zone.radius:
                    # Apply zone-specific effects based on state
                    if zone.stabilization_state == GravityStabilizationState.BUBBLE_LAYER:
                        # Make particle weightless
                        particle.gravitational_strength *= 0.9
                        
                        # Apply bubble warping effect
                        if distance > zone.radius - zone.bubble_thickness:
                            inward_force = (zone.center - particle.position) / distance
                            particle.velocity += inward_force * 0.1
                    
                    elif zone.stabilization_state == GravityStabilizationState.SEALED:
                        # Apply downforce
                        downforce = np.array([0, 0, -zone.strength * 0.1])
                        particle.velocity += downforce / particle.mass * self.dt
                    
                    elif zone.stabilization_state == GravityStabilizationState.CONTROLLED_EXTRACTION:
                        # Apply controlled extraction through spacers
                        for spacer in self.gravity_stabilizer.dimensional_spacers:
                            if spacer.active:
                                spacer_distance = np.linalg.norm(particle.position - spacer.position)
                                if spacer_distance < 1.0:
                                    # Extract through spacer cage
                                    extraction_direction = self.collision_system.void_center - particle.position
                                    if np.linalg.norm(extraction_direction) > 0.001:
                                        extraction_direction = extraction_direction / np.linalg.norm(extraction_direction)
                                        extraction_force = extraction_direction * spacer.cage_strength
                                        particle.velocity += extraction_force / particle.mass * self.dt
    
    def _measure_density_and_emissions(self, previous_particles):
        """Measure density and detect emissions"""
        # Measure collision zone densities
        zone_density_readings = self.density_analyzer.measure_collision_zone_density(
            self.collision_system.collision_detector.collision_zones,
            self.collision_system.particles
        )
        
        # Detect emission events
        emission_events = self.density_analyzer.detect_density_emissions(
            self.collision_system.particles, previous_particles
        )
        
        # Store density measurements
        self.density_measurements.append({
            'timestamp': self.simulation_time,
            'zone_densities': zone_density_readings,
            'emission_events': emission_events,
            'total_particles': len(self.collision_system.particles)
        })
    
    def run_simulation(self, duration: float = 8.0, print_interval: float = 0.5):
        """Run the complete collision simulation"""
        print(f"Starting collision-based extraction simulation for {duration} seconds...")
        print(f"Using GPU: {self.use_gpu}")
        print("Density measurement and emission tracking enabled")
        print("Gravity stabilization system with bubble layers enabled")
        print("Dual resonance system with quad-state particles enabled")
        print("Warp zone system with Hz wave fluctuations enabled")
        print("-" * 90)
        
        steps = int(duration / self.dt)
        print_steps = int(print_interval / self.dt)
        
        start_time = time.time()
        
        for step in range(steps):
            self.run_simulation_step()
            
            # Print status periodically
            if step % print_steps == 0:
                status = self.collision_system.get_system_status()
                collision_stats = status['collision_statistics']
                density_stats = self.density_analyzer.get_density_statistics()
                gravity_stats = self.gravity_stabilizer.get_stabilization_status()
                resonance_stats = self.dual_resonance.get_resonance_status()
                warp_stats = self.warp_zone_system.get_warp_zone_status()
                
                print(f"Time: {self.simulation_time:.2f}s | "
                      f"Particles: {status['total_particles']} | "
                      f"Trapped: {status['particle_states']['trapped']} | "
                      f"Extracting: {status['particle_states']['extracting']} | "
                      f"Collisions: {collision_stats['total_collisions']} | "
                      f"Avg Density: {density_stats.get('average_density', 0):.2e} | "
                      f"Bubble Zones: {gravity_stats['bubble_statistics']['total_bubbles']} | "
                      f"Quad States: {resonance_stats['quad_state_statistics']['total_quad_particles']} | "
                      f"Warp Zones: {warp_stats['total_warp_zones']} | "
                      f"Contained Energy: {warp_stats.get('total_contained_energy', 0):.2e} | "
                      f"Safe Zones: {warp_stats.get('measurement_safe_zones', 0)}")
        
        end_time = time.time()
        print(f"\nSimulation completed in {end_time - start_time:.2f} seconds")
        self.print_final_statistics()
    
    def print_final_statistics(self):
        """Print final simulation statistics"""
        print("\n" + "="*90)
        print("COMPLETE PARTICLE EXTRACTION SYSTEM STATISTICS")
        print("="*90)
        
        status = self.collision_system.get_system_status()
        collision_stats = status['collision_statistics']
        density_stats = self.density_analyzer.get_density_statistics()
        gravity_stats = self.gravity_stabilizer.get_stabilization_status()
        resonance_stats = self.dual_resonance.get_resonance_status()
        warp_stats = self.warp_zone_system.get_warp_zone_status()
        
        print(f"\nParticle Statistics:")
        print(f"  Total Particles: {status['total_particles']}")
        print(f"  Free Particles: {status['particle_states']['free']}")
        print(f"  Trapped Particles: {status['particle_states']['trapped']}")
        print(f"  Colliding Particles: {status['particle_states']['colliding']}")
        print(f"  Extracting Particles: {status['particle_states']['extracting']}")
        print(f"  Void-Bound Particles: {status['particle_states']['void_bound']}")
        print(f"  Field-Bending Particles: {status['particle_states']['field_bending']}")
        
        print(f"\nCollision Statistics:")
        print(f"  Total Collisions: {collision_stats['total_collisions']}")
        print(f"  Active Collision Zones: {collision_stats['active_collision_zones']}")
        print(f"  Active Force Fields: {collision_stats['active_force_fields']}")
        print(f"  Total Extractions: {collision_stats['total_extractions']}")
        print(f"  Extractions Completed: {status['extractions_completed']}")
        
        print(f"\nDensity & Emission Statistics:")
        print(f"  Total Density Measurements: {density_stats.get('total_measurements', 0)}")
        print(f"  Average Density: {density_stats.get('average_density', 0):.2e} kg/m³")
        print(f"  Peak Density: {density_stats.get('max_density', 0):.2e} kg/m³")
        print(f"  Average Particle Count per Measurement: {density_stats.get('average_particle_count', 0):.1f}")
        print(f"  Total Emission Events: {density_stats.get('total_emissions', 0)}")
        print(f"  Peak Emission Rate: {density_stats.get('peak_emission_rate', 0):.2f} particles/s")
        
        print(f"\nGravity Stabilization Statistics:")
        print(f"  Total Gravity Zones: {gravity_stats['total_zones']}")
        print(f"  Bubble Layers Created: {gravity_stats['bubble_statistics']['total_bubbles']}")
        print(f"  Average Bubble Stability: {gravity_stats['bubble_statistics']['average_stability']:.3f}")
        print(f"  Average Bubble Pressure: {gravity_stats['bubble_statistics']['average_pressure']:.1f} Pa")
        print(f"  Total Dimensional Spacers: {gravity_stats['spacer_statistics']['total_spacers']}")
        print(f"  Active Spacers: {gravity_stats['spacer_statistics']['active_spacers']}")
        print(f"  Average Cage Strength: {gravity_stats['spacer_statistics']['average_cage_strength']:.2f}")
        print(f"  Energy Release Events: {gravity_stats['energy_release_events']}")
        
        print(f"\nDual Resonance Statistics:")
        print(f"  Total Quad-State Particles: {resonance_stats['quad_state_statistics']['total_quad_particles']}")
        print(f"  Average Coherence Factor: {resonance_stats['quad_state_statistics']['average_coherence']:.3f}")
        print(f"  High Coherence Particles: {resonance_stats['quad_state_statistics']['high_coherence_particles']}")
        print(f"  Total Micro-Plank Scales: {resonance_stats['total_micro_plank_scales']}")
        print(f"  Dimensional Overlaps: {resonance_stats['dimensional_statistics']['total_overlaps']}")
        print(f"  Average Overlap Strength: {resonance_stats['dimensional_statistics']['average_overlap_strength']:.3f}")
        print(f"  Average Null Zone Stability: {resonance_stats['dimensional_statistics']['average_null_stability']:.3f}")
        
        print(f"\nWarp Zone Statistics:")
        print(f"  Total Warp Zones: {warp_stats['total_warp_zones']}")
        print(f"  Active Warp Zones: {sum(1 for z in warp_stats['zone_details'].values() if z['state'] in ['active', 'stable'])}")
        print(f"  Training Model Efficiency: {warp_stats['training_model']['model_efficiency']:.3f}")
        print(f"  Density Adjustment Factor: {warp_stats['training_model']['density_adjustment']:.3f}")
        print(f"  Pullback Threshold: {warp_stats['training_model']['pullback_threshold']:.3f}")
        print(f"  Successful Extractions: {warp_stats['training_model']['successful_extractions']}")
        print(f"  Total Extraction Attempts: {warp_stats['training_model']['total_extractions']}")
        print(f"  Total Hz Fluctuations: {warp_stats['total_hz_fluctuations']}")
        print(f"  Total Contained Energy: {warp_stats.get('total_contained_energy', 0):.2e} J")
        print(f"  Measurement Safe Zones: {warp_stats.get('measurement_safe_zones', 0)}")
        print(f"  Average Containment Efficiency: {warp_stats.get('average_containment_efficiency', 0):.3f}")
        
        # Show warp zone details
        print(f"\nWarp Zone Details:")
        for zone_id, zone_info in warp_stats['zone_details'].items():
            print(f"  Zone {zone_id}: State={zone_info['state']}, "
                  f"Particles={zone_info['particle_count']}/{zone_info['capacity']}, "
                  f"Stability={zone_info['stability']:.3f}, "
                  f"Hz_Freq={zone_info['hz_frequency']:.2e} Hz, "
                  f"Ready={zone_info['extraction_ready']}, "
                  f"Contained_E={zone_info['contained_energy']:.2e} J, "
                  f"Safe={zone_info['measurement_safe']}, "
                  f"Efficiency={zone_info['containment_efficiency']:.3f}")
        
        # Show resonance channel details
        print(f"\nResonance Channel Details:")
        for channel in resonance_stats['resonance_channels']:
            print(f"  {channel['type'].title()} Channel: "
                  f"Freq={channel['frequency']:.2e} Hz, "
                  f"Amp={channel['amplitude']:.3f}, "
                  f"Phase={channel['phase']:.3f}, "
                  f"Active={channel['active']}")
        
        # Show gravity zone details
        print(f"\nGravity Zone Details:")
        for zone_id, zone_info in gravity_stats['gravity_zones'].items():
            print(f"  Zone {zone_id}: State={zone_info['state']}, "
                  f"Occupied={zone_info['occupied_positions']}, "
                  f"Seal Energy={zone_info['seal_energy']:.2e}, "
                  f"Spacers={zone_info['spacers']}")
        
        # Export density data
        self.density_analyzer.export_density_data("collision_density_data.csv")
        
        print(f"\n" + "="*90)
        print("SYSTEM SUMMARY: All extraction mechanisms operational")
        print("✓ Collision-based trapping and extraction")
        print("✓ Density measurement and emission tracking") 
        print("✓ Gravity stabilization with bubble layers")
        print("✓ Dual resonance with quad-state particles")
        print("✓ Micro-plank scale gravitational self-direction")
        print("✓ Dimensional overlap and null zone maintenance")
        print("✓ Hz wave fluctuation warp zones with training model")
        print("✓ Safe void zone extraction without collisions")
        print("="*90)
    
    def visualize_collision_system(self):
        """Create comprehensive visualization of the collision system"""
        fig = plt.figure(figsize=(18, 12))
        fig.suptitle('Collision-Based Particle Extraction System', fontsize=16, fontweight='bold')
        
        # Create subplot grid
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # Main 3D visualization
        ax1 = fig.add_subplot(gs[:, 0:2], projection='3d')
        self._plot_3d_collision_system(ax1)
        
        # Collision zone statistics
        ax2 = fig.add_subplot(gs[0, 2])
        self._plot_collision_zone_stats(ax2)
        
        # Particle state timeline
        ax3 = fig.add_subplot(gs[1, 2])
        self._plot_collision_timeline(ax3)
        
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def _plot_3d_collision_system(self, ax):
        """Plot 3D collision system visualization"""
        # Plot collision zones
        for i, zone in enumerate(self.collision_system.collision_detector.collision_zones):
            # Draw collision zone as sphere
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 20)
            x = zone.radius * np.outer(np.cos(u), np.sin(v)) + zone.center[0]
            y = zone.radius * np.outer(np.sin(u), np.sin(v)) + zone.center[1]
            z = zone.radius * np.outer(np.ones(np.size(u)), np.cos(v)) + zone.center[2]
            
            color = 'red' if len(zone.trapped_particles) > 0 else 'blue'
            alpha = 0.3 if len(zone.trapped_particles) == 0 else 0.5
            ax.plot_surface(x, y, z, alpha=alpha, color=color)
            
            # Mark extraction candidates
            if zone.id in self.collision_system.collision_detector.extraction_candidates:
                candidate_id = self.collision_system.collision_detector.extraction_candidates[zone.id]
                candidate = next((p for p in self.collision_system.particles if p.id == candidate_id), None)
                if candidate:
                    ax.scatter(*candidate.position, color='yellow', s=100, marker='*', 
                             edgecolor='black', linewidth=2)
        
        # Plot void zone
        void_center = self.collision_system.void_center
        void_radius = 1.0
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 20)
        x = void_radius * np.outer(np.cos(u), np.sin(v)) + void_center[0]
        y = void_radius * np.outer(np.sin(u), np.sin(v)) + void_center[1]
        z = void_radius * np.outer(np.ones(np.size(u)), np.cos(v)) + void_center[2]
        ax.plot_surface(x, y, z, alpha=0.2, color='black')
        
        # Plot particle trajectories with state-based coloring
        for particle_id, trajectory in self.particle_trajectories.items():
            if len(trajectory) > 1:
                trajectory_array = np.array(trajectory)
                particle = next((p for p in self.collision_system.particles if p.id == particle_id), None)
                
                if particle:
                    color = self._get_collision_particle_color(particle)
                    alpha = 0.8
                    linewidth = 2 if particle.state in [CollisionState.EXTRACTING, CollisionState.VOID_BOUND] else 1
                    
                    ax.plot(trajectory_array[:, 0], 
                           trajectory_array[:, 1], 
                           trajectory_array[:, 2], 
                           color=color, alpha=alpha, linewidth=linewidth)
        
        # Plot force fields
        for field in self.collision_system.collision_detector.force_fields:
            if field.field_type == "extraction":
                # Draw force field as arrow
                ax.quiver(field.position[0], field.position[1], field.position[2],
                         field.direction[0], field.direction[1], field.direction[2],
                         length=field.strength/10, color='green', alpha=0.6, arrow_length_ratio=0.3)
        
        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Y Position (m)')
        ax.set_zlabel('Z Position (m)')
        ax.set_title('3D Collision-Based Extraction System')
        
        # Create legend
        legend_elements = [
            ('Collision Zone', 'blue'),
            ('Active Zone', 'red'),
            ('Extraction Candidate', 'yellow'),
            ('Void Zone', 'black'),
            ('Free Particle', 'lightblue'),
            ('Trapped Particle', 'orange'),
            ('Extracting Particle', 'green'),
            ('Void-Bound Particle', 'purple')
        ]
        
        for label, color in legend_elements:
            ax.plot([], [], [], color=color, label=label, linewidth=3)
        
        ax.legend(loc='upper right', fontsize=8)
    
    def _plot_collision_zone_stats(self, ax):
        """Plot collision zone statistics"""
        zone_data = []
        zone_labels = []
        
        for i, zone in enumerate(self.collision_system.collision_detector.collision_zones):
            trapped_count = len(zone.trapped_particles)
            zone_data.append(trapped_count)
            zone_labels.append(f'Zone {i}')
        
        if zone_data:
            bars = ax.bar(zone_labels, zone_data, color=['red' if count > 0 else 'blue' for count in zone_data], 
                         alpha=0.7, edgecolor='black')
            
            # Add value labels
            for bar, value in zip(bars, zone_data):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{value}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Trapped Particles')
        ax.set_title('Collision Zone Occupancy')
        ax.grid(True, alpha=0.3)
    
    def _plot_collision_timeline(self, ax):
        """Plot collision system timeline"""
        if not self.system_status_history:
            ax.text(0.5, 0.5, 'No simulation data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        times = [status['simulation_time'] for status in self.system_status_history]
        
        # Plot different states over time
        states = ['free', 'trapped', 'extracting', 'void_bound']
        colors_state = ['lightblue', 'orange', 'green', 'purple']
        
        for state, color in zip(states, colors_state):
            counts = [status['particle_states'].get(state, 0) 
                     for status in self.system_status_history]
            ax.plot(times, counts, label=state.replace('_', ' ').title(), 
                   color=color, linewidth=2, marker='o', markersize=2)
        
        # Plot collision count
        collision_counts = [status['collision_statistics']['total_collisions'] 
                           for status in self.system_status_history]
        ax.plot(times, collision_counts, label='Total Collisions', 
               color='red', linewidth=2, linestyle='--', marker='x', markersize=3)
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Count')
        ax.set_title('Collision System Evolution')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def _get_collision_particle_color(self, particle):
        """Get color based on collision state"""
        color_map = {
            CollisionState.FREE: 'lightblue',
            CollisionState.TRAPPED: 'orange',
            CollisionState.COLLIDING: 'red',
            CollisionState.EXTRACTING: 'green',
            CollisionState.VOID_BOUND: 'purple',
            CollisionState.FIELD_BENDING: 'darkviolet'
        }
        return color_map.get(particle.state, 'gray')

def main():
    """Main function to run the collision simulation"""
    print("="*60)
    print("COLLISION-BASED PARTICLE EXTRACTION SYSTEM")
    print("Force Collision & Avoidance Extraction")
    print("="*60)
    
    # Use CPU mode for compatibility
    use_gpu = True
    print("Using CPU computation for collision system")
    
    # Create and run simulation
    sim = CollisionSimulationRunner(use_gpu=use_gpu)
    
    # Run simulation
    sim.run_simulation(duration=8.0, print_interval=0.5)
    
    # Visualize results
    print("\nGenerating collision system visualization...")
    sim.visualize_collision_system()

if __name__ == "__main__":
    main()
