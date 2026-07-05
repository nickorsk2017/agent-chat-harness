"""gateway — the API Gateway bounded context.

REST boundary for the frontend chat. Delegates domain work to the
master_orchestrator MCP agent and maps its result into the shared ApiResponse
envelope. Contains no domain logic itself.
"""
