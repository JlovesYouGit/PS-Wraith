# Package Resolver - Fix Repository Issues

A universal cross-language dependency resolver that automatically detects and fixes package-related issues in multi-language repositories.

## Wraith Flash Mode & Device Integration

This tool now includes **Wraith Flash Mode** for direct operation in the `wraithps4-serv-backup-performance booster` directory, with full integration of **IOsrom** NAND/image handling code for device updates.

### Flash Mode Features

- **Direct Wraith Directory Operation**: Automatically detects and operates within the wraith system directory
- **Device Image Bridge**: Integrates IOsrom NAND flash, image extraction, and filesystem writing
- **Library Mirror Manager**: Syncs device library, manages package updates via RJ45/USB connection
- **Makefile Transfer**: Generates `wraith_transfer.mk` for automated device transfer operations
- **Cross-Language Package Resolution**: Same GF X H G F algorithm, now with device update capability

### Wraith Directory Structure

```
wraithps4-serv-backup-performance booster/
├── main.py                    # Wraith system entry
├── boost_engine.py            # Gramshas performance engine
├── hardware_interface.py      # 24-electrode RJ45 protocol
├── pragma_logic.py            # Cascade ordering & storage keys
├── storage_manager.py         # 34-layer engraving backups
├── buffer_manager.py          # Internal memory & hash bridges
├── network_protection.py      # 6IPv-to-24-Duplex encryption
├── interleave_manager.py      # Copy-re-add interleaving
├── market_engine.py           # PS Market token chain
└── persistence_manager.py     # Core layer 3 & 9 protection
```

### IOsrom Integration

The tool includes the [IOsrom](https://github.com/JlovesYouGit/IOsrom) repository for NAND and image handling:

- `direct_nand_flasher.py` - Direct NAND write bypassing all tools
- `WRITE_NAND_DIRECT.py` - Write filesystem directly via iBoot commands
- `FINAL_NAND_FLASH.py` - Complete NAND flash sequence
- `proper_nand_writer.py` - libimobiledevice restore protocol
- `img3tool.py` / `img4tool.py` - IMG3/IMG4 payload extraction
- `extract_ipsw_parts.py` - IPSW component extraction
- `filesystem_writer.py` - DMG filesystem to NAND

### Flash Mode Commands

```bash
# Run flash mode (auto-detects wraith directory)
node CONTROL_CENTER.js flash

# Full wraith mode with device integration
node CONTROL_CENTER.js wraith

# Sync device library mirror
node CONTROL_CENTER.js mirror

# Initialize device image bridge
node CONTROL_CENTER.js bridge

# Generate transfer Makefile
node CONTROL_CENTER.js makefile

# Using npm scripts
npm run flash      # Flash mode
npm run wraith     # Full wraith mode
npm run mirror     # Mirror sync
npm run makefile   # Generate Makefile
```

### Device Transfer Makefile

The generated `wraith_transfer.mk` provides:

```makefile
# Flash all components to NAND
make flash

# Verify NAND integrity
make verify

# Full transfer pipeline
make transfer

# IOsrom integration
make iosrom-nand
make iosrom-final
make iosrom-write

# Fast flash mode
make fast
make full
```

### How Flash Mode Works

1. **Detect Wraith Directory**: Scans for wraithps4-serv-backup-performance booster files
2. **Initialize Image Bridge**: Spawns `wraith_image_bridge.py` with IOsrom NAND handling
3. **Sync Library Mirror**: Uses `wraith_mirror_manager.js` to sync device packages
4. **Run Resolution**: Standard GF X H G F resolution in flash mode
5. **Apply Updates**: Packages are applied to connected device via RJ45 bridge

### Common Repository Issues This Tool Fixes

### 1. "Dependency Not Found" / "Module Not Found" Errors

**Problem:** Package was removed from registry or renamed.

**Fix:**
```bash
node index.js . adjust
```

The tool will search for available versions and suggest alternatives:
```
[VersionProtocol] old-package-name: ^1.0.0 → new-package-name 2.1.0 (adjusted)
```

### 2. Version Conflicts Between Dependencies

**Problem:** Package A requires lodash ^4.17.0, Package B requires lodash ^3.10.0

**Fix:**
```bash
node index.js .
```

The GF X H G F algorithm finds compatible versions:
```
✓ Column formed successfully
  Packages resolved: 15
  No conflict: true
  GF value: 0.8534
```

### 3. "Cannot resolve dependency" After Node/Python/Rust Update

**Problem:** Language version updated, old packages incompatible.

**Fix:**
```bash
# Python packages
python3 pipeline_bridge.py . 

# Node packages
node central_orchestrator.js .
```

Auto-creates virtual environments and finds compatible versions.

### 4. Mixed Language Project Dependency Hell

**Problem:** Backend (Python) and Frontend (Node.js) have conflicting transitive dependencies.

**Fix:**
```bash
# From project root
node index.js . terminal

# In terminal mode:
> r  # Resolve all packages
> c  # Check for corrections
```

The unified environment treats all packages as one ecosystem.

### 5. "npm install" or "pip install" Fails Repeatedly

**Problem:** Installation fails due to version mismatches.

**Fix:**
```bash
# Enable predictive monitoring
node predictive_pid_layer.js . 

# Let it run during installation - it will:
# - Detect version_mismatch errors in real-time
# - Suggest corrected versions
# - Output: "resolve_version_conflicts:lodash,axios"
```

### 6. Lockfile Out of Sync

**Problem:** package-lock.json or requirements.txt doesn't match actual installed versions.

**Fix:**
```bash
node index.js . 

# Parses installed packages and suggests lockfile updates:
# [Resolver] Detected 5 version mismatches
# Install commands:
#   npm install lodash@4.17.21
#   pip install requests==2.31.0
```

### 7. Security Vulnerabilities in Dependencies

**Problem:** npm audit or pip-audit shows vulnerable packages.

**Fix:**
```bash
# The targeting system prioritizes security updates
python3 pipeline_bridge.py . 

# Rules applied:
# [security-critical] priority=100 - updates auth/crypto packages first
```

## Quick Fix Commands

| Issue | Command |
|-------|---------|
| Version conflicts | `node index.js . adjust` |
| Missing packages | `node index.js .` |
| Install failures | `node predictive_pid_layer.js .` |
| Mixed language deps | `node central_orchestrator.js .` |
| Python venv issues | `python3 pipeline_bridge.py .` |
| Auto-watch for changes | `node index.js . watch` |
| Flash mode | `node CONTROL_CENTER.js flash` |
| Wraith mode | `node CONTROL_CENTER.js wraith` |
| Mirror sync | `node CONTROL_CENTER.js mirror` |

## How It Works

1. **Auto-Detect** - Finds package.json, requirements.txt, Cargo.toml, go.mod
2. **GF X H G F Algorithm** - Calculates compatibility scores (GF=Gap Factor, H=Harmony)
3. **Version Adjustment** - Searches registries for best matching versions
4. **Unified Resolution** - Ensures all languages work together
5. **Safe Installation** - Auto-creates venvs, installs corrected versions
6. **Device Integration** - Flash mode syncs and updates connected devices

## Installation

```bash
git clone https://github.com/JlovesYouGit/pk-resolver.git
cd pk-resolver
```

## Usage Examples

### Fix a Broken Node.js Project

```bash
cd my-broken-node-project
node index.js .

# Output shows:
# Detected 12 packages
# [VersionProtocol] 3 packages adjusted for compatibility
# npm install commands generated
```

### Fix Python Requirements Conflicts

```bash
cd my-python-project
python3 pipeline_bridge.py .

# Output:
# [CONSTRAINT] Auto-creating venv
# Adjusted 2 packages
# pip install commands generated
```

### Fix Full-Stack (Node + Python)

```bash
cd my-fullstack-app
node central_orchestrator.js .

# Unified resolution across backend/frontend
# Reports cross-language compatibility
```

### Flash Mode with Device

```bash
cd wraithps4-serv-backup-performance booster
node CONTROL_CENTER.js flash

# Output:
# [FLASH] Wraith Flash Mode ACTIVATED
# [FLASH] RJ45 connected: true
# [FLASH] Device image bridge initialized
# [FLASH] Mirror sync complete
# [FLASH] IOsrom integration available
```

## Files Generated

After running, check these files for resolution details:

- `.package_resolver_columns.json` - Resolved compatibility data
- `.pid_predictions.json` - Package error predictions
- `.unified_manifest.json` - Cross-language dependency map
- `wraith_transfer.mk` - Device transfer Makefile
- `library_mirror/` - Device library mirror directory

## Troubleshooting

### "No compatible resolution"

```bash
# Increase resolution rounds
node index.js . adjust

# Or manually specify a version
# Edit package.json/requirements.txt with working version
```

### "Python packages not installing"

```bash
# Verify venv was created
ls safely_contained_venv/bin/pip

# If missing, run:
python3 -m venv safely_contained_venv
python3 pipeline_bridge.py .
```

### "Device not connected in flash mode"

```bash
# Check RJ45/USB connection
irecovery -c getenv

# Verify device is in correct mode
make detect

# Check IOsrom tools are available
ls IOsrom/direct_nand_flasher.py
```

### "Still getting errors after fix"

```bash
# Clear resolution cache
rm .package_resolver_columns.json
node index.js .

# Or run in watch mode to catch new issues
node index.js . watch
```

## CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
- name: Fix Dependencies
  run: |
    git clone https://github.com/JlovesYouGit/pk-resolver.git
    node pk-resolver/index.js . adjust

- name: Flash Mode (Wraith)
  if: github.event_name == 'push' && contains(github.ref, 'main')
  run: |
    cd pk-resolver
    node CONTROL_CENTER.js wraith
```

## What Makes This Different

- **Cross-Language**: Fixes Node + Python + Rust + Go in one run
- **Proactive**: Predicts issues before they break builds
- **Automatic**: No manual version hunting
- **Safe**: Creates isolated environments
- **Device Integration**: Direct NAND flash and library mirror sync via IOsrom
- **Wraith Mode**: Operates within PS4 performance booster ecosystem

## Architecture

```
┌─────────────────────────────────────────────────────┐
│           Package Resolver v2                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐    ┌─────────────────────────┐  │
│  │   index.js   │───▶│  library parser logic/  │  │
│  │  (Main)      │    │    resolver.js          │  │
│  └──────────────┘    └─────────────────────────┘  │
│         │                       │                  │
│         ▼                       ▼                  │
│  ┌──────────────┐    ┌─────────────────────────┐  │
│  │   CONTROL    │    │  IOsrom Integration     │  │
│  │   CENTER.js  │    │  - NAND flash           │  │
│  └──────────────┘    │  - Image extraction     │  │
│         │             │  - IPSW handling        │  │
│         ▼             └─────────────────────────┘  │
│  ┌──────────────┐                                  │
│  │   Wraith     │◀─────────────────────────────────┤
│  │   Flash.js   │    ┌─────────────────────────┐  │
│  └──────────────┘    │  Wraith Image Bridge    │  │
│         │             │  (Python)               │  │
│         ▼             └─────────────────────────┘  │
│  ┌──────────────┐                                  │
│  │   Wraith     │                                  │
│  │   Mirror     │◀─────────────────────────────────┤
│  │   Manager.js │    ┌─────────────────────────┐  │
│  └──────────────┘    │  wraith_transfer.mk     │  │
│         │             │  (Makefile)             │  │
│         ▼             └─────────────────────────┘  │
│  ┌──────────────┐                                  │
│  │   Central    │                                  │
│  │   Orchestra  │                                  │
│  │   tor.js     │                                  │
│  └──────────────┘                                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Need Help?

Check the full guide: `unified_venv/how to use rule.md`

## License

MIT - See LICENSE file
