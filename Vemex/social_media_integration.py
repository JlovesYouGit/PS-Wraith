import json
import time
import hashlib
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


class SocialPlatform(Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"


class ContentType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"


class EngagementMetric(Enum):
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVES = "saves"
    VIEWS = "views"
    REACH = "reach"
    IMPRESSIONS = "impressions"


@dataclass
class SocialPost:
    platform: SocialPlatform
    content_type: ContentType
    text: str
    media_urls: List[str]
    hashtags: List[str]
    mentions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    post_id: Optional[str] = None
    status: str = "draft"
    created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z"))


@dataclass
class EngagementData:
    post_id: str
    platform: SocialPlatform
    metrics: Dict[str, int]
    engagement_rate: float
    audience_demographics: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z"))


@dataclass
class ContentStrategy:
    platform: SocialPlatform
    best_posting_times: List[str]
    top_hashtags: List[str]
    content_themes: List[str]
    avg_engagement_rate: float
    audience_insights: Dict[str, Any]


class SocialMediaIntegration:
    def __init__(self, base_path: Path, vemex_engine: Optional[Any] = None):
        self.base_path = base_path
        self.vemex_engine = vemex_engine
        self.config_file = base_path / ".social_media_config.json"
        self.posts_file = base_path / ".social_media_posts.json"
        self.engagement_file = base_path / ".social_media_engagement.json"
        self.strategies_file = base_path / ".social_media_strategies.json"
        self.credentials_file = base_path / ".social_media_credentials.json"
        
        self.config: Dict[str, Any] = {}
        self.posts: Dict[str, SocialPost] = {}
        self.engagement_history: List[EngagementData] = []
        self.strategies: Dict[str, ContentStrategy] = {}
        self.credentials: Dict[str, Dict[str, str]] = {}
        self.capability_cache: Dict[str, Any] = {}
        
        self._load_data()
        self._init_default_strategies()

    def _load_data(self) -> None:
        for file_path, attr_name, is_json in [
            (self.config_file, "config", True),
            (self.posts_file, "posts", True),
            (self.engagement_file, "engagement_history", False),
            (self.strategies_file, "strategies", True),
            (self.credentials_file, "credentials", True),
        ]:
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if attr_name == "posts":
                        self.posts = {k: SocialPost(**v) for k, v in data.items()}
                    elif attr_name == "engagement_history":
                        self.engagement_history = [EngagementData(**e) for e in data]
                    elif attr_name == "strategies":
                        self.strategies = {k: ContentStrategy(**v) for k, v in data.items()}
                    else:
                        setattr(self, attr_name, data)
                except Exception:
                    pass

    def _save_data(self) -> None:
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, default=str)
            with open(self.posts_file, "w", encoding="utf-8") as f:
                json.dump({k: asdict(v) for k, v in self.posts.items()}, f, indent=2, default=str)
            with open(self.engagement_file, "w", encoding="utf-8") as f:
                json.dump([asdict(e) for e in self.engagement_history], f, indent=2, default=str)
            with open(self.strategies_file, "w", encoding="utf-8") as f:
                json.dump({k: asdict(v) for k, v in self.strategies.items()}, f, indent=2, default=str)
        except Exception:
            pass

    def _init_default_strategies(self) -> None:
        if not self.strategies:
            self.strategies = {
                SocialPlatform.TIKTOK.value: ContentStrategy(
                    platform=SocialPlatform.TIKTOK,
                    best_posting_times=["18:00", "20:00", "21:00"],
                    top_hashtags=["#fyp", "#viral", "#trending", "#foryou", "#foryoupage"],
                    content_themes=["short_insights", "quick_tutorials", "entertaining"],
                    avg_engagement_rate=0.08,
                    audience_insights={"primary_age": "18-34", "primary_region": "US"},
                ),
                SocialPlatform.INSTAGRAM.value: ContentStrategy(
                    platform=SocialPlatform.INSTAGRAM,
                    best_posting_times=["12:00", "18:00", "20:00"],
                    top_hashtags=["#instagood", "#photooftheday", "#beautiful", "#happy", "#love"],
                    content_themes=["visual_stories", "carousel_insights", "reels"],
                    avg_engagement_rate=0.05,
                    audience_insights={"primary_age": "25-44", "primary_region": "US"},
                ),
            }
            self._save_data()

    def get_available_platforms(self) -> List[str]:
        return [p.value for p in SocialPlatform]

    def get_available_content_types(self, platform: Optional[str] = None) -> List[str]:
        if platform == SocialPlatform.TIKTOK.value:
            return [ct.value for ct in [ContentType.VIDEO, ContentType.TEXT, ContentType.STORY]]
        elif platform == SocialPlatform.INSTAGRAM.value:
            return [ct.value for ct in [ContentType.IMAGE, ContentType.VIDEO, ContentType.CAROUSEL, ContentType.STORY, ContentType.REEL]]
        return [ct.value for ct in ContentType]

    def set_credentials(self, platform: str, credentials: Dict[str, str]) -> None:
        self.credentials[platform] = credentials
        self._save_data()

    def get_credentials(self, platform: str) -> Optional[Dict[str, str]]:
        return self.credentials.get(platform)

    def create_post(self, post: SocialPost) -> Dict[str, Any]:
        post_id = hashlib.sha256(f"{post.platform.value}:{post.text[:50]}:{time.time()}".encode()).hexdigest()[:16]
        post.post_id = post_id
        self.posts[post_id] = post
        self._save_data()
        return {
            "success": True,
            "post_id": post_id,
            "platform": post.platform.value,
            "status": post.status,
        }

    def simulate_post(self, post: SocialPost) -> Dict[str, Any]:
        create_result = self.create_post(post)
        post_id = create_result["post_id"]
        engagement = self._simulate_engagement(post)
        engagement_data = EngagementData(
            post_id=post_id,
            platform=post.platform,
            metrics=engagement,
            engagement_rate=random.uniform(0.02, 0.15),
            audience_demographics={"age_range": "18-44", "region": "US"},
        )
        self.engagement_history.append(engagement_data)
        if len(self.engagement_history) > 10000:
            self.engagement_history = self.engagement_history[-10000:]
        self._save_data()
        return {
            "success": True,
            "post_id": post_id,
            "simulated": True,
            "engagement": engagement,
            "engagement_rate": engagement_data.engagement_rate,
        }

    def _simulate_engagement(self, post: SocialPost) -> Dict[str, int]:
        base = random.randint(100, 10000)
        return {
            "views": base,
            "likes": int(base * random.uniform(0.02, 0.1)),
            "comments": int(base * random.uniform(0.001, 0.01)),
            "shares": int(base * random.uniform(0.0005, 0.005)),
            "saves": int(base * random.uniform(0.001, 0.008)),
        }

    def get_engagement_summary(self, platform: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        entries = self.engagement_history
        if platform:
            entries = [e for e in entries if e.platform.value == platform]
        entries = entries[-limit:]
        total_engagement = 0
        total_views = 0
        for entry in entries:
            total_views += entry.metrics.get("views", 0)
            total_engagement += (
                entry.metrics.get("likes", 0)
                + entry.metrics.get("comments", 0)
                + entry.metrics.get("shares", 0)
                + entry.metrics.get("saves", 0)
            )
        engagement_rate = total_engagement / total_views if total_views > 0 else 0.0
        return {
            "total_posts": len(entries),
            "total_views": total_views,
            "total_engagement": total_engagement,
            "engagement_rate": engagement_rate,
            "recent_posts": [
                {
                    "post_id": e.post_id,
                    "platform": e.platform.value,
                    "metrics": e.metrics,
                    "engagement_rate": e.engagement_rate,
                }
                for e in entries[-10:]
            ],
        }

    def learn_from_engagement(self) -> Dict[str, Any]:
        if not self.engagement_history:
            return {"status": "no_data"}
        learnings: Dict[str, Any] = {"updated_strategies": [], "insights": []}
        for platform in [p.value for p in SocialPlatform]:
            platform_entries = [e for e in self.engagement_history if e.platform.value == platform]
            if not platform_entries:
                continue
            avg_engagement = sum(e.engagement_rate for e in platform_entries) / len(platform_entries)
            if platform in self.strategies:
                self.strategies[platform].avg_engagement_rate = avg_engagement
            learnings["insights"].append({
                "platform": platform,
                "avg_engagement_rate": avg_engagement,
                "total_posts": len(platform_entries),
            })
        self._save_data()
        learnings["status"] = "completed"
        return learnings

    def generate_content_suggestions(self, platform: str, theme: str, count: int = 3) -> List[Dict[str, Any]]:
        strategy = self.strategies.get(platform)
        suggestions = []
        for i in range(count):
            text = self._generate_content_text(platform, theme)
            hashtags = strategy.top_hashtags[:random.randint(3, 6)] if strategy else []
            suggestions.append({
                "platform": platform,
                "text": text,
                "hashtags": hashtags,
                "content_type": random.choice(self.get_available_content_types(platform)),
                "predicted_engagement": random.uniform(0.03, 0.12),
            })
        return suggestions

    def _generate_content_text(self, platform: str, theme: str) -> str:
        if platform == SocialPlatform.TIKTOK.value:
            templates = [
                f"Wait for it... {theme} is about to change everything you thought you knew.",
                f"POV: you just discovered the real truth about {theme}.",
                f"Here is why {theme} matters more than you think.",
            ]
        else:
            templates = [
                f"Exploring the depths of {theme} — and what I found changed my perspective entirely.",
                f"{theme.capitalize()} is not just a trend. It is a shift.",
                f"A closer look at {theme}: the story behind the headline.",
            ]
        return random.choice(templates)

    def get_capabilities(self) -> Dict[str, Any]:
        if not self.capability_cache:
            self.capability_cache = {
                "platforms": self.get_available_platforms(),
                "tiktok_content_types": self.get_available_content_types(SocialPlatform.TIKTOK.value),
                "instagram_content_types": self.get_available_content_types(SocialPlatform.INSTAGRAM.value),
                "has_credentials": {p: bool(self.get_credentials(p)) for p in self.get_available_platforms()},
                "total_posts": len(self.posts),
                "total_engagement_records": len(self.engagement_history),
                "strategies_loaded": list(self.strategies.keys()),
            }
        return self.capability_cache

    def get_performance_report(self) -> Dict[str, Any]:
        return {
            "engagement_summary": self.get_engagement_summary(),
            "capabilities": self.get_capabilities(),
            "learnings": self.learn_from_engagement(),
            "recent_posts": [
                {
                    "post_id": p.post_id,
                    "platform": p.platform.value,
                    "text": p.text[:120],
                    "status": p.status,
                }
                for p in list(self.posts.values())[-10:]
            ],
        }
