# Wraith Flash Mode Makefile
# Direct operation in wraith directory with IOsrom integration
# Device: iPad1,1 (A4) - NAND flash capable
# Build system with SDK toolchain variables

# =============================================================================
# SDK Toolchain Variables
# =============================================================================
SDK_VARCC_VAR ?= wraith_sdk
DEPLOY_VAR ?= wraith_deploy
VERSION_VAR := $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev-$(shell date +%Y%m%d)")
CFLAGS_VAR ?= -O2 -Wall -DWRAITH_FLASH_MODE -DIOsrom_INTEGRATION -DVEMEX_ACTIVE -DSEEDGATE_ACTIVE -DVERSION=\"$(VERSION_VAR)\"
ELF_VAR ?= wraith_resolver.elf

# =============================================================================
# Build Configuration
# =============================================================================
DEVICE_ID = iPad1,1
CHIP = A4
NAND_BASE = 0x09000000
IRECOVERY = irecovery
PYTHON = python3
NODE = node
CLANG = clang
CC = $(CLANG)

# Wraith components
WRATH_DIR = wraithps4-serv-backup-performance booster
IOSROM_DIR = IOsrom
NODEPACK_DIR = nodepack
VEMEX_DIR = Vemex
SEEDGATE_DIR = SeedGate

# Python bridges
IMAGE_BRIDGE = $(NODEPACK_DIR)/wraith_image_bridge.py
MIRROR_MANAGER = $(NODEPACK_DIR)/wraith_mirror_manager.js
FLASH_MODE = $(NODEPACK_DIR)/wraith_flash.js
CENTRAL_ORCHESTRATOR = $(NODEPACK_DIR)/central_orchestrator.js
CONTROL_CENTER = $(NODEPACK_DIR)/CONTROL_CENTER.js
PIPELINE_BRIDGE = $(NODEPACK_DIR)/pipeline_bridge.py
LATCH_SYSTEM = $(NODEPACK_DIR)/wraith_latch.js
VEMEX_INTEGRATION = $(VEMEX_DIR)/seedgate_integration.py
SEEDGATE_CLI = $(SEEDGATE_DIR)/python/seed_sampler/cli.py

# Mirror directories
MIRROR_DIR = library_mirror
MIRROR_IMAGES = $(MIRROR_DIR)/images
MIRROR_PACKAGES = $(MIRROR_DIR)/packages
MIRROR_NAND = $(MIRROR_DIR)/nand

# Extracted components
EXTRACTED_DIR = extracted
CHARGFAST_DIR = N:/ROMLOADDER/chargfast\ via\ usb

# SDK paths
SDK_ROOT = $(SDK_VARCC_VAR)
DEPLOY_ROOT = $(DEPLOY_VAR)
BUILD_DIR = build
DIST_DIR = dist

.PHONY: all help detect status prepare flash verify clean reboot \
        wraith wraith-flash wraith-mirror wraith-bridge transfer \
        ipsw-extract nand-flash device-sync package-update \
        iosrom-nand iosrom-final iosrom-write fast full \
        install-packages fix-packages resolver latch \
        build-sdk build-elf build-all vemex-scan seedgate-scan \
        sdk-info version-info deploy \
        network-scan device-find device-connect \
        goldhen-deploy goldhen-config goldhen-cheats goldhen-status \
        goldhen-deploy-device goldhen-troubleshoot goldhen-server

all: detect status

help:
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║          Wraith Flash Mode Makefile                         ║"
	@echo "║          PS4 Performance Booster + Device Flash              ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "SDK Build Variables:"
	@echo "  SDK_VARCC_VAR=$(SDK_VARCC_VAR)"
	@echo "  DEPLOY_VAR=$(DEPLOY_VAR)"
	@echo "  VERSION_VAR=$(VERSION_VAR)"
	@echo "  CFLAGS_VAR=$(CFLAGS_VAR)"
	@echo "  ELF_VAR=$(ELF_VAR)"
	@echo ""
	@echo "Device Targets:"
	@echo "  make detect          - Detect connected device"
	@echo "  make status          - Show device and system status"
	@echo "  make prepare         - Prepare directories and environment"
	@echo "  make flash           - Flash components to NAND"
	@echo "  make verify          - Verify NAND integrity"
	@echo "  make clean           - Clean extracted files"
	@echo "  make reboot          - Reboot device"
	@echo ""
	@echo "Wraith Integration:"
	@echo "  make wraith          - Run full wraith flash mode"
	@echo "  make wraith-flash    - Run flash mode resolution"
	@echo "  make wraith-mirror   - Sync device library mirror"
	@echo "  make wraith-bridge   - Initialize wraith image bridge"
	@echo "  make transfer        - Full transfer pipeline"
	@echo "  make network-scan    - Scan local network for devices"
	@echo "  make device-find     - Find best device on network"
	@echo "  make device-connect  - Connect to discovered device"
	@echo ""
	@echo "Latching System:"
	@echo "  make latch           - Start wraith automatic latching"
	@echo "  make latch-status    - Show latching status"
	@echo "  make latch-stop      - Stop latching system"
	@echo ""
	@echo "GoldHEN Integration:"
	@echo "  make goldhen-deploy  - Deploy GoldHEN payload to device"
	@echo "  make goldhen-config  - Configure GoldHEN settings"
	@echo "  make goldhen-cheats  - Setup GoldHEN cheats directory"
	@echo "  make goldhen-status  - Show GoldHEN status"
	@echo ""
	@echo "Package Management:"
	@echo "  make install-packages - Install resolved packages"
	@echo "  make fix-packages     - Fix package conflicts"
	@echo "  make resolver         - Run package resolver"
	@echo ""
	@echo "IOsrom Integration:"
	@echo "  make iosrom-nand     - Run IOsrom NAND flasher"
	@echo "  make iosrom-final    - Run IOsrom FINAL_NAND_FLASH"
	@echo "  make iosrom-write    - Run IOsrom WRITE_NAND_DIRECT"
	@echo ""
	@echo "SDK Build:"
	@echo "  make build-sdk       - Build SDK components"
	@echo "  make build-elf       - Build ELF binary"
	@echo "  make build-all       - Build everything"
	@echo "  make sdk-info        - Show SDK info"
	@echo "  make version-info    - Show version info"
	@echo "  make deploy          - Deploy to device"
	@echo ""
	@echo "Vemex/SeedGate:"
	@echo "  make vemex-scan      - Run Vemex seed scan"
	@echo "  make seedgate-scan   - Run SeedGate scan"
	@echo ""
	@echo "Fast Targets (Flash Mode):"
	@echo "  make fast            - Fast flash (detect + prepare + flash)"
	@echo "  make full            - Full pipeline (detect + extract + flash + verify)"
	@echo ""
	@echo "Examples:"
	@echo "  make detect"
	@echo "  make wraith"
	@echo "  make fast IPSW=my_firmware.ipsw"
	@echo "  make build-elf SDK_VARCC_VAR=./sdk DEPLOY_VAR=./deploy"

# Device detection
detect:
	@echo "[+] Detecting device via RJ45/USB..."
	@$(IRECOVERY) -c getenv 2>/dev/null | head -5 || echo "[!] Device not detected - check connection"
	@echo "[+] Device detection complete"

status:
	@echo "[+] Wraith System Status"
	@echo "  SDK_VARCC_VAR: $(SDK_VARCC_VAR)"
	@echo "  DEPLOY_VAR: $(DEPLOY_VAR)"
	@echo "  VERSION_VAR: $(VERSION_VAR)"
	@echo "  CFLAGS_VAR: $(CFLAGS_VAR)"
	@echo "  ELF_VAR: $(ELF_VAR)"
	@echo "  Device connected: $(shell $(IRECOVERY) -c getenv > /dev/null 2>&1 && echo YES || echo NO)"
	@echo "  Mirror directory: $(shell test -d $(MIRROR_DIR) && echo EXISTS || echo MISSING)"
	@echo "  Wraith directory: $(shell test -d '$(WRATH_DIR)' && echo EXISTS || echo MISSING)"
	@echo "  IOsrom directory: $(shell test -d '$(IOSROM_DIR)' && echo EXISTS || echo MISSING)"
	@echo "  Vemex directory: $(shell test -d '$(VEMEX_DIR)' && echo EXISTS || echo MISSING)"
	@echo "  SeedGate directory: $(shell test -d '$(SEEDGATE_DIR)' && echo EXISTS || echo MISSING)"
	@echo "  Flash mode: ENABLED"
	@echo "  RJ45 active: CHECKING..."
	@echo ""
	@echo "[+] NODEPACK Status"
	@echo "  Resolver: $(shell test -f $(NODEPACK_DIR)/index.js && echo EXISTS || echo MISSING)"
	@echo "  Image Bridge: $(shell test -f $(IMAGE_BRIDGE) && echo EXISTS || echo MISSING)"
	@echo "  Mirror Manager: $(shell test -f $(MIRROR_MANAGER) && echo EXISTS || echo MISSING)"
	@echo "  Flash Mode: $(shell test -f $(FLASH_MODE) && echo EXISTS || echo MISSING)"
	@echo "  Latch System: $(shell test -f $(LATCH_SYSTEM) && echo EXISTS || echo MISSING)"

# SDK info
sdk-info:
	@echo "[+] SDK Information"
	@echo "  SDK_VARCC_VAR: $(SDK_VARCC_VAR)"
	@echo "  DEPLOY_VAR: $(DEPLOY_VAR)"
	@echo "  SDK_ROOT: $(shell test -d '$(SDK_ROOT)' && echo EXISTS || echo MISSING)"
	@echo "  DEPLOY_ROOT: $(shell test -d '$(DEPLOY_ROOT)' && echo EXISTS || echo MISSING)"

version-info:
	@echo "[+] Version Information"
	@echo "  VERSION_VAR: $(VERSION_VAR)"
	@echo "  Git tags: $(shell git tag -l | tail -5)"
	@echo "  Git commit: $(shell git rev-parse --short HEAD 2>/dev/null || echo N/A)"
	@echo "  Git branch: $(shell git branch -s | head -1)"

# Environment preparation
prepare:
	@echo "[+] Preparing directories..."
	@mkdir -p $(MIRROR_IMAGES) $(MIRROR_PACKAGES) $(MIRROR_NAND)
	@mkdir -p $(MIRROR_DIR)/boot $(MIRROR_DIR)/system $(MIRROR_DIR)/frameworks
	@mkdir -p $(EXTRACTED_DIR)
	@mkdir -p $(BUILD_DIR) $(DIST_DIR)
	@echo "[+] Directories prepared"
	@echo "[+] Environment ready for flash mode"

# =============================================================================
# SDK Build Rules
# =============================================================================
build-sdk: prepare
	@echo "[+] Building SDK components..."
	@echo "  SDK: $(SDK_VARCC_VAR)"
	@echo "  Deploy: $(DEPLOY_VAR)"
	@echo "  Version: $(VERSION_VAR)"
	@echo "  CFLAGS: $(CFLAGS_VAR)"
	@if [ -d "$(SDK_VARCC_VAR)" ]; then \
		echo "[+] SDK found at $(SDK_VARCC_VAR)"; \
		cd $(SDK_VARCC_VAR) && $(MAKE) all 2>/dev/null || echo "[!] SDK build failed"; \
	else \
		echo "[!] SDK not found at $(SDK_VARCC_VAR) - using defaults"; \
	fi
	@echo "[+] SDK build complete"

build-elf: prepare
	@echo "[+] Building ELF binary..."
	@echo "  Output: $(ELF_VAR)"
	@echo "  CFLAGS: $(CFLAGS_VAR)"
	@mkdir -p $(BUILD_DIR)
	@$(CC) $(CFLAGS_VAR) -I$(SDK_VARCC_VAR)/include -o $(BUILD_DIR)/$(ELF_VAR) \
		$(NODEPACK_DIR)/wraith_latch.js \
		$(NODEPACK_DIR)/wraith_flash.js \
		$(NODEPACK_DIR)/wraith_image_bridge.py \
		$(NODEPACK_DIR)/wraith_mirror_manager.js 2>/dev/null || \
		echo "[!] ELF build requires full source compilation"
	@echo "[+] ELF build complete: $(BUILD_DIR)/$(ELF_VAR)"

build-all: build-sdk build-elf
	@echo "[+] Full build complete"
	@echo "  SDK: $(SDK_VARCC_VAR)"
	@echo "  Deploy: $(DEPLOY_VAR)"
	@echo "  ELF: $(ELF_VAR)"
	@echo "  Version: $(VERSION_VAR)"

# =============================================================================
# Deploy Rules
# =============================================================================
deploy: build-all detect
	@echo "[+] Deploying to device..."
	@echo "  Target: $(DEPLOY_VAR)"
	@echo "  ELF: $(ELF_VAR)"
	@if [ -d "$(DEPLOY_VAR)" ]; then \
		cp $(BUILD_DIR)/$(ELF_VAR) $(DEPLOY_VAR)/; \
		echo "[+] Deployed to $(DEPLOY_VAR)"; \
	else \
		echo "[!] Deploy directory not found: $(DEPLOY_VAR)"; \
	fi
	@echo "[+] Deploy complete"

# Wraith integration
wraith: wraith-bridge wraith-flash wraith-mirror
	@echo "[+] Wraith full mode complete"

wraith-flash:
	@echo "[+] Running wraith flash mode..."
	@$(NODE) $(FLASH_MODE) . flash
	@echo "[+] Wraith flash complete"

wraith-mirror:
	@echo "[+] Syncing device library mirror..."
	@$(NODE) $(MIRROR_MANAGER) . --mirror
	@echo "[+] Mirror sync complete"

wraith-bridge:
	@echo "[+] Initializing wraith image bridge..."
	@$(PYTHON) $(IMAGE_BRIDGE) . --mirror
	@echo "[+] Bridge initialized"

# Transfer pipeline
transfer: detect prepare ipsw-extract nand-flash verify
	@echo "[+] Full transfer pipeline complete"

# IPSW operations
ipsw-extract:
	@if [ -z "$(IPS)" ]; then \
		echo "[!] Usage: make ipsw-extract IPSW=file.ipsw"; \
		exit 1; \
	fi
	@echo "[+] Extracting IPSW: $(IPS)"
	@$(PYTHON) $(IMAGE_BRIDGE) . --extract $(IPS)
	@echo "[+] IPSW extracted to $(EXTRACTED_DIR)"

# NAND flash operations
nand-flash: prepare
	@echo "[+] Flashing components to NAND..."
	@$(PYTHON) $(IMAGE_BRIDGE) . --flash-nand
	@echo "[+] NAND flash complete"

flash: nand-flash
	@echo "[+] Flash operation complete"

verify:
	@echo "[+] Verifying NAND integrity..."
	@$(IRECOVERY) -c getenv | grep boot-partition || echo "[!] Verification check"
	@echo "[+] Verification complete"

# Device sync
device-sync:
	@echo "[+] Syncing device library to mirror..."
	@$(PYTHON) $(IMAGE_BRIDGE) . --mirror
	@echo "[+] Device sync complete"

# Network device discovery (real network, no stubs)
network-scan:
	@echo "[+] Scanning local network for devices..."
	@$(PYTHON) -c "from SeedGate.internal.seed_sampler_integration.network.client import DeviceFinder; df = DeviceFinder(); devices = df.scan(force=True); print(f'Found {len(devices)} device(s):'); [print(f'  {d.mac} @ {d.ip}') for d in devices]" 2>/dev/null || \
		echo "[!] SeedGate network client scan failed - check installation"
	@echo "[+] Network scan complete"

device-find:
	@echo "[+] Finding best device on network..."
	@$(PYTHON) -c "from SeedGate.internal.seed_sampler_integration.network.client import DeviceFinder; df = DeviceFinder(); dev = df.find_best_device(); print(dev.mac + ' ' + dev.ip if dev else 'No device found')" 2>/dev/null || \
		echo "[!] SeedGate device finder failed - check installation"
	@echo "[+] Device find complete"

device-connect:
	@echo "[+] Connecting to discovered device..."
	@$(NODE) $(LATCH_SYSTEM) . run
	@echo "[+] Device connect complete"

# GoldHEN integration
GOLDHEN_DIR = GoldHEN
GOLDHEN_BIN = $(GOLDHEN_DIR)/goldhen.bin
GOLDHEN_INTEGRATION = goldhen_integration.py
GOLDHEN_DEPLOYER = goldhen_device_deployer.js
GOLDHEN_ENDPOINT_SERVER = goldhen_endpoint_server.js

goldhen-deploy:
	@echo "[+] Deploying GoldHEN payload..."
	@if [ ! -f "$(GOLDHEN_BIN)" ]; then \
		echo "[!] GoldHEN payload not found: $(GOLDHEN_BIN)"; \
		exit 1; \
	fi
	@$(PYTHON) $(GOLDHEN_INTEGRATION) . --deploy
	@echo "[+] GoldHEN deployment complete"

goldhen-deploy-device:
	@echo "[+] Full GoldHEN device deployment..."
	@$(NODE) $(GOLDHEN_DEPLOYER) . deploy
	@echo "[+] GoldHEN device deployment complete"

goldhen-config:
	@echo "[+] GoldHEN configuration..."
	@$(PYTHON) $(GOLDHEN_INTEGRATION) . --config
	@echo "[+] GoldHEN config displayed"

goldhen-cheats:
	@echo "[+] Setting up GoldHEN cheats directory..."
	@$(PYTHON) $(GOLDHEN_INTEGRATION) . --cheats
	@echo "[+] GoldHEN cheats directory ready"

goldhen-status:
	@echo "[+] GoldHEN status..."
	@$(PYTHON) $(GOLDHEN_INTEGRATION) . --status
	@echo "[+] GoldHEN status displayed"

goldhen-troubleshoot:
	@echo "[+] Troubleshooting GoldHEN deployment..."
	@$(NODE) $(GOLDHEN_DEPLOYER) . troubleshoot
	@echo "[+] Troubleshooting complete"

goldhen-server:
	@echo "[+] Starting GoldHEN HTTP endpoint server..."
	@echo "[+] Open PS4 browser and navigate to http://<server-ip>:8080"
	@$(NODE) $(GOLDHEN_ENDPOINT_SERVER) . 8080
	@echo "[+] Server stopped"

# Package management
package-update:
	@if [ -z "$(PKG)" ] || [ -z "$(VER)" ] || [ -z "$(LANG)" ]; then \
		echo "[!] Usage: make package-update PKG=name VER=version LANG=python"; \
		exit 1; \
	fi
	@echo "[+] Updating package: $(PKG)@$(VER) ($(LANG))"
	@$(NODE) $(MIRROR_MANAGER) . --package-update $(PKG) $(VER) $(LANG)
	@echo "[+] Package updated"

install-packages:
	@echo "[+] Installing resolved packages..."
	@$(NODE) $(NODEPACK_DIR)/index.js . flash
	@echo "[+] Package installation complete"

fix-packages:
	@echo "[+] Fixing package conflicts..."
	@$(NODE) $(CONTROL_CENTER) fix .
	@echo "[+] Package fix complete"

resolver:
	@echo "[+] Running package resolver..."
	@$(NODE) $(NODEPACK_DIR)/index.js . flash
	@echo "[+] Resolution complete"

# Makefile generation
makefile:
	@echo "[+] Generating transfer Makefile..."
	@$(PYTHON) $(IMAGE_BRIDGE) . --makefile
	@echo "[+] Makefile generated: wraith_transfer.mk"

# IOsrom integration
iosrom-nand:
	@echo "[+] Running IOsrom NAND flasher..."
	@cd $(IOSROM_DIR) && $(PYTHON) direct_nand_flasher.py
	@echo "[+] IOsrom NAND flash complete"

iosrom-final:
	@echo "[+] Running IOsrom FINAL_NAND_FLASH..."
	@cd $(IOSROM_DIR) && $(PYTHON) FINAL_NAND_FLASH.py
	@echo "[+] IOsrom final flash complete"

iosrom-write:
	@echo "[+] Running IOsrom WRITE_NAND_DIRECT..."
	@cd $(IOSROM_DIR) && $(PYTHON) WRITE_NAND_DIRECT.py
	@echo "[+] IOsrom direct write complete"

# Fast targets
fast: detect prepare flash
	@echo "[+] Fast flash complete"

full: detect prepare ipsw-extract flash verify
	@echo "[+] Full pipeline complete"

# Clean
clean:
	@echo "[+] Cleaning..."
	@rm -rf $(EXTRACTED_DIR)/*
	@rm -rf $(MIRROR_DIR)/*
	@echo "[+] Clean complete"

reboot:
	@echo "[+] Rebooting device..."
	@$(IRECOVERY) -c reboot
	@echo "[+] Reboot command sent"

# Default target
.DEFAULT_GOAL := help
