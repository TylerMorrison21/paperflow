'use client'
import { useEffect, useState } from 'react'
import { getPaperStatus } from '@/lib/api'
import { analytics } from '@/lib/analytics'

export default function ProcessingStatus({ paperId, onComplete, onError }: {
  paperId: string
  onComplete: (id: string) => void
  onError?: (msg: string) => void
}) {
  const [elapsed, setElapsed] = useState(0)
  const [startTime] = useState(Date.now())

  useEffect(() => {
    const timer = setInterval(() => setElapsed(s => s + 1), 1000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const { status, error, error_code } = await getPaperStatus(paperId)
        if (status === 'complete') {
          clearInterval(interval)
          const durationSec = Math.round((Date.now() - startTime) / 1000)
          analytics.parseSuccess(paperId, durationSec)
          onComplete(paperId)
        }
        if (status === 'error') {
          clearInterval(interval)
          analytics.parseFailed(error_code || 'PARSE_FAILED', error || 'Processing failed')
          onError?.(error ?? 'Processing failed')
        }
      } catch { /* keep polling */ }
    }, 3000)
    return () => clearInterval(interval)
  }, [paperId, onComplete, onError, startTime])

  const mins = Math.floor(elapsed / 60)
  const secs = elapsed % 60
  const timeStr = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`

  return (
    <div style={{ textAlign: 'center', fontFamily: 'system-ui', padding: '2rem' }}>
      <div style={{ width: 48, height: 48, border: '4px solid #eee', borderTopColor: 'var(--accent)', borderRadius: '50%', animation: 'spin 0.8s linear infinite', margin: '0 auto 1.5rem' }} />
      <p style={{ fontWeight: 600, marginBottom: '0.5rem' }}>Converting your paper…</p>
      <p style={{ color: 'var(--muted)', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Usually takes 30–120 seconds</p>
      <p style={{ color: 'var(--muted)', fontSize: '0.8rem' }}>{timeStr} elapsed</p>
      <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
    </div>
  )
}
