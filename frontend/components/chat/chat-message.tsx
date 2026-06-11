"use client"

import { cn } from "@/lib/utils"
import { Bot, User } from "lucide-react"
import type { ChatMessage as ChatMessageType } from "@/types/chat"
import { useEffect, useState } from "react"

interface ChatMessageProps {
  message: ChatMessageType
}

function MarkdownContent({ content }: { content: string }) {
  return (
    <div className="space-y-2 text-sm leading-relaxed">
      {content.split("\n").map((line, lineIdx) => {
        const parts = line.split(/(\*\*[^*]+\*\*)/g)
        return (
          <p key={lineIdx}>
            {parts.map((part, i) => {
              if (part.startsWith("**") && part.endsWith("**")) {
                return (
                  <strong key={i} className="font-semibold text-foreground/90">
                    {part.slice(2, -2)}
                  </strong>
                )
              }
              return <span key={i}>{part}</span>
            })}
          </p>
        )
      })}
    </div>
  )
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user"

  return (
    <div
      className={cn(
        "flex animate-fade-in gap-3",
        isUser ? "justify-end" : "justify-start",
      )}
    >
      {!isUser && (
        <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-accent/20">
          <Bot className="h-4 w-4 text-accent" />
        </div>
      )}

      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-4 py-2.5",
          isUser
            ? "bg-accent text-white rounded-br-sm"
            : "glass rounded-bl-sm text-foreground/80",
        )}
      >
        <MarkdownContent content={message.content} />
      </div>

      {isUser && (
        <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-surface-hover">
          <User className="h-4 w-4 text-foreground/60" />
        </div>
      )}
    </div>
  )
}
