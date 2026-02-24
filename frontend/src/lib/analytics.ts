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
  visitHome: () => {
    if (POSTHOG_KEY) posthog.capture('visit_home')
  },
  uploadStart: (filename: string, sizeKB: number) => {
    if (POSTHOG_KEY) posthog.capture('upload_start', { filename, sizeKB })
  },
  parseSuccess: (paperId: string, durationSec: number) => {
    if (POSTHOG_KEY) posthog.capture('parse_success', { paperId, durationSec })
  },
  parseFailed: (errorCode: string, errorMessage: string) => {
    if (POSTHOG_KEY) posthog.capture('parse_failed', { errorCode, errorMessage })
  },
  readerView: (paperId: string) => {
    if (POSTHOG_KEY) posthog.capture('reader_view', { paperId })
  },
  shareCopyLink: (paperId: string) => {
    if (POSTHOG_KEY) posthog.capture('share_copy_link', { paperId })
  },
  feedbackSubmit: (type: string, message: string) => {
    if (POSTHOG_KEY) posthog.capture('feedback_submit', { type, message })
  },
  exportMarkdown: (paperId: string) => {
    if (POSTHOG_KEY) posthog.capture('export_markdown', { paperId })
  }
}
