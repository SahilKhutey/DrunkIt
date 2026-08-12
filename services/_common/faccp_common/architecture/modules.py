"""
FACCP Functional Module Architecture (13 Domains, 71 Modules, 12-Phase Development Order).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class ModuleDefinition:
    code: str
    name: str
    domain: str
    description: str
    database: str | None = None


class DomainRegistry:
    DOMAINS: ClassVar[dict[str, list[str]]] = {
        "Administration": [f"ADM-0{i}" for i in range(1, 9)],
        "Consumer": [f"CON-0{i}" for i in range(1, 9)],
        "Retailer": [f"RET-0{i}" for i in range(1, 10)],
        "Trust": [f"TRU-0{i}" for i in range(1, 8)],
        "Compliance": [f"CMP-0{i}" for i in range(1, 7)],
        "Commerce": [f"COM-0{i}" for i in range(1, 7)],
        "Finance": [f"FIN-0{i}" for i in range(1, 5)],
        "Fulfillment": [f"FUL-0{i}" for i in range(1, 7)],
        "Notifications": ["NTF-01"],
        "Audit": [f"AUD-0{i}" for i in range(1, 4)],
        "Analytics": [f"ANL-0{i}" for i in range(1, 4)],
        "Support": [f"SUP-0{i}" for i in range(1, 5)],
        "Platform": [f"PLT-0{i}" for i in range(1, 7)],
    }

    TOTAL_DOMAINS: ClassVar[int] = 13
    TOTAL_MODULES: ClassVar[int] = 71


class FunctionalArchitecture:
    DEVELOPMENT_PHASES: ClassVar[dict[int, list[str]]] = {
        0: ["PLT-01", "PLT-02", "PLT-03", "PLT-04"],
        1: ["TRU-01", "TRU-02", "ADM-01", "ADM-07", "PLT-01"],
        2: ["TRU-04", "TRU-07", "TRU-05"],
        3: ["ADM-02", "ADM-03", "CMP-01"],
        4: ["RET-01", "RET-02", "RET-03", "RET-04"],
        5: ["RET-05", "COM-01", "RET-06", "COM-02"],
        6: ["CON-01", "CON-02", "CON-03", "CON-04", "CON-05"],
        7: ["COM-04", "COM-05", "COM-06", "FIN-01", "CON-06", "CON-07"],
        8: ["FUL-01", "FUL-02", "FUL-03", "FUL-04", "FUL-05", "FUL-06", "RET-08", "CON-08"],
        9: ["AUD-01", "AUD-02", "AUD-03", "TRU-06"],
        10: ["ANL-01", "ANL-02", "ANL-03", "NTF-01"],
        11: ["SUP-01", "SUP-02", "SUP-03", "SUP-04"],
        12: ["PLT-05", "PLT-06"],
    }
