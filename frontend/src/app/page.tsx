'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import UploadZone from '@/components/UploadZone'
import { analytics } from '@/lib/analytics'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    analytics.visitHome()
  }, [])

  return (
    <main style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '2rem', gap: '2rem' }}>
      <div style={{ textAlign: 'center', maxWidth: 600 }}>
        <h1 style={{ fontSize: 'clamp(2rem, 5vw, 3rem)', fontWeight: 700, lineHeight: 1.2, marginBottom: '1rem' }}>
          Read papers, not PDFs
        </h1>
        <p style={{ fontFamily: 'system-ui', fontSize: '1.1rem', color: 'var(--muted)', marginBottom: '2rem' }}>
          Transform academic PDFs into beautiful, readable articles
        </p>
      </div>

      <UploadZone onComplete={id => router.push(`/read/${id}`)} />

      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center', fontFamily: 'system-ui', fontSize: '0.875rem' }}>
        {['LaTeX equations', 'Mobile optimized', 'Inline figures & tables'].map(chip => (
          <span key={chip} style={{ padding: '0.4rem 0.9rem', border: '1px solid var(--border)', borderRadius: 999, color: 'var(--muted)' }}>
            {chip}
          </span>
        ))}
      </div>
    </main>
  )
}
