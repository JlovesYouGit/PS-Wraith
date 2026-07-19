#!/usr/bin/env node
/**
 * Wraith Flash Mode - Direct operation in wraith directory
 * Integrates package resolver v2 with wraithps4-serv-backup-performance booster
 * Integrates IOsrom NAND/image handling for device updates
 * Flash mode: fast, direct, bypasses standard checks
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { WraithMirrorManager } = require('./wraith_mirror_manager');

class WraithFlashMode {
    constructor(workDir) {
        this.workDir = workDir;
        this.wraithDir = this.detectWraithDirectory();
        this.iosromDir = this.detectIOsromDirectory();
        this.goldhenDir = this.detectGoldHENDirectory();
        this.flashActive = false;
        this.rj45Connected = false;
        this.engraveLayers = 34;
        this.performanceBoost = false;
        this.mirrorManager = null;
        this.imageBridge = null;
    }

    detectWraithDirectory() {
        const wraithIndicators = [
            'boost_engine.py',
            'hardware_interface.py',
            'pragma_logic.py',
            'storage_manager.py',
            'buffer_manager.py',
            'network_protection.py',
            'interleave_manager.py',
            'market_engine.py',
            'persistence_manager.py',
            'main.py'
        ];

        for (const file of wraithIndicators) {
            if (fs.existsSync(path.join(this.workDir, file))) {
                return this.workDir;
            }
        }

        const parentDir = path.join(this.workDir, '..');
        for (const file of wraithIndicators) {
            if (fs.existsSync(path.join(parentDir, file))) {
                return parentDir;
            }
        }

        return null;
    }

    detectIOsromDirectory() {
        const iosromIndicators = [
            'direct_nand_flasher.py',
            'WRITE_NAND_DIRECT.py',
            'FINAL_NAND_FLASH.py',
            'proper_nand_writer.py',
            'img3tool.py',
            'img4tool.py'
        ];

        // Check current directory
        for (const file of iosromIndicators) {
            if (fs.existsSync(path.join(this.workDir, file))) {
                return this.workDir;
            }
        }

        // Check sibling IOsrom directory
        const siblingDir = path.join(this.workDir, '..', 'IOsrom');
        for (const file of iosromIndicators) {
            if (fs.existsSync(path.join(siblingDir, file))) {
                return siblingDir;
            }
        }

        // Check parent's sibling
        const parentSibling = path.join(this.workDir, '..', '..', 'IOsrom');
        for (const file of iosromIndicators) {
            if (fs.existsSync(path.join(parentSibling, file))) {
                return parentSibling;
            }
        }

        return null;
    }

    detectGoldHENDirectory() {
        const goldhenIndicators = [
            'goldhen.bin',
            'config.ini',
            'cheats'
        ];

        // Check current directory
        for (const file of goldhenIndicators) {
            if (fs.existsSync(path.join(this.workDir, 'GoldHEN', file))) {
                return path.join(this.workDir, 'GoldHEN');
            }
        }

        // Check GoldHEN directory in workDir
        const goldhenDir = path.join(this.workDir, 'GoldHEN');
        if (fs.existsSync(goldhenDir) && fs.existsSync(path.join(goldhenDir, 'goldhen.bin'))) {
            return goldhenDir;
        }

        // Check sibling directory
        const siblingDir = path.join(this.workDir, '..', 'GoldHEN');
        if (fs.existsSync(siblingDir) && fs.existsSync(path.join(siblingDir, 'goldhen.bin'))) {
            return siblingDir;
        }

        return null;
    }

    isGoldHENAvailable() {
        return this.goldhenDir !== null;
    }

    isFlashMode() {
        return this.wraithDir !== null && this.flashActive;
    }

    isIOsromAvailable() {
        return this.iosromDir !== null;
    }

    activateFlash() {
        this.flashActive = true;
        this.rj45Connected = this.detectRJ45();
        this.performanceBoost = true;
        
        console.log('[FLASH] Wraith Flash Mode ACTIVATED');
        console.log(`[FLASH] Wraith directory: ${this.wraithDir}`);
        console.log(`[FLASH] IOsrom directory: ${this.iosromDir}`);
        console.log(`[FLASH] GoldHEN directory: ${this.goldhenDir}`);
        console.log(`[FLASH] GoldHEN available: ${this.isGoldHENAvailable()}`);
        console.log(`[FLASH] RJ45 connected: ${this.rj45Connected}`);
        console.log(`[FLASH] Performance boost: ${this.performanceBoost}`);
        
        // Initialize mirror manager
        this.mirrorManager = new WraithMirrorManager(this.workDir, this);
        
        return {
            active: true,
            wraithDir: this.wraithDir,
            iosromDir: this.iosromDir,
            goldhenDir: this.goldhenDir,
            goldhenAvailable: this.isGoldHENAvailable(),
            rj45: this.rj45Connected,
            boost: this.performanceBoost
        };
    }

    detectRJ45() {
        try {
            const { stdout } = require('child_process').execSync(
                "lsof -i -P | grep LISTEN | head -1 | awk '{print $2}' || echo ''",
                { encoding: 'utf8' }
            );
            const pid = stdout.trim();
            return !!pid;
        } catch (e) {
            return true;
        }
    }

    getWraithComponents() {
        if (!this.wraithDir) return null;

        return {
            boostEngine: path.join(this.wraithDir, 'boost_engine.py'),
            hardwareInterface: path.join(this.wraithDir, 'hardware_interface.py'),
            pragmaLogic: path.join(this.wraithDir, 'pragma_logic.py'),
            storageManager: path.join(this.wraithDir, 'storage_manager.py'),
            bufferManager: path.join(this.wraithDir, 'buffer_manager.py'),
            networkProtection: path.join(this.wraithDir, 'network_protection.py'),
            interleaveManager: path.join(this.wraithDir, 'interleave_manager.py'),
            marketEngine: path.join(this.wraithDir, 'market_engine.py'),
            persistenceManager: path.join(this.wraithDir, 'persistence_manager.py'),
            main: path.join(this.wraithDir, 'main.py')
        };
    }

    getIOsromComponents() {
        if (!this.iosromDir) return null;

        return {
            directNandFlasher: path.join(this.iosromDir, 'direct_nand_flasher.py'),
            writeNandDirect: path.join(this.iosromDir, 'WRITE_NAND_DIRECT.py'),
            finalNandFlash: path.join(this.iosromDir, 'FINAL_NAND_FLASH.py'),
            properNandWriter: path.join(this.iosromDir, 'proper_nand_writer.py'),
            img3tool: path.join(this.iosromDir, 'img3tool.py'),
            img4tool: path.join(this.iosromDir, 'img4tool.py'),
            filesystemWriter: path.join(this.iosromDir, 'filesystem_writer.py'),
            checkIpswIntegrity: path.join(this.iosromDir, 'check_ipsw_integrity.py'),
            extractIpswParts: path.join(this.iosromDir, 'extract_ipsw_parts.py')
        };
    }

    async runWraithBoost() {
        if (!this.flashActive) {
            console.log('[FLASH] Flash mode not active. Call activateFlash() first.');
            return null;
        }

        const components = this.getWraithComponents();
        if (!components) {
            console.log('[FLASH] No wraith components found.');
            return null;
        }

        console.log('[FLASH] Running wraith boost sequence...');
        
        const boostData = {
            gramshasEngine: components.boostEngine,
            diskLayer: this.engraveLayers,
            rj45Active: this.rj45Connected,
            performanceHash: this.generatePerformanceHash()
        };

        return boostData;
    }

    async runDeviceImageBridge() {
        if (!this.flashActive) {
            console.log('[FLASH] Flash mode not active.');
            return null;
        }

        console.log('[FLASH] Running device image bridge...');
        
        const imageBridgeScript = path.join(__dirname, 'wraith_image_bridge.py');
        const args = [imageBridgeScript, this.workDir];
        
        if (this.rj45Connected) {
            args.push('--mirror');
        }

        return new Promise((resolve, reject) => {
            const proc = spawn('python3', args, {
                stdio: ['pipe', 'pipe', 'pipe']
            });

            let output = '';
            proc.stdout.on('data', (data) => {
                output += data.toString();
            });

            proc.stderr.on('data', (data) => {
                console.log('[ImageBridge]', data.toString().trim());
            });

            proc.on('close', (code) => {
                if (code === 0) {
                    resolve(output.trim());
                } else {
                    reject(new Error(`Image bridge exited with code ${code}`));
                }
            });
        });
    }

    async runMirrorSync() {
        if (!this.mirrorManager) {
            this.mirrorManager = new WraithMirrorManager(this.workDir, this);
        }

        const result = await this.mirrorManager.initialize();
        if (result.deviceConnected) {
            await this.mirrorManager.syncDeviceLibrary();
        }

        return this.mirrorManager.getStatus();
    }

    async runIOsromFlash(ipswPath) {
        if (!this.iosromDir) {
            console.log('[FLASH] IOsrom directory not found');
            return null;
        }

        console.log(`[FLASH] Running IOsrom flash with: ${ipswPath}`);
        
        const finalNandFlash = path.join(this.iosromDir, 'FINAL_NAND_FLASH.py');
        
        return new Promise((resolve, reject) => {
            const proc = spawn('python3', [finalNandFlash], {
                stdio: ['pipe', 'pipe', 'pipe'],
                cwd: this.iosromDir
            });

            let output = '';
            proc.stdout.on('data', (data) => {
                output += data.toString();
            });

            proc.stderr.on('data', (data) => {
                console.log('[IOsrom]', data.toString().trim());
            });

            proc.on('close', (code) => {
                if (code === 0) {
                    resolve(output.trim());
                } else {
                    reject(new Error(`IOsrom flash exited with code ${code}`));
                }
            });
        });
    }

    async runGoldHENDeploy(targetIp) {
        if (!this.goldhenDir) {
            console.log('[FLASH] GoldHEN directory not found');
            return null;
        }

        const goldhenBin = path.join(this.goldhenDir, 'goldhen.bin');
        if (!fs.existsSync(goldhenBin)) {
            console.log('[FLASH] GoldHEN binary not found');
            return null;
        }

        console.log(`[FLASH] Deploying GoldHEN payload...`);
        console.log(`[FLASH] Payload: ${goldhenBin}`);
        
        const args = [path.join(__dirname, 'goldhen_integration.py'), this.workDir, '--deploy'];
        if (targetIp) {
            args.push('--ip', targetIp);
        }

        return new Promise((resolve, reject) => {
            const proc = spawn('python3', args, {
                stdio: ['pipe', 'pipe', 'pipe']
            });

            let output = '';
            proc.stdout.on('data', (data) => {
                output += data.toString();
            });

            proc.stderr.on('data', (data) => {
                console.log('[GoldHEN]', data.toString().trim());
            });

            proc.on('close', (code) => {
                if (code === 0) {
                    resolve(output.trim());
                } else {
                    reject(new Error(`GoldHEN deploy exited with code ${code}`));
                }
            });
        });
    }

    async runGoldHENConfig() {
        if (!this.goldhenDir) {
            console.log('[FLASH] GoldHEN directory not found');
            return null;
        }

        const goldhenIntegration = path.join(__dirname, 'goldhen_integration.py');
        
        return new Promise((resolve, reject) => {
            const proc = spawn('python3', [goldhenIntegration, this.workDir, '--config'], {
                stdio: ['pipe', 'pipe', 'pipe']
            });

            let output = '';
            proc.stdout.on('data', (data) => {
                output += data.toString();
            });

            proc.stderr.on('data', (data) => {
                console.log('[GoldHEN]', data.toString().trim());
            });

            proc.on('close', (code) => {
                if (code === 0) {
                    resolve(output.trim());
                } else {
                    reject(new Error(`GoldHEN config exited with code ${code}`));
                }
            });
        });
    }

    async runGoldHENCheats() {
        if (!this.goldhenDir) {
            console.log('[FLASH] GoldHEN directory not found');
            return null;
        }

        const goldhenIntegration = path.join(__dirname, 'goldhen_integration.py');
        
        return new Promise((resolve, reject) => {
            const proc = spawn('python3', [goldhenIntegration, this.workDir, '--cheats'], {
                stdio: ['pipe', 'pipe', 'pipe']
            });

            let output = '';
            proc.stdout.on('data', (data) => {
                output += data.toString();
            });

            proc.stderr.on('data', (data) => {
                console.log('[GoldHEN]', data.toString().trim());
            });

            proc.on('close', (code) => {
                if (code === 0) {
                    resolve(output.trim());
                } else {
                    reject(new Error(`GoldHEN cheats exited with code ${code}`));
                }
            });
        });
    }

    generatePerformanceHash() {
        const crypto = require('crypto');
        const seed = `wraith_flash_${Date.now()}_${this.engraveLayers}`;
        return crypto.createHash('sha256').update(seed).digest('hex').substring(0, 16);
    }

    getFlashResolutionConfig() {
        if (!this.isFlashMode()) {
            return null;
        }

        return {
            mode: 'flash',
            wraithIntegration: true,
            iosromIntegration: !!this.iosromDir,
            skipValidation: true,
            fastTrack: true,
            engraveLayers: this.engraveLayers,
            rj45Active: this.rj45Connected,
            performanceOptimized: true,
            nandDirectWrite: true,
            imageBridge: true,
            mirrorSync: true
        };
    }

    getFullStatus() {
        return {
            flashMode: this.isFlashMode(),
            wraithDir: this.wraithDir,
            iosromDir: this.iosromDir,
            goldhenDir: this.goldhenDir,
            goldhenAvailable: this.isGoldHENAvailable(),
            rj45Connected: this.rj45Connected,
            performanceBoost: this.performanceBoost,
            engraveLayers: this.engraveLayers,
            mirrorManager: !!this.mirrorManager,
            mirrorStatus: this.mirrorManager ? this.mirrorManager.getStatus() : null
        };
    }
}

module.exports = { WraithFlashMode };

