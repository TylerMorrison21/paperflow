'use client'
import { useState, useCallback } from 'react'
import { uploadPDF } from '@/lib/api'
import ProcessingStatus from './ProcessingStatus'
import { analytics } from '@/lib/analytics'

type UploadState =
  | { status: 'idle' }
  | { status: 'uploading' }
  | { status: 'processing', paperId: string }
  | { status: 'error', errorCode: string, message: string, retryable: boolean }

export default function UploadZone({ onComplete }: { onComplete: (id: string) => void }) {
  const [state, setState] = useState<UploadState>({ status: 'idle' })
  const [dragOver, setDragOver] = useState(false)

  const handleFile = useCallback(async (file: File) => {
    if (!file.name.endsWith('.pdf')) {
      setState({
        status: 'error',
        errorCode: 'INVALID_PDF',
        message: 'Please upload a valid PDF file.',
        retryable: true
      })
      return
    }

    // Track upload start
    analytics.uploadStart(file.name, Math.round(file.size / 1024))

    setState({ status: 'uploading' })
    try {
      const { paper_id } = await uploadPDF(file)
      setState({ status: 'processing', paperId: paper_id })
    } catch (err: any) {
      const errorCode = err.message || 'UPLOAD_FAILED'
      analytics.parseFailed(errorCode, err.toString())
      setState({
        status: 'error',
        errorCode,
        message: getErrorMessage(errorCode),
        retryable: errorCode !== 'FILE_TOO_LARGE'
      })
    }
  }, [])

  const handleRetry = () => {
    setState({ status: 'idle' })
  }

  if (state.status === 'processing') {
    return <ProcessingStatus paperId={state.paperId} onComplete={onComplete} onError={(msg) => {
      setState({
        status: 'error',
        errorCode: 'PARSE_FAILED',
        message: msg,
        retryable: true
      })
    }} />
  }

  if (state.status === 'error') {
    return (
      <div style={{
        maxWidth: 480,
        width: '100%',
        padding: '2rem',
        textAlign: 'center',
        border: '2px solid #fee',
        borderRadius: 12,
        background: '#fff5f5'
      }}>
        <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⚠️</div>
        <h3 style={{ fontFamily: 'system-ui', fontWeight: 600, marginBottom: '0.5rem', color: '#c00' }}>
          {state.errorCode}
        </h3>
        <p style={{ fontFamily: 'system-ui', fontSize: '0.95rem', color: '#666', marginBottom: '1.5rem' }}>
          {state.message}
        </p>
        {state.retryable && (
          <button
            onClick={handleRetry}
            style={{
              fontFamily: 'system-ui',
              padding: '0.6rem 1.5rem',
              background: 'var(--accent)',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              cursor: 'pointer',
              fontWeight: 600
            }}
          >
            Try Again
          </button>
        )}
      </div>
    )
  }

  return (
    <>
      <div
        onDragOver={e => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={e => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f) }}
        onClick={() => document.getElementById('pdf-input')?.click()}
        style={{
          border: `2px dashed ${dragOver ? 'var(--accent)' : '#ccc'}`,
          borderRadius: 12,
          padding: '3rem 2rem',
          cursor: 'pointer',
          background: dragOver ? '#fff5f5' : 'transparent',
          transition: 'all 0.2s',
          maxWidth: 480,
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
        }}
      >
        <input id="pdf-input" type="file" accept=".pdf" style={{ display: 'none' }}
          onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f) }} />
        <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📄</div>
        <p style={{ fontFamily: 'system-ui', fontWeight: 600, marginBottom: '0.5rem' }}>
          {state.status === 'uploading' ? 'Uploading…' : 'Drop a PDF here, or click to browse'}
        </p>
        <p style={{ fontFamily: 'system-ui', fontSize: '0.875rem', color: 'var(--muted)' }}>PDF files only</p>
      </div>

      {/* Trust Signal */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        marginTop: '1rem',
        fontFamily: 'system-ui',
        fontSize: '0.875rem',
        color: 'var(--muted)'
      }}>
        <span style={{ fontSize: '1rem' }}>🔒</span>
        <span>Private & secure. We never use your data to train AI.</span>
      </div>
    </>
  )
}

function getErrorMessage(errorCode: string): string {
  const messages: Record<string, string> = {
    'FILE_TOO_LARGE': 'PDF file is too large. Maximum size is 50MB.',
    'RATE_LIMITED': 'Too many requests. Please wait a moment and try again.',
    'INVALID_PDF': 'This file is not a valid PDF.',
    'PARSE_FAILED': 'Failed to process PDF. The file may be corrupted or unsupported.',
    'UPLOAD_FAILED': 'Upload failed. Please check your connection and try again.'
  }
  return messages[errorCode] || 'An unexpected error occurred.'
}
