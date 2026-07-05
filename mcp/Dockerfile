# syntax=docker/dockerfile:1
# MCP — master_orchestrator plus its three sub-agents (web / doc / image).
# The orchestrator fans out to the sub-agents in-process over stdio, so all four
# distributions are installed into this single image. Install order matters:
# `agent_core` is a dependency of every agent and goes first.

FROM python:3.11-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY . .
RUN pip install --upgrade pip \
    && pip install ./agent_core \
    && pip install ./web_agent ./doc_analyzer ./image_analyzer ./master_orchestrator

EXPOSE 8100
# Serve the orchestrator over streamable-HTTP (path /mcp) so the gateway can reach it.
# Transport/host/port are chosen here at run time — the application code is untouched.
CMD ["python", "-c", "from master_orchestrator.main import mcp; mcp.run(transport='streamable-http', host='0.0.0.0', port=8100)"]
