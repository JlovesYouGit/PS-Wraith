import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle, Polygon
import seaborn as sns
from typing import List, Dict, Tuple
import time

class EnhancedParticleVisualizer:
    def __init__(self, simulation):
        self.simulation = simulation
        self.fig = None
        self.axes = {}
        self.colors = {
            'red_particle': '#FF4444',
            'blue_particle': '#4444FF',
            'processed': '#44FF44',
            'dark_matter': '#FF44FF',
            'void': '#000000',
            'plate': '#888888',
            'crystal': '#00FFFF',
            'electrode': '#FFFF00'
        }
        
    def create_comprehensive_visualization(self):
        """Create comprehensive visualization showing all system processes"""
        self.fig = plt.figure(figsize=(20, 15))
        self.fig.suptitle('Particle Extraction System - Complete Process Visualization', fontsize=16, fontweight='bold')
        
        # Create subplot grid
        gs = self.fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # Main 3D visualization
        self.axes['main_3d'] = self.fig.add_subplot(gs[0:2, 0:2], projection='3d')
        
        # Equation visualization
        self.axes['equations'] = self.fig.add_subplot(gs[0, 2])
        
        # Field strength map
        self.axes['field_map'] = self.fig.add_subplot(gs[0, 3])
        
        # Particle state timeline
        self.axes['timeline'] = self.fig.add_subplot(gs[1, 2:])
        
        # Conversion efficiency
        self.axes['conversion'] = self.fig.add_subplot(gs[2, 0])
        
        # System metrics
        self.axes['metrics'] = self.fig.add_subplot(gs[2, 1])
        
        # Process flow diagram
        self.axes['flow'] = self.fig.add_subplot(gs[2, 2])
        
        # Energy distribution
        self.axes['energy'] = self.fig.add_subplot(gs[2, 3])
        
        self._populate_all_visualizations()
        
        return self.fig
    
    def _populate_all_visualizations(self):
        """Populate all visualization panels"""
        self._plot_main_3d_system()
        self._plot_equations()
        self._plot_field_strength_map()
        self._plot_particle_timeline()
        self._plot_conversion_efficiency()
        self._plot_system_metrics()
        self._plot_process_flow()
        self._plot_energy_distribution()
    
    def _plot_main_3d_system(self):
        """Plot main 3D system visualization"""
        ax = self.axes['main_3d']
        
        # Plot system components
        self._plot_dimensional_plate(ax)
        self._plot_void_zone(ax)
        self._plot_crystal_geometry(ax)
        self._plot_gravitational_fields(ax)
        
        # Plot particle trajectories with color coding by state
        for particle_id, trajectory in self.simulation.particle_trajectories.items():
            if len(trajectory) > 1:
                trajectory_array = np.array(trajectory)
                
                # Find particle state
                particle = None
                for p in self.simulation.extraction_system.particles:
                    if p.id == particle_id:
                        particle = p
                        break
                
                if particle:
                    color = self._get_particle_color(particle)
                    alpha = 0.8 if particle.state.value == 'dense_dark_matter' else 0.6
                    linewidth = 2 if particle.state.value == 'dense_dark_matter' else 1
                    
                    ax.plot(trajectory_array[:, 0], 
                           trajectory_array[:, 1], 
                           trajectory_array[:, 2], 
                           color=color, alpha=alpha, linewidth=linewidth)
        
        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Y Position (m)')
        ax.set_zlabel('Z Position (m)')
        ax.set_title('3D Particle Extraction System')
        ax.legend(['Dimensional Plate', 'Void Zone', 'Crystal', 'Gravitational Fields', 'Particles'])
    
    def _plot_dimensional_plate(self, ax):
        """Plot dimensional plate"""
        if self.simulation.dimensional_plate:
            vertices = self.simulation.dimensional_plate.plate_vertices
            
            # Create plate surface
            if len(vertices) >= 3:
                from mpl_toolkits.mplot3d.art3d import Poly3DCollection
                verts = [vertices]
                plate = Poly3DCollection(verts, alpha=0.3, facecolor='gray', edgecolor='black')
                ax.add_collection3d(plate)
    
    def _plot_void_zone(self, ax):
        """Plot void zone as sphere"""
        if self.simulation.void_zone:
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 20)
            x = self.simulation.void_zone.void_radius * np.outer(np.cos(u), np.sin(v)) + self.simulation.void_zone.void_center[0]
            y = self.simulation.void_zone.void_radius * np.outer(np.sin(u), np.sin(v)) + self.simulation.void_zone.void_center[1]
            z = self.simulation.void_zone.void_radius * np.outer(np.ones(np.size(u)), np.cos(v)) + self.simulation.void_zone.void_center[2]
            ax.plot_surface(x, y, z, alpha=0.2, color='red')
    
    def _plot_crystal_geometry(self, ax):
        """Plot crystal geometry"""
        if self.simulation.crystal_processor:
            vertices = self.simulation.crystal_processor.crystal_vertices
            
            # Plot crystal edges
            edges = [
                [0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0],  # Bottom hexagon
                [6, 7], [7, 8], [8, 9], [9, 10], [10, 11], [11, 6],  # Top hexagon
                [0, 6], [1, 7], [2, 8], [3, 9], [4, 10], [5, 11]  # Vertical edges
            ]
            
            for edge in edges:
                if edge[0] < len(vertices) and edge[1] < len(vertices):
                    points = vertices[edge]
                    ax.plot3D(*points.T, 'c-', linewidth=2, alpha=0.7)
            
            # Plot electrodes
            for electrode in self.simulation.crystal_processor.electrodes:
                ax.scatter(*electrode.position, color='yellow', s=50, marker='o')
    
    def _plot_gravitational_fields(self, ax):
        """Plot gravitational field centers and influence"""
        for field in self.simulation.extraction_system.gravitational_fields:
            # Plot field center
            ax.scatter(*field.field_center, color='blue', s=100, marker='*', alpha=0.8)
            
            # Plot field influence sphere
            if field.is_active:
                u = np.linspace(0, 2 * np.pi, 10)
                v = np.linspace(0, np.pi, 10)
                radius = np.sqrt(field.field_strength) * 0.3
                x = radius * np.outer(np.cos(u), np.sin(v)) + field.field_center[0]
                y = radius * np.outer(np.sin(u), np.sin(v)) + field.field_center[1]
                z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + field.field_center[2]
                ax.plot_surface(x, y, z, alpha=0.1, color='blue')
    
    def _plot_equations(self):
        """Plot key equations being used"""
        ax = self.axes['equations']
        ax.axis('off')
        
        equations = [
            r'$F_{gravity} = m \cdot g \cdot \rho_{factor}$',
            r'$p = m \cdot v$',
            r'$I = 0.4 \cdot m \cdot r^2$',
            r'$f_{resonance} = \frac{E}{h}$',
            r'$\rho_{dark} = 10^{15} \frac{kg}{m^3}$',
            r'$\vec{F}_{total} = \sum_{i} \vec{F}_{field,i}$',
            r'$\vec{v}_{new} = \vec{v}_{old} + \vec{a} \cdot \Delta t$',
            r'$E_{photonic} = h \cdot f$'
        ]
        
        y_pos = 0.9
        for eq in equations:
            ax.text(0.05, y_pos, eq, fontsize=10, transform=ax.transAxes,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            y_pos -= 0.11
        
        ax.set_title('Key Equations in System', fontweight='bold')
    
    def _plot_field_strength_map(self):
        """Plot 2D field strength map"""
        ax = self.axes['field_map']
        
        # Create 2D grid
        x = np.linspace(-5, 5, 50)
        y = np.linspace(-5, 5, 50)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)
        
        # Calculate field strength at each point
        for field in self.simulation.extraction_system.gravitational_fields:
            if field.is_active:
                for i in range(len(x)):
                    for j in range(len(y)):
                        pos = np.array([X[i, j], Y[i, j], 0])
                        field_vec = field.calculate_field_at_point(pos)
                        Z[i, j] += np.linalg.norm(field_vec)
        
        # Create contour plot
        contour = ax.contourf(X, Y, Z, levels=20, cmap='viridis')
        ax.contour(X, Y, Z, levels=10, colors='black', alpha=0.3, linewidths=0.5)
        
        # Add colorbar
        plt.colorbar(contour, ax=ax, label='Field Strength (N)')
        
        # Mark system components
        if self.simulation.dimensional_plate:
            plate_bounds = self.simulation.dimensional_plate.polygon_bounds
            rect = Rectangle((plate_bounds['min'][0], plate_bounds['min'][1]), 
                           plate_bounds['max'][0] - plate_bounds['min'][0],
                           plate_bounds['max'][1] - plate_bounds['min'][1],
                           fill=False, edgecolor='red', linewidth=2)
            ax.add_patch(rect)
        
        if self.simulation.void_zone:
            circle = Circle((self.simulation.void_zone.void_center[0], 
                            self.simulation.void_zone.void_center[1]),
                           self.simulation.void_zone.void_radius,
                           fill=False, edgecolor='darkred', linewidth=2)
            ax.add_patch(circle)
        
        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Y Position (m)')
        ax.set_title('Gravitational Field Strength Map')
    
    def _plot_particle_timeline(self):
        """Plot particle state changes over time"""
        ax = self.axes['timeline']
        
        if not self.simulation.system_status_history:
            ax.text(0.5, 0.5, 'No simulation data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        times = [status['simulation_time'] for status in self.simulation.system_status_history]
        
        # Plot different particle states over time
        states = ['active', 'processed', 'dense_dark_matter']
        colors_state = ['blue', 'green', 'purple']
        
        for state, color in zip(states, colors_state):
            counts = [status['particle_states'].get(state, 0) 
                     for status in self.simulation.system_status_history]
            ax.plot(times, counts, label=state.replace('_', ' ').title(), 
                   color=color, linewidth=2, marker='o', markersize=3)
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Particle Count')
        ax.set_title('Particle State Evolution')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_conversion_efficiency(self):
        """Plot dark matter conversion efficiency"""
        ax = self.axes['conversion']
        
        conversion_stats = self.simulation.dark_matter_converter.get_conversion_statistics()
        
        if conversion_stats['total_conversions'] > 0:
            # Create pie chart
            labels = ['Converted', 'Failed']
            sizes = [conversion_stats['total_conversions'], 
                    max(1, conversion_stats['total_conversions'] / max(conversion_stats['average_conversion_probability'], 0.01) - conversion_stats['total_conversions'])]
            colors = ['gold', 'lightgray']
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                             autopct='%1.1f%%', startangle=90)
            
            # Add efficiency text
            ax.text(0.5, -1.2, f'Avg Efficiency: {conversion_stats["average_conversion_probability"]:.3f}',
                   ha='center', va='center', transform=ax.transAxes, fontsize=10, fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'No Conversions\nYet', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12)
        
        ax.set_title('Dark Matter Conversion')
    
    def _plot_system_metrics(self):
        """Plot key system metrics"""
        ax = self.axes['metrics']
        
        if not self.simulation.system_status_history:
            return
        
        # Calculate metrics
        latest_status = self.simulation.system_status_history[-1]
        
        metrics = [
            ('Total Particles', latest_status['total_particles']),
            ('Red Particles', latest_status['red_particles']),
            ('Active Fields', latest_status['gravitational_fields_active']),
            ('Processed', latest_status['particle_states']['processed']),
            ('Dark Matter', latest_status['particle_states']['dense_dark_matter'])
        ]
        
        # Create bar chart
        labels = [metric[0] for metric in metrics]
        values = [metric[1] for metric in metrics]
        colors = ['skyblue', 'lightcoral', 'lightgreen', 'gold', 'plum']
        
        bars = ax.bar(labels, values, color=colors, alpha=0.7, edgecolor='black')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{value}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Count')
        ax.set_title('System Metrics')
        ax.tick_params(axis='x', rotation=45)
    
    def _plot_process_flow(self):
        """Plot process flow diagram"""
        ax = self.axes['flow']
        ax.axis('off')
        
        # Define process stages
        stages = [
            ('Active\nParticles', (0.1, 0.8), 'lightblue'),
            ('Field\nDestabilization', (0.3, 0.8), 'lightcoral'),
            ('Dimensional\nPlate', (0.5, 0.8), 'lightgray'),
            ('Void\nZone', (0.7, 0.8), 'darkred'),
            ('Weightless\nState', (0.9, 0.8), 'lightyellow'),
            ('Crystal\nProcessing', (0.5, 0.5), 'lightcyan'),
            ('Electrode\nPassage', (0.3, 0.3), 'lightgreen'),
            ('Processed\nState', (0.7, 0.3), 'gold'),
            ('Dark Matter\nConversion', (0.5, 0.1), 'plum')
        ]
        
        # Draw stages and connections
        for i, (name, pos, color) in enumerate(stages):
            # Draw box
            rect = Rectangle(pos, 0.15, 0.08, facecolor=color, 
                           edgecolor='black', linewidth=1)
            ax.add_patch(rect)
            
            # Add text
            ax.text(pos[0] + 0.075, pos[1] + 0.04, name, 
                   ha='center', va='center', fontsize=8, fontweight='bold')
            
            # Draw arrows
            if i < len(stages) - 1:
                next_pos = stages[i+1][1]
                ax.annotate('', xy=(next_pos[0], next_pos[1] + 0.04),
                          xytext=(pos[0] + 0.15, pos[1] + 0.04),
                          arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))
        
        ax.set_title('Particle Processing Flow', fontweight='bold')
    
    def _plot_energy_distribution(self):
        """Plot energy distribution of particles"""
        ax = self.axes['energy']
        
        # Calculate particle energies
        energies = []
        particle_types = []
        
        for particle in self.simulation.extraction_system.particles:
            kinetic_energy = 0.5 * particle.mass * np.linalg.norm(particle.velocity)**2
            energies.append(kinetic_energy)
            particle_types.append(particle.particle_type.value)
        
        if energies:
            # Create histogram
            ax.hist(energies, bins=20, alpha=0.7, color='orange', edgecolor='black')
            ax.set_xlabel('Kinetic Energy (J)')
            ax.set_ylabel('Particle Count')
            ax.set_title('Energy Distribution')
            ax.grid(True, alpha=0.3)
            
            # Add statistics
            mean_energy = np.mean(energies)
            ax.axvline(mean_energy, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_energy:.2e} J')
            ax.legend()
        else:
            ax.text(0.5, 0.5, 'No particles\navailable', ha='center', va='center', 
                   transform=ax.transAxes)
    
    def _get_particle_color(self, particle):
        """Get color based on particle state and type"""
        if particle.state.value == 'dense_dark_matter':
            return self.colors['dark_matter']
        elif particle.state.value == 'processed':
            return self.colors['processed']
        elif particle.particle_type.value == 'red_particle':
            return self.colors['red_particle']
        else:
            return self.colors['blue_particle']
    
    def save_visualization(self, filename='particle_extraction_visualization.png'):
        """Save the complete visualization"""
        if self.fig:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Visualization saved as {filename}")
            return filename
        return None

def run_enhanced_visualization():
    """Run enhanced visualization with the simulation"""
    from simulation_runner import ParticleExtractionSimulation
    
    print("Creating enhanced particle extraction visualization...")
    
    # Run simulation
    sim = ParticleExtractionSimulation(use_gpu=False)
    sim.run_simulation(duration=5.0, print_interval=0.5)
    
    # Create enhanced visualization
    visualizer = EnhancedParticleVisualizer(sim)
    fig = visualizer.create_comprehensive_visualization()
    
    # Save visualization
    filename = visualizer.save_visualization()
    
    # Show the plot
    plt.show()
    
    return filename

if __name__ == "__main__":
    run_enhanced_visualization()
