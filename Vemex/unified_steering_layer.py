import json
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

from external_ai_integration import ExternalAIIntegration, ExternalAIRequest, ExternalAIResponse, SteeringMode, ExternalAIProvider
from social_media_integration import SocialMediaIntegration, SocialPlatform, ContentType, SocialPost


class SteeringStrategy(Enum):
    ADAPTIVE = "adaptive"
    CONSISTENCY_FIRST = "consistency_first"
    PERFORMANCE_FIRST = "performance_first"
    EXPLORATION = "exploration"


@dataclass
class SteeringDecision:
    provider: str
    model: str
    steering_mode: SteeringMode
    strategy: SteeringStrategy
    confidence: float
    reason: str
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z"))


@dataclass
class UnifiedInteraction:
    interaction_type: str
    external_response: Optional[ExternalAIResponse]
    steered_response: Optional[str]
    social_post: Optional[SocialPost]
    decision: Optional[SteeringDecision]
    success: bool
    feedback_score: Optional[float]
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z"))


class UnifiedSteeringLayer:
    def __init__(self, base_path: Path, vemex_engine: Optional[Any] = None):
        self.base_path = base_path
        self.vemex_engine = vemex_engine
        self.external_ai = ExternalAIIntegration(base_path, vemex_engine)
        self.social_media = SocialMediaIntegration(base_path, vemex_engine)
        
        self.history_file = base_path / ".unified_steering_history.json"
        self.strategy_file = base_path / ".unified_steering_strategy.json"
        self.performance_file = base_path / ".unified_steering_performance.json"
        
        self.history: List[UnifiedInteraction] = []
        self.strategy_config: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, Any] = {}
        
        self._load_data()
        self._init_default_strategy()
        
        self.seedgate = None
        if vemex_engine and hasattr(vemex_engine, 'seedgate') and vemex_engine.seedgate:
            self.seedgate = vemex_engine.seedgate

    def _load_data(self) -> None:
        for file_path, attr_name in [
            (self.history_file, "history"),
            (self.strategy_file, "strategy_config"),
            (self.performance_file, "performance_metrics"),
        ]:
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if attr_name == "history":
                        self.history = []
                        for item in data:
                            if item.get("decision") and isinstance(item["decision"], dict):
                                decision_data = item["decision"]
                                if isinstance(decision_data.get("steering_mode"), str):
                                    decision_data["steering_mode"] = SteeringMode(decision_data["steering_mode"])
                                if isinstance(decision_data.get("strategy"), str):
                                    decision_data["strategy"] = SteeringStrategy(decision_data["strategy"])
                                item["decision"] = SteeringDecision(**decision_data)
                            self.history.append(UnifiedInteraction(**item))
                    else:
                        setattr(self, attr_name, data)
                except Exception:
                    pass

    def _save_data(self) -> None:
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump([asdict(item) for item in self.history], f, indent=2, default=str)
            with open(self.strategy_file, "w", encoding="utf-8") as f:
                json.dump(self.strategy_config, f, indent=2, default=str)
            with open(self.performance_file, "w", encoding="utf-8") as f:
                json.dump(self.performance_metrics, f, indent=2, default=str)
        except Exception:
            pass

    def _init_default_strategy(self) -> None:
        if not self.strategy_config:
            self.strategy_config = {
                "default_strategy": SteeringStrategy.ADAPTIVE.value,
                "steering_mode_preferences": {
                    "reasoning": SteeringMode.IMPROVE.value,
                    "creative": SteeringMode.REWRITE.value,
                    "factual": SteeringMode.VALIDATE.value,
                    "general": SteeringMode.MERGE.value,
                },
                "provider_strategy_overrides": {
                    ExternalAIProvider.CLAUDE.value: {
                        "creative": SteeringMode.REWRITE.value,
                        "philosophical": SteeringMode.IMPROVE.value,
                    },
                    ExternalAIProvider.GEMINI.value: {
                        "analytical": SteeringMode.VALIDATE.value,
                        "coding": SteeringMode.IMPROVE.value,
                    },
                    ExternalAIProvider.CHATGPT.value: {
                        "general": SteeringMode.MERGE.value,
                        "coding": SteeringMode.IMPROVE.value,
                    },
                    ExternalAIProvider.KIMI.value: {
                        "long_context": SteeringMode.MERGE.value,
                        "summarization": SteeringMode.REWRITE.value,
                    },
                },
                "adaptation": {
                    "learning_rate": 0.08,
                    "exploration_rate": 0.1,
                    "min_feedback_samples": 5,
                    "performance_window": 50,
                },
            }
            self._save_data()

    def decide_steering(self, provider: str, model: str, task_type: str, context: Dict[str, Any]) -> SteeringDecision:
        task_lower = task_type.lower()
        mode_prefs = self.strategy_config.get("steering_mode_preferences", {})
        provider_overrides = self.strategy_config.get("provider_strategy_overrides", {}).get(provider, {})
        
        steering_mode = SteeringMode.MERGE
        reason = "default"
        
        for keyword, mode in mode_prefs.items():
            if keyword in task_lower:
                steering_mode = SteeringMode(mode)
                reason = f"task_keyword:{keyword}"
                break
        
        if provider in provider_overrides:
            for keyword, mode in provider_overrides[provider].items():
                if keyword in task_lower:
                    steering_mode = SteeringMode(mode)
                    reason = f"provider_override:{provider}:{keyword}"
                    break
        
        if context.get("force_steering_mode"):
            steering_mode = SteeringMode(context["force_steering_mode"])
            reason = "forced"
        
        strategy = SteeringStrategy.ADAPTIVE
        if context.get("strategy"):
            strategy = SteeringStrategy(context["strategy"])
        
        confidence = 0.7
        if reason != "default":
            confidence = 0.85
        
        return SteeringDecision(
            provider=provider,
            model=model,
            steering_mode=steering_mode,
            strategy=strategy,
            confidence=confidence,
            reason=reason,
        )

    def process_external_ai(self, prompt: str, provider: str, model: Optional[str] = None, task_type: str = "general", steering_mode: Optional[SteeringMode] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        provider_enum = ExternalAIProvider(provider)
        model = model or self.external_ai.get_best_model_for_task(task_type) or "default"
        model = model.split(":")[-1] if ":" in model else model
        
        decision = self.decide_steering(provider, model, task_type, context)
        if steering_mode:
            decision.steering_mode = steering_mode
            decision.reason = "explicit"
        
        request = ExternalAIRequest(
            prompt=prompt,
            provider=provider_enum,
            model=model,
            steering=decision.steering_mode,
            context={"task_type": task_type, **context},
        )
        
        routing_info = {}
        if self.seedgate:
            try:
                routing_context = {
                    "provider": provider,
                    "model": model,
                    "task_type": task_type,
                    "connection_id": context.get("connection_id", "default_network"),
                }
                route_decision = self.seedgate.decide_transport(routing_context)
                
                connection_id = context.get("connection_id", "default_network")
                connection = self.seedgate.get_connection(connection_id)
                
                if not connection or not connection.established:
                    auto_established = False
                    if self.seedgate.config.get("auto_routing", True):
                        mac = connection.mac if connection else "00:00:00:00:00:00"
                        port = connection.port if connection else 8080
                        if not mac or mac == "00:00:00:00:00:00":
                            mac = f"auto:{provider}:{model}"
                        if not port:
                            port = 8080
                        establish_result = self.seedgate.establish_connection(
                            connection_id=connection_id,
                            mac=mac,
                            port=port,
                            transport=route_decision.transport,
                        )
                        auto_established = establish_result.get("success", False)
                        connection = self.seedgate.get_connection(connection_id)
                
                routing_info = {
                    "transport": route_decision.transport.value,
                    "connection_id": connection_id,
                    "connection_established": connection.established if connection else False,
                    "routing_reason": route_decision.reason,
                    "routing_confidence": route_decision.confidence,
                    "auto_established": not connection.established if connection else False,
                }
                
                if connection and connection.established:
                    seed_result = self.seedgate.process_seeds(routing_context)
                    routing_info["seed_routing"] = {
                        "processed": seed_result.get("processed", 0),
                        "routed": seed_result.get("routed", 0),
                    }
            except Exception as e:
                routing_info = {"error": f"routing_failed: {e!r}"}
        
        response = self.external_ai.query_external_ai_sync(request)
        steered_content = response.improved_content or response.content
        
        interaction = UnifiedInteraction(
            interaction_type="external_ai",
            external_response=response,
            steered_response=steered_content,
            social_post=None,
            decision=decision,
            success=response.confidence > 0,
            feedback_score=None,
        )
        self.history.append(interaction)
        if len(self.history) > 10000:
            self.history = self.history[-10000:]
        self._save_data()
        
        result = {
            "success": interaction.success,
            "content": steered_content,
            "original_content": response.content,
            "provider": provider,
            "model": response.model,
            "steering_mode": decision.steering_mode.value,
            "steering_reason": decision.reason,
            "confidence": response.confidence,
            "latency_ms": response.latency_ms,
        }
        if routing_info:
            result["routing"] = routing_info
        return result

    def post_to_social(self, platform: str, text: str, content_type: str = "text", media_urls: Optional[List[str]] = None, hashtags: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        platform_enum = SocialPlatform(platform)
        content_type_enum = ContentType(content_type)
        post = SocialPost(
            platform=platform_enum,
            content_type=content_type_enum,
            text=text,
            media_urls=media_urls or [],
            hashtags=hashtags or [],
            mentions=[],
            metadata=metadata or {},
        )
        result = self.social_media.simulate_post(post)
        
        decision = SteeringDecision(
            provider="social_media",
            model=f"{platform}_post",
            steering_mode=SteeringMode.IMPROVE,
            strategy=SteeringStrategy.ADAPTIVE,
            confidence=0.8,
            reason="social_media_post",
        )
        
        interaction = UnifiedInteraction(
            interaction_type="social_media_post",
            external_response=None,
            steered_response=text,
            social_post=post,
            decision=decision,
            success=result.get("success", False),
            feedback_score=None,
        )
        self.history.append(interaction)
        self._save_data()
        
        return result

    def generate_and_post(self, platform: str, theme: str, steering_mode: Optional[SteeringMode] = None) -> Dict[str, Any]:
        suggestions = self.social_media.generate_content_suggestions(platform, theme, count=1)
        if not suggestions:
            return {"success": False, "error": "No suggestions generated"}
        
        suggestion = suggestions[0]
        context = {"task_type": "social_content", "theme": theme}
        if steering_mode:
            context["force_steering_mode"] = steering_mode.value
        
        ai_result = self.process_external_ai(
            prompt=f"Generate engaging social media content about {theme} for {platform}",
            provider=ExternalAIProvider.CHATGPT.value,
            task_type="social_content",
            context=context,
        )
        
        text = ai_result.get("content", suggestion["text"])
        post_result = self.post_to_social(
            platform=platform,
            text=text,
            content_type=suggestion["content_type"],
            hashtags=suggestion.get("hashtags", []),
            metadata={"theme": theme, "ai_generated": True},
        )
        
        return {
            "success": post_result.get("success", False),
            "text": text,
            "post_id": post_result.get("post_id"),
            "platform": platform,
            "theme": theme,
            "engagement": post_result.get("engagement", {}),
            "ai_provider": ai_result.get("provider"),
            "steering_mode": ai_result.get("steering_mode"),
        }

    def record_feedback(self, interaction_index: int, feedback_score: float) -> Dict[str, Any]:
        if not (0 <= interaction_index < len(self.history)):
            return {"success": False, "error": "Invalid interaction index"}
        
        interaction = self.history[interaction_index]
        interaction.feedback_score = feedback_score
        
        if interaction.external_response:
            provider = interaction.external_response.provider.value
            model = interaction.external_response.model
            self.external_ai.record_feedback(provider, model, feedback_score)
        
        self._adapt_strategy(interaction, feedback_score)
        self._save_data()
        
        return {
            "success": True,
            "interaction_type": interaction.interaction_type,
            "feedback_score": feedback_score,
            "adapted": True,
        }

    def _adapt_strategy(self, interaction: UnifiedInteraction, feedback_score: float) -> None:
        adaptation = self.strategy_config.get("adaptation", {})
        learning_rate = adaptation.get("learning_rate", 0.08)
        
        if interaction.decision and feedback_score < 0.5:
            provider_overrides = self.strategy_config.setdefault("provider_strategy_overrides", {})
            provider = interaction.decision.provider
            provider_overrides.setdefault(provider, {})
            current_mode = interaction.decision.steering_mode
            if hasattr(current_mode, "value"):
                current_mode = current_mode.value
            alt_modes = [m.value for m in SteeringMode if m.value != current_mode]
            new_mode = random.choice(alt_modes) if random.random() < adaptation.get("exploration_rate", 0.1) else current_mode
            provider_overrides[provider]["fallback"] = new_mode

    def get_unified_summary(self) -> Dict[str, Any]:
        recent = self.history[-50:]
        external_ai_calls = [i for i in recent if i.interaction_type == "external_ai"]
        social_posts = [i for i in recent if i.interaction_type == "social_media_post"]
        
        external_success_rate = 0.0
        if external_ai_calls:
            external_success_rate = sum(1 for i in external_ai_calls if i.success) / len(external_ai_calls)
        
        social_success_rate = 0.0
        if social_posts:
            social_success_rate = sum(1 for i in social_posts if i.success) / len(social_posts)
        
        steering_distribution: Dict[str, int] = {}
        for interaction in external_ai_calls:
            if interaction.decision:
                mode = interaction.decision.steering_mode
                if hasattr(mode, "value"):
                    mode = mode.value
                steering_distribution[mode] = steering_distribution.get(mode, 0) + 1
        
        return {
            "total_interactions": len(self.history),
            "recent_external_ai_calls": len(external_ai_calls),
            "recent_social_posts": len(social_posts),
            "external_ai_success_rate": external_success_rate,
            "social_posting_success_rate": social_success_rate,
            "steering_distribution": steering_distribution,
            "external_ai_stats": self.external_ai.get_performance_stats(),
            "social_media_stats": self.social_media.get_performance_report(),
            "strategy_config": self.strategy_config,
        }

    def get_available_capabilities(self) -> Dict[str, Any]:
        return {
            "external_ai_providers": self.external_ai.get_available_providers(),
            "external_ai_models": {p: self.external_ai.get_available_models(p) for p in self.external_ai.get_available_providers()},
            "social_platforms": self.social_media.get_available_platforms(),
            "steering_modes": [m.value for m in SteeringMode],
            "strategies": [s.value for s in SteeringStrategy],
        }
