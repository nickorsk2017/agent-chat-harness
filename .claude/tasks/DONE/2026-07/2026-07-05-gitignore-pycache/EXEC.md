# EXEC — 2026-07-05-gitignore-pycache
## v1
- R1: root `.gitignore` now = `.DS_Store` + `__pycache__/` + `*.py[cod]`.
- R2: `git rm -r --cached` on all tracked `__pycache__` dirs; 0 tracked matches remain; files kept on disk.
- Changed: `.gitignore` (modified); index-only deletions of `**/__pycache__/*.pyc`.
- Test: `git ls-files | grep -c __pycache__` -> 0; `git check-ignore backend/_common/__pycache__/x.pyc` -> ignored.
