#!/usr/bin/env node
/**
 * Wraith Automatic Latching System
 * Latch to variables on Ethernet device connection using MAC/USB-C adapter
 * Integrates Vemex/SeedGate connection specs with wraith protocol
 * Always active - monitors for device connections and auto-latches
 * Uses real network discovery via SeedGate device finder
 */

const { spawn, exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const util = require('util');
const execAsync = util.promisify(exec);
const { WraithFlashMode } = require('./wraith_flash');
const { WraithMirrorManager } = require('./wraith_mirror_manager');

class WraithLatchSystem {
    constructor(workDir) {
        this.workDir = workDir;
        this.flashMode = new WraithFlashMode(workDir);
        this.mirrorManager = null;
        this.latched = false;
        this.deviceMac = null;
        this.deviceIp = null;
        this.adapterType = 'USB-C_Ethernet';
        this.ethernetPort = 'en0';
        this.latchTimeout = 5000;
        this.pollInterval = 2000;
        this.pollTimer = null;
        this.vemexActive = true;
        this.seedgateActive = true;
        this.nandOverpass = {
            enabled: true,
            boolean: true,
            string: 'nand_overpass_active',
            int: 34,
            arrayOfStrings: ['nand_read', 'nand_write', 'nand_erase', 'direct_flash'],
            regex: '^nand\\s+(read|write|erase|open|close)$',
            float: 1.0
        };
        this.deviceFinder = null;
        this.seedgateProcess = null;
        this.macMapper = null;
        this.adminPass = 'jj';
        this.keepAliveInterval = null;
        this.connectionState = 'disconnected';
        this.softLayerUnblocked = false;
    }

    async initialize() {
        console.log('[Latch] Initializing Wraith Automatic Latching System...');
        
        // Activate flash mode
        const flashStatus = this.flashMode.activateFlash();
        if (!flashStatus.active) {
            console.log('[Latch] Not in wraith directory - limited mode');
        } else {
            console.log(`[Latch] Flash mode active: ${flashStatus.wraithDir}`);
        }

        // Initialize mirror manager
        this.mirrorManager = new WraithMirrorManager(this.workDir, this.flashMode);
        await this.mirrorManager.initialize();

        // Load meta.json configuration
        this.loadMetaConfig();

        // Start SeedGate real network client (always active)
        this.startSeedGateNetwork();

        // Start latching loop
        this.startLatching();

        return {
            initialized: true,
            latched: this.latched,
            deviceMac: this.deviceMac,
            adapterType: this.adapterType,
            flashMode: flashStatus.active
        };
    }

    loadMetaConfig() {
        const metaPath = path.join(this.workDir, 'meta.json');
        if (!fs.existsSync(metaPath)) {
            const parentMeta = path.join(this.workDir, '..', 'meta.json');
            if (fs.existsSync(parentMeta)) {
                this.meta = JSON.parse(fs.readFileSync(parentMeta, 'utf8'));
            } else {
                this.meta = {};
            }
        } else {
            this.meta = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
        }

        if (this.meta.wraith) {
            this.nandOverpass = { ...this.nandOverpass, ...this.meta.wraith.nand_overpass };
            if (this.meta.wraith.mac_gating) {
                this.adapterType = this.meta.wraith.mac_gating.adapter_type || this.adapterType;
                this.ethernetPort = this.meta.wraith.mac_gating.ethernet_port || this.ethernetPort;
            }
        }

        // Initialize MAC mapper from SeedGate JSON
        this.macMapper = this.loadMacMapper();
        
        // Load admin pass from meta
        if (this.meta.wraith && this.meta.wraith.protocol && this.meta.wraith.protocol.auth_token) {
            this.adminPass = this.meta.wraith.protocol.auth_token;
        }

        console.log(`[Latch] Meta config loaded: nand_overpass=${this.nandOverpass.enabled}`);
        console.log(`[Latch] MAC mapper loaded: ${this.macMapper ? 'ACTIVE' : 'INACTIVE'}`);
        console.log(`[Latch] Admin pass: ${this.adminPass ? 'SET' : 'NONE'}`);
    }

    loadMacMapper() {
        const connectionsPath = path.join(this.workDir, 'SeedGate', 'data', '.seedgate_connections.json');
        if (!fs.existsSync(connectionsPath)) {
            const parentConnections = path.join(this.workDir, '..', 'SeedGate', 'data', '.seedgate_connections.json');
            if (fs.existsSync(parentConnections)) {
                try {
                    const data = JSON.parse(fs.readFileSync(parentConnections, 'utf8'));
                    return this.buildMacMapper(data);
                } catch (e) {
                    console.log(`[Latch] Could not load parent SeedGate connections: ${e.message}`);
                }
            }
            return null;
        }

        try {
            const data = JSON.parse(fs.readFileSync(connectionsPath, 'utf8'));
            return this.buildMacMapper(data);
        } catch (e) {
            console.log(`[Latch] Could not load SeedGate connections: ${e.message}`);
            return null;
        }
    }

    buildMacMapper(connectionsData) {
        const mapper = {
            primary: null,
            fallbacks: [],
            keepAliveTargets: [],
            adminUnblocked: new Set(),
            softLayerUnblocked: false,
            mappings: new Map(),
            senderMac: null,
            receiverMac: null,
            macRoute: null
        };

        for (const [id, conn] of Object.entries(connectionsData)) {
            const mac = conn.mac;
            const ip = conn.ip;
            if (!mac || !ip) continue;

            const mapping = {
                id,
                mac,
                ip,
                port: conn.port,
                established: conn.established,
                transport: conn.transport,
                keepAlive: conn.keep_alive || false,
                ps4Candidate: conn.ps4_candidate || false,
                score: conn.score || 0,
                timestamp: conn.timestamp,
                lanMac: conn.lan_mac || null,
                senderMac: conn.sender_mac || null,
                receiverMac: conn.receiver_mac || null,
                macRoute: conn.mac_route || null
            };

            mapper.mappings.set(mac, mapping);

            // Extract sender/receiver MAC routing
            if (conn.sender_mac && !mapper.senderMac) {
                mapper.senderMac = conn.sender_mac;
            }
            if (conn.receiver_mac && !mapper.receiverMac) {
                mapper.receiverMac = conn.receiver_mac;
            }
            if (conn.mac_route && !mapper.macRoute) {
                mapper.macRoute = conn.mac_route;
            }

            if (mapping.keepAlive && !mapper.keepAliveTargets.includes(mac)) {
                mapper.keepAliveTargets.push(mac);
            }

            if (mapping.ps4Candidate && mapping.score > 0 && !mapper.primary) {
                mapper.primary = mapping;
            }

            if (conn.established) {
                mapper.fallbacks.push(mapping);
            }
        }

        // Sort fallbacks by score descending
        mapper.fallbacks.sort((a, b) => (b.score || 0) - (a.score || 0));

        console.log(`[Latch] MAC mapper built: primary=${mapper.primary ? mapper.primary.mac : 'none'}`);
        if (mapper.senderMac) {
            console.log(`[Latch] Sender MAC: ${mapper.senderMac}`);
        }
        if (mapper.receiverMac) {
            console.log(`[Latch] Receiver MAC: ${mapper.receiverMac}`);
        }
        console.log(`[Latch] Keep-alive targets: ${mapper.keepAliveTargets.length}, fallbacks: ${mapper.fallbacks.length}`);
        
        return mapper;
    }

    async detectNetworkDevice() {
        const result = { connected: false, mac: null, ip: null, adapter: null, port: null, source: null };

        // Priority 1: Use sender/receiver MAC routing from SeedGate JSON
        if (this.macMapper && this.macMapper.senderMac && this.macMapper.receiverMac) {
            const senderMac = this.macMapper.senderMac;
            const receiverMac = this.macMapper.receiverMac;
            const primary = this.macMapper.primary;
            
            console.log(`[Latch] [MACRoute] Sender: ${senderMac} -> Receiver: ${receiverMac}`);
            
            // Try to reach receiver through sender's network
            if (primary) {
                console.log(`[Latch] [MACRoute] Trying route via primary: ${primary.mac} @ ${primary.ip}`);
                
                if (await this.probeDevice(primary.ip, primary.port)) {
                    result.connected = true;
                    result.mac = receiverMac;
                    result.ip = primary.ip;
                    result.adapter = this.adapterType;
                    result.port = primary.port || this.ethernetPort;
                    result.source = 'mac_route_sender_to_receiver';
                    console.log(`[Latch] [MACRoute] Route ESTABLISHED: ${senderMac} -> ${receiverMac} @ ${primary.ip}`);
                    return result;
                }
            }
            
            // Try direct connection to receiver MAC's IP
            if (primary) {
                console.log(`[Latch] [MACRoute] Trying direct connection to receiver...`);
                if (await this.probeDevice(primary.ip, primary.port)) {
                    result.connected = true;
                    result.mac = receiverMac;
                    result.ip = primary.ip;
                    result.adapter = this.adapterType;
                    result.port = primary.port || this.ethernetPort;
                    result.source = 'mac_route_direct';
                    console.log(`[Latch] [MACRoute] Direct connection to receiver ESTABLISHED`);
                    return result;
                }
            }
        }

        // Priority 2: Use MAC mapper primary target (from SeedGate JSON)
        if (this.macMapper && this.macMapper.primary) {
            const primary = this.macMapper.primary;
            console.log(`[Latch] [MACMapper] Trying primary target: ${primary.mac} @ ${primary.ip}`);
            
            if (await this.probeDevice(primary.ip, primary.port)) {
                result.connected = true;
                result.mac = primary.mac;
                result.ip = primary.ip;
                result.adapter = this.adapterType;
                result.port = primary.port || this.ethernetPort;
                result.source = 'mac_mapper_primary';
                console.log(`[Latch] [MACMapper] Primary target REACHABLE`);
                return result;
            } else {
                console.log(`[Latch] [MACMapper] Primary target UNREACHABLE, trying fallbacks...`);
            }
        }

        // Priority 2: Try keep-alive targets
        if (this.macMapper && this.macMapper.keepAliveTargets.length > 0) {
            for (const mac of this.macMapper.keepAliveTargets) {
                const mapping = this.macMapper.mappings.get(mac);
                if (!mapping) continue;
                
                console.log(`[Latch] [MACMapper] Trying keep-alive target: ${mac} @ ${mapping.ip}`);
                if (await this.probeDevice(mapping.ip, mapping.port)) {
                    result.connected = true;
                    result.mac = mac;
                    result.ip = mapping.ip;
                    result.adapter = this.adapterType;
                    result.port = mapping.port || this.ethernetPort;
                    result.source = 'mac_mapper_keepalive';
                    console.log(`[Latch] [MACMapper] Keep-alive target REACHABLE`);
                    return result;
                }
            }
        }

        // Priority 3: Try fallback devices
        if (this.macMapper && this.macMapper.fallbacks.length > 0) {
            for (const mapping of this.macMapper.fallbacks) {
                if (mapping.mac === (this.macMapper.primary && this.macMapper.primary.mac)) continue;
                if (this.macMapper.keepAliveTargets.includes(mapping.mac)) continue;
                
                console.log(`[Latch] [MACMapper] Trying fallback: ${mapping.mac} @ ${mapping.ip}`);
                if (await this.probeDevice(mapping.ip, mapping.port)) {
                    result.connected = true;
                    result.mac = mapping.mac;
                    result.ip = mapping.ip;
                    result.adapter = this.adapterType;
                    result.port = mapping.port || this.ethernetPort;
                    result.source = 'mac_mapper_fallback';
                    console.log(`[Latch] [MACMapper] Fallback REACHABLE`);
                    return result;
                }
            }
        }

        // Priority 4: Check via SeedGate device finder first
        try {
            const finderOutput = await execAsync(
                "python3 -c \"import sys; sys.path.insert(0, 'SeedGate'); from internal.seed_sampler_integration.network.client import DeviceFinder; df = DeviceFinder(); dev = df.find_best_device(); print(dev.mac + ' ' + dev.ip if dev else '')\" 2>/dev/null || echo ''"
            );
            const parts = finderOutput.stdout.trim().split(' ');
            if (parts.length >= 2 && parts[0] && parts[1]) {
                result.connected = true;
                result.mac = parts[0];
                result.ip = parts[1];
                result.adapter = this.adapterType;
                result.port = this.ethernetPort;
                result.source = 'seedgate_finder';
                console.log(`[Latch] [SeedGate] Device found via finder: ${parts[0]} @ ${parts[1]}`);
                return result;
            }
        } catch (e) {
            // Ignore
        }

        // Priority 5: ARP table scan
        try {
            const { stdout } = await execAsync("arp -a 2>/dev/null | grep -v incomplete | head -5 || echo ''");
            const lines = stdout.trim().split('\n');
            for (const line of lines) {
                const match = line.match(/\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-fA-F:]{17})/);
                if (match) {
                    result.connected = true;
                    result.mac = match.group(2).toLowerCase();
                    result.ip = match.group(1);
                    result.adapter = this.adapterType;
                    result.port = this.ethernetPort;
                    result.source = 'arp_table';
                    return result;
                }
            }
        } catch (e) {
            // Ignore
        }

        return result;
    }

    async probeDevice(ip, port) {
        if (!ip) return false;
        
        const ports = [port, 8080, 80, 443, 5000, 3000, 9000, 22, 2323, 9293].filter(Boolean);
        
        for (const p of ports) {
            try {
                const result = await this.tcpProbe(ip, p);
                if (result) {
                    console.log(`[Latch] [Probe] Device reachable at ${ip}:${p}`);
                    return true;
                }
            } catch (e) {
                continue;
            }
        }
        
        return false;
    }

    async tcpProbe(ip, port) {
        return new Promise((resolve) => {
            const net = require('net');
            const socket = new net.Socket();
            const timeout = 1500;
            
            socket.setTimeout(timeout);
            
            socket.connect(port, ip, () => {
                socket.end();
                resolve(true);
            });
            
            socket.on('error', () => {
                try { socket.destroy(); } catch (e) {}
                resolve(false);
            });
            
            socket.on('timeout', () => {
                try { socket.destroy(); } catch (e) {}
                resolve(false);
            });
        });
    }

    startSeedGateNetwork() {
        console.log('[Latch] SeedGate network client ACTIVE');
        
        // Spawn SeedGate network client in background
        const networkClient = path.join(this.workDir, 'SeedGate', 'internal', 'seed_sampler_integration', 'network', 'client.py');
        if (!fs.existsSync(networkClient)) {
            const siblingClient = path.join(this.workDir, '..', 'SeedGate', 'internal', 'seed_sampler_integration', 'network', 'client.py');
            if (fs.existsSync(siblingClient)) {
                this.seedgateProcess = spawn('python3', [siblingClient], {
                    stdio: ['pipe', 'pipe', 'pipe'],
                    cwd: path.join(this.workDir, '..', 'SeedGate')
                });
            }
        } else {
            this.seedgateProcess = spawn('python3', [networkClient], {
                stdio: ['pipe', 'pipe', 'pipe'],
                cwd: path.join(this.workDir, 'SeedGate')
            });
        }

        if (this.seedgateProcess) {
            this.seedgateProcess.stdout.on('data', (data) => {
                console.log('[SeedGate]', data.toString().trim());
            });
            this.seedgateProcess.stderr.on('data', (data) => {
                console.log('[SeedGate]', data.toString().trim());
            });
        }
    }

    startLatching() {
        console.log(`[Latch] Starting latching loop (poll every ${this.pollInterval}ms)`);
        this.pollTimer = setInterval(() => this.pollDevice(), this.pollInterval);
        this.pollDevice();
    }

    async pollDevice() {
        try {
            const deviceInfo = await this.detectNetworkDevice();
            
            if (deviceInfo.connected && !this.latched) {
                console.log(`[Latch] Device detected: ${deviceInfo.mac} @ ${deviceInfo.ip}`);
                await this.latchToDevice(deviceInfo);
            } else if (!deviceInfo.connected && this.latched) {
                console.log('[Latch] Device disconnected - unlatching');
                this.unlatch();
            }

            if (this.latched) {
                this.updateNandOverpass();
            }
        } catch (e) {
            console.error('[Latch] Poll error:', e.message);
        }
    }

    async detectNetworkDevice() {
        const result = { connected: false, mac: null, ip: null, adapter: null, port: null };

        // Check via SeedGate device finder first
        try {
            const finderOutput = await execAsync(
                "python3 -c \"import sys; sys.path.insert(0, 'SeedGate'); from internal.seed_sampler_integration.network.client import DeviceFinder; df = DeviceFinder(); dev = df.find_best_device(); print(dev.mac + ' ' + dev.ip if dev else '')\" 2>/dev/null || echo ''"
            );
            const parts = finderOutput.stdout.trim().split(' ');
            if (parts.length >= 2 && parts[0] && parts[1]) {
                result.connected = true;
                result.mac = parts[0];
                result.ip = parts[1];
                result.adapter = this.adapterType;
                result.port = this.ethernetPort;
                return result;
            }
        } catch (e) {
            // Ignore
        }

        // Fallback: scan ARP table
        try {
            const { stdout } = await execAsync("arp -a 2>/dev/null | grep -v incomplete | head -5 || echo ''");
            const lines = stdout.trim().split('\n');
            for (const line of lines) {
                const match = line.match(/\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-fA-F:]{17})/);
                if (match) {
                    result.connected = true;
                    result.mac = match.group(2).toLowerCase();
                    result.ip = match.group(1);
                    result.adapter = this.adapterType;
                    result.port = this.ethernetPort;
                    return result;
                }
            }
        } catch (e) {
            // Ignore
        }

        // Fallback: check active network connections
        try {
            const { stdout } = await execAsync("ss -tn 2>/dev/null | awk 'NR>1 {print $5}' | sort -u | head -10 || echo ''");
            const ips = stdout.trim().split('\n').filter(ip => ip && !ip.startsWith('127.'));
            if (ips.length > 0) {
                result.connected = true;
                result.ip = ips[0];
                result.mac = await this.resolveMacFromIp(result.ip);
                result.adapter = this.adapterType;
                result.port = this.ethernetPort;
                return result;
            }
        } catch (e) {
            // Ignore
        }

        return result;
    }

    async resolveMacFromIp(ip) {
        try {
            const { stdout } = await execAsync(`arp -a ${ip} 2>/dev/null | grep -oE '([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}' || echo ''`);
            return stdout.trim() || null;
        } catch (e) {
            return null;
        }
    }

    async latchToDevice(deviceInfo) {
        console.log(`[Latch] Latching to device ${deviceInfo.mac} @ ${deviceInfo.ip}...`);
        
        this.deviceMac = deviceInfo.mac;
        this.deviceIp = deviceInfo.ip;
        this.adapterType = deviceInfo.adapter;
        this.ethernetPort = deviceInfo.port;
        this.latched = true;
        this.connectionState = 'active';

        // Latch environment variables
        process.env.WRAITH_LATCHED = 'true';
        process.env.WRAITH_DEVICE_MAC = deviceInfo.mac;
        process.env.WRAITH_DEVICE_IP = deviceInfo.ip || '';
        process.env.WRAITH_ADAPTER_TYPE = deviceInfo.adapter;
        process.env.WRAITH_ETHERNET_PORT = deviceInfo.port || '';
        process.env.WRAITH_NAND_OVERPASS = this.nandOverpass.boolean ? 'true' : 'false';
        process.env.WRAITH_NAND_ARRAY = JSON.stringify(this.nandOverpass.arrayOfStrings);
        process.env.WRAITH_NAND_REGEX = this.nandOverpass.regex;
        process.env.WRAITH_NAND_INT = String(this.nandOverpass.int);
        process.env.WRAITH_NAND_FLOAT = String(this.nandOverpass.float);
        process.env.WRAITH_ADMIN_PASS = this.adminPass;

        // Update SeedGate connections JSON using MAC mapper
        await this.updateSeedGateConnections(deviceInfo);

        // Unblock soft layer using admin pass
        await this.unblockSoftLayer();

        // Start keep-alive loop
        this.startKeepAlive();

        // Vemex connection registration
        if (this.mirrorManager) {
            await this.mirrorManager.applyPackageToDevice(
                'wraith_latch',
                '1.0.0',
                'wraith'
            );
        }

        console.log(`[Latch] Latched successfully to ${deviceInfo.mac}`);
        console.log(`[Latch] Adapter: ${deviceInfo.adapter}`);
        console.log(`[Latch] Port: ${deviceInfo.port || 'N/A'}`);
        console.log(`[Latch] IP: ${deviceInfo.ip || 'N/A'}`);
        console.log(`[Latch] NAND overpass: ${this.nandOverpass.string}`);
        console.log(`[Latch] Ethernet bootstrap: ${this.nandOverpass.config.ethernet_bootstrap}`);
        console.log(`[Latch] USB-C adapter: ${this.nandOverpass.config.usb_c_adapter}`);
        console.log(`[Latch] Auto-latch: ${this.nandOverpass.config.auto_latch}`);
        console.log(`[Latch] Keep-alive: ACTIVE`);
        console.log(`[Latch] Soft layer: ${this.softLayerUnblocked ? 'UNBLOCKED' : 'BLOCKED'}`);

        return {
            latched: true,
            mac: deviceInfo.mac,
            ip: deviceInfo.ip,
            adapter: deviceInfo.adapter,
            port: deviceInfo.port,
            nandOverpass: this.nandOverpass,
            keepAlive: true,
            softLayerUnblocked: this.softLayerUnblocked
        };
    }

    async unblockSoftLayer() {
        if (this.softLayerUnblocked) return;
        
        try {
            // Use Vemex integration to configure soft-layer unblocking
            const { execAsync } = require('child_process');
            const util = require('util');
            const exec = util.promisify(execAsync);
            
            // Unblock via admin pass privilege
            const unblockScript = `
import sys
sys.path.insert(0, 'Vemex')
try:
    from seedgate_integration import SeedGateIntegration
    from pathlib import Path
    
    integration = SeedGateIntegration(Path('.'))
    integration.config['admin_pass'] = '${this.adminPass}'
    integration.config['soft_layer_unblocked'] = True
    integration.config['mac_mapper_active'] = True
    integration._save_data()
    print('SOFT_LAYER_UNBLOCKED')
except Exception as e:
    print(f'SOFT_LAYER_UNBLOCK_FAILED: {e}')
`;
            
            try {
                const { stdout } = await exec(`python3 -c "${unblockScript.replace(/"/g, '\\"')}" 2>/dev/null || echo 'SOFT_LAYER_UNBLOCK_FAILED'`);
                if (stdout.includes('SOFT_LAYER_UNBLOCKED')) {
                    this.softLayerUnblocked = true;
                    console.log('[Latch] Soft layer UNBLOCKED via admin pass');
                } else {
                    console.log(`[Latch] Soft layer unblock result: ${stdout.trim()}`);
                }
            } catch (e) {
                // Try direct file manipulation as fallback
                await this.unblockSoftLayerDirect();
            }
        } catch (e) {
            console.log(`[Latch] Soft layer unblock error: ${e.message}`);
        }
    }

    async unblockSoftLayerDirect() {
        try {
            const configPath = path.join(this.workDir, '.seedgate_config.json');
            let config = {};
            
            if (fs.existsSync(configPath)) {
                config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
            }
            
            config.admin_pass = this.adminPass;
            config.soft_layer_unblocked = true;
            config.mac_mapper_active = true;
            config.unblocked_at = new Date().toISOString();
            config.unblocked_by = 'wraith_latch';
            
            fs.writeFileSync(configPath, JSON.stringify(config, indent=2));
            this.softLayerUnblocked = true;
            console.log('[Latch] Soft layer UNBLOCKED via direct config');
        } catch (e) {
            console.log(`[Latch] Direct unblock failed: ${e.message}`);
        }
    }

    startKeepAlive() {
        if (this.keepAliveInterval) {
            clearInterval(this.keepAliveInterval);
        }
        
        console.log('[Latch] Starting keep-alive loop...');
        this.keepAliveInterval = setInterval(() => this.sendKeepAlive(), 5000);
        this.sendKeepAlive();
    }

    async sendKeepAlive() {
        if (!this.latched || !this.deviceMac) return;
        
        try {
            // Update MAC mapper with latest state
            await this.updateMacMapperState();
            
            // Send keep-alive packet to device
            const keepAliveData = {
                mac: this.deviceMac,
                ip: this.deviceIp,
                timestamp: Date.now(),
                adminPass: this.adminPass,
                softLayerUnblocked: this.softLayerUnblocked,
                connectionState: this.connectionState
            };
            
            // Write keep-alive to SeedGate routing log
            const routingLogPath = path.join(this.workDir, 'SeedGate', 'data', '.seedgate_routing_log.json');
            let routingLog = [];
            
            if (fs.existsSync(routingLogPath)) {
                try {
                    routingLog = JSON.parse(fs.readFileSync(routingLogPath, 'utf8'));
                } catch (e) {
                    routingLog = [];
                }
            }
            
            routingLog.push({
                ...keepAliveData,
                type: 'keep_alive',
                source: 'wraith_latch'
            });
            
            // Keep log size manageable
            if (routingLog.length > 1000) {
                routingLog = routingLog.slice(-500);
            }
            
            fs.writeFileSync(routingLogPath, JSON.stringify(routingLog, indent=2));
            
        } catch (e) {
            console.log(`[Latch] Keep-alive error: ${e.message}`);
        }
    }

    async updateMacMapperState() {
        if (!this.macMapper) return;
        
        // Update current device state in mapper
        if (this.deviceMac && this.macMapper.mappings.has(this.deviceMac)) {
            const mapping = this.macMapper.mappings.get(this.deviceMac);
            mapping.lastSeen = new Date().toISOString();
            mapping.established = true;
            mapping.connectionState = this.connectionState;
            mapping.softLayerUnblocked = this.softLayerUnblocked;
        }
        
        // Persist updated mappings
        await this.persistMacMapper();
    }

    async persistMacMapper() {
        if (!this.macMapper) return;
        
        const connectionsPath = path.join(this.workDir, 'SeedGate', 'data', '.seedgate_connections.json');
        const connections = {};
        
        for (const [mac, mapping] of this.macMapper.mappings) {
            connections[mapping.id] = {
                mac: mapping.mac,
                ip: mapping.ip,
                port: mapping.port,
                established: mapping.established,
                transport: mapping.transport,
                keep_alive: mapping.keepAlive,
                ps4_candidate: mapping.ps4Candidate,
                score: mapping.score,
                timestamp: mapping.timestamp,
                last_seen: mapping.lastSeen,
                connection_state: mapping.connectionState,
                soft_layer_unblocked: mapping.softLayerUnblocked,
                source: 'wraith_mac_mapper'
            };
        }
        
        try {
            fs.writeFileSync(connectionsPath, JSON.stringify(connections, indent=2));
        } catch (e) {
            console.log(`[Latch] Could not persist MAC mapper: ${e.message}`);
        }
    }

    async updateSeedGateConnections(deviceInfo) {
        const connectionsPath = path.join(this.workDir, 'SeedGate', 'data', '.seedgate_connections.json');
        if (!fs.existsSync(connectionsPath)) {
            const parentConnections = path.join(this.workDir, '..', 'SeedGate', 'data', '.seedgate_connections.json');
            if (fs.existsSync(parentConnections)) {
                this.seedgateConnectionsPath = parentConnections;
            } else {
                this.seedgateConnectionsPath = connectionsPath;
            }
        } else {
            this.seedgateConnectionsPath = connectionsPath;
        }

        let connections = {};
        try {
            if (fs.existsSync(this.seedgateConnectionsPath)) {
                connections = JSON.parse(fs.readFileSync(this.seedgateConnectionsPath, 'utf8'));
            }
        } catch (e) {
            connections = {};
        }

        // Use MAC mapper if available for optimized updating
        if (this.macMapper && deviceInfo.mac) {
            const existingId = this.findConnectionIdByMac(connections, deviceInfo.mac);
            if (existingId) {
                // Update existing connection
                connections[existingId] = {
                    ...connections[existingId],
                    mac: deviceInfo.mac,
                    ip: deviceInfo.ip,
                    port: deviceInfo.port,
                    established: true,
                    transport: "network",
                    adapter: deviceInfo.adapter,
                    timestamp: new Date().toISOString(),
                    source: "wraith_latch",
                    keep_alive: true,
                    connection_state: "active",
                    soft_layer_unblocked: this.softLayerUnblocked,
                    admin_pass_verified: true
                };
                
                console.log(`[Latch] Updated existing SeedGate connection: ${existingId}`);
            } else {
                // Add new connection
                const connectionId = `wraith_${deviceInfo.mac.replace(/:/g, '')}`;
                connections[connectionId] = {
                    mac: deviceInfo.mac,
                    ip: deviceInfo.ip,
                    port: deviceInfo.port,
                    established: true,
                    transport: "network",
                    adapter: deviceInfo.adapter,
                    timestamp: new Date().toISOString(),
                    source: "wraith_latch",
                    keep_alive: true,
                    connection_state: "active",
                    soft_layer_unblocked: this.softLayerUnblocked,
                    admin_pass_verified: true,
                    ps4_candidate: true,
                    score: 10,
                    reasons: ["mac_mapper_auto_latch"]
                };
                
                console.log(`[Latch] Added new SeedGate connection: ${connectionId}`);
            }
        } else {
            // Fallback to old behavior
            const connectionId = `wraith_${Date.now()}`;
            connections[connectionId] = {
                mac: deviceInfo.mac,
                ip: deviceInfo.ip,
                port: deviceInfo.port,
                established: true,
                transport: "network",
                adapter: deviceInfo.adapter,
                timestamp: new Date().toISOString(),
                source: "wraith_latch",
                keep_alive: true
            };
            
            console.log(`[Latch] Added fallback SeedGate connection: ${connectionId}`);
        }

        try {
            fs.writeFileSync(this.seedgateConnectionsPath, JSON.stringify(connections, indent=2));
            console.log(`[Latch] SeedGate connections persisted`);
        } catch (e) {
            console.log(`[Latch] Could not update SeedGate connections: ${e.message}`);
        }
    }

    findConnectionIdByMac(connections, mac) {
        for (const [id, conn] of Object.entries(connections)) {
            if (conn.mac && conn.mac.toLowerCase() === mac.toLowerCase()) {
                return id;
            }
        }
        return null;
    }

    unlatch() {
        console.log('[Latch] Unlatching from device...');
        
        this.latched = false;
        this.deviceMac = null;
        this.deviceIp = null;

        delete process.env.WRAITH_LATCHED;
        delete process.env.WRAITH_DEVICE_MAC;
        delete process.env.WRAITH_DEVICE_IP;
        delete process.env.WRAITH_ADAPTER_TYPE;
        delete process.env.WRAITH_ETHERNET_PORT;

        console.log('[Latch] Unlatched');
    }

    updateNandOverpass() {
        if (!this.latched) return;

        this.nandOverpass.boolean = true;
        this.nandOverpass.float = 1.0;
        
        if (this.meta.wraith && this.meta.wraith.nand_overpass) {
            this.meta.wraith.nand_overpass.boolean = this.nandOverpass.boolean;
            this.meta.wraith.nand_overpass.float = this.nandOverpass.float;
        }
    }

    getLatchStatus() {
        return {
            latched: this.latched,
            deviceMac: this.deviceMac,
            deviceIp: this.deviceIp,
            adapterType: this.adapterType,
            ethernetPort: this.ethernetPort,
            connectionState: this.connectionState,
            softLayerUnblocked: this.softLayerUnblocked,
            adminPass: this.adminPass ? 'SET' : 'NONE',
            nandOverpass: this.nandOverpass,
            flashMode: this.flashMode.isFlashMode(),
            wraithDir: this.flashMode.wraithDir,
            iosromDir: this.flashMode.iosromDir,
            vemexActive: this.vemexActive,
            seedgateActive: this.seedgateActive,
            macMapper: this.macMapper ? {
                primary: this.macMapper.primary ? this.macMapper.primary.mac : null,
                keepAliveTargets: this.macMapper.keepAliveTargets,
                fallbacks: this.macMapper.fallbacks.map(f => f.mac),
                mappingCount: this.macMapper.mappings.size
            } : null,
            env: {
                WRAITH_LATCHED: process.env.WRAITH_LATCHED,
                WRAITH_DEVICE_MAC: process.env.WRAITH_DEVICE_MAC,
                WRAITH_DEVICE_IP: process.env.WRAITH_DEVICE_IP,
                WRAITH_ADAPTER_TYPE: process.env.WRAITH_ADAPTER_TYPE,
                WRAITH_ETHERNET_PORT: process.env.WRAITH_ETHERNET_PORT,
                WRAITH_NAND_OVERPASS: process.env.WRAITH_NAND_OVERPASS,
                WRAITH_ADMIN_PASS: process.env.WRAITH_ADMIN_PASS ? 'SET' : 'NONE'
            }
        };
    }

    stop() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
        
        if (this.keepAliveInterval) {
            clearInterval(this.keepAliveInterval);
            this.keepAliveInterval = null;
        }
        
        if (this.seedgateProcess) {
            this.seedgateProcess.kill();
        }
        
        this.unlatch();
        console.log('[Latch] Latching system stopped');
    }
}

// Main entry
async function main() {
    const workDir = process.argv[2] || process.cwd();
    const mode = process.argv[3] || 'run'; // run, status, stop
    
    const latchSystem = new WraithLatchSystem(workDir);
    
    if (mode === 'status') {
        const status = latchSystem.getLatchStatus();
        console.log(JSON.stringify(status, null, 2));
        return;
    }
    
    if (mode === 'stop') {
        latchSystem.stop();
        return;
    }
    
    const result = await latchSystem.initialize();
    console.log('\n[Latch] System initialized');
    console.log(JSON.stringify(result, null, 2));
    
    if (mode === 'run') {
        console.log('\n[Latch] Running... Press Ctrl+C to stop');
        process.on('SIGINT', () => {
            latchSystem.stop();
            process.exit(0);
        });
        
        await new Promise(() => {});
    }
}

main().catch(console.error);

module.exports = { WraithLatchSystem };
