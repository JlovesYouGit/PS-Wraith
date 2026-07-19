#!/usr/bin/env node
/**
 * Wraith Mirror Manager - Library Mirror Operations
 * Manages device image mirror, package updates, and library synchronization
 * Integrates with IOsrom NAND/image handling via wraith_image_bridge.py
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const util = require('util');
const execAsync = util.promisify(require('child_process').exec);

class WraithMirrorManager {
    constructor(workDir, flashMode = null) {
        this.workDir = workDir;
        this.flashMode = flashMode;
        this.mirrorDir = path.join(workDir, 'library_mirror');
        this.imageBridge = null;
        this.deviceMirror = null;
        this.syncedPackages = new Map();
        this.rj45Active = false;
        
        this.ensureMirrorDir();
    }

    ensureMirrorDir() {
        if (!fs.existsSync(this.mirrorDir)) {
            fs.mkdirSync(this.mirrorDir, { recursive: true });
        }
        
        // Create subdirectories
        const subdirs = [
            'images',
            'packages',
            'nand',
            'boot',
            'system',
            'frameworks',
            'applications'
        ];
        
        for (const dir of subdirs) {
            const fullPath = path.join(this.mirrorDir, dir);
            if (!fs.existsSync(fullPath)) {
                fs.mkdirSync(fullPath, { recursive: true });
            }
        }
    }

    async initialize() {
        console.log('[Mirror] Initializing Wraith Mirror Manager...');
        
        // Initialize Python image bridge
        this.imageBridge = await this.spawnImageBridge();
        
        // Detect device connection
        this.rj45Active = await this.detectDeviceConnection();
        
        console.log(`[Mirror] Device connected: ${this.rj45Active}`);
        console.log(`[Mirror] Mirror directory: ${this.mirrorDir}`);
        
        return {
            initialized: true,
            deviceConnected: this.rj45Active,
            mirrorDir: this.mirrorDir
        };
    }

    spawnImageBridge() {
        return new Promise((resolve, reject) => {
            const bridgeScript = path.join(__dirname, 'wraith_image_bridge.py');
            const proc = spawn('python3', [bridgeScript, this.workDir, '--mirror'], {
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

            // Timeout after 10 seconds
            setTimeout(() => {
                proc.kill();
                reject(new Error('Image bridge initialization timeout'));
            }, 10000);
        });
    }

    async detectDeviceConnection() {
        try {
            const { stdout } = await execAsync('irecovery -c getenv 2>/dev/null || echo "NOT_CONNECTED"');
            return stdout.includes('NOT_CONNECTED') === false;
        } catch (e) {
            return false;
        }
    }

    // Get device image from connection
    async getDeviceImage(componentName) {
        if (!this.rj45Active) {
            console.log('[Mirror] No device connected');
            return null;
        }

        console.log(`[Mirror] Getting device image: ${componentName}`);
        
        try {
            const result = await execAsync(
                `irecovery -c "nand read 0x0 0x100000" -o ${path.join(this.mirrorDir, 'images', componentName)}`
            );
            return path.join(this.mirrorDir, 'images', componentName);
        } catch (e) {
            console.log(`[Mirror] Failed to get image: ${e.message}`);
            return null;
        }
    }

    // Extract IPSW components to mirror
    async extractIPSWComponents(ipswPath) {
        if (!fs.existsSync(ipswPath)) {
            console.log(`[Mirror] IPSW not found: ${ipswPath}`);
            return null;
        }

        console.log(`[Mirror] Extracting IPSW components: ${path.basename(ipswPath)}`);
        
        try {
            const bridgeScript = path.join(__dirname, 'wraith_image_bridge.py');
            const proc = spawn('python3', [bridgeScript, this.workDir, '--extract', ipswPath], {
                stdio: ['pipe', 'pipe', 'pipe']
            });

            let output = '';
            proc.stdout.on('data', (data) => {
                output += data.toString();
            });

            proc.stderr.on('data', (data) => {
                console.log('[Extract]', data.toString().trim());
            });

            await new Promise((resolve, reject) => {
                proc.on('close', (code) => {
                    if (code === 0) resolve(output);
                    else reject(new Error(`Extract failed with code ${code}`));
                });
            });

            // Parse extracted components
            const components = this.parseExtractedComponents();
            console.log(`[Mirror] Extracted ${components.length} components`);
            return components;
        } catch (e) {
            console.log(`[Mirror] Extraction failed: ${e.message}`);
            return null;
        }
    }

    parseExtractedComponents() {
        const components = [];
        const imagesDir = path.join(this.mirrorDir, 'images');
        
        if (!fs.existsSync(imagesDir)) return components;
        
        const files = fs.readdirSync(imagesDir);
        for (const file of files) {
            const filePath = path.join(imagesDir, file);
            const stat = fs.statSync(filePath);
            
            if (stat.isFile()) {
                components.push({
                    name: file,
                    path: filePath,
                    size: stat.size,
                    type: this.detectImageType(file)
                });
            }
        }
        
        return components;
    }

    detectImageType(filename) {
        const ext = path.extname(filename).toLowerCase();
        if (ext === '.img3' || ext === '.img4') return 'firmware';
        if (ext === '.dmg') return 'filesystem';
        if (ext === '.dfu') return 'dfu';
        if (filename.includes('kernel')) return 'kernel';
        if (filename.includes('iboot')) return 'iboot';
        if (filename.includes('llb')) return 'llb';
        return 'unknown';
    }

    // Flash components to device NAND
    async flashToDevice(components) {
        if (!this.rj45Active) {
            console.log('[Mirror] No device connected for flashing');
            return false;
        }

        console.log(`[Mirror] Flashing ${components.length} components to device...`);
        
        try {
            const bridgeScript = path.join(__dirname, 'wraith_image_bridge.py');
            const proc = spawn('python3', [bridgeScript, this.workDir, '--flash-nand'], {
                stdio: ['pipe', 'pipe', 'pipe']
            });

            let output = '';
            proc.stdout.on('data', (data) => {
                output += data.toString();
            });

            proc.stderr.on('data', (data) => {
                console.log('[Flash]', data.toString().trim());
            });

            await new Promise((resolve, reject) => {
                proc.on('close', (code) => {
                    if (code === 0) resolve(output);
                    else reject(new Error(`Flash failed with code ${code}`));
                });
            });

            console.log('[Mirror] Flash complete');
            return true;
        } catch (e) {
            console.log(`[Mirror] Flash failed: ${e.message}`);
            return false;
        }
    }

    // Generate Makefile for device transfer
    async generateTransferMakefile() {
        console.log('[Mirror] Generating transfer Makefile...');
        
        try {
            const bridgeScript = path.join(__dirname, 'wraith_image_bridge.py');
            const proc = spawn('python3', [bridgeScript, this.workDir, '--makefile'], {
                stdio: ['pipe', 'pipe', 'pipe']
            });

            await new Promise((resolve, reject) => {
                proc.on('close', (code) => {
                    if (code === 0) resolve();
                    else reject(new Error(`Makefile generation failed with code ${code}`));
                });
            });

            const makefilePath = path.join(this.workDir, 'wraith_transfer.mk');
            if (fs.existsSync(makefilePath)) {
                console.log(`[Mirror] Generated: ${makefilePath}`);
                return makefilePath;
            }
        } catch (e) {
            console.log(`[Mirror] Makefile generation failed: ${e.message}`);
        }
        
        return null;
    }

    // Sync device library to mirror
    async syncDeviceLibrary() {
        if (!this.rj45Active) {
            console.log('[Mirror] No device connected for sync');
            return false;
        }

        console.log('[Mirror] Syncing device library...');
        
        try {
            const bridgeScript = path.join(__dirname, 'wraith_image_bridge.py');
            const proc = spawn('python3', [bridgeScript, this.workDir, '--mirror'], {
                stdio: ['pipe', 'pipe', 'pipe']
            });

            await new Promise((resolve, reject) => {
                proc.on('close', (code) => {
                    if (code === 0) resolve();
                    else reject(new Error(`Mirror sync failed with code ${code}`));
                });
            });

            console.log('[Mirror] Library sync complete');
            return true;
        } catch (e) {
            console.log(`[Mirror] Sync failed: ${e.message}`);
            return false;
        }
    }

    // Apply package update to device via mirror
    async applyPackageToDevice(packageName, version, language) {
        if (!this.rj45Active) {
            console.log('[Mirror] No device connected');
            return false;
        }

        console.log(`[Mirror] Applying package: ${packageName}@${version} (${language})`);
        
        // Add to synced packages
        this.syncedPackages.set(`${language}:${packageName}`, version);
        
        // Write package manifest to mirror
        const manifest = {
            name: packageName,
            version: version,
            language: language,
            timestamp: Date.now(),
            rj45Active: this.rj45Active
        };
        
        const manifestPath = path.join(this.mirrorDir, 'packages', `${packageName}.json`);
        fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
        
        return true;
    }

    // Get mirror status
    getStatus() {
        const imagesDir = path.join(this.mirrorDir, 'images');
        const packagesDir = path.join(this.mirrorDir, 'packages');
        
        let imageCount = 0;
        let packageCount = 0;
        
        if (fs.existsSync(imagesDir)) {
            imageCount = fs.readdirSync(imagesDir).length;
        }
        if (fs.existsSync(packagesDir)) {
            packageCount = fs.readdirSync(packagesDir).length;
        }
        
        return {
            initialized: !!this.imageBridge,
            deviceConnected: this.rj45Active,
            mirrorDir: this.mirrorDir,
            imageCount,
            packageCount,
            syncedPackages: this.syncedPackages.size
        };
    }
}

module.exports = { WraithMirrorManager };
