"""
Accessibility Guidelines (WCAG 2.2 AA).
"""

from __future__ import annotations

from enum import Enum
from typing import ClassVar


class WCAGLevel(str, Enum):
    A = "A"
    AA = "AA"
    AAA = "AAA"


class AccessibilityGuidelines:
    TARGET_LEVEL: WCAGLevel = WCAGLevel.AA

    REQUIREMENTS: ClassVar[list[str]] = [
        "Keyboard navigation for all interactive controls",
        "Visible focus indicators on focusable elements",
        "Semantic HTML elements (header, nav, main, article, footer)",
        "Screen-reader labels (aria-label, aria-describedby, aria-live)",
        "Minimum 4.5:1 color contrast ratio for body text",
        "Accessible forms with explicit label associations",
        "Reduced-motion support via prefers-reduced-motion",
        "Touch-friendly target sizes (minimum 44x44px)",
    ]
