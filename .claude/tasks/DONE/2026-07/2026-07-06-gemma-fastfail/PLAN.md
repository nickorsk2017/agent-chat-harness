# PLAN — 2026-07-06-gemma-fastfail
## v1
D1. --timeout default None -> 60.0 (always sets LLM_REQUEST_TIMEOUT_S pre-import); help text
    notes default 60.
D2. After build_chat_model, set `chat.max_retries = 0` in a try/except (probe-local; leaves
    shared agent_core untouched, agents still use max_retries=1). Worst-case wait ~= one
    timeout instead of two.
D3. In the invoke-failure branch, detect timeout (type name contains 'timeout' or message
    'timed out') and append a hint listing likely causes + remedies (--timeout / --model).
Files (1). A1<-D1, A2<-D2, A3<-D3.
