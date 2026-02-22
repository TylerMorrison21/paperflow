'use client'
import Link from 'next/link'

export default function SettingsBar({ title, fontSize, setFontSize, dark, setDark }: {
  title: string
  fontSize: number
  setFontSize: (n: number) => void
  dark: boolean
  setDark: (v: boolean) => void
}) {
  const sizes = [16, 18, 20]
  const cycle = (dir: 1 | -1) => {
    const i = sizes.indexOf(fontSize)
    setFontSize(sizes[Math.max(0, Math.min(sizes.length - 1, i + dir))])
  }

  const bar: React.CSSProperties = {
    position: 'sticky', top: 0, zIndex: 10,
    display: 'flex', alignItems: 'center', gap: '1rem',
    padding: '0.6rem 1.5rem',
    background: dark ? '#111' : 'var(--bg)',
    borderBottom: '1px solid var(--border)',
    fontFamily: 'system-ui', fontSize: '0.875rem',
  }
  const btn: React.CSSProperties = { background: 'none', border: 'none', cursor: 'pointer', padding: '0.25rem 0.5rem', borderRadius: 4, fontSize: '0.875rem' }

  return (
    <div style={bar}>
      <Link href="/" style={{ textDecoration: 'none', color: 'var(--muted)', fontSize: '1.1rem' }}>←</Link>
      <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--text)' }}>{title}</span>
      <button style={btn} onClick={() => cycle(-1)}>A−</button>
      <button style={btn} onClick={() => cycle(1)}>A+</button>
      <button style={btn} onClick={() => setDark(!dark)}>{dark ? '☀️' : '🌙'}</button>
    </div>
  )
}
