"""Unit tests for Kubernetes manifests YAML syntax, securityContext, and health probes."""

import os
import pytest
import yaml


def test_kubernetes_manifests_validity():
    """Verify all Kubernetes YAML manifests parse cleanly with valid apiVersion and kind."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    k8s_dir = os.path.join(root_dir, "infra", "kubernetes")

    yaml_files = []
    for root, _, files in os.walk(k8s_dir):
        for file in files:
            if file.endswith(".yaml") or file.endswith(".yml"):
                yaml_files.append(os.path.join(root, file))

    assert len(yaml_files) >= 5

    for yf in yaml_files:
        with open(yf, "r", encoding="utf-8") as f:
            docs = list(yaml.safe_load_all(f))
            for doc in docs:
                if doc is None:
                    continue
                assert "apiVersion" in doc, f"Manifest {yf} missing apiVersion"
                assert "kind" in doc, f"Manifest {yf} missing kind"


def test_order_deployment_security_and_probes():
    """Verify Order deployment enforces runAsNonRoot, allowPrivilegeEscalation=false, liveness & readiness probes."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    dep_path = os.path.join(root_dir, "infra", "kubernetes", "order", "deployment.yaml")
    with open(dep_path, "r", encoding="utf-8") as f:
        dep = yaml.safe_load(f)

    pod_spec = dep["spec"]["template"]["spec"]
    assert pod_spec["securityContext"]["runAsNonRoot"] is True

    container = pod_spec["containers"][0]
    assert container["securityContext"]["allowPrivilegeEscalation"] is False
    assert "livenessProbe" in container
    assert "readinessProbe" in container
    assert "resources" in container
