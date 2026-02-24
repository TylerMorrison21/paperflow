'use client'
import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import rehypeRaw from 'rehype-raw'
import { Section } from '@/lib/types'
import InlinePopover from './InlinePopover'
import HighlightToolbar from './HighlightToolbar'
import { useHighlights } from '@/hooks/useHighlights'
import { analytics } from '@/lib/analytics'
import '@/styles/reader.css'

function slugify(text: string) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

function resolveImage(src: string, images: Record<string, string>): string {
  const raw = images[src] ?? images[src.split('/').pop() ?? '']
  if (!raw) return src
  // Marker may return bare base64 or already-prefixed data URLs
  return raw.startsWith('data:') ? raw : `data:image/png;base64,${raw}`
}

export default function ArticleBody({ sections, images, fontSize, paperId }: {
  sections: Section[]
  images: Record<string, string>
  fontSize: number
  paperId: string
}) {
  const [popoverTarget, setPopoverTarget] = useState<string | null>(null)
  const [highlightToolbar, setHighlightToolbar] = useState<{ top: number, left: number } | null>(null)
  const [selectedText, setSelectedText] = useState<string>('')
  const { highlights, addHighlight } = useHighlights(paperId)

  // Handle text selection
  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection()
      if (!selection || selection.isCollapsed) {
        setHighlightToolbar(null)
        return
      }

      const text = selection.toString().trim()
      if (text.length < 3) {
        setHighlightToolbar(null)
        return
      }

      // Check if selection is within reader body
      const range = selection.getRangeAt(0)
      const container = range.commonAncestorContainer
      const readerBody = document.querySelector('.reader-body')
      if (!readerBody?.contains(container)) {
        setHighlightToolbar(null)
        return
      }

      setSelectedText(text)

      // Position toolbar above selection
      const rect = range.getBoundingClientRect()
      setHighlightToolbar({
        top: window.scrollY + rect.top - 50,
        left: rect.left + rect.width / 2 - 100
      })
    }

    document.addEventListener('mouseup', handleSelection)
    document.addEventListener('selectionchange', handleSelection)

    return () => {
      document.removeEventListener('mouseup', handleSelection)
      document.removeEventListener('selectionchange', handleSelection)
    }
  }, [])

  const handleHighlight = (color: string) => {
    if (!selectedText) return

    // Get context (surrounding text)
    const selection = window.getSelection()
    const range = selection?.getRangeAt(0)
    const context = range?.startContainer.parentElement?.textContent?.slice(0, 100)

    addHighlight(selectedText, color, context)

    // Track analytics
    analytics.textHighlight?.(paperId, color)

    // Clear selection and toolbar
    window.getSelection()?.removeAllRanges()
    setHighlightToolbar(null)
    setSelectedText('')
  }

  const heading = (Tag: 'h1' | 'h2' | 'h3' | 'h4') =>
    ({ children, ...p }: any) => <Tag id={slugify(String(children))} {...p}>{children}</Tag>

  // Intercept anchor links for inline popover
  const handleLinkClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    if (href.startsWith('#')) {
      e.preventDefault()
      const targetId = href.slice(1)
      const target = document.getElementById(targetId)

      // Check if target is a figure, table, or reference
      if (target && (
        targetId.startsWith('fig-') ||
        targetId.startsWith('table-') ||
        targetId.startsWith('ref-') ||
        target.tagName === 'FIGURE' ||
        target.tagName === 'TABLE' ||
        target.closest('figure') ||
        target.closest('table')
      )) {
        setPopoverTarget(targetId)

        // Track popover usage
        const targetType = targetId.startsWith('fig-') ? 'figure' :
                          targetId.startsWith('table-') ? 'table' : 'reference'
        analytics.inlinePopover(paperId, targetType)
      } else {
        // Regular scroll for section headings
        target?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }
  }

  const components: any = {
    h1: heading('h1'), h2: heading('h2'), h3: heading('h3'), h4: heading('h4'),
    img: ({ src, alt }: any) => <img src={resolveImage(src ?? '', images)} alt={alt ?? ''} />,
    table: ({ children }: any) => <div style={{ overflowX: 'auto' }}><table>{children}</table></div>,
    a: ({ href, children, ...props }: any) => (
      <a
        href={href}
        onClick={(e) => handleLinkClick(e, href)}
        style={{ cursor: 'pointer', color: 'var(--accent)', textDecoration: 'underline' }}
        {...props}
      >
        {children}
      </a>
    ),
    // Wrap KaTeX errors gracefully
    math: ({ value }: any) => {
      try {
        return null // let rehype-katex handle it
      } catch {
        return <code>{value}</code>
      }
    },
  }

  // Strip out page markers from markdown
  const stripPageMarkers = (md: string) => {
    return md.replace(/<span class="page-marker"[^>]*>.*?<\/span>/g, '')
  }

  return (
    <>
      <div className="reader-body" style={{ fontSize }}>
        {sections.map(s => (
          <section key={s.id} id={s.id}>
            <ReactMarkdown
              remarkPlugins={[remarkMath]}
              rehypePlugins={[rehypeRaw, rehypeKatex]}
              components={components}
            >
              {stripPageMarkers(s.markdown)}
            </ReactMarkdown>
          </section>
        ))}
      </div>

      {/* Inline Popover */}
      {popoverTarget && (
        <InlinePopover
          targetId={popoverTarget}
          onClose={() => setPopoverTarget(null)}
        />
      )}

      {/* Highlight Toolbar */}
      {highlightToolbar && (
        <HighlightToolbar
          position={highlightToolbar}
          onHighlight={handleHighlight}
          onClose={() => setHighlightToolbar(null)}
        />
      )}
    </>
  )
}
