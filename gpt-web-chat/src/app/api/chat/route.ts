import { after } from "next/server";
import { bot } from "@/lib/bot";

export async function POST(request: Request) {
  return bot.webhooks.web(request, {
    waitUntil: (task) => after(() => task),
  });
}
