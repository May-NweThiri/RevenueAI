"use client"

import { useCallback, useRef, useState } from "react"
import { Send, Loader2 } from "lucide-react"

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("")
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = useCallback(() => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue("")
    if (inputRef.current) {
      inputRef.current.style.height = "auto"
    }
  }, [value, disabled, onSend])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        handleSend()
      }
    },
    [handleSend],
  )

  return (
    <div className="flex items-end gap-2">
      <textarea
        ref={inputRef}
        value={value}
        onChange={(e) => {
          setValue(e.target.value)
          e.target.style.height = "auto"
          e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`
        }}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about your data..."
        rows={1}
        disabled={disabled}
        className="min-h-[44px] flex-1 resize-none rounded-xl border border-surface-border bg-surface-card px-4 py-2.5 text-sm text-foreground placeholder-foreground/30 outline-none transition-colors focus:border-accent/50 disabled:opacity-50"
      />
      <button
        onClick={handleSend}
        disabled={disabled || !value.trim()}
        className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-accent text-white transition-colors hover:bg-accent-hover disabled:opacity-40"
      >
        {disabled ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Send className="h-4 w-4" />
        )}
      </button>
    </div>
  )
}
