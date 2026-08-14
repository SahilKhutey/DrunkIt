"""Unit tests for Dockerfiles non-root security and multi-stage build standards."""

import os
import pytest


def test_dockerfile_non_root_security():
    """Verify all Dockerfiles use multi-stage builds and execute as non-root USER drunkit."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    docker_dir = os.path.join(root_dir, "infra", "docker")
    dockerfiles = [f for f in os.listdir(docker_dir) if f.startswith("Dockerfile.")]

    assert len(dockerfiles) >= 5

    for df in dockerfiles:
        path = os.path.join(docker_dir, df)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "USER drunkit" in content, f"Dockerfile {df} must declare non-root USER drunkit"
        assert "AS builder" in content, f"Dockerfile {df} must use multi-stage builder"
        assert "AS runtime" in content, f"Dockerfile {df} must use multi-stage runtime"
