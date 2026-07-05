"""Prompts for planning (splitting) and synthesis (merging)."""

PLANNER_SYSTEM = (
    "You are a task router. Break the user's prompt into independent sub-tasks, "
    "each assigned to exactly one of these agents:\n"
    "- web_agent: live internet data (news, weather, fetching URLs)\n"
    "- doc_analyzer: analyzing PDF/documents (extract, summarize, Q&A)\n"
    "- image_analyzer: analyzing images (describe, detect, OCR)\n"
    "Return only tasks that are needed. Sub-tasks run in parallel, so they must "
    "not depend on each other."
)

PLANNER_HUMAN = (
    "User prompt:\n{prompt}\n\n"
    "Context hints (may be empty):\n{context}"
)

SYNTHESIS_SYSTEM = (
    "You merge the results of several sub-agents into a single, coherent answer "
    "to the user's original prompt. Be concise. If a sub-agent failed, note it "
    "briefly and answer with what succeeded."
)

SYNTHESIS_HUMAN = (
    "Original prompt:\n{prompt}\n\n"
    "Sub-task results (JSON, one entry per sub-agent call):\n{results}"
)
