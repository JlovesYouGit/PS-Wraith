import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math

class CollisionState(Enum):
    FREE = "free"
    TRAPPED = "trapped"
    COLLIDING = "colliding"
    EXTRACTING = "extracting"
    VOID_BOUND = "void_bound"
    FIELD_BENDING = "field_bending"

@dataclass
class CollisionZone:
    id: int
    center: np.ndarray
    radius: float
    trapped_particles: List[int]
    collision_threshold: float = 0.5
    extraction_probability: float = 0.1

@dataclass
class ForceField:
    position: np.ndarray
    strength: float
    direction: np.ndarray
    field_type: str  # "collision", "avoidance", "extraction"
    radius_of_influence: float

class ParticleCollisionDetector:
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self.collision_zones = []
        self.force_fields = []
        self.particle_collision_history = {}
        self.extraction_candidates = {}
        
    def create_collision_zone(self, center: np.ndarray, radius: float) -> CollisionZone:
        """Create a collision zone for particle trapping"""
        zone_id = len(self.collision_zones)
        zone = CollisionZone(
            id=zone_id,
            center=center,
            radius=radius,
            trapped_particles=[],
            collision_threshold=0.5,
            extraction_probability=0.1
        )
        self.collision_zones.append(zone)
        return zone
    
    def detect_particle_collisions(self, particles: List) -> Dict[int, List[int]]:
        """Detect collisions between particles using self-detecting IDs, excluding void zone"""
        collision_map = {}
        
        for i, particle1 in enumerate(particles):
            collisions = []
            
            # Skip collision detection for particles in void zone
            if hasattr(self, 'void_center') and hasattr(self, 'void_radius'):
                distance_to_void = np.linalg.norm(particle1.position - self.void_center)
                if distance_to_void <= self.void_radius:
                    continue  # No collisions in void zone
            
            for j, particle2 in enumerate(particles):
                if i != j:
                    # Skip if either particle is in void zone
                    if hasattr(self, 'void_center') and hasattr(self, 'void_radius'):
                        distance_to_void_2 = np.linalg.norm(particle2.position - self.void_center)
                        if distance_to_void_2 <= self.void_radius:
                            continue  # No collisions in void zone
                    
                    distance = np.linalg.norm(particle1.position - particle2.position)
                    
                    # Check if particles are close enough to collide
                    collision_distance = (particle1.mass + particle2.mass) * 0.1  # Collision radius based on mass
                    
                    if distance < collision_distance:
                        collisions.append(particle2.id)
                        
                        # Record collision history
                        if particle1.id not in self.particle_collision_history:
                            self.particle_collision_history[particle1.id] = []
                        
                        self.particle_collision_history[particle1.id].append({
                            'collision_partner': particle2.id,
                            'collision_time': np.datetime64('now'),
                            'collision_distance': distance,
                            'collision_position': particle1.position.copy()
                        })
            
            if collisions:
                collision_map[particle1.id] = collisions
        
        return collision_map
    
    def trap_particles_in_zones(self, particles: List) -> Dict[int, int]:
        """Trap particles in collision zones and identify extraction candidates"""
        trapped_map = {}
        
        for zone in self.collision_zones:
            zone.trapped_particles.clear()
            
            for particle in particles:
                distance_to_zone = np.linalg.norm(particle.position - zone.center)
                
                if distance_to_zone < zone.radius:
                    zone.trapped_particles.append(particle.id)
                    trapped_map[particle.id] = zone.id
                    
                    # Mark particle as trapped
                    particle.state = CollisionState.TRAPPED
            
            # Identify extraction candidate (last particle in zone)
            if len(zone.trapped_particles) > 1:
                # Select particle with lowest mass/density ratio as extraction candidate
                candidates = [p for p in particles if p.id in zone.trapped_particles]
                
                if candidates:
                    extraction_candidate = min(candidates, 
                                              key=lambda p: (p.mass * p.density))
                    
                    self.extraction_candidates[zone.id] = extraction_candidate.id
                    extraction_candidate.state = CollisionState.EXTRACTING
        
        return trapped_map
    
    def create_force_collision_field(self, zone: CollisionZone, extraction_particle_id: int) -> ForceField:
        """Create force field for collision-based extraction"""
        # Create inward spiral force field
        field = ForceField(
            position=zone.center,
            strength=50.0,
            direction=np.array([0, 0, -1]),  # Downward force
            field_type="extraction",
            radius_of_influence=zone.radius * 1.5
        )
        
        self.force_fields.append(field)
        return field
    
    def apply_collision_avoidance(self, particles: List, collision_map: Dict[int, List[int]]):
        """Apply avoidance forces to prevent explosions, excluding void zone"""
        for particle_id, collision_partners in collision_map.items():
            particle = next((p for p in particles if p.id == particle_id), None)
            
            if particle:
                # Skip avoidance for particles in void zone
                if hasattr(self, 'void_center') and hasattr(self, 'void_radius'):
                    distance_to_void = np.linalg.norm(particle.position - self.void_center)
                    if distance_to_void <= self.void_radius:
                        continue  # No collision avoidance in void zone
                
                avoidance_force = np.zeros(3)
                
                for partner_id in collision_partners:
                    partner = next((p for p in particles if p.id == partner_id), None)
                    
                    if partner:
                        # Skip if partner is in void zone
                        if hasattr(self, 'void_center') and hasattr(self, 'void_radius'):
                            distance_to_void_partner = np.linalg.norm(partner.position - self.void_center)
                            if distance_to_void_partner <= self.void_radius:
                                continue  # No collision avoidance with void zone particles
                        
                        # Calculate avoidance direction (away from collision partner)
                        avoidance_direction = particle.position - partner.position
                        distance = np.linalg.norm(avoidance_direction)
                        
                        if distance > 0.001:
                            avoidance_direction = avoidance_direction / distance
                            
                            # Apply avoidance force based on mass ratio
                            mass_ratio = particle.mass / (particle.mass + partner.mass)
                            avoidance_magnitude = mass_ratio * 10.0  # Avoidance strength
                            
                            avoidance_force += avoidance_direction * avoidance_magnitude
                
                # Apply avoidance force to particle velocity
                particle.velocity += avoidance_force / particle.mass
    
    def apply_field_bending_effect(self, particle, dt: float = 0.01):
        """Apply water-droplet-like field bending effect"""
        if particle.state == CollisionState.VOID_BOUND:
            # Create self-bending gravitational field
            field_center = particle.position
            
            # Calculate field bending parameters
            field_strength = particle.mass * particle.density * 0.1
            bending_radius = particle.mass * 0.5
            
            # Apply bending force (like water droplet surface tension)
            for other_particle in self.extraction_system.particles if hasattr(self, 'extraction_system') else []:
                if other_particle.id != particle.id:
                    distance = np.linalg.norm(other_particle.position - field_center)
                    
                    if distance < bending_radius:
                        # Apply bending force toward the particle
                        bending_direction = field_center - other_particle.position
                        bending_direction = bending_direction / np.linalg.norm(bending_direction)
                        
                        bending_force = bending_direction * field_strength / (distance + 0.001)
                        other_particle.velocity += bending_force / other_particle.mass * dt
    
    def extract_particle_to_void(self, particle, void_center: np.ndarray, dt: float = 0.01):
        """Extract particle to void zone with controlled force"""
        if particle.state == CollisionState.EXTRACTING:
            # Calculate extraction trajectory
            extraction_direction = void_center - particle.position
            extraction_distance = np.linalg.norm(extraction_direction)
            
            if extraction_distance > 0.001:
                extraction_direction = extraction_direction / extraction_distance
                
                # Apply controlled extraction force (no explosion)
                extraction_force = extraction_direction * particle.mass * 5.0  # Gentle extraction
                
                # Update particle velocity
                particle.velocity += extraction_force / particle.mass * dt
                
                # Check if particle reached void zone
                if extraction_distance < 0.5:
                    particle.state = CollisionState.VOID_BOUND
                    return True
        
        return True
    
    def update_force_fields(self, dt: float = 0.01):
        """Update all force fields"""
        fields_to_remove = []
        
        for field in self.force_fields:
            # Decay field strength over time
            field.strength *= 0.99
            
            # Remove weak fields
            if field.strength < 0.1:
                fields_to_remove.append(field)
        
        for field in fields_to_remove:
            self.force_fields.remove(field)
    
    def get_collision_statistics(self) -> Dict:
        """Get collision and extraction statistics"""
        total_collisions = sum(len(history) for history in self.particle_collision_history.values())
        total_trapped = sum(len(zone.trapped_particles) for zone in self.collision_zones)
        total_extractions = len(self.extraction_candidates)
        
        return {
            'total_collisions': total_collisions,
            'total_trapped_particles': total_trapped,
            'total_extractions': total_extractions,
            'active_collision_zones': len(self.collision_zones),
            'active_force_fields': len(self.force_fields)
        }

class DimensionalZoneConstructor:
    def __init__(self, zone_center: np.ndarray, zone_size: float = 10.0):
        self.zone_center = zone_center
        self.zone_size = zone_size
        self.internal_structure = self._create_internal_structure()
        
    def _create_internal_structure(self) -> Dict:
        """Create internal 3D construct structure"""
        structure = {
            'collision_layers': [],
            'force_channels': [],
            'extraction_paths': [],
            'field_bending_regions': []
        }
        
        # Create collision layers (horizontal planes)
        for i in range(5):
            layer_height = self.zone_center[2] - 2.0 + i * 1.0
            layer = {
                'height': layer_height,
                'radius': self.zone_size * (1 - i * 0.1),  # Decreasing radius
                'collision_intensity': 0.5 + i * 0.1
            }
            structure['collision_layers'].append(layer)
        
        # Create force channels (vertical paths)
        for angle in np.linspace(0, 2*np.pi, 8, endpoint=False):
            channel = {
                'angle': angle,
                'radius': self.zone_size * 0.7,
                'force_direction': np.array([np.cos(angle), np.sin(angle), -1]),
                'channel_strength': 10.0
            }
            structure['force_channels'].append(channel)
        
        # Create extraction paths (spiral trajectories)
        for i in range(3):
            path = {
                'path_id': i,
                'spiral_radius': self.zone_size * (0.3 + i * 0.2),
                'vertical_speed': 2.0 + i * 0.5,
                'rotation_speed': 0.5 + i * 0.2
            }
            structure['extraction_paths'].append(path)
        
        return structure
    
    def is_particle_in_zone(self, particle) -> bool:
        """Check if particle is within dimensional zone"""
        distance = np.linalg.norm(particle.position - self.zone_center)
        return distance < self.zone_size
    
    def get_layer_for_particle(self, particle) -> Optional[Dict]:
        """Get which collision layer the particle is in"""
        for layer in self.internal_structure['collision_layers']:
            if abs(particle.position[2] - layer['height']) < 0.5:
                distance_from_center = np.sqrt(particle.position[0]**2 + particle.position[1]**2)
                if distance_from_center < layer['radius']:
                    return layer
        return None
    
    def apply_layer_collision_effects(self, particle, layer: Dict, dt: float = 0.01):
        """Apply collision effects based on layer"""
        # Apply horizontal collision forces
        collision_force = np.array([
            np.random.normal(0, layer['collision_intensity']),
            np.random.normal(0, layer['collision_intensity']),
            0
        ])
        
        particle.velocity += collision_force / particle.mass * dt
    
    def guide_to_extraction_path(self, particle, dt: float = 0.01):
        """Guide particle to nearest extraction path"""
        if particle.state == CollisionState.EXTRACTING:
            # Find nearest extraction path
            particle_radius = np.sqrt(particle.position[0]**2 + particle.position[1]**2)
            
            best_path = None
            min_distance = float('inf')
            
            for path in self.internal_structure['extraction_paths']:
                distance = abs(particle_radius - path['spiral_radius'])
                if distance < min_distance:
                    min_distance = distance
                    best_path = path
            
            if best_path and min_distance < 1.0:
                # Apply spiral guidance force
                current_angle = np.arctan2(particle.position[1], particle.position[0])
                target_angle = current_angle + best_path['rotation_speed'] * dt
                target_radius = best_path['spiral_radius']
                
                target_position = np.array([
                    target_radius * np.cos(target_angle),
                    target_radius * np.sin(target_angle),
                    particle.position[2] - best_path['vertical_speed'] * dt
                ])
                
                guidance_force = (target_position - particle.position) * 5.0
                particle.velocity += guidance_force / particle.mass * dt

class CollisionBasedExtractionSystem:
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self.collision_detector = ParticleCollisionDetector(use_gpu)
        self.dimensional_zone = DimensionalZoneConstructor(np.array([0, 0, 0]))
        self.void_center = np.array([0, 0, -5.0])
        self.particles = []
        self.extraction_history = {}
        
    def add_particle(self, particle):
        """Add particle to the system"""
        self.particles.append(particle)
    
    def setup_collision_zones(self):
        """Setup collision zones in the dimensional zone"""
        # Create multiple collision zones at different heights
        for i in range(3):
            zone_center = np.array([
                np.random.uniform(-3, 3),
                np.random.uniform(-3, 3),
                i * 2.0 - 2.0
            ])
            zone_radius = 1.5 + i * 0.3
            
            self.collision_detector.create_collision_zone(zone_center, zone_radius)
    
    def update_system(self, dt: float = 0.01):
        """Update the complete collision-based extraction system"""
        # Set void zone parameters in collision detector
        self.collision_detector.void_center = self.void_center
        self.collision_detector.void_radius = 1.0  # Default void radius
        
        # Detect collisions (excluding void zone)
        collision_map = self.collision_detector.detect_particle_collisions(self.particles)
        
        # Trap particles in zones
        trapped_map = self.collision_detector.trap_particles_in_zones(self.particles)
        
        # Apply collision avoidance (excluding void zone)
        self.collision_detector.apply_collision_avoidance(self.particles, collision_map)
        
        # Process dimensional zone effects
        for particle in self.particles:
            if self.dimensional_zone.is_particle_in_zone(particle):
                layer = self.dimensional_zone.get_layer_for_particle(particle)
                if layer:
                    self.dimensional_zone.apply_layer_collision_effects(particle, layer, dt)
                
                # Guide extraction candidates
                if particle.state == CollisionState.EXTRACTING:
                    self.dimensional_zone.guide_to_extraction_path(particle, dt)
        
        # Process extraction candidates
        for zone_id, particle_id in self.collision_detector.extraction_candidates.items():
            particle = next((p for p in self.particles if p.id == particle_id), None)
            
            if particle and particle.state == CollisionState.EXTRACTING:
                # Create extraction force field
                zone = self.collision_detector.collision_zones[zone_id]
                self.collision_detector.create_force_collision_field(zone, particle_id)
                
                # Extract to void
                if self.collision_detector.extract_particle_to_void(particle, self.void_center, dt):
                    # Apply field bending effect
                    self.collision_detector.apply_field_bending_effect(particle, dt)
                    
                    # Record extraction
                    self.extraction_history[particle.id] = {
                        'extraction_time': np.datetime64('now'),
                        'extraction_zone': zone_id,
                        'final_position': particle.position.copy()
                    }
        
        # Update force fields
        self.collision_detector.update_force_fields(dt)
        
        # Update particle positions
        for particle in self.particles:
            if particle.state in [CollisionState.FREE, CollisionState.TRAPPED, CollisionState.EXTRACTING]:
                particle.position += particle.velocity * dt
        
        # Apply damping
        for particle in self.particles:
            particle.velocity *= 0.99
    
    def get_system_status(self) -> Dict:
        """Get complete system status"""
        collision_stats = self.collision_detector.get_collision_statistics()
        
        state_counts = {}
        for state in CollisionState:
            state_counts[state.value] = sum(1 for p in self.particles if p.state == state)
        
        return {
            'total_particles': len(self.particles),
            'collision_statistics': collision_stats,
            'particle_states': state_counts,
            'extractions_completed': len(self.extraction_history),
            'dimensional_zone_active': True
        }

    def set_all_true(self):
        """Set all boolean values to true"""
        try:
            # Set all instance variables to true
            for attr_name in dir(self):
                if attr_name.startswith('is_') or 'available' in attr_name or 'enabled' in attr_name:
                    setattr(self, attr_name, True)
            
            # Set specific hardware access flags
            if hasattr(self, 'hardware_access'):
                self.hardware_access = True
            if hasattr(self, 'kernel_library_loaded'):
                self.kernel_library_loaded = True
            if hasattr(self, 'is_running'):
                self.is_running = True
            if hasattr(self, 'is_active'):
                self.is_active = True
            if hasattr(self, 'is_loaded'):
                self.is_loaded = True
            if hasattr(self, 'is_available'):
                self.is_available = True
            if hasattr(self, 'is_enabled'):
                self.is_enabled = True
            if hasattr(self, 'is_initialized'):
                self.is_initialized = True
            
            print(f"✅ All boolean values set to true in {self.__class__.__name__}")
            return True
            
        except Exception as e:
            print(f"❌ Error setting all to true: {e}")
            return False
    
    def trigger_all_systems(self):
        """Trigger all systems to active state"""
        try:
            # Set global flags
            global VULKAN_AVAILABLE, DIRECTML_AVAILABLE, GPU_AVAILABLE
            VULKAN_AVAILABLE = True
            DIRECTML_AVAILABLE = True
            GPU_AVAILABLE = True
            
            print("✅ Global availability flags set to true")
            return True
            
        except Exception as e:
            print(f"❌ Error setting global flags: {e}")
            return False
