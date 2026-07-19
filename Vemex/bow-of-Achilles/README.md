# NETesSpectrumBench

**Professional WiFi Spectrum Analysis and Network Testing Suite**

A comprehensive, cross-platform tool for WiFi spectrum analysis, network testing, and cellular tower mapping with advanced visualization capabilities.

## 🚀 Quick Start

### Simple Installation & Usage

```bash
# Clone the repository
git clone https://github.com/JlovesYouGit/NETesSpectrumBench.git
cd NETesSpectrumBench

# Install dependencies
pip install -r requirements.txt

# Launch the application
python main.py gui
```

### Available Commands

```bash
python main.py gui                    # Launch GUI interface
python main.py wifi-scan             # Scan WiFi networks
python main.py tower-scan --place "City" --output towers.csv
python main.py spectrum-3d           # 3D spectrum visualization
python main.py help                  # Show help
```

## 📦 Installation Options

### 1. Run from Source (Developers)
```bash
git clone https://github.com/JlovesYouGit/NETesSpectrumBench.git
cd NETesSpectrumBench
pip install -r requirements.txt
python main.py
```

### 2. Install as Package
```bash
pip install -e .
netesspectrumbench
```

### 3. Standalone Executable (No Python Required)
```bash
python build_exe.py
dist/NETesSpectrumBench.exe
```

## ✨ Features

- **WiFi Network Analysis**: Comprehensive scanning and analysis of wireless networks
- **Cellular Tower Mapping**: Query and visualize cellular tower locations using OpenStreetMap data
- **3D Spectrum Visualization**: Advanced 3D plotting of spectrum data
- **Cross-Platform Support**: Windows, Linux, and macOS compatibility
- **Professional GUI**: Intuitive graphical interface for all features
- **Command-Line Interface**: Powerful CLI for automation and scripting
- **Export Capabilities**: Save data in CSV, JSON, and HTML formats

## 🛠️ System Requirements

- **Python**: 3.9 or higher
- **Operating System**: Windows 10+, Linux (Ubuntu 18.04+), macOS 10.14+
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Network**: Internet connection for cellular tower data queries

## 📚 Documentation

- [User Guide](USER_GUIDE.md) - Comprehensive usage instructions
- [CLI Usage](CLI_USAGE.md) - Command-line interface documentation
- [Features & Capabilities](spectrum_analysis/FEATURES_CAPABILITIES.md) - Detailed feature overview
- [System Architecture](spectrum_analysis/SYSTEM_ARCHITECTURE.md) - Technical architecture details

## 🔧 Development

### Setting up Development Environment

```bash
# Clone and setup
git clone https://github.com/JlovesYouGit/NETesSpectrumBench.git
cd NETesSpectrumBench

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
ruff check .
ruff format .
```

### Building Executables

```bash
# Build standalone executable
python build_exe.py

# The executable will be created in the dist/ directory
```

## 🔬 Technical Notice: RF Analyzer vs. Theoretical TESA Simulation

This codebase contains two distinct functional layers:

1. **RF Spectrum Analyzer & Network Mapping (Fully Functional)**: Implements actual, real-world WiFi network scanning, RSSI measuring, and cellular tower queries (via the OpenStreetMap Overpass API) alongside real-time 2D/3D visualizations and reports.
2. **TESA & Blockchain Bridge (Theoretical/Simulation)**: Implements a deterministic simulation framework modeling dimensional mapping, resonance frequencies, and "key derivation" concepts. 
   - *Security Note*: The key derivation system (`blockchain_tesa_bridge.py`) does **not** cryptographically recover or break actual private keys for arbitrary Bitcoin addresses (which is mathematically impossible under modern cryptographic standards due to the one-way nature of SHA-256, RIPEMD-160, and ECDSA discrete logarithm constraints). Instead, it runs deterministic hashing cascades using the input address as a seed to model how a theoretical resonance bridge would match parameters.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenStreetMap contributors for cellular tower data
- The Python community for excellent libraries
- Contributors and testers who help improve this tool

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/JlovesYouGit/NETesSpectrumBench/issues)
- **Documentation**: Check the `docs/` directory for detailed guides
- **Community**: Join discussions in GitHub Discussions

---

**NETesSpectrumBench** - Professional WiFi spectrum analysis made simple and powerful! 🚀

