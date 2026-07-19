#!/usr/bin/env node
/**
 * CONTROL CENTER - Single Entry Point
 * 
 * This is the ONLY file you need to interact with.
 * Run: node CONTROL_CENTER.js <command>
 * 
 * Available Commands:
 *   fix       - Fix all package issues in current directory
 *   interactive - Interactive terminal mode
 *   watch     - Watch for changes and auto-fix
 *   status    - Check current status
 *   help      - Show this help
 */

const { spawn, exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// Simple colored output
const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    red: '\x1b[31m',
    blue: '\x1b[34m'
};

function log(msg, color = 'reset') {
    console.log(colors[color] + msg + colors.reset);
}

// Main command router
async function main() {
    const command = process.argv[2] || 'help';
    const targetDir = process.argv[3] || '.';

    log('\n=== Package Resolver Control Center ===\n', 'blue');

    switch(command) {
        case 'fix':
            await runFix(targetDir);
            break;
        case 'interactive':
        case 'i':
            await runInteractive(targetDir);
            break;
        case 'watch':
        case 'w':
            await runWatch(targetDir);
            break;
        case 'status':
        case 's':
            await showStatus(targetDir);
            break;
        case 'python':
        case 'py':
            await runPythonBridge(targetDir);
            break;
        case 'flash':
        case 'f':
            await runFlashMode(targetDir);
            break;
        case 'wraith':
        case 'wr':
            await runWraithMode(targetDir);
            break;
        case 'mirror':
        case 'm':
            await runMirrorSync(targetDir);
            break;
        case 'bridge':
        case 'b':
            await runImageBridge(targetDir);
            break;
        case 'makefile':
        case 'mk':
            await runMakefile(targetDir);
            break;
        case 'network-scan':
        case 'ns':
            await runNetworkScan(targetDir);
            break;
        case 'device-find':
        case 'df':
            await runDeviceFind(targetDir);
            break;
        case 'device-connect':
        case 'dc':
            await runDeviceConnect(targetDir);
            break;
        case 'latch':
        case 'l':
            await runLatchSystem(targetDir);
            break;
        case 'goldhen':
        case 'gh':
            await runGoldHEN(targetDir);
            break;
        case 'goldhen-deploy':
        case 'gd':
            await runGoldHENDeploy(targetDir);
            break;
        case 'goldhen-config':
        case 'gc':
            await runGoldHENConfig(targetDir);
            break;
        case 'goldhen-cheats':
        case 'gch':
            await runGoldHENCheats(targetDir);
            break;
        case 'goldhen-status':
        case 'gs':
            await runGoldHENStatus(targetDir);
            break;
        case 'goldhen-deploy-device':
        case 'gdd':
            await runGoldHENDeployDevice(targetDir);
            break;
        case 'goldhen-troubleshoot':
        case 'gt':
            await runGoldHENTroubleshoot(targetDir);
            break;
        case 'goldhen-server':
        case 'gserver':
            await runGoldHENServer(targetDir);
            break;
        case 'help':
        default:
            showHelp();
    }
}

// Command: Fix - Run one-shot resolution
async function runFix(dir) {
    log('🔧 Fixing packages in: ' + path.resolve(dir), 'blue');
    
    // Check what package files exist
    const hasNode = fs.existsSync(path.join(dir, 'package.json'));
    const hasPython = fs.existsSync(path.join(dir, 'requirements.txt')) || 
                      fs.existsSync(path.join(dir, 'pyproject.toml'));
    const hasRust = fs.existsSync(path.join(dir, 'Cargo.toml'));
    const hasGo = fs.existsSync(path.join(dir, 'go.mod'));
    
    log('\nDetected:');
    if (hasNode) log('  ✓ Node.js project (package.json)', 'green');
    if (hasPython) log('  ✓ Python project (requirements.txt/pyproject.toml)', 'green');
    if (hasRust) log('  ✓ Rust project (Cargo.toml)', 'green');
    if (hasGo) log('  ✓ Go project (go.mod)', 'green');
    
    if (!hasNode && !hasPython && !hasRust && !hasGo) {
        log('\n❌ No package files found', 'red');
        log('   Looking for: package.json, requirements.txt, Cargo.toml, go.mod', 'yellow');
        return;
    }
    
    log('\n⏳ Running resolution...', 'blue');
    
    // Run the main resolver
    const indexPath = path.join(__dirname, 'index.js');
    await runCommand('node', [indexPath, dir], { cwd: dir });
    
    log('\n✅ Fix complete!', 'green');
    log('   Check .package_resolver_columns.json for results', 'yellow');
}

// Command: Interactive - Run terminal mode
async function runInteractive(dir) {
    log('🖥️  Starting interactive mode...', 'blue');
    log('   Commands: r=resolve, p=parse, c=correct, w=watch, q=quit\n', 'yellow');
    
    const indexPath = path.join(__dirname, 'index.js');
    await runCommand('node', [indexPath, dir, 'terminal'], { 
        cwd: dir,
        stdio: 'inherit'  // Allow user interaction
    });
}

// Command: Watch - Auto-re-resolve on changes
async function runWatch(dir) {
    log('👁️  Starting watch mode...', 'blue');
    log('   Will auto-fix when package files change', 'yellow');
    log('   Press Ctrl+C to stop\n', 'yellow');
    
    const indexPath = path.join(__dirname, 'index.js');
    await runCommand('node', [indexPath, dir, 'watch'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: Python Bridge - Direct Python control
async function runPythonBridge(dir) {
    log('🐍 Running Python bridge...', 'blue');
    
    const pyPath = path.join(__dirname, 'pipeline_bridge.py');
    await runCommand('python3', [pyPath, dir], { cwd: dir });
}

// Command: Flash Mode - Wraith directory operation
async function runFlashMode(dir) {
    log('⚡ Running flash mode in wraith directory...', 'blue');
    log('   Flash mode: fast track, wraith integration, RJ45 protocol active\n', 'yellow');
    
    const indexPath = path.join(__dirname, 'index.js');
    await runCommand('node', [indexPath, dir, 'flash'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: Wraith Mode - Full wraith integration
async function runWraithMode(dir) {
    log('🔧 Running full wraith mode...', 'blue');
    log('   Wraith mode: full integration with device and mirror\n', 'yellow');
    
    const orchestratorPath = path.join(__dirname, 'central_orchestrator.js');
    await runCommand('node', [orchestratorPath, dir, 'flash'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: Mirror Sync - Sync device library mirror
async function runMirrorSync(dir) {
    log('🔄 Syncing device library mirror...', 'blue');
    log('   Mirror: device image and package synchronization\n', 'yellow');
    
    const mirrorPath = path.join(__dirname, 'wraith_mirror_manager.js');
    await runCommand('node', [mirrorPath, dir, '--mirror'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: Image Bridge - Initialize device image bridge
async function runImageBridge(dir) {
    log('🌉 Initializing device image bridge...', 'blue');
    log('   Bridge: IOsrom NAND/image handling integration\n', 'yellow');
    
    const bridgePath = path.join(__dirname, 'wraith_image_bridge.py');
    await runCommand('python3', [bridgePath, dir, '--mirror'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: Makefile - Generate transfer Makefile
async function runMakefile(dir) {
    log('🔨 Generating transfer Makefile...', 'blue');
    log('   Makefile: device transfer operations\n', 'yellow');
    
    const bridgePath = path.join(__dirname, 'wraith_image_bridge.py');
    await runCommand('python3', [bridgePath, dir, '--makefile'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: Network Scan - Scan local network for devices
async function runNetworkScan(dir) {
    log('🔍 Scanning local network for devices...', 'blue');
    log('   Network: real discovery via SeedGate client (no stubs)\n', 'yellow');
    
    const makefilePath = path.join(dir, 'Makefile');
    await runCommand('make', ['-C', dir, 'network-scan'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: Device Find - Find best device on network
async function runDeviceFind(dir) {
    log('🎯 Finding best device on network...', 'blue');
    log('   Device: MAC/IP discovery via SeedGate finder\n', 'yellow');
    
    await runCommand('make', ['-C', dir, 'device-find'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: Device Connect - Connect to discovered device
async function runDeviceConnect(dir) {
    log('🔗 Connecting to discovered device...', 'blue');
    log('   Connect: automatic latching to network device\n', 'yellow');
    
    await runCommand('make', ['-C', dir, 'device-connect'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: Latch System - Start/stop wraith automatic latching
async function runLatchSystem(dir) {
    log('⚡ Running wraith latching system...', 'blue');
    log('   Latch: automatic device detection and MAC gating\n', 'yellow');
    
    const latchPath = path.join(__dirname, 'wraith_latch.js');
    await runCommand('node', [latchPath, dir, 'run'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: GoldHEN - Run GoldHEN status
async function runGoldHEN(dir) {
    log('🏆 Running GoldHEN integration...', 'blue');
    log('   GoldHEN: PS4 Homebrew Enabler v2.4b17.3\n', 'yellow');
    
    const goldhenPath = path.join(__dirname, 'goldhen_integration.py');
    await runCommand('python3', [goldhenPath, dir, '--status'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: GoldHEN Deploy - Deploy GoldHEN payload
async function runGoldHENDeploy(dir) {
    log('🚀 Deploying GoldHEN payload...', 'blue');
    log('   Payload: goldhen.bin -> PS4 device\n', 'yellow');
    
    const goldhenPath = path.join(__dirname, 'goldhen_integration.py');
    await runCommand('python3', [goldhenPath, dir, '--deploy'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: GoldHEN Config - Configure GoldHEN
async function runGoldHENConfig(dir) {
    log('⚙️  Configuring GoldHEN...', 'blue');
    log('   Config: GoldHEN settings and features\n', 'yellow');
    
    const goldhenPath = path.join(__dirname, 'goldhen_integration.py');
    await runCommand('python3', [goldhenPath, dir, '--config'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: GoldHEN Cheats - Setup cheats directory
async function runGoldHENCheats(dir) {
    log('🎮 Setting up GoldHEN cheats directory...', 'blue');
    log('   Cheats: json, shn, mc4 format support\n', 'yellow');
    
    const goldhenPath = path.join(__dirname, 'goldhen_integration.py');
    await runCommand('python3', [goldhenPath, dir, '--cheats'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: GoldHEN Status - Show GoldHEN status
async function runGoldHENStatus(dir) {
    log('📊 GoldHEN status...', 'blue');
    
    const goldhenPath = path.join(__dirname, 'goldhen_integration.py');
    await runCommand('python3', [goldhenPath, dir, '--status'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: GoldHEN Deploy Device - Full deployment to device
async function runGoldHENDeployDevice(dir) {
    log('🚀 Deploying GoldHEN to device...', 'blue');
    log('   Device: MAC-based transfer, kernel patches, troubleshooting\n', 'yellow');
    
    const deployerPath = path.join(__dirname, 'goldhen_device_deployer.js');
    await runCommand('node', [deployerPath, dir, 'deploy'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: GoldHEN Troubleshoot - Troubleshoot device connection
async function runGoldHENTroubleshoot(dir) {
    log('🔧 Troubleshooting GoldHEN device deployment...', 'blue');
    log('   Checks: connectivity, payload, MAC, admin pass\n', 'yellow');
    
    const deployerPath = path.join(__dirname, 'goldhen_device_deployer.js');
    await runCommand('node', [deployerPath, dir, 'troubleshoot'], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: GoldHEN Server - Start HTTP endpoint server for PS4 browser
async function runGoldHENServer(dir) {
    log('🌐 Starting GoldHEN HTTP endpoint server...', 'blue');
    log('   Server: payload + kernel patches for PS4 browser\n', 'yellow');
    
    const serverPath = path.join(__dirname, 'goldhen_endpoint_server.js');
    const port = process.argv[4] || 8080;
    
    await runCommand('node', [serverPath, dir, port], { 
        cwd: dir,
        stdio: 'inherit'
    });
}

// Command: Status - Show current state
async function showStatus(dir) {
    log('📊 Status for: ' + path.resolve(dir), 'blue');
    
    // Check for generated files
    const columnFile = path.join(dir, '.package_resolver_columns.json');
    const manifestFile = path.join(dir, '.unified_manifest.json');
    const venvDir = path.join(dir, 'safely_contained_venv');
    
    // Check for wraith directory
    const wraithDir = checkWraithDirectory(dir);
    if (wraithDir) {
        log('\nWraith Integration:', 'green');
        log('  ✓ Wraith directory detected', 'green');
        log('  ✓ Flash mode available', 'green');
    }
    
    log('\nGenerated Files:');
    if (fs.existsSync(columnFile)) {
        const data = JSON.parse(fs.readFileSync(columnFile, 'utf8'));
        log(`  ✓ Resolution data: ${data.columns?.length || 0} columns`, 'green');
    } else {
        log('  ✗ No resolution data (run: fix)', 'yellow');
    }
    
    if (fs.existsSync(venvDir)) {
        log('  ✓ Python venv: active', 'green');
    } else {
        log('  ✗ No Python venv', 'yellow');
    }
    
    // Count package files
    const counts = {
        node: fs.existsSync(path.join(dir, 'package.json')) ? 1 : 0,
        python: (fs.existsSync(path.join(dir, 'requirements.txt')) || 
                 fs.existsSync(path.join(dir, 'pyproject.toml'))) ? 1 : 0,
        rust: fs.existsSync(path.join(dir, 'Cargo.toml')) ? 1 : 0,
        go: fs.existsSync(path.join(dir, 'go.mod')) ? 1 : 0
    };
    
    const total = counts.node + counts.python + counts.rust + counts.go;
    log(`\nPackage Sources: ${total} detected`);
    if (counts.node) log('  - Node.js (npm)');
    if (counts.python) log('  - Python (pip)');
    if (counts.rust) log('  - Rust (cargo)');
    if (counts.go) log('  - Go (modules)');
}

function checkWraithDirectory(dir) {
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
        if (fs.existsSync(path.join(dir, file))) {
            return dir;
        }
    }
    
    const parentDir = path.join(dir, '..');
    for (const file of wraithIndicators) {
        if (fs.existsSync(path.join(parentDir, file))) {
            return parentDir;
        }
    }
    
    return null;
}

// Helper: Run a command and return promise
function runCommand(cmd, args, options) {
    return new Promise((resolve, reject) => {
        const proc = spawn(cmd, args, {
            ...options,
            stdio: options.stdio || 'pipe'
        });
        
        let stdout = '';
        let stderr = '';
        
        if (proc.stdout) {
            proc.stdout.on('data', (data) => {
                stdout += data.toString();
                if (options.stdio !== 'inherit') {
                    process.stdout.write(data);
                }
            });
        }
        
        if (proc.stderr) {
            proc.stderr.on('data', (data) => {
                stderr += data.toString();
                if (options.stdio !== 'inherit') {
                    process.stderr.write(data);
                }
            });
        }
        
        proc.on('close', (code) => {
            if (code === 0) {
                resolve({ stdout, stderr });
            } else {
                reject(new Error(`Command failed with code ${code}`));
            }
        });
    });
}

// Show help
function showHelp() {
    log('USAGE: node CONTROL_CENTER.js <command> [directory]', 'blue');
    log('\nCommands:');
    log('  fix           Fix all package issues (default)');
    log('  interactive   Start interactive terminal mode');
    log('  watch         Watch for changes and auto-fix');
    log('  status        Show current project status');
    log('  python        Run Python bridge directly');
    log('  flash         Run flash mode in wraith directory');
    log('  wraith        Run full wraith mode with device integration');
    log('  mirror        Sync device library mirror');
    log('  bridge        Initialize device image bridge');
    log('  makefile      Generate transfer Makefile');
    log('  network-scan  Scan local network for devices');
    log('  device-find   Find best device on network');
    log('  device-connect Connect to discovered device');
    log('  latch         Start/stop wraith automatic latching');
    log('  goldhen       Show GoldHEN status');
    log('  goldhen-deploy Deploy GoldHEN payload to device');
    log('  goldhen-config Configure GoldHEN settings');
    log('  goldhen-cheats Setup GoldHEN cheats directory');
    log('  goldhen-status Show GoldHEN status');
    log('  goldhen-deploy-device Full device deployment with kernel patches');
    log('  goldhen-troubleshoot Troubleshoot device connection');
    log('  goldhen-server Start HTTP endpoint server for PS4 browser');
    log('  help          Show this help');
    log('\nExamples:');
    log('  node CONTROL_CENTER.js fix                    # Fix current directory');
    log('  node CONTROL_CENTER.js fix ./my-project       # Fix specific project');
    log('  node CONTROL_CENTER.js interactive            # Interactive mode');
    log('  node CONTROL_CENTER.js watch                  # Watch mode');
    log('  node CONTROL_CENTER.js flash                  # Flash mode (wraith dir)');
    log('  node CONTROL_CENTER.js wraith                 # Full wraith mode');
    log('  node CONTROL_CENTER.js mirror                 # Sync device mirror');
    log('  node CONTROL_CENTER.js network-scan           # Scan network for devices');
    log('  node CONTROL_CENTER.js device-find            # Find best device');
    log('  node CONTROL_CENTER.js latch                  # Start latching system');
    log('  node CONTROL_CENTER.js goldhen-server         # Start HTTP server for PS4 browser');
    log('  node CONTROL_CENTER.js status                 # Check status');
    log('\nWhat This Fixes:');
    log('  • npm install failures');
    log('  • pip install failures');
    log('  • Version conflicts');
    log('  • Missing packages');
    log('  • Cross-language dependency issues');
    log('  • Device image handling (IOsrom integration)');
    log('  • NAND flash operations');
    log('  • Library mirror synchronization');
    log('  • Real network device discovery (SeedGate)');
    log('  • Automatic MAC-based latching');
}

// Run main
main().catch(err => {
    log('\n❌ Error: ' + err.message, 'red');
    process.exit(1);
});
