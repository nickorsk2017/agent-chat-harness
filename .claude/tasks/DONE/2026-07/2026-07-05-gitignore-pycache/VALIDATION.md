# VALIDATION — 2026-07-05-gitignore-pycache
## v1
verdict: PASS
- R1/A1: `.gitignore` contains `__pycache__/`, `*.py[cod]`; check-ignore confirms both backend and mcp pyc paths ignored.
- R2/A2: `git ls-files | grep -c __pycache__` = 0; on-disk caches intact.
- A3: diff = .gitignore + index deletions only; no source changes. Commit pending (Engineer, post-closure per pre-commit gate).
issues: []
