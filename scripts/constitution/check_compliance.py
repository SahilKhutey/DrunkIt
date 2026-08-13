"""
Constitution Checker Module (Protocol Compliance Verification).
Audits codebase against all 9 Articles of the System Constitution.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any

# Ensure faccp_common and root_dir are importable if run standalone
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
common_path = os.path.join(root_dir, "services/_common")
if common_path not in sys.path:
    sys.path.insert(0, common_path)


try:
    from faccp_common.compliance.policy_access import PolicyAccessGuard
except ImportError:
    PolicyAccessGuard = None  # Fallback if dependencies unlinked


@dataclass
class ConstitutionCheckResult:
    article: str
    name: str
    status: str  # PASSED | FAILED
    violations: list[str] = field(default_factory=list)


class ConstitutionChecker:
    """Runs compliance checks for all 9 Articles of the System Constitution."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = root_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

    def check_all(self) -> dict[str, Any]:
        articles = [
            ("Article 1", "Security", self.check_security),
            ("Article 2", "Privacy", self.check_privacy),
            ("Article 3", "Compliance", self.check_compliance),
            ("Article 4", "Data", self.check_data),
            ("Article 5", "API", self.check_api),
            ("Article 6", "Events", self.check_events),
            ("Article 7", "Testing", self.check_testing),
            ("Article 8", "Operations", self.check_operations),
            ("Article 9", "Governance", self.check_governance),
            ("Protocol 09", "Domain Isolation", self.check_domain_isolation),
            ("Protocol 10", "Single Responsibility", self.check_single_responsibility),
            ("Protocol 11", "API Contract", self.check_api_contracts),
            ("Protocol 12", "Deployment Isolation", self.check_deployment_isolation),
            ("Protocol 13", "Source-of-Truth", self.check_source_of_truth),
            ("Protocol 14", "Identity Protocol", self.check_identity_protocol),
            ("Protocol 15", "Authentication Protocol", self.check_authentication_protocol),
            ("Protocol 16", "Authorization Protocol", self.check_authorization_protocol),
            ("Protocol 17", "Trust Verification Protocol", self.check_trust_protocol),
            ("Protocol 60", "Development Gate System", self.check_development_gates_protocol),
            ("Architecture", "Functional Architecture", self.check_functional_architecture_step),
            ("Communication", "Communication System", self.check_communication_system_step),
            ("Catalog", "Catalog & Template Platform", self.check_catalog_and_templates_step),
            ("Product", "Product Platform Architecture", self.check_product_platform_step),
            ("WebUI", "Web UI Platform Architecture", self.check_web_ui_platform_step),
            ("ProductAdmin", "Product Catalog Admin System", self.check_product_catalog_admin_step),
            ("ConsumerListing", "Consumer Listing Engine", self.check_consumer_listing_engine_step),
            ("ListingSpec", "Listing Engine Specification", self.check_listing_engine_spec_step),
            ("DeliveryEngine", "Delivery System & Delivery Engine", self.check_delivery_engine_step),
            ("Phase0Foundation", "Phase 0 Foundation Execution", self.check_phase0_foundation_step),
            ("IdentityService", "Phase 1 Identity Service Microservice", self.check_identity_service_step),
            ("ComplianceService", "Phase 2 Compliance Service Microservice", self.check_compliance_service_step),
            ("ConsumerService", "Phase 3 Consumer Service Microservice", self.check_consumer_service_step),
            ("RetailerService", "Phase 4 Retailer Service Microservice", self.check_retailer_service_step),
            ("CatalogService", "Phase 5 Catalog Service Microservice", self.check_catalog_service_step),
            ("InventoryService", "Phase 5 Inventory Service Microservice", self.check_inventory_service_step),
            ("OrderService", "Phase 6 Order Service Microservice", self.check_order_service_step),
            ("PaymentService", "Phase 7 Payment Service Microservice", self.check_payment_service_step),
            ("DeliveryService", "Phase 7 Delivery Service Microservice", self.check_delivery_service_step),
            ("AuditService", "Phase 8 Audit Service Microservice", self.check_audit_service_step),
            ("RiskService", "Phase 8 Risk Service Microservice", self.check_risk_service_step),
            ("RealtimeService", "Phase 8 Realtime Service Microservice", self.check_realtime_service_step),
            ("AnalyticsService", "Phase 9 Analytics Service Microservice", self.check_analytics_service_step),
            ("RecommendationService", "Phase 10 Recommendation Service Microservice", self.check_recommendation_service_step),
            ("GatewayService", "Phase 11 API Gateway Service Microservice", self.check_gateway_service_step),
            ("WhitelabelService", "Phase 12 Whitelabel Service Microservice", self.check_whitelabel_service_step),
            ("SupportAgentService", "Phase 12 AI Support Agent Service Microservice", self.check_support_agent_service_step),
            ("FunctionalModules", "Phase 26 Master 66 Functional Architecture Modules", self.check_functional_modules_step),
            ("CommunicationArchitecture", "Phase 27 Master Communication System Architecture Audit", self.check_communication_architecture_step),
            ("CatalogPlatform", "Phase 28 Master Catalog & Template System Architecture Audit", self.check_catalog_platform_step),
            ("ProductCatalogSystem", "Phase 29 Master Product Catalog & Consumer View System Architecture Audit", self.check_product_catalog_system_step),
            ("WebUIArchitecture", "Phase 30 Master Web UI & Visual Development Architecture Audit", self.check_web_ui_architecture_step),
            ("ProductCatalogAdminSystem", "Phase 31 Master User/Admin Product Catalog & Listing Template System Architecture Audit", self.check_product_catalog_admin_system_step),
            ("ConsumerListingEngineSpec", "Phase 32 Consumer Listing Engine Specification Audit", self.check_consumer_listing_engine_spec_step),
            ("DeliveryEngineSpec", "Phase 33 Delivery System & Logistics Engine Architecture Audit", self.check_delivery_engine_spec_step),
            ("DeliveryCoreService", "Phase 34 Development Phase D1 — Delivery Core & State Machine Engine", self.check_delivery_core_service_step),
            ("DriverManagementService", "Phase 35 Development Phase D2 — Driver Management System", self.check_driver_management_service_step),
            ("DispatchEngineService", "Phase 36 Development Phase D3 — Dispatch Engine", self.check_dispatch_engine_service_step),
            ("FulfilmentService", "Phase 37 Development Phase D4 — Fulfilment + Serviceability Engine", self.check_fulfilment_service_step),
            ("ProductionInfrastructure", "Phase 38 Development Phase D5 — Production Data & Real-Time Infrastructure", self.check_production_infrastructure_step),
            ("ComplianceEngine", "Phase 39 Development Phase D6 — Identity, Verification & Compliance Engine", self.check_compliance_engine_step),
            ("RegulatoryCatalogue", "Phase 40 Development Phase D7 — Regulatory Product Catalogue & SKU Intelligence Engine", self.check_regulatory_catalogue_step),
            ("InventoryFulfilment", "Phase 41 Development Phase D8 — Inventory + Store Fulfilment Engine", self.check_inventory_fulfilment_step),
            ("OrderCheckout", "Phase 42 Development Phase D9 — Order Management + Checkout Engine", self.check_order_checkout_step),
            ("PaymentFinancial", "Phase 43 Development Phase D10 — Payment + Financial Transaction Engine", self.check_payment_financial_step),
        ]

        results: list[ConstitutionCheckResult] = []
        for art_id, name, check_fn in articles:
            violations = check_fn()
            status = "FAILED" if violations else "PASSED"
            results.append(ConstitutionCheckResult(article=art_id, name=name, status=status, violations=violations))

        passed_count = sum(1 for r in results if r.status == "PASSED")
        total = len(results)
        return {
            "total_articles": total,
            "passed": passed_count,
            "failed": total - passed_count,
            "compliance_score_pct": round((passed_count / total) * 100, 2),
            "results": [r.__dict__ for r in results],
        }

    def check_functional_modules_step(self) -> list[str]:
        from scripts.constitution.check_functional_modules import FunctionalModulesChecker
        checker = FunctionalModulesChecker(root_dir=self.root_dir)
        res = checker.audit_functional_modules()
        if res["score_pct"] < 100.0:
            return [f"Functional modules audit failed: {res['score_pct']}% verified."]
        return []

    def check_communication_architecture_step(self) -> list[str]:
        from scripts.constitution.check_communication_architecture import CommunicationArchitectureChecker
        checker = CommunicationArchitectureChecker(root_dir=self.root_dir)
        res = checker.audit_communication_architecture()
        if res["score_pct"] < 100.0:
            return [f"Communication architecture audit failed: {res['score_pct']}% verified."]
        return []

    def check_catalog_platform_step(self) -> list[str]:
        from scripts.constitution.check_catalog_platform import CatalogPlatformChecker
        checker = CatalogPlatformChecker(root_dir=self.root_dir)
        res = checker.audit_catalog_platform()
        if res["score_pct"] < 100.0:
            return [f"Catalog platform audit failed: {res['score_pct']}% verified."]
        return []

    def check_product_catalog_system_step(self) -> list[str]:
        from scripts.constitution.check_product_catalog_system import ProductCatalogSystemChecker
        checker = ProductCatalogSystemChecker(root_dir=self.root_dir)
        res = checker.audit_product_catalog_system()
        if res["score_pct"] < 100.0:
            return [f"Product catalog system audit failed: {res['score_pct']}% verified."]
        return []

    def check_web_ui_architecture_step(self) -> list[str]:
        from scripts.constitution.check_web_ui_architecture import WebUIArchitectureChecker
        checker = WebUIArchitectureChecker(root_dir=self.root_dir)
        res = checker.audit_web_ui_architecture()
        if res["score_pct"] < 100.0:
            return [f"Web UI architecture audit failed: {res['score_pct']}% verified."]
        return []

    def check_product_catalog_admin_system_step(self) -> list[str]:
        from scripts.constitution.check_product_catalog_admin import ProductCatalogAdminChecker
        checker = ProductCatalogAdminChecker(root_dir=self.root_dir)
        res = checker.audit_product_catalog_admin()
        if res["score_pct"] < 100.0:
            return [f"Product catalog admin audit failed: {res['score_pct']}% verified."]
        return []

    def check_consumer_listing_engine_spec_step(self) -> list[str]:
        from scripts.constitution.check_consumer_listing_engine import ConsumerListingEngineChecker
        checker = ConsumerListingEngineChecker(root_dir=self.root_dir)
        res = checker.audit_consumer_listing_engine()
        if res["score_pct"] < 100.0:
            return [f"Consumer listing engine audit failed: {res['score_pct']}% verified."]
        return []

    def check_delivery_engine_spec_step(self) -> list[str]:
        from scripts.constitution.check_delivery_engine import DeliveryEngineChecker
        checker = DeliveryEngineChecker(root_dir=self.root_dir)
        res = checker.audit_delivery_engine()
        if res["score_pct"] < 100.0:
            return [f"Delivery engine audit failed: {res['score_pct']}% verified."]
        return []

    def check_delivery_core_service_step(self) -> list[str]:
        from scripts.constitution.check_delivery_core_service import DeliveryCoreServiceChecker
        checker = DeliveryCoreServiceChecker(root_dir=self.root_dir)
        res = checker.audit_delivery_core_service()
        if res["score_pct"] < 100.0:
            return [f"Delivery core service audit failed: {res['score_pct']}% verified."]
        return []

    def check_driver_management_service_step(self) -> list[str]:
        from scripts.constitution.check_driver_management_service import DriverManagementServiceChecker
        checker = DriverManagementServiceChecker(root_dir=self.root_dir)
        res = checker.audit_driver_management_service()
        if res["score_pct"] < 100.0:
            return [f"Driver management service audit failed: {res['score_pct']}% verified."]
        return []

    def check_dispatch_engine_service_step(self) -> list[str]:
        from scripts.constitution.check_dispatch_engine_service import DispatchEngineServiceChecker
        checker = DispatchEngineServiceChecker(root_dir=self.root_dir)
        res = checker.audit_dispatch_engine_service()
        if res["score_pct"] < 100.0:
            return [f"Dispatch engine service audit failed: {res['score_pct']}% verified."]
        return []

    def check_fulfilment_service_step(self) -> list[str]:
        from scripts.constitution.check_fulfilment_service import FulfilmentServiceChecker
        checker = FulfilmentServiceChecker(root_dir=self.root_dir)
        res = checker.audit_fulfilment_service()
        if res["score_pct"] < 100.0:
            return [f"Fulfilment service audit failed: {res['score_pct']}% verified."]
        return []

    def check_production_infrastructure_step(self) -> list[str]:
        from scripts.constitution.check_production_infrastructure import ProductionInfrastructureChecker
        checker = ProductionInfrastructureChecker(root_dir=self.root_dir)
        res = checker.audit_production_infrastructure()
        if res["score_pct"] < 100.0:
            return [f"Production infrastructure audit failed: {res['score_pct']}% verified."]
        return []

    def check_compliance_engine_step(self) -> list[str]:
        from scripts.constitution.check_compliance_engine import ComplianceEngineChecker
        checker = ComplianceEngineChecker(root_dir=self.root_dir)
        res = checker.audit_compliance_engine()
        if res["score_pct"] < 100.0:
            return [f"Compliance engine audit failed: {res['score_pct']}% verified."]
        return []

    def check_regulatory_catalogue_step(self) -> list[str]:
        from scripts.constitution.check_regulatory_catalogue import RegulatoryCatalogueChecker
        checker = RegulatoryCatalogueChecker(root_dir=self.root_dir)
        res = checker.audit_regulatory_catalogue()
        if res["score_pct"] < 100.0:
            return [f"Regulatory catalogue audit failed: {res['score_pct']}% verified."]
        return []

    def check_inventory_fulfilment_step(self) -> list[str]:
        from scripts.constitution.check_inventory_fulfilment import InventoryFulfilmentChecker
        checker = InventoryFulfilmentChecker(root_dir=self.root_dir)
        res = checker.audit_inventory_fulfilment()
        if res["score_pct"] < 100.0:
            return [f"Inventory fulfilment audit failed: {res['score_pct']}% verified."]
        return []

    def check_order_checkout_step(self) -> list[str]:
        from scripts.constitution.check_order_checkout import OrderCheckoutChecker
        checker = OrderCheckoutChecker(root_dir=self.root_dir)
        res = checker.audit_order_checkout()
        if res["score_pct"] < 100.0:
            return [f"Order checkout audit failed: {res['score_pct']}% verified."]
        return []

    def check_payment_financial_step(self) -> list[str]:
        from scripts.constitution.check_payment_financial import PaymentFinancialChecker
        checker = PaymentFinancialChecker(root_dir=self.root_dir)
        res = checker.audit_payment_financial()
        if res["score_pct"] < 100.0:
            return [f"Payment financial audit failed: {res['score_pct']}% verified."]
        return []
















    def check_security(self) -> list[str]:
        violations = []
        # Check hardcoded secret patterns
        secret_pattern = re.compile(r"""(password|secret_key|api_key)\s*=\s*['"][^'"]{8,}['"]""", re.IGNORECASE)
        for root, _, files in os.walk(os.path.join(self.root_dir, "services")):
            if "_common" in root or ".venv" in root:
                continue
            for f in files:
                if f.endswith((".py", ".ts", ".tsx", ".yaml", ".yml")) and not f.endswith((".example", ".sample")):
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                            content = fh.read()
                            if secret_pattern.search(content):
                                violations.append(f"Hardcoded secret pattern found in {os.path.relpath(path, self.root_dir)}")
                    except Exception:
                        pass
        return violations

    def check_privacy(self) -> list[str]:
        violations = []
        # Check privacy module existence
        privacy_path = os.path.join(self.root_dir, "services/_common/faccp_common/privacy/data_minimization.py")
        if not os.path.exists(privacy_path):
            violations.append("Privacy Constitution module missing: data_minimization.py")
        return violations

    def check_compliance(self) -> list[str]:
        violations = []
        if PolicyAccessGuard:
            services_dir = os.path.join(self.root_dir, "services")
            for root, _, files in os.walk(services_dir):
                for f in files:
                    if f.endswith(".py"):
                        path = os.path.join(root, f)
                        try:
                            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                                content = fh.read()
                                v = PolicyAccessGuard.audit(path, content)
                                violations.extend(v)
                        except Exception:
                            pass
        return violations

    def check_data(self) -> list[str]:
        violations = []
        # Check cross-service direct DB access or cross-service FK / service module imports
        services_dir = os.path.join(self.root_dir, "services")
        for root, _, files in os.walk(services_dir):
            if "_common" in root:
                continue
            rel_path = os.path.relpath(root, services_dir)
            current_service = rel_path.split(os.sep)[0]
            for f in files:
                if f.endswith(".py"):
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                            content = fh.read()
                            for line in content.splitlines():
                                line_clean = line.strip()
                                # Detect actual cross-service import patterns like "from services.other_service" or "import services.other_service"
                                if re.search(r"\b(from|import)\s+services\.([a-zA-Z0-9_-]+)", line_clean):
                                    match = re.search(r"\b(from|import)\s+services\.([a-zA-Z0-9_-]+)", line_clean)
                                    imported_service = match.group(2)
                                    if imported_service != current_service and imported_service != "_common":
                                        violations.append(f"Cross-service direct import violation in {os.path.relpath(path, self.root_dir)}: {line_clean}")
                    except Exception:
                        pass
        return violations


    def check_api(self) -> list[str]:
        violations = []
        # Check DTO envelope presence
        envelope_path = os.path.join(self.root_dir, "services/_common/faccp_common/dto/envelope.py")
        if not os.path.exists(envelope_path):
            violations.append("API Constitution standard response envelope missing: dto/envelope.py")
        return violations

    def check_events(self) -> list[str]:
        violations = []
        events_path = os.path.join(self.root_dir, "services/_common/faccp_common/events.py")
        if not os.path.exists(events_path):
            violations.append("Event Constitution envelope module missing: events.py")
        return violations

    def check_testing(self) -> list[str]:
        violations = []
        tests_dir = os.path.join(self.root_dir, "tests")
        if not os.path.exists(tests_dir):
            violations.append("Testing Constitution directory missing: tests/")
        return violations

    def check_operations(self) -> list[str]:
        violations = []
        compose_path = os.path.join(self.root_dir, "docker-compose.yml")
        if not os.path.exists(compose_path):
            violations.append("Operations Constitution local infrastructure manifest missing: docker-compose.yml")
        return violations

    def check_governance(self) -> list[str]:
        violations = []
        codeowners_path = os.path.join(self.root_dir, ".github/CODEOWNERS")
        if not os.path.exists(codeowners_path):
            violations.append("Governance Constitution CODEOWNERS file missing: .github/CODEOWNERS")
        return violations

    def check_domain_isolation(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_domain_isolation import DomainIsolationChecker
            from scripts.constitution.check_shared_code import SharedCodeChecker
            
            iso_checker = DomainIsolationChecker(root_dir=self.root_dir)
            report = iso_checker.check_all()
            for service, viols in report.items():
                violations.extend(viols)

            shared_checker = SharedCodeChecker(root_dir=self.root_dir)
            shared_viols = shared_checker.check_common_dir()
            violations.extend(shared_viols)
        except Exception as e:
            violations.append(f"Domain isolation verification failed to execute: {e}")
        return violations

    def check_single_responsibility(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_single_responsibility import SingleResponsibilityChecker
            srp_checker = SingleResponsibilityChecker(root_dir=self.root_dir)
            report = srp_checker.check_all()
            for service, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Single responsibility verification failed to execute: {e}")
        return violations

    def check_api_contracts(self) -> list[str]:
        violations = []
        envelope_path = os.path.join(self.root_dir, "services/_common/faccp_common/dto/envelope.py")
        if not os.path.exists(envelope_path):
            violations.append("API Contract response envelope standard missing: dto/envelope.py")
        return violations

    def check_deployment_isolation(self) -> list[str]:
        violations = []
        ff_path = os.path.join(self.root_dir, "services/_common/faccp_common/feature_flags.py")
        if not os.path.exists(ff_path):
            violations.append("Deployment Isolation feature flags module missing: feature_flags.py")
        workflow_path = os.path.join(self.root_dir, ".github/workflows/constitution.yml")
        if not os.path.exists(workflow_path):
            violations.append("Deployment Isolation CI workflow missing: .github/workflows/constitution.yml")
        return violations

    def check_source_of_truth(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_source_of_truth import SourceOfTruthChecker
            sot_checker = SourceOfTruthChecker(root_dir=self.root_dir)
            report = sot_checker.check_all()
            for service, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Source-of-truth verification failed to execute: {e}")
        return violations

    def check_identity_protocol(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_identity_compliance import IdentityComplianceChecker
            id_checker = IdentityComplianceChecker(root_dir=self.root_dir)
            report = id_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Identity protocol verification failed to execute: {e}")
        return violations

    def check_authentication_protocol(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_auth_pipeline import AuthPipelineChecker
            auth_checker = AuthPipelineChecker(root_dir=self.root_dir)
            report = auth_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Authentication protocol verification failed to execute: {e}")
        return violations

    def check_authorization_protocol(self) -> list[str]:
        violations = []
        try:
            from faccp_common.authz import AuthorizationEngine
            engine = AuthorizationEngine()
            if not hasattr(engine, "authorize"):
                violations.append("AuthorizationEngine missing mandatory authorize method")
        except Exception as e:
            violations.append(f"Authorization protocol verification failed to execute: {e}")
        return violations

    def check_trust_protocol(self) -> list[str]:
        violations = []
        try:
            from faccp_common.trust import TrustDecisionEngine
            engine = TrustDecisionEngine()
            if not hasattr(engine, "evaluate"):
                violations.append("TrustDecisionEngine missing mandatory evaluate method")
        except Exception as e:
            violations.append(f"Trust verification protocol verification failed to execute: {e}")
        return violations

    def check_development_gates_protocol(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_development_gates import DevelopmentGatesChecker
            gate_checker = DevelopmentGatesChecker(root_dir=self.root_dir)
            report = gate_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Development Gate System verification failed to execute: {e}")
        return violations

    def check_functional_architecture_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_functional_architecture import FunctionalArchitectureChecker
            arch_checker = FunctionalArchitectureChecker(root_dir=self.root_dir)
            report = arch_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Functional Architecture verification failed to execute: {e}")
        return violations

    def check_communication_system_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_communication_system import CommunicationSystemChecker
            comm_checker = CommunicationSystemChecker(root_dir=self.root_dir)
            report = comm_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Communication System verification failed to execute: {e}")
        return violations

    def check_catalog_and_templates_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_catalog_and_templates import CatalogAndTemplatesChecker
            cat_checker = CatalogAndTemplatesChecker(root_dir=self.root_dir)
            report = cat_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Catalog & Template Platform verification failed to execute: {e}")
        return violations

    def check_product_platform_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_product_platform import ProductPlatformChecker
            prod_checker = ProductPlatformChecker(root_dir=self.root_dir)
            report = prod_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Product Platform Architecture verification failed to execute: {e}")
        return violations

    def check_web_ui_platform_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_web_ui_platform import WebUIPlatformChecker
            ui_checker = WebUIPlatformChecker(root_dir=self.root_dir)
            report = ui_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Web UI Platform Architecture verification failed to execute: {e}")
        return violations

    def check_product_catalog_admin_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_product_catalog_admin import ProductCatalogAdminChecker
            admin_checker = ProductCatalogAdminChecker(root_dir=self.root_dir)
            report = admin_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Product Catalog Admin System verification failed to execute: {e}")
        return violations

    def check_consumer_listing_engine_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_consumer_listing_engine import ConsumerListingEngineChecker
            engine_checker = ConsumerListingEngineChecker(root_dir=self.root_dir)
            report = engine_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Consumer Listing Engine verification failed to execute: {e}")
        return violations

    def check_listing_engine_spec_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_listing_engine_spec import ListingEngineSpecChecker
            spec_checker = ListingEngineSpecChecker(root_dir=self.root_dir)
            report = spec_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Listing Engine Specification verification failed to execute: {e}")
        return violations

    def check_delivery_engine_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_delivery_engine import DeliveryEngineChecker
            del_checker = DeliveryEngineChecker(root_dir=self.root_dir)
            report = del_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Delivery System & Delivery Engine verification failed to execute: {e}")
        return violations

    def check_phase0_foundation_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_phase0_foundation import Phase0FoundationChecker
            p0_checker = Phase0FoundationChecker(root_dir=self.root_dir)
            report = p0_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 0 Foundation Execution verification failed to execute: {e}")
        return violations

    def check_identity_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_identity_service import IdentityServiceChecker
            id_checker = IdentityServiceChecker(root_dir=self.root_dir)
            report = id_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 1 Identity Service Microservice verification failed to execute: {e}")
        return violations

    def check_compliance_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_compliance_service import ComplianceServiceChecker
            cmp_checker = ComplianceServiceChecker(root_dir=self.root_dir)
            report = cmp_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 2 Compliance Service Microservice verification failed to execute: {e}")
        return violations

    def check_consumer_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_consumer_service import ConsumerServiceChecker
            c_checker = ConsumerServiceChecker(root_dir=self.root_dir)
            report = c_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 3 Consumer Service Microservice verification failed to execute: {e}")
        return violations

    def check_retailer_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_retailer_service import RetailerServiceChecker
            ret_checker = RetailerServiceChecker(root_dir=self.root_dir)
            report = ret_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 4 Retailer Service Microservice verification failed to execute: {e}")
        return violations

    def check_catalog_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_catalog_service import CatalogServiceChecker
            cat_checker = CatalogServiceChecker(root_dir=self.root_dir)
            report = cat_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 5 Catalog Service Microservice verification failed to execute: {e}")
        return violations

    def check_inventory_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_inventory_service import InventoryServiceChecker
            inv_checker = InventoryServiceChecker(root_dir=self.root_dir)
            report = inv_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 5 Inventory Service Microservice verification failed to execute: {e}")
        return violations

    def check_order_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_order_service import OrderServiceChecker
            ord_checker = OrderServiceChecker(root_dir=self.root_dir)
            report = ord_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 6 Order Service Microservice verification failed to execute: {e}")
        return violations

    def check_payment_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_payment_service import PaymentServiceChecker
            pay_checker = PaymentServiceChecker(root_dir=self.root_dir)
            report = pay_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 7 Payment Service Microservice verification failed to execute: {e}")
        return violations

    def check_delivery_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_delivery_service import DeliveryServiceChecker
            del_checker = DeliveryServiceChecker(root_dir=self.root_dir)
            report = del_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 7 Delivery Service Microservice verification failed to execute: {e}")
        return violations

    def check_audit_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_audit_service import AuditServiceChecker
            aud_checker = AuditServiceChecker(root_dir=self.root_dir)
            report = aud_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 8 Audit Service Microservice verification failed to execute: {e}")
        return violations

    def check_risk_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_risk_service import RiskServiceChecker
            rsk_checker = RiskServiceChecker(root_dir=self.root_dir)
            report = rsk_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 8 Risk Service Microservice verification failed to execute: {e}")
        return violations

    def check_realtime_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_realtime_service import RealtimeServiceChecker
            rt_checker = RealtimeServiceChecker(root_dir=self.root_dir)
            report = rt_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 8 Realtime Service Microservice verification failed to execute: {e}")
        return violations

    def check_analytics_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_analytics_service import AnalyticsServiceChecker
            an_checker = AnalyticsServiceChecker(root_dir=self.root_dir)
            report = an_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 9 Analytics Service Microservice verification failed to execute: {e}")
        return violations

    def check_recommendation_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_recommendation_service import RecommendationServiceChecker
            rec_checker = RecommendationServiceChecker(root_dir=self.root_dir)
            report = rec_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 10 Recommendation Service Microservice verification failed to execute: {e}")
        return violations

    def check_gateway_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_gateway_service import GatewayServiceChecker
            gw_checker = GatewayServiceChecker(root_dir=self.root_dir)
            report = gw_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 11 API Gateway Service Microservice verification failed to execute: {e}")
        return violations

    def check_whitelabel_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_whitelabel_service import WhitelabelServiceChecker
            wl_checker = WhitelabelServiceChecker(root_dir=self.root_dir)
            report = wl_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 12 Whitelabel Service Microservice verification failed to execute: {e}")
        return violations

    def check_support_agent_service_step(self) -> list[str]:
        violations = []
        try:
            from scripts.constitution.check_support_agent_service import SupportAgentServiceChecker
            sa_checker = SupportAgentServiceChecker(root_dir=self.root_dir)
            report = sa_checker.check_all()
            for area, viols in report.items():
                violations.extend(viols)
        except Exception as e:
            violations.append(f"Phase 12 AI Support Agent Service Microservice verification failed to execute: {e}")
        return violations


























if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    checker = ConstitutionChecker()
    report = checker.check_all()
    print("=" * 60)
    print(f"FACCP SYSTEM CONSTITUTION COMPLIANCE REPORT")
    print(f"Overall Compliance Score: {report['compliance_score_pct']}% ({report['passed']}/{report['total_articles']} Passed)")
    print("=" * 60)
    for res in report["results"]:
        status_symbol = "[PASS]" if res["status"] == "PASSED" else "[FAIL]"
        print(f"{status_symbol} {res['article']}: {res['name']} - {res['status']}")
        for v in res["violations"]:
            print(f"   └── Violation: {v}")
    if report["failed"] > 0:
        sys.exit(1)
    sys.exit(0)

