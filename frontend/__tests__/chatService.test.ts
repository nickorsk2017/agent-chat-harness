import { sendChatMessage } from "@/services/chatService";

describe("chatService (mock)", () => {
  it("returns a mock reply that references the prompt", async () => {
    const prompt = "What's the weather in Berlin?";
    const res = await sendChatMessage({ prompt });

    expect(res.reply).toEqual(expect.any(String));
    expect(res.reply).toContain(prompt);
    expect(res.reply.toLowerCase()).toContain("mock");
  });

  it("rejects when the signal is already aborted", async () => {
    const controller = new AbortController();
    controller.abort();

    await expect(
      sendChatMessage({ prompt: "hi" }, controller.signal),
    ).rejects.toThrow();
  });
});
