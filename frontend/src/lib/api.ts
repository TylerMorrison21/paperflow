import { PaperData, PaperStatus } from './types'

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export async function uploadPDF(file: File): Promise<{ paper_id: string; status: string }> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/api/parse`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getPaperStatus(id: string): Promise<PaperStatus> {
  const res = await fetch(`${BASE}/api/parse/${id}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getPaper(id: string): Promise<PaperData> {
  const res = await fetch(`${BASE}/api/paper/${id}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
