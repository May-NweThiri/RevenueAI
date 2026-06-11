const REPORT_BG = "#0f0f13"

function sanitizeFilename(name: string): string {
  return name.replace(/\.[^/.]+$/, "").replace(/[^a-z0-9-_]+/gi, "_")
}

export async function downloadReportPdf(
  element: HTMLElement,
  datasetName: string,
): Promise<void> {
  const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
    import("html2canvas"),
    import("jspdf"),
  ])

  const canvas = await html2canvas(element, {
    backgroundColor: REPORT_BG,
    scale: 2,
    useCORS: true,
    logging: false,
    windowWidth: element.scrollWidth,
  })

  const pdf = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" })
  const pageWidth = pdf.internal.pageSize.getWidth()
  const pageHeight = pdf.internal.pageSize.getHeight()

  const imgWidth = pageWidth
  const imgHeight = (canvas.height * imgWidth) / canvas.width

  let heightLeft = imgHeight
  let position = 0
  const imgData = canvas.toDataURL("image/png")

  pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight)
  heightLeft -= pageHeight

  while (heightLeft > 0) {
    position -= pageHeight
    pdf.addPage()
    pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight
  }

  pdf.save(`${sanitizeFilename(datasetName) || "revenueai-report"}.pdf`)
}
