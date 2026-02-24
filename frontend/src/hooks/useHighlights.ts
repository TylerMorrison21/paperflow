'use client'
import { useState, useEffect } from 'react'

export interface Highlight {
  id: string
  paperId: string
  text: string
  color: string
  timestamp: number
  context?: string
  anchorOffset: number
  focusOffset: number
}

const STORAGE_KEY = 'paperflow_highlights'

const COLOR_MAP: Record<string, string> = {
  yellow: '#fef08a',
  green: '#bbf7d0',
  blue: '#bfdbfe',
  pink: '#fbcfe8'
}

export function useHighlights(paperId: string) {
  const [highlights, setHighlights] = useState<Highlight[]>([])

  // Load highlights from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        const all: Highlight[] = JSON.parse(stored)
        setHighlights(all.filter(h => h.paperId === paperId))
      } catch (e) {
        console.error('Failed to load highlights:', e)
      }
    }
  }, [paperId])

  // Restore highlights to DOM when they load
  useEffect(() => {
    if (highlights.length === 0) return

    // Wait for content to render
    setTimeout(() => {
      highlights.forEach(h => {
        restoreHighlightToDOM(h)
      })
    }, 500)
  }, [highlights])

  const restoreHighlightToDOM = (highlight: Highlight) => {
    // Find text in the document using context
    if (!highlight.context) return

    const readerBody = document.querySelector('.reader-body')
    if (!readerBody) return

    const walker = document.createTreeWalker(
      readerBody,
      NodeFilter.SHOW_TEXT,
      null
    )

    let node
    while (node = walker.nextNode()) {
      const text = node.textContent || ''
      if (text.includes(highlight.text)) {
        try {
          const range = document.createRange()
          const startIndex = text.indexOf(highlight.text)
          if (startIndex === -1) continue

          range.setStart(node, startIndex)
          range.setEnd(node, startIndex + highlight.text.length)

          const mark = document.createElement('mark')
          mark.className = 'pf-highlight'
          mark.dataset.highlightId = highlight.id
          mark.style.background = COLOR_MAP[highlight.color] || highlight.color
          mark.style.cursor = 'pointer'
          mark.style.borderRadius = '2px'
          mark.style.padding = '2px 0'

          range.surroundContents(mark)
          break
        } catch (e) {
          console.warn('Failed to restore highlight:', e)
        }
      }
    }
  }

  const addHighlight = (text: string, color: string, context?: string) => {
    const selection = window.getSelection()
    if (!selection || selection.rangeCount === 0) return

    const range = selection.getRangeAt(0)

    // Create the highlight object
    const newHighlight: Highlight = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      paperId,
      text,
      color,
      timestamp: Date.now(),
      context,
      anchorOffset: range.startOffset,
      focusOffset: range.endOffset
    }

    // Wrap the selected text in a <mark> element
    try {
      const mark = document.createElement('mark')
      mark.className = 'pf-highlight'
      mark.dataset.highlightId = newHighlight.id
      mark.style.background = COLOR_MAP[color] || color
      mark.style.cursor = 'pointer'
      mark.style.borderRadius = '2px'
      mark.style.padding = '2px 0'

      range.surroundContents(mark)

      // Add click handler to remove highlight
      mark.addEventListener('click', () => {
        if (confirm('Remove this highlight?')) {
          removeHighlight(newHighlight.id)
        }
      })
    } catch (e) {
      console.error('Failed to apply highlight:', e)
      return
    }

    // Save to localStorage
    const stored = localStorage.getItem(STORAGE_KEY)
    const all: Highlight[] = stored ? JSON.parse(stored) : []
    all.push(newHighlight)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(all))

    // Update state
    setHighlights(prev => [...prev, newHighlight])

    return newHighlight.id
  }

  const removeHighlight = (id: string) => {
    // Remove from DOM
    const mark = document.querySelector(`[data-highlight-id="${id}"]`)
    if (mark) {
      const parent = mark.parentNode
      while (mark.firstChild) {
        parent?.insertBefore(mark.firstChild, mark)
      }
      parent?.removeChild(mark)
    }

    // Remove from localStorage
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return

    const all: Highlight[] = JSON.parse(stored)
    const filtered = all.filter(h => h.id !== id)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered))

    // Update state
    setHighlights(prev => prev.filter(h => h.id !== id))
  }

  const clearHighlights = () => {
    // Remove all marks from DOM
    highlights.forEach(h => {
      const mark = document.querySelector(`[data-highlight-id="${h.id}"]`)
      if (mark) {
        const parent = mark.parentNode
        while (mark.firstChild) {
          parent?.insertBefore(mark.firstChild, mark)
        }
        parent?.removeChild(mark)
      }
    })

    // Remove from localStorage
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return

    const all: Highlight[] = JSON.parse(stored)
    const filtered = all.filter(h => h.paperId !== paperId)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered))

    // Update state
    setHighlights([])
  }

  const exportHighlights = (paperTitle: string) => {
    if (highlights.length === 0) return null

    let markdown = `# Highlights from ${paperTitle}\n\n`
    markdown += `Exported: ${new Date().toLocaleDateString()}\n\n`
    markdown += `---\n\n`

    highlights.forEach((h, idx) => {
      markdown += `## Highlight ${idx + 1}\n\n`
      markdown += `> ${h.text}\n\n`
      if (h.context) {
        markdown += `*Context: ${h.context}*\n\n`
      }
      markdown += `---\n\n`
    })

    markdown += `*Exported via [PaperFlow](https://paperflow.app)*\n`

    return markdown
  }

  return {
    highlights,
    addHighlight,
    removeHighlight,
    clearHighlights,
    exportHighlights
  }
}

