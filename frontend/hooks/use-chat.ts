"use client"

import { useCallback, useEffect, useState } from "react"
import { api } from "@/lib/api-client"

export function useChat(datasetId: string) {
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([])
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!datasetId) return
    api
      .getConversation(datasetId)
      .then((conv) => {
        if (conv.messages?.length) {
          setMessages(conv.messages)
        }
      })
      .catch(() => {
        // no prior conversation
      })
  }, [datasetId])

  const sendMessage = useCallback(
    async (question: string) => {
      setError(null)
      setMessages((prev) => [...prev, { role: "user", content: question }])
      setStreaming(true)

      try {
        const res = await api.sendMessage(datasetId, question)
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: res.reply },
        ])
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to send message")
      } finally {
        setStreaming(false)
      }
    },
    [datasetId],
  )

  return { messages, streaming, error, sendMessage }
}
