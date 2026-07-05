# VALIDATION — 2026-07-04-mcp-flatten-packages

validation_version: 1
result: PASS

## Acceptance conformance
- A1 packages/ wrapper gone from the layout; each agent is mcp/<import_root>/ with code
  directly inside + co-located pyproject.toml; no <name>/<name> doubling: PASS (5/5).
- A2 Each moved pyproject builds its import root via flat-layout hatch target
  (only-include=["."], sources={"."="<name>"}): PASS (present in all 5).
- A3 mcp/pyproject.toml uv.sources + docstring point at mcp/<name>; no stale `packages/`
  install/source path in any *.toml/*.md (sole grep hit is explanatory prose): PASS.
- A4 mcp/README.md table + install cmds and mcp/CLAUDE.md folder map reflect flat layout: PASS.
- A5 py_compile of every moved module across 5 agents: PASS; each folder importable-shaped.
- R4 imports unchanged (import-root based): PASS.

## Plan conformance
S1–S5 executed. RK-1 (hatch flat target) resolved with only-include/sources form; RK-2
(pycache) mooted — moved, not deleted; RK-3 (scope) honored: only mcp/ touched.

## Issues
(none blocking)

## Note (non-blocking, environment)
5 empty `mcp/packages/<dist>/` directories remain — the build sandbox mount denies rmdir.
They are empty (0 entries) and untracked by git (whole mcp/ tree is new/untracked), so they
never enter the repo; they disappear on a clean checkout or via Finder. Hatch wheel targets
were set to the correct flat-layout form but not build-tested (no build backend / PyPI in
sandbox); py_compile + reference correctness are the in-sandbox gate and pass.
