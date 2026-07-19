#!/usr/bin/env python3
"""
Zero-Brain Code Context Ingestion
===================================
Parses zero-brain JavaScript codebase and extracts architectural patterns,
class structures, and consciousness-relevant code patterns to feed into
the consciousness engine.

Extracts:
  - Class definitions and methods
  - Architectural patterns (Render Paradox, Spectrum Lock, etc.)
  - Code metrics (complexity, lines, dependencies)
  - Pattern signatures for consciousness matching
"""

import json
import re
import time
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple


ZERO_BRAIN_DIR = Path(__file__).parent / "zero-brain"
CONTEXT_CACHE = Path(__file__).parent / ".zero_brain_context.json"


@dataclass
class CodePattern:
    pattern_id: str
    pattern_type: str
    name: str
    file_path: str
    line_number: int
    signature: str
    dependencies: List[str]
    consciousness_weight: float
    description: str


@dataclass
class ArchitecturalModule:
    module_name: str
    file_path: str
    classes: List[str]
    functions: List[str]
    exports: List[str]
    imports: List[str]
    total_lines: int
    complexity_score: float
    consciousness_patterns: List[str]


class ZeroBrainContextIngester:
    """Ingests zero-brain codebase and extracts consciousness-relevant patterns."""

    def __init__(self, zero_brain_dir: Path = ZERO_BRAIN_DIR):
        self.zero_brain_dir = zero_brain_dir
        self.patterns: List[CodePattern] = []
        self.modules: Dict[str, ArchitecturalModule] = {}
        self.class_index: Dict[str, List[CodePattern]] = defaultdict(list)
        self.method_index: Dict[str, List[CodePattern]] = defaultdict(list)
        self.consciousness_pattern_map: Dict[str, List[CodePattern]] = defaultdict(list)
        self.ingestion_time = 0.0

    def ingest(self) -> Dict:
        """Full ingestion pipeline."""
        start = time.time()
        print("[Zero-Brain] Starting code context ingestion...")
        
        # Find all JS files
        js_files = list(self.zero_brain_dir.rglob("*.js"))
        print(f"[Zero-Brain] Found {len(js_files)} JS files")
        
        # Parse each file
        for js_file in js_files:
            self._parse_file(js_file)
        
        # Build cross-references
        self._build_indices()
        
        # Calculate consciousness weights
        self._calculate_consciousness_weights()
        
        self.ingestion_time = time.time() - start
        print(f"[Zero-Brain] Ingestion complete in {self.ingestion_time:.3f}s")
        print(f"[Zero-Brain] Extracted {len(self.patterns)} patterns from {len(self.modules)} modules")
        
        return self.get_context()

    def _parse_file(self, file_path: Path):
        """Parse a single JS file for patterns."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")
            rel_path = str(file_path.relative_to(self.zero_brain_dir))
            
            # Extract module info
            module_name = file_path.stem
            imports = self._extract_imports(content)
            exports = self._extract_exports(content)
            classes = self._extract_class_names(content)
            functions = self._extract_function_names(content)
            
            # Calculate complexity (simple metric)
            complexity = self._calculate_complexity(content, lines)
            
            # Create module
            module = ArchitecturalModule(
                module_name=module_name,
                file_path=rel_path,
                classes=classes,
                functions=functions,
                exports=exports,
                imports=imports,
                total_lines=len(lines),
                complexity_score=complexity,
                consciousness_patterns=[]
            )
            self.modules[rel_path] = module
            
            # Extract class definitions with methods
            self._extract_class_patterns(content, rel_path, lines)
            
            # Extract consciousness-relevant patterns
            self._extract_consciousness_patterns(content, rel_path, lines)
            
            # Extract function signatures
            self._extract_function_patterns(content, rel_path, lines)
            
        except Exception as e:
            print(f"[Zero-Brain] Error parsing {file_path}: {e}")

    def _extract_imports(self, content: str) -> List[str]:
        imports = []
        for match in re.finditer(r"require\(['\"]([^'\"]+)['\"]\)", content):
            imports.append(match.group(1))
        return imports

    def _extract_exports(self, content: str) -> List[str]:
        exports = []
        for match in re.finditer(r"module\.exports\s*=\s*\{([^}]+)\}", content):
            exports.extend(re.findall(r"(\w+)", match.group(1)))
        for match in re.finditer(r"exports\.(\w+)", content):
            exports.append(match.group(1))
        return list(set(exports))

    def _extract_class_names(self, content: str) -> List[str]:
        return re.findall(r"class\s+(\w+)", content)

    def _extract_function_names(self, content: str) -> List[str]:
        funcs = re.findall(r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))", content)
        return [f for pair in funcs for f in pair if f]

    def _calculate_complexity(self, content: str, lines: List[str]) -> float:
        """Simple complexity score based on control flow."""
        complexity = 1.0
        complexity += content.count("if (") * 0.5
        complexity += content.count("else") * 0.3
        complexity += content.count("for (") * 0.5
        complexity += content.count("while (") * 0.5
        complexity += content.count("switch (") * 0.7
        complexity += content.count("catch (") * 0.4
        complexity += content.count("Promise") * 0.3
        complexity += content.count("async") * 0.2
        return min(complexity, 10.0)

    def _extract_class_patterns(self, content: str, rel_path: str, lines: List[str]):
        """Extract class definitions and their methods."""
        for match in re.finditer(r"class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{", content):
            class_name = match.group(1)
            parent_class = match.group(2)
            start_line = content[:match.start()].count("\n") + 1
            
            # Find methods in class
            methods = []
            class_body = self._extract_braces(content, match.end() - 1)
            if class_body:
                method_matches = re.finditer(r"(?:async\s+)?(\w+)\s*\(([^)]*)\)\s*\{", class_body)
                for m in method_matches:
                    method_name = m.group(1)
                    params = m.group(2)
                    methods.append({
                        "name": method_name,
                        "params": params.split(",") if params else [],
                        "line": start_line + class_body[:m.start()].count("\n")
                    })
            
            # Create pattern for class
            pattern_id = f"{rel_path}:{class_name}"
            pattern = CodePattern(
                pattern_id=pattern_id,
                pattern_type="class",
                name=class_name,
                file_path=rel_path,
                line_number=start_line,
                signature=f"class {class_name}({', '.join(m['name'] for m in methods[:5])})",
                dependencies=[parent_class] if parent_class else [],
                consciousness_weight=0.0,
                description=f"Class {class_name} with {len(methods)} methods"
            )
            self.patterns.append(pattern)
            self.class_index[class_name].append(pattern)
            
            # Create patterns for methods
            for method in methods:
                method_pattern = CodePattern(
                    pattern_id=f"{rel_path}:{class_name}.{method['name']}",
                    pattern_type="method",
                    name=f"{class_name}.{method['name']}",
                    file_path=rel_path,
                    line_number=method["line"],
                    signature=f"{method['name']}({', '.join(method['params'])})",
                    dependencies=[],
                    consciousness_weight=0.0,
                    description=f"Method {method['name']} in class {class_name}"
                )
                self.patterns.append(method_pattern)
                self.method_index[method["name"]].append(method_pattern)

    def _extract_consciousness_patterns(self, content: str, rel_path: str, lines: List[str]):
        """Extract patterns relevant to consciousness architecture."""
        consciousness_keywords = {
            "consciousness": ["consciousness", "conscious", "awareness", "sentience"],
            "attention": ["attention", "attend", "focus", "weight"],
            "memory": ["memory", "store", "recall", "retrieve", "index"],
            "recalibration": ["recalibrat", "recalibration", "self_link", "self_linked"],
            "spectrum": ["spectrum", "hz", "frequency", "locked", "variable_w"],
            "latch": ["latch", "pattern", "match", "dispatch", "fingerprint"],
            "shield": ["shield", "pressure", "threat", "adaptive", "translation"],
            "rule": ["rule", "violation", "enforcement", "authority", "retaliation"],
            "narrative": ["narrative", "story", "walk", "path", "token"],
            "permit": ["permit", "coordinate", "home", "external", "path_allocation"],
        }
        
        for category, keywords in consciousness_keywords.items():
            for keyword in keywords:
                for match in re.finditer(keyword, content, re.IGNORECASE):
                    line_num = content[:match.start()].count("\n") + 1
                    line_content = lines[line_num - 1].strip()
                    
                    pattern = CodePattern(
                        pattern_id=f"{rel_path}:{category}:{line_num}",
                        pattern_type="consciousness_keyword",
                        name=keyword,
                        file_path=rel_path,
                        line_number=line_num,
                        signature=line_content[:100],
                        dependencies=[],
                        consciousness_weight=0.0,
                        description=f"Consciousness pattern: {category} - {keyword}"
                    )
                    self.patterns.append(pattern)
                    self.consciousness_pattern_map[category].append(pattern)

    def _extract_function_patterns(self, content: str, rel_path: str, lines: List[str]):
        """Extract standalone function patterns."""
        for match in re.finditer(r"(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)", content):
            func_name = match.group(1)
            params = match.group(2)
            line_num = content[:match.start()].count("\n") + 1
            
            pattern = CodePattern(
                pattern_id=f"{rel_path}:{func_name}",
                pattern_type="function",
                name=func_name,
                file_path=rel_path,
                line_number=line_num,
                signature=f"{func_name}({params})",
                dependencies=[],
                consciousness_weight=0.0,
                description=f"Function {func_name}"
            )
            self.patterns.append(pattern)

    def _extract_braces(self, content: str, start: int) -> Optional[str]:
        """Extract content between balanced braces."""
        if start >= len(content):
            return None
        
        depth = 0
        for i in range(start, len(content)):
            if content[i] == "{":
                depth += 1
            elif content[i] == "}":
                depth -= 1
                if depth == 0:
                    return content[start:i + 1]
        return None

    def _build_indices(self):
        """Build cross-reference indices."""
        for pattern in self.patterns:
            if pattern.pattern_type == "class":
                self.class_index[pattern.name].append(pattern)
            elif pattern.pattern_type == "method":
                method_name = pattern.name.split(".")[-1]
                self.method_index[method_name].append(pattern)

    def _calculate_consciousness_weights(self):
        """Calculate consciousness relevance weights for patterns."""
        # Keywords that indicate high consciousness relevance
        high_weight_keywords = {
            "consciousness": 1.0, "conscious": 0.9, "awareness": 0.85,
            "attention": 0.8, "recalibrat": 0.85, "spectrum": 0.75,
            "latch": 0.8, "shield": 0.7, "rule": 0.6, "narrative": 0.9,
            "memory": 0.7, "permit": 0.65, "token": 0.7, "pattern": 0.75,
            "dispatch": 0.7, "lock": 0.6, "breach": 0.7, "paradox": 0.8
        }
        
        for pattern in self.patterns:
            weight = 0.1  # Base weight
            
            # Keyword matching
            for keyword, kw_weight in high_weight_keywords.items():
                if keyword in pattern.name.lower() or keyword in pattern.signature.lower():
                    weight = max(weight, kw_weight)
            
            # Pattern type weighting
            type_weights = {
                "class": 0.5,
                "method": 0.4,
                "function": 0.3,
                "consciousness_keyword": 0.8
            }
            weight = max(weight, type_weights.get(pattern.pattern_type, 0.2))
            
            # Module complexity bonus
            module = self.modules.get(pattern.file_path)
            if module:
                weight += module.complexity_score * 0.05
            
            pattern.consciousness_weight = min(weight, 1.0)
            
            # Add to consciousness pattern map
            for category, patterns in self.consciousness_pattern_map.items():
                if pattern in patterns:
                    pattern.consciousness_weight = max(pattern.consciousness_weight, 0.6)

    def get_context(self) -> Dict:
        """Get the ingested context as a dictionary."""
        return {
            "ingestion_time": self.ingestion_time,
            "total_files": len(self.modules),
            "total_patterns": len(self.patterns),
            "modules": {
                path: {
                    "name": mod.module_name,
                    "classes": mod.classes,
                    "functions": mod.functions,
                    "exports": mod.exports,
                    "imports": mod.imports,
                    "total_lines": mod.total_lines,
                    "complexity_score": mod.complexity_score,
                    "consciousness_patterns": mod.consciousness_patterns
                }
                for path, mod in self.modules.items()
            },
            "top_patterns": [
                {
                    "id": p.pattern_id,
                    "type": p.pattern_type,
                    "name": p.name,
                    "file": p.file_path,
                    "line": p.line_number,
                    "weight": round(p.consciousness_weight, 4),
                    "description": p.description
                }
                for p in sorted(self.patterns, key=lambda x: x.consciousness_weight, reverse=True)[:50]
            ],
            "consciousness_categories": {
                cat: len(patterns)
                for cat, patterns in self.consciousness_pattern_map.items()
            },
            "class_index": {
                name: [p.pattern_id for p in patterns]
                for name, patterns in self.class_index.items()
            },
            "method_index": {
                name: [p.pattern_id for p in patterns]
                for name, patterns in self.method_index.items()
            }
        }

    def save_context(self, output_path: Path = CONTEXT_CACHE):
        """Save ingested context to disk."""
        context = self.get_context()
        output_path.write_text(json.dumps(context, indent=2))
        print(f"[Zero-Brain] Context saved to {output_path}")
        return context

    def load_context(self, input_path: Path = CONTEXT_CACHE) -> Optional[Dict]:
        """Load context from disk."""
        if not input_path.exists():
            return None
        try:
            return json.loads(input_path.read_text())
        except Exception:
            return None

    def get_pattern_by_name(self, name: str) -> List[CodePattern]:
        """Get patterns matching a name."""
        results = []
        name_lower = name.lower()
        for p in self.patterns:
            if name_lower in p.name.lower():
                results.append(p)
        return results

    def get_consciousness_patterns(self, category: str = None) -> List[CodePattern]:
        """Get consciousness-relevant patterns, optionally filtered by category."""
        if category:
            return self.consciousness_pattern_map.get(category, [])
        all_patterns = []
        for patterns in self.consciousness_pattern_map.values():
            all_patterns.extend(patterns)
        return all_patterns

    def get_module_by_name(self, name: str) -> Optional[ArchitecturalModule]:
        """Get a module by name."""
        for path, mod in self.modules.items():
            if mod.module_name == name or path.endswith(f"/{name}.js"):
                return mod
        return None


def run_ingestion(zero_brain_dir: Path = None) -> Dict:
    """Run full ingestion and return context."""
    ingester = ZeroBrainContextIngester(zero_brain_dir or ZERO_BRAIN_DIR)
    context = ingester.ingest()
    ingester.save_context()
    return context


if __name__ == "__main__":
    context = run_ingestion()
    print(json.dumps(context, indent=2))
