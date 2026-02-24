'use client'
import { useState, useEffect } from 'react'

export interface Highlight {
  id: string
  paperId: string
  text: string
  color: string
  timestamp: number
  context?: string // surrounding text for context
}

const STORAGE_KEY = 'paperflow_highlights'

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

  const addHighlight = (text: string, color: string, context?: string) => {
    const newHighlight: Highlight = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      paperId,
      text,
      color,
      timestamp: Date.now(),
      context
    }

    // Load all highlights
    const stored = localStorage.getItem(STORAGE_KEY)
    const all: Highlight[] = stored ? JSON.parse(stored) : []

    // Add new highlight
    all.push(newHighlight)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(all))

    // Update state
    setHighlights(prev => [...prev, newHighlight])

    return newHighlight.id
  }

  const removeHighlight = (id: string) => {
    // Load all highlights
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return

    const all: Highlight[] = JSON.parse(stored)
    const filtered = all.filter(h => h.id !== id)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered))

    // Update state
    setHighlights(prev => prev.filter(h => h.id !== id))
  }

  const clearHighlights = () => {
    // Load all highlights
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

    // Build markdown
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
