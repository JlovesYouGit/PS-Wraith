#!/usr/bin/env python3
"""
3D Spectrum Wave Environment Visualizer
Creates a 3D visualization showing RF spectrum propagation from our perspective.
"""

import json

import matplotlib.pyplot as plt
import numpy as np


class SpectrumWave3D:
    """3D visualization of spectrum wave propagation environment."""

    def __init__(self):
        self.fig = plt.figure(figsize=(15, 12))
        self.ax = self.fig.add_subplot(111, projection='3d')

        # Our position is at origin (0, 0, 0)
        self.our_position = np.array([0, 0, 0])

        # Load our detected networks
        try:
            with open('spectrum_boost_results.json') as f:
                self.networks = json.load(f)
        except FileNotFoundError:
            self.networks = []

    def estimate_3d_position(self, signal_percent, channel, vendor):
        """
        Estimate 3D position of access point based on signal strength and characteristics.
        Returns (x, y, z) coordinates relative to our position.
        """
        # Estimate distance from signal strength (rough approximation)
        if signal_percent >= 95:
            distance = np.random.uniform(1, 5)  # Very close
        elif signal_percent >= 80:
            distance = np.random.uniform(5, 15)  # Close
        elif signal_percent >= 60:
            distance = np.random.uniform(15, 50)  # Medium
        elif signal_percent >= 40:
            distance = np.random.uniform(50, 100)  # Far
        else:
            distance = np.random.uniform(100, 200)  # Very far

        # Generate random but realistic 3D position
        # Assume most APs are at similar height (residential/office buildings)
        angle_xy = np.random.uniform(0, 2 * np.pi)  # Random horizontal direction
        height_variation = np.random.uniform(-5, 15)  # Height variation (-5m to +15m)

        x = distance * np.cos(angle_xy)
        y = distance * np.sin(angle_xy)
        z = height_variation

        return np.array([x, y, z])

    def create_wave_propagation(self, source_pos, frequency_mhz, signal_strength):
        """Create wave propagation visualization from source position."""
        # Calculate wavelength (c = f * λ)
        c = 3e8  # Speed of light in m/s
        frequency_hz = frequency_mhz * 1e6
        wavelength = c / frequency_hz

        # Create concentric spheres representing wave fronts
        wave_radii = []
        max_radius = 100  # Maximum visualization radius

        # Create multiple wave fronts based on wavelength
        for i in range(1, int(max_radius / wavelength) + 1, 3):  # Every 3rd wave for clarity
            radius = i * wavelength
            if radius <= max_radius:
                wave_radii.append(radius)

        return wave_radii, wavelength

    def draw_wave_sphere(self, center, radius, alpha=0.1, color='blue'):
        """Draw a translucent sphere representing a wave front."""
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 20)

        x = center[0] + radius * np.outer(np.cos(u), np.sin(v))
        y = center[1] + radius * np.outer(np.sin(u), np.sin(v))
        z = center[2] + radius * np.outer(np.ones(np.size(u)), np.cos(v))

        self.ax.plot_surface(x, y, z, alpha=alpha, color=color)

    def get_frequency_color(self, frequency_mhz):
        """Get color based on frequency (spectrum visualization)."""
        if frequency_mhz < 2500:  # 2.4 GHz band
            return 'red', '2.4GHz'
        elif frequency_mhz < 6000:  # 5 GHz band
            return 'blue', '5GHz'
        else:  # 6 GHz and above
            return 'purple', '6GHz+'

    def visualize_spectrum_environment(self):
        """Create the main 3D spectrum visualization."""
        print("🌊 Creating 3D Spectrum Wave Visualization...")

        # Clear the plot
        self.ax.clear()

        # Set up the 3D environment
        self.ax.set_xlabel('Distance East (meters)', fontsize=10)
        self.ax.set_ylabel('Distance North (meters)', fontsize=10)
        self.ax.set_zlabel('Height (meters)', fontsize=10)
        self.ax.set_title(
            '3D RF Spectrum Wave Environment\n(From Our Perspective)',
            fontsize=14,
            fontweight='bold',
        )

        # Mark our position
        self.ax.scatter(
            *self.our_position,
            color='gold',
            s=200,
            marker='*',
            label='Our Position',
            edgecolors='black',
            linewidth=2,
        )

        # Add coordinate system arrows
        arrow_length = 20
        self.ax.quiver(0, 0, 0, arrow_length, 0, 0, color='red', alpha=0.7, arrow_length_ratio=0.1)
        self.ax.quiver(
            0, 0, 0, 0, arrow_length, 0, color='green', alpha=0.7, arrow_length_ratio=0.1
        )
        self.ax.quiver(0, 0, 0, 0, 0, arrow_length, color='blue', alpha=0.7, arrow_length_ratio=0.1)

        # Process each detected network
        network_positions = []
        colors_used = set()

        for _i, network in enumerate(self.networks):
            ssid = network['ssid']
            signal = network['signal_percent']
            frequency = network['frequency_mhz']
            vendor = network['vendor']

            # Estimate 3D position
            pos = self.estimate_3d_position(signal, network['channel'], vendor)
            network_positions.append((pos, network))

            # Get frequency-based color
            color, band = self.get_frequency_color(frequency)
            colors_used.add((color, band))

            # Draw access point
            marker_size = max(50, signal * 2)  # Size based on signal strength
            self.ax.scatter(
                *pos, color=color, s=marker_size, alpha=0.8, edgecolors='black', linewidth=1
            )

            # Add label
            label_text = f"{ssid}\n{signal}%\n{band}"
            self.ax.text(
                pos[0], pos[1], pos[2] + 5, label_text, fontsize=8, ha='center', va='bottom'
            )

            # Draw wave propagation (simplified - just a few key waves)
            wave_radii, wavelength = self.create_wave_propagation(pos, frequency, signal)

            # Draw only a few wave fronts for clarity
            for j, radius in enumerate(wave_radii[:3]):  # Only first 3 waves
                alpha = 0.05 * (signal / 100) * (1 - j * 0.3)  # Fade with distance and signal
                if alpha > 0.01:
                    self.draw_wave_sphere(pos, radius, alpha=alpha, color=color)

        # Add interference visualization between close networks
        self._add_interference_visualization(network_positions)

        # Add ground plane
        self._add_ground_plane()

        # Add legend
        legend_elements = []
        legend_elements.append(
            plt.Line2D(
                [0],
                [0],
                marker='*',
                color='w',
                markerfacecolor='gold',
                markersize=15,
                label='Our Position',
            )
        )

        for color, band in colors_used:
            legend_elements.append(
                plt.Line2D(
                    [0],
                    [0],
                    marker='o',
                    color='w',
                    markerfacecolor=color,
                    markersize=10,
                    label=f'{band} Networks',
                )
            )

        self.ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))

        # Set reasonable axis limits
        max_range = 80
        self.ax.set_xlim([-max_range, max_range])
        self.ax.set_ylim([-max_range, max_range])
        self.ax.set_zlim([-10, 30])

        # Add information text
        info_text = f"""
Networks Detected: {len(self.networks)}
2.4GHz: {len([n for n in self.networks if n['frequency_mhz'] < 2500])}
5GHz: {len([n for n in self.networks if n['frequency_mhz'] >= 5000])}
Range: {min([n['signal_percent'] for n in self.networks])}% - {max([n['signal_percent'] for n in self.networks])}%
        """.strip()

        self.ax.text2D(
            0.02,
            0.98,
            info_text,
            transform=self.ax.transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
        )

        print("✅ 3D Visualization Complete!")

    def _add_interference_visualization(self, network_positions):
        """Add visualization of potential interference between networks."""
        for i, (pos1, net1) in enumerate(network_positions):
            for _j, (pos2, net2) in enumerate(network_positions[i + 1 :], i + 1):
                distance = np.linalg.norm(pos1 - pos2)

                # Check for potential interference (same band, close channels)
                freq_diff = abs(net1['frequency_mhz'] - net2['frequency_mhz'])
                same_band = net1['band'] == net2['band']

                if same_band and freq_diff < 100 and distance < 50:  # Potential interference
                    # Draw interference line
                    self.ax.plot(
                        [pos1[0], pos2[0]],
                        [pos1[1], pos2[1]],
                        [pos1[2], pos2[2]],
                        'orange',
                        alpha=0.3,
                        linewidth=2,
                        linestyle='--',
                    )

    def _add_ground_plane(self):
        """Add a ground plane for reference."""
        x_ground = np.linspace(-80, 80, 10)
        y_ground = np.linspace(-80, 80, 10)
        X_ground, Y_ground = np.meshgrid(x_ground, y_ground)
        Z_ground = np.zeros_like(X_ground) - 2  # Slightly below zero

        self.ax.plot_surface(X_ground, Y_ground, Z_ground, alpha=0.1, color='gray')

    def save_visualization(self, filename='spectrum_3d_environment.png'):
        """Save the 3D visualization to file."""
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"💾 3D visualization saved as: {filename}")

    def show_interactive(self):
        """Show interactive 3D plot."""
        # Save instead of showing for headless environment
        plt.savefig('spectrum_3d_interactive.png', dpi=300, bbox_inches='tight')
        print("💾 Interactive 3D plot saved as: spectrum_3d_interactive.png")


def create_spectrum_wave_diagram():
    """Create a 2D spectrum wave diagram showing frequency bands."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # Load network data
    try:
        with open('spectrum_boost_results.json') as f:
            networks = json.load(f)
    except FileNotFoundError:
        networks = []

    # Top plot: Frequency spectrum
    frequencies = [net['frequency_mhz'] for net in networks]
    signals = [net['signal_percent'] for net in networks]
    colors = ['red' if f < 2500 else 'blue' for f in frequencies]

    ax1.scatter(frequencies, signals, c=colors, s=100, alpha=0.7, edgecolors='black')
    ax1.set_xlabel('Frequency (MHz)')
    ax1.set_ylabel('Signal Strength (%)')
    ax1.set_title('RF Spectrum Analysis - Detected Networks')
    ax1.grid(True, alpha=0.3)

    # Add frequency band labels
    ax1.axvspan(2400, 2500, alpha=0.2, color='red', label='2.4 GHz Band')
    ax1.axvspan(5000, 6000, alpha=0.2, color='blue', label='5 GHz Band')
    ax1.legend()

    # Add network labels
    for net in networks:
        ax1.annotate(
            net['ssid'],
            (net['frequency_mhz'], net['signal_percent']),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=8,
        )

    # Bottom plot: Wave propagation simulation
    x = np.linspace(0, 100, 1000)  # Distance in meters

    for net in networks:
        freq_ghz = net['frequency_mhz'] / 1000
        signal = net['signal_percent']

        # Simple wave equation: A * sin(2π * f * t) * exp(-distance/range)
        wavelength = 300 / freq_ghz  # Approximate wavelength in meters
        amplitude = signal / 100
        decay = np.exp(-x / 50)  # Signal decay with distance

        wave = amplitude * np.sin(2 * np.pi * x / wavelength) * decay

        color = 'red' if net['frequency_mhz'] < 2500 else 'blue'
        ax2.plot(
            x,
            wave,
            color=color,
            alpha=0.7,
            linewidth=2,
            label=f"{net['ssid']} ({freq_ghz:.1f} GHz)",
        )

    ax2.set_xlabel('Distance (meters)')
    ax2.set_ylabel('Wave Amplitude (normalized)')
    ax2.set_title('Spectrum Wave Propagation from Our Position')
    ax2.grid(True, alpha=0.3)
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig('spectrum_wave_analysis.png', dpi=300, bbox_inches='tight')
    print("💾 Spectrum wave analysis saved as: spectrum_wave_analysis.png")

    return fig


def main():
    """Main function to create 3D spectrum visualization."""
    print("🌊 SPECTRUM WAVE 3D ENVIRONMENT VISUALIZER")
    print("=" * 50)

    # Create 3D visualization
    visualizer = SpectrumWave3D()
    visualizer.visualize_spectrum_environment()
    visualizer.save_visualization()

    # Create 2D spectrum analysis
    create_spectrum_wave_diagram()

    print("\n✅ Visualizations created successfully!")
    print("📊 Files generated:")
    print("   • spectrum_3d_environment.png - 3D RF environment")
    print("   • spectrum_wave_analysis.png - 2D spectrum analysis")

    # Show interactive plot
    print("\n🖥️  Displaying interactive 3D visualization...")
    visualizer.show_interactive()


if __name__ == "__main__":
    main()
