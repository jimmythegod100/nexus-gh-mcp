import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

os.environ.setdefault("GITHUB_TOKEN", "test-token")
os.environ.setdefault("GITHUB_OWNER", "jimmythegod100")

from src.github_client import GitHubClient
from src.tools import MCP_TOOLS


def test_gh_mcp_tools_registered():
    names = {tool.name for tool in MCP_TOOLS}
    assert "create_repo" in names
    assert "push_file" in names
    assert "create_branch" in names


@pytest.mark.asyncio
async def test_github_client_create_repo():
    client = GitHubClient()
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "html_url": "https://github.com/jimmythegod100/mock-repo",
        "full_name": "jimmythegod100/mock-repo",
    }
    mock_response.raise_for_status = MagicMock()

    mock_http = AsyncMock()
    mock_http.post = AsyncMock(return_value=mock_response)
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=None)

    with patch("src.github_client.httpx.AsyncClient", return_value=mock_http):
        result = await client.create_repo("mock-repo", description="Mock")

    assert result["full_name"] == "jimmythegod100/mock-repo"
    mock_http.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_github_client_create_branch():
    client = GitHubClient()
    ref_response = MagicMock()
    ref_response.json.return_value = {"object": {"sha": "abc123"}}
    ref_response.raise_for_status = MagicMock()
    create_response = MagicMock()
    create_response.json.return_value = {"ref": "refs/heads/feature/test"}
    create_response.raise_for_status = MagicMock()

    mock_http = AsyncMock()
    mock_http.get = AsyncMock(return_value=ref_response)
    mock_http.post = AsyncMock(return_value=create_response)
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=None)

    with patch("src.github_client.httpx.AsyncClient", return_value=mock_http):
        result = await client.create_branch("nexus-control-plane", "feature/test")

    assert result["ref"] == "refs/heads/feature/test"


@pytest.mark.asyncio
async def test_github_client_create_pull_request():
    client = GitHubClient()
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "html_url": "https://github.com/jimmythegod100/nexus-control-plane/pull/1",
        "number": 1,
    }
    mock_response.raise_for_status = MagicMock()

    mock_http = AsyncMock()
    mock_http.post = AsyncMock(return_value=mock_response)
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=None)

    with patch("src.github_client.httpx.AsyncClient", return_value=mock_http):
        result = await client.create_pull_request(
            "nexus-control-plane", "Test PR", "feature/test", body="Automated test"
        )

    assert result["number"] == 1


@pytest.mark.asyncio
async def test_github_client_push_file():
    client = GitHubClient()
    existing = MagicMock()
    existing.status_code = 404
    put_response = MagicMock()
    put_response.json.return_value = {"content": {"path": "README.md"}, "commit": {"sha": "deadbeef"}}
    put_response.raise_for_status = MagicMock()

    mock_http = AsyncMock()
    mock_http.get = AsyncMock(return_value=existing)
    mock_http.put = AsyncMock(return_value=put_response)
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=None)

    with patch("src.github_client.httpx.AsyncClient", return_value=mock_http):
        result = await client.push_file(
            "nexus-control-plane", "README.md", "# Test", "Update readme"
        )

    assert result["content"]["path"] == "README.md"


@pytest.mark.asyncio
async def test_github_client_ping_success():
    client = GitHubClient()
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_http = AsyncMock()
    mock_http.get = AsyncMock(return_value=mock_response)
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=None)

    with patch("src.github_client.httpx.AsyncClient", return_value=mock_http):
        assert await client.ping() is True


@pytest.mark.asyncio
async def test_github_client_ping_failure():
    client = GitHubClient()
    with patch("src.github_client.httpx.AsyncClient", side_effect=OSError("network down")):
        assert await client.ping() is False
