'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import UploadZone from '@/components/UploadZone'
import { analytics } from '@/lib/analytics'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    analytics.visitHome()
  }, [])

  return (
    <>
      {/* Header */}
      <header style={{
        padding: '1.5rem 5%',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        position: 'fixed',
        width: '100%',
        top: 0,
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        zIndex: 1000,
        borderBottom: '1px solid rgba(0, 0, 0, 0.05)'
      }}>
        <div style={{
          fontSize: '1.5rem',
          fontWeight: 700,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          📄 PaperFlow
        </div>
        <nav style={{ display: 'flex', gap: '2rem' }}>
          <a href="#features" style={{ textDecoration: 'none', color: '#666', fontWeight: 500 }}>Features</a>
          <a href="#how-it-works" style={{ textDecoration: 'none', color: '#666', fontWeight: 500 }}>How it Works</a>
          <a href="#faq" style={{ textDecoration: 'none', color: '#666', fontWeight: 500 }}>FAQ</a>
        </nav>
      </header>

      {/* Privacy Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)',
        padding: '1rem',
        textAlign: 'center',
        fontSize: '0.9rem',
        color: '#666',
        borderBottom: '1px solid rgba(0, 0, 0, 0.05)',
        marginTop: '80px'
      }}>
        🔒 <strong>Private & secure:</strong> We never use your data to train AI
      </div>

      <main style={{ fontFamily: 'system-ui' }}>
        {/* Hero Section */}
        <section style={{
          padding: '6rem 5% 4rem',
          textAlign: 'center',
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)'
        }}>
          <h1 style={{
            fontSize: 'clamp(2.5rem, 6vw, 3.5rem)',
            fontWeight: 800,
            marginBottom: '1.5rem',
            lineHeight: 1.2,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Read papers without<br />scroll-back hell.
          </h1>
          <p style={{ fontSize: '1.25rem', color: '#666', maxWidth: 700, margin: '0 auto 2rem', lineHeight: 1.8 }}>
            Click any Figure / Table / Reference inline—keep your place, keep context. Turn PDFs into a clean, shareable reading link.
          </p>
          <p style={{ fontSize: '1rem', color: '#999', marginTop: '1rem' }}>
            Built for researchers, students, and anyone who reads academic papers on their phone.
          </p>

          <div style={{
            maxWidth: 600,
            margin: '3rem auto',
            padding: '3rem',
            background: 'white',
            borderRadius: '20px',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.1)'
          }}>
            <UploadZone onComplete={id => router.push(`/read/${id}`)} />
            <p style={{ marginTop: '1.5rem', fontSize: '0.95rem', color: '#999', lineHeight: 1.8 }}>
              ✓ Click citations, figures & tables to view inline – no scroll-back hell<br />
              ✓ Highlight text + export to Markdown for zero-friction knowledge capture<br />
              ✓ Copy text with auto-citation – perfect for Slack, Discord, and email<br />
              ✓ Shareable link for every paper
            </p>
          </div>
        </section>

        {/* Comparison Section */}
        <section style={{ padding: '6rem 5%', background: 'white' }}>
          <h2 style={{ fontSize: '2.5rem', fontWeight: 700, textAlign: 'center', marginBottom: '3rem', color: '#1a1a1a' }}>
            The Difference
          </h2>
          <div style={{
            maxWidth: 1200,
            margin: '0 auto',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '3rem'
          }}>
            {/* Before */}
            <div style={{
              background: 'white',
              borderRadius: '16px',
              overflow: 'hidden',
              border: '2px solid #ff6b6b'
            }}>
              <div style={{
                padding: '1.5rem',
                color: 'white',
                fontWeight: 700,
                fontSize: '1.2rem',
                textAlign: 'center',
                background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)'
              }}>
                📄 Regular PDF
              </div>
              <div style={{ padding: '2rem' }}>
                <div style={{
                  width: '100%',
                  height: '400px',
                  background: '#f8f9fa',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '1.5rem',
                  border: '1px solid rgba(0, 0, 0, 0.05)',
                  color: '#999'
                }}>
                  Traditional PDF View
                </div>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {['Endless scrolling to check references', 'Lose your place constantly', 'Figures buried pages away', 'Hard to read on mobile', 'No inline citations'].map((item, i) => (
                    <li key={i} style={{
                      padding: '0.8rem 0',
                      borderBottom: i < 4 ? '1px solid rgba(0, 0, 0, 0.05)' : 'none',
                      display: 'flex',
                      alignItems: 'center',
                      color: '#666'
                    }}>
                      <span style={{ marginRight: '0.8rem', fontSize: '1.2rem' }}>❌</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* After */}
            <div style={{
              background: 'white',
              borderRadius: '16px',
              overflow: 'hidden',
              border: '2px solid #667eea',
              boxShadow: '0 10px 40px rgba(102, 126, 234, 0.15)'
            }}>
              <div style={{
                padding: '1.5rem',
                color: 'white',
                fontWeight: 700,
                fontSize: '1.2rem',
                textAlign: 'center',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              }}>
                ✨ PaperFlow
              </div>
              <div style={{ padding: '2rem' }}>
                <div style={{
                  width: '100%',
                  height: '400px',
                  background: '#f8f9fa',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '1.5rem',
                  border: '1px solid rgba(0, 0, 0, 0.05)',
                  color: '#999'
                }}>
                  Structured Reading View
                </div>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {['Click any citation to view inline', 'Never lose your reading position', 'Figures appear instantly', 'Perfect mobile experience', 'Smart highlighting & export'].map((item, i) => (
                    <li key={i} style={{
                      padding: '0.8rem 0',
                      borderBottom: i < 4 ? '1px solid rgba(0, 0, 0, 0.05)' : 'none',
                      display: 'flex',
                      alignItems: 'center',
                      color: '#666'
                    }}>
                      <span style={{ marginRight: '0.8rem', fontSize: '1.2rem' }}>✅</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" style={{
          padding: '6rem 5%',
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)'
        }}>
          <h2 style={{ fontSize: '2.5rem', fontWeight: 700, textAlign: 'center', marginBottom: '3rem', color: '#1a1a1a' }}>
            Why PaperFlow?
          </h2>
          <div style={{
            maxWidth: 1200,
            margin: '0 auto',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '2rem'
          }}>
            {[
              { icon: '🔗', title: 'Inline Everything', desc: 'Click citations, figures, tables, and references to view them instantly—without losing your place. No more scroll-back hell.' },
              { icon: '✍️', title: 'Smart Knowledge Capture', desc: 'Highlight text and export to Markdown. Copy with auto-citations for Slack, Discord, and email. Build your knowledge base effortlessly.' },
              { icon: '🌐', title: 'Share & Collaborate', desc: 'Every paper gets a clean, shareable link. Mobile-friendly reading on any device. Perfect for teams and study groups.' }
            ].map((feature, i) => (
              <div key={i} style={{
                padding: '2rem',
                background: 'white',
                borderRadius: '16px',
                border: '1px solid rgba(0, 0, 0, 0.05)',
                transition: 'transform 0.3s, box-shadow 0.3s'
              }}>
                <div style={{
                  width: '50px',
                  height: '50px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '1.5rem',
                  fontSize: '1.5rem'
                }}>
                  {feature.icon}
                </div>
                <h3 style={{ fontSize: '1.3rem', marginBottom: '0.8rem', color: '#1a1a1a' }}>{feature.title}</h3>
                <p style={{ color: '#666', lineHeight: 1.7 }}>{feature.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* How it Works */}
        <section id="how-it-works" style={{ padding: '6rem 5%', background: 'white' }}>
          <h2 style={{ fontSize: '2.5rem', fontWeight: 700, textAlign: 'center', marginBottom: '3rem', color: '#1a1a1a' }}>
            How it works
          </h2>
          <div style={{
            maxWidth: 1000,
            margin: '0 auto',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '3rem'
          }}>
            {[
              { num: '1', title: 'Upload a PDF', desc: 'Drop your academic paper and we\'ll start processing immediately.' },
              { num: '2', title: 'We convert it', desc: 'Our AI transforms your PDF into a structured, mobile-friendly reading page.' },
              { num: '3', title: 'Tap inline links', desc: 'Click citations, figures, and references to view them without scrolling.' }
            ].map((step, i) => (
              <div key={i} style={{ textAlign: 'center' }}>
                <div style={{
                  width: '60px',
                  height: '60px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1.5rem',
                  fontSize: '1.5rem',
                  fontWeight: 700
                }}>
                  {step.num}
                </div>
                <h3 style={{ fontSize: '1.3rem', marginBottom: '0.8rem', color: '#1a1a1a' }}>{step.title}</h3>
                <p style={{ color: '#666', lineHeight: 1.7 }}>{step.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* FAQ */}
        <section id="faq" style={{ padding: '6rem 5%', maxWidth: 900, margin: '0 auto' }}>
          <h2 style={{ fontSize: '2.5rem', fontWeight: 700, textAlign: 'center', marginBottom: '3rem', color: '#1a1a1a' }}>
            FAQ
          </h2>
          {[
            { q: 'Does it support scanned PDFs?', a: 'Some work better than others. If parsing fails, you\'ll see an error and can retry.' },
            { q: 'Do you store my files?', a: 'We store converted papers to enable shareable links. Original PDFs are processed and discarded. You can request deletion anytime at contact@paperflow.app.' },
            { q: 'Pricing?', a: 'Free during beta. We\'re collecting feedback to shape the paid plan.' }
          ].map((faq, i) => (
            <div key={i} style={{
              marginBottom: '1.5rem',
              background: 'white',
              borderRadius: '12px',
              overflow: 'hidden',
              border: '1px solid rgba(0, 0, 0, 0.05)'
            }}>
              <div style={{
                padding: '1.5rem',
                fontWeight: 600,
                color: '#1a1a1a',
                cursor: 'pointer'
              }}>
                {faq.q}
              </div>
              <div style={{
                padding: '0 1.5rem 1.5rem',
                color: '#666',
                lineHeight: 1.7
              }}>
                {faq.a}
              </div>
            </div>
          ))}
        </section>

        {/* Footer */}
        <footer style={{
          padding: '3rem 5%',
          textAlign: 'center',
          background: '#1a1a1a',
          color: 'white'
        }}>
          <p>&copy; 2026 PaperFlow. All rights reserved.</p>
          <div style={{ marginTop: '1rem' }}>
            <a href="/privacy" style={{ color: '#667eea', textDecoration: 'none', margin: '0 1rem' }}>Privacy</a>
            <a href="/terms" style={{ color: '#667eea', textDecoration: 'none', margin: '0 1rem' }}>Terms</a>
            <a href="mailto:contact@paperflow.app" style={{ color: '#667eea', textDecoration: 'none', margin: '0 1rem' }}>Contact</a>
          </div>
        </footer>
      </main>
    </>
  )
}
