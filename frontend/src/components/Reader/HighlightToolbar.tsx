'use client'
import { useState } from 'react'

interface HighlightToolbarProps {
  onHighlight: (color: string) => void
  onClose: () => void
  position: { top: number, left: number }
}

const COLORS = [
  { name: 'Yellow', value: '#fff59d' },
  { name: 'Green', value: '#a5d6a7' },
  { name: 'Blue', value: '#90caf9' },
  { name: 'Pink', value: '#f48fb1' },
]

export default function HighlightToolbar({ onHighlight, onClose, position }: HighlightToolbarProps) {
  return (
    <div
      style={{
        position: 'absolute',
        top: position.top,
        left: position.left,
        background: 'var(--bg)',
        border: '1px solid var(--border)',
        borderRadius: 8,
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        padding: '0.5rem',
        display: 'flex',
        gap: '0.5rem',
        zIndex: 1000,
        animation: 'fadeIn 0.15s ease-out',
      }}
    >
      {COLORS.map(color => (
        <button
          key={color.value}
          onClick={() => onHighlight(color.value)}
          title={`Highlight ${color.name}`}
          style={{
            width: 32,
            height: 32,
            borderRadius: 4,
            border: '2px solid var(--border)',
            background: color.value,
            cursor: 'pointer',
            transition: 'transform 0.1s',
          }}
          onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
        />
      ))}
      <button
        onClick={onClose}
        style={{
          width: 32,
          height: 32,
          borderRadius: 4,
          border: '2px solid var(--border)',
          background: 'var(--bg)',
          cursor: 'pointer',
          fontSize: '1rem',
          color: 'var(--muted)',
        }}
      >
        ✕
      </button>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-5px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  )
}
