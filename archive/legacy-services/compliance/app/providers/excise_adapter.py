from abc import ABC, abstractmethod


class GovernmentExciseAdapter(ABC):

    @abstractmethod
    async def verify_license(self, license_number: str) -> dict:
        pass

    @abstractmethod
    async def verify_product(self, product_reference: str) -> dict:
        pass

    @abstractmethod
    async def verify_retailer(self, retailer_id: str) -> dict:
        pass


class StateExciseAdapter(GovernmentExciseAdapter):

    def __init__(self, state_code: str = "IN-STATE-X"):
        self.state_code = state_code

    async def verify_license(self, license_number: str) -> dict:
        if license_number.startswith("INVALID"):
            return {"verified": False, "reference": None, "state": self.state_code}
        return {"verified": True, "reference": f"gov_lic_ref_{license_number}", "state": self.state_code}

    async def verify_product(self, product_reference: str) -> dict:
        return {"verified": True, "reference": f"gov_prod_ref_{product_reference}", "state": self.state_code}

    async def verify_retailer(self, retailer_id: str) -> dict:
        return {"verified": True, "reference": f"gov_ret_ref_{retailer_id}", "state": self.state_code}
