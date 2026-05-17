"use client"

import { useEffect, useState } from "react"
import { api } from "@/lib/api-client"
import type { Insight } from "@/types/insight"

export function useInsights(datasetId: string) {
  const [insights, setInsights] = useState<Insight[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!datasetId) return
    api
      .getInsights(datasetId)
      .then((res) => setInsights(res.insights))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [datasetId])

  return { insights, loading, error }
}
