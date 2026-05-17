"use client"

import { useEffect, useRef } from "react"
import { ChatMessage } from "./chat-message"
import { ChatInput } from "./chat-input"
import { LoadingDots } from "@/components/shared/loading-spinner"
import { MessageSquare } from "lucide-react"
import type { ChatMessage as ChatMessageType } from "@/types/chat"

interface ChatWindowProps {
  messages: ChatMessageType[]
  streaming: boolean
  error: string | null
  onSend: (message: string) => void
}

export function ChatWindow({
  messages,
  streaming,
  error,
  onSend,
}: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, streaming])

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <div className="mb-4 rounded-2xl bg-accent/10 p-4">
              <MessageSquare className="h-8 w-8 text-accent" />
            </div>
            <h3 className="text-lg font-medium text-foreground/70">
              Ask about your data
            </h3>
            <p className="mt-1 max-w-md text-sm text-foreground/40">
              Ask questions about revenue, products, trends, or any other
              business metrics in your dataset.
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} />
        ))}

        {streaming && (
          <div className="flex justify-start">
            <div className="glass rounded-2xl rounded-bl-sm px-4 py-3">
              <LoadingDots />
            </div>
          </div>
        )}

        {error && (
          <div className="rounded-lg bg-red-500/10 px-4 py-2 text-sm text-red-400">
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="border-t border-surface-border p-4">
        <ChatInput onSend={onSend} disabled={streaming} />
      </div>
    </div>
  )
}
