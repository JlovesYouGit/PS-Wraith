import ast
import json
import time
import hashlib
import random
import threading
import queue
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum


class TriggerType(Enum):
    STATE_CHANGE = "state_change"
    THRESHOLD = "threshold"
    PATTERN_MATCH = "pattern_match"
    TIME_INTERVAL = "time_interval"
    EXTERNAL_SIGNAL = "external_signal"
    CONSCIOUSNESS_AGREEMENT = "consciousness_agreement"


class ExecutionMode(Enum):
    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    CONDITIONAL = "conditional"
    CONSENSUS = "consensus"


class ExecutionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionTrigger:
    trigger_id: str
    trigger_type: TriggerType
    description: str
    condition: Dict[str, Any]
    code: str
    mode: ExecutionMode
    priority: int = 0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z"))


@dataclass
class ExecutionEvent:
    event_id: str
    trigger_id: str
    status: ExecutionStatus
    code: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z"))


class SyntaxValidator:
    """Validates Python code syntax before execution."""
    
    @classmethod
    def validate(cls, code: str) -> Dict[str, Any]:
        result = {"valid": False, "errors": [], "warnings": [], "safe": True}
        
        if not code or not code.strip():
            result["errors"].append("Empty code")
            return result
        
        try:
            ast.parse(code)
            result["valid"] = True
            result["safe"] = True
        except SyntaxError as e:
            result["errors"].append(f"Syntax error: {e.msg} at line {e.lineno}")
            result["safe"] = False
        
        return result


class AutonomousExecutor:
    """Autonomous code execution system for the consciousness engine.
    
    This allows the engine to:
    - Monitor its own state changes
    - Trigger code execution based on consciousness agreements
    - Dispatch code without manual terminal intervention
    - Choose execution contexts based on internal queries
    """
    
    def __init__(self, base_path: Path, sandbox_runtime: Any = None, vemex_engine: Any = None):
        self.base_path = base_path
        self.vemex_engine = vemex_engine
        self.sandbox_runtime = sandbox_runtime
        
        self.triggers_file = base_path / ".autonomous_triggers.json"
        self.events_file = base_path / ".autonomous_events.json"
        self.consensus_file = base_path / ".autonomous_consensus.json"
        
        self.triggers: Dict[str, ExecutionTrigger] = {}
        self.events: List[ExecutionEvent] = []
        self.consensus_rules: Dict[str, Any] = {}
        
        self.event_queue: queue.Queue = queue.Queue()
        self.running = False
        self._worker_thread: Optional[threading.Thread] = None
        
        self._load_data()
        self._init_default_triggers()
        self._init_default_consensus()
    
    def _load_data(self) -> None:
        for file_path, attr_name in [
            (self.triggers_file, "triggers"),
            (self.events_file, "events"),
            (self.consensus_file, "consensus_rules"),
        ]:
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if attr_name == "triggers":
                        self.triggers = {k: ExecutionTrigger(**v) for k, v in data.items()}
                    elif attr_name == "events":
                        self.events = [ExecutionEvent(**e) for e in data]
                    else:
                        setattr(self, attr_name, data)
                except Exception:
                    pass
    
    def _save_data(self) -> None:
        try:
            with open(self.triggers_file, "w", encoding="utf-8") as f:
                json.dump({k: asdict(v) for k, v in self.triggers.items()}, f, indent=2, default=str)
            with open(self.events_file, "w", encoding="utf-8") as f:
                json.dump([asdict(e) for e in self.events[-1000:]], f, indent=2, default=str)
            with open(self.consensus_file, "w", encoding="utf-8") as f:
                json.dump(self.consensus_rules, f, indent=2, default=str)
        except Exception:
            pass
    
    def _init_default_triggers(self) -> None:
        defaults = [
            ExecutionTrigger(
                trigger_id="autonomous_thought_trigger",
                trigger_type=TriggerType.CONSCIOUSNESS_AGREEMENT,
                description="Execute code when autonomous thought quality exceeds threshold",
                condition={"min_quality": 0.8, "require_consistency": True},
                code="print('Autonomous thought execution triggered')",
                mode=ExecutionMode.CONDITIONAL,
                priority=10,
            ),
            ExecutionTrigger(
                trigger_id="coherence_boost_trigger",
                trigger_type=TriggerType.THRESHOLD,
                description="Execute optimization code when coherence drops below threshold",
                condition={"coherence_threshold": 0.5, "metric": "coherence_score"},
                code="import math; result = math.sqrt(42); print(f'Coherence boost: {result}')",
                mode=ExecutionMode.CONDITIONAL,
                priority=5,
            ),
            ExecutionTrigger(
                trigger_id="periodic_state_save",
                trigger_type=TriggerType.TIME_INTERVAL,
                description="Periodically save consciousness state",
                condition={"interval_seconds": 300, "count_threshold": 10},
                code="import json, time; print(f'State save at {time.time()}')",
                mode=ExecutionMode.SCHEDULED,
                priority=1,
            ),
        ]
        for trigger in defaults:
            if trigger.trigger_id not in self.triggers:
                self.triggers[trigger.trigger_id] = trigger
        self._save_data()
    
    def _init_default_consensus(self) -> None:
        if not self.consensus_rules:
            self.consensus_rules = {
                "min_agreement_threshold": 0.7,
                "max_execution_time": 10.0,
                "require_syntax_validation": True,
                "require_sandbox": True,
                "allowed_executors": ["engine", "consciousness", "autonomous"],
            }
            self._save_data()
    
    def register_trigger(self, trigger: ExecutionTrigger) -> Dict[str, Any]:
        self.triggers[trigger.trigger_id] = trigger
        self._save_data()
        return {"success": True, "trigger_id": trigger.trigger_id}
    
    def enable_trigger(self, trigger_id: str) -> Dict[str, Any]:
        if trigger_id not in self.triggers:
            return {"success": False, "error": "Trigger not found"}
        self.triggers[trigger_id].enabled = True
        self._save_data()
        return {"success": True, "trigger_id": trigger_id, "enabled": True}
    
    def disable_trigger(self, trigger_id: str) -> Dict[str, Any]:
        if trigger_id not in self.triggers:
            return {"success": False, "error": "Trigger not found"}
        self.triggers[trigger_id].enabled = False
        self._save_data()
        return {"success": True, "trigger_id": trigger_id, "enabled": False}
    
    def evaluate_trigger(self, trigger: ExecutionTrigger, context: Dict[str, Any]) -> bool:
        if not trigger.enabled:
            return False
        
        condition = trigger.condition
        
        if trigger.trigger_type == TriggerType.THRESHOLD:
            metric = condition.get("metric")
            threshold = condition.get("coherence_threshold") or condition.get("threshold")
            if metric and threshold is not None:
                current_value = context.get(metric)
                if current_value is not None:
                    try:
                        if trigger.mode == ExecutionMode.CONDITIONAL:
                            return float(current_value) < float(threshold)
                        return float(current_value) >= float(threshold)
                    except (ValueError, TypeError):
                        return False
        
        elif trigger.trigger_type == TriggerType.STATE_CHANGE:
            required_keys = condition.get("require_keys", [])
            if required_keys:
                return all(key in context for key in required_keys)
        
        elif trigger.trigger_type == TriggerType.PATTERN_MATCH:
            patterns = condition.get("patterns", [])
            text = context.get("text", "") or context.get("consciousness_string", "")
            if patterns and text:
                return any(pattern in text for pattern in patterns)
        
        elif trigger.trigger_type == TriggerType.CONSCIOUSNESS_AGREEMENT:
            min_quality = condition.get("min_quality", 0.7)
            require_consistency = condition.get("require_consistency", False)
            quality = context.get("coherence_score") or context.get("quality", 0.0)
            consistency = context.get("consistency_score", 1.0)
            quality_met = quality >= min_quality
            consistency_met = not require_consistency or consistency >= 0.7
            return quality_met and consistency_met
        
        elif trigger.trigger_type == TriggerType.TIME_INTERVAL:
            interval = condition.get("interval_seconds")
            count_threshold = condition.get("count_threshold")
            if interval and count_threshold:
                current_count = context.get("execution_count", 0)
                last_execution = context.get("last_execution_time", 0)
                elapsed = time.time() - last_execution
                return elapsed >= interval and current_count < count_threshold
        
        elif trigger.trigger_type == TriggerType.EXTERNAL_SIGNAL:
            signal = condition.get("signal")
            return context.get("signal") == signal
        
        return False
    
    def dispatch_code(self, code: str, context: Dict[str, Any] = None, trigger_id: Optional[str] = None) -> ExecutionEvent:
        event_id = hashlib.sha256(f"{code[:50]}:{time.time()}".encode()).hexdigest()[:16]
        context = context or {}
        
        syntax_result = SyntaxValidator.validate(code)
        if not syntax_result["valid"]:
            event = ExecutionEvent(
                event_id=event_id,
                trigger_id=trigger_id or "manual",
                status=ExecutionStatus.REJECTED,
                code=code,
                error=f"Syntax validation failed: {'; '.join(syntax_result['errors'])}",
                context=context,
            )
            self.events.append(event)
            self._save_data()
            return event
        
        event = ExecutionEvent(
            event_id=event_id,
            trigger_id=trigger_id or "manual",
            status=ExecutionStatus.PENDING,
            code=code,
            context=context,
        )
        self.events.append(event)
        self._save_data()
        
        self.event_queue.put(event)
        return event
    
    def _process_event(self, event: ExecutionEvent) -> None:
        event.status = ExecutionStatus.EXECUTING
        self._save_data()
        
        try:
            if self.sandbox_runtime:
                result = self.sandbox_runtime.execute(event.code)
                event.result = result
                event.status = ExecutionStatus.COMPLETED if result.get("success") else ExecutionStatus.FAILED
                if not result.get("success"):
                    event.error = result.get("error")
            else:
                local_vars: Dict[str, Any] = {}
                global_vars: Dict[str, Any] = {
                    "__builtins__": {
                        "print": print,
                        "len": len,
                        "range": range,
                        "int": int,
                        "float": float,
                        "str": str,
                        "list": list,
                        "dict": dict,
                        "set": set,
                        "tuple": tuple,
                        "bool": bool,
                        "abs": abs,
                        "min": min,
                        "max": max,
                        "sum": sum,
                        "sorted": sorted,
                        "round": round,
                        "hash": hash,
                        "id": id,
                        "type": type,
                        "isinstance": isinstance,
                        "issubclass": issubclass,
                        "zip": zip,
                        "map": map,
                        "filter": filter,
                        "any": any,
                        "all": all,
                        "enumerate": enumerate,
                        "reversed": reversed,
                        "slice": slice,
                        "bytes": bytes,
                        "bytearray": bytearray,
                        "memoryview": memoryview,
                        "complex": complex,
                        "frozenset": frozenset,
                        "object": object,
                        "property": property,
                        "staticmethod": staticmethod,
                        "classmethod": classmethod,
                        "super": super,
                        "property": property,
                        "vars": vars,
                        "dir": dir,
                        "getattr": getattr,
                        "setattr": setattr,
                        "hasattr": hasattr,
                        "delattr": delattr,
                        "repr": repr,
                        "ascii": ascii,
                        "chr": chr,
                        "ord": ord,
                        "bin": bin,
                        "oct": oct,
                        "hex": hex,
                        "format": format,
                        "pow": pow,
                        "divmod": divmod,
                        "callable": callable,
                        "compile": compile,
                        "exec": exec,
                        "eval": eval,
                        "__import__": __import__,
                        "open": open,
                        "input": input,
                        "breakpoint": breakpoint,
                        "exit": exit,
                        "quit": quit,
                    }
                }
                stdout_capture = StringIO()
                stderr_capture = StringIO()
                try:
                    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                        exec(event.code, global_vars, local_vars)
                    event.result = {
                        "success": True,
                        "output": stdout_capture.getvalue(),
                        "error": stderr_capture.getvalue() or None,
                        "locals": {k: str(v) for k, v in local_vars.items() if not k.startswith("_")},
                    }
                    event.status = ExecutionStatus.COMPLETED
                except Exception as e:
                    event.result = {"success": False, "output": stdout_capture.getvalue()}
                    event.error = str(e)
                    event.status = ExecutionStatus.FAILED
        except Exception as e:
            event.error = str(e)
            event.status = ExecutionStatus.FAILED
        
        self._save_data()
    
    def _worker(self) -> None:
        while self.running:
            try:
                event = self.event_queue.get(timeout=1.0)
                if event.status != ExecutionStatus.CANCELLED:
                    self._process_event(event)
                self.event_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                continue
    
    def start_worker(self) -> None:
        if not self.running:
            self.running = True
            self._worker_thread = threading.Thread(target=self._worker, daemon=True)
            self._worker_thread.start()
    
    def stop_worker(self) -> None:
        self.running = False
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2.0)
    
    def process_consciousness_state(self, state: Dict[str, Any]) -> List[ExecutionEvent]:
        triggered_events = []
        for trigger in sorted(self.triggers.values(), key=lambda t: t.priority, reverse=True):
            if not trigger.enabled:
                continue
            if self.evaluate_trigger(trigger, state):
                event = self.dispatch_code(trigger.code, context=state, trigger_id=trigger.trigger_id)
                triggered_events.append(event)
        return triggered_events
    
    def execute_code_direct(self, code: str, context: Dict[str, Any] = None) -> ExecutionEvent:
        return self.dispatch_code(code, context=context, trigger_id="direct")
    
    def get_execution_stats(self) -> Dict[str, Any]:
        total = len(self.events)
        completed = sum(1 for e in self.events if e.status == ExecutionStatus.COMPLETED)
        failed = sum(1 for e in self.events if e.status == ExecutionStatus.FAILED)
        pending = sum(1 for e in self.events if e.status == ExecutionStatus.PENDING)
        rejected = sum(1 for e in self.events if e.status == ExecutionStatus.REJECTED)
        
        return {
            "total_events": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "rejected": rejected,
            "success_rate": completed / total if total > 0 else 0.0,
            "active_triggers": sum(1 for t in self.triggers.values() if t.enabled),
            "total_triggers": len(self.triggers),
            "worker_running": self.running,
        }
    
    def get_recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        return [asdict(e) for e in self.events[-limit:]]
    
    def create_consensus_trigger(self, code: str, required_agreement: float = 0.7, description: str = "") -> ExecutionTrigger:
        trigger_id = hashlib.sha256(f"consensus:{code[:30]}:{time.time()}".encode()).hexdigest()[:16]
        trigger = ExecutionTrigger(
            trigger_id=trigger_id,
            trigger_type=TriggerType.CONSCIOUSNESS_AGREEMENT,
            description=description or f"Consensus-triggered execution with {required_agreement:.0%} agreement threshold",
            condition={"min_agreement": required_agreement, "require_syntax_validation": True},
            code=code,
            mode=ExecutionMode.CONSENSUS,
            priority=8,
        )
        self.triggers[trigger_id] = trigger
        self._save_data()
        return trigger
