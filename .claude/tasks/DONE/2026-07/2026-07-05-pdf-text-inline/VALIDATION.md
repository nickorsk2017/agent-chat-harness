# VALIDATION — 2026-07-05-pdf-text-inline

## v1 — PASS
- A1 PASS (static): PDF branch writes nothing (no write_bytes on pdf path); context
  keys document_name/document_text produced by gateway and consumed by
  _split_document_context; dispatch injects text into doc requests.
- A2 PASS: image branch still writes to upload_dir and emits image_path (verified
  by grep + new test test_image_still_saved_to_upload_dir).
- A3 PASS: repo grep — zero pdf_path/extract_text/pypdf references left under mcp/;
  planner prompt lists doc tools with `doc` and forbids inventing names.
- A4 PARTIAL-BY-DESIGN: both test suites rewritten/extended (5 mcp + 4 backend
  upload tests); every changed file passes py_compile. PyPI is unreachable from
  the sandbox, so runtime pytest execution is delegated to the Engineer
  (fallback explicitly approved in PLAN v1 validation plan):
  run `pytest backend/tests mcp/master_orchestrator/tests` host-side or rebuild
  the stack (docker compose up -d --build) and smoke-test a CV upload.
- Constraint check: web_agent/image_analyzer/frontend untouched.
No blocking issues.
