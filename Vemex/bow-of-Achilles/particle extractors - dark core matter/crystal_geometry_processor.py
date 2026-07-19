import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum
from particle_extraction_system import Particle, ParticleState

class ElectrodeState(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CHARGING = "charging"
    DISCHARGING = "discharging"

@dataclass
class Electrode:
    id: int
    position: np.ndarray
    orientation: np.ndarray
    charge: float
    max_charge: float
    state: ElectrodeState
    influence_radius: float
    passage_efficiency: float

@dataclass
class CrystalFace:
    vertices: List[np.ndarray]
    normal: np.ndarray
    face_type: str  # "entry", "processing", "exit"
    electrode_ids: List[int]

class CrystalGeometryProcessor:
    def __init__(self, crystal_vertices: np.ndarray, electrode_configs: List[Dict], use_gpu: bool = True):
        self.crystal_vertices = crystal_vertices
        self.use_gpu = use_gpu
        self.electrodes = self._initialize_electrodes(electrode_configs)
        self.crystal_faces = self._create_crystal_faces()
        self.processing_zone_bounds = self._calculate_processing_bounds()
        
        # GPU arrays for computation
        if self.use_gpu:
            self._initialize_gpu_arrays()
        
        # Processing parameters
        self.electrode_activation_sequence = []
        self.particle_processing_history = {}
        self.crystal_resonance_frequency = 2.45e9  # GHz frequency for photonic processing
        
    def _initialize_electrodes(self, electrode_configs: List[Dict]) -> List[Electrode]:
        """Initialize electrodes from configuration"""
        electrodes = []
        
        for i, config in enumerate(electrode_configs):
            electrode = Electrode(
                id=i,
                position=np.array(config['position']),
                orientation=np.array(config['orientation']),
                charge=0.0,
                max_charge=config.get('max_charge', 100.0),
                state=ElectrodeState.INACTIVE,
                influence_radius=config.get('influence_radius', 0.5),
                passage_efficiency=config.get('passage_efficiency', 0.8)
            )
            electrodes.append(electrode)
        
        return electrodes
    
    def _create_crystal_faces(self) -> List[CrystalFace]:
        """Create crystal faces from vertices"""
        faces = []
        
        # Define crystal geometry (hexagonal prism)
        # Bottom face
        bottom_vertices = [
            self.crystal_vertices[0], self.crystal_vertices[1], self.crystal_vertices[2],
            self.crystal_vertices[3], self.crystal_vertices[4], self.crystal_vertices[5]
        ]
        bottom_normal = np.array([0, 0, -1])
        faces.append(CrystalFace(bottom_vertices, bottom_normal, "entry", [0, 1]))
        
        # Top face
        top_vertices = [
            self.crystal_vertices[6], self.crystal_vertices[7], self.crystal_vertices[8],
            self.crystal_vertices[9], self.crystal_vertices[10], self.crystal_vertices[11]
        ]
        top_normal = np.array([0, 0, 1])
        faces.append(CrystalFace(top_vertices, top_normal, "exit", [4, 5]))
        
        # Side faces (rectangular)
        for i in range(6):
            v1 = self.crystal_vertices[i]
            v2 = self.crystal_vertices[(i + 1) % 6]
            v3 = self.crystal_vertices[(i + 1) % 6 + 6]
            v4 = self.crystal_vertices[i + 6]
            
            side_vertices = [v1, v2, v3, v4]
            
            # Calculate normal for side face
            edge1 = v2 - v1
            edge2 = v4 - v1
            normal = np.cross(edge1, edge2)
            normal = normal / np.linalg.norm(normal)
            
            faces.append(CrystalFace(side_vertices, normal, "processing", [i + 2]))
        
        return faces
    
    def _calculate_processing_bounds(self) -> Dict[str, np.ndarray]:
        """Calculate processing zone boundaries"""
        return {
            'min': np.min(self.crystal_vertices, axis=0),
            'max': np.max(self.crystal_vertices, axis=0)
        }
    
    def _initialize_gpu_arrays(self):
        """Initialize GPU arrays for computation"""
        import cupy as cp
        
        self.gpu_vertices = cp.asarray(self.crystal_vertices)
        self.gpu_electrode_positions = cp.asarray([e.position for e in self.electrodes])
        self.gpu_electrode_charges = cp.asarray([e.charge for e in self.electrodes])
        self.gpu_influence_radii = cp.asarray([e.influence_radius for e in self.electrodes])
    
    def is_particle_in_processing_zone(self, particle: Particle) -> bool:
        """Check if particle is within crystal processing zone"""
        pos = particle.position
        bounds = self.processing_zone_bounds
        
        return (bounds['min'][0] <= pos[0] <= bounds['max'][0] and
                bounds['min'][1] <= pos[1] <= bounds['max'][1] and
                bounds['min'][2] <= pos[2] <= bounds['max'][2])
    
    def find_crystal_face_intersection(self, particle: Particle, direction: np.ndarray) -> Optional[CrystalFace]:
        """Find which crystal face the particle will intersect"""
        min_distance = float('inf')
        closest_face = None
        
        for face in self.crystal_faces:
            # Ray-plane intersection
            denom = np.dot(face.normal, direction)
            if abs(denom) > 1e-6:
                t = np.dot(face.vertices[0] - particle.position, face.normal) / denom
                
                if t > 0 and t < min_distance:
                    # Check if intersection point is within face bounds
                    intersection_point = particle.position + t * direction
                    
                    if self._is_point_in_face(intersection_point, face):
                        min_distance = t
                        closest_face = face
        
        return closest_face
    
    def _is_point_in_face(self, point: np.ndarray, face: CrystalFace) -> bool:
        """Check if point is within face boundaries"""
        # Use cross product method for convex polygons
        for i in range(len(face.vertices)):
            v1 = face.vertices[i]
            v2 = face.vertices[(i + 1) % len(face.vertices)]
            
            edge = v2 - v1
            to_point = point - v1
            
            cross = np.cross(face.normal, edge)
            if np.dot(to_point, cross) < 0:
                return True
        
        return True
    
    def activate_electrode_sequence(self, particle: Particle, entry_face: CrystalFace):
        """Activate electrode sequence based on entry face"""
        # Determine electrode activation sequence
        if entry_face.face_type == "entry":
            # Activate entry electrodes first
            for electrode_id in entry_face.electrode_ids:
                if electrode_id < len(self.electrodes):
                    self.electrodes[electrode_id].state = ElectrodeState.CHARGING
                    self.electrodes[electrode_id].charge = self.electrodes[electrode_id].max_charge
            
            # Schedule processing electrodes
            self.electrode_activation_sequence = [e.id for e in self.electrodes 
                                                if 2 <= e.id <= 7]  # Processing electrodes
    
    def apply_electrode_passage(self, particle: Particle) -> bool:
        """Apply electrode passage effects to particle"""
        passage_successful = True
        
        for electrode in self.electrodes:
            distance = np.linalg.norm(particle.position - electrode.position)
            
            if distance <= electrode.influence_radius:
                # Calculate electrode influence
                influence_strength = (1 - distance / electrode.influence_radius) * electrode.passage_efficiency
                
                if electrode.state == ElectrodeState.ACTIVE or electrode.state == ElectrodeState.CHARGING:
                    # Apply electromagnetic force
                    em_force = electrode.orientation * electrode.charge * influence_strength * 0.1
                    particle.velocity += em_force / particle.mass
                    
                    # Modify particle charge
                    particle.charge += electrode.charge * influence_strength * 0.01
                    
                    passage_successful = True
                
                # Discharge electrode after interaction
                if electrode.state == ElectrodeState.CHARGING:
                    electrode.state = ElectrodeState.DISCHARGING
                    electrode.charge *= 0.9
        
        return passage_successful
    
    def process_crystal_resonance(self, particle: Particle) -> bool:
        """Process particle through crystal resonance field"""
        if not self.is_particle_in_processing_zone(particle):
            return True
        
        # Calculate resonance effect based on particle properties
        resonance_factor = particle.density * particle.mass
        
        # Apply resonance frequency modulation
        if resonance_factor > 0.5:
            # High-density particles get stronger processing
            velocity_modulation = np.sin(self.crystal_resonance_frequency * 0.0001) * 0.1
            particle.velocity *= (1 + velocity_modulation)
            
            # Modify trajectory for optimal processing
            particle.trajectory_vector *= 1.05
            
            return True
        
        return True
    
    def guide_particle_to_exit(self, particle: Particle) -> bool:
        """Guide particle toward exit face"""
        # Find exit face
        exit_face = None
        for face in self.crystal_faces:
            if face.face_type == "exit":
                exit_face = face
                break
        
        if not exit_face:
            return True
        
        # Calculate direction to exit face center
        exit_center = np.mean(exit_face.vertices, axis=0)
        direction_to_exit = exit_center - particle.position
        direction_to_exit = direction_to_exit / np.linalg.norm(direction_to_exit)
        
        # Apply guiding force
        guiding_force = direction_to_exit * particle.mass * 2.0
        particle.velocity += guiding_force / particle.mass
        
        # Activate exit electrodes
        for electrode_id in exit_face.electrode_ids:
            if electrode_id < len(self.electrodes):
                self.electrodes[electrode_id].state = ElectrodeState.ACTIVE
                self.electrodes[electrode_id].charge = self.electrodes[electrode_id].max_charge
        
        return True
    
    def complete_particle_processing(self, particle: Particle) -> bool:
        """Complete particle processing and mark as processed"""
        # Check if particle has successfully passed through crystal
        for face in self.crystal_faces:
            if face.face_type == "exit":
                if np.dot(particle.velocity, face.normal) > 0:  # Moving toward exit
                    distance_to_exit = np.dot(particle.position - face.vertices[0], face.normal)
                    
                    if distance_to_exit > 0.1:  # Has exited the crystal
                        particle.state = ParticleState.PROCESSED
                        
                        # Record processing history
                        self.particle_processing_history[particle.id] = {
                            'entry_time': np.datetime64('now'),
                            'processing_duration': np.linalg.norm(particle.velocity),
                            'final_charge': particle.charge,
                            'electrodes_used': [e.id for e in self.electrodes if e.state != ElectrodeState.INACTIVE]
                        }
                        
                        # Reset electrodes
                        for electrode in self.electrodes:
                            electrode.state = ElectrodeState.INACTIVE
                            electrode.charge = 0.0
                        
                        return True
        
        return True
    
    def update_processing_system(self, dt: float = 0.01):
        """Update the entire crystal processing system"""
        # Update electrode states
        for electrode in self.electrodes:
            if electrode.state == ElectrodeState.DISCHARGING:
                electrode.charge *= 0.95
                if electrode.charge < 0.1:
                    electrode.state = ElectrodeState.INACTIVE
                    electrode.charge = 0.0
        
        # Process electrode activation sequence
        if self.electrode_activation_sequence:
            next_electrode_id = self.electrode_activation_sequence.pop(0)
            if next_electrode_id < len(self.electrodes):
                self.electrodes[next_electrode_id].state = ElectrodeState.CHARGING
                self.electrodes[next_electrode_id].charge = self.electrodes[next_electrode_id].max_charge
    
    def get_processing_status(self) -> Dict:
        """Get current processing system status"""
        return {
            'total_electrodes': len(self.electrodes),
            'active_electrodes': sum(1 for e in self.electrodes if e.state == ElectrodeState.ACTIVE),
            'charging_electrodes': sum(1 for e in self.electrodes if e.state == ElectrodeState.CHARGING),
            'processed_particles': len(self.particle_processing_history),
            'crystal_resonance_active': True,
            'processing_zone_bounds': self.processing_zone_bounds
        }
