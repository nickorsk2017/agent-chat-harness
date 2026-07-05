# VALIDATION — 2026-07-04-split-agents-packages
result: PASS
validation_version: 1

## Acceptance conformance
- A1 PASS: 5 distinct distributions (agent-core, web-agent, doc-analyzer, image-analyzer,
  master-orchestrator); each pyproject wheel target == its import root; deps scoped per agent.
- A2 PASS: AST scan + repo grep — zero sibling-agent imports, zero `mcp_agents` references in
  source/docs/toml. Orchestrator pyproject has no sibling-agent dependency.
- A3 PASS (offline): every `<agent>.main` imports only its own root + agent_core + 3rd-party;
  `subagent_client.py` reaches sub-agents via FastMCP `Client` with `-m <agent>.main` launch
  (no Python import of siblings). `compileall` rc=0. Full runtime import not run — sandbox has
  no PyPI/deps (documented limitation, not a defect); structural equivalence verified.
- A4 PASS: README rewritten (per-package install/run + distribution table); CLAUDE.md folder
  structure + running sections updated; `.env.example` keys match all four config env_prefix.
- A5 PASS: `AgentResponse` returned in all 4 agents' tool modules; orchestrator retains
  `asyncio.gather` concurrent dispatch (graph.py:50); fail-soft envelope path unchanged.

## Requirement conformance
- R1 PASS  R2 PASS (agent-core shared dist; no sibling import)  R3 PASS (MCP client only)
  R4 PASS (layout + console entry points)  R5 PASS (docs/env updated).

## Issues
(none blocking)

## Note
Recommend a follow-up smoke run of `pip install -e` per package + `python -c "import <root>.main"`
in a deps-enabled environment to confirm A3 at runtime. Non-blocking; all offline gates pass.
