import { useChatStore } from "@/stores/chatStore";

describe("chatStore.send", () => {
  beforeEach(() => {
    useChatStore.getState().reset();
  });

  it("appends a user message then the mock assistant reply", async () => {
    await useChatStore.getState().send("Hello, agent");

    const { messages, isSending, error } = useChatStore.getState();
    expect(messages).toHaveLength(2);
    expect(messages[0].role).toBe("user");
    expect(messages[0].content).toBe("Hello, agent");
    expect(messages[1].role).toBe("assistant");
    expect(messages[1].content.length).toBeGreaterThan(0);
    expect(isSending).toBe(false);
    expect(error).toBeNull();
  });

  it("ignores empty prompts", async () => {
    await useChatStore.getState().send("   ");
    expect(useChatStore.getState().messages).toHaveLength(0);
  });
});
