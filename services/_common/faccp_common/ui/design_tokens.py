"""
Design Tokens System (9 Token Categories).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar


class ColorSystem:
    PRIMARY: str = "#1E293B"
    SECONDARY: str = "#475569"
    BACKGROUND: str = "#F8FAFC"
    SURFACE: str = "#FFFFFF"

    # Status treatments
    SUCCESS: str = "#10B981"
    WARNING: str = "#F59E0B"
    ERROR: str = "#EF4444"
    INFO: str = "#3B82F6"


class TypographyScale:
    DISPLAY: str = "2.25rem"
    H1: str = "1.875rem"
    H2: str = "1.5rem"
    H3: str = "1.25rem"
    BODY: str = "1rem"
    SMALL: str = "0.875rem"
    CAPTION: str = "0.75rem"


class SpacingScale:
    SCALE: ClassVar[list[int]] = [4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80]


class DesignTokens:
    CATEGORIES: ClassVar[list[str]] = [
        "colors",
        "typography",
        "spacing",
        "radius",
        "shadows",
        "borders",
        "breakpoints",
        "motion",
        "z-index",
    ]

    COMPONENT_LAYERS: ClassVar[list[str]] = [
        "Tokens",
        "Primitives",
        "Components",
        "Patterns",
        "Sections",
        "Pages",
        "Applications",
    ]
