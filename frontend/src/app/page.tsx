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
    <main style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '3rem 1.5rem', fontFamily: 'system-ui' }}>
      {/* Hero Section */}
      <div style={{ textAlign: 'center', maxWidth: 700, marginBottom: '3rem' }}>
        <h1 style={{ fontSize: 'clamp(2.5rem, 6vw, 3.5rem)', fontWeight: 700, lineHeight: 1.1, marginBottom: '1.5rem' }}>
          Read papers without scroll-back hell.
        </h1>
        <p style={{ fontSize: '1.25rem', color: 'var(--muted)', lineHeight: 1.6, marginBottom: '2.5rem' }}>
          Click any Figure / Table / Reference inline—keep your place, keep context. Turn PDFs into a clean, shareable reading link.
        </p>

        {/* CTAs */}
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap', marginBottom: '2rem' }}>
          <button
            onClick={() => document.getElementById('upload-zone')?.scrollIntoView({ behavior: 'smooth' })}
            style={{
              padding: '0.875rem 2rem',
              fontSize: '1.1rem',
              fontWeight: 600,
              background: 'var(--foreground)',
              color: 'var(--background)',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
            }}
          >
            Upload a PDF
          </button>
          <button
            onClick={() => router.push('/read/fa494148-786a-43bb-b971-d014a81e7773')}
            style={{
              padding: '0.875rem 2rem',
              fontSize: '1.1rem',
              fontWeight: 600,
              background: 'transparent',
              color: 'var(--foreground)',
              border: '2px solid var(--border)',
              borderRadius: '8px',
              cursor: 'pointer',
            }}
          >
            View a demo paper
          </button>
        </div>

        {/* 3 Bullets */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', alignItems: 'center', fontSize: '0.95rem', color: 'var(--muted)' }}>
          <div>✓ Click citations/figures to view inline (no scroll-back hell)</div>
          <div>✓ Highlight text + export to Markdown (zero-friction knowledge capture)</div>
          <div>✓ Export full paper to Markdown (for Obsidian/Notion)</div>
          <div>✓ Shareable link for every paper</div>
        </div>
      </div>

      {/* Upload Zone */}
      <div id="upload-zone" style={{ marginBottom: '4rem', width: '100%', maxWidth: 600 }}>
        <UploadZone onComplete={id => router.push(`/read/${id}`)} />
      </div>

      {/* How It Works */}
      <div style={{ maxWidth: 900, width: '100%', marginBottom: '4rem' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 700, textAlign: 'center', marginBottom: '2.5rem' }}>
          How it works
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>📄</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>Upload a PDF</h3>
            <p style={{ color: 'var(--muted)', fontSize: '0.95rem' }}>Drop your academic paper</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>⚙️</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>We convert it</h3>
            <p style={{ color: 'var(--muted)', fontSize: '0.95rem' }}>Into a structured reading page</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🔗</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>Tap inline links</h3>
            <p style={{ color: 'var(--muted)', fontSize: '0.95rem' }}>Citations/figures and keep reading</p>
          </div>
        </div>
      </div>

      {/* Mini FAQ */}
      <div style={{ maxWidth: 700, width: '100%', marginBottom: '4rem' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 700, textAlign: 'center', marginBottom: '2.5rem' }}>
          FAQ
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Does it support scanned PDFs?
            </h3>
            <p style={{ color: 'var(--muted)', fontSize: '0.95rem', lineHeight: 1.6 }}>
              Some work better than others—if parsing fails, you'll see an error and can retry.
            </p>
          </div>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Do you store my files?
            </h3>
            <p style={{ color: 'var(--muted)', fontSize: '0.95rem', lineHeight: 1.6 }}>
              We store converted papers to enable shareable links. Original PDFs are processed and discarded. You can request deletion anytime at contact@paperflow.app.
            </p>
          </div>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Pricing?
            </h3>
            <p style={{ color: 'var(--muted)', fontSize: '0.95rem', lineHeight: 1.6 }}>
              Free during beta. We're collecting feedback to shape the paid plan.
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--border)', paddingTop: '2rem', width: '100%', textAlign: 'center' }}>
        <div style={{ display: 'flex', gap: '1.5rem', justifyContent: 'center', fontSize: '0.9rem', color: 'var(--muted)' }}>
          <a href="/privacy" style={{ textDecoration: 'none', color: 'inherit' }}>Privacy</a>
          <span>•</span>
          <a href="/terms" style={{ textDecoration: 'none', color: 'inherit' }}>Terms</a>
          <span>•</span>
          <a href="mailto:contact@paperflow.app" style={{ textDecoration: 'none', color: 'inherit' }}>Contact</a>
        </div>
      </footer>
    </main>
  )
}
