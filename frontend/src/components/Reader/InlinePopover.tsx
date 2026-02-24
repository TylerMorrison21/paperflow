'use client'
import { useState, useEffect, useRef } from 'react'

interface PopoverProps {
  targetId: string
  onClose: () => void
}

export default function InlinePopover({ targetId, onClose }: PopoverProps) {
  const [content, setContent] = useState<HTMLElement | null>(null)
  const [position, setPosition] = useState({ top: 0, left: 0 })
  const popoverRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Find the target element (figure, table, or reference)
    const target = document.getElementById(targetId)
    if (!target) {
      onClose()
      return
    }

    // Clone the content
    const clone = target.cloneNode(true) as HTMLElement
    setContent(clone)

    // Calculate position (center below the clicked link)
    const updatePosition = () => {
      const rect = target.getBoundingClientRect()
      const viewportWidth = window.innerWidth
      const popoverWidth = 400 // max width

      let left = rect.left + rect.width / 2 - popoverWidth / 2

      // Keep within viewport
      if (left < 10) left = 10
      if (left + popoverWidth > viewportWidth - 10) left = viewportWidth - popoverWidth - 10

      setPosition({
        top: window.scrollY + rect.bottom + 10,
        left: left + window.scrollX
      })
    }

    updatePosition()
    window.addEventListener('resize', updatePosition)
    window.addEventListener('scroll', updatePosition)

    return () => {
      window.removeEventListener('resize', updatePosition)
      window.removeEventListener('scroll', updatePosition)
    }
  }, [targetId, onClose])

  useEffect(() => {
    // Close on click outside
    const handleClickOutside = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        onClose()
      }
    }

    // Close on Escape key
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }

    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleEscape)

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [onClose])

  if (!content) return null

  return (
    <>
      {/* Backdrop */}
      <div
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0, 0, 0, 0.1)',
          zIndex: 999,
        }}
        onClick={onClose}
      />

      {/* Popover */}
      <div
        ref={popoverRef}
        style={{
          position: 'absolute',
          top: position.top,
          left: position.left,
          maxWidth: 400,
          maxHeight: '70vh',
          overflowY: 'auto',
          background: 'var(--bg)',
          border: '2px solid var(--accent)',
          borderRadius: 8,
          boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
          padding: '1rem',
          zIndex: 1000,
          fontFamily: 'system-ui',
          fontSize: '0.9rem',
          animation: 'popoverFadeIn 0.15s ease-out',
        }}
      >
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: 8,
            right: 8,
            background: 'none',
            border: 'none',
            fontSize: '1.2rem',
            cursor: 'pointer',
            color: 'var(--muted)',
            padding: '0.25rem',
            lineHeight: 1,
          }}
        >
          ✕
        </button>
        <div dangerouslySetInnerHTML={{ __html: content.innerHTML }} />
      </div>

      <style jsx>{`
        @keyframes popoverFadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </>
  )
}
