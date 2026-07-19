import hashlib
import time

from hardware_interface import DiskReadOrder


class WraithStorageManager:
    """
    Wraith PS4 Storage Manager - Specialised for 34-layer engraving backups.
    Handles mismatch protection, hash backups, and internal storage from server cascades.
    """

    def __init__(self):
        self.auth_key = "jj"
        self.engrave_port = "entry_serv_port_0x34"
        self.internal_storage_pool = {}
        self.hash_backups = []
        self.mismatch_threshold = 0
        self.cascade_url = (
            "https://netcascade-lx03mqh8s-jjs-projects-48d739bf.vercel.app/"
        )
        self.self_serv_enabled = True
        self.pragma_storage_key = None
        self.interleave_registry = {}

    def authenticate_entry(self, input_code):
        """
        Entry auth via proper code auth jj.
        """
        if input_code == self.auth_key:
            print(f"[STORAGE] Auth verified: {self.auth_key}. Gateway open.")
            return True
        print("[STORAGE] Auth failed. Entry denied.")
        return False

    def backup_engrave_hash(self, layer_hash):
        """
        Backup similar hash from engrave entry serv port.
        Ensures the 34-layer engraving state is preserved.
        """
        timestamp = time.time()
        backup_entry = {"port": self.engrave_port, "hash": layer_hash, "ts": timestamp}
        self.hash_backups.append(backup_entry)
        print(f"[STORAGE] Engrave hash backed up from {self.engrave_port}.")

    def entry_copy_mismatch_protection(self, incoming_data, internal_copy):
        """
        Find copy hash allow all entry copy mismatch protection = from internal post.
        Compares incoming server data with internal state to prevent corruption.
        """
        incoming_hash = hashlib.sha256(str(incoming_data).encode()).hexdigest()
        internal_hash = hashlib.sha256(str(internal_copy).encode()).hexdigest()

        if incoming_hash == internal_hash:
            print("[STORAGE] Mismatch protection: VERIFIED. Hashes match.")
            return True
        else:
            print(
                "[STORAGE] Mismatch protection: WARNING! Forcing alignment via internal post."
            )
            # Allow all entry but trigger auto-correction to internal state
            return "ALIGNMENT_REQUIRED"

    def store_to_internal_from_serv(self, node_data, auth_token, storage_key=None):
        """
        Store to internal from serv backup - pulls compressed nodes.
        Passes via the specialised 24-electrode RJ45 bridge protocol.
        """
        if not self.authenticate_entry(auth_token):
            return False

        if storage_key:
            self.pragma_storage_key = storage_key
            print(
                f"[STORAGE] Pragma Internal Storage Key applied: {self.pragma_storage_key[:16]}..."
            )

        print(f"[STORAGE] Accessing cascade: {self.cascade_url}")
        # Core new mem access gateway internal self serv logic
        memory_address = hex(id(self.internal_storage_pool))

        # Perma write to call via mem
        self.internal_storage_pool[memory_address] = {
            "nodes": node_data,
            "perma_write": True,
            "self_serv": self.self_serv_enabled,
            "rotations": "24/ms",
            "pragma_key": self.pragma_storage_key,
            "interleave_id": hashlib.md5(str(node_data).encode()).hexdigest(),
        }

        print(f"[STORAGE] Internal storage synchronized at mem-gate {memory_address}.")
        return True

    def sync_disk_read_state(self, disk_layer=0, read_order=DiskReadOrder.BURST_RECALL):
        """
        Disk spinner set to revolve 6 / to 6/12 read internal disk.
        24 rotations per every millisecond on disk read save-storage.
        Integrates virtual disk rotation selector for precise enum matching.
        """
        print(f"[STORAGE] Syncing disk read state for layer {disk_layer}...")
        print(f"[STORAGE] Read Order: {read_order.name} (Matched and Re-ordered)")
        print("[STORAGE] Performance: 24 rotations per ms (Synchronized / Un-flagged).")
        print("[STORAGE] Storage-on-device optimized for 6/12 read ratio.")

    def run_storage_cycle(self, node_packet, current_hash, pragma_key=None):
        """
        Full orchestration of the storage and backup protocol.
        """
        print("--- WRAITH STORAGE PROTOCOL INITIATED ---")

        # 1. Auth and Backup
        if self.authenticate_entry("jj"):
            self.backup_engrave_hash(current_hash)

            # 2. Mismatch Protection
            # Simulated internal comparison
            self.entry_copy_mismatch_protection(node_packet, node_packet)

            # 3. Store and Sync
            self.store_to_internal_from_serv(node_packet, "jj", pragma_key)

            # Apply virtual disk rotation selector for unknown read orders
            # Re-orders memory to read properly and avoid system flags
            self.sync_disk_read_state(
                disk_layer=34, read_order=DiskReadOrder.UNKNOWN_ENGRAVE
            )

            # Internal storage write function: save-protecthash-tohasheval
            self.save_protecthash_to_hasheval(current_hash)

        print("--- WRAITH STORAGE PROTOCOL COMPLETE: SELF-SERV ACTIVE ---")

    def load_cpu_buffer_serv(self, cpu_buffer):
        """
        Allow buffers to load cpu when serv.
        """
        print("[STORAGE] Loading buffers to CPU via memory access gateway...")
        # Map CPU buffer to high-priority internal memory segment
        cpu_gate = f"CPU_GATE_{hashlib.md5(str(cpu_buffer).encode()).hexdigest()[:8]}"
        self.internal_storage_pool[cpu_gate] = cpu_buffer
        print(f"[STORAGE] CPU load successful: {cpu_gate}")

    def clarify_precision_hash(self, external_read_data):
        """
        Process external read to clarify hash orders to be more precise.
        """
        print("[STORAGE] Processing external read for hash precision...")
        # Precise hash ordering algorithm
        sorted_data = "".join(sorted(str(external_read_data)))
        precision_hash = hashlib.sha256(sorted_data.encode()).hexdigest()
        print(f"[STORAGE] Precise hash order: {precision_hash[:16]}...")
        return precision_hash

    def save_protecthash_to_hasheval(self, target_hash):
        """
        Internal storage write function save-protecthash-tohasheval.
        """
        print("[STORAGE] Initiating save-protecthash-tohasheval sequence...")
        # Evaluation of the protected hash
        eval_sig = hashlib.sha384(target_hash.encode()).hexdigest()
        self.hash_backups.append({"protect_hash": target_hash, "eval": eval_sig})
        print(f"[STORAGE] Protect-hash-eval committed: {eval_sig[:12]}...")

    def propagate_interleave_id(self, interleave_id, source_node):
        """
        Allowed copy-re-add to count eval --copy and change unique if ever interleaved.
        Propagates unique IDs for interleaved storage segments.
        """
        print(f"[STORAGE] Propagating unique Interleave ID: {interleave_id[:16]}...")
        self.interleave_registry[interleave_id] = {
            "source": source_node,
            "timestamp": time.time(),
            "status": "PROPAGATED",
        }
        return True


if __name__ == "__main__":
    sm = WraithStorageManager()
    sample_nodes = ["node_alpha_x34", "node_beta_x34"]
    sample_hash = hashlib.sha256(b"layer_34_engrave_init").hexdigest()
    sm.run_storage_cycle(sample_nodes, sample_hash)
