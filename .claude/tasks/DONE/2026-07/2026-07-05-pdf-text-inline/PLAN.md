# PLAN — 2026-07-05-pdf-text-inline

## v1

### Design
The `documents` state channel already persists `{key: text}` and synthesis already
answers from it. Move extraction from doc_analyzer to the gateway and key documents
by NAME instead of path; doc sub-agent tools become pure text->LLM.

Context contract (gateway -> orchestrator):
- PDF:   `document_name` = original filename, `document_text` = extracted text.
- Image: `image_path` (unchanged).

### Changes
1. backend/pyproject.toml: add `pypdf>=4.0.0`.
2. backend/gateway/services/chat_service.py — save_uploads():
   - pdf branch: PdfReader(BytesIO(data)) in-memory, join page texts; empty text ->
     GatewayValidationError ("no extractable text — scanned PDF? attach as image");
     context["document_name"|"document_text"]; NO disk write.
   - image branch unchanged. upload_dir now only created/used for images.
3. mcp/master_orchestrator/prompts/orchestrate.py:
   - doc_analyzer tool list: summarize_document {"request": {"doc": str, "max_points": int}},
     ask_document {"request": {"doc": str, "question": str}}; extract_text removed.
   - File routing: context key `new_document` (a document NAME whose full text is
     already stored) -> exactly one doc task using that EXACT name; never invent
     names/paths. pdf_path rules deleted; image rules unchanged.
4. mcp/master_orchestrator/tools/graph.py:
   - _plan_node: pop document_text/document_name from request.context ->
     `{name: text}` documents update BEFORE planning; planner gets sanitized context
     where those keys are replaced by `new_document: <name>`; return documents update.
   - _dispatch_node: delete _new_pdf_extract_tasks/_harvest_documents/_extract_target;
     for DOC tasks inject request["text"] from state documents by request["doc"]
     (fallback: most recent stored doc); planner-supplied text never required.
   - Module docstring updated (documents keyed by name, extraction at gateway).
5. mcp/doc_analyzer:
   - schemas/http.py: SummarizeRequest{doc, text, max_points}, AskRequest{doc, text,
     question}; ExtractRequest/ExtractResponse removed.
   - schemas/document.py: DocSummary.path->doc, DocAnswer.path->doc; ExtractedText &
     DocumentMeta removed.
   - tools/doc_tools.py: extract_text tool removed.
   - tools/providers.py: summarize/ask take (doc, text, ...), no file IO;
     extract_text/_parse_pages removed; pyproject: drop pypdf.
6. docker-compose.yml: update uploads-volume comment (images only).
7. Tests:
   - mcp test_memory.py: turn-1 uses {"document_name": "cv.pdf", "document_text": ...};
     assert documents stored with NO sub-agent call, planner saw sanitized context;
     replace duplicate-extract test with text-injection test (doc task gets text from
     state); reducer test unchanged.
   - backend test_chat_thread.py: adapt if it touches uploads (inspect at exec time).

### Risks
- Planner (gemma) must emit `doc` instead of `path`: prompt states it explicitly and
  dispatch falls back to the latest stored document when `doc` is missing/wrong.
- Large PDFs inflate orchestrate payload/state: acceptable (cap 15MB upload; synthesis
  already truncates via document_max_chars).

### Validation plan
- python -m py_compile on all changed py files.
- pytest mcp/master_orchestrator/tests backend/tests if deps installable in sandbox;
  otherwise Engineer runs them host-side before deploy.
- grep: no pdf_path / extract_text / pypdf references left in mcp except archives.
