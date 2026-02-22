'use client'
import { TOCItem } from '@/lib/types'

export default function TOCSidebar({ toc, activeId }: { toc: TOCItem[]; activeId: string }) {
  return (
    <nav style={{
      width: 260,
      flexShrink: 0,
      position: 'sticky',
      top: 56,
      height: 'calc(100vh - 56px)',
      overflowY: 'auto',
      padding: '1.5rem 1rem',
      borderRight: '1px solid var(--border)',
      fontFamily: 'system-ui',
      fontSize: '0.85rem',
    }}>
      <p style={{ fontWeight: 700, marginBottom: '1rem', textTransform: 'uppercase', fontSize: '0.7rem', letterSpacing: '0.08em', color: 'var(--muted)' }}>Contents</p>
      {toc.map(item => (
        <a
          key={item.id}
          href={`#${item.anchor}`}
          onClick={e => { e.preventDefault(); document.getElementById(item.anchor)?.scrollIntoView({ behavior: 'smooth' }) }}
          style={{
            display: 'block',
            padding: '0.3rem 0',
            paddingLeft: `${(item.level - 1) * 0.75}rem`,
            color: activeId === item.id ? 'var(--accent)' : 'var(--text)',
            textDecoration: 'none',
            lineHeight: 1.4,
            borderLeft: activeId === item.id ? '2px solid var(--accent)' : '2px solid transparent',
          }}
        >
          {item.title}
        </a>
      ))}
    </nav>
  )
}
