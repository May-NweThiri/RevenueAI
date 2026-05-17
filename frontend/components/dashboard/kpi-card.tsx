import { GlassCard } from "@/components/shared/glass-card"
import { cn } from "@/lib/utils"
import { TrendingDown, TrendingUp } from "lucide-react"

interface KPICardProps {
  title: string
  value: string
  subtitle?: string
  trend?: number
  icon: React.ReactNode
  className?: string
}

export function KPICard({
  title,
  value,
  subtitle,
  trend,
  icon,
  className,
}: KPICardProps) {
  const isPositive = trend !== undefined && trend >= 0
  const isNegative = trend !== undefined && trend < 0

  return (
    <GlassCard className={cn("", className)}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-medium uppercase tracking-wider text-foreground/40">
            {title}
          </p>
          <p className="text-2xl font-bold tracking-tight">{value}</p>
          {subtitle && (
            <p className="text-xs text-foreground/40">{subtitle}</p>
          )}
        </div>
        <div className="rounded-lg bg-accent/10 p-2.5 text-accent">
          {icon}
        </div>
      </div>
      {trend !== undefined && (
        <div className="mt-3 flex items-center gap-1.5 border-t border-surface-border pt-3">
          {isPositive ? (
            <TrendingUp className="h-3.5 w-3.5 text-revenue-up" />
          ) : isNegative ? (
            <TrendingDown className="h-3.5 w-3.5 text-revenue-down" />
          ) : null}
          <span
            className={cn(
              "text-xs font-medium",
              isPositive && "text-revenue-up",
              isNegative && "text-revenue-down",
              trend === 0 && "text-foreground/40",
            )}
          >
            {isPositive && "+"}
            {trend?.toFixed(1)}%
          </span>
          <span className="text-xs text-foreground/40">vs previous</span>
        </div>
      )}
    </GlassCard>
  )
}
