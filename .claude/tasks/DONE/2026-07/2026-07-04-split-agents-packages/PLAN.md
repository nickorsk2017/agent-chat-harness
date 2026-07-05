# PLAN — 2026-07-04-split-agents-packages
plan_version: 1

## Target structure (satisfies R1, R4)
Convert the single `mcp/mcp_agents/*` namespace into one directory per distribution,
each an independent, pip-installable package with its own `pyproject.toml`:

```
mcp/
  packages/
    agent-core/        # shared dist -> import root `agent_core`
      agent_core/{__init__,envelope,llm}.py
      pyproject.toml   # name = agent-core
    web-agent/         # import root `web_agent`
      web_agent/{__init__,config,main}.py + db/ schemas/ tools/ prompts/
      pyproject.toml   # name = web-agent ; deps: fastmcp,pydantic,pydantic-settings,httpx,agent-core
    doc-analyzer/      # import root `doc_analyzer`  (same shape)
    image-analyzer/    # import root `image_analyzer`
    master-orchestrator/ # import root `master_orchestrator`
      pyproject.toml   # deps: fastmcp,langchain*,langgraph,pydantic*,agent-core (NO sub-agent deps)
```
Each package keeps the CLAUDE.md-mandated layout; only the namespace root moves from
`mcp_agents.<agent>` to `<agent>` (top-level import root). Old `mcp/mcp_agents/` removed.

## Shared-code decision (R2) — ADR-style
- Chosen: extract `mcp_agents/shared/{envelope,llm}.py` into a standalone distribution
  `agent-core` (import root `agent_core`); every agent lists `agent-core` as an explicit
  dependency. Satisfies "no sibling-agent import" without code duplication or drift.
- Rejected: vendoring the two files into each agent (4x duplication, drift risk on the
  envelope contract that all agents must share).
- Rejected: keeping `mcp_agents.shared` (violates R1/R2 — forces the umbrella package).
- Consequence: `agent-core` is a real dependency; local dev installs it via a path/editable
  dep. Keep it dependency-light (only pydantic + langchain-core) so agents don't inherit bloat.

## Import rewrite map (R2, A2)
- `from mcp_agents.shared.envelope import ...`  -> `from agent_core.envelope import ...`
- `from mcp_agents.shared.llm import ...`        -> `from agent_core.llm import ...`
- `from mcp_agents.<agent>.X import ...`         -> `from <agent>.X import ...` (drop prefix)
- Orchestrator sub-agent registry (config.py `args=["-m","mcp_agents.web_agent.main"]`)
  -> `["-m","web_agent.main"]` etc. Still launched as MCP servers over stdio, never imported
  (R3 preserved — `subagent_client.py` uses FastMCP `Client`, no Python import of siblings).

## pyproject strategy (R1, A1)
- One `pyproject.toml` per package. Build backend hatchling; `[tool.hatch.build.targets.wheel]
  packages = ["<import_root>"]`.
- Dependencies scoped per agent from its actual imports:
  - agent-core: pydantic, langchain-core
  - web-agent: fastmcp, pydantic, pydantic-settings, httpx, agent-core
  - doc-analyzer: fastmcp, pydantic, pydantic-settings, agent-core (+ pdf provider dep if used)
  - image-analyzer: fastmcp, pydantic, pydantic-settings, agent-core
  - master-orchestrator: fastmcp, langchain, langchain-core, langgraph, pydantic,
    pydantic-settings, agent-core  (explicitly NOT web/doc/image packages)
- Each app package declares a console entry point `[project.scripts]` so `main()` is runnable,
  keeping `python -m <root>.main` working too (R4).
- Old top-level `mcp/pyproject.toml`: replace umbrella build with a dev aggregator that
  editable-installs all packages for local work (or a workspace README section). Decide in
  Executor per least-disruption; must not re-introduce a single shared dist.

## Executor sequencing
- P1: Create `packages/agent-core` (move shared/{envelope,llm}.py -> agent_core/, add __init__, pyproject).
- P2: For each agent create `packages/<agent-dist>/<import_root>/`, git-move its subtree
  (config, main, db, schemas, tools, prompts) out from `mcp_agents/<agent>/`.
- P3: Rewrite imports across all moved files per the map (mechanical; no logic change).
- P4: Write per-package `pyproject.toml` (P1..master) with scoped deps + entry points.
- P5: Update orchestrator `config.py` subagent args to the new module paths.
- P6: Replace `mcp/pyproject.toml` umbrella with a dev-aggregator; delete emptied
  `mcp/mcp_agents/` (including `shared/`, `__init__`). Purge `__pycache__`.
- P7: Update `mcp/README.md` (per-package install/run) and verify `.env.example` vs each
  config.py (R5). Update `mcp/CLAUDE.md` "Folder structure"/"Running" only if now inaccurate.

## Risks
- Editable/path resolution for `agent-core` in local dev (mitigate: document `pip install -e`
  per package, or a root dev-aggregator that installs all in order).
- Hidden `mcp_agents.` references in tests/docs/CI (mitigate: repo-wide grep in P3/P7, A2 gate).
- CLAUDE.md line 63 documents `python -m mcp_agents.{name}.main`; if structure changes, that
  running rule must be updated to stay authoritative (R5, precedence rule).

## Verification hooks for Validator (maps to Acceptance)
- A1: each pyproject present, distinct `name`, scoped deps.
- A2: `grep -rn "mcp_agents"` returns nothing in source (only allowed in history/docs notes);
  no sibling-agent cross-import.
- A3: fresh-interpreter import smoke of each `<root>.main` and orchestrator client registry.
- A4/A5: README/.env consistency; envelope + concurrent asyncio.gather dispatch intact.
