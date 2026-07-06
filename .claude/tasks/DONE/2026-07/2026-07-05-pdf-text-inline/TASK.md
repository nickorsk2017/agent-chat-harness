# TASK — 2026-07-05-pdf-text-inline
owner: Engineer
immutable: true

## Requirements
- R1: Stop persisting uploaded PDFs to disk. The gateway extracts the PDF text
  in-memory at upload time and forwards it to the orchestrator; doc_analyzer
  receives text, never a file path.
- R2: Images keep the current file flow (vision needs bytes) — uploads volume stays.
- R3: Thread memory semantics preserved: extracted text stored in the LangGraph
  `documents` channel; follow-up turns answer from stored text with no re-analysis.
- R4: doc_analyzer loses file IO: no path-based tools, no pypdf; pypdf moves to the
  backend gateway.

## Acceptance
- A1: POST /api/chat/files with a PDF writes nothing to upload_dir; orchestrator
  context carries document_name + document_text; doc summarize/ask runs on that text.
- A2: Image upload still saves to upload_dir and routes image_path as before.
- A3: Planner prompt has no pdf_path/extract_text; doc tasks reference the document
  by name and dispatch injects stored text into sub-agent arguments.
- A4: Tests updated and passing (mcp test_memory.py, backend test_chat_thread.py);
  all changed files compile.

## Constraints
- No changes to web_agent/image_analyzer behavior or frontend API shape.
