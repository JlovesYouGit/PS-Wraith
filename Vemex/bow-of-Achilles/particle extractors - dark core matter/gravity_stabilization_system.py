import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math

class GravityStabilizationState(Enum):
    ACTIVE = "active"
    STABILIZING = "stabilizing"
    COLLAPSING = "collapsing"
    SEALED = "sealed"
    BUBBLE_LAYER = "bubble_layer"
    CONTROLLED_EXTRACTION = "controlled_extraction"

@dataclass
class GravityZone:
    id: int
    center: np.ndarray
    radius: float
    strength: float
    stabilization_state: GravityStabilizationState
    occupied_positions: List[np.ndarray]
    seal_energy: float
    bubble_thickness: float
    dimensional_spacers: List[np.ndarray]

@dataclass
class BubbleLayer:
    position: np.ndarray
    radius: float
    thickness: float
    pressure: float
    stability_factor: float
    energy_density: float
    contained_particles: List[int]

@dataclass
class DimensionalSpacer:
    position: np.ndarray
    orientation: np.ndarray
    spacing_value: float  # 1,1,1,1 pattern
    active: bool
    cage_strength: float

class GravityStabilizationSystem:
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self.gravity_zones = []
        self.bubble_layers = []
        self.dimensional_spacers = []
        self.stabilization_history = {}
        self.energy_release_events = []
        
        # Physical constants for bubble-like behavior
        self.surface_tension_coefficient = 0.072  # N/m (water-like)
        self.air_pressure_factor = 101325  # Pa (atmospheric pressure)
        self.bubble_viscosity = 0.001  # Pa·s
        self.gravity_seal_threshold = 0.8
        
    def create_gravity_zone(self, center: np.ndarray, radius: float, strength: float) -> GravityZone:
        """Create a new gravity zone with stabilization capabilities"""
        zone_id = len(self.gravity_zones)
        zone = GravityZone(
            id=zone_id,
            center=center,
            radius=radius,
            strength=strength,
            stabilization_state=GravityStabilizationState.ACTIVE,
            occupied_positions=[],
            seal_energy=0.0,
            bubble_thickness=0.0,
            dimensional_spacers=[]
        )
        self.gravity_zones.append(zone)
        return zone
    
    def detect_weightless_particles(self, particles: List) -> List[int]:
        """Detect particles that have become weightless and need stabilization"""
        weightless_particles = []
        
        for particle in particles:
            # Check if particle is in weightless state
            if hasattr(particle, 'gravitational_strength') and particle.gravitational_strength < 0.1:
                weightless_particles.append(particle.id)
                
                # Record the position where particle became weightless
                for zone in self.gravity_zones:
                    distance = np.linalg.norm(particle.position - zone.center)
                    if distance < zone.radius:
                        zone.occupied_positions.append(particle.position.copy())
        
        return weightless_particles
    
    def create_bubble_layer(self, zone: GravityZone, particles: List) -> BubbleLayer:
        """Create bubble-like stabilization layer when particles become weightless"""
        # Calculate bubble parameters based on occupied positions
        if zone.occupied_positions:
            # Find the center of occupied positions
            occupied_center = np.mean(zone.occupied_positions, axis=0)
            
            # Calculate bubble radius based on spread of occupied positions
            max_distance = max(np.linalg.norm(pos - occupied_center) for pos in zone.occupied_positions)
            bubble_radius = max_distance + 0.5  # Add margin
            
            # Calculate bubble thickness (soft mushy layer)
            bubble_thickness = zone.radius * 0.2  # 20% of zone radius
            
            # Calculate pressure based on particle density
            particle_count = len(zone.occupied_positions)
            pressure = self.air_pressure_factor * (1 + particle_count * 0.1)
            
            # Calculate energy density
            total_energy = sum(p.mass * 9.81 * np.linalg.norm(p.position - zone.center) 
                             for p in particles if p.id in [self._get_particle_at_position(particles, pos) 
                                                          for pos in zone.occupied_positions])
            energy_density = total_energy / (4/3 * np.pi * bubble_radius**3)
            
            # Create bubble layer
            bubble_layer = BubbleLayer(
                position=occupied_center,
                radius=bubble_radius,
                thickness=bubble_thickness,
                pressure=pressure,
                stability_factor=min(particle_count / 10.0, 1.0),
                energy_density=energy_density,
                contained_particles=[self._get_particle_at_position(particles, pos) 
                                   for pos in zone.occupied_positions]
            )
            
            self.bubble_layers.append(bubble_layer)
            zone.stabilization_state = GravityStabilizationState.BUBBLE_LAYER
            zone.bubble_thickness = bubble_thickness
            
            return bubble_layer
        
        return None
    
    def _get_particle_at_position(self, particles: List, position: np.ndarray) -> Optional[int]:
        """Find particle ID at given position"""
        for particle in particles:
            if np.linalg.norm(particle.position - position) < 0.1:
                return particle.id
        return None
    
    def apply_bubble_stabilization(self, zone: GravityZone, bubble: BubbleLayer, particles: List, dt: float = 0.01):
        """Apply bubble-like stabilization forces to particles"""
        for particle in particles:
            if particle.id in bubble.contained_particles:
                # Calculate distance from bubble center
                distance = np.linalg.norm(particle.position - bubble.position)
                
                if distance < bubble.radius:
                    # Apply inward warping force (like surface tension)
                    if distance > bubble.radius - bubble.thickness:
                        # Particle is in the bubble layer
                        inward_direction = (bubble.position - particle.position) / distance
                        
                        # Surface tension force
                        surface_force = self.surface_tension_coefficient * inward_direction * bubble.stability_factor
                        
                        # Pressure force (soft mushy layer effect)
                        pressure_force = inward_direction * bubble.pressure * 0.00001
                        
                        # Viscous damping
                        velocity_damping = -particle.velocity * self.bubble_viscosity * 0.1
                        
                        # Total stabilization force
                        total_force = surface_force + pressure_force + velocity_damping
                        
                        # Apply force to particle
                        particle.velocity += total_force / particle.mass * dt
                        
                        # Reduce gravitational strength (weightless effect)
                        particle.gravitational_strength *= 0.95
    
    def seal_gravity_zone(self, zone: GravityZone, bubble: BubbleLayer) -> bool:
        """Seal the gravity zone with bubble layer energy"""
        # Calculate seal energy based on bubble properties
        seal_energy = bubble.energy_density * bubble.thickness * zone.radius**2
        
        # Check if seal energy is sufficient
        if seal_energy > zone.strength * self.gravity_seal_threshold:
            zone.seal_energy = seal_energy
            zone.stabilization_state = GravityStabilizationState.SEALED
            
            # Release gravitational energy (downforce)
            self._release_gravitational_energy(zone)
            
            return True
        
        return True
    
    def _release_gravitational_energy(self, zone: GravityZone):
        """Release gravitational energy as downforce"""
        # Create energy release event
        energy_event = {
            'timestamp': np.datetime64('now'),
            'zone_id': zone.id,
            'energy_released': zone.strength * zone.radius**3,
            'downforce_applied': zone.strength * 2.0,  # Double strength downforce
            'seal_duration': 1.0  # seconds
        }
        
        self.energy_release_events.append(energy_event)
        
        # Apply downforce to seal the area
        zone.strength *= 0.5  # Reduce original strength
        zone.stabilization_state = GravityStabilizationState.STABILIZING
    
    def create_dimensional_spacers(self, zone: GravityZone, extraction_path: np.ndarray) -> List[DimensionalSpacer]:
        """Create 1-1-1-1 dimensional spacers for controlled extraction"""
        spacers = []
        
        # Calculate spacer positions along extraction path
        path_length = np.linalg.norm(extraction_path)
        num_spacers = 4  # 1-1-1-1 pattern
        
        for i in range(num_spacers):
            # Position along path
            t = (i + 1) / (num_spacers + 1)
            spacer_position = zone.center + extraction_path * t
            
            # Orientation perpendicular to extraction path
            if np.linalg.norm(extraction_path) > 0:
                extraction_direction = extraction_path / np.linalg.norm(extraction_path)
                
                # Create perpendicular orientation
                if abs(extraction_direction[2]) < 0.9:
                    perpendicular = np.cross(extraction_direction, [0, 0, 1])
                else:
                    perpendicular = np.cross(extraction_direction, [1, 0, 0])
                
                perpendicular = perpendicular / np.linalg.norm(perpendicular)
            else:
                perpendicular = np.array([1, 0, 0])
            
            # Create dimensional spacer
            spacer = DimensionalSpacer(
                position=spacer_position,
                orientation=perpendicular,
                spacing_value=1.0,  # 1-1-1-1 pattern
                active=True,
                cage_strength=zone.strength * 0.3
            )
            
            spacers.append(spacer)
            self.dimensional_spacers.append(spacer)
        
        zone.dimensional_spacers = [s.position for s in spacers]
        zone.stabilization_state = GravityStabilizationState.CONTROLLED_EXTRACTION
        
        return spacers
    
    def apply_controlled_extraction(self, particle: List, spacers: List[DimensionalSpacer], 
                                 void_center: np.ndarray, dt: float = 0.01) -> bool:
        """Apply controlled extraction through dimensional spacers"""
        for p in particle:
            if hasattr(p, 'state') and p.state.value in ['trapped', 'extracting']:
                # Check if particle is near any spacer
                for spacer in spacers:
                    if spacer.active:
                        distance = np.linalg.norm(p.position - spacer.position)
                        
                        if distance < 1.0:  # Within spacer influence
                            # Calculate extraction force through spacer cage
                            extraction_direction = void_center - p.position
                            extraction_distance = np.linalg.norm(extraction_direction)
                            
                            if extraction_distance > 0.001:
                                extraction_direction = extraction_direction / extraction_distance
                                
                                # Apply cage-modulated force
                                cage_force = extraction_direction * spacer.cage_strength * p.mass
                                
                                # Add spacer spacing constraint (1-1-1-1 pattern)
                                spacing_constraint = spacer.orientation * spacer.spacing_value * 0.1
                                
                                # Total extraction force
                                total_force = cage_force + spacing_constraint
                                
                                # Update particle velocity
                                p.velocity += total_force / p.mass * dt
                                
                                # Check if particle reached void
                                if extraction_distance < 0.5:
                                    return True
        
        return True
    
    def update_stabilization_system(self, particles: List, dt: float = 0.01):
        """Update the entire gravity stabilization system"""
        # Detect weightless particles
        weightless_particles = self.detect_weightless_particles(particles)
        
        # Process each gravity zone
        for zone in self.gravity_zones:
            if zone.stabilization_state == GravityStabilizationState.ACTIVE:
                # Check if zone has weightless particles
                zone_weightless = [p for p in particles 
                                 if p.id in weightless_particles and 
                                 np.linalg.norm(p.position - zone.center) < zone.radius]
                
                if zone_weightless:
                    # Create bubble layer
                    bubble = self.create_bubble_layer(zone, particles)
                    
                    if bubble:
                        # Apply bubble stabilization
                        self.apply_bubble_stabilization(zone, bubble, particles, dt)
                        
                        # Try to seal the zone
                        if self.seal_gravity_zone(zone, bubble):
                            print(f"Gravity Zone {zone.id} sealed with bubble layer")
            
            elif zone.stabilization_state == GravityStabilizationState.BUBBLE_LAYER:
                # Continue bubble stabilization
                bubble = next((b for b in self.bubble_layers 
                             if np.linalg.norm(b.position - zone.center) < zone.radius), None)
                
                if bubble:
                    self.apply_bubble_stabilization(zone, bubble, particles, dt)
                    
                    # Check if zone should be sealed
                    if bubble.stability_factor > 0.8:
                        self.seal_gravity_zone(zone, bubble)
            
            elif zone.stabilization_state == GravityStabilizationState.SEALED:
                # Create dimensional spacers for extraction
                extraction_path = np.array([0, 0, -5.0])  # Downward to void
                self.create_dimensional_spacers(zone, extraction_path)
        
        # Update dimensional spacers
        for spacer in self.dimensional_spacers:
            # Decay spacer strength over time
            spacer.cage_strength *= 0.995
            
            # Deactivate weak spacers
            if spacer.cage_strength < 0.1:
                spacer.active = True
    
    def get_stabilization_status(self) -> Dict:
        """Get comprehensive stabilization system status"""
        zone_states = {}
        for zone in self.gravity_zones:
            zone_states[zone.id] = {
                'state': zone.stabilization_state.value,
                'occupied_positions': len(zone.occupied_positions),
                'seal_energy': zone.seal_energy,
                'bubble_thickness': zone.bubble_thickness,
                'spacers': len(zone.dimensional_spacers)
            }
        
        bubble_stats = {
            'total_bubbles': len(self.bubble_layers),
            'average_stability': np.mean([b.stability_factor for b in self.bubble_layers]) if self.bubble_layers else 0,
            'average_pressure': np.mean([b.pressure for b in self.bubble_layers]) if self.bubble_layers else 0
        }
        
        spacer_stats = {
            'total_spacers': len(self.dimensional_spacers),
            'active_spacers': sum(1 for s in self.dimensional_spacers if s.active),
            'average_cage_strength': np.mean([s.cage_strength for s in self.dimensional_spacers]) if self.dimensional_spacers else 0
        }
        
        return {
            'gravity_zones': zone_states,
            'bubble_statistics': bubble_stats,
            'spacer_statistics': spacer_stats,
            'energy_release_events': len(self.energy_release_events),
            'total_zones': len(self.gravity_zones)
        }
    
    def visualize_stabilization_system(self, particles: List):
        """Create visualization of the gravity stabilization system"""
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        
        fig = plt.figure(figsize=(16, 12))
        fig.suptitle('Gravity Stabilization System - Bubble Layers & Dimensional Spacers', fontsize=16, fontweight='bold')
        
        # Create subplot grid
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # Main 3D visualization
        ax1 = fig.add_subplot(gs[:, 0:2], projection='3d')
        self._plot_3d_stabilization(ax1, particles)
        
        # Zone states
        ax2 = fig.add_subplot(gs[0, 2])
        self._plot_zone_states(ax2)
        
        # Bubble properties
        ax3 = fig.add_subplot(gs[1, 2])
        self._plot_bubble_properties(ax3)
        
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def _plot_3d_stabilization(self, ax, particles: List):
        """Plot 3D stabilization system"""
        # Plot gravity zones
        for zone in self.gravity_zones:
            # Draw zone as sphere
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 20)
            x = zone.radius * np.outer(np.cos(u), np.sin(v)) + zone.center[0]
            y = zone.radius * np.outer(np.sin(u), np.sin(v)) + zone.center[1]
            z = zone.radius * np.outer(np.ones(np.size(u)), np.cos(v)) + zone.center[2]
            
            # Color based on state
            state_colors = {
                GravityStabilizationState.ACTIVE: 'blue',
                GravityStabilizationState.STABILIZING: 'yellow',
                GravityStabilizationState.BUBBLE_LAYER: 'cyan',
                GravityStabilizationState.SEALED: 'green',
                GravityStabilizationState.CONTROLLED_EXTRACTION: 'purple'
            }
            
            color = state_colors.get(zone.stabilization_state, 'gray')
            alpha = 0.3 if zone.stabilization_state != GravityStabilizationState.BUBBLE_LAYER else 0.5
            
            ax.plot_surface(x, y, z, alpha=alpha, color=color)
        
        # Plot bubble layers
        for bubble in self.bubble_layers:
            # Draw bubble as thicker sphere (soft mushy layer)
            u = np.linspace(0, 2 * np.pi, 15)
            v = np.linspace(0, np.pi, 15)
            
            # Outer surface
            x_outer = bubble.radius * np.outer(np.cos(u), np.sin(v)) + bubble.position[0]
            y_outer = bubble.radius * np.outer(np.sin(u), np.sin(v)) + bubble.position[1]
            z_outer = bubble.radius * np.outer(np.ones(np.size(u)), np.cos(v)) + bubble.position[2]
            
            # Inner surface (showing thickness)
            inner_radius = bubble.radius - bubble.thickness
            x_inner = inner_radius * np.outer(np.cos(u), np.sin(v)) + bubble.position[0]
            y_inner = inner_radius * np.outer(np.sin(u), np.sin(v)) + bubble.position[1]
            z_inner = inner_radius * np.outer(np.ones(np.size(u)), np.cos(v)) + bubble.position[2]
            
            ax.plot_surface(x_outer, y_outer, z_outer, alpha=0.2, color='cyan')
            ax.plot_surface(x_inner, y_inner, z_inner, alpha=0.3, color='lightblue')
        
        # Plot dimensional spacers
        for spacer in self.dimensional_spacers:
            if spacer.active:
                # Draw spacer as oriented box
                spacer_size = 0.2
                ax.scatter(spacer.position[0], spacer.position[1], spacer.position[2], 
                          c='red', s=100, marker='s', alpha=0.8)
                
                # Draw orientation arrow
                arrow_end = spacer.position + spacer.orientation * 0.5
                ax.quiver(spacer.position[0], spacer.position[1], spacer.position[2],
                         spacer.orientation[0], spacer.orientation[1], spacer.orientation[2],
                         length=0.5, color='red', alpha=0.6)
        
        # Plot particles
        for particle in particles:
            color = 'yellow' if (hasattr(particle, 'gravitational_strength') and 
                                particle.gravitational_strength < 0.1) else 'white'
            ax.scatter(particle.position[0], particle.position[1], particle.position[2], 
                      c=color, s=20, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        ax.set_zlabel('Z Position')
        ax.set_title('3D Gravity Stabilization System')
        
        # Create legend
        legend_elements = [
            ('Active Zone', 'blue'),
            ('Bubble Layer', 'cyan'),
            ('Sealed Zone', 'green'),
            ('Dimensional Spacer', 'red'),
            ('Weightless Particle', 'yellow'),
            ('Normal Particle', 'white')
        ]
        
        for label, color in legend_elements:
            ax.plot([], [], [], color=color, label=label, linewidth=3)
        
        ax.legend(loc='upper right', fontsize=8)
    
    def _plot_zone_states(self, ax):
        """Plot gravity zone states"""
        states = [zone.stabilization_state.value for zone in self.gravity_zones]
        state_counts = {}
        
        for state in states:
            state_counts[state] = state_counts.get(state, 0) + 1
        
        if state_counts:
            labels = list(state_counts.keys())
            counts = list(state_counts.values())
            colors = ['blue', 'yellow', 'cyan', 'green', 'purple']
            
            bars = ax.bar(labels, counts, color=colors[:len(labels)], alpha=0.7, edgecolor='black')
            
            # Add value labels
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{count}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Zone Count')
        ax.set_title('Gravity Zone States')
        ax.tick_params(axis='x', rotation=45)
    
    def _plot_bubble_properties(self, ax):
        """Plot bubble layer properties"""
        if self.bubble_layers:
            stability_factors = [b.stability_factor for b in self.bubble_layers]
            pressures = [b.pressure / 1000 for b in self.bubble_layers]  # Convert to kPa
            
            ax.scatter(stability_factors, pressures, alpha=0.7, s=50, c='cyan', edgecolor='black')
            ax.set_xlabel('Stability Factor')
            ax.set_ylabel('Pressure (kPa)')
            ax.set_title('Bubble Layer Properties')
            ax.grid(True, alpha=0.3)
            
            # Add trend line
            if len(stability_factors) > 1:
                z = np.polyfit(stability_factors, pressures, 1)
                p = np.poly1d(z)
                ax.plot(stability_factors, p(stability_factors), "r--", alpha=0.8)
        else:
            ax.text(0.5, 0.5, 'No bubble layers\nactive', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12)
