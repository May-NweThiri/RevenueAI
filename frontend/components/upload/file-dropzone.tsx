"use client"

import { useCallback, useRef, useState } from "react"
import { cn } from "@/lib/utils"
import { CloudUpload, FileSpreadsheet, X } from "lucide-react"

interface FileDropzoneProps {
  onFile: (file: File) => void
  disabled?: boolean
}

export function FileDropzone({ onFile, disabled }: FileDropzoneProps) {
  const [dragOver, setDragOver] = useState(false)
  const [selected, setSelected] = useState<File | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragOver(false)
      const file = e.dataTransfer.files[0]
      if (file) {
        setSelected(file)
        onFile(file)
      }
    },
    [onFile],
  )

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) {
        setSelected(file)
        onFile(file)
      }
    },
    [onFile],
  )

  const clear = useCallback(() => {
    setSelected(null)
    if (inputRef.current) inputRef.current.value = ""
  }, [])

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault()
        if (!disabled) setDragOver(true)
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className={cn(
        "relative cursor-pointer rounded-2xl border-2 border-dashed p-12 text-center transition-all",
        dragOver
          ? "border-accent bg-accent/5"
          : selected
            ? "border-revenue-up/40 bg-revenue-up/5"
            : "border-surface-border hover:border-foreground/20 hover:bg-surface-hover/50",
        disabled && "pointer-events-none opacity-50",
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.xlsx,.xls"
        onChange={handleChange}
        className="hidden"
      />

      {selected ? (
        <div className="flex flex-col items-center gap-3">
          <FileSpreadsheet className="h-10 w-10 text-revenue-up" />
          <div>
            <p className="font-medium text-foreground/80">{selected.name}</p>
            <p className="text-sm text-foreground/40">
              {(selected.size / 1024).toFixed(1)} KB
            </p>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation()
              clear()
            }}
            className="mt-2 flex items-center gap-1.5 rounded-lg bg-surface-hover px-3 py-1.5 text-xs text-foreground/60 hover:text-foreground"
          >
            <X className="h-3 w-3" />
            Remove
          </button>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-3">
          <CloudUpload className="h-10 w-10 text-foreground/30" />
          <div>
            <p className="font-medium text-foreground/70">
              Drop your file here, or click to browse
            </p>
            <p className="mt-1 text-sm text-foreground/40">
              Supports CSV and Excel files (.csv, .xlsx)
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
