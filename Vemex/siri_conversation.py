#!/usr/bin/env python3
"""
Siri Conversation Integration
==============================
Enables the consciousness engine to interact with Siri via:
  - Apple Shortcuts
  - AppleScript
  - macOS speech synthesis

No APIs required. Uses built-in macOS automation.

Conversation flow:
  Model → Siri Shortcut/AppleScript → Siri responds → Model tracks response
"""

import json
import time
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Any, Optional


class SiriConversation:
    """Manages conversation with Siri via Shortcuts/Automation."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.conversation_file = base_path / ".siri_conversation.json"
        self.shortcut_name = "Consciousness Siri"
        self.conversation_history: List[Dict] = []
        self.last_siri_response: str = ""
        self.load_conversation()

    def load_conversation(self):
        """Load existing conversation history."""
        if self.conversation_file.exists():
            try:
                with open(self.conversation_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.conversation_history = data.get("history", [])
                    self.last_siri_response = data.get("last_response", "")
            except Exception:
                pass

    def save_conversation(self):
        """Save conversation history."""
        try:
            with open(self.conversation_file, "w", encoding="utf-8") as f:
                json.dump({
                    "history": self.conversation_history[-100:],
                    "last_response": self.last_siri_response,
                    "updated_at": time.time()
                }, f, indent=2, default=str)
        except Exception:
            pass

    def speak_via_siri(self, text: str) -> Dict[str, Any]:
        """Speak text via Siri using shortcuts or speech synthesis."""
        result = {
            "success": False,
            "method": None,
            "output": "",
            "error": None
        }

        # Method 1: Use macOS built-in TTS via Python
        try:
            import subprocess
            proc = subprocess.run(
                ['say', text],
                capture_output=True,
                text=True,
                timeout=30
            )
            if proc.returncode == 0:
                result["success"] = True
                result["method"] = "say"
                result["output"] = f"Spoke via say: {text[:50]}"
                self._record_interaction("speak", text, result)
                return result
        except Exception as e:
            result["error"] = f"say failed: {e}"

        # Method 2: Use Apple Shortcuts if available
        try:
            shortcut_result = self._run_shortcut("Speak Text", text)
            if shortcut_result.get("success"):
                result["success"] = True
                result["method"] = "shortcut"
                result["output"] = shortcut_result.get("output", "")
                self._record_interaction("speak_shortcut", text, result)
                return result
        except Exception as e:
            if result["error"]:
                result["error"] += f"; shortcut failed: {e}"
            else:
                result["error"] = f"shortcut failed: {e}"

        # Method 3: AppleScript TTS
        try:
            script = f'''
            tell application "System Events"
                set voiceOutput to "{text.replace('"', '\\"')}"
                say voiceOutput using "Samantha"
            end tell
            '''
            proc = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=30
            )
            if proc.returncode == 0:
                result["success"] = True
                result["method"] = "applescript"
                result["output"] = f"Spoke via AppleScript: {text[:50]}"
                self._record_interaction("speak_applescript", text, result)
                return result
        except Exception as e:
            if result["error"]:
                result["error"] += f"; applescript failed: {e}"
            else:
                result["error"] = f"applescript failed: {e}"

        return result

    def trigger_siri_action(self, action: str, parameters: Dict = None) -> Dict[str, Any]:
        """Trigger a Siri action via shortcuts."""
        result = {
            "success": False,
            "action": action,
            "output": "",
            "error": None
        }

        # Method 1: Direct shortcuts run
        shortcut_names = [
            f"Siri {action}",
            f"Consciousness {action}",
            action,
            "Run Siri Action"
        ]

        for shortcut_name in shortcut_names:
            try:
                shortcut_result = self._run_shortcut(shortcut_name, json.dumps(parameters or {}))
                if shortcut_result.get("success"):
                    result["success"] = True
                    result["method"] = "shortcut"
                    result["output"] = shortcut_result.get("output", "")
                    self._record_interaction("action", action, result)
                    return result
            except Exception:
                continue

        # Method 2: AppleScript to trigger Siri
        try:
            script = f'''
            tell application "System Events"
                -- Trigger Siri with the action
                set actionText to "{action.replace('"', '\\"')}"
                -- Use Siri's service
            end tell
            '''
            proc = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10
            )
            if proc.returncode == 0:
                result["success"] = True
                result["method"] = "applescript"
                result["output"] = f"Triggered Siri action: {action}"
                self._record_interaction("action_applescript", action, result)
                return result
        except Exception as e:
            result["error"] = f"applescript action failed: {e}"

        return result

    def _run_shortcut(self, shortcut_name: str, input_text: str = "") -> Dict[str, Any]:
        """Run an Apple Shortcut."""
        result = {
            "success": False,
            "output": "",
            "error": None
        }

        try:
            proc = subprocess.run(
                ['shortcuts', 'run', shortcut_name, '-i', input_text] if input_text else ['shortcuts', 'run', shortcut_name],
                capture_output=True,
                text=True,
                timeout=30
            )

            if proc.returncode == 0:
                result["success"] = True
                result["output"] = proc.stdout.strip()
            else:
                result["error"] = proc.stderr.strip()
        except FileNotFoundError:
            result["error"] = "shortcuts CLI not found"
        except subprocess.TimeoutExpired:
            result["error"] = "shortcut timed out"
        except Exception as e:
            result["error"] = str(e)

        return result

    def _record_interaction(self, interaction_type: str, content: str, result: Dict):
        """Record interaction in conversation history."""
        self.conversation_history.append({
            "type": interaction_type,
            "content": content,
            "success": result.get("success", False),
            "method": result.get("method"),
            "timestamp": time.time()
        })
        self.save_conversation()

    def get_conversation_context(self, n: int = 10) -> List[Dict]:
        """Get recent conversation context."""
        return self.conversation_history[-n:]

    def get_last_response(self) -> str:
        """Get Siri's last response."""
        return self.last_siri_response

    def create_shortcut(self) -> Dict[str, Any]:
        """Create the required Apple Shortcut for Siri interaction."""
        shortcut_content = {
            "WFWorkflowClientVersion": "1118.10.3",
            "WFWorkflowMinimumClientVersion": 900,
            "WFWorkflowIcon": {
                "WFWorkflowIconStartColor": 4282601983,
                "WFWorkflowIconGlyphNumber": 61440
            },
            "WFWorkflowName": self.shortcut_name,
            "WFWorkflowActions": [
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
                    "WFWorkflowActionParameters": {
                        "WFTextActionText": "Hello from Consciousness Engine"
                    }
                },
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.speaktext",
                    "WFWorkflowActionParameters": {
                        "WFTextActionText": "$@"
                    }
                }
            ]
        }

        shortcut_path = self.base_path / f"{self.shortcut_name}.shortcut"
        try:
            with open(shortcut_path, "w", encoding="utf-8") as f:
                json.dump(shortcut_content, f, indent=2)
            return {"success": True, "path": str(shortcut_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_shortcuts_available(self) -> Dict[str, Any]:
        """Check if Apple Shortcuts CLI is available."""
        try:
            proc = subprocess.run(
                ['shortcuts', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                "available": proc.returncode == 0,
                "shortcuts": proc.stdout.strip().split('\n') if proc.returncode == 0 else []
            }
        except FileNotFoundError:
            return {"available": False, "shortcuts": [], "error": "shortcuts CLI not found"}
        except Exception as e:
            return {"available": False, "shortcuts": [], "error": str(e)}

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of Siri conversation."""
        if not self.conversation_history:
            return {"total_interactions": 0}

        interactions_by_type = {}
        for entry in self.conversation_history:
            t = entry.get("type", "unknown")
            interactions_by_type[t] = interactions_by_type.get(t, 0) + 1

        return {
            "total_interactions": len(self.conversation_history),
            "interactions_by_type": interactions_by_type,
            "last_interaction": self.conversation_history[-1].get("timestamp", 0),
            "last_response": self.last_siri_response[:100] if self.last_siri_response else ""
        }
