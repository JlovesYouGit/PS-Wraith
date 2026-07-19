#!/usr/bin/env python3
"""
Siri Integration Module
=======================
Integrates Siri/Assistant data into the consciousness engine.

Accessible data sources:
  - ~/Library/Assistant/SiriAnalytics.db
  - ~/Library/Assistant/SiriSyncItems.db
  - ~/Library/Assistant/SiriReferenceResolution
  - ~/Library/Assistant/com.apple.siri.corrections.laststate.plist
  - ~/Library/Assistant/SyncSnapshot.plist

Features:
  - Extract Siri corrections and learned vocabulary
  - Read Siri reference resolution data
  - Access Siri analytics for context understanding
  - Learn from Siri interaction patterns
"""

import json
import time
import os
import subprocess
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter


class SiriIntegration:
    """Integrates Siri/Assistant data into consciousness engine."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.assistant_path = Path.home() / "Library" / "Assistant"
        self.siri_data_file = base_path / ".siri_data.json"
        self.corrections_file = base_path / ".siri_corrections.json"
        self.vocabulary_file = base_path / ".siri_vocabulary.json"
        
        self.corrections: Dict[str, str] = {}
        self.vocabulary: Dict[str, int] = {}
        self.reference_resolutions: Dict[str, Any] = {}
        self.analytics: Dict[str, Any] = {}
        
        self.load_siri_data()

    def load_siri_data(self):
        """Load existing Siri data."""
        if self.siri_data_file.exists():
            try:
                with open(self.siri_data_file, "r", encoding="utf-8") as f:
                    self.analytics = json.load(f)
            except Exception:
                pass
        
        if self.corrections_file.exists():
            try:
                with open(self.corrections_file, "r", encoding="utf-8") as f:
                    self.corrections = json.load(f)
            except Exception:
                pass
        
        if self.vocabulary_file.exists():
            try:
                with open(self.vocabulary_file, "r", encoding="utf-8") as f:
                    self.vocabulary = json.load(f)
            except Exception:
                pass

    def save_siri_data(self):
        """Save Siri data to disk."""
        try:
            with open(self.siri_data_file, "w", encoding="utf-8") as f:
                json.dump(self.analytics, f, indent=2, default=str)
            with open(self.corrections_file, "w", encoding="utf-8") as f:
                json.dump(self.corrections, f, indent=2, default=str)
            with open(self.vocabulary_file, "w", encoding="utf-8") as f:
                json.dump(self.vocabulary, f, indent=2, default=str)
        except Exception:
            pass

    def extract_siri_analytics(self) -> Dict[str, Any]:
        """Extract data from SiriAnalytics.db if accessible."""
        result = {
            "success": False,
            "analytics": {},
            "error": None
        }
        
        db_path = self.assistant_path / "SiriAnalytics.db"
        if not db_path.exists():
            result["error"] = "SiriAnalytics.db not found"
            return result
        
        try:
            # Try to read the SQLite database
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            result["tables"] = tables
            
            # Try to read common analytics tables
            for table in tables[:5]:
                try:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                    rows = cursor.fetchall()
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cursor.fetchall()]
                    result["analytics"][table] = {
                        "columns": columns,
                        "sample_rows": len(rows),
                        "data": rows[:3]
                    }
                except Exception:
                    continue
            
            conn.close()
            result["success"] = True
        except Exception as e:
            result["error"] = str(e)
        
        return result

    def extract_siri_sync_items(self) -> Dict[str, Any]:
        """Extract data from SiriSyncItems.db if accessible."""
        result = {
            "success": False,
            "sync_items": {},
            "error": None
        }
        
        db_path = self.assistant_path / "SiriSyncItems.db"
        if not db_path.exists():
            result["error"] = "SiriSyncItems.db not found"
            return result
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables[:5]:
                try:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                    rows = cursor.fetchall()
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cursor.fetchall()]
                    result["sync_items"][table] = {
                        "columns": columns,
                        "sample_rows": len(rows)
                    }
                except Exception:
                    continue
            
            conn.close()
            result["success"] = True
        except Exception as e:
            result["error"] = str(e)
        
        return result

    def extract_reference_resolution(self) -> Dict[str, Any]:
        """Extract SiriReferenceResolution data if accessible."""
        result = {
            "success": False,
            "resolutions": {},
            "error": None
        }
        
        ref_path = self.assistant_path / "SiriReferenceResolution"
        if not ref_path.exists():
            result["error"] = "SiriReferenceResolution not found"
            return result
        
        try:
            if ref_path.is_file():
                # Try to read as plist
                proc = subprocess.run(
                    ['plutil', '-convert', 'json', '-o', '-', str(ref_path)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if proc.returncode == 0:
                    data = json.loads(proc.stdout)
                    result["resolutions"] = data
                    result["success"] = True
            elif ref_path.is_dir():
                # Directory with multiple files
                for f in ref_path.iterdir():
                    if f.is_file():
                        try:
                            proc = subprocess.run(
                                ['plutil', '-convert', 'json', '-o', '-', str(f)],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            if proc.returncode == 0:
                                data = json.loads(proc.stdout)
                                result["resolutions"][f.name] = data
                        except Exception:
                            continue
                result["success"] = True
        except Exception as e:
            result["error"] = str(e)
        
        return result

    def extract_corrections_from_plist(self) -> Dict[str, str]:
        """Extract corrections from Siri plist files."""
        corrections = {}
        
        plist_path = self.assistant_path / "com.apple.siri.corrections.laststate.plist"
        if not plist_path.exists():
            return corrections
        
        try:
            proc = subprocess.run(
                ['plutil', '-convert', 'json', '-o', '-', str(plist_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if proc.returncode == 0:
                data = json.loads(proc.stdout)
                self._extract_corrections_from_dict(data, corrections)
        except Exception:
            pass
        
        return corrections

    def _extract_corrections_from_dict(self, data: Dict, corrections: Dict):
        """Recursively extract corrections from dictionary."""
        if isinstance(data, dict):
            for key, value in data.items():
                key_lower = key.lower()
                if any(term in key_lower for term in ['correct', 'fix', 'replace', 'substitute']):
                    if isinstance(value, str) and len(value) < 200:
                        corrections[key] = value
                    elif isinstance(value, dict):
                        self._extract_corrections_from_dict(value, corrections)
                elif isinstance(value, (dict, list)):
                    self._extract_corrections_from_dict(value, corrections)
        elif isinstance(data, list):
            for item in data:
                self._extract_corrections_from_dict(item, corrections)

    def ingest_all_siri_data(self) -> Dict[str, Any]:
        """Ingest all accessible Siri data."""
        results = {
            "analytics": self.extract_siri_analytics(),
            "sync_items": self.extract_siri_sync_items(),
            "reference_resolution": self.extract_reference_resolution(),
            "corrections": self.extract_corrections_from_plist()
        }
        
        # Update corrections
        self.corrections.update(results["corrections"])
        
        # Extract vocabulary from reference resolutions
        if results["reference_resolution"].get("success"):
            refs = results["reference_resolution"].get("resolutions", {})
            self._extract_vocabulary_from_refs(refs)
        
        # Update analytics
        self.analytics.update({
            "last_ingested": time.time(),
            "sources": ["analytics", "sync_items", "reference_resolution", "corrections"],
            "corrections_count": len(self.corrections),
            "vocabulary_count": len(self.vocabulary)
        })
        
        self.save_siri_data()
        
        return {
            "success": True,
            "analytics_success": results["analytics"].get("success", False),
            "sync_success": results["sync_items"].get("success", False),
            "refs_success": results["reference_resolution"].get("success", False),
            "corrections_imported": len(results["corrections"]),
            "vocabulary_extracted": len(self.vocabulary)
        }

    def _extract_vocabulary_from_refs(self, refs: Dict):
        """Extract vocabulary from reference resolution data."""
        def extract_words(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(key, str) and len(key) > 2:
                        word = key.lower()
                        self.vocabulary[word] = self.vocabulary.get(word, 0) + 1
                    extract_words(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_words(item)
        
        extract_words(refs)

    def get_siri_suggestions(self, query: str) -> List[str]:
        """Get Siri-like suggestions based on learned patterns."""
        suggestions = []
        query_lower = query.lower()
        
        # Check corrections
        for wrong, right in self.corrections.items():
            if wrong.lower() in query_lower or query_lower in wrong.lower():
                suggestions.append(right)
        
        # Check vocabulary for common terms
        words = query_lower.split()
        for word in words:
            if word in self.vocabulary and self.vocabulary[word] > 5:
                related = [w for w, count in self.vocabulary.items() 
                          if count > 3 and w != word][:3]
                suggestions.extend(related)
        
        return list(set(suggestions))[:5]

    def apply_siri_knowledge_to_input(self, user_input: str) -> str:
        """Apply Siri knowledge to improve input understanding."""
        if not self.corrections:
            return user_input
        
        words = user_input.split()
        corrected = []
        
        for word in words:
            # Check for exact corrections
            if word in self.corrections:
                corrected.append(self.corrections[word])
            elif word.lower() in {k.lower(): v for k, v in self.corrections.items()}:
                lower_map = {k.lower(): v for k, v in self.corrections.items()}
                corrected.append(lower_map.get(word.lower(), word))
            else:
                corrected.append(word)
        
        return " ".join(corrected)

    def learn_from_interaction(self, user_input: str, system_response: str, feedback: float = 0.5):
        """Learn from user interaction to improve Siri-like understanding."""
        if feedback > 0.7:
            # Successful interaction - extract vocabulary
            words = user_input.lower().split()
            for word in words:
                if len(word) > 2:
                    self.vocabulary[word] = self.vocabulary.get(word, 0) + 1
        
        # Record interaction in analytics
        self.analytics.setdefault("interactions", []).append({
            "input": user_input[:200],
            "response": system_response[:200],
            "feedback": feedback,
            "timestamp": time.time()
        })
        
        # Keep only last 100 interactions
        if len(self.analytics.get("interactions", [])) > 100:
            self.analytics["interactions"] = self.analytics["interactions"][-100:]
        
        self.save_siri_data()

    def get_siri_summary(self) -> Dict[str, Any]:
        """Get summary of Siri integration."""
        return {
            "corrections_count": len(self.corrections),
            "vocabulary_count": len(self.vocabulary),
            "analytics_keys": list(self.analytics.keys()),
            "interaction_count": len(self.analytics.get("interactions", [])),
            "sample_corrections": list(self.corrections.items())[:10],
            "sample_vocabulary": list(self.vocabulary.items())[:10]
        }
