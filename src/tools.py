from src.models import MCPToolDefinition

CREATE_REPO_TOOL = MCPToolDefinition(
    name="create_repo",
    description="Create a GitHub repository",
    input_schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "description": {"type": "string"},
            "private": {"type": "boolean"},
            "auto_init": {"type": "boolean"},
        },
        "required": ["name"],
    },
    output_schema={"type": "object", "properties": {"html_url": {"type": "string"}}},
)

CREATE_BRANCH_TOOL = MCPToolDefinition(
    name="create_branch",
    description="Create a branch from an existing ref",
    input_schema={
        "type": "object",
        "properties": {
            "repo": {"type": "string"},
            "branch": {"type": "string"},
            "from_ref": {"type": "string"},
        },
        "required": ["repo", "branch"],
    },
    output_schema={"type": "object", "properties": {"ref": {"type": "string"}}},
)

CREATE_WORKFLOW_TOOL = MCPToolDefinition(
    name="create_workflow",
    description="Create or update a GitHub Actions workflow file",
    input_schema={
        "type": "object",
        "properties": {
            "repo": {"type": "string"},
            "path": {"type": "string"},
            "content": {"type": "string"},
            "message": {"type": "string"},
            "branch": {"type": "string"},
        },
        "required": ["repo", "path", "content", "message"],
    },
    output_schema={"type": "object", "properties": {"commit": {"type": "object"}}},
)

PUSH_FILE_TOOL = MCPToolDefinition(
    name="push_file",
    description="Create or update a file in a repository",
    input_schema={
        "type": "object",
        "properties": {
            "repo": {"type": "string"},
            "path": {"type": "string"},
            "content": {"type": "string"},
            "message": {"type": "string"},
            "branch": {"type": "string"},
        },
        "required": ["repo", "path", "content", "message"],
    },
    output_schema={"type": "object", "properties": {"content": {"type": "object"}}},
)

MCP_TOOLS = [CREATE_REPO_TOOL, CREATE_BRANCH_TOOL, CREATE_WORKFLOW_TOOL, PUSH_FILE_TOOL]
