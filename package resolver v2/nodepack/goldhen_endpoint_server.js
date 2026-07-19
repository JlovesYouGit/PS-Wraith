#!/usr/bin/env node
/**
 * Wraith GoldHEN HTTP Endpoint Server
 * Hosts payload and kernel patches for PS4 browser connection
 * Standard PS4 homebrew delivery method
 */

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const url = require('url');
const os = require('os');

const SSL_KEY = '/tmp/goldhen.key';
const SSL_CERT = '/tmp/goldhen.crt';

class GoldHENEndpointServer {
    constructor(workDir, port = 8080) {
        this.workDir = workDir;
        this.port = port;
        this.httpPort = port;
        this.httpsPort = port + 1;
        this.server = null;
        this.httpsServer = null;
        this.running = false;
        
        // GoldHEN paths
        this.goldhenDir = path.join(workDir, 'GoldHEN');
        this.goldhenBin = path.join(this.goldhenDir, 'goldhen.bin');
        this.payloadsDir = path.join(workDir, 'library_mirror', 'payloads');
        
        // Resolve actual payload path - check multiple locations
        this.goldhenBin = this.resolvePayloadPath(workDir);
        
        // Device info - loaded from SeedGate/meta at runtime
        this.deviceMac = null;
        this.deviceIp = null;
        this.receiverMac = null;
        this.senderMac = null;
        
        // Get actual server IP
        this.serverIp = this.getLocalIP();
        
        // Resolve gateway from SeedGate/meta if available
        this.gateway = this.resolveGateway();
        
        // Kernel patches
        this.kernelPatches = this.loadKernelPatches();
        
        // Request log
        this.requestLog = [];
    }

    resolvePayloadPath(workDir) {
        const candidates = [
            path.join(workDir, 'GoldHEN', 'goldhen.bin'),
            path.join(workDir, 'nodepack', 'GoldHEN', 'goldhen.bin'),
            path.join(workDir, 'library_mirror', 'payloads', 'goldhen.bin'),
            path.join(workDir, 'nodepack', 'library_mirror', 'payloads', 'goldhen.bin'),
            '/Users/u/Desktop/PS-enhance/GoldHEN-2.4b17.3/goldhen.bin'
        ];
        
        for (const candidate of candidates) {
            if (fs.existsSync(candidate)) {
                console.log(`[Server] Found payload at: ${candidate}`);
                return candidate;
            }
        }
        
        console.log(`[Server] Warning: goldhen.bin not found in any expected location`);
        console.log(`[Server] Checked: ${candidates.join(', ')}`);
        return path.join(workDir, 'GoldHEN', 'goldhen.bin');
    }

    getLocalIP() {
        const interfaces = os.networkInterfaces();
        
        // Priority: en0, then en1, then any non-internal IPv4
        const priorityInterfaces = ['en0', 'en1', 'eth0', 'wlan0'];
        
        for (const name of priorityInterfaces) {
            if (interfaces[name]) {
                for (const iface of interfaces[name]) {
                    if (iface.family === 'IPv4' && !iface.internal) {
                        return iface.address;
                    }
                }
            }
        }
        
        // Fallback: any non-internal IPv4
        for (const name of Object.keys(interfaces)) {
            for (const iface of interfaces[name]) {
                if (iface.family === 'IPv4' && !iface.internal) {
                    return iface.address;
                }
            }
        }
        
        return '127.0.0.1';
    }
    
    resolveGateway() {
        try {
            const metaPath = path.join(this.workDir, 'meta.json');
            if (fs.existsSync(metaPath)) {
                const meta = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
                if (meta.gateway) return meta.gateway;
            }
        } catch (e) {}
        return null;
    }

    loadKernelPatches() {
        const patchesFile = path.join(this.workDir, 'library_mirror', 'kernel_patches.json');
        if (fs.existsSync(patchesFile)) {
            try {
                const data = JSON.parse(fs.readFileSync(patchesFile, 'utf8'));
                return data.patches || [];
            } catch (e) {
                return [];
            }
        }
        
        // Default patches
        return [
            { name: 'sys_dynlib_dlsym', description: 'Allow dynamic library symbol resolution', critical: true },
            { name: 'debug_settings', description: 'Enable debug settings menu', critical: true },
            { name: 'homebrew_enabler', description: 'Enable homebrew execution', critical: true },
            { name: 'fw_update_block', description: 'Block firmware updates', critical: false },
            { name: 'screenshot_enable', description: 'Enable screenshots in all games', critical: false },
            { name: 'rest_mode_support', description: 'Enable rest mode for homebrew', critical: false },
            { name: 'external_hdd_support', description: 'Enable external HDD support', critical: false },
            { name: 'vr_support', description: 'Enable VR support for homebrew', critical: false },
            { name: 'remote_pkg_install', description: 'Enable remote package installation', critical: false },
            { name: 'debug_trophies', description: 'Enable debug trophy support', critical: false },
            { name: 'remote_play_enabler', description: 'Enable remote play enhancements', critical: false },
            { name: 'plugin_support', description: 'Enable plugin loading', critical: false },
            { name: 'fps_counter', description: 'Enable FPS counter overlay', critical: false },
            { name: 'scanlines_overlay', description: 'Enable scanlines overlay', critical: false },
            { name: 'cheat_menu', description: 'Enable cheat menu', critical: false }
        ];
    }

    getRoutes() {
        return {
            senderMac: this.senderMac,
            receiverMac: this.receiverMac,
            deviceMac: this.deviceMac,
            deviceIp: this.deviceIp,
            lanMac: this.receiverMac,
            gateway: this.gateway || '192.168.0.1',
            interface: 'en0',
            adapter: 'USB-C_Ethernet',
            adminPass: 'jj'
        };
    }

    start() {
        if (this.running) {
            console.log(`[Server] Already running on ports ${this.httpPort} (HTTP) and ${this.httpsPort} (HTTPS)`);
            return;
        }

        // HTTP server
        this.server = http.createServer((req, res) => this.handleRequest(req, res));
        
        this.server.listen(this.httpPort, '0.0.0.0', () => {
            console.log(`[Server] HTTP server running on http://${this.serverIp}:${this.httpPort}`);
            console.log(`[Server] PS4 browser can use: http://${this.serverIp}:${this.httpPort}`);
        });

        this.server.on('error', (err) => {
            if (err.code === 'EADDRINUSE') {
                console.log(`[Server] HTTP port ${this.httpPort} in use, trying ${this.httpPort + 1}`);
                this.httpPort++;
                this.start();
            } else {
                console.error(`[Server] Error: ${err.message}`);
            }
        });

        // HTTPS server
        this.httpsServer = https.createServer({
            key: fs.readFileSync(SSL_KEY),
            cert: fs.readFileSync(SSL_CERT)
        }, (req, res) => this.handleRequest(req, res));
        
        this.httpsServer.listen(this.httpsPort, '0.0.0.0', () => {
            this.running = true;
            console.log(`[Server] HTTPS server running on https://${this.serverIp}:${this.httpsPort}`);
            console.log(`[Server] PS4 browser can use: https://${this.serverIp}:${this.httpsPort}`);
        });

        this.httpsServer.on('error', (err) => {
            if (err.code === 'EADDRINUSE') {
                console.log(`[Server] HTTPS port ${this.httpsPort} in use, trying ${this.httpsPort + 1}`);
                this.httpsPort++;
                this.start();
            } else {
                console.error(`[Server] HTTPS Error: ${err.message}`);
            }
        });
    }

    handleRequest(req, res) {
        const parsedUrl = url.parse(req.url, true);
        const pathname = parsedUrl.pathname;
        const query = parsedUrl.query;
        
        // Log request
        this.logRequest(req, pathname, query);
        
        // Route handling
        switch (pathname) {
            case '/':
            case '/index.html':
                this.serveIndex(res);
                break;
                
            case '/goldhen.bin':
                this.servePayload(res);
                break;
                
            case '/kernel_patches':
            case '/kernel_patches.json':
                this.serveKernelPatches(res);
                break;
                
            case '/routes':
            case '/routes.json':
                this.serveRoutes(res);
                break;
                
            case '/status':
                this.serveStatus(res);
                break;
                
            case '/deploy':
                this.handleDeploy(req, res);
                break;
                
            default:
                this.serve404(res);
        }
    }

    serveIndex(res) {
        const serverUrl = `https://${this.serverIp}:${this.port}`;
        
        const html = `<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>GoldHEN</title>
</head>
<body style="background:#000;color:#0f0;font-family:monospace;padding:20px;">
    <h1>GoldHEN PS4</h1>
    <p>Server: ${serverUrl}</p>
    <p><a href="/goldhen.bin" style="color:#0f0;font-size:24px;">DOWNLOAD goldhen.bin</a></p>
    <p>Device: ${this.deviceIp}</p>
</body>
</html>`;
        
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(html);
    }

    servePayload(res) {
        if (!fs.existsSync(this.goldhenBin)) {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Payload not found' }));
            return;
        }
        
        const payload = fs.readFileSync(this.goldhenBin);
        const stats = fs.statSync(this.goldhenBin);
        
        res.writeHead(200, {
            'Content-Type': 'application/octet-stream',
            'Content-Length': stats.size,
            'Content-Disposition': 'attachment; filename="goldhen.bin"',
            'X-GoldHEN-Version': '2.4b17.3',
            'X-GoldHEN-SHA256': this.getFileHash(this.goldhenBin)
        });
        res.end(payload);
    }

    serveKernelPatches(res) {
        const patches = {
            timestamp: new Date().toISOString(),
            deviceMac: this.deviceMac,
            deviceIp: this.deviceIp,
            senderMac: this.senderMac,
            receiverMac: this.receiverMac,
            adminPass: 'jj',
            patches: this.kernelPatches,
            routes: this.getRoutes()
        };
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(patches, null, 2));
    }

    serveRoutes(res) {
        const routes = this.getRoutes();
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(routes, null, 2));
    }

    serveStatus(res) {
        const status = {
            server: {
                running: this.running,
                port: this.port,
                uptime: process.uptime(),
                serverIp: this.serverIp
            },
            device: {
                mac: this.deviceMac,
                ip: this.deviceIp,
                senderMac: this.senderMac,
                receiverMac: this.receiverMac
            },
            goldhen: {
                payload_exists: fs.existsSync(this.goldhenBin),
                version: '2.4b17.3',
                patches_count: this.kernelPatches.length
            },
            connection: {
                url: `http://${this.serverIp}:${this.port}`,
                ps4_url: `http://${this.serverIp}:${this.port}`,
                note: 'Use this URL in PS4 browser'
            },
            recent_requests: this.requestLog.slice(-10)
        };
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(status, null, 2));
    }

    handleDeploy(req, res) {
        const parsedUrl = url.parse(req.url, true);
        const query = parsedUrl.query;
        
        if (query.action === 'payload') {
            // Redirect to payload download
            res.writeHead(302, { 'Location': '/goldhen.bin' });
            res.end();
            return;
        }
        
        if (query.action === 'patches') {
            // Return kernel patches
            this.serveKernelPatches(res);
            return;
        }
        
        // Default deploy response
        const deployInfo = {
            status: 'ready',
            message: 'GoldHEN deployment server ready',
            device: {
                mac: this.deviceMac,
                ip: this.deviceIp,
                senderMac: this.senderMac,
                receiverMac: this.receiverMac
            },
            connection: {
                server_ip: this.serverIp,
                port: this.port,
                url: `http://${this.serverIp}:${this.port}`
            },
            endpoints: {
                payload: '/goldhen.bin',
                patches: '/kernel_patches',
                routes: '/routes',
                status: '/status'
            },
            instructions: [
                '1. Connect PS4 browser to this server',
                `2. Navigate to: http://${this.serverIp}:${this.port}`,
                '3. Click "Deploy GoldHEN" button',
                '4. Payload will be downloaded automatically'
            ]
        };
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(deployInfo, null, 2));
    }

    serve404(res) {
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end('<h1>404 - Not Found</h1><p>GoldHEN PS4 Homebrew Enabler</p>');
    }

    logRequest(req, pathname, query) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            ip: req.connection.remoteAddress,
            method: req.method,
            path: pathname,
            query: query,
            userAgent: req.headers['user-agent']
        };
        
        this.requestLog.push(logEntry);
        
        // Keep log size manageable
        if (this.requestLog.length > 1000) {
            this.requestLog = this.requestLog.slice(-500);
        }
        
        // Log to console
        console.log(`[Server] ${req.method} ${pathname} from ${logEntry.ip}`);
    }

    getFileHash(filePath) {
        try {
            const crypto = require('crypto');
            const hash = crypto.createHash('sha256');
            hash.update(fs.readFileSync(filePath));
            return hash.digest('hex').substring(0, 16);
        } catch (e) {
            return 'unknown';
        }
    }

    stop() {
        if (this.server) {
            this.server.close();
        }
        if (this.httpsServer) {
            this.httpsServer.close();
        }
        this.running = false;
        console.log(`[Server] Servers stopped on HTTP ${this.httpPort} and HTTPS ${this.httpsPort}`);
    }
}

// Main entry
async function main() {
    const workDir = process.argv[2] || process.cwd();
    const port = parseInt(process.argv[3]) || 8080;
    
    const server = new GoldHENEndpointServer(workDir, port);
    
    // Start server
    server.start();
    
    // Handle shutdown
    process.on('SIGINT', () => {
        console.log('\n[Server] Shutting down...');
        server.stop();
        process.exit(0);
    });
    
    // Keep running
    console.log('[Server] Press Ctrl+C to stop');
}

main().catch(err => {
    console.error('[Server] Error:', err.message);
    process.exit(1);
});

module.exports = { GoldHENEndpointServer };
