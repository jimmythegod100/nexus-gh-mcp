import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from src.config import get_settings, setup_logging
from src.github_client import GitHubClient
from src.models import (
    CreateBranchRequest,
    CreatePullRequestRequest,
    CreateRepoRequest,
    HealthCheckResponse,
    PushFileRequest,
)
from src.tools import MCP_TOOLS

logger = logging.getLogger(__name__)
setup_logging()

gh_client: GitHubClient | None = None
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global gh_client
    gh_client = GitHubClient()
    logger.info("nexus-gh-mcp started")
    yield
    logger.info("nexus-gh-mcp shutdown")


app = FastAPI(title="NEXUS GitHub MCP Server", version="0.1.0", lifespan=lifespan)


@app.post("/tools/create_repo")
async def create_repo(req: CreateRepoRequest):
    try:
        result = await gh_client.create_repo(
            name=req.name,
            description=req.description,
            private=req.private,
            auto_init=req.auto_init,
        )
        return {"html_url": result.get("html_url"), "full_name": result.get("full_name")}
    except Exception as e:
        logger.error("create_repo failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/tools/create_branch")
async def create_branch(req: CreateBranchRequest):
    try:
        result = await gh_client.create_branch(req.repo, req.branch, req.from_ref)
        return {"ref": result.get("ref")}
    except Exception as e:
        logger.error("create_branch failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/tools/create_pull_request")
async def create_pull_request(req: CreatePullRequestRequest):
    try:
        result = await gh_client.create_pull_request(
            req.repo, req.title, req.head, req.base, req.body
        )
        return {"html_url": result.get("html_url"), "number": result.get("number")}
    except Exception as e:
        logger.error("create_pull_request failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/tools/push_file")
async def push_file(req: PushFileRequest):
    try:
        result = await gh_client.push_file(
            req.repo, req.path, req.content, req.message, req.branch
        )
        return {"content": result.get("content"), "commit": result.get("commit")}
    except Exception as e:
        logger.error("push_file failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/health")
async def health_check():
    settings = get_settings()
    github_ok = await gh_client.ping() if gh_client else False
    return HealthCheckResponse(
        status="healthy" if github_ok else "degraded",
        service="nexus-gh-mcp",
        uptime_seconds=int(time.time() - start_time),
        github_connected=github_ok,
        owner=settings.GITHUB_OWNER,
    )


@app.get("/mcp/tools")
async def list_mcp_tools():
    return {"tools": [tool.model_dump() for tool in MCP_TOOLS]}


@app.get("/")
async def root():
    return {
        "service": "nexus-gh-mcp",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "tools": "/mcp/tools",
            "create_repo": "/tools/create_repo",
            "create_branch": "/tools/create_branch",
            "create_pull_request": "/tools/create_pull_request",
            "push_file": "/tools/push_file",
        },
    }


def run() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    run()
