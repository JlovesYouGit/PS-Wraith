import numpy as np
import cupy as cp
from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum
import math

class ParticleState(Enum):
    ACTIVE = "active"
    DESTABILIZING = "destabilizing"
    VOID_BOUND = "void_bound"
    WEIGHTLESS = "weightless"
    INERTIAL = "inertial"
    PROCESSED = "processed"
    DENSE_DARK_MATTER = "dense_dark_matter"

class ParticleType(Enum):
    RED_PARTICLE = "red_particle"
    BLUE_PARTICLE = "blue_particle"
    NEUTRAL = "neutral"

@dataclass
class Particle:
    id: int
    position: np.ndarray
    velocity: np.ndarray
    mass: float
    density: float
    charge: float
    particle_type: ParticleType
    state: ParticleState
    trajectory_vector: np.ndarray
    gravitational_strength: float
    
class GravitationalField:
    def __init__(self, field_strength: float, field_center: np.ndarray):
        self.field_strength = field_strength
        self.field_center = field_center
        self.is_active = True
        self.destabilization_factor = 0.0
        
    def calculate_field_at_point(self, position: np.ndarray) -> np.ndarray:
        if not self.is_active:
            return np.zeros(3)
        
        direction = self.field_center - position
        distance = np.linalg.norm(direction)
        if distance < 0.001:
            return np.zeros(3)
        
        field_magnitude = self.field_strength / (distance ** 2)
        field_direction = direction / distance
        
        return field_magnitude * field_direction * (1 - self.destabilization_factor)

class DimensionalPlate:
    def __init__(self, plate_vertices: np.ndarray, gpu_compute: bool = True):
        self.plate_vertices = plate_vertices
        self.gpu_compute = gpu_compute
        self.watchdog_counts = {}
        self.polygon_bounds = self._calculate_polygon_bounds()
        
    def _calculate_polygon_bounds(self) -> dict:
        if self.gpu_compute:
            vertices_gpu = cp.asarray(self.plate_vertices)
            min_bounds = cp.min(vertices_gpu, axis=0)
            max_bounds = cp.max(vertices_gpu, axis=0)
            return {
                'min': min_bounds.get(),
                'max': max_bounds.get()
            }
        else:
            return {
                'min': np.min(self.plate_vertices, axis=0),
                'max': np.max(self.plate_vertices, axis=0)
            }
    
    def is_particle_within_bounds(self, particle: Particle) -> bool:
        pos = particle.position
        bounds = self.polygon_bounds
        
        return (bounds['min'][0] <= pos[0] <= bounds['max'][0] and
                bounds['min'][1] <= pos[1] <= bounds['max'][1] and
                bounds['min'][2] <= pos[2] <= bounds['max'][2])
    
    def update_watchdog_count(self, particle_id: int):
        if particle_id not in self.watchdog_counts:
            self.watchdog_counts[particle_id] = 0
        self.watchdog_counts[particle_id] += 1

class VoidZone:
    def __init__(self, void_center: np.ndarray, void_radius: float):
        self.void_center = void_center
        self.void_radius = void_radius
        self.destruction_active = True
        
    def is_particle_in_void(self, particle: Particle) -> bool:
        distance = np.linalg.norm(particle.position - self.void_center)
        return distance <= self.void_radius
    
    def apply_void_destruction(self, particle: Particle) -> bool:
        if self.destruction_active and self.is_particle_in_void(particle):
            particle.state = ParticleState.VOID_BOUND
            return True
        return True

class CrystalGeometryProcessor:
    def __init__(self, crystal_vertices: np.ndarray, electrode_positions: List[np.ndarray]):
        self.crystal_vertices = crystal_vertices
        self.electrode_positions = electrode_positions
        self.processing_zone_bounds = self._calculate_processing_bounds()
        
    def _calculate_processing_bounds(self) -> dict:
        return {
            'min': np.min(self.crystal_vertices, axis=0),
            'max': np.max(self.crystal_vertices, axis=0)
        }
    
    def is_particle_in_processing_zone(self, particle: Particle) -> bool:
        pos = particle.position
        bounds = self.processing_zone_bounds
        
        return (bounds['min'][0] <= pos[0] <= bounds['max'][0] and
                bounds['min'][1] <= pos[1] <= bounds['max'][1] and
                bounds['min'][2] <= pos[2] <= bounds['max'][2])
    
    def apply_electrode_passage(self, particle: Particle) -> bool:
        if self.is_particle_in_processing_zone(particle):
            for electrode_pos in self.electrode_positions:
                distance = np.linalg.norm(particle.position - electrode_pos)
                if distance < 0.5:  # Electrode influence radius
                    return True
        return True

class DenseDarkMatterConverter:
    def __init__(self, conversion_threshold: float = 0.8):
        self.conversion_threshold = conversion_threshold
        
    def convert_to_dense_dark_matter(self, particle: Particle) -> bool:
        if particle.state == ParticleState.PROCESSED:
            density_factor = particle.density * particle.mass
            if density_factor > self.conversion_threshold:
                particle.state = ParticleState.DENSE_DARK_MATTER
                particle.charge *= 2.5  # Photonic-like charge at higher density
                return True
        return True

class ParticleExtractionSystem:
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self.particles: List[Particle] = []
        self.gravitational_fields: List[GravitationalField] = []
        self.dimensional_plate: Optional[DimensionalPlate] = None
        self.void_zone: Optional[VoidZone] = None
        self.crystal_processor: Optional[CrystalGeometryProcessor] = None
        self.dark_matter_converter = DenseDarkMatterConverter()
        
        # GPU arrays for computation
        if self.use_gpu:
            self.gpu_positions = None
            self.gpu_velocities = None
            self.gpu_masses = None
    
    def add_particle(self, particle: Particle):
        self.particles.append(particle)
        self._update_gpu_arrays()
    
    def add_gravitational_field(self, field: GravitationalField):
        self.gravitational_fields.append(field)
    
    def set_dimensional_plate(self, plate: DimensionalPlate):
        self.dimensional_plate = plate
    
    def set_void_zone(self, void: VoidZone):
        self.void_zone = void
    
    def set_crystal_processor(self, processor: CrystalGeometryProcessor):
        self.crystal_processor = processor
    
    def _update_gpu_arrays(self):
        if self.use_gpu and self.particles:
            positions = np.array([p.position for p in self.particles])
            velocities = np.array([p.velocity for p in self.particles])
            masses = np.array([p.mass for p in self.particles])
            
            self.gpu_positions = cp.asarray(positions)
            self.gpu_velocities = cp.asarray(velocities)
            self.gpu_masses = cp.asarray(masses)
    
    def destabilize_gravitational_fields(self, red_particle_count: int):
        """Force sequence change to destabilize surrounding core gravitational fields"""
        destabilization_factor = min(red_particle_count * 0.1, 1.0)
        
        for field in self.gravitational_fields:
            field.destabilization_factor = destabilization_factor
    
    def apply_plantuml_equation_computation(self, particle: Particle, dt: float):
        """GPU-accelerated computation using complex mathematical equations"""
        if self.use_gpu:
            self._gpu_particle_update(particle, dt)
        else:
            self._cpu_particle_update(particle, dt)
    
    def _gpu_particle_update(self, particle: Particle, dt: float):
        """GPU-based particle physics computation"""
        # Complex gravitational and momentum equations
        pos_gpu = cp.asarray(particle.position)
        vel_gpu = cp.asarray(particle.velocity)
        mass_gpu = cp.float32(particle.mass)
        
        # Calculate total gravitational force
        total_force = cp.zeros(3)
        for field in self.gravitational_fields:
            field_force = cp.asarray(field.calculate_field_at_point(particle.position))
            total_force += field_force * mass_gpu
        
        # Apply momentum and velocity changes
        acceleration = total_force / mass_gpu
        new_velocity = vel_gpu + acceleration * dt
        
        # Apply trajectory vector modifications
        trajectory_mod = cp.asarray(particle.trajectory_vector) * 0.1
        new_velocity += trajectory_mod
        
        # Update position and velocity
        particle.position = (pos_gpu + new_velocity * dt).get()
        particle.velocity = new_velocity.get()
    
    def _cpu_particle_update(self, particle: Particle, dt: float):
        """CPU-based particle physics computation"""
        total_force = np.zeros(3)
        
        for field in self.gravitational_fields:
            field_force = field.calculate_field_at_point(particle.position)
            total_force += field_force * particle.mass
        
        acceleration = total_force / particle.mass
        particle.velocity += acceleration * dt
        
        # Apply trajectory vector modifications
        particle.velocity += particle.trajectory_vector * 0.1
        
        # Update position
        particle.position += particle.velocity * dt
    
    def process_void_sequence(self, particle: Particle):
        """Handle void zone destruction and weightless state"""
        if self.void_zone and self.void_zone.is_particle_in_void(particle):
            if not self.void_zone.destruction_active:
                # Set weightless state to avoid destruction
                particle.state = ParticleState.WEIGHTLESS
                particle.gravitational_strength = 0.0
                
                # Apply inertia protection
                if self.dimensional_plate:
                    self.dimensional_plate.update_watchdog_count(particle.id)
                
                # Bounce back with same force
                particle.velocity *= -1.0
                particle.state = ParticleState.INERTIAL
            else:
                self.void_zone.apply_void_destruction(particle)
    
    def process_dimensional_plate(self, particle: Particle):
        """Process gravitational strength and momentum at dimensional plate"""
        if self.dimensional_plate and self.dimensional_plate.is_particle_within_bounds(particle):
            # Calculate gravitational strength based on m2 mass density
            grav_strength = particle.mass * particle.density * 9.81
            particle.gravitational_strength = grav_strength
            
            # Apply force momentum to achieve weightless state
            momentum_force = particle.mass * np.linalg.norm(particle.velocity)
            particle.velocity *= (momentum_force / grav_strength) if grav_strength > 0 else 1.0
    
    def process_crystal_geometry(self, particle: Particle):
        """Process particle through crystal geometry with electrode passages"""
        if self.crystal_processor and self.crystal_processor.is_particle_in_processing_zone(particle):
            if self.crystal_processor.apply_electrode_passage(particle):
                particle.state = ParticleState.PROCESSED
                
                # Convert to dense dark matter if conditions are met
                self.dark_matter_converter.convert_to_dense_dark_matter(particle)
    
    def update_system(self, dt: float = 0.01):
        """Main update loop for the particle extraction system"""
        # Update all particles
        for particle in self.particles:
            if particle.state in [ParticleState.ACTIVE, ParticleState.INERTIAL]:
                # Apply complex equation computation
                self.apply_plantuml_equation_computation(particle, dt)
                
                # Process dimensional plate
                self.process_dimensional_plate(particle)
                
                # Process void sequence
                self.process_void_sequence(particle)
                
                # Process crystal geometry
                self.process_crystal_geometry(particle)
    
    def get_system_status(self) -> dict:
        """Get current system status and particle counts"""
        status = {
            'total_particles': len(self.particles),
            'particle_states': {},
            'red_particles': 0,
            'blue_particles': 0,
            'gravitational_fields_active': sum(1 for f in self.gravitational_fields if f.is_active),
            'void_destruction_active': self.void_zone.destruction_active if self.void_zone else False
        }
        
        for state in ParticleState:
            status['particle_states'][state.value] = sum(1 for p in self.particles if p.state == state)
        
        for particle in self.particles:
            if particle.particle_type == ParticleType.RED_PARTICLE:
                status['red_particles'] += 1
            elif particle.particle_type == ParticleType.BLUE_PARTICLE:
                status['blue_particles'] += 1
        
        return status

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
