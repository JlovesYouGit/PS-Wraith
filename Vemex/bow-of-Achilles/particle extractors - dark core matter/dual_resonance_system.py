import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math

class DualResonanceState(Enum):
    NULL_ZONE = "null_zone"
    UP_RESONANCE = "up_resonance"
    DOWN_RESONANCE = "down_resonance"
    DUAL_CHANNEL = "dual_channel"
    MICRO_PLANK = "micro_plank"
    DIMENSIONAL_OVERLAP = "dimensional_overlap"
    QUAD_STATE = "quad_state"

@dataclass
class ResonanceChannel:
    channel_id: int
    frequency: float
    amplitude: float
    phase: float
    direction: np.ndarray  # Up or down force direction
    resonance_type: str  # "up", "down", "dual"
    active: bool

@dataclass
class MicroPlankScale:
    scale_factor: float  # Planck scale ~1.6e-35 m
    gravitational_direction: np.ndarray
    inertia_factor: float
    resonance_coupling: float
    dimensional_bridge: bool

@dataclass
class DimensionalOverlap:
    gravitational_dimension: np.ndarray
    non_gravitational_dimension: np.ndarray
    overlap_strength: float
    property_transfer_rate: float
    null_zone_stability: float

@dataclass
class QuadStateParticle:
    particle_id: int
    state_1: DualResonanceState  # Null zone
    state_2: DualResonanceState  # Up resonance
    state_3: DualResonanceState  # Down resonance
    state_4: DualResonanceState  # Dimensional overlap
    coherence_factor: float
    stability_matrix: np.ndarray

class DualResonanceSystem:
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self.resonance_channels = []
        self.micro_plank_scales = {}
        self.dimensional_overlaps = {}
        self.quad_state_particles = {}
        
        # Physical constants for resonance
        self.planck_length = 1.616e-35  # meters
        self.planck_frequency = 7.4e42  # Hz
        self.resonance_coupling_constant = 0.137  # Fine structure constant
        self.null_zone_threshold = 0.001
        self.coherence_threshold = 0.8
        
        # Initialize dual resonance channels
        self._initialize_resonance_channels()
    
    def _initialize_resonance_channels(self):
        """Initialize up and down resonance channels"""
        # Up resonance channel
        up_channel = ResonanceChannel(
            channel_id=0,
            frequency=self.planck_frequency * 1e-30,  # Scaled down for simulation
            amplitude=1.0,
            phase=0.0,
            direction=np.array([0, 0, 1]),  # Upward
            resonance_type="up",
            active=True
        )
        
        # Down resonance channel
        down_channel = ResonanceChannel(
            channel_id=1,
            frequency=self.planck_frequency * 1e-30,  # Same frequency, different phase
            amplitude=1.0,
            phase=np.pi,  # Opposite phase
            direction=np.array([0, 0, -1]),  # Downward
            resonance_type="down",
            active=True
        )
        
        self.resonance_channels = [up_channel, down_channel]
    
    def create_micro_plank_scale(self, particle_id: int, particle_velocity: np.ndarray) -> MicroPlankScale:
        """Create micro-planck scale gravitational self-direction"""
        # Calculate gravitational direction based on particle motion
        velocity_magnitude = np.linalg.norm(particle_velocity)
        if velocity_magnitude > 0.001:
            gravitational_direction = particle_velocity / velocity_magnitude
        else:
            gravitational_direction = np.array([0, 0, -1])  # Default downward
        
        # Calculate inertia factor based on velocity
        inertia_factor = min(velocity_magnitude / 10.0, 1.0)
        
        # Calculate resonance coupling
        resonance_coupling = self.resonance_coupling_constant * inertia_factor
        
        # Create micro plank scale
        micro_plank = MicroPlankScale(
            scale_factor=self.planck_length * 1e20,  # Scaled for visualization
            gravitational_direction=gravitational_direction,
            inertia_factor=inertia_factor,
            resonance_coupling=resonance_coupling,
            dimensional_bridge=True
        )
        
        self.micro_plank_scales[particle_id] = micro_plank
        return micro_plank
    
    def create_dimensional_overlap(self, particle_id: int) -> DimensionalOverlap:
        """Create overlap between gravitational and non-gravitational dimensions"""
        # Gravitational dimension (normal space)
        gravitational_dimension = np.array([1.0, 0.0, 0.0])
        
        # Non-gravitational dimension (null space)
        non_gravitational_dimension = np.array([0.0, 1.0, 0.0])
        
        # Calculate overlap strength
        overlap_strength = 0.5 + 0.5 * np.sin(np.random.random() * 2 * np.pi)
        
        # Property transfer rate
        property_transfer_rate = overlap_strength * 0.1
        
        # Null zone stability
        null_zone_stability = 1.0 - overlap_strength * 0.2
        
        overlap = DimensionalOverlap(
            gravitational_dimension=gravitational_dimension,
            non_gravitational_dimension=non_gravitational_dimension,
            overlap_strength=overlap_strength,
            property_transfer_rate=property_transfer_rate,
            null_zone_stability=null_zone_stability
        )
        
        self.dimensional_overlaps[particle_id] = overlap
        return overlap
    
    def create_quad_state_particle(self, particle) -> QuadStateParticle:
        """Create particle with 4 simultaneous states"""
        # Initialize 4 different states
        state_1 = DualResonanceState.NULL_ZONE
        state_2 = DualResonanceState.UP_RESONANCE
        state_3 = DualResonanceState.DOWN_RESONANCE
        state_4 = DualResonanceState.DIMENSIONAL_OVERLAP
        
        # Calculate coherence factor
        coherence_factor = np.random.random() * 0.3 + 0.7  # 0.7 to 1.0
        
        # Create stability matrix (4x4 matrix for state interactions)
        stability_matrix = np.random.random((4, 4)) * 0.5 + 0.5
        stability_matrix = (stability_matrix + stability_matrix.T) / 2  # Make symmetric
        np.fill_diagonal(stability_matrix, 1.0)  # Diagonal = 1.0
        
        quad_particle = QuadStateParticle(
            particle_id=particle.id,
            state_1=state_1,
            state_2=state_2,
            state_3=state_3,
            state_4=state_4,
            coherence_factor=coherence_factor,
            stability_matrix=stability_matrix
        )
        
        self.quad_state_particles[particle.id] = quad_particle
        return quad_particle
    
    def apply_dual_resonance_forces(self, particle, dt: float = 0.01) -> Tuple[np.ndarray, np.ndarray]:
        """Apply simultaneous up and down resonance forces"""
        up_force = np.zeros(3)
        down_force = np.zeros(3)
        
        for channel in self.resonance_channels:
            if channel.active:
                # Calculate resonance force based on frequency and phase
                omega = 2 * np.pi * channel.frequency
                resonance_factor = channel.amplitude * np.sin(omega * self._get_simulation_time() + channel.phase)
                
                # Apply force in channel direction
                channel_force = channel.direction * resonance_factor * particle.mass
                
                if channel.resonance_type == "up":
                    up_force += channel_force
                elif channel.resonance_type == "down":
                    down_force += channel_force
        
        return up_force, down_force
    
    def apply_micro_plank_gravity(self, particle, dt: float = 0.01) -> np.ndarray:
        """Apply micro-planck scale gravitational self-direction"""
        if particle.id not in self.micro_plank_scales:
            self.create_micro_plank_scale(particle.id, particle.velocity)
        
        micro_plank = self.micro_plank_scales[particle.id]
        
        # Calculate gravitational force based on particle's own direction
        gravity_strength = particle.mass * 9.81 * micro_plank.inertia_factor
        gravitational_force = micro_plank.gravitational_direction * gravity_strength
        
        # Apply resonance coupling modulation
        coupling_modulation = 1.0 + micro_plank.resonance_coupling * np.sin(self._get_simulation_time() * 10)
        gravitational_force *= coupling_modulation
        
        return gravitational_force
    
    def apply_dimensional_property_transfer(self, particle, dt: float = 0.01) -> Dict[str, float]:
        """Transfer properties between gravitational and non-gravitational dimensions"""
        if particle.id not in self.dimensional_overlaps:
            self.create_dimensional_overlap(particle.id)
        
        overlap = self.dimensional_overlaps[particle.id]
        
        # Calculate property transfers
        gravitational_properties = {
            'mass': particle.mass,
            'charge': particle.charge,
            'density': particle.density
        }
        
        non_gravitational_properties = {
            'null_mass': particle.mass * overlap.property_transfer_rate,
            'null_charge': particle.charge * (1 - overlap.property_transfer_rate),
            'null_density': particle.density * overlap.null_zone_stability
        }
        
        # Apply property mixing
        particle.mass = (gravitational_properties['mass'] * (1 - overlap.property_transfer_rate) + 
                        non_gravitational_properties['null_mass'] * overlap.property_transfer_rate)
        
        particle.charge = (gravitational_properties['charge'] * overlap.null_zone_stability + 
                         non_gravitational_properties['null_charge'] * (1 - overlap.null_zone_stability))
        
        return {
            'gravitational_strength': overlap.overlap_strength,
            'null_zone_stability': overlap.null_zone_stability,
            'property_transfer_rate': overlap.property_transfer_rate
        }
    
    def maintain_null_zone_stability(self, particle, dt: float = 0.01) -> bool:
        """Maintain null zone state with 4 simultaneous states"""
        if particle.id not in self.quad_state_particles:
            self.create_quad_state_particle(particle)
        
        quad_particle = self.quad_state_particles[particle.id]
        
        # Check coherence
        if quad_particle.coherence_factor < self.coherence_threshold:
            return True
        
        # Calculate null zone stability
        stability_sum = np.sum(quad_particle.stability_matrix)
        null_zone_stability = stability_sum / (4 * 4)  # Normalize by matrix size
        
        # Apply null zone effects
        if null_zone_stability > self.null_zone_threshold:
            # Null zone active - particle experiences all 4 states
            particle.gravitational_strength *= 0.99  # Slight reduction
            particle.velocity *= 0.995  # Slight damping
            
            # Apply quad-state interactions
            for i in range(4):
                for j in range(4):
                    if i != j:
                        interaction_strength = quad_particle.stability_matrix[i, j]
                        # Apply small perturbation based on state interaction
                        perturbation = np.random.normal(0, interaction_strength * 0.001, 3)
                        particle.velocity += perturbation
            
            return True
        
        return True
    
    def update_quad_state_coherence(self, particle, dt: float = 0.01):
        """Update coherence factor for quad-state particles"""
        if particle.id in self.quad_state_particles:
            quad_particle = self.quad_state_particles[particle.id]
            
            # Coherence decay over time
            coherence_decay = 0.001 * dt
            quad_particle.coherence_factor *= (1 - coherence_decay)
            
            # Coherence recovery based on resonance
            up_force, down_force = self.apply_dual_resonance_forces(particle, dt)
            resonance_balance = np.linalg.norm(up_force) / (np.linalg.norm(up_force) + np.linalg.norm(down_force) + 0.001)
            
            # Recover coherence if forces are balanced
            if 0.4 < resonance_balance < 0.6:
                quad_particle.coherence_factor = min(1.0, quad_particle.coherence_factor + 0.01 * dt)
    
    def calculate_quad_state_energy(self, particle) -> float:
        """Calculate total energy from all 4 states"""
        if particle.id not in self.quad_state_particles:
            return 0.0
        
        quad_particle = self.quad_state_particles[particle.id]
        
        # Kinetic energy
        kinetic_energy = 0.5 * particle.mass * np.linalg.norm(particle.velocity)**2
        
        # State interaction energy
        state_energy = 0.0
        for i in range(4):
            for j in range(i+1, 4):
                interaction_energy = quad_particle.stability_matrix[i, j] * quad_particle.coherence_factor
                state_energy += interaction_energy
        
        # Dimensional overlap energy
        if particle.id in self.dimensional_overlaps:
            overlap = self.dimensional_overlaps[particle.id]
            overlap_energy = overlap.overlap_strength * particle.mass * 9.81
            state_energy += overlap_energy
        
        total_energy = kinetic_energy + state_energy
        return total_energy
    
    def get_resonance_status(self) -> Dict:
        """Get comprehensive resonance system status"""
        channel_status = []
        for channel in self.resonance_channels:
            channel_status.append({
                'channel_id': channel.channel_id,
                'type': channel.resonance_type,
                'active': channel.active,
                'frequency': channel.frequency,
                'amplitude': channel.amplitude,
                'phase': channel.phase
            })
        
        quad_state_stats = {
            'total_quad_particles': len(self.quad_state_particles),
            'average_coherence': np.mean([qp.coherence_factor for qp in self.quad_state_particles.values()]) if self.quad_state_particles else 0,
            'high_coherence_particles': sum(1 for qp in self.quad_state_particles.values() if qp.coherence_factor > 0.9)
        }
        
        dimensional_stats = {
            'total_overlaps': len(self.dimensional_overlaps),
            'average_overlap_strength': np.mean([overlap.overlap_strength for overlap in self.dimensional_overlaps.values()]) if self.dimensional_overlaps else 0,
            'average_null_stability': np.mean([overlap.null_zone_stability for overlap in self.dimensional_overlaps.values()]) if self.dimensional_overlaps else 0
        }
        
        return {
            'resonance_channels': channel_status,
            'quad_state_statistics': quad_state_stats,
            'dimensional_statistics': dimensional_stats,
            'total_micro_plank_scales': len(self.micro_plank_scales)
        }
    
    def _get_simulation_time(self) -> float:
        """Get current simulation time (placeholder)"""
        return 0.0  # This would be set by the main simulation loop
    
    def set_simulation_time(self, time: float):
        """Set simulation time for resonance calculations"""
        self.simulation_time = time
    
    def visualize_dual_resonance_system(self, particles: List):
        """Create visualization of dual resonance system"""
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        
        fig = plt.figure(figsize=(16, 12))
        fig.suptitle('Dual Resonance System - Quad State Particles', fontsize=16, fontweight='bold')
        
        # Create subplot grid
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # Main 3D visualization
        ax1 = fig.add_subplot(gs[:, 0:2], projection='3d')
        self._plot_3d_dual_resonance(ax1, particles)
        
        # Resonance channels
        ax2 = fig.add_subplot(gs[0, 2])
        self._plot_resonance_channels(ax2)
        
        # Quad state coherence
        ax3 = fig.add_subplot(gs[1, 2])
        self._plot_quad_state_coherence(ax3)
        
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def _plot_3d_dual_resonance(self, ax, particles: List):
        """Plot 3D dual resonance system"""
        # Plot particles with quad-state visualization
        for particle in particles:
            if particle.id in self.quad_state_particles:
                quad_particle = self.quad_state_particles[particle.id]
                
                # Color based on coherence
                color_intensity = quad_particle.coherence_factor
                color = (color_intensity, 0.5, 1 - color_intensity)
                
                # Plot particle
                ax.scatter(particle.position[0], particle.position[1], particle.position[2],
                          c=[color], s=50, alpha=0.8)
                
                # Plot state indicators as small spheres around particle
                state_offsets = [
                    [0.2, 0, 0],  # State 1
                    [-0.2, 0, 0],  # State 2
                    [0, 0.2, 0],  # State 3
                    [0, -0.2, 0]   # State 4
                ]
                
                for i, offset in enumerate(state_offsets):
                    state_pos = particle.position + np.array(offset)
                    state_color = ['red', 'blue', 'green', 'yellow'][i]
                    ax.scatter(state_pos[0], state_pos[1], state_pos[2],
                              c=state_color, s=10, alpha=0.6)
        
        # Plot resonance field lines
        for channel in self.resonance_channels:
            if channel.active:
                # Create field line
                t = np.linspace(0, 2, 20)
                field_line = np.outer(t, channel.direction) * 3
                
                # Offset based on channel
                offset = np.array([channel.channel_id * 2 - 0.5, 0, 0])
                field_line += offset
                
                ax.plot(field_line[:, 0], field_line[:, 1], field_line[:, 2],
                       color='cyan' if channel.resonance_type == 'up' else 'orange',
                       alpha=0.5, linewidth=2)
        
        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        ax.set_zlabel('Z Position')
        ax.set_title('3D Dual Resonance System')
    
    def _plot_resonance_channels(self, ax):
        """Plot resonance channel status"""
        channel_names = [f"Channel {c.channel_id} ({c.resonance_type})" for c in self.resonance_channels]
        channel_amplitudes = [c.amplitude for c in self.resonance_channels]
        channel_colors = ['cyan' if c.resonance_type == 'up' else 'orange' for c in self.resonance_channels]
        
        bars = ax.bar(channel_names, channel_amplitudes, color=channel_colors, alpha=0.7, edgecolor='black')
        
        ax.set_ylabel('Amplitude')
        ax.set_title('Resonance Channels')
        ax.tick_params(axis='x', rotation=45)
        
        # Add frequency labels
        for i, (bar, channel) in enumerate(zip(bars, self.resonance_channels)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                   f'{channel.frequency:.2e} Hz', ha='center', va='bottom', fontsize=8)
    
    def _plot_quad_state_coherence(self, ax):
        """Plot quad-state particle coherence"""
        if self.quad_state_particles:
            coherence_values = [qp.coherence_factor for qp in self.quad_state_particles.values()]
            particle_ids = list(self.quad_state_particles.keys())
            
            scatter = ax.scatter(particle_ids, coherence_values, 
                               c=coherence_values, cmap='viridis', s=50, alpha=0.7)
            
            ax.axhline(y=self.coherence_threshold, color='red', linestyle='--', 
                      label=f'Threshold ({self.coherence_threshold})')
            
            ax.set_xlabel('Particle ID')
            ax.set_ylabel('Coherence Factor')
            ax.set_title('Quad-State Coherence')
            ax.legend()
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'No quad-state\nparticles yet', ha='center', va='center',
                   transform=ax.transAxes, fontsize=12)
