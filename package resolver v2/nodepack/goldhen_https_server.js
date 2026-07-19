#!/usr/bin/env node
/**
 * Wraith GoldHEN HTTPS Endpoint Server
 * HTTPS version for PS4 browser compatibility
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const url = require('url');
const os = require('os');

const SSL_KEY = '/tmp/goldhen.key';
const SSL_CERT = '/tmp/goldhen.crt';

class GoldHENHTTPServer {
    constructor(workDir, port = 8443) {
        this.workDir = workDir;
        this.port = port;
        this.server = null;
        this.running = false;
        
        // GoldHEN paths
        this.goldhenDir = path.join(workDir, 'GoldHEN');
        this.goldhenBin = path.join(this.goldhenDir, 'goldhen.bin');
        this.payloadsDir = path.join(workDir, 'library_mirror', 'payloads');
        
        // Device info - loaded at runtime
        this.deviceMac = null;
        this.deviceIp = null;
        this.receiverMac = null;
        this.senderMac = null;
        
        // Get actual server IP
        this.serverIp = this.getLocalIP();
        
        // Resolve gateway dynamically
        this.gateway = this.resolveGateway();
        
        // Kernel patches
        this.kernelPatches = this.loadKernelPatches();
        
        // Request log
        this.requestLog = [];
    }

    getLocalIP() {
        const interfaces = os.networkInterfaces();
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
        
        for (const name of Object.keys(interfaces)) {
            for (const iface of interfaces[name]) {
                if (iface.family === 'IPv4' && !iface.internal) {
                    return iface.address;
                }
            }
        }
        
        return '127.0.0.1';
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
            console.log(`[HTTPS Server] Already running on port ${this.port}`);
            return;
        }

        if (!fs.existsSync(SSL_KEY) || !fs.existsSync(SSL_CERT)) {
            throw new Error('SSL certificate not found. Generate with: openssl req -x509 -newkey rsa:4096 -keyout /tmp/goldhen.key -out /tmp/goldhen.crt -days 365 -nodes');
        }

        const options = {
            key: fs.readFileSync(SSL_KEY),
            cert: fs.readFileSync(SSL_CERT)
        };

        this.server = https.createServer(options, (req, res) => this.handleRequest(req, res));
        
        this.server.listen(this.port, '0.0.0.0', () => {
            this.running = true;
            console.log(`[HTTPS Server] GoldHEN HTTPS server running on https://${this.serverIp}:${this.port}`);
            console.log(`[HTTPS Server] PS4 browser should navigate to: https://${this.serverIp}:${this.port}`);
        });

        this.server.on('error', (err) => {
            if (err.code === 'EADDRINUSE') {
                console.log(`[HTTPS Server] Port ${this.port} in use, trying ${this.port + 1}`);
                this.port++;
                this.start();
            } else {
                console.error(`[HTTPS Server] Error: ${err.message}`);
            }
        });
    }

    handleRequest(req, res) {
        const parsedUrl = url.parse(req.url, true);
        const pathname = parsedUrl.pathname;
        const query = parsedUrl.query;
        
        this.logRequest(req, pathname, query);
        
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
    <title>GoldHEN PS4</title>
    <style>
        body { 
            font-family: monospace; 
            background: #0a0a0a; 
            color: #00ff00; 
            padding: 20px; 
        }
        .box { 
            border: 2px solid #00ff00; 
            padding: 20px; 
            margin: 10px 0; 
            background: #001100;
        }
        a { 
            color: #00ff00; 
            font-size: 24px; 
            text-decoration: underline;
        }
        button { 
            background: #00ff00; 
            color: #000; 
            border: none; 
            padding: 15px 30px; 
            font-size: 18px; 
            font-family: monospace; 
            cursor: pointer; 
            margin: 10px;
        }
    </style>
</head>
<body>
    <div class="box">
        <h1>GoldHEN v2.4b17.3</h1>
        <p>PS4 Homebrew Enabler</p>
        <p>Server: ${serverUrl}</p>
    </div>
    
    <div class="box">
        <h2>Download Payload</h2>
        <a href="/goldhen.bin">Click here to download goldhen.bin</a>
        <br><br>
        <button onclick="window.location.href='/goldhen.bin'">Download GoldHEN</button>
    </div>
    
    <div class="box">
        <h2>Status</h2>
        <p>Device: ${this.deviceIp}</p>
        <p>Server IP: ${this.serverIp}</p>
        <p>Port: ${this.port}</p>
    </div>
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
            'X-GoldHEN-Version': '2.4b17.3'
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
                serverIp: this.serverIp,
                protocol: 'https'
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
                url: `https://${this.serverIp}:${this.port}`,
                ps4_url: `https://${this.serverIp}:${this.port}`
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
            res.writeHead(302, { 'Location': '/goldhen.bin' });
            res.end();
            return;
        }
        
        this.serveKernelPatches(res);
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
        if (this.requestLog.length > 1000) {
            this.requestLog = this.requestLog.slice(-500);
        }
        
        console.log(`[HTTPS Server] ${req.method} ${pathname} from ${logEntry.ip}`);
    }

    stop() {
        if (this.server) {
            this.server.close();
            this.running = false;
            console.log(`[HTTPS Server] Server stopped on port ${this.port}`);
        }
    }
}

// Main entry
async function main() {
    const workDir = process.argv[2] || process.cwd();
    const port = parseInt(process.argv[3]) || 8443;
    
    const server = new GoldHENHTTPServer(workDir, port);
    server.start();
    
    process.on('SIGINT', () => {
        console.log('\n[HTTPS Server] Shutting down...');
        server.stop();
        process.exit(0);
    });
    
    console.log('[HTTPS Server] Press Ctrl+C to stop');
}

main().catch(err => {
    console.error('[HTTPS Server] Error:', err.message);
    process.exit(1);
});

module.exports = { GoldHENHTTPServer };
