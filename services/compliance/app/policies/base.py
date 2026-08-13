from abc import ABC, abstractmethod
from typing import Any


class CompliancePolicy(ABC):

    policy_version = "1.0.0"

    @abstractmethod
    async def evaluate(
        self,
        context: Any,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError
