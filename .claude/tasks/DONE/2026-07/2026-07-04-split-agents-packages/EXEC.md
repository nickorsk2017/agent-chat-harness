# EXEC — 2026-07-04-split-agents-packages
exec_version: 1

## Summary (per PLAN.md P1–P7)
- P1: Extracted `mcp_agents/shared/{envelope,llm}.py` -> new dist `packages/agent-core/`
  (import root `agent_core`), added its `pyproject.toml`.
- P2: Split each agent into its own dist dir with a top-level import root:
  `packages/{web-agent,doc-analyzer,image-analyzer,master-orchestrator}/<root>/…`,
  preserving db/schemas/tools/prompts/config.py/main.py layout.
- P3: Rewrote imports (mechanical, no logic change):
  `mcp_agents.shared.*`->`agent_core.*`; `mcp_agents.<agent>.*`->`<agent>.*`.
- P4: Wrote one `pyproject.toml` per package — distinct `name`, scoped deps, hatchling wheel
  target = import root, `[project.scripts]` console entry (`web-agent`, `doc-analyzer`,
  `image-analyzer`, `master-orchestrator`). Every agent depends on `agent-core`; the
  orchestrator depends on NO sibling agent package.
- P5: Orchestrator `config.py` subagent launch args -> `["-m","<agent>.main"]`
  (still launched as MCP servers over stdio; `subagent_client.py` uses FastMCP `Client`,
  no Python import of siblings — R3 preserved).
- P6: Replaced umbrella `mcp/pyproject.toml` with a dev-aggregator (editable-installs all
  packages; builds no shared package). Deleted the entire old `mcp/mcp_agents/` tree
  (required enabling file-delete for host-origin files).
- P7: Updated `mcp/README.md` (per-package install/run, distribution table) and
  `mcp/CLAUDE.md` (Folder structure + Running). Verified `.env.example` prefixes match all
  four `config.py` `env_prefix` values.

## Changed files
- ADD  packages/agent-core/{pyproject.toml, agent_core/{__init__,envelope,llm}.py}
- ADD  packages/web-agent/{pyproject.toml, web_agent/**}
- ADD  packages/doc-analyzer/{pyproject.toml, doc_analyzer/**}
- ADD  packages/image-analyzer/{pyproject.toml, image_analyzer/**}
- ADD  packages/master-orchestrator/{pyproject.toml, master_orchestrator/**}
- MOD  packages/master-orchestrator/master_orchestrator/config.py (subagent args)
- MOD  (all moved modules) import lines rewritten agent_core / <agent>
- REPL mcp/pyproject.toml (umbrella -> dev aggregator)
- MOD  mcp/README.md, mcp/CLAUDE.md
- DEL  mcp/mcp_agents/** (old umbrella namespace)

## Verification performed (env-limited)
- `compileall packages` rc=0 (all modules parse).
- pyproject audit: 5 distinct dist names, correct wheel targets, scoped deps, entry points;
  master-orchestrator has no sibling-agent dep.
- AST import scan across packages: no sibling-agent import, no `mcp_agents` import.
- repo grep: `mcp_agents` absent from all source/docs/toml.
- `.env.example` keys match every config.py env_prefix.
- NOTE: full `pip install -e` / runtime import blocked — sandbox has no PyPI access
  (403 proxy) and no fastmcp/langchain installed. Left for Validator to confirm in an
  environment with deps; offline structural checks all pass.
