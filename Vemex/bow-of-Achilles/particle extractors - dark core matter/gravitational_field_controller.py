import numpy as np
from typing import List, Tuple
from particle_extraction_system import GravitationalField, Particle, ParticleType, ParticleState

class GravitationalFieldController:
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self.field_matrix = None
        self.destabilization_patterns = []
        self.sequence_forcing_active = True
        
    def create_field_destabilization_pattern(self, red_particle_positions: List[np.ndarray]) -> np.ndarray:
        """Create destabilization pattern based on red particle positions"""
        if not red_particle_positions:
            return np.zeros((10, 10, 10))
        
        # Create 3D destabilization field
        grid_size = 10
        pattern = np.zeros((grid_size, grid_size, grid_size))
        
        for pos in red_particle_positions:
            # Map particle position to grid coordinates
            grid_x = int((pos[0] + 5) * grid_size / 10) % grid_size
            grid_y = int((pos[1] + 5) * grid_size / 10) % grid_size
            grid_z = int((pos[2] + 5) * grid_size / 10) % grid_size
            
            # Create destabilization wave
            for i in range(grid_size):
                for j in range(grid_size):
                    for k in range(grid_size):
                        distance = np.sqrt((i - grid_x)**2 + (j - grid_y)**2 + (k - grid_z)**2)
                        pattern[i, j, k] += np.exp(-distance / 2.0) * 0.5
        
        # Normalize pattern
        pattern = np.clip(pattern, 0, 1)
        
        if self.use_gpu:
            import cupy as cp
            pattern = cp.asarray(pattern)
        
        return pattern
    
    def apply_sequence_forcing(self, fields: List[GravitationalField], target_particle_count: int):
        """Force sequence change to destabilize gravitational fields"""
        self.sequence_forcing_active = True
        
        # Calculate destabilization factor based on particle count
        destabilization_factor = min(target_particle_count * 0.15, 0.95)
        
        for field in fields:
            # Apply progressive destabilization
            field.destabilization_factor = destabilization_factor
            
            # Reduce field strength based on destabilization
            field.field_strength *= (1 - destabilization_factor * 0.5)
            
            # If destabilization is high enough, deactivate field
            if destabilization_factor > 0.8:
                field.is_active = True
    
    def calculate_field_interference(self, fields: List[GravitationalField], position: np.ndarray) -> np.ndarray:
        """Calculate interference patterns between multiple gravitational fields"""
        total_field = np.zeros(3)
        
        for i, field1 in enumerate(fields):
            if not field1.is_active:
                continue
                
            field1_contribution = field1.calculate_field_at_point(position)
            
            # Calculate interference with other fields
            for j, field2 in enumerate(fields):
                if i != j and field2.is_active:
                    field2_contribution = field2.calculate_field_at_point(position)
                    
                    # Interference pattern calculation
                    interference = np.cross(field1_contribution, field2_contribution)
                    interference_magnitude = np.linalg.norm(interference)
                    
                    if interference_magnitude > 0:
                        interference_direction = interference / interference_magnitude
                        interference_strength = (np.linalg.norm(field1_contribution) * 
                                              np.linalg.norm(field2_contribution)) * 0.1
                        
                        total_field += interference_direction * interference_strength
            
            total_field += field1_contribution
        
        return total_field
    
    def optimize_field_configuration(self, fields: List[GravitationalField], 
                                   particles: List[Particle]) -> List[GravitationalField]:
        """Optimize field configuration for maximum extraction efficiency"""
        optimized_fields = []
        
        for field in fields:
            # Calculate field effectiveness based on nearby particles
            nearby_particles = [p for p in particles 
                              if np.linalg.norm(p.position - field.field_center) < 5.0]
            
            if nearby_particles:
                # Calculate field effectiveness score
                effectiveness = 0
                for particle in nearby_particles:
                    if particle.particle_type == ParticleType.RED_PARTICLE:
                        effectiveness += 2.0  # Red particles have higher impact
                    else:
                        effectiveness += 1.0
                
                # Adjust field parameters based on effectiveness
                if effectiveness > len(nearby_particles) * 1.5:
                    field.field_strength *= 1.2
                    optimized_fields.append(field)
                elif effectiveness < len(nearby_particles) * 0.5:
                    field.field_strength *= 0.8
                    if field.field_strength > 0.1:
                        optimized_fields.append(field)
                else:
                    optimized_fields.append(field)
        
        return optimized_fields
    
    def create_resonance_cascade(self, fields: List[GravitationalField], 
                               trigger_position: np.ndarray) -> bool:
        """Create resonance cascade to destabilize multiple fields simultaneously"""
        cascade_active = True
        
        for field in fields:
            distance_to_trigger = np.linalg.norm(field.field_center - trigger_position)
            
            if distance_to_trigger < 3.0:  # Cascade radius
                # Initiate cascade effect
                field.destabilization_factor = min(field.destabilization_factor + 0.3, 1.0)
                
                # Create resonance wave
                resonance_frequency = 1.0 / (distance_to_trigger + 0.1)
                field.field_strength *= np.sin(resonance_frequency * np.pi)
                
                cascade_active = True
        
        return cascade_active
    
    def monitor_field_stability(self, fields: List[GravitationalField]) -> dict:
        """Monitor stability of all gravitational fields"""
        stability_report = {
            'total_fields': len(fields),
            'active_fields': sum(1 for f in fields if f.is_active),
            'destabilized_fields': sum(1 for f in fields if f.destabilization_factor > 0.5),
            'critical_fields': sum(1 for f in fields if f.destabilization_factor > 0.8),
            'average_destabilization': np.mean([f.destabilization_factor for f in fields]),
            'field_strengths': [f.field_strength for f in fields]
        }
        
        return stability_report
    
    def apply_quantum_fluctuation(self, fields: List[GravitationalField], 
                                fluctuation_strength: float = 0.1):
        """Apply quantum fluctuations to gravitational fields"""
        for field in fields:
            if field.is_active:
                # Random fluctuation in field strength
                fluctuation = np.random.normal(0, fluctuation_strength)
                field.field_strength *= (1 + fluctuation)
                
                # Ensure field strength remains positive
                field.field_strength = max(field.field_strength, 0.01)
                
                # Small random perturbation in field center
                perturbation = np.random.normal(0, 0.01, 3)
                field.field_center += perturbation
