const XLSX_MIME =
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

export async function saveExcelBlob(blob, suggestedName) {
  if (window.showSaveFilePicker) {
    try {
      const handle = await window.showSaveFilePicker({
        suggestedName,
        types: [
          {
            description: 'Excel 文件',
            accept: {
              [XLSX_MIME]: ['.xlsx']
            }
          }
        ]
      })
      const writable = await handle.createWritable()
      await writable.write(blob)
      await writable.close()
      return { saved: true, canceled: false, mode: 'picker' }
    } catch (error) {
      if (error?.name === 'AbortError') {
        return { saved: false, canceled: true, mode: 'picker' }
      }
      throw error
    }
  }

  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = suggestedName
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
  return { saved: true, canceled: false, mode: 'download' }
}
