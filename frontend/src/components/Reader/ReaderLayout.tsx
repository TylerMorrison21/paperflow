'use client'
import { useState, useEffect } from 'react'
import { PaperData } from '@/lib/types'
import TOCSidebar from './TOCSidebar'
import ArticleBody from './ArticleBody'
import SettingsBar from './SettingsBar'

export default function ReaderLayout({ paper }: { paper: PaperData }) {
  const [fontSize, setFontSize] = useState(18)
  const [dark, setDark] = useState(false)
  const [activeId, setActiveId] = useState('')
  const [drawerOpen, setDrawerOpen] = useState(false)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  useEffect(() => {
    const obs = new IntersectionObserver(
      entries => {
        const visible = entries.filter(e => e.isIntersecting)
        if (visible.length) setActiveId(visible[0].target.id)
      },
      { threshold: 0.3 }
    )
    document.querySelectorAll('section[id]').forEach(el => obs.observe(el))
    return () => obs.disconnect()
  }, [paper.sections])

  return (
    <div style={{ background: dark ? '#1a1a1a' : 'var(--bg)', minHeight: '100vh' }}>
      <SettingsBar title={paper.title} fontSize={fontSize} setFontSize={setFontSize} dark={dark} setDark={setDark} />

      <div style={{ display: 'flex' }}>
        {/* Desktop TOC */}
        <div className="hidden md:block">
          <TOCSidebar toc={paper.toc} activeId={activeId} />
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden"
          onClick={() => setDrawerOpen(true)}
          style={{ position: 'fixed', bottom: '1.5rem', left: '1rem', zIndex: 20, background: 'var(--accent)', color: '#fff', border: 'none', borderRadius: '50%', width: 44, height: 44, fontSize: '1.2rem', cursor: 'pointer' }}
        >☰</button>

        {/* Mobile drawer */}
        {drawerOpen && (
          <div style={{ position: 'fixed', inset: 0, zIndex: 30, display: 'flex' }}>
            <div style={{ flex: 1, background: 'rgba(0,0,0,0.4)' }} onClick={() => setDrawerOpen(false)} />
            <div style={{ width: 280, background: dark ? '#111' : '#fff', overflowY: 'auto' }}>
              <button onClick={() => setDrawerOpen(false)} style={{ float: 'right', padding: '1rem', background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer' }}>✕</button>
              <TOCSidebar toc={paper.toc} activeId={activeId} />
            </div>
          </div>
        )}

        <main style={{ flex: 1, minWidth: 0 }}>
          <ArticleBody sections={paper.sections} images={paper.images} fontSize={fontSize} />
        </main>
      </div>
    </div>
  )
}
