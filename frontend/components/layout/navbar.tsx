"use client"

import { usePathname } from "next/navigation"

const titles: Record<string, string> = {
  "/": "Home",
  "/upload": "Upload Data",
  "/dashboard": "Dashboard",
}

export function Navbar() {
  const pathname = usePathname()

  let title = titles[pathname] || "Dashboard"
  if (pathname.startsWith("/dashboard/") && pathname.includes("/chat")) {
    title = "AI Chat"
  } else if (pathname.startsWith("/dashboard/") && pathname !== "/dashboard") {
    title = "Dataset Detail"
  }

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b border-surface-border bg-surface/80 px-6 backdrop-blur-xl">
      <div>
        <h1 className="text-sm font-medium text-foreground/80">{title}</h1>
      </div>
      <div className="ml-auto flex items-center gap-3">
        <div className="flex items-center gap-2 rounded-full bg-accent/10 px-3 py-1 text-xs text-accent">
          <span className="h-1.5 w-1.5 rounded-full bg-accent" />
          Local Server
        </div>
      </div>
    </header>
  )
}
