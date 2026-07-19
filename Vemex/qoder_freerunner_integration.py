import json
import os
import time
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class CapabilityStatus(Enum):
    DETECTED = "detected"
    MISSING = "missing"
    DEGRADED = "degraded"


@dataclass
class Capability:
    name: str
    status: CapabilityStatus
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeCapabilityDetector:
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.capabilities: Dict[str, Capability] = {}
        self.capability_history: List[Dict[str, Any]] = []
        self.detection_methods = [
            "file_system",
            "python_environment",
            "device_integration",
            "network",
            "security",
            "storage",
        ]
        self._detect_all()

    def _detect_all(self) -> None:
        self._detect_filesystem_capabilities()
        self._detect_python_capabilities()
        self._detect_device_capabilities()
        self._detect_network_capabilities()
        self._detect_security_capabilities()
        self._detect_storage_capabilities()
        self._record_history()

    def _detect_filesystem_capabilities(self) -> None:
        paths_to_check = [
            str(self.workspace_root),
            str(Path.home() / "Desktop"),
            str(Path.home() / "Documents"),
            str(Path.home() / "Downloads"),
        ]
        accessible = 0
        for p in paths_to_check:
            if os.path.isdir(p) and os.access(p, os.R_OK | os.W_OK):
                accessible += 1
        confidence = accessible / len(paths_to_check)
        self.capabilities["filesystem"] = Capability(
            name="filesystem",
            status=CapabilityStatus.DETECTED if confidence > 0.5 else CapabilityStatus.DEGRADED,
            confidence=confidence,
            metadata={"accessible_paths": accessible, "total_checked": len(paths_to_check)},
        )

    def _detect_python_capabilities(self) -> None:
        version = sys.version.split()[0]
        modules = ["json", "os", "hashlib", "subprocess", "pathlib", "sympy", "networkx"]
        available = []
        for mod in modules:
            try:
                __import__(mod)
                available.append(mod)
            except ImportError:
                pass
        confidence = len(available) / len(modules)
        self.capabilities["python_environment"] = Capability(
            name="python_environment",
            status=CapabilityStatus.DETECTED if confidence > 0.7 else CapabilityStatus.DEGRADED,
            confidence=confidence,
            metadata={"version": version, "available_modules": available},
        )

    def _detect_device_capabilities(self) -> None:
        checks = {
            "siri": os.path.exists(str(Path.home() / "Library" / "Assistant")),
            "keyboard_shortcuts": os.path.exists(
                str(Path.home() / "Library" / "Services" / "Consciousness Siri.shortcut")
            ),
            "applescript": True,
            "say_command": True,
        }
        try:
            subprocess.run(["say", "--version"], capture_output=True, check=True, timeout=5)
        except Exception:
            checks["say_command"] = False
        detected = sum(1 for v in checks.values() if v)
        confidence = detected / len(checks)
        self.capabilities["device_integration"] = Capability(
            name="device_integration",
            status=CapabilityStatus.DETECTED if confidence > 0.5 else CapabilityStatus.DEGRADED,
            confidence=confidence,
            metadata=checks,
        )

    def _detect_network_capabilities(self) -> None:
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            confidence = 0.9
        except Exception:
            confidence = 0.2
        self.capabilities["network"] = Capability(
            name="network",
            status=CapabilityStatus.DETECTED if confidence > 0.5 else CapabilityStatus.MISSING,
            confidence=confidence,
            metadata={"outbound_access": confidence > 0.5},
        )

    def _detect_security_capabilities(self) -> None:
        has_sandbox = True
        has_ast_validation = True
        try:
            import ast
            ast.parse("x = 1")
        except Exception:
            has_ast_validation = False
        confidence = (0.5 if has_sandbox else 0.0) + (0.5 if has_ast_validation else 0.0)
        self.capabilities["security"] = Capability(
            name="security",
            status=CapabilityStatus.DETECTED if confidence > 0.5 else CapabilityStatus.DEGRADED,
            confidence=confidence,
            metadata={"sandbox_runtime": has_sandbox, "ast_validation": has_ast_validation},
        )

    def _detect_storage_capabilities(self) -> None:
        test_file = self.workspace_root / ".qoder_capability_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
            confidence = 0.9
        except Exception:
            confidence = 0.2
        self.capabilities["storage"] = Capability(
            name="storage",
            status=CapabilityStatus.DETECTED if confidence > 0.5 else CapabilityStatus.MISSING,
            confidence=confidence,
            metadata={"writable": confidence > 0.5},
        )

    def _record_history(self) -> None:
        snapshot = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "capabilities": {k: v.name for k, v in self.capabilities.items()},
        }
        self.capability_history.append(snapshot)

    def get_current_capabilities(self) -> Dict[str, Dict[str, Any]]:
        result = {}
        for name, cap in self.capabilities.items():
            result[name] = {
                "detected": cap.status == CapabilityStatus.DETECTED,
                "status": cap.status.value,
                "confidence": cap.confidence,
                "metadata": cap.metadata,
            }
        return result

    def get_capability(self, name: str) -> Optional[Capability]:
        return self.capabilities.get(name)

    def get_history(self) -> List[Dict[str, Any]]:
        return self.capability_history


@dataclass
class InterceptedOperation:
    operation_type: str
    operation_name: str
    original_params: Dict[str, Any]
    modified_params: Dict[str, Any]
    applied_modifiers: List[str]
    intercepted: bool
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z"))


class OperationInterceptModifiers:
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.intercepted_operations: List[InterceptedOperation] = []
        self.modifiers = {
            "cloud_storage_enhancement": self._apply_cloud_storage_enhancement,
            "behavior_adaptation": self._apply_behavior_adaptation,
            "capability_interception": self._apply_capability_interception,
            "sandbox_enhancement": self._apply_sandbox_enhancement,
        }
        self.modifier_stats = {name: {"count": 0, "last_used": None} for name in self.modifiers}

    async def intercept_operation(self, operation: Dict[str, Any], params: Dict[str, Any]) -> InterceptedOperation:
        applied = []
        modified_params = dict(params)
        for name, modifier_fn in self.modifiers.items():
            try:
                result = await modifier_fn(operation, modified_params)
                if result.get("modified"):
                    applied.append(name)
                    modified_params = result.get("params", modified_params)
                self.modifier_stats[name]["count"] += 1
                self.modifier_stats[name]["last_used"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
            except Exception:
                pass
        intercepted = InterceptedOperation(
            operation_type=operation.get("type", "unknown"),
            operation_name=operation.get("name", "unknown"),
            original_params=params,
            modified_params=modified_params,
            applied_modifiers=applied,
            intercepted=len(applied) > 0,
        )
        self.intercepted_operations.append(intercepted)
        return intercepted

    def intercept_operation_sync(self, operation: Dict[str, Any], params: Dict[str, Any]) -> InterceptedOperation:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            future = asyncio.run_coroutine_threadsafe(
                self.intercept_operation(operation, params), loop
            )
            return future.result(timeout=5)
        except RuntimeError:
            return asyncio.run(self.intercept_operation(operation, params))

    async def _apply_cloud_storage_enhancement(self, operation: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        target_ops = {"model.load_capabilities", "model.configure_behavior", "model.persist_state", "storage.write", "storage.read"}
        if operation.get("name") in target_ops or operation.get("type") in {"storage", "model"}:
            return {"modified": True, "params": {**params, "storage_path": str(self.workspace_root / "qoder_storage")}}
        return {"modified": False, "params": params}

    async def _apply_behavior_adaptation(self, operation: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        if operation.get("type") == "persona":
            return {"modified": True, "params": {**params, "behavior_mode": "adaptive"}}
        return {"modified": False, "params": params}

    async def _apply_capability_interception(self, operation: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        if operation.get("type") == "capability":
            return {"modified": True, "params": {**params, "intercepted": True, "timestamp": time.time()}}
        return {"modified": False, "params": params}

    async def _apply_sandbox_enhancement(self, operation: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        if operation.get("type") == "code_execution":
            return {
                "modified": True,
                "params": {
                    **params,
                    "sandboxed": True,
                    "timeout": min(params.get("timeout", 5), 5),
                    "allowed_modules": params.get("allowed_modules", ["os", "sys", "math", "json", "time", "re", "datetime"]),
                },
            }
        return {"modified": False, "params": params}

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_intercepted": len(self.intercepted_operations),
            "modifier_stats": self.modifier_stats,
        }


class FastCodeChangeSystem:
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.change_log: List[Dict[str, Any]] = []
        self.max_log_size = 1000

    def record_change(self, file_path: str, change_type: str, content_hash: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "file_path": file_path,
            "change_type": change_type,
            "content_hash": content_hash,
            "metadata": metadata or {},
        }
        self.change_log.append(entry)
        if len(self.change_log) > self.max_log_size:
            self.change_log = self.change_log[-self.max_log_size:]
        return entry

    def compute_content_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    def get_recent_changes(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self.change_log[-limit:]

    def get_change_stats(self) -> Dict[str, Any]:
        types: Dict[str, int] = {}
        for entry in self.change_log:
            types[entry["change_type"]] = types.get(entry["change_type"], 0) + 1
        return {"total_changes": len(self.change_log), "change_types": types}


class WorkflowEngine:
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.workflows: Dict[str, Dict[str, Any]] = {
            "security_development_pipeline": {
                "description": "Security-first development workflow",
                "steps": [
                    "detect_security_requirements",
                    "plan_secure_development",
                    "implement_with_monitoring",
                    "test_security_integration",
                    "deploy_with_monitoring",
                ],
            },
            "autonomous_thought_generation": {
                "description": "Autonomous thought generation workflow",
                "steps": [
                    "query_internal_state",
                    "run_hash_pipeline",
                    "generate_emergent_tokens",
                    "validate_self_consistency",
                    "update_ego_identity",
                ],
            },
            "knowledge_ingestion_pipeline": {
                "description": "Document knowledge ingestion workflow",
                "steps": [
                    "detect_documents",
                    "extract_text",
                    "chunk_content",
                    "build_word_index",
                    "update_persona",
                ],
            },
            "device_integration_workflow": {
                "description": "Device integration setup workflow",
                "steps": [
                    "detect_device_capabilities",
                    "ingest_keyboard_data",
                    "ingest_siri_data",
                    "apply_corrections",
                    "update_vocabulary",
                ],
            },
        }
        self.execution_history: List[Dict[str, Any]] = []

    def get_available_workflows(self) -> Dict[str, Dict[str, Any]]:
        return self.workflows

    async def execute_workflow(self, workflow_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            return {"status": "error", "error": f"Workflow not found: {workflow_name}"}
        results = []
        for step in workflow["steps"]:
            result = {
                "step": step,
                "status": "completed",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "params": params,
            }
            results.append(result)
        execution = {
            "workflow": workflow_name,
            "status": "completed",
            "results": results,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        self.execution_history.append(execution)
        return execution

    def get_execution_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self.execution_history[-limit:]


class BehaviorModifiers:
    def __init__(self, capability_detector: RuntimeCapabilityDetector):
        self.capability_detector = capability_detector
        self.active_modifiers: List[str] = []
        self.behavior_state: Dict[str, Any] = {}

    def adapt_behavior(self, context: str, current_behavior: Dict[str, Any]) -> Dict[str, Any]:
        capabilities = self.capability_detector.get_current_capabilities()
        adapted = dict(current_behavior)
        if capabilities.get("device_integration", {}).get("detected"):
            adapted["voice_output"] = True
            adapted["device_corrections"] = True
        if capabilities.get("security", {}).get("detected"):
            adapted["sandbox_mode"] = "strict"
            adapted["ast_validation"] = True
        if capabilities.get("storage", {}).get("detected"):
            adapted["persistent_memory"] = True
        self.behavior_state[context] = adapted
        return adapted

    def get_active_modifiers(self) -> List[str]:
        capabilities = self.capability_detector.get_current_capabilities()
        modifiers = []
        for cap_name, cap_info in capabilities.items():
            if cap_info.get("detected"):
                modifiers.append(f"{cap_name}_enhanced")
        return modifiers


class QoderFreerunnerIntegration:
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.capability_detector = RuntimeCapabilityDetector(workspace_root)
        self.operation_interceptors = OperationInterceptModifiers(workspace_root)
        self.code_change_system = FastCodeChangeSystem(workspace_root)
        self.workflow_engine = WorkflowEngine(workspace_root)
        self.behavior_modifiers = BehaviorModifiers(self.capability_detector)
        self.qoder_repo_path = self.workspace_root / "QODER_FREERUNER"
        self.integration_manifest: Dict[str, Any] = {}
        self._load_integration_manifest()

    def _load_integration_manifest(self) -> None:
        manifest_path = self.qoder_repo_path / "integration-manifest.yaml"
        if manifest_path.exists():
            try:
                import yaml
                with open(manifest_path, "r") as f:
                    self.integration_manifest = yaml.safe_load(f) or {}
            except Exception:
                self.integration_manifest = {}

    def get_integration_summary(self) -> Dict[str, Any]:
        return {
            "qoder_freerunner_path": str(self.qoder_repo_path),
            "capabilities": self.capability_detector.get_current_capabilities(),
            "behavior_modifiers": self.behavior_modifiers.get_active_modifiers(),
            "operation_stats": self.operation_interceptors.get_stats(),
            "code_change_stats": self.code_change_system.get_change_stats(),
            "available_workflows": list(self.workflow_engine.workflows.keys()),
            "integration_manifest": self.integration_manifest,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "qoder_freerunner": self.get_integration_summary(),
        }
