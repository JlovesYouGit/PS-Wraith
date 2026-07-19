import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist

class DensityMeasurementType(Enum):
    VOLUME_DENSITY = "volume_density"
    SURFACE_DENSITY = "surface_density"
    POINT_DENSITY = "point_density"
    EMISSION_RATE = "emission_rate"

@dataclass
class DensityReading:
    timestamp: float
    position: np.ndarray
    density_value: float
    particle_count: int
    volume: float
    measurement_type: DensityMeasurementType
    emission_rate: float = 0.0

@dataclass
class EmissionEvent:
    timestamp: float
    emission_position: np.ndarray
    emission_density: float
    particle_ids: List[int]
    emission_type: str  # "collision", "extraction", "decay"

class DensityEmissionAnalyzer:
    def __init__(self, measurement_volume_size: float = 2.0, grid_resolution: int = 10):
        self.measurement_volume_size = measurement_volume_size
        self.grid_resolution = grid_resolution
        self.density_readings = []
        self.emission_events = []
        self.density_grid = None
        self.emission_history = []
        
        # Initialize measurement grid
        self._initialize_density_grid()
        
    def _initialize_density_grid(self):
        """Initialize 3D density measurement grid"""
        # Create 3D grid for density measurements
        x = np.linspace(-self.measurement_volume_size, self.measurement_volume_size, self.grid_resolution)
        y = np.linspace(-self.measurement_volume_size, self.measurement_volume_size, self.grid_resolution)
        z = np.linspace(-self.measurement_volume_size, self.measurement_volume_size, self.grid_resolution)
        
        self.grid_x, self.grid_y, self.grid_z = np.meshgrid(x, y, z)
        self.grid_points = np.column_stack([self.grid_x.ravel(), self.grid_y.ravel(), self.grid_z.ravel()])
        self.grid_volumes = np.ones(len(self.grid_points)) * (2 * self.measurement_volume_size / self.grid_resolution) ** 3
        
    def measure_local_density(self, particles: List, measurement_position: np.ndarray, 
                            radius: float = 1.0) -> DensityReading:
        """Measure local particle density at a specific position"""
        # Count particles within measurement radius
        particle_count = 0
        total_mass = 0
        total_density = 0
        
        for particle in particles:
            distance = np.linalg.norm(particle.position - measurement_position)
            if distance <= radius:
                particle_count += 1
                total_mass += particle.mass
                total_density += particle.density
        
        # Calculate volume density
        volume = (4/3) * np.pi * radius**3
        volume_density = total_mass / volume if volume > 0 else 0
        
        # Calculate average particle density
        avg_particle_density = total_density / particle_count if particle_count > 0 else 0
        
        # Calculate emission rate (particles leaving the volume)
        emission_rate = self._calculate_emission_rate(particles, measurement_position, radius)
        
        reading = DensityReading(
            timestamp=np.datetime64('now'),
            position=measurement_position,
            density_value=volume_density,
            particle_count=particle_count,
            volume=volume,
            measurement_type=DensityMeasurementType.VOLUME_DENSITY,
            emission_rate=emission_rate
        )
        
        self.density_readings.append(reading)
        return reading
    
    def _calculate_emission_rate(self, particles: List, center: np.ndarray, radius: float) -> float:
        """Calculate emission rate of particles leaving the measurement volume"""
        emission_count = 0
        
        for particle in particles:
            distance = np.linalg.norm(particle.position - center)
            
            # Check if particle is moving outward (leaving the volume)
            if distance < radius * 1.1:  # Near boundary
                velocity_radial = np.dot(particle.velocity, (particle.position - center)) / distance
                
                if velocity_radial > 0:  # Moving outward
                    emission_count += 1
        
        # Emission rate as particles per second (normalized)
        emission_rate = emission_count * 10.0  # Scale factor for visualization
        
        return emission_rate
    
    def measure_grid_density(self, particles: List) -> np.ndarray:
        """Measure density across the entire grid"""
        density_values = np.zeros(len(self.grid_points))
        
        for i, grid_point in enumerate(self.grid_points):
            # Find particles near this grid point
            nearby_particles = []
            
            for particle in particles:
                distance = np.linalg.norm(particle.position - grid_point)
                if distance < self.measurement_volume_size / self.grid_resolution:
                    nearby_particles.append(particle)
            
            if nearby_particles:
                # Calculate density at this grid point
                total_mass = sum(p.mass for p in nearby_particles)
                density_values[i] = total_mass / self.grid_volumes[i]
        
        self.density_grid = density_values.reshape(self.grid_resolution, self.grid_resolution, self.grid_resolution)
        return self.density_grid
    
    def detect_density_emissions(self, particles: List, previous_particles: List = None) -> List[EmissionEvent]:
        """Detect density-based emission events"""
        emission_events = []
        
        if previous_particles is None:
            previous_particles = []
        
        # Find particles that have been emitted (new particles)
        current_ids = {p.id for p in particles}
        previous_ids = {p.id for p in previous_particles}
        
        emitted_particle_ids = current_ids - previous_ids
        
        if emitted_particle_ids:
            emitted_particles = [p for p in particles if p.id in emitted_particle_ids]
            
            # Group emitted particles by location
            emission_clusters = self._cluster_emitted_particles(emitted_particles)
            
            for cluster in emission_clusters:
                # Calculate emission density
                total_mass = sum(p.mass for p in cluster)
                cluster_center = np.mean([p.position for p in cluster], axis=0)
                cluster_radius = np.max([np.linalg.norm(p.position - cluster_center) for p in cluster])
                cluster_volume = (4/3) * np.pi * cluster_radius**3 if cluster_radius > 0 else 1.0
                
                emission_density = total_mass / cluster_volume
                
                emission_event = EmissionEvent(
                    timestamp=np.datetime64('now'),
                    emission_position=cluster_center,
                    emission_density=emission_density,
                    particle_ids=[p.id for p in cluster],
                    emission_type="density_emission"
                )
                
                emission_events.append(emission_event)
                self.emission_events.append(emission_event)
        
        return emission_events
    
    def _cluster_emitted_particles(self, particles: List, clustering_radius: float = 1.0) -> List[List]:
        """Cluster emitted particles by proximity"""
        if not particles:
            return []
        
        clusters = []
        unclustered = particles.copy()
        
        while unclustered:
            # Start new cluster with first unclustered particle
            cluster = [unclustered.pop(0)]
            
            # Find all particles within clustering radius
            i = 0
            while i < len(cluster):
                particle = cluster[i]
                
                remaining = []
                for other in unclustered:
                    distance = np.linalg.norm(particle.position - other.position)
                    if distance <= clustering_radius:
                        cluster.append(other)
                    else:
                        remaining.append(other)
                
                unclustered = remaining
                i += 1
            
            clusters.append(cluster)
        
        return clusters
    
    def measure_collision_zone_density(self, collision_zones: List, particles: List) -> Dict[int, DensityReading]:
        """Measure density within each collision zone"""
        zone_density_readings = {}
        
        for zone in collision_zones:
            reading = self.measure_local_density(particles, zone.center, zone.radius)
            reading.measurement_type = DensityMeasurementType.POINT_DENSITY
            zone_density_readings[zone.id] = reading
        
        return zone_density_readings
    
    def calculate_density_gradient(self, particles: List) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate density gradient field"""
        if self.density_grid is None:
            self.measure_grid_density(particles)
        
        # Calculate gradients using numpy
        grad_x, grad_y, grad_z = np.gradient(self.density_grid)
        
        return grad_x, grad_y, grad_z
    
    def get_density_statistics(self) -> Dict:
        """Get comprehensive density statistics"""
        if not self.density_readings:
            return {}
        
        density_values = [reading.density_value for reading in self.density_readings]
        particle_counts = [reading.particle_count for reading in self.density_readings]
        emission_rates = [reading.emission_rate for reading in self.density_readings]
        
        return {
            'total_measurements': len(self.density_readings),
            'average_density': np.mean(density_values),
            'max_density': np.max(density_values),
            'min_density': np.min(density_values),
            'average_particle_count': np.mean(particle_counts),
            'max_particle_count': np.max(particle_counts),
            'total_emissions': len(self.emission_events),
            'average_emission_rate': np.mean(emission_rates),
            'peak_emission_rate': np.max(emission_rates)
        }
    
    def visualize_density_field(self, particles: List, save_path: str = None):
        """Create comprehensive density visualization"""
        fig = plt.figure(figsize=(16, 12))
        fig.suptitle('Particle Density and Emission Analysis', fontsize=16, fontweight='bold')
        
        # Create subplot grid
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # 3D density field
        ax1 = fig.add_subplot(gs[0, 0], projection='3d')
        self._plot_3d_density_field(ax1, particles)
        
        # Density heatmap (XY plane)
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_density_heatmap(ax2, particles, plane='xy')
        
        # Density heatmap (XZ plane)
        ax3 = fig.add_subplot(gs[0, 2])
        self._plot_density_heatmap(ax3, particles, plane='xz')
        
        # Emission rate over time
        ax4 = fig.add_subplot(gs[1, 0])
        self._plot_emission_timeline(ax4)
        
        # Density distribution histogram
        ax5 = fig.add_subplot(gs[1, 1])
        self._plot_density_distribution(ax5)
        
        # Particle count vs density
        ax6 = fig.add_subplot(gs[1, 2])
        self._plot_count_vs_density(ax6)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Density visualization saved as {save_path}")
        
        plt.show()
        return fig
    
    def _plot_3d_density_field(self, ax, particles: List):
        """Plot 3D density field"""
        # Measure grid density
        density_grid = self.measure_grid_density(particles)
        
        # Plot density as scatter plot with color mapping
        threshold = np.max(density_grid) * 0.1  # Only show significant densities
        
        for i in range(self.grid_resolution):
            for j in range(self.grid_resolution):
                for k in range(self.grid_resolution):
                    if density_grid[i, j, k] > threshold:
                        point = self.grid_points[i * self.grid_resolution**2 + j * self.grid_resolution + k]
                        ax.scatter(point[0], point[1], point[2], 
                                  c=density_grid[i, j, k], cmap='hot', 
                                  s=50, alpha=0.6)
        
        # Plot particles
        for particle in particles:
            color = 'red' if hasattr(particle, 'particle_type') and particle.particle_type.value == 'red_particle' else 'blue'
            ax.scatter(particle.position[0], particle.position[1], particle.position[2], 
                      c=color, s=20, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('3D Density Field')
    
    def _plot_density_heatmap(self, ax, particles: List, plane: str = 'xy'):
        """Plot 2D density heatmap"""
        # Create 2D grid for specific plane
        grid_2d = np.zeros((self.grid_resolution, self.grid_resolution))
        
        for i in range(self.grid_resolution):
            for j in range(self.grid_resolution):
                # Map 2D coordinates to 3D grid
                if plane == 'xy':
                    k = self.grid_resolution // 2  # Middle Z plane
                    density_value = self.density_grid[i, j, k] if self.density_grid is not None else 0
                elif plane == 'xz':
                    k = self.grid_resolution // 2  # Middle Y plane
                    density_value = self.density_grid[i, k, j] if self.density_grid is not None else 0
                else:
                    density_value = 0
                
                grid_2d[i, j] = density_value
        
        # Create heatmap
        im = ax.imshow(grid_2d, cmap='hot', origin='lower', 
                      extent=[-self.measurement_volume_size, self.measurement_volume_size,
                             -self.measurement_volume_size, self.measurement_volume_size])
        
        # Add colorbar
        plt.colorbar(im, ax=ax, label='Density (kg/m³)')
        
        # Plot particle projections
        for particle in particles:
            if plane == 'xy':
                ax.plot(particle.position[0], particle.position[1], 'wo', markersize=3)
            elif plane == 'xz':
                ax.plot(particle.position[0], particle.position[2], 'wo', markersize=3)
        
        ax.set_xlabel(f'{plane[0].upper()} Position')
        ax.set_ylabel(f'{plane[1].upper()} Position')
        ax.set_title(f'Density Heatmap ({plane.upper()} Plane)')
    
    def _plot_emission_timeline(self, ax):
        """Plot emission rate over time"""
        if not self.density_readings:
            ax.text(0.5, 0.5, 'No emission data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        times = list(range(len(self.density_readings)))
        emission_rates = [reading.emission_rate for reading in self.density_readings]
        
        ax.plot(times, emission_rates, 'r-', linewidth=2, marker='o', markersize=3)
        ax.fill_between(times, emission_rates, alpha=0.3, color='red')
        
        ax.set_xlabel('Measurement Index')
        ax.set_ylabel('Emission Rate')
        ax.set_title('Density Emission Rate Over Time')
        ax.grid(True, alpha=0.3)
    
    def _plot_density_distribution(self, ax):
        """Plot density value distribution"""
        if not self.density_readings:
            ax.text(0.5, 0.5, 'No density data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        density_values = [reading.density_value for reading in self.density_readings]
        
        ax.hist(density_values, bins=20, alpha=0.7, color='blue', edgecolor='black')
        ax.set_xlabel('Density Value (kg/m³)')
        ax.set_ylabel('Frequency')
        ax.set_title('Density Distribution')
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        mean_density = np.mean(density_values)
        ax.axvline(mean_density, color='red', linestyle='--', linewidth=2, 
                  label=f'Mean: {mean_density:.2e}')
        ax.legend()
    
    def _plot_count_vs_density(self, ax):
        """Plot particle count vs density relationship"""
        if not self.density_readings:
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        density_values = [reading.density_value for reading in self.density_readings]
        particle_counts = [reading.particle_count for reading in self.density_readings]
        
        scatter = ax.scatter(density_values, particle_counts, alpha=0.6, 
                           c=range(len(density_values)), cmap='viridis')
        
        ax.set_xlabel('Density (kg/m³)')
        ax.set_ylabel('Particle Count')
        ax.set_title('Particle Count vs Density')
        ax.grid(True, alpha=0.3)
        
        # Add trend line
        if len(density_values) > 1:
            z = np.polyfit(density_values, particle_counts, 1)
            p = np.poly1d(z)
            ax.plot(density_values, p(density_values), "r--", alpha=0.8, linewidth=2)
    
    def export_density_data(self, filename: str = "density_data.csv"):
        """Export density measurements to CSV"""
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'position_x', 'position_y', 'position_z', 
                         'density_value', 'particle_count', 'volume', 'emission_rate']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for reading in self.density_readings:
                writer.writerow({
                    'timestamp': str(reading.timestamp),
                    'position_x': reading.position[0],
                    'position_y': reading.position[1],
                    'position_z': reading.position[2],
                    'density_value': reading.density_value,
                    'particle_count': reading.particle_count,
                    'volume': reading.volume,
                    'emission_rate': reading.emission_rate
                })
        
        print(f"Density data exported to {filename}")

# Integration function for collision system
def integrate_density_analyzer(collision_system):
    """Integrate density analyzer into collision system"""
    analyzer = DensityEmissionAnalyzer(measurement_volume_size=5.0, grid_resolution=15)
    
    # Add analyzer to collision system
    collision_system.density_analyzer = analyzer
    
    return analyzer
