import type {
  SendMessageRequest,
  SendMessageResponse,
} from "@/types/chat";

/**
 * MOCK chat endpoint.
 *
 * The backend gateway and the MCP orchestrator do not exist yet, so this
 * simulates a network round-trip and returns a canned agent reply.
 *
 * TODO(backend/mcp): replace the body with a real `fetch` to the gateway,
 * keeping this function signature stable so callers (stores/) don't change.
 */
const MOCK_LATENCY_MS = 700;

export async function sendChatMessage(
  request: SendMessageRequest,
  signal?: AbortSignal,
): Promise<SendMessageResponse> {
  await delay(MOCK_LATENCY_MS, signal);
  return { reply: buildMockReply(request.prompt) };
}

function buildMockReply(prompt: string): string {
  const text = prompt.trim();
  return (
    `🤖 (mock) Received your message: “${text}”.\n\n` +
    `The backend gateway and the MCP orchestrator are not connected yet — this is a ` +
    `stubbed reply from the AI agent. A real response from the sub-agents ` +
    `(web, PDF, images) running in parallel will appear here later.`
  );
}

function delay(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) {
      reject(new DOMException("Aborted", "AbortError"));
      return;
    }
    const timer = setTimeout(resolve, ms);
    signal?.addEventListener(
      "abort",
      () => {
        clearTimeout(timer);
        reject(new DOMException("Aborted", "AbortError"));
      },
      { once: true },
    );
  });
}
