import os

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

os.environ.setdefault("GITHUB_TOKEN", "test-token")
os.environ.setdefault("GITHUB_OWNER", "jimmythegod100")

from src.main import app


@pytest.fixture
def client():
    mock_gh = AsyncMock()
    mock_gh.ping = AsyncMock(return_value=True)
    mock_gh.create_repo = AsyncMock(
        return_value={
            "html_url": "https://github.com/jimmythegod100/test",
            "full_name": "jimmythegod100/test",
        }
    )
    with TestClient(app) as test_client:
        import src.main as main_module

        main_module.gh_client = mock_gh
        yield test_client


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "nexus-gh-mcp"


def test_mcp_tools_list(client):
    response = client.get("/mcp/tools")
    assert response.status_code == 200
    names = [t["name"] for t in response.json()["tools"]]
    assert "create_repo" in names
    assert "push_file" in names


def test_create_repo(client):
    response = client.post(
        "/tools/create_repo",
        json={"name": "test-repo", "description": "Test", "private": False},
    )
    assert response.status_code == 200
    assert "html_url" in response.json()
