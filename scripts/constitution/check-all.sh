#!/bin/bash
set -e

echo "=================================================="
echo "      FACCP SYSTEM CONSTITUTION AUDIT RUNNER    "
echo "=================================================="

PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD scripts/constitution/check_compliance.py
$PYTHON_CMD scripts/constitution/check_source_of_truth.py
$PYTHON_CMD scripts/constitution/check_identity_compliance.py
$PYTHON_CMD scripts/constitution/check_auth_pipeline.py
$PYTHON_CMD scripts/constitution/check_development_gates.py
$PYTHON_CMD scripts/constitution/check_functional_architecture.py
$PYTHON_CMD scripts/constitution/check_communication_system.py
$PYTHON_CMD scripts/constitution/check_catalog_and_templates.py
$PYTHON_CMD scripts/constitution/check_product_platform.py
$PYTHON_CMD scripts/constitution/check_web_ui_platform.py
$PYTHON_CMD scripts/constitution/check_product_catalog_admin.py
$PYTHON_CMD scripts/constitution/check_consumer_listing_engine.py
$PYTHON_CMD scripts/constitution/check_listing_engine_spec.py
$PYTHON_CMD scripts/constitution/check_delivery_engine.py
$PYTHON_CMD scripts/constitution/check_phase0_foundation.py
$PYTHON_CMD scripts/constitution/check_identity_service.py
$PYTHON_CMD scripts/constitution/check_compliance_service.py
$PYTHON_CMD scripts/constitution/check_consumer_service.py
$PYTHON_CMD scripts/constitution/check_retailer_service.py
$PYTHON_CMD scripts/constitution/check_catalog_service.py
$PYTHON_CMD scripts/constitution/check_inventory_service.py
$PYTHON_CMD scripts/constitution/check_order_service.py
$PYTHON_CMD scripts/constitution/check_payment_service.py
$PYTHON_CMD scripts/constitution/check_delivery_service.py
$PYTHON_CMD scripts/constitution/check_audit_service.py
$PYTHON_CMD scripts/constitution/check_risk_service.py
$PYTHON_CMD scripts/constitution/check_realtime_service.py
$PYTHON_CMD scripts/constitution/check_analytics_service.py
$PYTHON_CMD scripts/constitution/check_recommendation_service.py

echo "✅ Pre-commit & local constitution audit complete."






















