"use client"

import { useCallback, useRef, useState } from "react"
import { api } from "@/lib/api-client"
import type { WSIncoming } from "@/types/chat"

export function useChat(datasetId: string) {
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([])
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  const sendMessage = useCallback(
    (question: string) => {
      setError(null)
      setMessages((prev) => [...prev, { role: "user", content: question }])
      setStreaming(true)

      const ws = new WebSocket(api.wsChat(datasetId))
      wsRef.current = ws

      let assistantContent = ""

      ws.onopen = () => {
        ws.send(JSON.stringify({ type: "message", content: question }))
      }

      ws.onmessage = (event) => {
        try {
          const data: WSIncoming = JSON.parse(event.data)
          if (data.type === "token" && data.content) {
            assistantContent += data.content
            setMessages((prev) => {
              const next = [...prev]
              if (next[next.length - 1]?.role === "assistant") {
                next[next.length - 1] = {
                  role: "assistant",
                  content: assistantContent,
                }
              } else {
                next.push({ role: "assistant", content: assistantContent })
              }
              return [...next]
            })
          } else if (data.type === "end") {
            setStreaming(false)
            ws.close()
          } else if (data.type === "error" && data.content) {
            setError(data.content)
            setStreaming(false)
            ws.close()
          }
        } catch {
          // ignore malformed messages
        }
      }

      ws.onerror = () => {
        setError("WebSocket connection failed")
        setStreaming(false)
      }

      ws.onclose = () => {
        setStreaming(false)
        wsRef.current = null
      }
    },
    [datasetId],
  )

  return { messages, streaming, error, sendMessage }
}
