# TASK — 2026-07-04-mcp-flatten-packages
owner: Engineer
immutable: true

## Requirements
- R1: Remove the `mcp/packages/` wrapper AND the doubled `<dist-name>/<import_root>`
  nesting. Each agent becomes a single top-level folder under `mcp/` whose name equals
  its Python import root, containing the code directly + its own `pyproject.toml`:
    packages/agent-core/agent_core/**            -> mcp/agent_core/**
    packages/web-agent/web_agent/**              -> mcp/web_agent/**
    packages/doc-analyzer/doc_analyzer/**        -> mcp/doc_analyzer/**
    packages/image-analyzer/image_analyzer/**    -> mcp/image_analyzer/**
    packages/master-orchestrator/master_orchestrator/** -> mcp/master_orchestrator/**
  Each agent's `pyproject.toml` moves up next to its import-root folder (e.g.
  `mcp/agent_core/pyproject.toml`... or `mcp/<name>/` holding both — see A1).
- R2: Agents remain independent, separately-installable distributions, each with its own
  `pyproject.toml`. No shared umbrella package is introduced.
- R3: Update every path reference to the old layout: the dev-aggregator
  `mcp/pyproject.toml` (`[tool.uv.sources]` paths + install docstring), `mcp/README.md`,
  and `mcp/CLAUDE.md` folder-structure section.
- R4: Python imports must keep working unchanged (they already use import roots like
  `master_orchestrator.*`, not `packages.*`).

## Acceptance
- A1: `mcp/packages/` no longer exists. Each of the 5 agents is `mcp/<import_root>/`
  with its code directly inside and its own `pyproject.toml` co-located so the
  distribution root == the agent folder (import root nested one level:
  `mcp/<name>/<name>/` is NOT allowed — flatten to `mcp/<name>/` as the dist dir
  containing `<name>` package + pyproject, matching how `packages/<dist>/<root>` collapses).
- A2: Every moved `pyproject.toml` still builds its own import root (hatch wheel target
  unchanged, still valid relative to its dir).
- A3: `mcp/pyproject.toml` `[tool.uv.sources]` and comments point at the new paths
  (`mcp/<name>`), no `packages/` references remain anywhere in mcp/*.toml or mcp/*.md.
- A4: `mcp/CLAUDE.md` folder map + `mcp/README.md` reflect the new layout.
- A5: A sanity import of each package from `mcp/` succeeds where deps allow, or (deps
  unavailable in sandbox) `py_compile` of every moved module passes and no `packages/`
  path token remains in configs/docs.

## Constraints
- Scope: `mcp/` subsystem only. Do NOT touch `backend/`, `frontend/`, or `.claude/`.
- Preserve file contents; this is a move + reference-update, not a rewrite.
- Use `git mv` so history is preserved.
- Latest-version pins in pyprojects stay as-is.
