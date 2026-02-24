import Link from 'next/link'

export default function TermsPage() {
  return (
    <main style={{ maxWidth: 800, margin: '0 auto', padding: '3rem 1.5rem', fontFamily: 'system-ui', lineHeight: 1.7 }}>
      <Link href="/" style={{ color: 'var(--muted)', textDecoration: 'none', fontSize: '0.9rem' }}>← Back to Home</Link>

      <h1 style={{ fontSize: '2.5rem', fontWeight: 700, marginTop: '2rem', marginBottom: '1rem' }}>Terms of Service</h1>
      <p style={{ color: 'var(--muted)', marginBottom: '2rem' }}>Last updated: February 24, 2026</p>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Acceptance of Terms</h2>
        <p style={{ marginBottom: '1rem' }}>
          By accessing and using PaperFlow, you accept and agree to be bound by these Terms of Service.
          If you do not agree, please do not use our service.
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Service Description</h2>
        <p style={{ marginBottom: '1rem' }}>
          PaperFlow converts academic PDF papers into web-readable articles with inline citations, figures, and tables.
          The service is currently in beta and provided free of charge.
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Acceptable Use</h2>
        <p style={{ marginBottom: '1rem' }}>You agree to:</p>
        <ul style={{ marginLeft: '1.5rem', marginBottom: '1rem' }}>
          <li>Only upload PDFs you have the right to process and share</li>
          <li>Not upload malicious files, spam, or illegal content</li>
          <li>Respect rate limits (10 uploads per 60 seconds per IP)</li>
          <li>Not attempt to reverse engineer, hack, or abuse the service</li>
          <li>Not use the service for commercial purposes without permission</li>
        </ul>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Content Ownership</h2>
        <p style={{ marginBottom: '1rem' }}>
          You retain all rights to the PDFs you upload. By using PaperFlow, you grant us a license to process,
          store, and display your content as necessary to provide the service.
        </p>
        <p style={{ marginBottom: '1rem' }}>
          You are responsible for ensuring you have the right to upload and share the content you submit.
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Service Availability</h2>
        <p style={{ marginBottom: '1rem' }}>
          PaperFlow is provided "as is" without warranties. We do not guarantee:
        </p>
        <ul style={{ marginLeft: '1.5rem', marginBottom: '1rem' }}>
          <li>100% uptime or availability</li>
          <li>Perfect conversion quality for all PDFs</li>
          <li>Permanent storage of converted papers</li>
          <li>Continued free access (pricing may be introduced)</li>
        </ul>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Rate Limits</h2>
        <p style={{ marginBottom: '1rem' }}>
          To ensure fair usage, we enforce rate limits of 10 uploads per 60 seconds per IP address.
          Excessive use may result in temporary or permanent blocking.
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>File Size Limits</h2>
        <p style={{ marginBottom: '1rem' }}>
          Maximum PDF file size is 50MB. Files exceeding this limit will be rejected.
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Termination</h2>
        <p style={{ marginBottom: '1rem' }}>
          We reserve the right to terminate or suspend access to our service immediately, without prior notice,
          for conduct that violates these Terms or is harmful to other users or the service.
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Limitation of Liability</h2>
        <p style={{ marginBottom: '1rem' }}>
          PaperFlow and its operators shall not be liable for any indirect, incidental, special, consequential,
          or punitive damages resulting from your use of the service.
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Changes to Terms</h2>
        <p style={{ marginBottom: '1rem' }}>
          We may modify these terms at any time. Continued use of PaperFlow after changes constitutes acceptance
          of the updated terms.
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Contact</h2>
        <p>
          Questions about these terms? Email us at <a href="mailto:contact@paperflow.app" style={{ color: 'var(--accent)' }}>contact@paperflow.app</a>
        </p>
      </section>
    </main>
  )
}
