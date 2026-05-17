export interface ChatMessage {
  role: "user" | "assistant"
  content: string
}

export interface ChatRequest {
  message: string
}

export interface ChatResponse {
  reply: string
  conversation_id: string
  insights: unknown | null
}

export interface ConversationResponse {
  id: string
  dataset_id: string
  messages: ChatMessage[]
  created_at: string
  updated_at: string
}

export interface WSIncoming {
  type: "token" | "end" | "error"
  content?: string
}
