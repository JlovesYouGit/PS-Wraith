#!/usr/bin/env python3
"""
Consciousness Exchange Bridge
Python bridge for unified-consciousness-render to interface with forward and F-dump modules.
"""

import sys
import os
import json
import hashlib
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

FORWARD_DIR = Path(__file__).resolve().parent.parent / 'forward'
F_DUMP_DIR = Path(__file__).resolve().parent.parent / 'F-dump'
EXCHANGE_CACHE_DIR = Path(__file__).resolve().parent / 'exchange-cache'
GIT_TREE_DIR = Path(__file__).resolve().parent / 'consciousness-git-tree'
MAX_CACHE_SIZE = 32 * 1024 * 1024  # 32MB


def load_fdump_env() -> Dict[str, str]:
    env_path = F_DUMP_DIR / '.env'
    env_vars = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def get_cache_size(cache_dir: Path) -> int:
    total = 0
    try:
        for entry in cache_dir.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
    except Exception:
        pass
    return total


def enforce_32mb_threshold(cache_dir: Path) -> int:
    if not cache_dir.exists():
        return 0
    current_size = get_cache_size(cache_dir)
    removed = 0
    dumps = sorted(cache_dir.glob('dump_*.pkl'), key=lambda p: p.stat().st_mtime)
    while current_size > MAX_CACHE_SIZE and len(dumps) > 1:
        oldest = dumps.pop(0)
        try:
            size = oldest.stat().st_size
            oldest.unlink()
            current_size -= size
            removed += size
        except Exception:
            pass
    return removed


def regenerate_seed(node_id: str) -> str:
    seed_input = f"{node_id}:{datetime.now().isoformat()}:{os.urandom(32).hex()}"
    seed = hashlib.sha256(seed_input.encode()).hexdigest()
    return seed


def allocate_dump(node_id: str, seed: str, topology: Dict[str, Any]) -> Optional[str]:
    cache_dir = F_DUMP_DIR / f"cache_{node_id}"
    cache_dir.mkdir(parents=True, exist_ok=True)

    enforce_32mb_threshold(cache_dir)

    timestamp = datetime.now().isoformat().replace(':', '-').replace('.', '-')
    dump_file = cache_dir / f"dump_{timestamp}.json"

    dump_data = {
        'nodeId': node_id,
        'seed': seed,
        'topology': topology,
        'timestamp': datetime.now().isoformat(),
        'memoryState': {
            'waveState': 'LOCKED',
            'signatures': [],
            'emissionChannels': [],
        },
    }

    with open(dump_file, 'w') as f:
        json.dump(dump_data, f, indent=2)

    return str(dump_file)


def generate_ultrasonic_signature() -> str:
    analyzer_script = FORWARD_DIR / 'ultrasonic_waveform_analyzer.py'
    if analyzer_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(analyzer_script), '--signature-only'],
                capture_output=True, text=True, timeout=10, cwd=str(FORWARD_DIR)
            )
            if result.returncode == 0 and result.stdout.strip():
                raw = result.stdout.strip()
                return hashlib.sha256((raw + datetime.now().isoformat()).encode()).hexdigest()
        except Exception:
            pass
    return hashlib.sha256(os.urandom(24)).hexdigest()


def get_topology_graph(env_vars: Dict[str, str]) -> Dict[str, Any]:
    return {
        'nodes': [
            {'id': env_vars.get('NODE_001_ID', 'node_001'), 'type': 'emission_source', 'uri': env_vars.get('NODE_001_URI', 'http://127.0.0.1:8080')},
            {'id': env_vars.get('NODE_002_ID', 'node_002'), 'type': 'matcher', 'uri': env_vars.get('NODE_002_URI', 'http://127.0.0.1:8081')},
        ],
        'edges': [
            {'source': env_vars.get('NODE_001_ID', 'node_001'), 'target': env_vars.get('NODE_002_ID', 'node_002'), 'type': 'wave_handshake', 'protocol': 'vsync'}
        ]
    }


def git_commit(message: str) -> bool:
    if not GIT_TREE_DIR.exists() or not (GIT_TREE_DIR / '.git').exists():
        return False
    try:
        subprocess.run(['git', '-C', str(GIT_TREE_DIR), 'add', '-A'], capture_output=True)
        subprocess.run(['git', '-C', str(GIT_TREE_DIR), 'commit', '-m', message], capture_output=True)
        return True
    except Exception:
        return False


def recall_from_tree(pattern: str) -> List[str]:
    if not GIT_TREE_DIR.exists() or not (GIT_TREE_DIR / '.git').exists():
        return []
    try:
        result = subprocess.run(
            ['git', '-C', str(GIT_TREE_DIR), 'log', '--all', '--oneline', '--grep', pattern],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return [line for line in result.stdout.strip().split('\n') if line]
    except Exception:
        pass
    return []


def handle_command(command: str, args: List[str]) -> Dict[str, Any]:
    if command == '--signature':
        sig = generate_ultrasonic_signature()
        return {'signature': sig}

    elif command == '--config':
        env = load_fdump_env()
        return {'env': env}

    elif command == '--cache-size':
        node_id = args[0] if args else 'node_001'
        cache_dir = F_DUMP_DIR / f"cache_{node_id}"
        return {'nodeId': node_id, 'size': get_cache_size(cache_dir), 'maxSize': MAX_CACHE_SIZE}

    elif command == '--enforce-threshold':
        node_id = args[0] if args else 'node_001'
        cache_dir = F_DUMP_DIR / f"cache_{node_id}"
        removed = enforce_32mb_threshold(cache_dir)
        return {'nodeId': node_id, 'removed': removed, 'remainingSize': get_cache_size(cache_dir)}

    elif command == '--allocate-dump':
        node_id = args[0] if args else 'node_001'
        seed = args[1] if len(args) > 1 else regenerate_seed(node_id)
        env = load_fdump_env()
        topology = get_topology_graph(env)
        dump_file = allocate_dump(node_id, seed, topology)
        return {'nodeId': node_id, 'dumpFile': dump_file, 'seed': seed}

    elif command == '--regenerate-seed':
        node_id = args[0] if args else 'node_001'
        seed = regenerate_seed(node_id)
        return {'nodeId': node_id, 'seed': seed}

    elif command == '--topology':
        env = load_fdump_env()
        return {'topology': get_topology_graph(env)}

    elif command == '--recall':
        pattern = args[0] if args else ''
        commits = recall_from_tree(pattern)
        return {'pattern': pattern, 'commits': commits}

    elif command == '--git-commit':
        message = args[0] if args else 'Exchange commit'
        success = git_commit(message)
        return {'success': success, 'message': message}

    elif command == '--wave-params':
        return {
            'powerAmplification': 30.0,
            'phaseInversion': 180.0,
            'initialVoltage': 5.0,
            'escalationRate': 1.5,
            'maxCycles': 50,
            'frequencyMatch': 40.0,
            'targetVoltage': 250.0,
            'pulseFrequency': 1000.0,
            'pulseDuration': 0.001,
            'burstCount': 1000,
            'dampingCoefficient': 0.95,
            'feedbackGain': 1.2,
            'reflectionCoefficient': 0.95,
            'primaryFrequency': 2417000000.0,
            'feedbackRate': 10000000.0,
            'powerMultiplier': 100.0,
            'analysisWindow': 10.0,
            'samplingRate': 100.0,
            'fluctuationThreshold': 5.0,
        }

    elif command == '--status':
        return {
            'forwardDir': str(FORWARD_DIR),
            'fDumpDir': str(F_DUMP_DIR),
            'exchangeCacheDir': str(EXCHANGE_CACHE_DIR),
            'gitTreeDir': str(GIT_TREE_DIR),
            'maxCacheSize': MAX_CACHE_SIZE,
            'waveParameters': {
                'powerAmplification': 30.0,
                'phaseInversion': 180.0,
                'initialVoltage': 5.0,
                'escalationRate': 1.5,
                'maxCycles': 50,
                'frequencyMatch': 40.0,
                'targetVoltage': 250.0,
                'pulseFrequency': 1000.0,
                'pulseDuration': 0.001,
                'burstCount': 1000,
                'dampingCoefficient': 0.95,
                'feedbackGain': 1.2,
                'reflectionCoefficient': 0.95,
                'primaryFrequency': 2417000000.0,
                'feedbackRate': 10000000.0,
                'powerMultiplier': 100.0,
                'analysisWindow': 10.0,
                'samplingRate': 100.0,
                'fluctuationThreshold': 5.0,
            },
        }

    else:
        return {'error': f'Unknown command: {command}', 'usage': 'bridge.py --command [args]'}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'No command provided', 'usage': 'bridge.py --command [args]'}))
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]
    result = handle_command(command, args)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
