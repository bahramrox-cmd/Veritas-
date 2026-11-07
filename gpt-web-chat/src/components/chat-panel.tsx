"use client";

import { FormEvent, useState } from "react";
import { useChat } from "@chat-adapter/web/react";

function messageText(message: {
  parts: Array<{ type: string; text?: string }>;
}) {
  return message.parts
    .map((part) => (part.type === "text" ? (part.text ?? "") : ""))
    .join("");
}

export function ChatPanel() {
  const { messages, sendMessage, status, error, stop } = useChat({
    api: "/api/chat",
    threadId: "main",
  });
  const [input, setInput] = useState("");
  const busy = status === "submitted" || status === "streaming";

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = input.trim();
    if (!text || busy) {
      return;
    }
    setInput("");
    await sendMessage({ text });
  }

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        gridTemplateRows: "auto 1fr auto",
        maxWidth: 760,
        margin: "0 auto",
        padding: "24px 16px 16px",
      }}
    >
      <header>
        <h1 style={{ margin: 0, fontSize: 22 }}>GPT Web Chat</h1>
        <p style={{ margin: "8px 0 0", color: "var(--muted)" }}>
          Chat SDK Web adapter streaming through AI Gateway.
        </p>
      </header>

      <section
        aria-label="Chat"
        style={{
          overflowY: "auto",
          padding: "20px 0",
          display: "flex",
          flexDirection: "column",
          gap: 12,
        }}
      >
        {messages.length === 0 ? (
          <p style={{ color: "var(--muted)" }}>
            Send a message to start a conversation.
          </p>
        ) : (
          messages.map((message) => (
            <article
              key={message.id}
              style={{
                alignSelf: message.role === "user" ? "flex-end" : "flex-start",
                background: message.role === "user" ? "var(--user)" : "var(--assistant)",
                border: "1px solid var(--border)",
                borderRadius: 16,
                padding: "12px 14px",
                maxWidth: "85%",
                whiteSpace: "pre-wrap",
              }}
            >
              <strong style={{ display: "block", fontSize: 12, color: "var(--muted)" }}>
                {message.role === "user" ? "You" : "Assistant"}
              </strong>
              {messageText(message) || (busy && message.role === "assistant" ? "…" : "")}
            </article>
          ))
        )}
        {error ? (
          <p role="alert" style={{ color: "#f87171" }}>
            {error.message || "Could not send your message. Check AI Gateway credentials and try again."}
          </p>
        ) : null}
      </section>

      <form onSubmit={onSubmit} style={{ display: "grid", gap: 8 }}>
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              event.currentTarget.form?.requestSubmit();
            }
          }}
          placeholder="Message…"
          rows={3}
          style={{
            width: "100%",
            resize: "vertical",
            background: "var(--panel)",
            color: "var(--text)",
            border: "1px solid var(--border)",
            borderRadius: 12,
            padding: 12,
          }}
        />
        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
          {busy ? (
            <button
              type="button"
              onClick={() => stop()}
              style={{
                background: "transparent",
                color: "var(--text)",
                border: "1px solid var(--border)",
                borderRadius: 999,
                padding: "8px 16px",
              }}
            >
              Stop
            </button>
          ) : null}
          <button
            type="submit"
            disabled={busy || !input.trim()}
            style={{
              background: "var(--accent)",
              color: "#04110c",
              border: 0,
              borderRadius: 999,
              padding: "8px 16px",
              fontWeight: 600,
            }}
          >
            Send
          </button>
        </div>
      </form>
    </main>
  );
}
