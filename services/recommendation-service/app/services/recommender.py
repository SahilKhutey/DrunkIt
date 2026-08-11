"""
Product recommendation engine.
Uses a hybrid approach:
1. Collaborative filtering
2. Content-based filtering
3. Context-aware boost
"""

import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

from faccp_common.logging import get_logger

logger = get_logger(__name__)


class ProductRecommender:

    def __init__(self) -> None:
        self.user_interactions: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.product_attributes: dict[str, dict[str, Any]] = {}
        self.product_users: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.product_popularity: Counter = Counter()


    def record_interaction(
        self, user_id: str, product_id: str, interaction_type: str, value: float = 1.0
    ) -> None:
        weights = {
            "view": 0.2, "add_to_cart": 0.6, "purchase": 1.0,
            "rating_5": 1.0, "rating_4": 0.8, "rating_3": 0.5,
            "rating_2": 0.2, "rating_1": 0.0,
        }
        score = value * weights.get(interaction_type, 0.1)
        self.user_interactions[user_id][product_id] += score
        self.product_users[product_id][user_id] += score
        self.product_popularity[product_id] += score

    def set_product_attributes(self, product_id: str, attributes: dict[str, Any]) -> None:
        self.product_attributes[product_id] = attributes

    def recommend(
        self, user_id: str, n: int = 10, exclude_ids: set[str] | None = None, context: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        exclude_ids = exclude_ids or set()
        context = context or {}
        scores: dict[str, float] = defaultdict(float)
        reasons: dict[str, list[str]] = defaultdict(list)

        similar_users = self._find_similar_users(user_id, top_k=20)
        for other_user, similarity in similar_users:
            for product_id, rating in self.user_interactions[other_user].items():
                if product_id in exclude_ids or product_id in self.user_interactions[user_id]:
                    continue
                scores[product_id] += similarity * rating
                reasons[product_id].append(f"similar_to_{other_user[:8]}")

        for product_id, rating in self.user_interactions[user_id].items():
            similar_products = self._find_similar_products(product_id, top_k=10)
            for similar_id, similarity in similar_products:
                if similar_id in exclude_ids or similar_id == product_id:
                    continue
                scores[similar_id] += rating * similarity
                reasons[similar_id].append(f"similar_to_purchased_{product_id[:8]}")

        if context.get("time_of_day") == "evening":
            for pid in list(scores.keys()):
                attrs = self.product_attributes.get(pid, {})
                if attrs.get("category") == "wine":
                    scores[pid] *= 1.2
                    reasons[pid].append("context:evening_wine_boost")

        if context.get("weather") == "hot":
            for pid in list(scores.keys()):
                attrs = self.product_attributes.get(pid, {})
                if attrs.get("category") == "beer" and attrs.get("abv", 0) < 6:
                    scores[pid] *= 1.3
                    reasons[pid].append("context:hot_weather_light_beer")

        if not scores:
            for pid, pop in self.product_popularity.most_common(n):
                scores[pid] = pop * 0.1
                reasons[pid].append("popular_fallback")

        ranked = sorted(scores.items(), key=lambda x: -x[1])
        recommendations = []
        for product_id, score in ranked[:n]:
            attrs = self.product_attributes.get(product_id, {})
            recommendations.append({
                "product_id": product_id,
                "score": float(score),
                "name": attrs.get("name", ""),
                "category": attrs.get("category", ""),
                "reasons": list(set(reasons[product_id]))[:3],
            })
        return recommendations

    def _find_similar_users(self, user_id: str, top_k: int = 20) -> list[tuple[str, float]]:
        target = self.user_interactions[user_id]
        if not target:
            return []
        similarities = []
        target_norm = math.sqrt(sum(v * v for v in target.values()))
        for other_id, other_interactions in self.user_interactions.items():
            if other_id == user_id:
                continue
            common = set(target.keys()) & set(other_interactions.keys())
            if not common:
                continue
            dot = sum(target[p] * other_interactions[p] for p in common)
            other_norm = math.sqrt(sum(v * v for v in other_interactions.values()))
            if target_norm == 0 or other_norm == 0:
                continue
            sim = dot / (target_norm * other_norm)
            if sim > 0.1:
                similarities.append((other_id, sim))
        similarities.sort(key=lambda x: -x[1])
        return similarities[:top_k]

    def _find_similar_products(self, product_id: str, top_k: int = 10) -> list[tuple[str, float]]:
        target = self.product_attributes.get(product_id, {})
        if not target:
            return []
        target_features = self._product_features(target)
        similarities = []
        for other_id, other_attrs in self.product_attributes.items():
            if other_id == product_id:
                continue
            other_features = self._product_features(other_attrs)
            if not target_features or not other_features:
                continue
            intersection = target_features & other_features
            union = target_features | other_features
            sim = len(intersection) / len(union) if union else 0
            if sim > 0.2:
                similarities.append((other_id, sim))
        similarities.sort(key=lambda x: -x[1])
        return similarities[:top_k]

    def _product_features(self, attrs: dict[str, Any]) -> set[str]:
        features = set()
        if attrs.get("category"): features.add(f"cat:{attrs['category']}")
        if attrs.get("brand"): features.add(f"brand:{attrs['brand']}")
        if attrs.get("subcategory"): features.add(f"subcat:{attrs['subcategory']}")
        abv = attrs.get("abv", 0)
        if abv:
            features.add(f"abv:{int(abv // 5) * 5}-{int(abv // 5) * 5 + 5}")
        vol = attrs.get("volume_ml", 0)
        if vol:
            features.add(f"vol:{int(vol // 250) * 250}ml")
        for tag in attrs.get("tags", []):
            features.add(f"tag:{tag}")
        return features
