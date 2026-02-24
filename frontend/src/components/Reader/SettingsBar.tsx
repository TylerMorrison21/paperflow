'use client'
import { useState } from 'react'
import Link from 'next/link'
import { analytics } from '@/lib/analytics'
import { PaperData } from '@/lib/types'
import { useHighlights } from '@/hooks/useHighlights'

export default function SettingsBar({ title, fontSize, setFontSize, dark, setDark, paperId, paper }: {
  title: string
  fontSize: number
  setFontSize: (n: number) => void
  dark: boolean
  setDark: (v: boolean) => void
  paperId: string
  paper: PaperData
}) {
  const [copied, setCopied] = useState(false)
  const [exported, setExported] = useState(false)
  const [highlightsExported, setHighlightsExported] = useState(false)
  const { highlights, exportHighlights } = useHighlights(paperId)

  const sizes = [16, 18, 20]
  const cycle = (dir: 1 | -1) => {
    const i = sizes.indexOf(fontSize)
    setFontSize(sizes[Math.max(0, Math.min(sizes.length - 1, i + dir))])
  }

  const handleCopyLink = async () => {
    const url = `${window.location.origin}/read/${paperId}`
    await navigator.clipboard.writeText(url)
    setCopied(true)
    analytics.shareCopyLink(paperId)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleExportMarkdown = () => {
    // Build clean markdown with title and sections
    let markdown = `# ${paper.title}\n\n`

    paper.sections.forEach(section => {
      markdown += section.markdown + '\n\n'
    })

    // Create blob and download
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    setExported(true)
    analytics.exportMarkdown(paperId)
    setTimeout(() => setExported(false), 2000)
  }

  const handleExportHighlights = () => {
    const markdown = exportHighlights(paper.title)
    if (!markdown) {
      alert('No highlights to export')
      return
    }

    // Create blob and download
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_highlights.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    setHighlightsExported(true)
    analytics.exportHighlights?.(paperId, highlights.length)
    setTimeout(() => setHighlightsExported(false), 2000)
  }

  const bar: React.CSSProperties = {
    position: 'sticky', top: 0, zIndex: 10,
    display: 'flex', alignItems: 'center', gap: '1rem',
    padding: '0.6rem 1.5rem',
    background: dark ? '#111' : 'var(--bg)',
    borderBottom: '1px solid var(--border)',
    fontFamily: 'system-ui', fontSize: '0.875rem',
  }
  const btn: React.CSSProperties = { background: 'none', border: 'none', cursor: 'pointer', padding: '0.25rem 0.5rem', borderRadius: 4, fontSize: '0.875rem', color: 'var(--text)' }

  return (
    <div style={bar}>
      <Link href="/" style={{ textDecoration: 'none', color: 'var(--muted)', fontSize: '1.1rem' }}>←</Link>
      <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--text)' }}>{title}</span>
      {highlights.length > 0 && (
        <button style={btn} onClick={handleExportHighlights}>
          {highlightsExported ? '✓ Exported!' : `💡 Export ${highlights.length} Highlights`}
        </button>
      )}
      <button style={btn} onClick={handleExportMarkdown}>
        {exported ? '✓ Exported!' : '📥 Export MD'}
      </button>
      <button style={btn} onClick={handleCopyLink}>
        {copied ? '✓ Copied!' : '🔗 Share'}
      </button>
      <button style={btn} onClick={() => cycle(-1)}>A−</button>
      <button style={btn} onClick={() => cycle(1)}>A+</button>
      <button style={btn} onClick={() => setDark(!dark)}>{dark ? '☀️' : '🌙'}</button>
    </div>
  )
}
