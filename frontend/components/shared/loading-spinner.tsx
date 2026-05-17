import { cn } from "@/lib/utils"

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg"
  className?: string
}

export function LoadingSpinner({ size = "md", className }: LoadingSpinnerProps) {
  const sizeMap = { sm: "h-4 w-4", md: "h-6 w-6", lg: "h-10 w-10" }
  return (
    <div className={cn("flex items-center justify-center", className)}>
      <div
        className={cn(
          "rounded-full border-2 border-surface-border border-t-accent",
          sizeMap[size],
        )}
        style={{ animation: "spin-slow 0.8s linear infinite" }}
      />
    </div>
  )
}

export function LoadingDots() {
  return (
    <div className="flex items-center gap-1 px-2">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="h-1.5 w-1.5 rounded-full bg-accent/60 animate-pulse-dot"
          style={{ animationDelay: `${i * 0.2}s` }}
        />
      ))}
    </div>
  )
}

export function LoadingPage() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <LoadingSpinner size="lg" />
    </div>
  )
}

export function EmptyState({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="mb-4 text-foreground/30">{icon}</div>
      <h3 className="text-lg font-medium text-foreground/70">{title}</h3>
      <p className="mt-1 text-sm text-foreground/40">{description}</p>
    </div>
  )
}
