"""
Pytest configuration for NERO Voice Assistant tests.

This file configures pytest with custom fixtures and settings.
"""

import pytest
import sys
import os


# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "timeout": 30,
        "retries": 2,
    }
