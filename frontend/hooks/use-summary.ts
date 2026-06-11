"use client"

import { useEffect, useState } from "react"
import { api } from "@/lib/api-client"
import type { DatasetSummary } from "@/types/summary"

export function useSummary(datasetId: string) {
  const [summary, setSummary] = useState<DatasetSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!datasetId) return
    api
      .getSummary(datasetId)
      .then(setSummary)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [datasetId])

  return { summary, loading, error }
}
