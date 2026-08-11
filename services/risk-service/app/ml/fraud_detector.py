"""
Fraud detection model.
Combines:
1. Rule-based scoring
2. Statistical anomaly detection (Z-score)
3. ML-based fraud classification
4. Ensemble final score
"""

from __future__ import annotations

import json
import math
import pickle
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from faccp_common.logging import get_logger
from app.ml.feature_engineering import FeatureExtractor

logger = get_logger(__name__)


class StatisticalAnomalyDetector:
    """
    Streaming Z-score based anomaly detection.
    Maintains running statistics (mean, std) per feature and flags instances whose Z-score exceeds a threshold.
    """

    def __init__(self, n_features: int, window_size: int = 1000, z_threshold: float = 3.0) -> None:
        self.n_features = n_features
        self.window_size = window_size
        self.z_threshold = z_threshold
        self.feature_windows: list[deque] = [deque(maxlen=window_size) for _ in range(n_features)]
        self.means = np.zeros(n_features)
        self.stds = np.ones(n_features)
        self.initialized = False

    def update(self, features: np.ndarray) -> None:
        for i in range(self.n_features):
            self.feature_windows[i].append(float(features[i]))
        if len(self.feature_windows[0]) >= 50:
            arr = np.array([list(w) for w in self.feature_windows])
            self.means = arr.mean(axis=1)
            self.stds = arr.std(axis=1)
            self.stds = np.where(self.stds < 1e-6, 1.0, self.stds)
            self.initialized = True

    def is_anomalous(self, features: np.ndarray) -> tuple[bool, np.ndarray]:
        if not self.initialized or len(self.feature_windows[0]) < 50:
            return False, np.zeros(self.n_features)
        z_scores = np.abs((features - self.means) / self.stds)
        max_z = z_scores.max()
        n_anomalous = (z_scores > self.z_threshold).sum()
        is_anomaly = max_z > self.z_threshold * 1.5 or n_anomalous >= 3
        return is_anomaly, z_scores


class FraudClassifier:
    """Lightweight linear fraud classifier with interpretable weights."""

    WEIGHTS = np.array([
        -0.05, 0.8, -0.02, -0.01, -0.03, 0.5, 0.6, 0.1, 0.02, 0.15,
        0.0001, 0.0002, 0.0001, 0.1, 0.4, 0.6, 0.5, 0.7, -0.005, 0.2,
        0.3, 1.0, 0.005, 0.8, 0.2, -0.04, 0.0, 0.0, 0.4, -0.1,
        -0.0001, 0.0, 0.5, 0.4, 0.00005, 0.00001, -0.5, -0.5, -0.3, -0.01,
        0.9, -0.005, -0.0001, -0.2, 0.6,
    ], dtype=np.float32)
    BIAS = 0.0

    def __init__(self) -> None:
        self.weights = self.WEIGHTS
        self.bias = self.BIAS

    def predict_proba(self, features: np.ndarray) -> float:
        """Return fraud probability in [0, 1]."""
        z = float(np.dot(features, self.weights) + self.bias)
        z = max(-500, min(500, z))
        return 1.0 / (1.0 + math.exp(-z))

    def predict(self, features: np.ndarray, threshold: float = 0.5) -> tuple[int, float]:
        prob = self.predict_proba(features)
        return (1 if prob >= threshold else 0), prob


class AccountTakeoverDetector:
    """Detects account takeover using session-level signals."""

    def evaluate(self, user_id: str, context: dict[str, Any]) -> tuple[float, list[str]]:
        signals = []
        score = 0.0
        if context.get("password_reset_within_1h", False):
            if context.get("new_device", False) or context.get("geo_distance_from_home_km", 0) > 500:
                score += 0.5
                signals.append("password_reset_with_new_device_location")

        failed_logins_24h = context.get("failed_logins_24h", 0)
        if failed_logins_24h > 5:
            score += 0.3
            signals.append(f"high_failed_login_count_{failed_logins_24h}")

        if context.get("unusual_hour_for_user", False):
            score += 0.2
            signals.append("unusual_hour_for_user_pattern")

        devices_24h = context.get("distinct_devices_24h", 1)
        if devices_24h > 2:
            score += 0.3
            signals.append(f"multiple_devices_{devices_24h}_in_24h")

        seconds_since_login = context.get("seconds_since_login", 9999)
        if seconds_since_login < 30 and context.get("is_sensitive_action", False):
            score += 0.2
            signals.append("sensitive_action_immediately_after_login")

        return min(score, 1.0), signals


class FraudDetectionEnsemble:
    """Combines rule score, anomaly score, ML probability, and ATO score."""

    def __init__(self) -> None:
        self.feature_extractor = FeatureExtractor()
        self.anomaly_detector = StatisticalAnomalyDetector(n_features=len(self.feature_extractor.FEATURE_NAMES))
        self.classifier = FraudClassifier()
        self.ato_detector = AccountTakeoverDetector()
        self.weights = {"rule": 0.25, "anomaly": 0.20, "ml": 0.35, "ato": 0.20}

    def evaluate(
        self,
        context: dict[str, Any],
        history: list[dict[str, Any]] | None = None,
        rule_score: float = 0.0,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        features = self.feature_extractor.extract(context, history)
        self.anomaly_detector.update(features)
        is_anomaly, z_scores = self.anomaly_detector.is_anomalous(features)
        anomaly_score = min(1.0, float(z_scores.max() / 6.0)) if self.anomaly_detector.initialized else 0.0

        fraud_prob = self.classifier.predict_proba(features)

        ato_score, ato_signals = (0.0, [])
        if user_id:
            ato_score, ato_signals = self.ato_detector.evaluate(user_id, context)

        final_score = (
            self.weights["rule"] * rule_score
            + self.weights["anomaly"] * anomaly_score
            + self.weights["ml"] * fraud_prob
            + self.weights["ato"] * ato_score
        )

        feature_dict = self.feature_extractor.feature_vector_to_dict(features)
        top_contributors = self._top_contributors(features, top_k=5)

        return {
            "final_score": float(final_score),
            "rule_score": float(rule_score),
            "anomaly_score": float(anomaly_score),
            "is_anomaly": is_anomaly,
            "ml_probability": float(fraud_prob),
            "ato_score": float(ato_score),
            "ato_signals": ato_signals,
            "z_scores": self.feature_extractor.feature_vector_to_dict(z_scores),
            "top_contributors": top_contributors,
            "feature_vector": feature_dict,
        }

    def _top_contributors(self, features: np.ndarray, top_k: int = 5) -> list[dict[str, Any]]:
        contributions = features * self.classifier.weights
        top_indices = np.argsort(np.abs(contributions))[::-1][:top_k]
        return [
            {
                "feature": self.feature_extractor.FEATURE_NAMES[i],
                "value": float(features[i]),
                "contribution": float(contributions[i]),
            }
            for i in top_indices
        ]


_ensemble: FraudDetectionEnsemble | None = None


def get_fraud_ensemble() -> FraudDetectionEnsemble:
    global _ensemble
    if _ensemble is None:
        _ensemble = FraudDetectionEnsemble()
    return _ensemble
