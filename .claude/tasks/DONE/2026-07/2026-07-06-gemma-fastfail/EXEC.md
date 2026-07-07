# EXEC — 2026-07-06-gemma-fastfail
## v1
--timeout default -> 60.0 (help updated). After build, `chat.max_retries = 0` (guarded) so
the probe makes a single attempt. Invoke-failure branch now detects timeout errors and
appends a hint (cold/overloaded model, model id not served to key, or entitlement; try a
longer --timeout or a different --model). One file; agents' shared code untouched.
