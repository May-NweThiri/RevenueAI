import type {
  Dataset,
  DatasetListResponse,
  UploadResponse,
  PreviewResponse,
} from "@/types/dataset"
import type { MetricsGroupedResponse } from "@/types/metrics"
import type { InsightListResponse } from "@/types/insight"
import type { ChatResponse, ChatRequest } from "@/types/chat"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message)
    this.name = "ApiError"
  }
}

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${BASE_URL}${path}`
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  })
  if (!res.ok) {
    const body = await res.text()
    throw new ApiError(res.status, body || res.statusText)
  }
  return res.json()
}

export const api = {
  uploadFile: async (file: File): Promise<UploadResponse> => {
    const form = new FormData()
    form.append("file", file)
    const res = await fetch(`${BASE_URL}/api/v1/upload`, {
      method: "POST",
      body: form,
    })
    if (!res.ok) {
      throw new ApiError(res.status, await res.text())
    }
    return res.json()
  },

  getUpload: (id: string): Promise<UploadResponse> =>
    request(`/api/v1/uploads/${id}`),

  getDatasets: (): Promise<DatasetListResponse> =>
    request("/api/v1/datasets"),

  getDataset: (id: string): Promise<Dataset> =>
    request(`/api/v1/datasets/${id}`),

  getDatasetPreview: (id: string): Promise<PreviewResponse> =>
    request(`/api/v1/datasets/${id}/preview`),

  getMetrics: (id: string): Promise<MetricsGroupedResponse> =>
    request(`/api/v1/metrics/${id}/grouped`),

  getInsights: (id: string): Promise<InsightListResponse> =>
    request(`/api/v1/insights/${id}`),

  sendMessage: (datasetId: string, msg: string): Promise<ChatResponse> =>
    request(`/api/v1/chat/${datasetId}`, {
      method: "POST",
      body: JSON.stringify({ message: msg } as ChatRequest),
    }),

  wsChat: (datasetId: string): string =>
    `${BASE_URL.replace(/^http/, "ws")}/api/v1/ws/chat/${datasetId}`,
}

export function pollForDataset(
  uploadId: string,
  interval = 2000,
  timeout = 60000,
): Promise<string> {
  const start = Date.now()
  return new Promise((resolve, reject) => {
    const check = async () => {
      try {
        const upload = await api.getUpload(uploadId)
        if (upload.dataset_id) {
          resolve(upload.dataset_id)
          return
        }
        if (upload.status === "failed") {
          reject(new Error(upload.error_msg || "Processing failed"))
          return
        }
      } catch {
        // retry
      }
      if (Date.now() - start > timeout) {
        reject(new Error("Timeout waiting for dataset processing"))
        return
      }
      setTimeout(check, interval)
    }
    check()
  })
}
