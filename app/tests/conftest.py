import os

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    # Tests rely on local docker services running:
    # postgres on localhost:5432, redis on localhost:6379
    # Ensure .env exists or set env vars in your shell.
    return TestClient(app)