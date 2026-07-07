# EXEC — 2026-07-06-gemma-langchain
## v1
Rewrote the probe to the agents' LangChain path: adds mcp/ to sys.path, lazily imports
build_chat_model + HumanMessage + master_orchestrator.config.settings, builds the model
with settings.llm_provider/model/api_key/base_url (as planner.py/graph.py) and invokes
one HumanMessage. Missing key/deps -> CONFIG; invoke exception/empty -> DOWN; reply -> UP.
--timeout sets LLM_REQUEST_TIMEOUT_S pre-import. --json + exit codes unchanged. Makefile
unchanged. One file.
