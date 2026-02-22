'use client'
import { useState, useCallback } from 'react'
import { uploadPDF } from '@/lib/api'
import ProcessingStatus from './ProcessingStatus'

export default function UploadZone({ onComplete }: { onComplete: (id: string) => void }) {
  const [state, setState] = useState<'idle' | 'uploading' | 'processing'>('idle')
  const [paperId, setPaperId] = useState<string | null>(null)
  const [dragOver, setDragOver] = useState(false)

  const handleFile = useCallback(async (file: File) => {
    if (!file.name.endsWith('.pdf')) return
    setState('uploading')
    try {
      const { paper_id } = await uploadPDF(file)
      setPaperId(paper_id)
      setState('processing')
    } catch {
      setState('idle')
    }
  }, [])

  if (state === 'processing' && paperId) {
    return <ProcessingStatus paperId={paperId} onComplete={onComplete} />
  }

  return (
    <div
      onDragOver={e => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={e => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f) }}
      onClick={() => document.getElementById('pdf-input')?.click()}
      style={{
        border: `2px dashed ${dragOver ? 'var(--accent)' : '#ccc'}`,
        borderRadius: 12,
        padding: '3rem 2rem',
        textAlign: 'center',
        cursor: 'pointer',
        background: dragOver ? '#fff5f5' : 'transparent',
        transition: 'all 0.2s',
        maxWidth: 480,
        width: '100%',
      }}
    >
      <input id="pdf-input" type="file" accept=".pdf" style={{ display: 'none' }}
        onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f) }} />
      <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📄</div>
      <p style={{ fontFamily: 'system-ui', fontWeight: 600, marginBottom: '0.5rem' }}>
        {state === 'uploading' ? 'Uploading…' : 'Drop a PDF here, or click to browse'}
      </p>
      <p style={{ fontFamily: 'system-ui', fontSize: '0.875rem', color: 'var(--muted)' }}>PDF files only</p>
    </div>
  )
}
