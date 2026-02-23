# Task A: Frontend P0 - Event Tracking + Sharing + Failure Experience

## Objectives
Implement analytics events, shareable links with copy button, and robust upload/processing/failure/retry state machine.

## 1. Analytics Events (PostHog)

Install PostHog:
```bash
cd /d/projects/pdfreflow/frontend
npm install posthog-js
```

Create analytics utility at `frontend/src/lib/analytics.ts`:
```typescript
import posthog from 'posthog-js'

const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY
const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com'

// Initialize PostHog (call once in layout)
export function initAnalytics() {
  if (typeof window !== 'undefined' && POSTHOG_KEY) {
    posthog.init(POSTHOG_KEY, {
      api_host: POSTHOG_HOST,
      loaded: (posthog) => {
        if (process.env.NODE_ENV === 'development') posthog.debug()
      }
    })
  }
}

// Event tracking functions
export const analytics = {
  visitHome: () => posthog.capture('visit_home'),
  uploadStart: (filename: string, sizeKB: number) =>
    posthog.capture('upload_start', { filename, sizeKB }),
  parseSuccess: (paperId: string, durationSec: number) =>
    posthog.capture('parse_success', { paperId, durationSec }),
  parseFailed: (errorCode: string, errorMessage: string) =>
    posthog.capture('parse_failed', { errorCode, errorMessage }),
  readerView: (paperId: string) =>
    posthog.capture('reader_view', { paperId }),
  shareCopyLink: (paperId: string) =>
    posthog.capture('share_copy_link', { paperId }),
  feedbackSubmit: (type: string, message: string) =>
    posthog.capture('feedback_submit', { type, message })
}
```

Initialize in `frontend/src/app/layout.tsx`:
```typescript
'use client'
import { useEffect } from 'react'
import { initAnalytics } from '@/lib/analytics'

export default function RootLayout({ children }) {
  useEffect(() => {
    initAnalytics()
  }, [])

  return (
    <html>
      <body>{children}</body>
    </html>
  )
}
```

## 2. Shareable Links + Copy Button

Update `frontend/src/app/read/[id]/page.tsx` to add copy link button in SettingsBar:

```typescript
'use client'
import { useState } from 'react'
import { analytics } from '@/lib/analytics'

function CopyLinkButton({ paperId }: { paperId: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    const url = `${window.location.origin}/read/${paperId}`
    await navigator.clipboard.writeText(url)
    setCopied(true)
    analytics.shareCopyLink(paperId)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button onClick={handleCopy} className="copy-link-btn">
      {copied ? '✓ Copied!' : '🔗 Share'}
    </button>
  )
}
```

Add to SettingsBar component.

## 3. Upload/Processing/Failure State Machine

Update `frontend/src/app/page.tsx` with robust state handling:

```typescript
'use client'
import { useState } from 'react'
import { analytics } from '@/lib/analytics'

type UploadState =
  | { status: 'idle' }
  | { status: 'uploading', progress: number }
  | { status: 'processing', paperId: string, elapsed: number }
  | { status: 'success', paperId: string }
  | { status: 'error', errorCode: string, message: string, retryable: boolean }

export default function HomePage() {
  const [state, setState] = useState<UploadState>({ status: 'idle' })

  const handleUpload = async (file: File) => {
    // Track upload start
    analytics.uploadStart(file.name, Math.round(file.size / 1024))

    setState({ status: 'uploading', progress: 0 })

    try {
      // Upload PDF
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/parse`, {
        method: 'POST',
        body: formData
      })

      if (!res.ok) {
        const error = await res.json()
        throw new Error(error.error_code || 'UPLOAD_FAILED')
      }

      const { paper_id } = await res.json()
      setState({ status: 'processing', paperId: paper_id, elapsed: 0 })

      // Poll for completion
      const startTime = Date.now()
      const pollInterval = setInterval(async () => {
        const elapsed = Math.round((Date.now() - startTime) / 1000)
        setState(s => s.status === 'processing' ? { ...s, elapsed } : s)

        const statusRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/parse/${paper_id}`)
        const statusData = await statusRes.json()

        if (statusData.status === 'complete') {
          clearInterval(pollInterval)
          analytics.parseSuccess(paper_id, elapsed)
          setState({ status: 'success', paperId: paper_id })
          // Redirect to reader
          window.location.href = `/read/${paper_id}`
        } else if (statusData.status === 'error') {
          clearInterval(pollInterval)
          analytics.parseFailed(statusData.error_code || 'UNKNOWN', statusData.message || 'Processing failed')
          setState({
            status: 'error',
            errorCode: statusData.error_code || 'PARSE_FAILED',
            message: statusData.message || 'Failed to process PDF',
            retryable: true
          })
        }
      }, 2000)

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
  }

  const handleRetry = () => {
    setState({ status: 'idle' })
  }

  return (
    <div>
      {state.status === 'idle' && <UploadZone onUpload={handleUpload} />}
      {state.status === 'uploading' && <div>Uploading... {state.progress}%</div>}
      {state.status === 'processing' && (
        <div>
          Processing your PDF... {state.elapsed}s
          <p className="text-sm text-gray-500">Usually takes 30-120 seconds</p>
        </div>
      )}
      {state.status === 'error' && (
        <div className="error-box">
          <h3>⚠️ {state.errorCode}</h3>
          <p>{state.message}</p>
          {state.retryable && (
            <button onClick={handleRetry}>Try Again</button>
          )}
        </div>
      )}
    </div>
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
```

## 4. Track Reader Views

Update `frontend/src/app/read/[id]/page.tsx`:

```typescript
'use client'
import { useEffect } from 'react'
import { analytics } from '@/lib/analytics'

export default function ReaderPage({ params }: { params: { id: string } }) {
  useEffect(() => {
    analytics.readerView(params.id)
  }, [params.id])

  // ... rest of component
}
```

## 5. Environment Variables

Add to `frontend/.env.local`:
```
NEXT_PUBLIC_POSTHOG_KEY=your_posthog_key_here
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
```

Add to Vercel environment variables when deploying.

## 6. Verification Checklist

Local testing:
```bash
cd /d/projects/pdfreflow/frontend
npm run dev
```

Test scenarios:
- [ ] Visit homepage → check PostHog for `visit_home` event
- [ ] Upload PDF → check `upload_start` event with filename/size
- [ ] Wait for processing → see elapsed time counter
- [ ] Processing completes → check `parse_success` event, redirect to reader
- [ ] Reader page loads → check `reader_view` event
- [ ] Click share button → check `share_copy_link` event, verify clipboard
- [ ] Upload invalid file → see error message with retry button
- [ ] Click retry → return to upload state

Error testing (simulate backend errors):
- [ ] 413 response → show "File too large" message, no retry button
- [ ] 429 response → show "Rate limited" message, show retry button
- [ ] Processing timeout → show error with retry

## Success Criteria

✅ All analytics events firing correctly in PostHog dashboard
✅ Share button copies correct URL to clipboard
✅ Upload state machine handles all states (idle/uploading/processing/success/error)
✅ Error messages are user-friendly and actionable
✅ Retry button works for retryable errors
✅ Processing shows elapsed time and estimated duration
