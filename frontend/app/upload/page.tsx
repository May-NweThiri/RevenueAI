"use client"

import { useCallback, useState } from "react"
import { useRouter } from "next/navigation"
import { FileDropzone } from "@/components/upload/file-dropzone"
import { GlassCard } from "@/components/shared/glass-card"
import { LoadingSpinner } from "@/components/shared/loading-spinner"
import { api, pollForDataset } from "@/lib/api-client"
import { CheckCircle, AlertCircle, ArrowRight } from "lucide-react"
import Link from "next/link"

type UploadState =
  | { status: "idle" }
  | { status: "uploading" }
  | { status: "processing"; uploadId: string; datasetId: string }
  | { status: "done"; datasetId: string }
  | { status: "error"; message: string }

export default function UploadPage() {
  const router = useRouter()
  const [state, setState] = useState<UploadState>({ status: "idle" })

  const handleFile = useCallback(async (file: File) => {
    setState({ status: "uploading" })
    try {
      const upload = await api.uploadFile(file)

      setState({
        status: "processing",
        uploadId: upload.id,
        datasetId: "",
      })

      const datasetId = await pollForDataset(upload.id)
      setState({ status: "done", datasetId })
    } catch (e: unknown) {
      let msg = e instanceof Error ? e.message : "Upload failed"
      if (e instanceof TypeError && e.message === "Failed to fetch") {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "not set"
        msg = `Cannot reach API at ${apiUrl}. Check that the backend is running and CORS is configured.`
      }
      console.error("Upload error:", e)
      setState({ status: "error", message: msg })
    }
  }, [])

  return (
    <div className="mx-auto max-w-2xl space-y-6 py-8">
      <div>
        <h2 className="text-xl font-semibold tracking-tight">
          Upload your data
        </h2>
        <p className="mt-1 text-sm text-foreground/40">
          Upload a CSV or Excel file to analyze revenue, trends, and more.
        </p>
      </div>

      <FileDropzone
        onFile={handleFile}
        disabled={state.status === "uploading" || state.status === "processing"}
      />

      {state.status === "uploading" && (
        <GlassCard>
          <div className="flex items-center gap-3">
            <LoadingSpinner />
            <div>
              <p className="text-sm font-medium">Uploading file...</p>
              <p className="text-xs text-foreground/40">
                Sending to server
              </p>
            </div>
          </div>
        </GlassCard>
      )}

      {state.status === "processing" && (
        <GlassCard>
          <div className="flex items-center gap-3">
            <LoadingSpinner />
            <div>
              <p className="text-sm font-medium">Processing dataset...</p>
              <p className="text-xs text-foreground/40">
                Detecting columns, calculating metrics, generating insights
              </p>
            </div>
          </div>
        </GlassCard>
      )}

      {state.status === "done" && (
        <GlassCard className="border-revenue-up/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-6 w-6 text-revenue-up" />
              <div>
                <p className="text-sm font-medium text-revenue-up">
                  Ready to explore!
                </p>
                <p className="text-xs text-foreground/40">
                  Your data has been processed and insights are ready.
                </p>
              </div>
            </div>
            <Link
              href={`/dashboard/${state.datasetId}`}
              className="flex items-center gap-1.5 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
            >
              View Dashboard
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </GlassCard>
      )}

      {state.status === "error" && (
        <GlassCard className="border-red-500/30">
          <div className="flex items-center gap-3">
            <AlertCircle className="h-6 w-6 shrink-0 text-red-400" />
            <div>
              <p className="text-sm font-medium text-red-400">Error</p>
              <p className="text-xs text-foreground/40">{state.message}</p>
            </div>
          </div>
        </GlassCard>
      )}
    </div>
  )
}
