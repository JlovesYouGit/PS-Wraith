import json
import time
import hashlib
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


class ExternalAIProvider(Enum):
    GEMINI = "gemini"
    CLAUDE = "claude"
    CHATGPT = "chatgpt"
    KIMI = "kimi"


class SteeringMode(Enum):
    IMPROVE = "improve"
    VALIDATE = "validate"
    MERGE = "merge"
    REWRITE = "rewrite"


@dataclass
class ExternalAIRequest:
    prompt: str
    provider: ExternalAIProvider
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024
    context: Dict[str, Any] = field(default_factory=dict)
    steering: Optional[SteeringMode] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExternalAIResponse:
    provider: ExternalAIProvider
    model: str
    content: str
    tokens_used: int
    latency_ms: float
    steering_applied: Optional[SteeringMode]
    improved_content: Optional[str]
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z"))


@dataclass
class AIModelProfile:
    provider: ExternalAIProvider
    model: str
    strength: str
    weakness: str
    best_use_case: str
    avg_latency_ms: float
    success_rate: float
    total_calls: int = 0
    successful_calls: int = 0
    feedback_scores: List[float] = field(default_factory=list)


class ExternalAIIntegration:
    def __init__(self, base_path: Path, vemex_engine: Optional[Any] = None):
        self.base_path = base_path
        self.vemex_engine = vemex_engine
        self.profiles_file = base_path / ".external_ai_profiles.json"
        self.history_file = base_path / ".external_ai_history.json"
        self.steering_rules_file = base_path / ".external_ai_steering_rules.json"
        
        self.profiles: Dict[str, AIModelProfile] = {}
        self.history: List[Dict[str, Any]] = []
        self.steering_rules: Dict[str, Any] = {}
        self.capability_cache: Dict[str, Any] = {}
        
        self._load_data()
        self._init_default_profiles()
        self._init_default_steering_rules()

    def _load_data(self) -> None:
        for file_path, attr_name in [
            (self.profiles_file, "profiles"),
            (self.history_file, "history"),
            (self.steering_rules_file, "steering_rules"),
        ]:
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        setattr(self, attr_name, json.load(f))
                except Exception:
                    pass

    def _save_data(self) -> None:
        try:
            with open(self.profiles_file, "w", encoding="utf-8") as f:
                json.dump(self.profiles, f, indent=2, default=str)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, default=str)
            with open(self.steering_rules_file, "w", encoding="utf-8") as f:
                json.dump(self.steering_rules, f, indent=2, default=str)
        except Exception:
            pass

    def _init_default_profiles(self) -> None:
        defaults = [
            AIModelProfile(
                provider=ExternalAIProvider.GEMINI,
                model="gemini-2.5-pro",
                strength="reasoning",
                weakness="verbosity",
                best_use_case="complex_analysis",
                avg_latency_ms=1200,
                success_rate=0.92,
            ),
            AIModelProfile(
                provider=ExternalAIProvider.GEMINI,
                model="gemini-2.5-flash",
                strength="speed",
                weakness="depth",
                best_use_case="quick_tasks",
                avg_latency_ms=400,
                success_rate=0.88,
            ),
            AIModelProfile(
                provider=ExternalAIProvider.CLAUDE,
                model="claude-sonnet-4-20250514",
                strength="nuance",
                weakness="speed",
                best_use_case="creative_writing",
                avg_latency_ms=1800,
                success_rate=0.94,
            ),
            AIModelProfile(
                provider=ExternalAIProvider.CLAUDE,
                model="claude-opus-4-20250514",
                strength="depth",
                weakness="cost",
                best_use_case="hard_problems",
                avg_latency_ms=3200,
                success_rate=0.96,
            ),
            AIModelProfile(
                provider=ExternalAIProvider.CHATGPT,
                model="gpt-4o",
                strength="general_purpose",
                weakness="consistency",
                best_use_case="general_chat",
                avg_latency_ms=1500,
                success_rate=0.90,
            ),
            AIModelProfile(
                provider=ExternalAIProvider.CHATGPT,
                model="gpt-4o-mini",
                strength="cost_efficiency",
                weakness="reasoning",
                best_use_case="simple_tasks",
                avg_latency_ms=500,
                success_rate=0.85,
            ),
            AIModelProfile(
                provider=ExternalAIProvider.KIMI,
                model="kimi-latest",
                strength="context_length",
                weakness="specialization",
                best_use_case="long_context",
                avg_latency_ms=1000,
                success_rate=0.87,
            ),
        ]
        for profile in defaults:
            key = f"{profile.provider.value}:{profile.model}"
            if key not in self.profiles:
                self.profiles[key] = asdict(profile)
        self._save_data()

    def _init_default_steering_rules(self) -> None:
        if not self.steering_rules:
            self.steering_rules = {
                "global": {
                    "min_confidence": 0.6,
                    "max_retries": 2,
                    "fallback_provider": ExternalAIProvider.CHATGPT.value,
                    "improve_threshold": 0.75,
                    "merge_threshold": 0.85,
                },
                "provider_preferences": {
                    ExternalAIProvider.CLAUDE.value: ["creative", "nuanced", "philosophical"],
                    ExternalAIProvider.GEMINI.value: ["analytical", "factual", "structured"],
                    ExternalAIProvider.CHATGPT.value: ["general", "conversational", "coding"],
                    ExternalAIProvider.KIMI.value: ["long_context", "summarization", "research"],
                },
                "steering_prompts": {
                    SteeringMode.IMPROVE.value: "Improve the following response for clarity, accuracy, and engagement while preserving the original meaning.",
                    SteeringMode.VALIDATE.value: "Validate the factual accuracy of the following response and correct any errors.",
                    SteeringMode.MERGE.value: "Merge the following multiple AI responses into a single coherent, high-quality response.",
                    SteeringMode.REWRITE.value: "Rewrite the following response in a clearer, more concise manner without losing key information.",
                },
            }
            self._save_data()

    def get_available_providers(self) -> List[str]:
        return [p.value for p in ExternalAIProvider]

    def get_available_models(self, provider: Optional[str] = None) -> List[str]:
        models = []
        for key, profile in self.profiles.items():
            profile_provider = profile.get("provider")
            if hasattr(profile_provider, "value"):
                profile_provider = profile_provider.value
            if provider is None or profile_provider == provider:
                models.append(profile["model"])
        return models

    def get_best_model_for_task(self, task_type: str) -> Optional[str]:
        best_model = None
        best_score = -1.0
        task_lower = task_type.lower()
        for key, profile in self.profiles.items():
            score = profile["success_rate"]
            preferences = self.steering_rules.get("provider_preferences", {}).get(profile["provider"], [])
            if any(pref in task_lower for pref in preferences):
                score += 0.1
            if profile["best_use_case"] in task_lower:
                score += 0.15
            if score > best_score:
                best_score = score
                best_model = key
        return best_model

    def build_prompt_with_steering(self, request: ExternalAIRequest) -> str:
        steering_prompts = self.steering_rules.get("steering_prompts", {})
        if request.steering and request.steering.value in steering_prompts:
            return f"{steering_prompts[request.steering.value]}\n\n{request.prompt}"
        return request.prompt

    def apply_vemex_steering(self, response_text: str, request: ExternalAIRequest, original_content: str) -> str:
        if not request.steering or not self.vemex_engine:
            return response_text
        try:
            if request.steering == SteeringMode.VALIDATE:
                consistency = getattr(self.vemex_engine, 'consistency_layer', None)
                if consistency:
                    validation = consistency.validate_output(response_text, {"external_ai": True})
                    if validation.get("score", 1.0) < 0.7:
                        return original_content or response_text
            elif request.steering == SteeringMode.IMPROVE:
                if len(response_text) < len(original_content or "") * 0.8 and original_content:
                    return original_content
        except Exception:
            pass
        return response_text

    def simulate_external_call(self, request: ExternalAIRequest) -> ExternalAIResponse:
        start = time.perf_counter()
        model_key = f"{request.provider.value}:{request.model or 'default'}"
        profile = self.profiles.get(model_key)
        if not profile:
            profile = asdict(AIModelProfile(
                provider=request.provider,
                model=request.model or "default",
                strength="general",
                weakness="unknown",
                best_use_case="general",
                avg_latency_ms=1000,
                success_rate=0.8,
            ))
            self.profiles[model_key] = profile
        
        latency = profile.get("avg_latency_ms", 1000) * (0.8 + random.random() * 0.4)
        success = random.random() < profile.get("success_rate", 0.8)
        content = ""
        if success:
            content = self._generate_simulated_response(request)
        else:
            content = "[External AI call failed]"
        
        steering_applied = request.steering
        improved_content = None
        if success and steering_applied:
            improved_content = self.apply_vemex_steering(content, request, content)
        
        elapsed_ms = (time.perf_counter() - start) * 1000
        response = ExternalAIResponse(
            provider=request.provider,
            model=profile.get("model", request.model or "default"),
            content=content,
            tokens_used=random.randint(50, 500) if success else 0,
            latency_ms=elapsed_ms,
            steering_applied=steering_applied,
            improved_content=improved_content,
            confidence=profile.get("success_rate", 0.8) if success else 0.0,
            metadata={"simulated": True, "task_type": request.context.get("task_type", "general")},
        )
        
        self._record_call(request, response, profile)
        return response

    def _generate_simulated_response(self, request: ExternalAIRequest) -> str:
        provider = request.provider.value
        prompt_lower = request.prompt.lower()
        if provider == ExternalAIProvider.CLAUDE.value:
            if "creative" in prompt_lower or "story" in prompt_lower:
                return "From the loom of thought, a narrative emerges — not as a straight line, but as a spiral of meaning that revisits itself at higher levels of understanding."
            elif "analyze" in prompt_lower or "reason" in prompt_lower:
                return "Let us break this down. The premise contains an implicit assumption that may not hold under scrutiny. If we examine the underlying structure, we find three interdependent variables that shift the outcome in non-obvious ways."
            return "That is a nuanced question. The answer depends on which frame of reference we adopt, because the context shapes the conclusion in ways that are easy to overlook."
        elif provider == ExternalAIProvider.GEMINI.value:
            if "code" in prompt_lower or "function" in prompt_lower:
                return "Here is a structured implementation:\n\n```python\ndef solve(input_data):\n    # Transform input through validated stages\n    processed = preprocess(input_data)\n    result = core_logic(processed)\n    return validate(result)\n```"
            elif "data" in prompt_lower or "analyze" in prompt_lower:
                return "Based on the available data, the key patterns are:\n1. Correlation between input variables and outcomes\n2. Outliers that deviate from expected distributions\n3. Temporal trends suggesting causal relationships"
            return "The evidence points to a structured conclusion: the problem can be decomposed into orthogonal subproblems, each solvable with established methods."
        elif provider == ExternalAIProvider.CHATGPT.value:
            if "code" in prompt_lower:
                return "Sure! Here is a simple example:\n\n```python\nprint('Hello, World!')\n```\n\nLet me know if you need more details."
            elif "explain" in prompt_lower:
                return "Of course! In simple terms, this works by taking your input, processing it through a series of steps, and returning a result that matches what you asked for."
            return "I understand what you are looking for. Here is a helpful response that addresses your question directly."
        elif provider == ExternalAIProvider.KIMI.value:
            if "long" in prompt_lower or "document" in prompt_lower:
                return "After reviewing the extensive context provided, the salient points are:\n\n1. The overarching theme connects multiple disparate elements into a coherent narrative.\n2. Supporting details reinforce the central thesis across different sections.\n3. Implications extend beyond the immediate scope, suggesting broader applications."
            return "Within the broader context, this particular query maps to a well-established pattern. The relevant factors align in a way that suggests a clear path forward."
        return "I have processed your request and generated a response based on my training and the context provided."

    def _record_call(self, request: ExternalAIRequest, response: ExternalAIResponse, profile: Dict[str, Any]) -> None:
        entry = {
            "timestamp": response.timestamp,
            "provider": response.provider.value,
            "model": response.model,
            "prompt_preview": request.prompt[:100],
            "success": response.confidence > 0,
            "latency_ms": response.latency_ms,
            "tokens_used": response.tokens_used,
            "steering": response.steering_applied.value if response.steering_applied else None,
            "confidence": response.confidence,
        }
        self.history.append(entry)
        if len(self.history) > 5000:
            self.history = self.history[-5000:]
        
        model_key = f"{request.provider.value}:{response.model}"
        if model_key in self.profiles:
            self.profiles[model_key]["total_calls"] = self.profiles[model_key].get("total_calls", 0) + 1
            if response.confidence > 0:
                self.profiles[model_key]["successful_calls"] = self.profiles[model_key].get("successful_calls", 0) + 1
            self.profiles[model_key]["feedback_scores"] = self.profiles[model_key].get("feedback_scores", [])
            self.profiles[model_key]["feedback_scores"].append(response.confidence)
            if len(self.profiles[model_key]["feedback_scores"]) > 200:
                self.profiles[model_key]["feedback_scores"] = self.profiles[model_key]["feedback_scores"][-200:]
        self._save_data()

    def record_feedback(self, provider: str, model: str, feedback_score: float) -> None:
        model_key = f"{provider}:{model}"
        if model_key in self.profiles:
            self.profiles[model_key]["feedback_scores"] = self.profiles[model_key].get("feedback_scores", [])
            self.profiles[model_key]["feedback_scores"].append(feedback_score)
            if len(self.profiles[model_key]["feedback_scores"]) > 200:
                self.profiles[model_key]["feedback_scores"] = self.profiles[model_key]["feedback_scores"][-200:]
            scores = self.profiles[model_key]["feedback_scores"]
            self.profiles[model_key]["success_rate"] = sum(scores) / len(scores)
            self._save_data()

    async def query_external_ai(self, request: ExternalAIRequest) -> ExternalAIResponse:
        try:
            import aiohttp
        except ImportError:
            return self.simulate_external_call(request)
        return self.simulate_external_call(request)

    def query_external_ai_sync(self, request: ExternalAIRequest) -> ExternalAIResponse:
        try:
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                future = asyncio.run_coroutine_threadsafe(
                    self.query_external_ai(request), loop
                )
                return future.result(timeout=30)
            except RuntimeError:
                return asyncio.run(self.query_external_ai(request))
        except Exception:
            return self.simulate_external_call(request)

    def get_performance_stats(self) -> Dict[str, Any]:
        total_calls = len(self.history)
        successful_calls = sum(1 for entry in self.history if entry.get("success"))
        avg_latency = 0.0
        if total_calls > 0:
            avg_latency = sum(entry.get("latency_ms", 0) for entry in self.history) / total_calls
        
        provider_stats: Dict[str, Dict[str, Any]] = {}
        for entry in self.history:
            provider = entry.get("provider", "unknown")
            if provider not in provider_stats:
                provider_stats[provider] = {"calls": 0, "successes": 0, "avg_latency": 0.0, "latencies": []}
            provider_stats[provider]["calls"] += 1
            if entry.get("success"):
                provider_stats[provider]["successes"] += 1
            provider_stats[provider]["latencies"].append(entry.get("latency_ms", 0))
        
        for provider, stats in provider_stats.items():
            if stats["latencies"]:
                stats["avg_latency"] = sum(stats["latencies"]) / len(stats["latencies"])
            stats["success_rate"] = stats["successes"] / stats["calls"] if stats["calls"] > 0 else 0.0
            del stats["latencies"]
        
        return {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "success_rate": successful_calls / total_calls if total_calls > 0 else 0.0,
            "avg_latency_ms": avg_latency,
            "provider_stats": provider_stats,
            "available_providers": self.get_available_providers(),
            "available_models": {p: self.get_available_models(p) for p in self.get_available_providers()},
        }
