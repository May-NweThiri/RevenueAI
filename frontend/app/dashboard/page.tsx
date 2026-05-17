"use client"

import { useDatasets } from "@/hooks/use-dataset"
import { GlassCard } from "@/components/shared/glass-card"
import { LoadingPage, EmptyState } from "@/components/shared/loading-spinner"
import { formatDate, timeAgo, formatNumber } from "@/lib/utils"
import {
  BarChart3,
  Database,
  MessageSquare,
  ArrowRight,
  Table,
} from "lucide-react"
import Link from "next/link"

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    ready: "bg-revenue-up/10 text-revenue-up",
    processing: "bg-amber-500/10 text-amber-400",
    failed: "bg-red-500/10 text-red-400",
    pending: "bg-foreground/10 text-foreground/40",
  }
  return (
    <span
      className={`rounded-full px-2.5 py-0.5 text-[11px] font-medium uppercase tracking-wider ${colors[status] || "bg-foreground/10 text-foreground/40"}`}
    >
      {status}
    </span>
  )
}

export default function DashboardPage() {
  const { datasets, loading, error } = useDatasets()

  if (loading) return <LoadingPage />

  if (error) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-sm text-red-400">Error: {error}</p>
      </div>
    )
  }

  if (datasets.length === 0) {
    return (
      <EmptyState
        icon={<Database className="h-12 w-12" />}
        title="No datasets yet"
        description="Upload your first CSV or Excel file to get started."
      />
    )
  }

  return (
    <div className="space-y-6 py-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">
            Your Datasets
          </h2>
          <p className="mt-1 text-sm text-foreground/40">
            {datasets.length} dataset{datasets.length !== 1 ? "s" : ""}{" "}
            uploaded
          </p>
        </div>
        <Link
          href="/upload"
          className="flex items-center gap-1.5 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
        >
          <BarChart3 className="h-4 w-4" />
          Upload
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {datasets.map((ds) => (
          <Link key={ds.id} href={`/dashboard/${ds.id}`}>
            <GlassCard hover className="group h-full">
              <div className="flex items-start justify-between">
                <div className="rounded-lg bg-accent/10 p-2.5 text-accent">
                  <Table className="h-5 w-5" />
                </div>
                <StatusBadge status={ds.status} />
              </div>

              <div className="mt-4 space-y-1">
                <p className="font-medium text-foreground/90">{ds.name}</p>
                <p className="text-xs text-foreground/40">
                  {formatNumber(ds.row_count)} rows &middot;{" "}
                  {formatNumber(ds.column_count)} columns
                </p>
              </div>

              <div className="mt-4 flex items-center justify-between border-t border-surface-border pt-3 text-xs text-foreground/40">
                <span>{timeAgo(ds.created_at)}</span>
                <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
              </div>
            </GlassCard>
          </Link>
        ))}
      </div>
    </div>
  )
}
