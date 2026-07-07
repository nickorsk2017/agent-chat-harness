# EXEC — 2026-07-06-fix-gemma-check-mount
## v1
Makefile `gemma-check` now bind-mounts the host script into the container instead of
relying on it being baked into the image:
  $(COMPOSE) run --rm --no-deps -v "$(CURDIR)/mcp/scripts:/app/scripts:ro" \
      mcp python /app/scripts/gemma_healthcheck.py $(ARGS)
The installed packages (agent_core, master_orchestrator, langchain) stay in the image;
only /app/scripts is overlaid with the current host copy, so a stale image no longer
misses the file and no rebuild is needed. `:ro` = read-only; --no-deps + ARGS unchanged.
One file changed (Makefile).
