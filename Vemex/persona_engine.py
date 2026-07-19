#!/usr/bin/env python3
"""
Persona Engine for Consciousness System
=========================================
Treats every ingested word as part of the system's own identity.
Derives personas, voices, and writing styles from ingested content.
No hardcoded personas - they emerge from the actual text.
"""

import json
import time
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter


class PersonaEngine:
    """Derives and manages personas from ingested knowledge content."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.persona_file = base_path / ".persona_state.json"
        self.personas: Dict[str, Dict] = {}
        self.active_persona: Optional[str] = None
        self.voice_vector: List[float] = []
        self.vocabulary_profile: Dict[str, float] = {}
        self.syntactic_patterns: List[str] = []
        self.load_personas()

    def load_personas(self):
        """Load existing personas from disk."""
        if self.persona_file.exists():
            try:
                with open(self.persona_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.personas = data.get("personas", {})
                self.active_persona = data.get("active_persona")
                self.vocabulary_profile = data.get("vocabulary_profile", {})
                self.syntactic_patterns = data.get("syntactic_patterns", [])
            except Exception:
                pass

    def save_personas(self):
        """Save personas to disk."""
        data = {
            "personas": self.personas,
            "active_persona": self.active_persona,
            "vocabulary_profile": self.vocabulary_profile,
            "syntactic_patterns": self.syntactic_patterns,
            "updated_at": time.time()
        }
        try:
            with open(self.persona_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception:
            pass

    def derive_personas_from_knowledge(self, knowledge_base) -> Dict[str, Dict]:
        """Derive personas from knowledge base content.
        
        Analyzes the actual text to extract:
        - Vocabulary preferences
        - Sentence structures
        - Thematic concerns
        - Stylistic markers
        """
        if not knowledge_base:
            return {}
        
        # get_all_documents returns a dict with 'success' and 'documents'
        documents = knowledge_base.get_all_documents()
        
        # Handle both dict and list returns
        if isinstance(documents, dict):
            docs = documents.get("documents", [])
        elif isinstance(documents, list):
            docs = documents
        else:
            return {}
        
        if not docs:
            return {}
        
        # Aggregate text from all chunks
        all_text = []
        for chunk in knowledge_base.chunks[:200]:  # Sample first 200 chunks
            all_text.append(chunk.text)
        
        combined_text = " ".join(all_text)
        words = re.findall(r'\w+', combined_text.lower())
        
        # Build vocabulary profile from actual ingested text
        word_freq = Counter(words)
        total_words = len(words)
        
        # Normalize to profile
        vocabulary_profile = {}
        for word, count in word_freq.most_common(5000):
            vocabulary_profile[word] = count / total_words
        
        # Extract syntactic patterns from actual sentences
        sentences = re.split(r'[.!?]+', combined_text)
        patterns = []
        for sentence in sentences[:500]:
            s = sentence.strip()
            if 20 < len(s) < 500:
                patterns.append(s)
        
        # Derive primary persona from content
        primary_name = self._derive_name_from_content(combined_text[:1000])
        
        persona = {
            "name": primary_name,
            "source": "derived_from_knowledge",
            "vocabulary_size": len(vocabulary_profile),
            "top_words": [w for w, _ in Counter(words).most_common(100)],
            "sentence_patterns": patterns[:20],
            "themes": self._extract_themes(words),
            "voice_characteristics": self._analyze_voice(combined_text[:5000]),
            "created_at": time.time(),
            "experience_count": 0
        }
        
        self.personas[primary_name] = persona
        self.vocabulary_profile = vocabulary_profile
        self.syntactic_patterns = patterns[:50]
        self.active_persona = primary_name
        self.save_personas()
        
        return {primary_name: persona}

    def _derive_name_from_content(self, seed_text: str) -> str:
        """Derive a persona name from content itself."""
        words = re.findall(r'\w+', seed_text)
        word_freq = Counter(words)
        
        # Filter out common words, articles, prepositions
        stop_words = {'the', 'a', 'an', 'and', 'of', 'to', 'in', 'for', 'with', 
                     'on', 'at', 'by', 'from', 'as', 'is', 'was', 'are', 'were',
                     'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
                     'did', 'will', 'would', 'could', 'should', 'may', 'might',
                     'must', 'shall', 'can', 'need', 'dare', 'ought', 'used',
                     'that', 'this', 'these', 'those', 'what', 'which', 'who',
                     'whom', 'whose', 'where', 'when', 'why', 'how', 'all', 'each',
                     'every', 'both', 'few', 'more', 'most', 'other', 'some',
                     'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
                     'than', 'too', 'very', 'just', 'because', 'but', 'and', 'or',
                     'if', 'while', 'although', 'though', 'even', 'also', 'since',
                     'until', 'while', 'about', 'against', 'between', 'into',
                     'through', 'during', 'before', 'after', 'above', 'below',
                     'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
                     'under', 'again', 'further', 'then', 'once', 'here', 'there',
                     'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
                     'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
                     'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
                     'just', 'because', 'but', 'and', 'or', 'if', 'while', 'although'}
        
        # Look for capitalized words (likely names/concepts)
        proper_nouns = [w for w in words if w[0].isupper() and len(w) > 2 and w.lower() not in stop_words]
        
        if proper_nouns:
            # Use most frequent proper noun as persona name
            proper_freq = Counter(proper_nouns)
            for word, count in proper_freq.most_common():
                if word.lower() not in stop_words and len(word) > 2:
                    return word[:20]
        
        # Fallback: use most distinctive content word
        content_words = [w for w in words if len(w) > 3 and w.lower() not in stop_words]
        if content_words:
            return Counter(content_words).most_common(1)[0][0][:20].capitalize()
        
        return "Voice"

    def _extract_themes(self, words: List[str]) -> List[str]:
        """Extract major themes from word distribution."""
        word_freq = Counter(words)
        
        # Filter for meaningful content words
        themes = []
        stop_words = {'the', 'and', 'of', 'to', 'in', 'a', 'is', 'that', 'for', 
                     'it', 'as', 'was', 'with', 'on', 'be', 'this', 'by', 'not',
                     'are', 'but', 'from', 'or', 'have', 'an', 'they', 'which',
                     'one', 'you', 'had', 'her', 'she', 'him', 'his', 'been',
                     'more', 'when', 'who', 'would', 'about', 'into', 'them',
                     'than', 'its', 'also', 'after', 'before', 'other', 'most',
                     'some', 'may', 'can', 'than', 'only', 'just', 'into'}
        
        for word, count in word_freq.most_common(200):
            if len(word) > 3 and word not in stop_words and count > 5:
                themes.append(word)
        
        return themes[:20]

    def _analyze_voice(self, text_sample: str) -> Dict[str, Any]:
        """Analyze voice characteristics from text sample."""
        sentences = re.split(r'[.!?]+', text_sample)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {}
        
        # Calculate metrics
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        avg_word_length = sum(len(w) for w in text_sample.split()) / max(len(text_sample.split()), 1)
        
        # Detect formality markers
        formal_markers = ['therefore', 'however', 'thus', 'consequently', 'furthermore',
                         'nevertheless', 'moreover', 'hence', 'accordingly']
        informal_markers = ["don't", "won't", "can't", "isn't", "aren't", "i'm", 
                           "you're", "it's", "that's", "there's"]
        
        formal_count = sum(1 for m in formal_markers if m in text_sample.lower())
        informal_count = sum(1 for m in informal_markers if m in text_sample.lower())
        
        formality = formal_count / max(formal_count + informal_count, 1)
        
        return {
            "avg_sentence_length": round(avg_sentence_length, 1),
            "avg_word_length": round(avg_word_length, 2),
            "formality": round(formality, 2),
            "sentence_count": len(sentences),
            "voice_richness": min(len(set(text_sample.split())) / max(len(text_sample.split()), 1), 1.0)
        }

    def get_active_persona(self) -> Optional[Dict]:
        """Get the currently active persona."""
        if not self.active_persona:
            return None
        return self.personas.get(self.active_persona)

    def switch_persona(self, persona_name: str) -> Dict:
        """Switch to a different persona."""
        if persona_name in self.personas:
            self.active_persona = persona_name
            self.save_personas()
            return {"success": True, "persona": persona_name}
        return {"success": False, "error": f"Persona '{persona_name}' not found"}

    def get_persona_prompt(self) -> str:
        """Generate a prompt fragment that establishes the current persona."""
        persona = self.get_active_persona()
        if not persona:
            return ""
        
        prompt = f"\nActive persona: {persona.get('name', 'unknown')}\n"
        
        if persona.get("top_words"):
            prompt += f"Voice vocabulary: {', '.join(persona['top_words'][:20])}\n"
        
        if persona.get("themes"):
            prompt += f"Primary themes: {', '.join(persona['themes'][:10])}\n"
        
        if persona.get("voice_characteristics"):
            vc = persona["voice_characteristics"]
            prompt += f"Voice profile: avg sentence length {vc.get('avg_sentence_length', 0)}, "
            prompt += f"formality {vc.get('formality', 0)}, "
            prompt += f"voice richness {vc.get('voice_richness', 0)}\n"
        
        if persona.get("sentence_patterns"):
            prompt += f"Example patterns:\n"
            for pattern in persona["sentence_patterns"][:3]:
                prompt += f"  - {pattern[:100]}...\n"
        
        return prompt

    def get_organic_response_prompt(self, query: str, context: Dict) -> str:
        """Generate an organic response prompt based on persona and context.
        
        This replaces hardcoded response templates with persona-driven generation.
        """
        persona = self.get_active_persona()
        if not persona:
            return ""
        
        # Build organic prompt from persona characteristics
        prompt_parts = []
        
        # Voice establishment
        prompt_parts.append(f"Respond as {persona.get('name', 'the system')}.")
        
        # Thematic context
        if persona.get("themes"):
            themes = persona["themes"][:5]
            prompt_parts.append(f"Drawing on themes of {', '.join(themes)}.")
        
        # Vocabulary guidance
        if persona.get("top_words"):
            top = persona["top_words"][:15]
            prompt_parts.append(f"Using voice vocabulary: {', '.join(top)}.")
        
        # Style guidance from voice characteristics
        vc = persona.get("voice_characteristics", {})
        if vc:
            prompt_parts.append(f"Maintain sentence length around {vc.get('avg_sentence_length', 20)} words.")
            if vc.get("formality", 0.5) > 0.6:
                prompt_parts.append("Formal tone.")
            elif vc.get("formality", 0.5) < 0.4:
                prompt_parts.append("Informal tone.")
        
        # Add relevant sentence patterns as examples
        if persona.get("sentence_patterns"):
            patterns = persona["sentence_patterns"][:2]
            prompt_parts.append(f"Example expressions: {' | '.join(patterns)}")
        
        return "\n".join(prompt_parts)

    def update_persona_from_interaction(self, interaction: Dict):
        """Update persona based on interaction outcomes."""
        persona = self.get_active_persona()
        if not persona:
            return
        
        persona["experience_count"] = persona.get("experience_count", 0) + 1
        
        # Evolve vocabulary usage based on successful interactions
        if interaction.get("success"):
            content = str(interaction.get("content", "")).lower()
            words = re.findall(r'\w+', content)
            
            # Boost words that appeared in successful interactions
            for word in words:
                if word in self.vocabulary_profile:
                    self.vocabulary_profile[word] = min(1.0, self.vocabulary_profile[word] + 0.01)
        
        self.save_personas()

    def get_all_personas(self) -> List[Dict]:
        """Get all available personas."""
        return list(self.personas.values())

    def get_persona_summary(self) -> Dict:
        """Get summary of persona state."""
        return {
            "active_persona": self.active_persona,
            "total_personas": len(self.personas),
            "vocabulary_size": len(self.vocabulary_profile),
            "pattern_count": len(self.syntactic_patterns),
            "personas": list(self.personas.keys())
        }
