import { streamText } from "ai";
import type { Message, Thread } from "chat";
import { toAiMessages } from "chat/ai";

const DEFAULT_MODEL = "openai/gpt-4.1-mini";

export async function respond(thread: Thread, message: Message) {
  if (message.author.isMe === true) {
    return;
  }

  const model = process.env.AI_GATEWAY_MODEL ?? DEFAULT_MODEL;
  const hasGatewayAuth = Boolean(
    process.env.AI_GATEWAY_API_KEY || process.env.VERCEL_OIDC_TOKEN,
  );

  if (!hasGatewayAuth) {
    await thread.post(
      "AI Gateway is not authenticated. Add AI_GATEWAY_API_KEY to gpt-web-chat/.env.local, restart the dev server, and send another message.",
    );
    return;
  }

  const history: Message[] = [];

  for await (const item of thread.messages) {
    history.push(item);
    if (history.length === 20) {
      break;
    }
  }

  if (history.length === 0) {
    history.push(message);
  }

  try {
    const result = streamText({
      model,
      system:
        "You are a helpful GPT-style assistant in a browser chat. Be clear, concise, and candid. If you are unsure, say so.",
      messages: await toAiMessages(history),
      abortSignal: thread.signal,
    });

    await thread.post(result.textStream);
  } catch (error) {
    const detail =
      error instanceof Error && /unauthenticated|api key|oidc/i.test(error.message)
        ? "AI Gateway is not authenticated. Set AI_GATEWAY_API_KEY in .env.local, or link this app to Vercel so OIDC can authenticate."
        : "The model request failed. Check the server log and try again.";
    await thread.post(detail);
  }
}
