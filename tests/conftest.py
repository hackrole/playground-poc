import pytest
from fastapi.testclient import TestClient
from playground.app import app


@pytest.fixture
def client():
    return TestClient(app)
