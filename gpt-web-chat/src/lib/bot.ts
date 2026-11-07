import { createWebAdapter } from "@chat-adapter/web";
import { createMemoryState } from "@chat-adapter/state-memory";
import { Chat } from "chat";
import { getUser } from "./auth-stub";
import { respond } from "./respond";

export const bot = new Chat({
  userName: process.env.BOT_USERNAME ?? "gpt-web-chat",
  adapters: {
    web: createWebAdapter({
      userName: process.env.BOT_USERNAME ?? "gpt-web-chat",
      protocol: "ai-sdk",
      getUser,
    }),
  },
  state: createMemoryState(),
});

bot.onNewMention(async (thread, message) => {
  await thread.subscribe();
  await respond(thread, message);
});

bot.onSubscribedMessage(async (thread, message) => {
  await respond(thread, message);
});

bot.onDirectMessage(async (thread, message) => {
  await respond(thread, message);
});
