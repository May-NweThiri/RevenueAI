import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { Sidebar } from "@/components/layout/sidebar"
import { Navbar } from "@/components/layout/navbar"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "FinX AI — AI-Powered Revenue Analytics",
  description:
    "Upload your sales data, get instant insights, and ask natural language questions with AI.",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <Sidebar />
        <div className="ml-60 min-h-screen">
          <Navbar />
          <main className="px-6">{children}</main>
        </div>
      </body>
    </html>
  )
}
