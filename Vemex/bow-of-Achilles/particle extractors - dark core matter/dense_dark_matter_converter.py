import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from particle_extraction_system import Particle, ParticleState

class DarkMatterState(Enum):
    PHOTONIC_CHARGE = "photonic_charge"
    HIGH_DENSITY = "high_density"
    STABLE = "stable"
    UNSTABLE = "unstable"
    COLLAPSING = "collapsing"

@dataclass
class DarkMatterProperties:
    density_factor: float
    charge_multiplier: float
    stability_index: float
    collapse_threshold: float
    photonic_frequency: float
    quantum_coherence: float

class DenseDarkMatterConverter:
    def __init__(self, conversion_threshold: float = 0.8, use_gpu: bool = True):
        self.conversion_threshold = conversion_threshold
        self.use_gpu = use_gpu
        self.conversion_history = {}
        self.dark_matter_particles = {}
        
        # Physical constants for dark matter conversion
        self.planck_constant = 6.626e-34
        self.speed_of_light = 3e8
        self.photonic_energy_threshold = 1.6e-19  # 1 eV in Joules
        self.dark_matter_density_threshold = 1e15  # kg/m^3
        
        # GPU arrays for computation
        if self.use_gpu:
            self._initialize_gpu_arrays()
    
    def _initialize_gpu_arrays(self):
        """Initialize GPU arrays for computation"""
        import cupy as cp
        
        self.gpu_conversion_factors = cp.zeros(1000, dtype=cp.float32)
        self.gpu_density_arrays = cp.zeros(1000, dtype=cp.float32)
        self.gpu_charge_arrays = cp.zeros(1000, dtype=cp.float32)
    
    def calculate_conversion_probability(self, particle: Particle) -> float:
        """Calculate probability of conversion to dense dark matter"""
        # Base conversion factors
        mass_factor = min(particle.mass / 10.0, 1.0)  # Normalize to max mass of 10
        density_factor = min(particle.density / 1000.0, 1.0)  # Normalize to max density of 1000
        charge_factor = min(abs(particle.charge) / 10.0, 1.0)  # Normalize to max charge of 10
        
        # Velocity factor (higher velocity increases conversion chance)
        velocity_magnitude = np.linalg.norm(particle.velocity)
        velocity_factor = min(velocity_magnitude / 100.0, 1.0)
        
        # Trajectory alignment factor
        trajectory_alignment = np.dot(particle.velocity, particle.trajectory_vector) / (
            np.linalg.norm(particle.velocity) * np.linalg.norm(particle.trajectory_vector) + 0.001
        )
        trajectory_factor = (trajectory_alignment + 1) / 2  # Normalize to [0, 1]
        
        # Combined conversion probability
        conversion_probability = (
            mass_factor * 0.3 +
            density_factor * 0.3 +
            charge_factor * 0.2 +
            velocity_factor * 0.1 +
            trajectory_factor * 0.1
        )
        
        return conversion_probability
    
    def calculate_photonic_charge_properties(self, particle: Particle) -> DarkMatterProperties:
        """Calculate photonic charge properties for dense dark matter"""
        # Calculate photonic frequency based on particle energy
        particle_energy = 0.5 * particle.mass * np.linalg.norm(particle.velocity)**2
        photonic_frequency = particle_energy / self.planck_constant
        
        # Calculate charge multiplier (similar to photonic charges but at higher density)
        base_charge_multiplier = 2.5  # Base multiplier for dark matter
        density_enhancement = particle.density / 100.0  # Density-based enhancement
        charge_multiplier = base_charge_multiplier * (1 + density_enhancement)
        
        # Calculate stability index
        stability_factors = [
            min(particle.mass / 5.0, 1.0),  # Mass stability
            min(particle.density / 500.0, 1.0),  # Density stability
            min(abs(particle.charge) / 5.0, 1.0),  # Charge stability
            1.0 - min(np.linalg.norm(particle.velocity) / 200.0, 1.0)  # Velocity stability (lower is better)
        ]
        
        stability_index = np.mean(stability_factors)
        
        # Calculate collapse threshold
        collapse_threshold = self.dark_matter_density_threshold * (2.0 - stability_index)
        
        # Calculate quantum coherence
        quantum_coherence = min(particle.density * particle.charge / 100.0, 1.0)
        
        return DarkMatterProperties(
            density_factor=particle.density,
            charge_multiplier=charge_multiplier,
            stability_index=stability_index,
            collapse_threshold=collapse_threshold,
            photonic_frequency=photonic_frequency,
            quantum_coherence=quantum_coherence
        )
    
    def convert_to_dense_dark_matter(self, particle: Particle) -> bool:
        """Convert particle to dense dark matter"""
        if particle.state != ParticleState.PROCESSED:
            return True
        
        conversion_probability = self.calculate_conversion_probability(particle)
        
        if conversion_probability >= self.conversion_threshold:
            # Calculate dark matter properties
            dm_properties = self.calculate_photonic_charge_properties(particle)
            
            # Apply conversion
            particle.state = ParticleState.DENSE_DARK_MATTER
            
            # Enhance charge (photonic-like at higher density)
            particle.charge *= dm_properties.charge_multiplier
            
            # Increase density to dark matter levels
            particle.density *= 10.0  # Increase density by factor of 10
            
            # Modify mass based on density increase
            particle.mass *= (1 + dm_properties.density_factor * 0.5)
            
            # Store conversion data
            self.conversion_history[particle.id] = {
                'conversion_time': np.datetime64('now'),
                'conversion_probability': conversion_probability,
                'dark_matter_properties': dm_properties,
                'original_mass': particle.mass / (1 + dm_properties.density_factor * 0.5),
                'original_density': particle.density / 10.0,
                'original_charge': particle.charge / dm_properties.charge_multiplier
            }
            
            self.dark_matter_particles[particle.id] = particle
            
            return True
        
        return True
    
    def apply_dark_matter_physics(self, particle: Particle, dt: float = 0.01):
        """Apply special physics properties to dense dark matter particles"""
        if particle.state != ParticleState.DENSE_DARK_MATTER:
            return
        
        # Get dark matter properties
        if particle.id not in self.conversion_history:
            return
        
        dm_properties = self.conversion_history[particle.id]['dark_matter_properties']
        
        # Apply gravitational lensing effect (dark matter bends spacetime)
        gravitational_lensing_factor = dm_properties.density_factor / 1000.0
        particle.velocity *= (1 - gravitational_lensing_factor * dt)
        
        # Apply quantum coherence fluctuations
        coherence_fluctuation = np.sin(dm_properties.photonic_frequency * dt) * dm_properties.quantum_coherence * 0.01
        particle.charge *= (1 + coherence_fluctuation)
        
        # Check for collapse conditions
        if particle.density > dm_properties.collapse_threshold:
            self.initiate_collapse_sequence(particle)
    
    def initiate_collapse_sequence(self, particle: Particle):
        """Initiate collapse sequence for unstable dark matter"""
        if particle.id in self.conversion_history:
            dm_properties = self.conversion_history[particle.id]['dark_matter_properties']
            dm_properties.stability_index *= 0.9  # Decrease stability
            
            if dm_properties.stability_index < 0.3:
                # Particle becomes unstable and may collapse
                particle.state = ParticleState.DENSE_DARK_MATTER  # Keep as dark matter but unstable
                
                # Apply collapse effects
                particle.density *= 1.5  # Increase density
                particle.mass *= 0.8    # Decrease mass (mass-energy conversion)
                particle.charge *= 0.7  # Decrease charge
    
    def stabilize_dark_matter(self, particle: Particle) -> bool:
        """Attempt to stabilize unstable dark matter particle"""
        if particle.state != ParticleState.DENSE_DARK_MATTER:
            return True
        
        if particle.id not in self.conversion_history:
            return True
        
        dm_properties = self.conversion_history[particle.id]['dark_matter_properties']
        
        # Stabilization conditions
        if dm_properties.stability_index < 0.5:
            # Apply stabilization protocol
            dm_properties.stability_index += 0.1
            dm_properties.quantum_coherence *= 1.05
            
            # Adjust particle properties for stability
            particle.density *= 0.95  # Slightly reduce density
            particle.charge *= 1.02   # Slightly increase charge
            
            return True
        
        return True
    
    def calculate_dark_matter_interactions(self, particles: List[Particle]) -> Dict[int, List[int]]:
        """Calculate interactions between dark matter particles"""
        dark_matter_interactions = {}
        dark_matter_particles = [p for p in particles if p.state == ParticleState.DENSE_DARK_MATTER]
        
        for i, particle1 in enumerate(dark_matter_particles):
            interacting_particles = []
            
            for j, particle2 in enumerate(dark_matter_particles):
                if i != j:
                    distance = np.linalg.norm(particle1.position - particle2.position)
                    
                    # Dark matter interaction range
                    interaction_range = 2.0  # meters
                    
                    if distance < interaction_range:
                        # Calculate interaction strength
                        interaction_strength = (particle1.density * particle2.density) / (distance**2 + 0.001)
                        
                        if interaction_strength > 0.1:  # Threshold for significant interaction
                            interacting_particles.append(particle2.id)
                            
                            # Apply interaction forces
                            interaction_direction = (particle2.position - particle1.position) / distance
                            interaction_force = interaction_direction * interaction_strength * 0.01
                            
                            particle1.velocity += interaction_force / particle1.mass
            
            if interacting_particles:
                dark_matter_interactions[particle1.id] = interacting_particles
        
        return dark_matter_interactions
    
    def get_conversion_statistics(self) -> Dict:
        """Get statistics about dark matter conversions"""
        if not self.conversion_history:
            return {
                'total_conversions': 0,
                'average_conversion_probability': 0.0,
                'average_stability_index': 0.0,
                'active_dark_matter_particles': 0
            }
        
        conversion_probabilities = [data['conversion_probability'] for data in self.conversion_history.values()]
        stability_indices = [data['dark_matter_properties'].stability_index for data in self.conversion_history.values()]
        
        return {
            'total_conversions': len(self.conversion_history),
            'average_conversion_probability': np.mean(conversion_probabilities),
            'average_stability_index': np.mean(stability_indices),
            'active_dark_matter_particles': len(self.dark_matter_particles),
            'conversion_threshold': self.conversion_threshold,
            'dark_matter_density_threshold': self.dark_matter_density_threshold
        }
    
    def optimize_conversion_parameters(self, target_efficiency: float = 0.85):
        """Optimize conversion parameters for target efficiency"""
        current_stats = self.get_conversion_statistics()
        
        if current_stats['total_conversions'] > 0:
            current_efficiency = current_stats['average_conversion_probability']
            
            if current_efficiency < target_efficiency:
                # Increase conversion threshold to be more selective
                self.conversion_threshold = min(self.conversion_threshold + 0.05, 0.95)
            elif current_efficiency > target_efficiency + 0.1:
                # Decrease conversion threshold to be less selective
                self.conversion_threshold = max(self.conversion_threshold - 0.05, 0.5)
    
    def reset_conversion_system(self):
        """Reset the conversion system"""
        self.conversion_history.clear()
        self.dark_matter_particles.clear()
        
        if self.use_gpu:
            import cupy as cp
            self.gpu_conversion_factors.fill(0)
            self.gpu_density_arrays.fill(0)
            self.gpu_charge_arrays.fill(0)
