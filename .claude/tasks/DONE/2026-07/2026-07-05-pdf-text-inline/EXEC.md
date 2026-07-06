# EXEC — 2026-07-05-pdf-text-inline

## v1
Per approved PLAN v1.

backend:
- pyproject.toml: +pypdf>=4.0.0.
- gateway/services/chat_service.py: save_uploads -> process_uploads; PDF branch
  extracts text in-memory (_extract_pdf_text: pypdf over BytesIO; malformed ->
  GatewayValidationError "could not read PDF"; empty -> "no extractable text");
  context = document_name + document_text; NO disk write. Image branch unchanged
  (upload_dir created lazily, images only). schemas/chat.py: context docstring.
- tests/test_uploads.py (new): pdf in-memory + nothing saved; image saved;
  malformed pdf 400; unsupported type 400.

mcp/master_orchestrator:
- prompts/orchestrate.py: doc_analyzer tools = summarize_document/ask_document with
  {"doc", ...}; text injected automatically (planner told to never copy text);
  new_document routing rule replaces pdf_path; extract_text removed.
- tools/graph.py: _split_document_context() (document_text -> documents channel,
  planner sees new_document hint only); _plan_node stores docs deterministically
  pre-planning; _inject_doc_text() fills request.text from state at dispatch with
  fallback to latest doc; results re-bound to PLANNED tasks so injected text never
  enters synthesis results JSON; removed _extract_target/_new_pdf_extract_tasks/
  _harvest_documents; docstrings updated.
- schemas/http.py: context description updated.
- tests/test_memory.py: rewritten for the new contract (5 tests incl. injection
  and fallback).

mcp/doc_analyzer:
- schemas: ExtractRequest/ExtractedText/DocumentMeta removed; Summarize/Ask take
  doc+text; DocSummary.path->doc; DocAnswer.path->doc, cited_pages->cited_sections.
- tools: extract_text tool/provider removed; providers are pure text->LLM (no pypdf,
  dep dropped from pyproject). prompts reference '{doc}' and quote passages.

infra/docs: docker-compose uploads comment (images only); mcp/README example context.
