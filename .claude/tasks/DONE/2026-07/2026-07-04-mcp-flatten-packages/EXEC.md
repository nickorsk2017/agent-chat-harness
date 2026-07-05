# EXEC — 2026-07-04-mcp-flatten-packages

exec_version: 1

## Summary
Flattened mcp/ per PLAN S1–S5. Each agent is now ONE top-level folder `mcp/<import_root>/`
holding its code directly + its own `pyproject.toml`. Removed the `packages/` wrapper and
the `<dist-name>/<import_root>` doubling. All path references updated; all modules compile.

## Moves (S1–S3)
- mcp/packages/agent-core/agent_core/**            -> mcp/agent_core/**            (+ pyproject.toml)
- mcp/packages/web-agent/web_agent/**              -> mcp/web_agent/**             (+ pyproject.toml)
- mcp/packages/doc-analyzer/doc_analyzer/**        -> mcp/doc_analyzer/**          (+ pyproject.toml)
- mcp/packages/image-analyzer/image_analyzer/**    -> mcp/image_analyzer/**        (+ pyproject.toml)
- mcp/packages/master-orchestrator/master_orchestrator/** -> mcp/master_orchestrator/** (+ pyproject.toml)
Used filesystem `mv` (git mv was blocked by a stale .git/index.lock; irrelevant since the
whole mcp/ tree is untracked new work — git will add only the new flat layout).

## Hatch build targets (S2, A2)
Each moved pyproject now sits inside its package dir, so the wheel target changed from
`packages = ["<name>"]` to flat-layout form:
  [tool.hatch.build.targets.wheel]
  only-include = ["."]
  sources = { "." = "<name>" }
maps the folder contents to the `<name>` import package in the wheel.

## Reference updates (S4, R3/A3/A4)
- mcp/pyproject.toml: `[tool.uv.sources]` paths packages/<dist> -> <name>; install
  docstring + description rewritten to the flat layout.
- mcp/README.md: distribution table -> `mcp/<name>` Path column; install commands ->
  `pip install -e <name>`; aggregator note updated.
- mcp/CLAUDE.md: Folder structure block rewritten to the flat `mcp/<name>/` tree (no
  packages/, no doubling).

## Verification (S5, A5)
- No stale `packages/` path token in mcp/*.toml or mcp/*.md (only remaining hit is the
  explanatory phrase "there is no `packages/` wrapper" in CLAUDE.md — intentional prose).
- py_compile of every moved module across all 5 agents: PASS.
- Each `mcp/<name>/` has co-located pyproject.toml + __init__.py: PASS (5/5).
- Imports unchanged (code uses import roots, never `packages.*`) — R4 satisfied.

## Known remnant (non-blocking)
The 5 now-empty `mcp/packages/<dist>/` dirs can't be `rmdir`'d from the build sandbox
(mount denies removal). They are EMPTY (0 entries) and git tracks nothing under them, so
they don't enter the repo. They vanish on a clean checkout or can be deleted in Finder.
