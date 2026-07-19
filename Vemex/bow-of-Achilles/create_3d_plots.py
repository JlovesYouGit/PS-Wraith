#!/usr/bin/env python3
"""Create 3D matplotlib visualizations of spectrum environment."""

import matplotlib

matplotlib.use('Agg')  # Use non-interactive backend
import json

import matplotlib.pyplot as plt
import numpy as np


def create_3d_visualization():
    """Create 3D matplotlib visualization."""
    print('Starting 3D visualization creation...')

    # Load network data
    try:
        with open('spectrum_boost_results.json') as f:
            networks = json.load(f)
        print(f'Loaded {len(networks)} networks')
    except FileNotFoundError:
        print('No network data found')
        networks = []

    print('Creating 3D matplotlib visualization...')

    # Create 3D plot
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Our position at origin
    ax.scatter(
        0,
        0,
        0,
        color='gold',
        s=300,
        marker='*',
        label='Our Position',
        edgecolors='black',
        linewidth=2,
    )

    # Plot networks
    for _i, net in enumerate(networks):
        # Estimate position based on signal strength
        signal = net['signal_percent']
        if signal >= 95:
            distance = np.random.uniform(1, 5)
        elif signal >= 80:
            distance = np.random.uniform(5, 15)
        else:
            distance = np.random.uniform(40, 80)

        # Random direction
        angle = (net['channel'] * 60) % 360
        x = distance * np.cos(np.radians(angle))
        y = distance * np.sin(np.radians(angle))
        z = np.random.uniform(-2, 10)

        # Color by frequency band
        color = 'red' if net['frequency_mhz'] < 2500 else 'blue'
        size = max(50, signal * 2)

        ax.scatter(x, y, z, color=color, s=size, alpha=0.7, edgecolors='black')
        ax.text(x, y, z + 3, f"{net['ssid']}\n{signal}%", fontsize=8, ha='center')

    # Set labels and title
    ax.set_xlabel('Distance East (m)')
    ax.set_ylabel('Distance North (m)')
    ax.set_zlabel('Height (m)')
    ax.set_title('3D RF Spectrum Environment\nFrom Our Perspective', fontsize=14, fontweight='bold')

    # Set limits
    ax.set_xlim([-50, 50])
    ax.set_ylim([-50, 50])
    ax.set_zlim([-5, 15])

    # Add legend
    legend_elements = [
        plt.Line2D(
            [0],
            [0],
            marker='*',
            color='w',
            markerfacecolor='gold',
            markersize=15,
            label='Our Position',
        ),
        plt.Line2D(
            [0],
            [0],
            marker='o',
            color='w',
            markerfacecolor='red',
            markersize=10,
            label='2.4GHz Networks',
        ),
        plt.Line2D(
            [0],
            [0],
            marker='o',
            color='w',
            markerfacecolor='blue',
            markersize=10,
            label='5GHz Networks',
        ),
    ]
    ax.legend(handles=legend_elements, loc='upper left')

    # Save the plot
    plt.tight_layout()
    plt.savefig('spectrum_3d_environment.png', dpi=300, bbox_inches='tight')
    print('✅ 3D visualization saved as: spectrum_3d_environment.png')

    # Create frequency spectrum plot
    fig2, ax2 = plt.subplots(figsize=(12, 6))

    frequencies = [net['frequency_mhz'] for net in networks]
    signals = [net['signal_percent'] for net in networks]
    colors = ['red' if f < 2500 else 'blue' for f in frequencies]

    ax2.scatter(frequencies, signals, c=colors, s=100, alpha=0.7, edgecolors='black')
    ax2.set_xlabel('Frequency (MHz)')
    ax2.set_ylabel('Signal Strength (%)')
    ax2.set_title('RF Spectrum Analysis - Detected Networks')
    ax2.grid(True, alpha=0.3)

    # Add frequency band shading
    ax2.axvspan(2400, 2500, alpha=0.2, color='red', label='2.4 GHz Band')
    ax2.axvspan(5000, 6000, alpha=0.2, color='blue', label='5 GHz Band')
    ax2.legend()

    # Add network labels
    for net in networks:
        ax2.annotate(
            net['ssid'],
            (net['frequency_mhz'], net['signal_percent']),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=8,
        )

    plt.tight_layout()
    plt.savefig('spectrum_frequency_analysis.png', dpi=300, bbox_inches='tight')
    print('✅ Frequency analysis saved as: spectrum_frequency_analysis.png')

    plt.close('all')
    print('📊 Matplotlib visualizations complete!')


if __name__ == "__main__":
    create_3d_visualization()
