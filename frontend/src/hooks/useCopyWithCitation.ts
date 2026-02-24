'use client'
import { useEffect } from 'react'
import { analytics } from '@/lib/analytics'

interface CopyWithCitationProps {
  paperId: string
  paperTitle: string
}

export function useCopyWithCitation({ paperId, paperTitle }: CopyWithCitationProps) {
  useEffect(() => {
    const handleCopy = (e: ClipboardEvent) => {
      const selection = window.getSelection()
      if (!selection || selection.isCollapsed) return

      const selectedText = selection.toString().trim()
      if (selectedText.length < 10) return // Ignore very short selections

      // Check if selection is within reader body
      const range = selection.getRangeAt(0)
      const container = range.commonAncestorContainer
      const readerBody = document.querySelector('.reader-body')
      if (!readerBody?.contains(container)) return

      // Build citation
      const citation = `\n\n—\nExtracted via PaperFlow.app\n${paperTitle}\nhttps://frontend-one-alpha-89.vercel.app/read/${paperId}`

      // Append citation to clipboard
      const textWithCitation = selectedText + citation

      // Set clipboard data
      e.clipboardData?.setData('text/plain', textWithCitation)
      e.preventDefault()

      // Track analytics
      analytics.copyWithCitation(paperId)
    }

    document.addEventListener('copy', handleCopy)

    return () => {
      document.removeEventListener('copy', handleCopy)
    }
  }, [paperId, paperTitle])
}
