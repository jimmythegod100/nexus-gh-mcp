import base64
import logging
from typing import Any, Optional

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)


class GitHubClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.GITHUB_API_URL
        self.owner = settings.GITHUB_OWNER
        self.headers = {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def create_repo(
        self,
        name: str,
        description: str = "",
        private: bool = False,
        auto_init: bool = True,
    ) -> dict[str, Any]:
        payload = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/user/repos",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def create_branch(self, repo: str, branch: str, from_ref: str = "main") -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            ref_resp = await client.get(
                f"{self.base_url}/repos/{self.owner}/{repo}/git/ref/heads/{from_ref}",
                headers=self.headers,
            )
            ref_resp.raise_for_status()
            sha = ref_resp.json()["object"]["sha"]
            create_resp = await client.post(
                f"{self.base_url}/repos/{self.owner}/{repo}/git/refs",
                headers=self.headers,
                json={"ref": f"refs/heads/{branch}", "sha": sha},
            )
            create_resp.raise_for_status()
            return create_resp.json()

    async def create_pull_request(
        self,
        repo: str,
        title: str,
        head: str,
        base: str = "main",
        body: str = "",
    ) -> dict[str, Any]:
        payload = {"title": title, "head": head, "base": base, "body": body}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/repos/{self.owner}/{repo}/pulls",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def push_file(
        self,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str = "main",
    ) -> dict[str, Any]:
        encoded = base64.b64encode(content.encode()).decode()
        async with httpx.AsyncClient(timeout=30.0) as client:
            sha: Optional[str] = None
            existing = await client.get(
                f"{self.base_url}/repos/{self.owner}/{repo}/contents/{path}",
                headers=self.headers,
                params={"ref": branch},
            )
            if existing.status_code == 200:
                sha = existing.json().get("sha")
            payload: dict[str, Any] = {
                "message": message,
                "content": encoded,
                "branch": branch,
            }
            if sha:
                payload["sha"] = sha
            response = await client.put(
                f"{self.base_url}/repos/{self.owner}/{repo}/contents/{path}",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def ping(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/user", headers=self.headers)
                return response.status_code == 200
        except Exception as exc:
            logger.warning("GitHub ping failed: %s", exc)
            return False
