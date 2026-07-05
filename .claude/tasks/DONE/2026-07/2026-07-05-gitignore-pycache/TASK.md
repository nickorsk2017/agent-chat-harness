# TASK — 2026-07-05-gitignore-pycache
owner: Engineer
immutable: true

## Requirements
- R1: Ignore Python bytecode caches repo-wide: add `__pycache__/` (and `*.pyc`) to the root `.gitignore`.
- R2: Untrack already-committed `__pycache__` files (`git rm -r --cached`) so R1 takes effect; working-tree files stay on disk.

## Acceptance
- A1: `git status` clean of `__pycache__` noise after touching any .py file.
- A2: No tracked path matching `__pycache__` remains in the index.
- A3: Single commit, no source-code changes.

## Constraints
- Root `.gitignore` only; do not modify subsystem .gitignore files.
