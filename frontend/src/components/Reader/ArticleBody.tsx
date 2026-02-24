'use client'
import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import rehypeRaw from 'rehype-raw'
import { Section } from '@/lib/types'
import InlinePopover from './InlinePopover'
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
    </>
  )
}
