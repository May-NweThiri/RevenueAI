import Link from "next/link"
import { BarChart3, MessageSquare, Upload, TrendingUp } from "lucide-react"

const features = [
  {
    icon: Upload,
    title: "Upload Any Dataset",
    desc: "Drop CSV or Excel files. RevenueAI auto-detects columns and structure.",
  },
  {
    icon: TrendingUp,
    title: "Instant Metrics",
    desc: "Total revenue, growth rates, top products, and category breakdowns calculated automatically.",
  },
  {
    icon: MessageSquare,
    title: "AI-Powered Chat",
    desc: "Ask questions in plain English. Get answers with real data from your dataset.",
  },
  {
    icon: BarChart3,
    title: "Smart Insights",
    desc: "AI identifies trends, anomalies, and opportunities in your data.",
  },
]

export default function LandingPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-16 py-12">
      {/* Hero */}
      <div className="space-y-6 text-center">
        <div className="inline-flex items-center gap-2 rounded-full bg-accent/10 px-4 py-1.5 text-xs font-medium text-accent">
          <span className="h-1.5 w-1.5 rounded-full bg-accent" />
          AI-Powered Revenue Analytics
        </div>
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          Understand your{" "}
          <span className="text-gradient">revenue data</span>
          <br />
          with the power of AI
        </h1>
        <p className="mx-auto max-w-xl text-base text-foreground/50">
          Upload your sales data, get instant insights, and ask natural language
          questions. RevenueAI combines pandas analytics with AI to make data
          exploration effortless.
        </p>
        <div className="flex items-center justify-center gap-3">
          <Link
            href="/upload"
            className="rounded-xl bg-accent px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
          >
            Get Started
          </Link>
          <Link
            href="/dashboard"
            className="rounded-xl border border-surface-border px-6 py-3 text-sm font-medium text-foreground/70 transition-colors hover:bg-surface-hover"
          >
            View Dashboard
          </Link>
        </div>
      </div>

      {/* Features */}
      <div className="grid gap-4 sm:grid-cols-2">
        {features.map((f) => (
          <div
            key={f.title}
            className="glass rounded-xl p-6 transition-colors hover:bg-glass-hover"
          >
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10 text-accent">
              <f.icon className="h-5 w-5" />
            </div>
            <h3 className="font-medium text-foreground/90">{f.title}</h3>
            <p className="mt-1 text-sm text-foreground/40">{f.desc}</p>
          </div>
        ))}
      </div>

      {/* How it works */}
      <div className="space-y-8 text-center">
        <h2 className="text-2xl font-semibold tracking-tight">
          How it works
        </h2>
        <div className="grid gap-6 sm:grid-cols-3">
          {[
            { step: "1", title: "Upload", desc: "Drop your CSV or Excel file" },
            {
              step: "2",
              title: "Analyze",
              desc: "AI detects columns and calculates metrics",
            },
            {
              step: "3",
              title: "Explore",
              desc: "Ask questions and get instant answers",
            },
          ].map((s) => (
            <div key={s.step} className="space-y-2">
              <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-accent/10 text-sm font-bold text-accent">
                {s.step}
              </div>
              <h3 className="font-medium text-foreground/80">{s.title}</h3>
              <p className="text-sm text-foreground/40">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
