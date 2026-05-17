"use client"

import { useParams } from "next/navigation"
import Link from "next/link"
import { useDataset } from "@/hooks/use-dataset"
import { useChat } from "@/hooks/use-chat"
import { ChatWindow } from "@/components/chat/chat-window"
import { LoadingPage } from "@/components/shared/loading-spinner"
import { GlassCard } from "@/components/shared/glass-card"
import { ArrowLeft, Database } from "lucide-react"

export default function ChatPage() {
  const params = useParams()
  const id = params.id as string
  const { dataset, loading } = useDataset(id)
  const { messages, streaming, error, sendMessage } = useChat(id)

  if (loading) return <LoadingPage />

  if (!dataset) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-sm text-red-400">Dataset not found</p>
      </div>
    )
  }

  return (
    <div className="flex h-[calc(100vh-7rem)] flex-col gap-4 py-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Link
          href={`/dashboard/${id}`}
          className="flex items-center gap-1 text-sm text-foreground/40 transition-colors hover:text-foreground/70"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Link>
        <div className="flex items-center gap-2 rounded-lg bg-surface-card px-3 py-1.5">
          <Database className="h-3.5 w-3.5 text-accent" />
          <span className="text-xs text-foreground/60">{dataset.name}</span>
        </div>
      </div>

      {/* Chat */}
      <GlassCard className="flex flex-1 flex-col overflow-hidden p-0">
        <ChatWindow
          messages={messages}
          streaming={streaming}
          error={error}
          onSend={sendMessage}
        />
      </GlassCard>
    </div>
  )
}
