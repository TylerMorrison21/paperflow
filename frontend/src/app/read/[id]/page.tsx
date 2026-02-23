'use client'
import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { getPaper, getPaperStatus } from '@/lib/api'
import { PaperData } from '@/lib/types'
import ReaderLayout from '@/components/Reader/ReaderLayout'
import ProcessingStatus from '@/components/ProcessingStatus'
import Link from 'next/link'
import { analytics } from '@/lib/analytics'

export default function ReadPage() {
  const { id } = useParams<{ id: string }>()
  const [paper, setPaper] = useState<PaperData | null>(null)
  const [status, setStatus] = useState<'loading' | 'processing' | 'complete' | 'error'>('loading')
  const [error, setError] = useState('')

  const loadPaper = async (paperId: string) => {
    const data = await getPaper(paperId)
    setPaper(data)
    setStatus('complete')
    analytics.readerView(paperId)
  }

  useEffect(() => {
    getPaperStatus(id).then(s => {
      if (s.status === 'complete') loadPaper(id)
      else if (s.status === 'error') { setError(s.error ?? 'Processing failed'); setStatus('error') }
      else setStatus('processing')
    }).catch(e => { setError(String(e)); setStatus('error') })
  }, [id])

  if (status === 'loading') return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'system-ui' }}>
      Loading…
    </div>
  )

  if (status === 'processing') return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <ProcessingStatus
        paperId={id}
        onComplete={loadPaper}
        onError={msg => { setError(msg); setStatus('error') }}
      />
    </div>
  )

  if (status === 'error') return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontFamily: 'system-ui', gap: '1rem' }}>
      <p style={{ color: 'var(--accent)', fontWeight: 600 }}>Something went wrong</p>
      <p style={{ color: 'var(--muted)', fontSize: '0.875rem', maxWidth: 400, textAlign: 'center' }}>{error}</p>
      <Link href="/" style={{ padding: '0.5rem 1.25rem', background: 'var(--accent)', color: '#fff', borderRadius: 6, textDecoration: 'none', fontSize: '0.875rem' }}>
        Try another PDF
      </Link>
    </div>
  )

  if (!paper) return null
  return <ReaderLayout paper={paper} paperId={id} />
}
