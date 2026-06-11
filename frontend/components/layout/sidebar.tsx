"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { BrandName } from "@/components/shared/brand-name"
import {
  BarChart3,
  CloudUpload,
  Home,
  MessageSquare,
  LayoutDashboard,
} from "lucide-react"

const navItems = [
  { href: "/", label: "Home", icon: Home },
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/upload", label: "Upload", icon: CloudUpload },
]

export function Sidebar() {
  const pathname = usePathname()

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/"
    return pathname.startsWith(href)
  }

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-60 border-r border-surface-border bg-surface/95 backdrop-blur-xl">
      <div className="flex h-full flex-col">
        <div className="flex items-center gap-2.5 border-b border-surface-border px-5 py-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent">
            <BarChart3 className="h-4 w-4 text-white" />
          </div>
          <BrandName className="text-lg" />
        </div>

        <nav className="flex-1 space-y-1 p-3">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive(item.href)
                  ? "bg-accent/10 text-accent"
                  : "text-foreground/50 hover:bg-surface-hover hover:text-foreground/80",
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="border-t border-surface-border p-4">
          <div className="flex items-center gap-3 rounded-lg bg-accent/5 px-3 py-2.5">
            <MessageSquare className="h-4 w-4 text-accent" />
            <div className="text-xs">
              <p className="font-medium text-accent">AI Ready</p>
              <p className="text-foreground/40">Ask questions</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}
