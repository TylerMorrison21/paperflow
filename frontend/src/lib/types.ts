export interface TOCItem {
  id: string
  title: string
  level: number
  anchor: string
}

export interface Section {
  id: string
  heading: string
  level: number
  markdown: string
  page_start?: number
  page_end?: number
}

export interface PaperData {
  title: string
  toc: TOCItem[]
  sections: Section[]
  images: Record<string, string>
  metadata: {
    page_count: number
    has_equations: boolean
    has_tables: boolean
    word_count: number
  }
}

export interface PaperStatus {
  paper_id: string
  status: 'processing' | 'complete' | 'error'
  error?: string
}
