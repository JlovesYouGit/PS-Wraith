import json
import os
import subprocess
import threading
import time
import hashlib
import pickle
import re
import socket
import glob
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from dotenv import load_dotenv


class NodeState(Enum):
    ACTIVE = "active"
    IDLE = "idle"
    LOCKED = "locked"
    TERMINATED = "terminated"


@dataclass
class TrafficBuffer:
    buffer: List[Dict[str, Any]]
    integrity_hash: str
    timestamp: str

    def update_hash(self):
        content = json.dumps(self.buffer, sort_keys=True)
        self.integrity_hash = hashlib.sha256(content.encode()).hexdigest()
        self.timestamp = datetime.now().isoformat()


@dataclass
class NodeConfig:
    node_id: str
    venv_path: str
    python_executable: str
    connectors: List[str]
    credentials: Dict[str, str]
    self_ip: str
    ip_mask: str
    gateway: str
    uri: str
    localhost_endpoint: str
    gateway_list: List[str]
    library_path: str


@dataclass
class ResolvedConnectionConfig:
    """Saved when a TCP session is proven through the NeuralMatcherChain."""
    uri: str
    resolved_ip: str
    reachable_port: int
    local_port: int
    gateway_used: str
    score: float
    permit_bit: int          # vsync encoded: 1 = domain permit granted, 0 = denied
    connect_key: str         # key that unlocked external domain permit
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# VsyncEncoder — binary state re-coder for neural matcher parameters
# ---------------------------------------------------------------------------
# Maps execution parameters to 0/1 signals that the NeuralMatcherChain reads.
# A parameter update propagates through the chain only when the encoded bit
# transitions from 0 → 1 (permit open) or 1 → 0 (permit revoked).
# ---------------------------------------------------------------------------

class VsyncEncoder:
    """
    Encodes/decodes execution parameters as vsync-aligned binary states.

    Rules:
      bit = 1  → parameter permits execution / connection / update
      bit = 0  → parameter blocks execution / connection / update

    encode_param() maps a string credential/key to a 0 or 1 based on:
      - SHA-256 of (key + domain_hint) — odd last byte → 1, even → 0
      - Caller can override the bit by passing force_bit=0|1

    The chain calls sync() on each candidate cycle to re-code all tracked
    parameters so stale 0-states can flip to 1 when a new key arrives.
    """

    def __init__(self):
        self._params: Dict[str, int] = {}   # param_name → current bit
        self._keys:   Dict[str, str] = {}   # param_name → last key used

    def encode_param(self, param_name: str, key: str,
                     domain_hint: str = "", force_bit: Optional[int] = None) -> int:
        if force_bit in (0, 1):
            bit = force_bit
        else:
            digest = hashlib.sha256(f"{key}{domain_hint}".encode()).digest()
            bit = 1 if (digest[-1] % 2 != 0) else 0
        self._params[param_name] = bit
        self._keys[param_name] = key
        return bit

    def decode_param(self, param_name: str) -> int:
        """Return current bit for param; defaults to 0 (blocked) if unknown."""
        return self._params.get(param_name, 0)

    def sync(self, domain_hint: str = "") -> Dict[str, int]:
        """Re-encode all tracked params against current keys — vsync pass."""
        for name, key in self._keys.items():
            digest = hashlib.sha256(f"{key}{domain_hint}".encode()).digest()
            self._params[name] = 1 if (digest[-1] % 2 != 0) else 0
        return dict(self._params)

    def permit_granted(self, param_name: str) -> bool:
        return self._params.get(param_name, 0) == 1

    def revoke(self, param_name: str):
        self._params[param_name] = 0

    def force_permit(self, param_name: str, key: str):
        self._params[param_name] = 1
        self._keys[param_name] = key


# ---------------------------------------------------------------------------
# Wave-format handshake types and lock
# ---------------------------------------------------------------------------

class WaveState(Enum):
    AWAIT   = "await"    # node not yet ready — flat baseline
    RISING  = "rising"   # node signalling readiness — leading edge
    PEAK    = "peak"     # node confirmed ready — amplitude peak
    LOCKED  = "locked"   # both sides peaked — connection locked


@dataclass
class HandshakeLock:
    """
    Written atomically once both URI nodes reach PEAK in the wave sequence.
    Acts as the persistent establish-point so neither node needs to re-handshake
    on subsequent runs — they read this file, verify TCP, and re-enter LOCKED.
    """
    node_001_uri:        str
    node_001_ip:         str
    node_001_port:       int
    node_002_uri:        str
    node_002_ip:         str
    node_002_port:       int
    local_port:          int        # shared localhost entry port
    gateway_used:        str
    connect_key:         str
    wave_sequence:       List[str]  # ordered log of wave states that led to LOCK
    timestamp:           str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_file(path: str) -> Optional['HandshakeLock']:
        if not os.path.exists(path):
            return None
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return HandshakeLock(**data)
        except (json.JSONDecodeError, TypeError, KeyError):
            return None

    def save(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


# ---------------------------------------------------------------------------
# WaveHandshake — mutual await between two URI nodes via wave signal
# ---------------------------------------------------------------------------

class WaveHandshake:
    """
    Coordinates a mutual await handshake between node_001 and node_002.

    Each node has a state file (wave_node_001.json / wave_node_002.json).
    The sequence:
      1. Both nodes write AWAIT  — baseline flat signal
      2. Each advances to RISING once it has resolved its URI via TCP
      3. Each polls the other's state file; when both are RISING → advance to PEAK
      4. When both are PEAK  → write LOCKED + save HandshakeLock JSON
      5. Connection buffer payload is routed through the local_port entry subnet
         during the entire await so neither node drops the buffer

    Wave signal encoding (for grep / decode):
      AWAIT  = 0x00  flat
      RISING = 0x01  leading edge
      PEAK   = 0x10  amplitude
      LOCKED = 0x11  both bits set  (binary vsync: 1‑1 = fully established)
    """

    WAVE_ENCODING: Dict[str, str] = {
        'await':  '0x00',
        'rising': '0x01',
        'peak':   '0x10',
        'locked': '0x11',
    }
    LOCK_FILE      = "handshake_lock.json"
    STATE_FILE_001 = "wave_node_001.json"
    STATE_FILE_002 = "wave_node_002.json"
    POLL_INTERVAL  = 0.25   # seconds
    AWAIT_TIMEOUT  = 15.0   # max seconds to wait for peer

    def __init__(self, node_001: 'Node', node_002: 'Node'):
        self.n1 = node_001
        self.n2 = node_002
        self._wave_log: List[str] = []

    # ------------------------------------------------------------------
    # State file helpers
    # ------------------------------------------------------------------

    def _write_state(self, node_id: str, state: WaveState,
                     extra: Optional[Dict[str, Any]] = None):
        path = self.STATE_FILE_001 if node_id == self.n1.config.node_id \
               else self.STATE_FILE_002
        payload = {
            'node_id':  node_id,
            'state':    state.value,
            'wave_hex': self.WAVE_ENCODING[state.value],
            'timestamp': datetime.now().isoformat(),
        }
        if extra:
            payload.update(extra)
        with open(path, 'w') as f:
            json.dump(payload, f, indent=2)
        entry = f"{node_id}:{state.value}({self.WAVE_ENCODING[state.value]})"
        self._wave_log.append(entry)
        node = self.n1 if node_id == self.n1.config.node_id else self.n2
        node._log_traffic({'action': 'wave_state', 'state': state.value,
                           'wave_hex': self.WAVE_ENCODING[state.value]})

    def _read_state(self, state_file: str) -> Optional[str]:
        if not os.path.exists(state_file):
            return None
        try:
            with open(state_file, 'r') as f:
                return json.load(f).get('state')
        except (json.JSONDecodeError, KeyError):
            return None

    def _peer_state(self, own_node_id: str) -> Optional[str]:
        peer_file = self.STATE_FILE_002 \
                    if own_node_id == self.n1.config.node_id \
                    else self.STATE_FILE_001
        return self._read_state(peer_file)

    # ------------------------------------------------------------------
    # Await loop — polls until peer reaches target state or timeout
    # ------------------------------------------------------------------

    def _await_peer(self, own_node_id: str,
                    target_state: str, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            peer = self._peer_state(own_node_id)
            if peer == target_state:
                return True
            time.sleep(self.POLL_INTERVAL)
        return False

    # ------------------------------------------------------------------
    # Core handshake
    # ------------------------------------------------------------------

    def run(self, cfg1: 'ResolvedConnectionConfig',
            cfg2: 'ResolvedConnectionConfig',
            local_port: int,
            connect_key: str) -> Optional[HandshakeLock]:
        """
        Execute the full wave handshake.
        cfg1/cfg2 are the TCP-proven configs for node_001 and node_002.
        Returns a HandshakeLock if both nodes peak, else None.
        """
        # --- AWAIT: both nodes announce themselves ---
        self._write_state(self.n1.config.node_id, WaveState.AWAIT)
        self._write_state(self.n2.config.node_id, WaveState.AWAIT)

        # --- RISING: node_001 has its TCP config, signal readiness ---
        self._write_state(self.n1.config.node_id, WaveState.RISING,
                          {'resolved_ip': cfg1.resolved_ip,
                           'port': cfg1.reachable_port})
        self._write_state(self.n2.config.node_id, WaveState.RISING,
                          {'resolved_ip': cfg2.resolved_ip,
                           'port': cfg2.reachable_port})

        # --- PEAK: each waits for peer RISING before going to PEAK ---
        n1_peer_risen = self._await_peer(
            self.n1.config.node_id, 'rising', self.AWAIT_TIMEOUT)
        n2_peer_risen = self._await_peer(
            self.n2.config.node_id, 'rising', self.AWAIT_TIMEOUT)

        if not (n1_peer_risen and n2_peer_risen):
            self.n1._log_traffic({'action': 'handshake_peer_rising_timeout'})
            return None

        self._write_state(self.n1.config.node_id, WaveState.PEAK)
        self._write_state(self.n2.config.node_id, WaveState.PEAK)

        # --- LOCKED: both must be at PEAK ---
        n1_peer_peaked = self._await_peer(
            self.n1.config.node_id, 'peak', self.AWAIT_TIMEOUT)
        n2_peer_peaked = self._await_peer(
            self.n2.config.node_id, 'peak', self.AWAIT_TIMEOUT)

        if not (n1_peer_peaked and n2_peer_peaked):
            self.n1._log_traffic({'action': 'handshake_peer_peak_timeout'})
            return None

        self._write_state(self.n1.config.node_id, WaveState.LOCKED)
        self._write_state(self.n2.config.node_id, WaveState.LOCKED)

        lock = HandshakeLock(
            node_001_uri   = cfg1.uri,
            node_001_ip    = cfg1.resolved_ip,
            node_001_port  = cfg1.reachable_port,
            node_002_uri   = cfg2.uri,
            node_002_ip    = cfg2.resolved_ip,
            node_002_port  = cfg2.reachable_port,
            local_port     = local_port,
            gateway_used   = cfg1.gateway_used,
            connect_key    = connect_key,
            wave_sequence  = list(self._wave_log),
        )
        lock.save(self.LOCK_FILE)
        self.n1._log_traffic({'action': 'handshake_locked',
                              'lock': lock.to_dict()})
        self.n2._log_traffic({'action': 'handshake_locked',
                              'lock': lock.to_dict()})
        return lock

    @staticmethod
    def decode_wave_hex(hex_str: str) -> str:
        """Decode wave signal hex back to state name for grep/logging."""
        mapping = {'0x00': 'await', '0x01': 'rising',
                   '0x10': 'peak',  '0x11': 'locked'}
        return mapping.get(hex_str, 'unknown')


class Node:
    def __init__(self, config: NodeConfig):
        self.config = config
        self.state = NodeState.IDLE
        self.traffic_buffer = TrafficBuffer([], "", "")
        self.instance = None
        self.keep_alive_thread = None
        self.lock = threading.Lock()
        self.json_lock_file = f"{config.node_id}_lock.json"
        self.cache_dir = f"cache_{config.node_id}"
        self.log_file = f"{config.node_id}_log.json"
        self.vsync = VsyncEncoder()
        os.makedirs(self.cache_dir, exist_ok=True)
        self._load_state()
        self._update_ip_from_uri()

    def _load_state(self):
        if os.path.exists(self.json_lock_file):
            with open(self.json_lock_file, 'r') as f:
                state = json.load(f)
                self.state = NodeState(state.get('state', 'idle'))

    def _is_private_ip(self, ip: str) -> bool:
        try:
            parts = list(map(int, ip.split('.')))
            return (
                parts[0] == 10
                or (parts[0] == 172 and 16 <= parts[1] <= 31)
                or (parts[0] == 192 and parts[1] == 168)
                or parts[0] == 127
            )
        except (ValueError, IndexError):
            return False

    def _update_ip_from_uri(self):
        if self.config.uri:
            extracted_ip = self.extract_ip_from_uri(self.config.uri)
            if extracted_ip and self._is_private_ip(extracted_ip):
                self.config.self_ip = extracted_ip
                self._log_traffic({'action': 'ip_update_from_uri',
                                   'new_ip': extracted_ip, 'uri': self.config.uri})
            elif extracted_ip:
                self._log_traffic({'action': 'ip_update_skipped_public',
                                   'resolved_ip': extracted_ip, 'uri': self.config.uri})

    def _save_state(self):
        with open(self.json_lock_file, 'w') as f:
            json.dump({'state': self.state.value,
                       'timestamp': datetime.now().isoformat()}, f)

    def link_venv(self):
        if os.path.exists(self.config.venv_path):
            self.config.python_executable = os.path.join(
                self.config.venv_path, 'bin', 'python')
            return True
        return False

    def open_instance(self):
        with self.lock:
            try:
                self.instance = subprocess.Popen(
                    [self.config.python_executable, '-c',
                     'import time; time.sleep(3600)'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.state = NodeState.ACTIVE
                self._save_state()
                self._start_keep_alive()
                return True
            except Exception as e:
                self._log_error(f"Failed to open instance: {e}")
                return False

    def _start_keep_alive(self):
        def keep_alive():
            while self.state == NodeState.ACTIVE:
                time.sleep(5)
                if self.instance and self.instance.poll() is not None:
                    self.open_instance()
        self.keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
        self.keep_alive_thread.start()

    def emit_status(self) -> Dict[str, Any]:
        return {
            'node_id': self.config.node_id,
            'state': self.state.value,
            'timestamp': datetime.now().isoformat(),
            'buffer_size': len(self.traffic_buffer.buffer)
        }

    def add_traffic(self, traffic: Dict[str, Any]):
        with self.lock:
            self.traffic_buffer.buffer.append(traffic)
            self.traffic_buffer.update_hash()
            self._log_traffic(traffic)

    def _log_traffic(self, traffic: Dict[str, Any]):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'node_id': self.config.node_id,
            'traffic': traffic
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def _log_error(self, message: str):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'node_id': self.config.node_id,
            'error': message
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def check_key_latch(self, key: str) -> bool:
        return key in self.config.credentials

    def update_seed(self, seed: str):
        self.config.credentials['seed'] = seed
        self._save_state()

    def match_arguments(self, args: Dict[str, Any]) -> bool:
        for key, value in args.items():
            if key in self.config.credentials and \
               self.config.credentials[key] != str(value):
                return False
        return True

    def cascade_to_first_node(self, data: Dict[str, Any]):
        self.add_traffic(data)
        for connector in self.config.connectors:
            self._log_traffic({'connector': connector, 'data': data})
        if self.config.uri:
            self._log_traffic({'uri_endpoint': self.config.uri, 'data': data})

    def save_cache_dump(self):
        cache_file = os.path.join(
            self.cache_dir,
            f"dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        )
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'buffer': self.traffic_buffer.buffer,
                'config': asdict(self.config),
                'state': self.state.value
            }, f)

    def load_cache_dump(self, cache_file: str):
        with open(cache_file, 'rb') as f:
            data = pickle.load(f)
            self.traffic_buffer.buffer = data['buffer']
            self.traffic_buffer.update_hash()

    def load_pkl_session_from_payload(self, payload: Dict[str, Any]):
        if 'pkl_file' in payload:
            pkl_path = payload['pkl_file']
            if os.path.exists(pkl_path):
                self.load_cache_dump(pkl_path)
                return True
        return False

    def extract_ip_from_uri(self, uri: str) -> Optional[str]:
        match = re.search(r'https?://([^/:]+)', uri)
        if match:
            hostname = match.group(1)
            try:
                return socket.gethostbyname(hostname)
            except socket.gaierror:
                pass
        return None

    def establish_link_via_ip_mask_gateway(self, target_ip: str,
                                           ip_mask: str, gateway: str) -> bool:
        if not self._validate_ip_mask(target_ip, ip_mask):
            return False
        return self._route_through_gateway(target_ip, gateway)

    def _validate_ip_mask(self, ip: str, mask: str) -> bool:
        """Both ip and self_ip must share the same network prefix under mask."""
        try:
            ip_parts   = list(map(int, ip.split('.')))
            mask_parts = list(map(int, mask.split('.')))
            self_parts = list(map(int, self.config.self_ip.split('.')))
            for i in range(4):
                if (ip_parts[i] & mask_parts[i]) != (self_parts[i] & mask_parts[i]):
                    return False
            return True
        except (ValueError, IndexError):
            return False

    def _route_through_gateway(self, target_ip: str, gateway: str) -> bool:
        try:
            socket.create_connection((gateway, 80), timeout=2)
            return True
        except (socket.timeout, socket.error):
            return False

    def route_via_localhost_endpoint(self, data: Dict[str, Any]) -> bool:
        if not self.config.localhost_endpoint:
            return False
        try:
            match = re.search(r'://([^:/]+)', self.config.localhost_endpoint)
            if not match:
                return False
            localhost_host = match.group(1)
            ports = list({8080, 80, 443, 3000, 5000, 8000})
            for port in ports:
                try:
                    s = socket.create_connection((localhost_host, port), timeout=1)
                    s.close()
                    self._log_traffic({'action': 'localhost_direct_route',
                                       'endpoint': f"{localhost_host}:{port}",
                                       'data': data})
                    return True
                except (socket.timeout, socket.error):
                    continue
        except (ValueError,):
            pass
        return False

    def _discover_ports_from_gateway(self) -> List[int]:
        for gateway in self.config.gateway_list:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((gateway, 80))
                sock.close()
                return [80, 443, 8080]
            except (socket.timeout, socket.error):
                continue
        return []

    def accept_ports_from_self_after_gateway(self, gateway_accessed: str) -> bool:
        if gateway_accessed in self.config.gateway_list:
            self.config.self_ip = socket.gethostbyname(socket.gethostname())
            self._log_traffic({'action': 'port_acceptance',
                               'gateway': gateway_accessed,
                               'self_ip': self.config.self_ip})
            return True
        return False

    def match_route_against_gateway_list(self, target_ip: str) -> Optional[str]:
        for gateway in self.config.gateway_list:
            if self._validate_ip_mask(target_ip, gateway):
                return gateway
        return None

    def query_library_source_objects(self, pattern: str) -> List[str]:
        if os.path.exists(self.config.library_path):
            return glob.glob(os.path.join(self.config.library_path, pattern))
        return []

    def load_source_object_code(self, file_path: str) -> Optional[str]:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return f.read()
            except IOError:
                return None
        return None

    def fetch_via_venv_payload(self, payload: Dict[str, Any]) \
            -> Optional[Dict[str, Any]]:
        if self.config.node_id == "node_001":
            return None
        if 'venv_fetch_command' in payload:
            cmd = payload['venv_fetch_command']
            try:
                result = subprocess.run(
                    [self.config.python_executable, '-c', cmd],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    return {'output': result.stdout, 'error': result.stderr}
            except subprocess.TimeoutExpired:
                return {'error': 'venv fetch timeout'}
        return None

    def send_back_from_self(self, data: Dict[str, Any]) -> bool:
        if self.config.node_id == "node_001":
            return False
        data['origin_ip']   = self.config.self_ip
        data['origin_node'] = self.config.node_id
        self.add_traffic(data)
        return True

    def verify_ip_originates_from_self(self, ip: str) -> bool:
        return ip == self.config.self_ip

    def terminate(self):
        with self.lock:
            self.state = NodeState.TERMINATED
            if self.instance:
                self.instance.terminate()
            self._save_state()


class IntentClass:
    def __init__(self):
        self.leaking_values = []
        self.ranges = {}

    def find_leaking_values(self, data: Dict[str, Any]) -> List[str]:
        leaks = [k for k, v in data.items()
                 if isinstance(v, str) and len(v) > 100]
        self.leaking_values.extend(leaks)
        return leaks

    def lock_to_node(self, node: Node, key: str):
        node.config.credentials[key] = "locked"


class Watchdog:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.worm_detected = False
        self.permitted = True

    def add_node(self, node: Node):
        self.nodes[node.config.node_id] = node

    def monitor_traffic(self):
        for node in self.nodes.values():
            if node.emit_status()['state'] != NodeState.ACTIVE.value:
                node.open_instance()

    def check_worm(self, traffic: Dict[str, Any]) -> bool:
        if 'worm' in str(traffic).lower():
            self.worm_detected = True
            return True
        return False

    def reroute_to_other_node(self, from_node: str, to_node: str,
                               traffic: Dict[str, Any]):
        if to_node in self.nodes:
            self.nodes[to_node].add_traffic(traffic)

    def await_permit(self) -> bool:
        while not self.permitted:
            time.sleep(0.1)
        return self.permitted

    def commit_if_worm_found(self):
        if self.worm_detected:
            for node in self.nodes.values():
                node.save_cache_dump()
            return True
        return False


class BinaryTreeNode:
    def __init__(self, node: Node):
        self.node = node
        self.left = None
        self.right = None

    def insert(self, node: Node):
        if node.config.node_id < self.node.config.node_id:
            if self.left is None:
                self.left = BinaryTreeNode(node)
            else:
                self.left.insert(node)
        else:
            if self.right is None:
                self.right = BinaryTreeNode(node)
            else:
                self.right.insert(node)

    def search(self, node_id: str) -> Optional['BinaryTreeNode']:
        if node_id == self.node.config.node_id:
            return self
        elif node_id < self.node.config.node_id:
            return self.left.search(node_id) if self.left else None
        else:
            return self.right.search(node_id) if self.right else None


# ---------------------------------------------------------------------------
# NeuralMatcherChain  (vsync-driven, binary permit enforcement)
# ---------------------------------------------------------------------------

class NeuralMatcherChain:
    """
    Chain-node sequence with vsync binary state encoding:

    Cycle per resolve() call:
      1. VsyncEncoder re-codes all execution parameters to 0/1.
      2. 'domain_permit' bit must be 1 (key-unlocked) before any TCP probe runs.
      3. node_001 (head) discovers the open localhost port and resolves the
         external hostname via DNS.
      4. node_002 (matcher) scores (gateway × port) candidates via live TCP
         to the *external* resolved IP.  Subnet fallback is never used.
      5. Best-scoring config — including its permit_bit=1 and the connect_key —
         is saved to disk.  On the next call the saved config is replayed if
         the TCP path is still alive and the permit bit is still 1.

    Vsync rules:
      permit_bit = 1  →  execution parameter update allowed, TCP probe runs
      permit_bit = 0  →  all probes blocked, chain returns None immediately
    """

    CANDIDATE_PORTS: List[int] = [80, 443, 8080, 8443, 3000, 5000, 8000]
    SAVED_CONFIG_FILE: str = "resolved_connection.json"
    PARAM_DOMAIN_PERMIT = "domain_permit"
    PARAM_TCP_EXEC      = "tcp_exec"
    PARAM_CONFIG_UPDATE = "config_update"

    def __init__(self, node_001: Node, node_002: Node):
        self.head    = node_001   # chain initiator
        self.matcher = node_002   # neural scorer / TCP prober
        self._lock   = threading.Lock()
        self._saved: Optional[ResolvedConnectionConfig] = None
        # shared vsync encoder — both nodes can inspect it
        self.vsync   = VsyncEncoder()
        self._load_saved_config()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load_saved_config(self):
        if os.path.exists(self.SAVED_CONFIG_FILE):
            try:
                with open(self.SAVED_CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                cfg = ResolvedConnectionConfig(**data)
                # Only restore if permit_bit was 1 at save time
                if cfg.permit_bit == 1:
                    self._saved = cfg
                    self.head._log_traffic({'action': 'chain_loaded_saved_config',
                                            'config': data})
            except (json.JSONDecodeError, TypeError, KeyError):
                self._saved = None

    def _persist_config(self, cfg: ResolvedConnectionConfig):
        with open(self.SAVED_CONFIG_FILE, 'w') as f:
            json.dump(cfg.to_dict(), f, indent=2)
        self._saved = cfg
        entry = {'action': 'chain_config_saved', 'config': cfg.to_dict()}
        self.head._log_traffic(entry)
        self.matcher._log_traffic(entry)

    # ------------------------------------------------------------------
    # Vsync pass — re-code all params, enforce permit bit
    # ------------------------------------------------------------------

    def _vsync_pass(self, connect_key: str, domain_hint: str) -> int:
        """
        Run a vsync cycle: re-encode all three execution parameters.
        Returns the domain_permit bit (0 or 1).
        connect_key is the credential that gates the external domain permit.
        """
        permit = self.vsync.encode_param(
            self.PARAM_DOMAIN_PERMIT, connect_key, domain_hint)
        self.vsync.encode_param(
            self.PARAM_TCP_EXEC, connect_key, domain_hint)
        self.vsync.encode_param(
            self.PARAM_CONFIG_UPDATE, connect_key, domain_hint)

        self.head._log_traffic({
            'action': 'vsync_pass',
            'domain_hint': domain_hint,
            'params': self.vsync.sync(domain_hint)   # second sync → stable
        })
        return permit

    # ------------------------------------------------------------------
    # Step 1 — discover open localhost port
    # ------------------------------------------------------------------

    def _probe_localhost_port(self) -> Optional[int]:
        for port in self.CANDIDATE_PORTS:
            try:
                s = socket.create_connection(('127.0.0.1', port), timeout=1)
                s.close()
                self.head._log_traffic({'action': 'chain_localhost_port_found',
                                        'port': port})
                return port
            except (socket.timeout, socket.error):
                continue
        return None

    # ------------------------------------------------------------------
    # Step 2 — head handoff: DNS resolve + localhost confirm
    # ------------------------------------------------------------------

    def _head_handoff(self, uri: str,
                      local_port: int) -> Tuple[Optional[str], Optional[int]]:
        resolved_ip = self.head.extract_ip_from_uri(uri)
        if not resolved_ip:
            self.head._log_traffic({'action': 'chain_head_dns_fail', 'uri': uri})
            return None, None
        try:
            s = socket.create_connection(('127.0.0.1', local_port), timeout=1)
            s.close()
        except (socket.timeout, socket.error):
            self.head._log_traffic({'action': 'chain_head_localhost_port_closed',
                                    'port': local_port})
            return None, None
        self.head._log_traffic({'action': 'chain_head_handoff',
                                 'uri': uri,
                                 'resolved_ip': resolved_ip,
                                 'local_port': local_port})
        return resolved_ip, local_port

    # ------------------------------------------------------------------
    # Step 3 — matcher scores candidates via TCP to external IP only
    # ------------------------------------------------------------------

    def _score_candidate(self, resolved_ip: str, port: int,
                         gateway: str, local_port: int) -> float:
        """
        TCP to resolved_ip:port is REQUIRED — no subnet fallback.
        Returns 0.0 if the external TCP connection fails.
        """
        # Gate: tcp_exec param must be 1
        if not self.vsync.permit_granted(self.PARAM_TCP_EXEC):
            return 0.0

        start = time.monotonic()
        try:
            s = socket.create_connection((resolved_ip, port), timeout=3)
            s.close()
            latency = time.monotonic() - start
        except (socket.timeout, socket.error):
            return 0.0

        gw_bonus = 0.0
        try:
            s = socket.create_connection((gateway, port), timeout=2)
            s.close()
            gw_bonus = 0.15
        except (socket.timeout, socket.error):
            pass

        port_bonus   = {443: 0.20, 80: 0.15, 8443: 0.10, 8080: 0.05}.get(port, 0.0)
        latency_score = max(0.0, (3.0 - latency) / 3.0) * 0.65
        score = round(min(1.0, latency_score + gw_bonus + port_bonus), 4)

        self.matcher._log_traffic({
            'action': 'chain_candidate_scored',
            'resolved_ip': resolved_ip,
            'port': port, 'gateway': gateway,
            'local_port': local_port,
            'latency': round(latency, 4),
            'score': score,
            'permit_bit': 1
        })
        return score

    def _matcher_evaluate(self, resolved_ip: str, local_port: int,
                           gateway_list: List[str], connect_key: str,
                           uri: str) -> Optional[ResolvedConnectionConfig]:
        best: Optional[ResolvedConnectionConfig] = None
        best_score = 0.0

        for gateway in gateway_list:
            for port in self.CANDIDATE_PORTS:
                score = self._score_candidate(resolved_ip, port,
                                              gateway, local_port)
                if score > best_score:
                    best_score = score
                    best = ResolvedConnectionConfig(
                        uri=uri,
                        resolved_ip=resolved_ip,
                        reachable_port=port,
                        local_port=local_port,
                        gateway_used=gateway,
                        score=score,
                        permit_bit=1,
                        connect_key=connect_key
                    )
        return best

    # ------------------------------------------------------------------
    # Await routing — mutual buffer hold through local subnet entry
    # ------------------------------------------------------------------

    def _route_buffer_through_subnet(self, payload: Dict[str, Any],
                                     local_port: int):
        """
        Keep the connection buffer payload circulating through 127.0.0.1:local_port
        while both nodes await each other.  Logs each routing pass so the buffer
        is never dropped during the handshake window.
        """
        try:
            s = socket.create_connection(('127.0.0.1', local_port), timeout=1)
            s.close()
            self.head._log_traffic({
                'action':     'buffer_routed_subnet',
                'local_port': local_port,
                'payload':    payload
            })
            self.matcher._log_traffic({
                'action':     'buffer_routed_subnet',
                'local_port': local_port,
                'payload':    payload
            })
        except (socket.timeout, socket.error):
            pass

    def await_routing(self, uri_001: str, uri_002: str,
                      connect_key: str = "",
                      buffer_payload: Optional[Dict[str, Any]] = None
                      ) -> Optional[HandshakeLock]:
        """
        Resolve both node URIs and run WaveHandshake so both nodes await each
        other before the lock is established.

        The establish point is the shared localhost entry port (127.0.0.1:LOCALHOST_PORT).
        Both nodes resolve their own URI for TCP scoring but the mutual await
        and lock are anchored to the local port — not between two external domains.
        The connection buffer payload routes through that local port during the
        entire await window so it is never dropped.

        Returns a HandshakeLock or None.
        """
        # Check for an existing valid lock first
        existing = HandshakeLock.from_file(WaveHandshake.LOCK_FILE)
        if existing:
            try:
                s1 = socket.create_connection(
                    (existing.node_001_ip, existing.node_001_port), timeout=2)
                s1.close()
                s2 = socket.create_connection(
                    (existing.node_002_ip, existing.node_002_port), timeout=2)
                s2.close()
                self.head._log_traffic({'action': 'handshake_reusing_lock',
                                        'lock': existing.to_dict()})
                return existing
            except (socket.timeout, socket.error):
                os.remove(WaveHandshake.LOCK_FILE)

        # Discover the shared localhost entry port — this is the actual
        # establish point both nodes route through
        local_port = self._probe_localhost_port()
        if local_port is None:
            self.head._log_traffic({'action': 'await_routing_no_localhost_port'})
            return None

        # Resolve node_001 URI (head node) via TCP scoring
        cfg1 = self.resolve(uri_001, connect_key=connect_key)
        if cfg1 is None:
            self.head._log_traffic({'action': 'await_routing_cfg1_fail',
                                    'uri': uri_001})
            return None

        # Resolve node_002 URI (matcher node) — DNS only, no external TCP
        # required since the lock establish point is localhost
        cfg2_ip = self.matcher.extract_ip_from_uri(uri_002)
        if cfg2_ip is None:
            self.matcher._log_traffic({'action': 'await_routing_cfg2_dns_fail',
                                       'uri': uri_002})
            return None

        # Build a minimal cfg2 from the matcher's resolved IP.
        # Use cfg1's proven port as the candidate — matcher shares the same
        # external reachability since both nodes are on the same local network.
        cfg2 = ResolvedConnectionConfig(
            uri          = uri_002,
            resolved_ip  = cfg2_ip,
            reachable_port = cfg1.reachable_port,
            local_port   = local_port,
            gateway_used = cfg1.gateway_used,
            score        = cfg1.score,
            permit_bit   = 1,
            connect_key  = connect_key,
        )

        # Route buffer through local subnet entry while awaiting
        bp = buffer_payload or {'action': 'await_buffer',
                                 'uri_001': uri_001, 'uri_002': uri_002}
        self._route_buffer_through_subnet(bp, local_port)

        # Run wave handshake — both nodes await each other over local port
        hs   = WaveHandshake(self.head, self.matcher)
        lock = hs.run(cfg1, cfg2, local_port, connect_key)

        # Final buffer route once locked
        if lock:
            self._route_buffer_through_subnet(
                {'action': 'post_lock_buffer', 'lock_ts': lock.timestamp},
                local_port
            )
        return lock

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def resolve(self, uri: str,
                connect_key: str = "") -> Optional[ResolvedConnectionConfig]:
        """
        Full vsync chain:
          vsync_pass (0/1 re-code) → localhost port → head handoff →
          matcher TCP scoring → persist config.

        connect_key is the credential that must produce permit_bit=1 to
        allow the external domain TCP probe to run.
        If permit_bit stays 0 after vsync, the chain returns None immediately.
        """
        with self._lock:
            # Extract domain hint from URI for vsync encoding
            m = re.search(r'https?://([^/:]+)', uri)
            domain_hint = m.group(1) if m else uri

            # --- Vsync pass: re-code all execution parameters ---
            permit_bit = self._vsync_pass(connect_key, domain_hint)

            if permit_bit == 0:
                self.head._log_traffic({
                    'action': 'chain_blocked_permit_bit_0',
                    'uri': uri, 'domain_hint': domain_hint,
                    'connect_key_provided': bool(connect_key)
                })
                return None

            # Fast-path: saved config still has live TCP path
            if self._saved and self._saved.permit_bit == 1:
                try:
                    s = socket.create_connection(
                        (self._saved.resolved_ip, self._saved.reachable_port),
                        timeout=2)
                    s.close()
                    self.head._log_traffic({'action': 'chain_using_saved_config',
                                            'config': self._saved.to_dict()})
                    return self._saved
                except (socket.timeout, socket.error):
                    self._saved = None

            # Step 1
            local_port = self._probe_localhost_port()
            if local_port is None:
                self.head._log_traffic({'action': 'chain_no_localhost_port'})
                return None

            # Step 2
            resolved_ip, confirmed_port = self._head_handoff(uri, local_port)
            if resolved_ip is None:
                return None

            # Step 3
            best = self._matcher_evaluate(
                resolved_ip, confirmed_port,
                self.head.config.gateway_list,
                connect_key, uri
            )

            if best is None:
                self.matcher._log_traffic({
                    'action': 'chain_no_viable_tcp_path',
                    'resolved_ip': resolved_ip,
                    'permit_bit': permit_bit
                })
                return None

            # Gate: config_update param must be 1 before persisting
            if self.vsync.permit_granted(self.PARAM_CONFIG_UPDATE):
                self._persist_config(best)
            else:
                self.head._log_traffic({
                    'action': 'chain_config_update_blocked',
                    'permit_bit': 0
                })

            return best


# ---------------------------------------------------------------------------
# ServerClassManager
# ---------------------------------------------------------------------------

class ServerClassManager:
    def __init__(self):
        self.tree = None
        self.watchdog = Watchdog()
        self.self_node_id: Optional[str] = None
        self._chain: Optional[NeuralMatcherChain] = None

    def set_self_node(self, node_id: str):
        self.self_node_id = node_id

    def init_chain(self, node_001: Node, node_002: Node):
        """Initialise the NeuralMatcherChain once both nodes are registered."""
        self._chain = NeuralMatcherChain(node_001, node_002)

    def establish_session_link_via_payload(self, payload: Dict[str, Any]) -> bool:
        """
        Session link established only when WaveHandshake locks both URI nodes
        via TCP-proven configs with permit_bit=1.
        Saves handshake_lock.json as the persistent establish-point.

        uri_001 comes from payload['uri'] (= node_001's config URI from env).
        uri_002 is derived from the matcher node's config URI so it always
        reflects what's in the env — never hardcoded.
        The mutual await routes through 127.0.0.1:LOCALHOST_PORT, not between
        the two external URIs directly.
        """
        if 'uri' not in payload:
            return False
        if self._chain is None:
            return False

        uri_001     = payload['uri']
        connect_key = payload.get('connect_key', '')

        # Always derive uri_002 from the matcher node's env config,
        # falling back to payload only if explicitly overridden
        uri_002 = payload.get('uri_002') or self._chain.matcher.config.uri

        self_node = self.tree_query(self.self_node_id) if self.self_node_id else None
        if self_node:
            self_node.load_pkl_session_from_payload(payload)

        # Run mutual await routing handshake — establish point is localhost
        if uri_002:
            lock = self._chain.await_routing(
                uri_001, uri_002,
                connect_key=connect_key,
                buffer_payload=payload
            )
            if lock is None:
                return False
            if self_node:
                self_node._log_traffic({
                    'action':     'session_link_established_via_handshake',
                    'lock':       lock.to_dict(),
                    'wave_state': '0x11'
                })
            return True

        # Single URI fallback — standard neural matcher resolve
        cfg = self._chain.resolve(uri_001, connect_key=connect_key)
        if cfg is None:
            return False
        if self_node:
            self_node._log_traffic({
                'action':      'session_link_established',
                'uri':         uri_001,
                'resolved_ip': cfg.resolved_ip,
                'port':        cfg.reachable_port,
                'gateway':     cfg.gateway_used,
                'local_port':  cfg.local_port,
                'score':       cfg.score,
                'permit_bit':  cfg.permit_bit,
                'connect_key': cfg.connect_key
            })
        return True

    def add_node(self, node: Node):
        self.watchdog.add_node(node)
        if self.tree is None:
            self.tree = BinaryTreeNode(node)
        else:
            self.tree.insert(node)

    def organize_via_git_tree(self, repo_path: str):
        try:
            result = subprocess.run(
                ['git', '-C', repo_path, 'ls-tree', '-r', '--name-only', 'HEAD'],
                capture_output=True, text=True)
            return result.stdout.split('\n') if result.returncode == 0 else []
        except Exception:
            return []

    def expand_cache_sessions(self):
        for node in self.watchdog.nodes.values():
            node.save_cache_dump()

    def tree_query(self, node_id: str) -> Optional[Node]:
        if self.tree:
            result = self.tree.search(node_id)
            return result.node if result else None
        return None

    def check_credential(self, node_id: str, credential: str) -> bool:
        node = self.tree_query(node_id)
        if node:
            return credential in node.config.credentials.values()
        return False


class SupersamplingMethod:
    def __init__(self):
        self.back_gate_queries = []
        self.space_fragments   = []

    def reach_connectors(self, node: Node) -> List[str]:
        return node.config.connectors

    def query_space_fragments(self, query: str) -> List[Dict[str, Any]]:
        return [f for f in self.space_fragments
                if query in f.get('content', '')]

    def reconstruct_cache(self, dump_location: str) -> Dict[str, Any]:
        if os.path.exists(dump_location):
            with open(dump_location, 'rb') as f:
                return pickle.load(f)
        return {}


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def load_config_from_env() -> Dict[str, Any]:
    load_dotenv()
    gateway_list       = os.getenv('GATEWAY_LIST',
                                   '192.168.1.1,192.168.1.254,10.0.0.1').split(',')
    localhost_endpoint = os.getenv('LOCALHOST_ENDPOINT', 'http://127.0.0.1:8080')
    library_path       = os.getenv('LIBRARY_PATH',
                                   '/usr/local/lib/python3.x/site-packages')

    return {
        'node_001': NodeConfig(
            node_id            = os.getenv('NODE_001_ID',                'node_001'),
            venv_path          = os.getenv('NODE_001_VENV_PATH',         '/tmp/venv1'),
            python_executable  = os.getenv('NODE_001_PYTHON_EXECUTABLE', 'python3'),
            connectors         = os.getenv('NODE_001_CONNECTORS',
                                           'connector_a,connector_b').split(','),
            credentials        = {'key': os.getenv('NODE_001_CREDENTIALS_KEY',
                                                    'value123')},
            self_ip            = os.getenv('NODE_001_SELF_IP',   '192.168.1.100'),
            ip_mask            = os.getenv('NODE_001_IP_MASK',   '255.255.255.0'),
            gateway            = os.getenv('NODE_001_GATEWAY',   '192.168.1.1'),
            uri                = os.getenv('NODE_001_URI',        'http://example.com/data'),
            localhost_endpoint = localhost_endpoint,
            gateway_list       = gateway_list,
            library_path       = library_path,
        ),
        'node_002': NodeConfig(
            node_id            = os.getenv('NODE_002_ID',                'node_002'),
            venv_path          = os.getenv('NODE_002_VENV_PATH',         '/tmp/venv2'),
            python_executable  = os.getenv('NODE_002_PYTHON_EXECUTABLE', 'python3'),
            connectors         = os.getenv('NODE_002_CONNECTORS',
                                           'connector_c,connector_d').split(','),
            credentials        = {'key': os.getenv('NODE_002_CREDENTIALS_KEY',
                                                    'value456')},
            self_ip            = os.getenv('NODE_002_SELF_IP',   '192.168.1.101'),
            ip_mask            = os.getenv('NODE_002_IP_MASK',   '255.255.255.0'),
            gateway            = os.getenv('NODE_002_GATEWAY',   '192.168.1.1'),
            uri                = os.getenv('NODE_002_URI',        'http://example.com/data2'),
            localhost_endpoint = localhost_endpoint,
            gateway_list       = gateway_list,
            library_path       = library_path,
        ),
        'self_node_id':             os.getenv('SELF_NODE_ID',                'node_002'),
        'source_object_query_pattern': os.getenv('SOURCE_OBJECT_QUERY_PATTERN', '*.py'),
        'connect_key':              os.getenv('CONNECT_KEY',                 ''),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    manager      = ServerClassManager()
    intent       = IntentClass()
    supersampling = SupersamplingMethod()

    env_config     = load_config_from_env()
    config1        = env_config['node_001']
    config2        = env_config['node_002']
    self_node_id   = env_config['self_node_id']
    source_pattern = env_config['source_object_query_pattern']
    connect_key    = env_config['connect_key']

    node1 = Node(config1)
    node2 = Node(config2)

    manager.add_node(node1)
    manager.add_node(node2)
    manager.set_self_node(self_node_id)

    # Initialise the NeuralMatcherChain (must be after add_node)
    manager.init_chain(node1, node2)

    node1.link_venv()
    node2.link_venv()

    node1.open_instance()
    node2.open_instance()

    traffic_data = {"source": "external", "payload": "test_data"}
    node1.add_traffic(traffic_data)

    node1.save_cache_dump()
    node2.save_cache_dump()

    localhost_route = node1.route_via_localhost_endpoint({"data": "localhost_test"})
    print(f"Localhost Route: {localhost_route}")

    matched_gateway = node1.match_route_against_gateway_list("192.168.1.100")
    print(f"Matched Gateway: {matched_gateway}")

    if matched_gateway:
        port_acceptance = node1.accept_ports_from_self_after_gateway(matched_gateway)
        print(f"Port Acceptance After Gateway: {port_acceptance}")

    source_objects = node1.query_library_source_objects(source_pattern)
    print(f"Source Objects Found: {len(source_objects)}")
    if source_objects:
        code = node1.load_source_object_code(source_objects[0])
        print(f"Source Code Loaded: {code[:100] if code else 'None'}...")

    payload = {
        "uri":                config1.uri,   # from NODE_001_URI in env
        "pkl_file":           f"cache_node_001/dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl",
        "venv_fetch_command": "print('venv executed')",
        "connect_key":        connect_key,
        # uri_002 is auto-derived from node2.config.uri (NODE_002_URI in env)
    }

    session_link = manager.establish_session_link_via_payload(payload)
    print(f"Session Link Established: {session_link}")

    venv_result = node2.fetch_via_venv_payload(payload)
    print(f"Venv Fetch Result: {venv_result}")

    send_back = node2.send_back_from_self({"data": "response"})
    print(f"Send Back From Self: {send_back}")

    status = node1.emit_status()
    print(f"Node Status: {json.dumps(status, indent=2)}")

    credential_valid = manager.check_credential("node_001", "value123")
    print(f"Credential Valid: {credential_valid}")

    node1.terminate()
    node2.terminate()


if __name__ == "__main__":
    main()
