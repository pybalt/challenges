import logging
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from .tools.bash import BashTool20241022, BashTool20250124
from .tools.computer import ComputerTool20241022, ComputerTool20250124
from .tools.edit import EditTool20241022, EditTool20250124
from .tools.base import ToolResult

class ExecuteRequest(BaseModel):
    tool_name: str
    input: dict[str, Any]
    tool_version: str = "computer_use_20241022"

app = FastAPI()

tool_classes = {
    "bash": {
        "computer_use_20241022": BashTool20241022,
        "computer_use_20250124": BashTool20250124,
    },
    "computer": {
        "computer_use_20241022": ComputerTool20241022,
        "computer_use_20250124": ComputerTool20250124,
    },
    "str_replace_based_edit": {
        "computer_use_20241022": EditTool20241022,
        "computer_use_20250124": EditTool20250124,
    },
}

@app.post("/execute_tool")
async def execute_tool(req: ExecuteRequest) -> dict:
    if req.tool_name not in tool_classes:
        return {"error": f"Unknown tool {req.tool_name}"}
    if req.tool_version not in tool_classes[req.tool_name]:
        return {"error": f"Unknown version {req.tool_version} for tool {req.tool_name}"}
    cls = tool_classes[req.tool_name][req.tool_version]
    tool = cls()
    try:
        result: ToolResult = tool(**req.input)
        return {
            "output": result.output,
            "error": result.error,
            "base64_image": result.base64_image,
        }
    except Exception as e:
        logging.exception(e)
        return {"error": str(e)}