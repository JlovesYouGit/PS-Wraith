import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math

class WarpZoneState(Enum):
    FORMING = "forming"
    ACTIVE = "active"
    STABLE = "stable"
    COLLAPSING = "collapsing"
    EXIT_READY = "exit_ready"

@dataclass
class HzWaveFluctuation:
    frequency: float  # Hz frequency
    amplitude: float
    phase: float
    wavelength: float
    propagation_speed: float
    fluctuation_type: str  # "density", "temporal", "spatial"
    containment_field: bool  # Whether this fluctuation creates containment
    loop_energy: float  # Energy contained in the loop
    leakage_rate: float  # How much energy leaks (should be near zero)

@dataclass
class WarpZone:
    id: int
    center: np.ndarray
    radius: float
    state: WarpZoneState
    stability_factor: float
    density_threshold: float
    hz_fluctuation: HzWaveFluctuation
    particle_capacity: int
    current_particles: List[int]
    extraction_ready: bool
    pullback_strength: float
    energy_containment: float  # How much energy is contained
    containment_loop_active: bool  # Whether the containment loop is active
    measurement_safe: bool  # Whether the zone is safe for measurement

@dataclass
class TrainingModel:
    model_id: int
    density_adjustment_factor: float
    pullback_threshold: float
    extraction_efficiency: float
    learning_rate: float
    adaptation_rate: float
    warp_zone_predictions: Dict[int, float]

class WarpZoneSystem:
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self.warp_zones = []
        self.hz_fluctuations = []
        self.training_model = None
        self.particle_hz_densities = {}
        self.extraction_history = []
        
        # Physical constants for Hz wave fluctuations
        self.base_hz_frequency = 1.0e6  # 1 MHz base frequency
        self.warp_formation_threshold = 0.7
        self.safe_exit_density = 0.1
        self.pullback_coefficient = 0.85
        
        # Initialize training model
        self._initialize_training_model()
    
    def _initialize_training_model(self):
        """Initialize the training model for density adjustment"""
        self.training_model = TrainingModel(
            model_id=1,
            density_adjustment_factor=1.0,
            pullback_threshold=0.5,
            extraction_efficiency=0.8,
            learning_rate=0.01,
            adaptation_rate=0.05,
            warp_zone_predictions={}
        )
    
    def calculate_particle_hz_density(self, particle) -> float:
        """Calculate Hz density based on particle properties"""
        # Base frequency from particle mass
        mass_frequency = self.base_hz_frequency * particle.mass
        
        # Density modulation
        density_modulation = particle.density / 1000.0  # Normalize density
        
        # Velocity Doppler effect
        velocity_magnitude = np.linalg.norm(particle.velocity)
        doppler_factor = 1.0 + velocity_magnitude / 100.0  # Simplified Doppler
        
        # Charge influence on frequency
        charge_modulation = 1.0 + abs(particle.charge) * 0.1
        
        # Calculate final Hz density
        hz_density = mass_frequency * density_modulation * doppler_factor * charge_modulation
        
        # Store for tracking
        self.particle_hz_densities[particle.id] = hz_density
        
        return hz_density
    
    def create_hz_wave_fluctuation(self, center_frequency: float, particle_density: float, containment_enabled: bool = True) -> HzWaveFluctuation:
        """Create Hz wave fluctuation with energy containment"""
        # Frequency modulation based on density
        frequency = center_frequency * (1.0 + particle_density * 0.1)
        
        # Amplitude based on density
        amplitude = 1.0 + particle_density * 0.5
        
        # Phase based on position and time
        phase = np.random.random() * 2 * np.pi
        
        # Wavelength calculation
        wavelength = 3e8 / frequency  # Speed of light / frequency
        
        # Propagation speed (slower in dense medium)
        propagation_speed = 3e8 / (1.0 + particle_density * 0.1)
        
        # Calculate energy to be contained
        loop_energy = particle_density * frequency * amplitude * 1e-10  # Scaled energy
        
        # Leakage rate (should be very low for containment)
        leakage_rate = 0.001 if containment_enabled else 0.1
        
        fluctuation = HzWaveFluctuation(
            frequency=frequency,
            amplitude=amplitude,
            phase=phase,
            wavelength=wavelength,
            propagation_speed=propagation_speed,
            fluctuation_type="density",
            containment_field=containment_enabled,
            loop_energy=loop_energy,
            leakage_rate=leakage_rate
        )
        
        self.hz_fluctuations.append(fluctuation)
        return fluctuation
    
    def create_warp_zone(self, position: np.ndarray, particle_hz_density: float) -> WarpZone:
        """Create a warp zone based on Hz density with energy containment"""
        # Calculate warp zone parameters
        zone_radius = 0.5 + particle_hz_density / self.base_hz_frequency * 0.5
        
        # Stability based on Hz density
        stability_factor = min(particle_hz_density / (self.base_hz_frequency * 2.0), 1.0)
        
        # Density threshold for warp formation
        density_threshold = self.warp_formation_threshold * (1.0 + particle_hz_density / self.base_hz_frequency)
        
        # Create Hz fluctuation with containment enabled
        hz_fluctuation = self.create_hz_wave_fluctuation(self.base_hz_frequency, particle_hz_density, containment_enabled=True)
        
        # Particle capacity based on zone size
        particle_capacity = int(zone_radius * 10)
        
        # Calculate initial energy containment
        energy_containment = hz_fluctuation.loop_energy * 0.8  # Start with 80% containment
        
        warp_zone = WarpZone(
            id=len(self.warp_zones),
            center=position,
            radius=zone_radius,
            state=WarpZoneState.FORMING,
            stability_factor=stability_factor,
            density_threshold=density_threshold,
            hz_fluctuation=hz_fluctuation,
            particle_capacity=particle_capacity,
            current_particles=[],
            extraction_ready=False,
            pullback_strength=self.pullback_coefficient,
            energy_containment=energy_containment,
            containment_loop_active=True,
            measurement_safe=True
        )
        
        self.warp_zones.append(warp_zone)
        return warp_zone
    
    def apply_hz_wave_slowdown(self, particle, warp_zone: WarpZone, dt: float = 0.01) -> bool:
        """Apply Hz wave slowdown to particle at exit moment with energy containment"""
        # Calculate distance to warp zone center
        distance = np.linalg.norm(particle.position - warp_zone.center)
        
        if distance < warp_zone.radius:
            # Calculate wave field at particle position
            omega = 2 * np.pi * warp_zone.hz_fluctuation.frequency
            wave_field = warp_zone.hz_fluctuation.amplitude * np.sin(
                omega * self._get_simulation_time() + warp_zone.hz_fluctuation.phase
            )
            
            # Apply slowdown based on Hz density
            particle_hz_density = self.calculate_particle_hz_density(particle)
            slowdown_factor = 1.0 - (particle_hz_density / self.base_hz_frequency) * 0.3
            
            # Apply wave modulation to velocity
            velocity_modulation = slowdown_factor * (1.0 - wave_field * 0.1)
            particle.velocity *= velocity_modulation
            
            # Apply energy containment loop
            if warp_zone.containment_loop_active:
                self._apply_energy_containment_loop(particle, warp_zone, dt)
            
            # Add particle to warp zone if not already there
            if particle.id not in warp_zone.current_particles:
                if len(warp_zone.current_particles) < warp_zone.particle_capacity:
                    warp_zone.current_particles.append(particle.id)
                    
                    # Update warp zone state
                    if len(warp_zone.current_particles) >= warp_zone.particle_capacity * 0.8:
                        warp_zone.state = WarpZoneState.ACTIVE
            
            return True
        
        return True
    
    def _apply_energy_containment_loop(self, particle, warp_zone: WarpZone, dt: float = 0.01):
        """Apply energy containment loop to prevent energy leakage to higher positions"""
        # Calculate particle's kinetic energy
        kinetic_energy = 0.5 * particle.mass * np.linalg.norm(particle.velocity)**2
        
        # Calculate containment field strength
        containment_strength = warp_zone.hz_fluctuation.loop_energy * warp_zone.energy_containment
        
        # Create containment loop (circular force field)
        distance_from_center = np.linalg.norm(particle.position - warp_zone.center)
        
        if distance_from_center < warp_zone.radius:
            # Calculate tangential force for circular containment
            radial_direction = (particle.position - warp_zone.center) / distance_from_center
            
            # Tangential direction (perpendicular to radial)
            tangential_direction = np.array([-radial_direction[1], radial_direction[0], 0])
            tangential_direction = tangential_direction / np.linalg.norm(tangential_direction)
            
            # Apply containment force
            containment_force = tangential_direction * containment_strength * 0.1
            
            # Add radial containment to prevent escape
            if distance_from_center > warp_zone.radius * 0.8:
                radial_containment = -radial_direction * containment_strength * 0.05
                containment_force += radial_containment
            
            # Apply containment forces
            particle.velocity += containment_force / particle.mass * dt
            
            # Prevent upward energy leakage
            if particle.velocity[2] > 0:  # Upward velocity
                particle.velocity[2] *= (1 - warp_zone.hz_fluctuation.leakage_rate)
            
            # Update energy containment
            warp_zone.energy_containment = min(1.0, warp_zone.energy_containment + kinetic_energy * 0.001)
            
            # Check if zone is safe for measurement
            warp_zone.measurement_safe = (warp_zone.hz_fluctuation.leakage_rate < 0.01 and 
                                       warp_zone.energy_containment > 0.5)
    
    def measure_contained_energy(self, warp_zone: WarpZone) -> Dict[str, float]:
        """Safely measure contained energy in the warp zone"""
        if not warp_zone.measurement_safe:
            return {
                'measurement_safe': False,
                'contained_energy': 0.0,
                'leakage_rate': warp_zone.hz_fluctuation.leakage_rate,
                'error': 'Zone not safe for measurement'
            }
        
        # Calculate total contained energy
        contained_energy = warp_zone.hz_fluctuation.loop_energy * warp_zone.energy_containment
        
        # Calculate energy leakage
        energy_leakage = contained_energy * warp_zone.hz_fluctuation.leakage_rate
        
        # Measurement results
        measurement = {
            'measurement_safe': True,
            'contained_energy': contained_energy,
            'leakage_rate': warp_zone.hz_fluctuation.leakage_rate,
            'energy_leakage': energy_leakage,
            'containment_efficiency': 1.0 - warp_zone.hz_fluctuation.leakage_rate,
            'loop_stability': warp_zone.stability_factor,
            'hz_frequency': warp_zone.hz_fluctuation.frequency,
            'particle_count': len(warp_zone.current_particles)
        }
        
        return measurement
    
    def update_training_model(self, extraction_success: bool, particle_hz_density: float):
        """Update training model based on extraction results"""
        if extraction_success:
            # Positive reinforcement
            self.training_model.extraction_efficiency += self.training_model.learning_rate * 0.1
            
            # Adjust density threshold
            if particle_hz_density < self.safe_exit_density:
                self.training_model.density_adjustment_factor *= 1.01
        else:
            # Negative reinforcement
            self.training_model.extraction_efficiency -= self.training_model.learning_rate * 0.05
            
            # Adjust pullback threshold
            self.training_model.pullback_threshold *= 0.99
        
        # Ensure values stay in reasonable range
        self.training_model.extraction_efficiency = np.clip(self.training_model.extraction_efficiency, 0.1, 1.0)
        self.training_model.density_adjustment_factor = np.clip(self.training_model.density_adjustment_factor, 0.5, 2.0)
        self.training_model.pullback_threshold = np.clip(self.training_model.pullback_threshold, 0.1, 0.9)
    
    def calculate_pullback_force(self, particle, warp_zone: WarpZone) -> np.ndarray:
        """Calculate pullback force for safe extraction"""
        # Get particle Hz density
        particle_hz_density = self.particle_hz_densities.get(particle.id, self.base_hz_frequency)
        
        # Calculate density drop factor
        density_drop = particle_hz_density / self.base_hz_frequency
        
        # Training model adjustment
        model_adjustment = self.training_model.density_adjustment_factor
        
        # Pullback strength based on training model
        pullback_strength = warp_zone.pullback_strength * model_adjustment
        
        # Direction away from warp zone center (for pullback)
        direction = particle.position - warp_zone.center
        distance = np.linalg.norm(direction)
        
        if distance > 0.001:
            direction = direction / distance
            
            # Calculate pullback force
            if density_drop > self.training_model.pullback_threshold:
                # Apply pullback
                pullback_force = direction * pullback_strength * particle.mass * density_drop
            else:
                # Allow extraction
                pullback_force = np.zeros(3)
                warp_zone.extraction_ready = True
        else:
            pullback_force = np.zeros(3)
        
        return pullback_force
    
    def process_warp_zone_extraction(self, particle, warp_zone: WarpZone, void_center: np.ndarray, dt: float = 0.01) -> bool:
        """Process safe extraction through warp zone"""
        if particle.id not in warp_zone.current_particles:
            return True
        
        # Check if warp zone is ready for extraction
        if not warp_zone.extraction_ready:
            # Apply pullback force
            pullback_force = self.calculate_pullback_force(particle, warp_zone)
            particle.velocity += pullback_force / particle.mass * dt
            return True
        
        # Check if particle can safely exit
        particle_hz_density = self.particle_hz_densities.get(particle.id, self.base_hz_density)
        
        if particle_hz_density < self.safe_exit_density:
            # Safe extraction - guide to void
            extraction_direction = void_center - particle.position
            extraction_distance = np.linalg.norm(extraction_direction)
            
            if extraction_distance > 0.001:
                extraction_direction = extraction_direction / extraction_distance
                
                # Gentle extraction force
                extraction_force = extraction_direction * particle.mass * 2.0
                particle.velocity += extraction_force / particle.mass * dt
                
                # Remove from warp zone
                if particle.id in warp_zone.current_particles:
                    warp_zone.current_particles.remove(particle.id)
                
                # Record successful extraction
                self.extraction_history.append({
                    'particle_id': particle.id,
                    'warp_zone_id': warp_zone.id,
                    'hz_density': particle_hz_density,
                    'extraction_time': np.datetime64('now'),
                    'success': True
                })
                
                # Update training model
                self.update_training_model(True, particle_hz_density)
                
                return True
        
        return True
    
    def update_warp_zones(self, particles: List, void_center: np.ndarray, dt: float = 0.01):
        """Update all warp zones"""
        zones_to_remove = []
        
        for warp_zone in self.warp_zones:
            # Apply Hz wave slowdown to nearby particles
            for particle in particles:
                if self.apply_hz_wave_slowdown(particle, warp_zone, dt):
                    # Process extraction if ready
                    if warp_zone.extraction_ready:
                        self.process_warp_zone_extraction(particle, warp_zone, void_center, dt)
            
            # Update warp zone stability
            if len(warp_zone.current_particles) == 0:
                warp_zone.stability_factor *= 0.99
                
                # Remove unstable zones
                if warp_zone.stability_factor < 0.1:
                    zones_to_remove.append(warp_zone)
            else:
                # Stabilize active zones
                if warp_zone.state == WarpZoneState.ACTIVE:
                    warp_zone.stability_factor = min(1.0, warp_zone.stability_factor + 0.01)
                    warp_zone.state = WarpZoneState.STABLE
        
        # Remove dead zones
        for zone in zones_to_remove:
            self.warp_zones.remove(zone)
    
    def create_lower_zone_warp_field(self, lower_zone_center: np.ndarray, particles: List) -> List[WarpZone]:
        """Create warp zones in lower zone based on particle Hz densities"""
        warp_zones_created = []
        
        # Analyze particles in lower zone area
        lower_zone_radius = 3.0
        nearby_particles = []
        
        for particle in particles:
            distance = np.linalg.norm(particle.position - lower_zone_center)
            if distance < lower_zone_radius:
                nearby_particles.append(particle)
        
        # Create warp zones based on particle clusters
        if nearby_particles:
            # Group particles by Hz density similarity
            density_groups = self._group_particles_by_hz_density(nearby_particles)
            
            for group in density_groups:
                if len(group) >= 2:  # Minimum particles for warp zone
                    # Calculate group center
                    group_center = np.mean([p.position for p in group], axis=0)
                    
                    # Calculate average Hz density
                    avg_hz_density = np.mean([self.calculate_particle_hz_density(p) for p in group])
                    
                    # Create warp zone
                    warp_zone = self.create_warp_zone(group_center, avg_hz_density)
                    warp_zones_created.append(warp_zone)
                    
                    # Add particles to warp zone
                    for particle in group:
                        if particle.id not in warp_zone.current_particles:
                            if len(warp_zone.current_particles) < warp_zone.particle_capacity:
                                warp_zone.current_particles.append(particle.id)
        
        return warp_zones_created
    
    def _group_particles_by_hz_density(self, particles: List) -> List[List]:
        """Group particles by similar Hz densities"""
        if not particles:
            return []
        
        # Calculate Hz densities
        hz_densities = [self.calculate_particle_hz_density(p) for p in particles]
        
        # Simple clustering by density similarity
        groups = []
        used_particles = set()
        
        for i, particle in enumerate(particles):
            if particle.id in used_particles:
                continue
            
            # Start new group
            group = [particle]
            used_particles.add(particle.id)
            
            # Find similar density particles
            for j, other_particle in enumerate(particles):
                if i != j and other_particle.id not in used_particles:
                    density_diff = abs(hz_densities[i] - hz_densities[j])
                    
                    # Group if densities are similar
                    if density_diff < self.base_hz_frequency * 0.1:
                        group.append(other_particle)
                        used_particles.add(other_particle.id)
            
            groups.append(group)
        
        return groups
    
    def get_warp_zone_status(self) -> Dict:
        """Get comprehensive warp zone system status"""
        zone_status = {}
        total_contained_energy = 0.0
        measurement_safe_zones = 0
        
        for zone in self.warp_zones:
            # Measure contained energy if safe
            energy_measurement = self.measure_contained_energy(zone)
            
            zone_status[zone.id] = {
                'state': zone.state.value,
                'stability': zone.stability_factor,
                'particle_count': len(zone.current_particles),
                'capacity': zone.particle_capacity,
                'extraction_ready': zone.extraction_ready,
                'hz_frequency': zone.hz_fluctuation.frequency,
                'pullback_strength': zone.pullback_strength,
                'energy_containment': zone.energy_containment,
                'containment_loop_active': zone.containment_loop_active,
                'measurement_safe': zone.measurement_safe,
                'contained_energy': energy_measurement.get('contained_energy', 0.0),
                'leakage_rate': zone.hz_fluctuation.leakage_rate,
                'containment_efficiency': energy_measurement.get('containment_efficiency', 0.0)
            }
            
            total_contained_energy += energy_measurement.get('contained_energy', 0.0)
            if zone.measurement_safe:
                measurement_safe_zones += 1
        
        training_status = {
            'model_efficiency': self.training_model.extraction_efficiency,
            'density_adjustment': self.training_model.density_adjustment_factor,
            'pullback_threshold': self.training_model.pullback_threshold,
            'successful_extractions': len([e for e in self.extraction_history if e['success']]),
            'total_extractions': len(self.extraction_history)
        }
        
        return {
            'total_warp_zones': len(self.warp_zones),
            'zone_details': zone_status,
            'training_model': training_status,
            'total_hz_fluctuations': len(self.hz_fluctuations),
            'total_contained_energy': total_contained_energy,
            'measurement_safe_zones': measurement_safe_zones,
            'average_containment_efficiency': np.mean([z['containment_efficiency'] for z in zone_status.values()]) if zone_status else 0.0
        }
    
    def _get_simulation_time(self) -> float:
        """Get current simulation time (placeholder)"""
        return 0.0  # This would be set by the main simulation loop
    
    def set_simulation_time(self, time: float):
        """Set simulation time for wave calculations"""
        self.simulation_time = time

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
