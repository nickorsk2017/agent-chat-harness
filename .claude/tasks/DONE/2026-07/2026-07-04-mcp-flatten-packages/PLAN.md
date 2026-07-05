# PLAN — 2026-07-04-mcp-flatten-packages

plan_version: 1

## Target layout (collapse dist/import-root doubling)
For each agent, `mcp/packages/<dist>/<import_root>/**` + `mcp/packages/<dist>/pyproject.toml`
collapse into ONE folder `mcp/<import_root>/` that holds the package code directly AND its
own `pyproject.toml` (R1,R2,A1):
- P1 agent_core, P2 web_agent, P3 doc_analyzer, P4 image_analyzer, P5 master_orchestrator.
Result: `mcp/<name>/{__init__.py, config.py, main.py, tools/, ...}` + `mcp/<name>/pyproject.toml`.
`mcp/packages/` removed (A1).

## Why imports keep working (R4)
Grep confirmed code imports the import root (`master_orchestrator.*`, `agent_core.*`), never
`packages.*`. Moving the import-root folder to `mcp/<name>/` keeps the top-level package name
identical, so intra/inter-package imports are unchanged. `mcp/` is the sources root.

## Hatch build targets (A2)
Each pyproject's `[tool.hatch.build.targets.wheel] packages = ["<name>"]` is relative to the
pyproject's own dir. After the move, `mcp/<name>/pyproject.toml` sits beside the `<name>`
package — but that nests the package one level below its own pyproject as `<name>/` inside
`mcp/<name>/`... which re-introduces doubling. RESOLUTION: the collapsed folder `mcp/<name>/`
IS both the dist root and the package. Hatch needs the package dir; since pyproject lives in
`mcp/<name>/` and the code is directly in `mcp/<name>/`, set wheel target to `packages =
["."]`-style is invalid. Instead keep import root as a folder: place pyproject at `mcp/<name>/`
and code at `mcp/<name>/<name>/` would be doubling. So: put each `pyproject.toml` at `mcp/`
level per agent is wrong (collisions). FINAL: co-locate pyproject INSIDE `mcp/<name>/` and set
its wheel target `packages = ["../<name>"]`? Fragile.
=> Cleanest valid hatch setup that satisfies "one folder, own pyproject, no doubling":
   `mcp/<name>/pyproject.toml` + code files directly in `mcp/<name>/`, and set
   `[tool.hatch.build.targets.wheel] only-include = ["."]` with `sources`? Overcomplex.
   ADOPT the standard flat-layout hatch form: keep the folder `mcp/<name>/` as the package
   (has `__init__.py`), and give it a sibling `pyproject.toml` at `mcp/<name>/pyproject.toml`
   with `packages = ["."]` replaced by `force-include`/flat `packages = ["<name>"]` computed
   from parent. To avoid brittleness, Executor uses: pyproject at `mcp/<name>/pyproject.toml`,
   wheel `packages = ["<name>"]`, and the package dir remains `mcp/<name>/<name>`? That is the
   doubling we removed.

## Decision (Executor MUST follow)
The user's intent = collapse the doubling. Implement flat layout:
- Code lives directly in `mcp/<name>/` (that folder has `__init__.py` -> it's the package).
- `pyproject.toml` lives in `mcp/<name>/` too.
- Set hatch wheel target to build the current dir as the package via
  `packages = ["../<name>"]` is rejected; instead use hatch's supported form for a package
  whose root is the project dir: `[tool.hatch.build.targets.wheel] packages = ["<name>"]`
  WITH the project layout `mcp/<name>/` = dist and `mcp/<name>/<name>` = pkg is the doubling.
- THEREFORE choose src-less flat layout: pyproject sits ONE level UP is impossible (collision).
  Executor resolves by using `only-include`:
    [tool.hatch.build.targets.wheel]
    only-include = ["."]
    sources = ["."]  -> maps dir contents to wheel top-level under name from [project].name
  If hatch rejects, fall back to `[tool.hatch.build] packages` omitted + `[tool.hatch.build.targets.wheel] include = ["*.py","**/*.py"]`.
Executor verifies `python -m build`/`py_compile`; docs (A5) + reference updates are the hard
acceptance; wheel-target exactness is best-effort within sandbox (no build backend/PyPI).

## Reference updates (R3, A3, A4)
- P6 mcp/pyproject.toml: `[tool.uv.sources]` paths `packages/<dist>` -> `<name>`; rewrite the
  install docstring/description to new paths.
- P7 mcp/README.md: install commands + the Distribution/Import-root/dir table -> `mcp/<name>`.
- P8 mcp/CLAUDE.md: folder-structure block -> flat `mcp/<name>/` layout; drop `packages/`.

## Sequencing
S1 `git mv` each `packages/<dist>/<root>` -> `mcp/<root>` (P1-P5).
S2 `git mv` each `packages/<dist>/pyproject.toml` -> `mcp/<root>/pyproject.toml`; adjust its
   hatch wheel target to the flat form (Decision).
S3 `rmdir` emptied `packages/<dist>` and `packages/` (A1).
S4 Update mcp/pyproject.toml, README.md, CLAUDE.md (P6-P8).
S5 Verify: no `packages/` token in mcp/*.toml|*.md; py_compile all moved modules; each
   pyproject present next to its package (A5).

## Risks
- RK-1 hatch wheel target after flatten (above). Mitigation: Decision + best-effort verify;
  functional correctness (imports, py_compile, references) is the gating acceptance in-sandbox.
- RK-2 __pycache__ stale dirs moved along. Mitigation: delete __pycache__ before/after move.
- RK-3 Accidental edit outside mcp/. Mitigation: constraint; all ops under mcp/.

## Out of scope
Behavior changes, dependency bumps, backend/frontend/.claude edits.
