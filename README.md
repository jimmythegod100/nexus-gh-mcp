# NEXUS GitHub MCP Server

MCP server for GitHub repository automation via the REST API.

## Quick Start

```bash
poetry install
cp .env.example .env
export GITHUB_TOKEN=ghp_your_token
poetry run nexus-gh-mcp
```

Service runs on http://localhost:8003

## MCP Tools

- **create_repo** — create a new repository
- **create_branch** — branch from an existing ref
- **create_workflow** — push a workflow file (via push_file)
- **push_file** — create or update a repository file

## Endpoints

- GET /health
- GET /mcp/tools
- POST /tools/create_repo
- POST /tools/create_branch
- POST /tools/create_pull_request
- POST /tools/push_file
