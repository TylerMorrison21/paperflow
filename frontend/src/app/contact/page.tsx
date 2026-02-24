import Link from 'next/link'

export default function ContactPage() {
  return (
    <main style={{ maxWidth: 800, margin: '0 auto', padding: '3rem 1.5rem', fontFamily: 'system-ui', lineHeight: 1.7 }}>
      <Link href="/" style={{ color: 'var(--muted)', textDecoration: 'none', fontSize: '0.9rem' }}>← Back to Home</Link>

      <h1 style={{ fontSize: '2.5rem', fontWeight: 700, marginTop: '2rem', marginBottom: '1rem' }}>Contact Us</h1>
      <p style={{ color: 'var(--muted)', marginBottom: '2rem', fontSize: '1.1rem' }}>
        We'd love to hear from you. Whether you have questions, feedback, or need support, reach out anytime.
      </p>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Email</h2>
        <p style={{ marginBottom: '1rem' }}>
          <a href="mailto:contact@paperflow.app" style={{ color: 'var(--accent)', fontSize: '1.1rem', textDecoration: 'none' }}>
            contact@paperflow.app
          </a>
        </p>
        <p style={{ color: 'var(--muted)', fontSize: '0.95rem' }}>
          We typically respond within 24-48 hours.
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>What to Include</h2>
        <p style={{ marginBottom: '1rem' }}>To help us assist you better, please include:</p>
        <ul style={{ marginLeft: '1.5rem', marginBottom: '1rem', color: 'var(--muted)' }}>
          <li>A clear description of your issue or question</li>
          <li>Paper ID (if relevant) — found in the URL like /read/abc-123</li>
          <li>Browser and device information (if reporting a bug)</li>
          <li>Screenshots (if applicable)</li>
        </ul>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Common Requests</h2>

        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>Bug Reports</h3>
          <p style={{ color: 'var(--muted)', fontSize: '0.95rem' }}>
            Found a bug? Let us know what happened, what you expected, and steps to reproduce it.
          </p>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>Feature Requests</h3>
          <p style={{ color: 'var(--muted)', fontSize: '0.95rem' }}>
            Have an idea to improve PaperFlow? We're collecting feedback to shape our roadmap.
          </p>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>Data Deletion</h3>
          <p style={{ color: 'var(--muted)', fontSize: '0.95rem' }}>
            Want to delete a converted paper? Send us the paper ID and we'll remove it within 48 hours.
          </p>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>Partnership & Press</h3>
          <p style={{ color: 'var(--muted)', fontSize: '0.95rem' }}>
            Interested in partnering or writing about PaperFlow? We'd love to chat.
          </p>
        </div>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Quick Feedback</h2>
        <p style={{ color: 'var(--muted)', fontSize: '0.95rem', marginBottom: '1rem' }}>
          For quick feedback, you can also use the feedback form in the reader view (available after converting a paper).
        </p>
      </section>

      <section style={{ marginBottom: '2rem', padding: '1.5rem', background: 'var(--bg-secondary)', borderRadius: '8px', border: '1px solid var(--border)' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.75rem' }}>Beta Notice</h2>
        <p style={{ color: 'var(--muted)', fontSize: '0.95rem' }}>
          PaperFlow is currently in beta. We're actively improving the service based on user feedback.
          Your input helps shape the future of academic reading.
        </p>
      </section>
    </main>
  )
}
