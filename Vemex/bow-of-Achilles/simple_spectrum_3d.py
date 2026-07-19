#!/usr/bin/env python3
"""
Simple 3D Spectrum Wave Environment Visualizer
Creates ASCII and basic visualizations of RF spectrum from our perspective.
"""

import json
import math


def load_network_data():
    """Load our detected network data."""
    try:
        with open('spectrum_boost_results.json') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def estimate_position(signal_percent, channel):
    """Estimate relative position based on signal strength."""
    # Distance estimation from signal strength
    if signal_percent >= 95:
        distance = 5  # Very close
        direction = "Same room"
    elif signal_percent >= 80:
        distance = 15  # Close
        direction = "Same building"
    elif signal_percent >= 60:
        distance = 40  # Medium
        direction = "Adjacent building"
    else:
        distance = 80  # Far
        direction = "Distant building"

    # Assign rough directions based on channel (for visualization)
    angle = (channel * 30) % 360  # Spread channels around compass

    x = distance * math.cos(math.radians(angle))
    y = distance * math.sin(math.radians(angle))
    z = 0  # Assume same level for simplicity

    return x, y, z, direction


def create_ascii_3d_map():
    """Create ASCII art 3D representation of spectrum environment."""
    networks = load_network_data()

    print("🌊 3D SPECTRUM WAVE ENVIRONMENT (ASCII)")
    print("=" * 60)
    print()

    # Create a 2D grid representing top-down view
    grid_size = 21  # 21x21 grid
    center = grid_size // 2
    grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]

    # Mark our position at center
    grid[center][center] = '★'

    # Position networks on grid
    network_info = []
    symbols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

    for i, network in enumerate(networks):
        if i >= len(symbols):
            break

        x, y, z, direction = estimate_position(network['signal_percent'], network['channel'])

        # Convert to grid coordinates
        grid_x = center + int(x / 8)  # Scale down
        grid_y = center + int(y / 8)

        # Ensure within bounds
        grid_x = max(0, min(grid_size - 1, grid_x))
        grid_y = max(0, min(grid_size - 1, grid_y))

        # Place symbol on grid
        if grid[grid_y][grid_x] == ' ':
            grid[grid_y][grid_x] = symbols[i]

        # Store network info
        network_info.append(
            {
                'symbol': symbols[i],
                'ssid': network['ssid'],
                'signal': network['signal_percent'],
                'frequency': network['frequency_mhz'],
                'band': network['band'],
                'direction': direction,
                'distance': math.sqrt(x * x + y * y),
            }
        )

    # Print the grid with compass directions
    print("    N")
    print("    ↑")
    for y in range(grid_size):
        if y == center:
            print("W ← ", end="")
        else:
            print("    ", end="")

        for x in range(grid_size):
            print(grid[y][x], end=" ")

        if y == center:
            print("→ E")
        else:
            print()

    print("    ↓")
    print("    S")
    print()

    # Print legend
    print("LEGEND:")
    print("★ = Our Position (Spectrum Scanner)")
    for info in network_info:
        band_color = "🔴" if info['frequency'] < 2500 else "🔵"
        print(f"{info['symbol']} = {info['ssid']} {band_color}")
        print(f"    {info['signal']}% signal, {info['band']}, {info['direction']}")
    print()


def create_spectrum_wave_analysis():
    """Create detailed spectrum wave analysis."""
    networks = load_network_data()

    print("📊 SPECTRUM WAVE PROPAGATION ANALYSIS")
    print("=" * 60)
    print()

    print("🌊 ELECTROMAGNETIC WAVE CHARACTERISTICS:")
    print()

    for i, network in enumerate(networks, 1):
        freq_mhz = network['frequency_mhz']
        freq_ghz = freq_mhz / 1000
        signal = network['signal_percent']

        # Calculate wave properties
        c = 3e8  # Speed of light (m/s)
        wavelength = c / (freq_mhz * 1e6)  # Wavelength in meters

        # Estimate distance from signal strength
        x, y, z, direction = estimate_position(signal, network['channel'])
        distance = math.sqrt(x * x + y * y + z * z)

        # Path loss calculation (simplified)
        # FSPL = 20*log10(d) + 20*log10(f) + 32.44
        path_loss = 20 * math.log10(distance) + 20 * math.log10(freq_ghz) + 32.44

        print(f"{i}. {network['ssid']} ({network['vendor']})")
        print(f"   📡 Frequency: {freq_ghz:.1f} GHz ({network['band']})")
        print(f"   🌊 Wavelength: {wavelength:.2f} meters")
        print(f"   📶 Signal Strength: {signal}% (~{-90 + signal * 0.6:.0f} dBm)")
        print(f"   📏 Estimated Distance: {distance:.0f} meters ({direction})")
        print(f"   📉 Path Loss: {path_loss:.1f} dB")
        print(f"   🎯 Wave Propagation: {'Line-of-sight' if signal > 80 else 'Through obstacles'}")
        print()

    # Spectrum utilization analysis
    print("📈 SPECTRUM UTILIZATION:")
    bands_24 = [n for n in networks if n['frequency_mhz'] < 2500]
    bands_5 = [n for n in networks if n['frequency_mhz'] >= 5000]

    print(f"   2.4 GHz Band: {len(bands_24)} networks")
    for net in bands_24:
        print(f"     • Ch{net['channel']}: {net['ssid']} ({net['signal_percent']}%)")

    print(f"   5 GHz Band: {len(bands_5)} networks")
    for net in bands_5:
        print(f"     • Ch{net['channel']}: {net['ssid']} ({net['signal_percent']}%)")
    print()

    # Interference analysis
    print("⚡ INTERFERENCE ANALYSIS:")
    channels_24 = [n['channel'] for n in bands_24]
    channels_5 = [n['channel'] for n in bands_5]

    # Check for overlapping channels in 2.4GHz
    overlapping_24 = []
    for i, ch1 in enumerate(channels_24):
        for _j, ch2 in enumerate(channels_24[i + 1 :], i + 1):
            if abs(ch1 - ch2) < 5:  # Channels overlap if within 5 channels
                overlapping_24.append((ch1, ch2))

    if overlapping_24:
        print(f"   🔴 2.4GHz Interference: {len(overlapping_24)} overlapping channel pairs")
        for ch1, ch2 in overlapping_24:
            print(f"     • Channels {ch1} and {ch2} may interfere")
    else:
        print("   ✅ 2.4GHz: Good channel separation")

    if len(set(channels_5)) == len(channels_5):
        print("   ✅ 5GHz: No channel conflicts detected")
    else:
        print("   🔴 5GHz: Some channel overlap detected")
    print()


def create_wave_propagation_diagram():
    """Create ASCII wave propagation diagram."""
    print("🌊 WAVE PROPAGATION PATTERN (Side View)")
    print("=" * 60)
    print()

    # Create a simple wave diagram
    width = 50
    height = 15

    # Our position at left
    diagram = [[' ' for _ in range(width)] for _ in range(height)]
    center_y = height // 2

    # Mark our position
    diagram[center_y][0] = '★'

    # Create wave pattern
    for x in range(1, width):
        for freq_offset, symbol in [(0, '~'), (2, '-'), (4, '.')]:
            y_offset = int(3 * math.sin(2 * math.pi * (x + freq_offset) / 8))
            y = center_y + y_offset
            if 0 <= y < height and diagram[y][x] == ' ':
                diagram[y][x] = symbol

    # Add network positions
    networks = load_network_data()
    for i, network in enumerate(networks[:3]):  # Show first 3 networks
        x, y, z, direction = estimate_position(network['signal_percent'], network['channel'])
        grid_x = min(width - 1, max(1, int(abs(x) / 3)))
        grid_y = center_y + int(z / 5)
        grid_y = max(0, min(height - 1, grid_y))

        symbol = ['A', 'B', 'C'][i]
        diagram[grid_y][grid_x] = symbol

    # Print diagram
    print("Height")
    print("  ↑")
    for y in range(height):
        print("  ", end="")
        for x in range(width):
            print(diagram[y][x], end="")
        print()
    print("  " + "─" * width + "→ Distance")
    print()

    print("WAVE LEGEND:")
    print("★ = Our Position (RF Source)")
    print("~ = 2.4GHz waves (longer wavelength)")
    print("- = 5GHz waves (shorter wavelength)")
    print(". = Higher frequency harmonics")
    print("A,B,C = Detected access points")
    print()


def main():
    """Main function for simple 3D spectrum visualization."""
    print("🌊 SPECTRUM WAVE ENVIRONMENT VISUALIZER")
    print("From the Perspective of Electromagnetic Waves")
    print("=" * 60)
    print()

    networks = load_network_data()

    if not networks:
        print("❌ No network data found. Please run spectrum_wave_booster.py first.")
        return

    print(f"📡 Analyzing {len(networks)} detected networks...")
    print()

    # Create visualizations
    create_ascii_3d_map()
    create_spectrum_wave_analysis()
    create_wave_propagation_diagram()

    print("✅ 3D Spectrum Wave Analysis Complete!")
    print()
    print("🎯 SUMMARY FROM WAVE PERSPECTIVE:")
    print("   • Electromagnetic waves propagate from our position")
    print("   • Different frequencies have different wavelengths")
    print("   • Signal strength indicates wave attenuation")
    print("   • Multiple bands create complex interference patterns")
    print("   • Wave propagation follows physics-based path loss")


if __name__ == "__main__":
    main()
