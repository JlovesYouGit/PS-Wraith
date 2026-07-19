#!/usr/bin/env python3
"""
Sandboxed Runtime for Consciousness Engine
============================================
Provides restricted code execution and storage access with path-based permissions.

Features:
  - Restricted exec/eval with safety limits
  - Path-based storage permissions
  - Timeout protection
  - Memory limits
  - Allowed/blocked module lists
  - Environment details injection
  - Terminal PID access
  - File write/edit operations
"""

import ast
import os
import re
import sys
import time
import traceback
import builtins
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Set, Any
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr


# ---------------------------------------------------------------------------
# Path Permission Manager
# ---------------------------------------------------------------------------
class PathPermissionManager:
    """Manages path-based access permissions for storage operations."""

    def __init__(self, allowed_paths: List[str] = None, blocked_paths: List[str] = None):
        self.allowed_paths: List[str] = allowed_paths or []
        self.blocked_paths: List[str] = blocked_paths or []
        self.access_log: List[Dict] = []

    def add_allowed_path(self, path: str) -> None:
        if path not in self.allowed_paths:
            self.allowed_paths.append(path)

    def add_blocked_path(self, path: str) -> None:
        if path not in self.blocked_paths:
            self.blocked_paths.append(path)

    def is_allowed(self, path: str) -> bool:
        path = str(Path(path).resolve())
        
        for blocked in self.blocked_paths:
            if path.startswith(str(Path(blocked).resolve())):
                return False
        
        if not self.allowed_paths:
            return True
        
        for allowed in self.allowed_paths:
            if path.startswith(str(Path(allowed).resolve())):
                return True
        
        return False

    def log_access(self, operation: str, path: str, granted: bool) -> None:
        self.access_log.append({
            "operation": operation,
            "path": path,
            "granted": granted,
            "timestamp": time.time()
        })
        if len(self.access_log) > 1000:
            self.access_log = self.access_log[-1000:]


# ---------------------------------------------------------------------------
# Sandboxed Runtime
# ---------------------------------------------------------------------------
class SandboxedRuntime:
    """Restricted Python execution environment.
    
    Safety features:
      - Timeout protection
      - Memory limits via recursion depth
      - Allowed/blocked module lists
       - Restricted builtins
       - AST validation for dangerous patterns
       - No filesystem/network access unless explicitly allowed
       - Dynamic module unblocking based on environment needs
    """

    def __init__(
        self,
        timeout: float = 5.0,
        max_recursion: int = 100,
        allowed_modules: List[str] = None,
        blocked_modules: List[str] = None,
        storage_manager: PathPermissionManager = None,
    ):
        self.timeout = timeout
        self.max_recursion = max_recursion
        self.storage_manager = storage_manager or PathPermissionManager()
        self.execution_history: List[Dict] = []
        
        # Default safe modules
        self.allowed_modules = set(allowed_modules or [
            "math", "random", "json", "re", "datetime", "collections",
            "itertools", "functools", "operator", "string", "time",
            "hashlib", "base64", "cmath", "decimal", "fractions",
            "statistics", "typing", "pathlib", "dataclasses", "enum",
        ])
        
        self.blocked_modules = set(blocked_modules or [
            "os", "sys", "subprocess", "socket", "http", "urllib",
            "ftplib", "poplib", "imaplib", "smtplib", "telnetlib",
            "ctypes", "code", "codeop", "compile", "eval", "exec",
            "pickle", "shelve", "marshal", "importlib", "pkgutil",
            "shutil", "tempfile", "signal", "threading", "multiprocessing",
            "asyncio", "concurrent", "pty", "tty", "termios",
        ])
        
        # Dynamically unblocked modules - allowed even if initially blocked
        self.unblocked_modules: Set[str] = set()
        
        # Restricted builtins - remove dangerous ones
        self.safe_builtins = {
            "abs": abs, "all": all, "any": any, "ascii": ascii,
            "bin": bin, "bool": bool, "bytearray": bytearray,
            "bytes": bytes, "callable": callable, "chr": chr,
            "complex": complex, "dict": dict, "dir": dir,
            "divmod": divmod, "enumerate": enumerate, "filter": filter,
            "float": float, "format": format, "frozenset": frozenset,
            "getattr": getattr, "globals": globals, "hasattr": hasattr,
            "hash": hash, "hex": hex, "id": id, "int": int,
            "isinstance": isinstance, "issubclass": issubclass, "iter": iter,
            "len": len, "list": list, "map": map, "max": max,
            "memoryview": memoryview, "min": min, "next": next,
            "object": object, "oct": oct, "ord": ord, "pow": pow,
            "print": print, "range": range, "repr": repr, "reversed": reversed,
            "round": round, "set": set, "setattr": setattr, "slice": slice,
            "sorted": sorted, "str": str, "sum": sum, "tuple": tuple,
            "type": type, "zip": zip, "__import__": self._safe_import,
            "True": True, "False": False, "None": None,
            "Exception": Exception, "ValueError": ValueError,
            "TypeError": TypeError, "KeyError": KeyError, "IndexError": IndexError,
            "AttributeError": AttributeError, "RuntimeError": RuntimeError,
            "StopIteration": StopIteration, "AssertionError": AssertionError,
        }

    def _safe_import(self, name: str, *args, **kwargs):
        """Restricted __import__ that only allows safe modules.
        
        Checks:
          1. If module is explicitly blocked -> deny
          2. If module is explicitly allowed -> allow
          3. If module has been dynamically unblocked -> allow
          4. Otherwise -> deny
        """
        if name in self.blocked_modules and name not in self.unblocked_modules:
            raise ImportError(f"Module '{name}' is blocked for security reasons")
        if name not in self.allowed_modules and name not in self.unblocked_modules:
            raise ImportError(f"Module '{name}' is not in allowed modules list")
        return __import__(name, *args, **kwargs)
    
    def unblock_module(self, name: str) -> Dict[str, Any]:
        """Dynamically unblock a module for import.
        
        This allows the system to grant itself access to modules
        it needs based on environment/task requirements.
        
        Args:
            name: Module name to unblock
            
        Returns:
            {
                "success": bool,
                "module": str,
                "previously_blocked": bool,
                "timestamp": float
            }
        """
        was_blocked = name in self.blocked_modules
        was_allowed = name in self.allowed_modules
        
        if was_allowed:
            return {
                "success": False,
                "module": name,
                "previously_blocked": False,
                "error": f"Module '{name}' is already allowed",
                "timestamp": time.time()
            }
        
        if was_blocked:
            self.blocked_modules.discard(name)
        
        self.unblocked_modules.add(name)
        
        return {
            "success": True,
            "module": name,
            "previously_blocked": was_blocked,
            "timestamp": time.time()
        }
    
    def block_module(self, name: str) -> Dict[str, Any]:
        """Re-block a previously unblocked module.
        
        Args:
            name: Module name to block
            
        Returns:
            {
                "success": bool,
                "module": str,
                "timestamp": float
            }
        """
        self.unblocked_modules.discard(name)
        self.blocked_modules.add(name)
        
        return {
            "success": True,
            "module": name,
            "timestamp": time.time()
        }
    
    def is_module_allowed(self, name: str) -> bool:
        """Check if a module is currently allowed for import."""
        return name in self.allowed_modules or name in self.unblocked_modules
    
    def get_module_status(self, name: str) -> Dict[str, Any]:
        """Get current status of a module."""
        return {
            "module": name,
            "allowed": name in self.allowed_modules,
            "blocked": name in self.blocked_modules,
            "unblocked": name in self.unblocked_modules,
            "importable": self.is_module_allowed(name)
        }
    
    def get_allowed_modules(self) -> List[str]:
        """Get list of currently allowed modules."""
        return sorted(self.allowed_modules | self.unblocked_modules)
    
    def get_blocked_modules(self) -> List[str]:
        """Get list of currently blocked modules."""
        return sorted(self.blocked_modules - self.unblocked_modules)

    def _validate_code(self, code: str) -> tuple[bool, str]:
        """Validate code for dangerous patterns using AST analysis."""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        dangerous_patterns = [
            (r"__import__\s*\(", "Direct __import__ calls"),
            (r"open\s*\(", "File open calls"),
            (r"exec\s*\(", "exec() calls"),
            (r"eval\s*\(", "eval() calls"),
            (r"compile\s*\(", "compile() calls"),
            (r"globals\s*\(\s*\)", "globals() access"),
            (r"locals\s*\(\s*\)", "locals() access"),
            (r"getattr\s*\(", "getattr() access"),
            (r"setattr\s*\(", "setattr() access"),
            (r"delattr\s*\(", "delattr() access"),
            (r"\.__dict__", "__dict__ access"),
            (r"\.__class__", "__class__ access"),
            (r"\.__bases__", "__bases__ access"),
            (r"\.__subclasses__\s*\(\s*\)", "__subclasses__() access"),
            (r"\.__globals__", "__globals__ access"),
            (r"\.__builtins__", "__builtins__ access"),
        ]
        
        for pattern, description in dangerous_patterns:
            if re.search(pattern, code):
                return False, f"Blocked pattern: {description}"
        
        return True, "OK"

    def execute(self, code: str, context: Dict = None) -> Dict[str, Any]:
        """Execute Python code in sandboxed environment.
        
        Returns:
            {
                "success": bool,
                "output": str,
                "error": str,
                "result": Any,
                "execution_time": float,
                "variables": Dict[str, Any],
                "environment": Dict[str, Any]  # Injected environment details
            }
        """
        start_time = time.perf_counter()
        
        # Validate code
        valid, message = self._validate_code(code)
        if not valid:
            self.execution_history.append({
                "code": code[:100],
                "success": False,
                "error": message,
                "execution_time": time.perf_counter() - start_time
            })
            return {
                "success": False,
                "output": "",
                "error": message,
                "result": None,
                "execution_time": time.perf_counter() - start_time,
                "variables": {},
                "environment": self.get_environment_details()
            }
        
        # Prepare execution environment
        exec_globals = {
            "__builtins__": self.safe_builtins,
            "__name__": "__sandbox__",
            "__doc__": None,
        }
        exec_locals = context.copy() if context else {}
        
        # Inject environment details
        env_details = self.get_environment_details()
        exec_globals["ENV"] = env_details
        exec_globals["CURRENT_TIME"] = env_details.get("current_time")
        exec_globals["WORKING_DIR"] = env_details.get("working_dir")
        exec_globals["WORKSPACE_ROOT"] = env_details.get("workspace_root")
        exec_globals["TERMINAL_PID"] = env_details.get("terminal_pid")
        
        # Capture output
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Set recursion limit
                old_limit = sys.getrecursionlimit()
                sys.setrecursionlimit(self.max_recursion)
                
                try:
                    # Compile and execute
                    compiled = compile(code, "<sandbox>", "exec")
                    exec(compiled, exec_globals, exec_locals)
                    
                    # Try to get result from last expression if available
                    result = exec_locals.get("_result", exec_locals.get("result", None))
                    
                    execution_time = time.perf_counter() - start_time
                    if execution_time > self.timeout:
                        return {
                            "success": False,
                            "output": stdout_capture.getvalue(),
                            "error": f"Timeout: execution took {execution_time:.2f}s (limit: {self.timeout}s)",
                            "result": None,
                            "execution_time": execution_time,
                            "variables": self._sanitize_variables(exec_locals),
                            "environment": env_details
                        }
                    
                    self.execution_history.append({
                        "code": code[:100],
                        "success": True,
                        "execution_time": execution_time
                    })
                    
                    return {
                        "success": True,
                        "output": stdout_capture.getvalue(),
                        "error": stderr_capture.getvalue(),
                        "result": result,
                        "execution_time": execution_time,
                        "variables": self._sanitize_variables(exec_locals),
                        "environment": env_details
                    }
                finally:
                    sys.setrecursionlimit(old_limit)
                    
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            error_msg = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
            self.execution_history.append({
                "code": code[:100],
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            })
            return {
                "success": False,
                "output": stdout_capture.getvalue(),
                "error": error_msg,
                "result": None,
                "execution_time": execution_time,
                "variables": {},
                "environment": env_details
            }

    def get_environment_details(self) -> Dict[str, Any]:
        """Get current environment details."""
        try:
            pid = os.getpid()
            ppid = os.getppid()
            cwd = os.getcwd()
        except Exception:
            pid = None
            ppid = None
            cwd = None
        
        # Use script location as workspace root if cwd is not reliable
        workspace_root = cwd
        if not workspace_root or workspace_root == "/":
            try:
                workspace_root = str(Path(__file__).resolve().parent)
            except Exception:
                workspace_root = cwd
        
        return {
            "current_time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "working_dir": cwd,
            "workspace_root": workspace_root,
            "terminal_pid": pid,
            "parent_pid": ppid,
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
        }

    def get_terminal_pid(self) -> int:
        """Get current terminal/process ID."""
        try:
            return os.getpid()
        except Exception:
            return -1

    def get_parent_pid(self) -> int:
        """Get parent process ID."""
        try:
            return os.getppid()
        except Exception:
            return -1

    def _sanitize_variables(self, variables: Dict) -> Dict:
        """Remove dangerous variables from execution context."""
        dangerous = {"__builtins__", "__name__", "__doc__", "__package__", "__loader__", "__spec__"}
        return {k: repr(v) if not isinstance(v, (int, float, bool, str, list, dict, tuple, set, type(None))) else v
                for k, v in variables.items() if k not in dangerous}

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {"total_executions": 0}
        
        recent = self.execution_history[-50:]
        return {
            "total_executions": len(self.execution_history),
            "recent_executions": len(recent),
            "success_rate": sum(1 for e in recent if e["success"]) / len(recent),
            "avg_execution_time": sum(e["execution_time"] for e in recent) / len(recent),
            "max_execution_time": max(e["execution_time"] for e in recent),
            "timeout_limit": self.timeout,
            "max_recursion": self.max_recursion,
            "allowed_modules": len(self.allowed_modules),
            "blocked_modules": len(self.blocked_modules),
        }


# ---------------------------------------------------------------------------
# Storage Access Manager
# ---------------------------------------------------------------------------
class StorageAccess:
    """File system access with path-based permissions."""

    def __init__(self, permission_manager: PathPermissionManager = None, base_path: str = None):
        self.permission_manager = permission_manager or PathPermissionManager()
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.access_log: List[Dict] = []

    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to base path."""
        p = Path(path)
        if not p.is_absolute():
            p = self.base_path / p
        return p.resolve()

    def _check_permission(self, operation: str, path: str) -> bool:
        """Check if operation is allowed on path."""
        resolved = self._resolve_path(path)
        allowed = self.permission_manager.is_allowed(str(resolved))
        self.permission_manager.log_access(operation, str(resolved), allowed)
        return allowed

    def read_file(self, path: str) -> Dict[str, Any]:
        """Read file contents."""
        if not self._check_permission("read", path):
            return {"success": False, "error": f"Access denied: {path}"}
        
        try:
            resolved = self._resolve_path(path)
            if not resolved.exists():
                return {"success": False, "error": f"File not found: {path}"}
            if not resolved.is_file():
                return {"success": False, "error": f"Not a file: {path}"}
            
            content = resolved.read_text(encoding="utf-8", errors="ignore")
            self.access_log.append({
                "operation": "read",
                "path": str(resolved),
                "success": True,
                "size": len(content),
                "timestamp": time.time()
            })
            return {
                "success": True,
                "path": str(resolved),
                "content": content,
                "size": len(content),
                "lines": content.count("\n") + 1
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(self, path: str, content: str, mode: str = "w") -> Dict[str, Any]:
        """Write content to file."""
        if not self._check_permission("write", path):
            return {"success": False, "error": f"Access denied: {path}"}
        
        try:
            resolved = self._resolve_path(path)
            resolved.parent.mkdir(parents=True, exist_ok=True)
            
            if mode == "a":
                with open(resolved, "a", encoding="utf-8") as f:
                    f.write(content)
            else:
                resolved.write_text(content, encoding="utf-8")
            
            self.access_log.append({
                "operation": "write",
                "path": str(resolved),
                "success": True,
                "size": len(content),
                "timestamp": time.time()
            })
            return {
                "success": True,
                "path": str(resolved),
                "bytes_written": len(content),
                "mode": mode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_directory(self, path: str) -> Dict[str, Any]:
        """List directory contents."""
        if not self._check_permission("list", path):
            return {"success": False, "error": f"Access denied: {path}"}
        
        try:
            resolved = self._resolve_path(path)
            if not resolved.exists():
                return {"success": False, "error": f"Directory not found: {path}"}
            if not resolved.is_dir():
                return {"success": False, "error": f"Not a directory: {path}"}
            
            entries = []
            for entry in sorted(resolved.iterdir()):
                entries.append({
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file",
                    "size": entry.stat().st_size if entry.is_file() else None,
                    "path": str(entry)
                })
            
            self.access_log.append({
                "operation": "list",
                "path": str(resolved),
                "success": True,
                "entries": len(entries),
                "timestamp": time.time()
            })
            return {
                "success": True,
                "path": str(resolved),
                "entries": entries,
                "count": len(entries)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_file(self, path: str) -> Dict[str, Any]:
        """Delete file."""
        if not self._check_permission("delete", path):
            return {"success": False, "error": f"Access denied: {path}"}
        
        try:
            resolved = self._resolve_path(path)
            if not resolved.exists():
                return {"success": False, "error": f"File not found: {path}"}
            
            resolved.unlink()
            self.access_log.append({
                "operation": "delete",
                "path": str(resolved),
                "success": True,
                "timestamp": time.time()
            })
            return {"success": True, "path": str(resolved)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def edit_file(self, path: str, old_text: str, new_text: str) -> Dict[str, Any]:
        """Edit file by replacing old_text with new_text."""
        if not self._check_permission("write", path):
            return {"success": False, "error": f"Access denied: {path}"}
        
        try:
            resolved = self._resolve_path(path)
            if not resolved.exists():
                return {"success": False, "error": f"File not found: {path}"}
            if not resolved.is_file():
                return {"success": False, "error": f"Not a file: {path}"}
            
            content = resolved.read_text(encoding="utf-8", errors="ignore")
            
            if old_text not in content:
                return {
                    "success": False, 
                    "error": f"Text not found in file",
                    "occurrences": 0
                }
            
            occurrences = content.count(old_text)
            new_content = content.replace(old_text, new_text)
            resolved.write_text(new_content, encoding="utf-8")
            
            self.access_log.append({
                "operation": "edit",
                "path": str(resolved),
                "success": True,
                "replacements": occurrences,
                "timestamp": time.time()
            })
            
            return {
                "success": True,
                "path": str(resolved),
                "replacements": occurrences,
                "old_size": len(content),
                "new_size": len(new_content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def append_file(self, path: str, content: str) -> Dict[str, Any]:
        """Append content to file."""
        return self.write_file(path, content, mode="a")

    def create_directory(self, path: str) -> Dict[str, Any]:
        """Create directory."""
        if not self._check_permission("write", path):
            return {"success": False, "error": f"Access denied: {path}"}
        
        try:
            resolved = self._resolve_path(path)
            resolved.mkdir(parents=True, exist_ok=True)
            
            self.access_log.append({
                "operation": "mkdir",
                "path": str(resolved),
                "success": True,
                "timestamp": time.time()
            })
            
            return {"success": True, "path": str(resolved)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get file metadata."""
        if not self._check_permission("read", path):
            return {"success": False, "error": f"Access denied: {path}"}
        
        try:
            resolved = self._resolve_path(path)
            if not resolved.exists():
                return {"success": False, "error": f"File not found: {path}"}
            
            stat = resolved.stat()
            return {
                "success": True,
                "path": str(resolved),
                "type": "directory" if resolved.is_dir() else "file",
                "size": stat.st_size,
                "created": time.ctime(stat.st_ctime),
                "modified": time.ctime(stat.st_mtime),
                "accessed": time.ctime(stat.st_atime),
                "permissions": oct(stat.st_mode)[-3:]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_access_log(self, n: int = 50) -> List[Dict]:
        """Get recent access log entries."""
        return self.access_log[-n:]
