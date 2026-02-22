'use client'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import rehypeRaw from 'rehype-raw'
import { Section } from '@/lib/types'
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

export default function ArticleBody({ sections, images, fontSize }: {
  sections: Section[]
  images: Record<string, string>
  fontSize: number
}) {
  const heading = (Tag: 'h1' | 'h2' | 'h3' | 'h4') =>
    ({ children, ...p }: any) => <Tag id={slugify(String(children))} {...p}>{children}</Tag>

  const components: any = {
    h1: heading('h1'), h2: heading('h2'), h3: heading('h3'), h4: heading('h4'),
    img: ({ src, alt }: any) => <img src={resolveImage(src ?? '', images)} alt={alt ?? ''} />,
    table: ({ children }: any) => <div style={{ overflowX: 'auto' }}><table>{children}</table></div>,
    // Wrap KaTeX errors gracefully
    math: ({ value }: any) => {
      try {
        return null // let rehype-katex handle it
      } catch {
        return <code>{value}</code>
      }
    },
  }

  return (
    <div className="reader-body" style={{ fontSize }}>
      {sections.map(s => (
        <section key={s.id} id={s.id}>
          <ReactMarkdown
            remarkPlugins={[remarkMath]}
            rehypePlugins={[rehypeRaw, rehypeKatex]}
            components={components}
          >
            {s.markdown}
          </ReactMarkdown>
        </section>
      ))}
    </div>
  )
}
