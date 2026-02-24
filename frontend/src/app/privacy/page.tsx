import Link from 'next/link'

export default function PrivacyPage() {
  return (
    <main style={{ maxWidth: 800, margin: '0 auto', padding: '3rem 1.5rem', fontFamily: 'system-ui', lineHeight: 1.7 }}>
      <Link href="/" style={{ color: 'var(--muted)', textDecoration: 'none', fontSize: '0.9rem' }}>← Back to Home</Link>

      <h1 style={{ fontSize: '2.5rem', fontWeight: 700, marginTop: '2rem', marginBottom: '1rem' }}>Privacy Policy</h1>
      <p style={{ color: 'var(--muted)', marginBottom: '2rem' }}>Last updated: February 24, 2026</p>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>What We Collect</h2>
        <p style={{ marginBottom: '1rem' }}>When you use PaperFlow, we collect:</p>
        <ul style={{ marginLeft: '1.5rem', marginBottom: '1rem' }}>
          <li>PDF files you upload for conversion</li>
          <li>IP address and user agent for rate limiting and analytics</li>
          <li>Usage analytics via PostHog (page views, conversion events)</li>
          <li>Feedback you voluntarily submit</li>
        </ul>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>How We Use Your Data</h2>
        <p style={{ marginBottom: '1rem' }}>We use your data to:</p>
        <ul style={{ marginLeft: '1.5rem', marginBottom: '1rem' }}>
          <li>Convert your PDFs into readable web articles</li>
          <li>Generate shareable links for your converted papers</li>
          <li>Improve our service through analytics and feedback</li>
          <li>Prevent abuse through rate limiting</li>
        </ul>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Data Storage</h2>
        <p style={{ marginBottom: '1rem' }}>
          Converted papers are stored on our servers to enable shareable links. We store the processed markdown,
          extracted images, and metadata needed to render your reading page.
        </p>
        <p style={{ marginBottom: '1rem' }}>
          Original PDF files are processed through the Datalab Marker API and are not permanently stored by us.
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Third-Party Services</h2>
        <p style={{ marginBottom: '1rem' }}>We use:</p>
        <ul style={{ marginLeft: '1.5rem', marginBottom: '1rem' }}>
          <li><strong>Datalab Marker API</strong> — PDF to markdown conversion</li>
          <li><strong>PostHog</strong> — Privacy-friendly analytics (optional, can be disabled)</li>
          <li><strong>Vercel</strong> — Frontend hosting</li>
          <li><strong>Railway</strong> — Backend hosting</li>
        </ul>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Your Rights</h2>
        <p style={{ marginBottom: '1rem' }}>You have the right to:</p>
        <ul style={{ marginLeft: '1.5rem', marginBottom: '1rem' }}>
          <li>Request deletion of your converted papers</li>
          <li>Access the data we store about you</li>
          <li>Opt out of analytics tracking</li>
        </ul>
        <p style={{ marginBottom: '1rem' }}>
          To exercise these rights, contact us at <a href="mailto:contact@paperflow.app" style={{ color: 'var(--accent)' }}>contact@paperflow.app</a>
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Data Retention</h2>
        <p style={{ marginBottom: '1rem' }}>
          Converted papers are retained indefinitely to support shareable links. You may request deletion at any time.
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Changes to This Policy</h2>
        <p style={{ marginBottom: '1rem' }}>
          We may update this policy from time to time. Continued use of PaperFlow after changes constitutes acceptance of the updated policy.
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Contact</h2>
        <p>
          Questions about privacy? Email us at <a href="mailto:contact@paperflow.app" style={{ color: 'var(--accent)' }}>contact@paperflow.app</a>
        </p>
      </section>
    </main>
  )
}
