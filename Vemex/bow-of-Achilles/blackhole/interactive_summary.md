# Interactive MSFB Sandbox Environment

## Overview
This project provides several interactive visualizations of the MSFB model that allow you to manipulate the components and see how they affect the final result in real-time.

## Files Created

### 1. blender_style_sandbox.py
A comprehensive 3D sandbox environment with multiple views:
- 3D visualization of components as spheres
- Top view and side view projections
- Interactive controls panel
- Sliders for all four components (M, S, F, B)
- Reset button to return to initial values

### 2. simple_interactive.py
A simplified interactive environment:
- Single plot with adjustable parameters
- Sliders for all four components
- Real-time text display of current values
- Reset button functionality

### 3. interactive_msfb.py
A focused interactive visualization:
- Single adjustable parameter (Mass)
- Visual feedback through waveform changes
- Real-time MSFB calculation display

## How to Use the Interactive Environments

### Running the Visualizations
```bash
python n:\blackhole\blender_style_sandbox.py
python n:\blackhole\simple_interactive.py
python n:\blackhole\interactive_msfb.py
```

### Interacting with the Controls
1. **Sliders**: Drag the sliders to adjust the values of M (Mass), S (Space curvature), F (Felt perception), and B (Bending deviation)
2. **Reset Button**: Click to return all values to their initial settings
3. **Real-time Updates**: All visualizations update immediately as you adjust the sliders

## Features of the Sandbox Environment

### Multi-View Visualization
- **3D View**: See components represented as spheres in 3D space
- **Top View**: 2D projection from above
- **Side View**: 2D projection from the side
- **Controls Panel**: Text display of current values and calculations

### Interactive Components
- **Mass (M)**: Adjustable from 1×10⁵ to 1×10⁷
- **Space (S)**: Adjustable from 1×10¹⁴ to 1×10¹⁶
- **Felt (F)**: Adjustable from 1×10⁻⁶ to 1×10⁻⁴
- **Bend (B)**: Adjustable from 1×10⁹ to 1×10¹¹

### Real-time Calculations
- Immediate recalculation of MSFB as parameters change
- Step-by-step breakdown of the calculation process
- Visual representation that scales with parameter values

## MSFB Model Details

### Components:
- **M (Mass factor)**: Represents the gravitational influence (4 × 10⁶)
- **S (Space curvature)**: Represents spacetime warping (10¹⁵ m⁻⁴)
- **F (Felt perception)**: Represents tidal forces (10⁻⁵ m/s²)
- **B (Bending deviation)**: Represents geodesic deviation (10¹⁰ m⁻²)

### Calculation:
MSFB = M × S × F × B
Initial result: MSFB = 4 × 10²⁶

## Visualization Methods

### 3D Sphere Representation
- Each component is represented as a sphere
- Sphere size scales with the log of the component value
- Different colors for each component:
  - Red: Mass (M)
  - Blue: Space curvature (S)
  - Green: Felt perception (F)
  - Orange: Bending deviation (B)

### Connection Visualization
- Dashed lines connect components in the order of calculation
- Central display shows the current MSFB result

### Waveform Visualization
- In simplified versions, component values affect waveform amplitude
- Provides immediate visual feedback on parameter changes

## Educational Value

This sandbox environment allows you to:
1. Understand how each component contributes to the final result
2. Experiment with different values to see their effects
3. Visualize the mathematical relationship between components
4. Gain intuition about the scale of gravitational effects near black holes

## Technical Implementation

The interactive environments use:
- **matplotlib** for visualization
- **matplotlib.widgets** for interactive controls
- **NumPy** for mathematical calculations
- **mpl_toolkits.mplot3d** for 3D visualization

## Troubleshooting

If the interactive windows don't appear:
1. Ensure you're running the scripts in an environment that supports GUI display
2. Check that matplotlib backend supports interactive widgets
3. Try running from a command prompt rather than an IDE terminal

## Extending the Sandbox

The sandbox can be extended to:
1. Add more complex physics calculations
2. Include additional components
3. Implement different visualization methods
4. Add preset scenarios for different black holes
5. Include educational tooltips and explanations