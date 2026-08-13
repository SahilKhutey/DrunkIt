"""
Unit tests for Driver App and Developer SDKs.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sdk_python_path = os.path.join(root_dir, "packages/sdk-python")

if sdk_python_path not in sys.path:
    sys.path.insert(0, sdk_python_path)

from faccp_sdk.client import FACCPClient


def test_python_sdk_client_init():
    client = FACCPClient(base_url="http://localhost:8000", api_key="test_key")
    assert client.base_url == "http://localhost:8000"
    assert client.api_key == "test_key"


def test_driver_app_directory_exists():
    driver_app_dir = os.path.join(root_dir, "apps/driver-app")
    assert os.path.exists(driver_app_dir)
    assert os.path.exists(os.path.join(driver_app_dir, "package.json"))
