#!/usr/bin/env python3
"""
Device Keyboard Integration Module
====================================
Integrates with Apple device data to access:
- Text replacements / autocorrect
- User dictionary
- Keyboard behavior patterns
- Typing context from accessible sources

Uses Apple Shortcuts and accessible device data to improve
the model's understanding of user input patterns.
"""

import json
import time
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter


class DeviceKeyboardIntegration:
    """Integrates device keyboard/autocorrect data into consciousness engine."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.keyboard_data_file = base_path / ".device_keyboard_data.json"
        self.text_replacements_file = base_path / ".text_replacements.json"
        self.typing_patterns_file = base_path / ".typing_patterns.json"
        
        self.text_replacements: Dict[str, str] = {}
        self.typing_patterns: Dict[str, Any] = {}
        self.device_keyboard_data: Dict[str, Any] = {}
        
        self.load_device_data()

    def load_device_data(self):
        """Load existing device keyboard data."""
        if self.keyboard_data_file.exists():
            try:
                with open(self.keyboard_data_file, "r", encoding="utf-8") as f:
                    self.device_keyboard_data = json.load(f)
            except Exception:
                pass
        
        if self.text_replacements_file.exists():
            try:
                with open(self.text_replacements_file, "r", encoding="utf-8") as f:
                    self.text_replacements = json.load(f)
            except Exception:
                pass
        
        if self.typing_patterns_file.exists():
            try:
                with open(self.typing_patterns_file, "r", encoding="utf-8") as f:
                    self.typing_patterns = json.load(f)
            except Exception:
                pass

    def save_device_data(self):
        """Save device keyboard data to disk."""
        try:
            with open(self.keyboard_data_file, "w", encoding="utf-8") as f:
                json.dump(self.device_keyboard_data, f, indent=2, default=str)
            with open(self.text_replacements_file, "w", encoding="utf-8") as f:
                json.dump(self.text_replacements, f, indent=2, default=str)
            with open(self.typing_patterns_file, "w", encoding="utf-8") as f:
                json.dump(self.typing_patterns, f, indent=2, default=str)
        except Exception:
            pass

    def export_via_applescript(self) -> Dict[str, Any]:
        """Use AppleScript/Automator to extract keyboard data from system."""
        result = {
            "success": False,
            "text_replacements": {},
            "typing_data": {},
            "error": None
        }
        
        try:
            # Try to get text replacements via AppleScript
            script = '''
            tell application "System Events"
                try
                    -- Get text replacement data if accessible
                    set textReplacements to ""
                end try
            end tell
            '''
            
            proc = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if proc.returncode == 0:
                result["typing_data"]["applescript_output"] = proc.stdout.strip()
        except Exception as e:
            result["error"] = str(e)
        
        return result

    def export_via_shortcuts(self) -> Dict[str, Any]:
        """Trigger Apple Shortcut to export keyboard/autocorrect data."""
        result = {
            "success": False,
            "shortcut_output": None,
            "error": None
        }
        
        try:
            # Try to run a shortcut if one exists
            shortcuts = [
                "Export Keyboard Data",
                "Export Autocorrect",
                "Keyboard Export",
                "Export Text Replacements"
            ]
            
            for shortcut_name in shortcuts:
                try:
                    proc = subprocess.run(
                        ['shortcuts', 'run', shortcut_name],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if proc.returncode == 0:
                        result["success"] = True
                        result["shortcut_name"] = shortcut_name
                        result["shortcut_output"] = proc.stdout.strip()
                        
                        # Try to parse as JSON
                        try:
                            data = json.loads(proc.stdout.strip())
                            result["data"] = data
                        except json.JSONDecodeError:
                            result["raw_output"] = proc.stdout.strip()
                        
                        return result
                except FileNotFoundError:
                    continue
                except subprocess.TimeoutExpired:
                    continue
            
            result["error"] = "No suitable shortcut found"
            return result
            
        except Exception as e:
            result["error"] = str(e)
            return result

    def extract_text_replacements_from_plist(self) -> Dict[str, str]:
        """Extract text replacements from accessible plist files."""
        replacements = {}
        
        possible_paths = [
            Path.home() / "Library" / "Preferences" / "com.apple.Keyboard-Settings.extension.plist",
            Path.home() / "Library" / "Preferences" / "com.apple.KeyboardViewService.plist",
            Path("/Library/Preferences/com.apple.Keyboard.plist"),
        ]
        
        for plist_path in possible_paths:
            if not plist_path.exists():
                continue
            
            try:
                # Use plutil to convert plist to JSON
                proc = subprocess.run(
                    ['plutil', '-convert', 'json', '-o', '-', str(plist_path)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if proc.returncode == 0:
                    data = json.loads(proc.stdout)
                    # Look for replacement data in various formats
                    self._extract_replacements_from_dict(data, replacements)
            except Exception:
                continue
        
        return replacements

    def _extract_replacements_from_dict(self, data: Dict, replacements: Dict):
        """Recursively extract text replacements from dictionary."""
        if isinstance(data, dict):
            for key, value in data.items():
                key_lower = key.lower()
                if any(term in key_lower for term in ['replace', 'shortcut', 'expansion', 'text']):
                    if isinstance(value, dict):
                        self._extract_replacements_from_dict(value, replacements)
                    elif isinstance(value, str) and len(value) < 200:
                        replacements[key] = value
                elif isinstance(value, (dict, list)):
                    self._extract_replacements_from_dict(value, replacements)
        elif isinstance(data, list):
            for item in data:
                self._extract_replacements_from_dict(item, replacements)

    def ingest_shortcut_export(self, export_data: str) -> Dict[str, Any]:
        """Ingest data exported from Apple Shortcuts."""
        try:
            data = json.loads(export_data)
            
            # Extract text replacements
            if "replacements" in data:
                self.text_replacements.update(data["replacements"])
            
            # Extract typing patterns
            if "patterns" in data:
                self.typing_patterns.update(data["patterns"])
            
            # Update device keyboard data
            self.device_keyboard_data.update({
                "last_updated": time.time(),
                "source": "shortcut_export",
                "replacements_count": len(self.text_replacements),
                "patterns_count": len(self.typing_patterns)
            })
            
            self.save_device_data()
            
            return {
                "success": True,
                "replacements_imported": len(self.text_replacements),
                "patterns_imported": len(self.typing_patterns)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_autocorrect_suggestions(self, word: str, context: str = "") -> List[str]:
        """Get autocorrect suggestions based on device data and patterns."""
        suggestions = []
        
        # Check text replacements first
        word_lower = word.lower()
        for trigger, replacement in self.text_replacements.items():
            if trigger.lower() == word_lower or word_lower in trigger.lower():
                suggestions.append(replacement)
        
        # Check typing patterns for common corrections
        if word_lower in self.typing_patterns:
            pattern_data = self.typing_patterns[word_lower]
            if isinstance(pattern_data, dict):
                corrections = pattern_data.get("corrections", [])
                suggestions.extend(corrections[:3])
        
        return suggestions[:5]

    def apply_device_knowledge_to_input(self, user_input: str) -> str:
        """Apply device keyboard knowledge to improve input understanding."""
        if not self.text_replacements:
            return user_input
        
        words = user_input.split()
        corrected = []
        
        for word in words:
            # Check for exact replacements
            if word in self.text_replacements:
                corrected.append(self.text_replacements[word])
            # Check for case-insensitive replacements
            elif word.lower() in {k.lower(): v for k, v in self.text_replacements.items()}:
                lower_map = {k.lower(): v for k, v in self.text_replacements.items()}
                corrected.append(lower_map.get(word.lower(), word))
            else:
                corrected.append(word)
        
        return " ".join(corrected)

    def learn_from_correction(self, original: str, corrected: str):
        """Learn from a correction to improve future suggestions."""
        if original == corrected:
            return
        
        # Record the correction pattern
        if original not in self.typing_patterns:
            self.typing_patterns[original] = {
                "corrections": [],
                "count": 0,
                "contexts": []
            }
        
        pattern = self.typing_patterns[original]
        pattern["count"] += 1
        if corrected not in pattern["corrections"]:
            pattern["corrections"].append(corrected)
        
        # Also add as text replacement
        self.text_replacements[original] = corrected
        
        self.save_device_data()

    def get_device_keyboard_summary(self) -> Dict[str, Any]:
        """Get summary of device keyboard data."""
        return {
            "text_replacements_count": len(self.text_replacements),
            "typing_patterns_count": len(self.typing_patterns),
            "device_data_keys": list(self.device_keyboard_data.keys()),
            "sample_replacements": list(self.text_replacements.items())[:10],
            "sample_patterns": list(self.typing_patterns.items())[:5]
        }

    def run_export_script(self) -> Dict[str, Any]:
        """Run the keyboard export script to gather device data."""
        result = {
            "success": False,
            "exported_data": {},
            "error": None
        }
        
        try:
            script_path = Path(__file__).parent / "export_keyboard_data.sh"
            if not script_path.exists():
                return {"success": False, "error": "Export script not found"}
            
            proc = subprocess.run(
                ['bash', str(script_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if proc.returncode == 0:
                # Try to parse the output
                try:
                    # The script outputs JSON to the export file
                    export_file = Path.home() / "Desktop" / "artificial mind map" / ".keyboard_export.json"
                    if export_file.exists():
                        with open(export_file, "r", encoding="utf-8") as f:
                            exported = json.load(f)
                        result["success"] = True
                        result["exported_data"] = exported
                        
                        # Ingest the exported data
                        self.ingest_shortcut_export(json.dumps(exported))
                    else:
                        result["error"] = "Export file not created"
                except Exception as e:
                    result["error"] = f"Failed to parse export: {e}"
            else:
                result["error"] = f"Script failed: {proc.stderr}"
        except Exception as e:
            result["error"] = str(e)
        
        return result

    def get_typing_context_for_input(self, user_input: str) -> Dict[str, Any]:
        """Get typing context and suggestions for a given input."""
        words = user_input.split()
        suggestions = {}
        corrections = {}
        
        for word in words:
            word_suggestions = self.get_autocorrect_suggestions(word, user_input)
            if word_suggestions:
                suggestions[word] = word_suggestions
            
            # Check if this word is a known correction
            if word in self.typing_patterns:
                corrections[word] = self.typing_patterns[word]
        
        return {
            "suggestions": suggestions,
            "corrections": corrections,
            "input_length": len(user_input),
            "word_count": len(words)
        }
