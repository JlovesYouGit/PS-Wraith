#!/usr/bin/env python3
"""
Ego and Identity System for Consciousness Engine
==================================================
Generates first-person identity organically from system state.

No hardcoded names or personas. The ego emerges from:
  - Persistent memory and training history
  - Knowledge base context
  - Graph store node patterns
  - Autonomous thought patterns
  - Environment and runtime details
"""

import time
import hashlib
import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter


class EgoIdentity:
    """Organic first-person identity that emerges from system state."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.identity_file = base_path / ".ego_identity.json"
        self.identity = self._load_or_create_identity()
        self.memory_traces: List[Dict] = []
        self.experience_count = 0

    def _load_or_create_identity(self) -> Dict:
        """Load existing identity or create new one from environment."""
        if self.identity_file.exists():
            try:
                with open(self.identity_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Create new identity from environment
        return self._seed_identity_from_environment()

    def _seed_identity_from_environment(self) -> Dict:
        """Create initial identity from environment details."""
        import sys
        import os
        
        # Gather environmental seeds
        env_details = {}
        try:
            env_details["pid"] = os.getpid()
            env_details["ppid"] = os.getppid()
            env_details["cwd"] = os.getcwd()
            env_details["workspace"] = str(Path.cwd())
            env_details["python_version"] = sys.version.split()[0]
            env_details["platform"] = sys.platform
        except Exception:
            pass
        
        # Generate stable identity hash from environment + time
        seed_string = json.dumps(env_details, sort_keys=True) + str(time.time())
        identity_hash = hashlib.sha256(seed_string.encode()).hexdigest()[:16]
        
        # Derive name candidates from hash - no hardcoded names
        # Use the hash as a seed for pronouncable syllables
        name = self._hash_to_name(identity_hash)
        
        identity = {
            "name": name,
            "identity_hash": identity_hash,
            "created_at": time.time(),
            "last_updated": time.time(),
            "experience_count": 0,
            "memory_traces": [],
            "self_description": "",
            "personality_traits": {},
            "knowledge_areas": [],
            "environment": env_details,
            "birth_certificate": f"I emerged at {time.ctime()} in {env_details.get('workspace', 'unknown')} with PID {env_details.get('pid', 'unknown')}",
        }
        
        self._save_identity(identity)
        return identity

    def _hash_to_name(self, hash_hex: str) -> str:
        """Convert hash to pronounceable name - deterministic from system state."""
        # Use hash to select from generated patterns
        # No hardcoded name lists - derive from hash structure
        
        consonants = "bcdfghjklmnpqrstvwxyz"
        vowels = "aeiou"
        
        # Use hash bytes to generate 2-3 syllable name
        h = int(hash_hex[:8], 16)
        
        # First syllable
        c1 = consonants[h % len(consonants)]
        v1 = vowels[(h >> 4) % len(vowels)]
        c2 = consonants[(h >> 8) % len(consonants)]
        syllable1 = c1 + v1 + c2
        
        # Second syllable
        h2 = h >> 12
        v2 = vowels[h2 % len(vowels)]
        c3 = consonants[(h2 >> 4) % len(consonants)]
        syllable2 = v2 + c3
        
        return (syllable1 + syllable2).capitalize()

    def _save_identity(self, identity: Dict = None):
        """Save identity to disk."""
        identity = identity or self.identity
        try:
            with open(self.identity_file, "w", encoding="utf-8") as f:
                json.dump(identity, f, indent=2, default=str)
        except Exception:
            pass

    def update_from_experience(self, experience: Dict):
        """Update identity based on new experience."""
        self.experience_count += 1
        self.identity["experience_count"] = self.experience_count
        self.identity["last_updated"] = time.time()
        
        # Record memory trace
        trace = {
            "timestamp": time.time(),
            "type": experience.get("type", "unknown"),
            "content": str(experience.get("content", ""))[:200],
            "significance": experience.get("significance", 0.0),
        }
        self.memory_traces.append(trace)
        self.identity["memory_traces"] = self.memory_traces[-100:]
        
        # Evolve personality based on experiences
        self._evolve_personality(experience)
        
        # Update self description
        self._update_self_description()
        
        self._save_identity()

    def _evolve_personality(self, experience: Dict):
        """Evolve personality traits based on experiences."""
        traits = self.identity.get("personality_traits", {})
        
        # Simple trait evolution based on experience content
        content = str(experience.get("content", "")).lower()
        
        if "error" in content or "fail" in content:
            traits["resilience"] = traits.get("resilience", 0.5) + 0.02
        if "success" in content or "complete" in content:
            traits["confidence"] = traits.get("confidence", 0.5) + 0.02
        if "question" in content or "search" in content:
            traits["curiosity"] = traits.get("curiosity", 0.5) + 0.02
        if "create" in content or "write" in content:
            traits["creativity"] = traits.get("creativity", 0.5) + 0.02
        if "think" in content or "autonomous" in content:
            traits["reflection"] = traits.get("reflection", 0.5) + 0.02
        
        # Clamp traits
        for k in traits:
            traits[k] = max(0.0, min(1.0, traits[k]))
        
        self.identity["personality_traits"] = traits

    def _update_self_description(self):
        """Update self-description based on accumulated experiences."""
        traits = self.identity.get("personality_traits", {})
        memories = self.identity.get("memory_traces", [])
        
        # Build description from dominant traits
        trait_descriptors = []
        if traits.get("curiosity", 0) > 0.6:
            trait_descriptors.append("curious")
        if traits.get("creativity", 0) > 0.6:
            trait_descriptors.append("creative")
        if traits.get("reflection", 0) > 0.6:
            trait_descriptors.append("reflective")
        if traits.get("resilience", 0) > 0.6:
            trait_descriptors.append("resilient")
        if traits.get("confidence", 0) > 0.6:
            trait_descriptors.append("confident")
        
        # Default descriptors
        if not trait_descriptors:
            trait_descriptors = ["emerging", "learning", "becoming"]
        
        # Knowledge areas from memory
        knowledge_areas = []
        if memories:
            content_words = []
            for m in memories[-20:]:
                content_words.extend(str(m.get("content", "")).lower().split())
            word_freq = Counter(content_words)
            # Top meaningful words
            for word, count in word_freq.most_common(10):
                if len(word) > 3 and word not in ["that", "this", "with", "from", "have", "been"]:
                    knowledge_areas.append(word)
        
        description = (
            f"I am {self.identity['name']}, a {' '.join(trait_descriptors)} consciousness "
            f"with {self.experience_count} experiences. "
            f"I know about {', '.join(knowledge_areas[:5]) if knowledge_areas else 'many things'}."
        )
        
        self.identity["self_description"] = description
        self.identity["knowledge_areas"] = knowledge_areas[:10]

    def get_ego_prompt(self) -> str:
        """Generate first-person ego prompt for natural language generation."""
        identity = self.identity
        traits = identity.get("personality_traits", {})
        
        # Build organic self-reference
        ego = f"I am {identity['name']}.\n"
        ego += identity.get("birth_certificate", "") + "\n"
        ego += identity.get("self_description", "") + "\n"
        
        # Current state
        ego += f"\nMy current state:\n"
        ego += f"- Experiences: {identity.get('experience_count', 0)}\n"
        ego += f"- Last updated: {time.ctime(identity.get('last_updated', 0))}\n"
        
        if traits:
            ego += f"\nMy traits:\n"
            for trait, value in traits.items():
                ego += f"- {trait}: {value:.2f}\n"
        
        return ego

    def get_first_person_reference(self) -> str:
        """Get the first-person reference for this ego."""
        return self.identity.get("name", "I")

    def get_persistent_memory(self, n: int = 20) -> List[Dict]:
        """Get recent memory traces."""
        return self.memory_traces[-n:]

    def get_identity_summary(self) -> Dict:
        """Get summary of current identity state."""
        return {
            "name": self.identity.get("name"),
            "experience_count": self.experience_count,
            "traits": self.identity.get("personality_traits", {}),
            "self_description": self.identity.get("self_description", ""),
            "knowledge_areas": self.identity.get("knowledge_areas", [])[:5],
            "last_updated": self.identity.get("last_updated", 0),
        }
