from typing import Any, Optional

from pydantic import BaseModel, Field


class CreateRepoRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    private: bool = False
    auto_init: bool = True


class CreateBranchRequest(BaseModel):
    repo: str
    branch: str
    from_ref: str = "main"


class CreatePullRequestRequest(BaseModel):
    repo: str
    title: str
    head: str
    base: str = "main"
    body: str = ""


class PushFileRequest(BaseModel):
    repo: str
    path: str
    content: str
    message: str
    branch: str = "main"


class MCPToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


class HealthCheckResponse(BaseModel):
    status: str
    service: str
    uptime_seconds: int
    github_connected: bool
    owner: str
