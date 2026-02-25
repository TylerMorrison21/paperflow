'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import UploadZone from '@/components/UploadZone'
import { analytics } from '@/lib/analytics'

export default function Home() {
  const router = useRouter()
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  useEffect(() => {
    analytics.visitHome()
  }, [])

  return (
    <>
      <style jsx>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;0,9..144,800;1,9..144,300&family=DM+Sans:wght@300;400;500;600&display=swap');

        :root {
          --ink: #0f0e17;
          --ink-muted: #6b6880;
          --ink-faint: #c4c2d0;
          --paper: #faf9f7;
          --white: #ffffff;
          --accent: #5b4cf5;
          --accent-light: #ede9ff;
          --accent-mid: #8b7ff5;
          --danger: #e8614d;
          --success: #2ec4a0;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
      `}</style>

      {/* Header */}
      <header style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        padding: '0 5%',
        height: '68px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'rgba(250,249,247,0.88)',
        backdropFilter: 'blur(16px) saturate(180%)',
        borderBottom: '1px solid rgba(15,14,23,0.08)'
      }}>
        <a href="#" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          fontFamily: "'Fraunces', serif",
          fontSize: '1.35rem',
          fontWeight: 600,
          color: 'var(--ink)',
          textDecoration: 'none',
          letterSpacing: '-0.02em'
        }}>
          <div style={{
            width: '34px',
            height: '34px',
            background: 'linear-gradient(135deg, #5b4cf5 0%, #9b8af4 100%)',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0
          }}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 3h8l4 4v10a1 1 0 01-1 1H4a1 1 0 01-1-1V4a1 1 0 011-1z" fill="rgba(255,255,255,0.25)" stroke="white" strokeWidth="1.2"/>
              <path d="M12 3v4h4" stroke="white" strokeWidth="1.2" strokeLinecap="round"/>
              <path d="M6 10h8M6 13h5" stroke="white" strokeWidth="1.2" strokeLinecap="round"/>
            </svg>
          </div>
          PaperFlow
        </a>
        <nav style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
          <a href="#features" style={{
            padding: '0.45rem 1rem',
            textDecoration: 'none',
            color: 'var(--ink-muted)',
            fontSize: '0.9rem',
            fontWeight: 500,
            borderRadius: '8px',
            transition: 'color 0.24s, background 0.24s'
          }}>Features</a>
          <a href="#how-it-works" style={{
            padding: '0.45rem 1rem',
            textDecoration: 'none',
            color: 'var(--ink-muted)',
            fontSize: '0.9rem',
            fontWeight: 500,
            borderRadius: '8px',
            transition: 'color 0.24s, background 0.24s'
          }}>How it works</a>
          <a href="#faq" style={{
            padding: '0.45rem 1rem',
            textDecoration: 'none',
            color: 'var(--ink-muted)',
            fontSize: '0.9rem',
            fontWeight: 500,
            borderRadius: '8px',
            transition: 'color 0.24s, background 0.24s'
          }}>FAQ</a>
        </nav>
      </header>

      {/* Banner */}
      <div style={{
        marginTop: '68px',
        padding: '0.6rem 5%',
        background: 'var(--accent-light)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        fontSize: '0.83rem',
        color: 'var(--accent)',
        fontWeight: 500
      }}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>
        </svg>
        <span>Private & secure — we never use your data to train AI</span>
      </div>

      <main style={{ fontFamily: "'DM Sans', sans-serif" }}>
        {/* Hero Section */}
        <section style={{
          padding: '7rem 5% 5rem',
          textAlign: 'center',
          position: 'relative',
          overflow: 'hidden'
        }}>
          <div style={{
            content: '',
            position: 'absolute',
            top: '-200px',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '900px',
            height: '600px',
            background: 'radial-gradient(ellipse at center, rgba(91,76,245,0.12) 0%, transparent 70%)',
            pointerEvents: 'none'
          }} />

          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '0.35rem 0.9rem',
            background: 'var(--white)',
            border: '1px solid rgba(15,14,23,0.08)',
            borderRadius: '100px',
            fontSize: '0.8rem',
            fontWeight: 500,
            color: 'var(--ink-muted)',
            marginBottom: '2rem',
            boxShadow: '0 1px 3px rgba(15,14,23,0.06), 0 4px 16px rgba(15,14,23,0.06)',
            position: 'relative'
          }}>
            <span style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              background: 'var(--success)',
              animation: 'pulse 2s infinite'
            }} />
            Free during beta
          </div>

          <h1 style={{
            fontFamily: "'Fraunces', serif",
            fontSize: 'clamp(2.8rem, 6vw, 4.8rem)',
            fontWeight: 800,
            lineHeight: 1.08,
            letterSpacing: '-0.04em',
            marginBottom: '1.5rem',
            color: 'var(--ink)',
            position: 'relative'
          }}>
            Read papers without<br />scroll-back hell.
          </h1>

          <p style={{
            fontSize: '1.15rem',
            color: 'var(--ink-muted)',
            maxWidth: '600px',
            margin: '0 auto 1rem',
            lineHeight: 1.75,
            fontWeight: 400,
            position: 'relative'
          }}>
            Click any figure, table, or citation inline — keep your place, keep context. Turn any academic PDF into a clean, shareable reading link.
          </p>

          <p style={{
            fontSize: '0.85rem',
            color: 'var(--ink-faint)',
            marginBottom: '3rem',
            position: 'relative'
          }}>
            Built for researchers, students, and anyone who reads papers on their phone.
          </p>

          <div style={{
            maxWidth: '560px',
            margin: '0 auto',
            background: 'var(--white)',
            borderRadius: '24px',
            boxShadow: '0 8px 40px rgba(15,14,23,0.12), 0 32px 80px rgba(15,14,23,0.1)',
            padding: '2.5rem',
            border: '1px solid rgba(15,14,23,0.08)',
            position: 'relative'
          }}>
            <UploadZone onComplete={id => router.push(`/read/${id}`)} />

            <div style={{
              marginTop: '1.75rem',
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '0.65rem'
            }}>
              {[
                { icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>, text: 'Click citations & figures inline' },
                { icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>, text: 'Highlight & export to Markdown' },
                { icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>, text: 'Copy with auto-citation' },
                { icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>, text: 'Shareable link per paper' }
              ].map((perk, i) => (
                <div key={i} style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '8px',
                  textAlign: 'left',
                  fontSize: '0.82rem',
                  color: 'var(--ink-muted)',
                  lineHeight: 1.4
                }}>
                  <div style={{ flexShrink: 0, marginTop: '1px', color: 'var(--accent)' }}>
                    {perk.icon}
                  </div>
                  {perk.text}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Comparison Section */}
        <section style={{ padding: '6rem 5%', background: 'var(--white)' }}>
          <p style={{
            textAlign: 'center',
            fontSize: '0.75rem',
            fontWeight: 600,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: 'var(--accent)',
            marginBottom: '1rem'
          }}>The difference</p>
          <h2 style={{
            fontFamily: "'Fraunces', serif",
            fontSize: 'clamp(1.8rem, 4vw, 2.8rem)',
            fontWeight: 700,
            letterSpacing: '-0.03em',
            textAlign: 'center',
            color: 'var(--ink)',
            marginBottom: '3.5rem',
            lineHeight: 1.2
          }}>From chaos to clarity</h2>

          <div style={{
            maxWidth: '1100px',
            margin: '0 auto',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '2rem'
          }}>
            {/* Before */}
            <div style={{
              borderRadius: '20px',
              overflow: 'hidden',
              border: '1.5px solid rgba(15,14,23,0.08)',
              background: 'var(--white)'
            }}>
              <div style={{
                padding: '1.1rem 1.75rem',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                fontWeight: 600,
                fontSize: '0.95rem',
                background: '#fff5f5',
                color: 'var(--danger)'
              }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                Regular PDF Reader
              </div>
              <div style={{ margin: '1.25rem 1.25rem 0', height: '220px', borderRadius: '10px', overflow: 'hidden', position: 'relative' }}>
                <div style={{ background: '#f5f4f0', height: '100%', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {[100, 78, 92, 55, 100, 78, 92, 100, 55, 78, 100, 92].map((width, i) => (
                    <div key={i} style={{
                      height: '8px',
                      borderRadius: '4px',
                      background: 'linear-gradient(90deg, #d8d5cc 0%, #e8e5dc 100%)',
                      width: `${width}%`
                    }} />
                  ))}
                </div>
                <div style={{ position: 'absolute', right: '6px', top: 0, bottom: 0, width: '4px', background: '#ddd', borderRadius: '2px' }}>
                  <div style={{ width: '4px', height: '30px', background: '#bbb', borderRadius: '2px', position: 'absolute', top: '60%' }} />
                </div>
              </div>
              <div style={{ padding: '1.25rem 1.75rem 1.5rem' }}>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 0 }}>
                  {[
                    'Scroll endlessly to check references',
                    'Lose your place constantly',
                    'Figures buried pages away',
                    'Poor mobile reading experience'
                  ].map((item, i) => (
                    <li key={i} style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      padding: '0.65rem 0',
                      borderBottom: i < 3 ? '1px solid rgba(15,14,23,0.08)' : 'none',
                      fontSize: '0.875rem',
                      color: 'var(--ink-muted)'
                    }}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#e8614d" strokeWidth="2.5" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* After */}
            <div style={{
              borderRadius: '20px',
              overflow: 'hidden',
              border: '1.5px solid var(--accent)',
              background: 'var(--white)',
              boxShadow: '0 0 0 3px rgba(91,76,245,0.08), 0 4px 20px rgba(15,14,23,0.08), 0 16px 48px rgba(15,14,23,0.08)'
            }}>
              <div style={{
                padding: '1.1rem 1.75rem',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                fontWeight: 600,
                fontSize: '0.95rem',
                background: 'var(--accent-light)',
                color: 'var(--accent)'
              }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                PaperFlow
              </div>
              <div style={{ margin: '1.25rem 1.25rem 0', height: '220px', borderRadius: '10px', overflow: 'hidden', position: 'relative' }}>
                <div style={{ background: '#f8f7ff', height: '100%', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {[100, 78, 92, 55, 100].map((width, i) => (
                    <div key={i} style={{
                      height: '8px',
                      borderRadius: '4px',
                      background: 'linear-gradient(90deg, #c4bbf8 0%, #ddd8fc 100%)',
                      width: `${width}%`
                    }} />
                  ))}
                </div>
                <div style={{
                  position: 'absolute',
                  bottom: '12px',
                  right: '12px',
                  width: '160px',
                  background: 'white',
                  borderRadius: '8px',
                  padding: '0.6rem 0.8rem',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
                  border: '1px solid rgba(15,14,23,0.08)',
                  fontSize: '0.7rem',
                  color: 'var(--ink)'
                }}>
                  <div style={{ color: 'var(--accent)', fontWeight: 600, marginBottom: '2px' }}>[12] Smith et al.</div>
                  {[90, 70, 80].map((width, i) => (
                    <div key={i} style={{ height: '5px', borderRadius: '3px', background: '#eee', margin: '2px 0', width: `${width}%` }} />
                  ))}
                </div>
              </div>
              <div style={{ padding: '1.25rem 1.75rem 1.5rem' }}>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 0 }}>
                  {[
                    'Click any citation to view inline',
                    'Never lose your reading position',
                    'Figures & tables appear instantly',
                    'Perfect mobile reading experience'
                  ].map((item, i) => (
                    <li key={i} style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      padding: '0.65rem 0',
                      borderBottom: i < 3 ? '1px solid rgba(15,14,23,0.08)' : 'none',
                      fontSize: '0.875rem',
                      color: 'var(--ink-muted)'
                    }}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2ec4a0" strokeWidth="2.5" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" style={{ padding: '6rem 5%', maxWidth: '1200px', margin: '0 auto' }}>
          <p style={{
            textAlign: 'center',
            fontSize: '0.75rem',
            fontWeight: 600,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: 'var(--accent)',
            marginBottom: '1rem'
          }}>Features</p>
          <h2 style={{
            fontFamily: "'Fraunces', serif",
            fontSize: 'clamp(1.8rem, 4vw, 2.8rem)',
            fontWeight: 700,
            letterSpacing: '-0.03em',
            textAlign: 'center',
            color: 'var(--ink)',
            marginBottom: '3.5rem',
            lineHeight: 1.2
          }}>Everything you need to<br />actually understand a paper</h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1.5rem',
            marginTop: '3.5rem'
          }}>
            {[
              {
                icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>,
                title: 'Inline Everything',
                desc: 'Click citations, figures, and tables to expand them right where you are. No jumping, no scrolling, no lost context.'
              },
              {
                icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>,
                title: 'Smart Knowledge Capture',
                desc: 'Highlight text and export instantly to Markdown. Copy with auto-generated citations — perfect for Slack, Notion, or your notes app.'
              },
              {
                icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>,
                title: 'Share & Collaborate',
                desc: 'Every paper gets a clean shareable link. Send it to a teammate or study group — they get the same seamless reading experience.'
              }
            ].map((feature, i) => (
              <div key={i} style={{
                padding: '2rem',
                background: 'var(--white)',
                borderRadius: '16px',
                border: '1px solid rgba(15,14,23,0.08)',
                transition: 'transform 0.24s, box-shadow 0.24s'
              }}>
                <div style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '1.25rem',
                  background: 'var(--accent-light)',
                  color: 'var(--accent)'
                }}>
                  {feature.icon}
                </div>
                <h3 style={{
                  fontFamily: "'Fraunces', serif",
                  fontSize: '1.15rem',
                  fontWeight: 600,
                  marginBottom: '0.6rem',
                  color: 'var(--ink)',
                  letterSpacing: '-0.02em'
                }}>{feature.title}</h3>
                <p style={{ fontSize: '0.9rem', color: 'var(--ink-muted)', lineHeight: 1.7 }}>{feature.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* How it Works */}
        <section id="how-it-works" style={{ padding: '6rem 5%', background: 'var(--ink)', color: 'white' }}>
          <p style={{
            textAlign: 'center',
            fontSize: '0.75rem',
            fontWeight: 600,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: 'var(--accent-mid)',
            marginBottom: '1rem'
          }}>How it works</p>
          <h2 style={{
            fontFamily: "'Fraunces', serif",
            fontSize: 'clamp(1.8rem, 4vw, 2.8rem)',
            fontWeight: 700,
            letterSpacing: '-0.03em',
            textAlign: 'center',
            color: 'white',
            marginBottom: '3.5rem',
            lineHeight: 1.2
          }}>Three steps to clarity</h2>

          <div style={{
            maxWidth: '900px',
            margin: '0 auto',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '2rem',
            position: 'relative'
          }}>
            {[
              { num: '1', title: 'Upload a PDF', desc: 'Drop your academic paper. We start processing it immediately — no sign-up required.' },
              { num: '2', title: 'We convert it', desc: 'Our AI extracts structure, links citations, figures, and tables into a clean reading page.' },
              { num: '3', title: 'Read without friction', desc: 'Tap any citation or figure inline. Share your link. Highlight & export what matters.' }
            ].map((step, i) => (
              <div key={i} style={{ textAlign: 'center', position: 'relative' }}>
                <div style={{
                  width: '56px',
                  height: '56px',
                  border: '1px solid rgba(255,255,255,0.15)',
                  background: 'rgba(255,255,255,0.05)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1.5rem',
                  fontFamily: "'Fraunces', serif",
                  fontSize: '1.4rem',
                  fontWeight: 700,
                  color: 'var(--accent-mid)',
                  position: 'relative',
                  zIndex: 1
                }}>
                  {step.num}
                </div>
                <h3 style={{
                  fontFamily: "'Fraunces', serif",
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  color: 'white',
                  marginBottom: '0.6rem',
                  letterSpacing: '-0.02em'
                }}>{step.title}</h3>
                <p style={{ fontSize: '0.88rem', color: 'rgba(255,255,255,0.5)', lineHeight: 1.7 }}>{step.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* FAQ */}
        <section id="faq" style={{ padding: '6rem 5%', maxWidth: '780px', margin: '0 auto' }}>
          <p style={{
            textAlign: 'center',
            fontSize: '0.75rem',
            fontWeight: 600,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: 'var(--accent)',
            marginBottom: '1rem'
          }}>FAQ</p>
          <h2 style={{
            fontFamily: "'Fraunces', serif",
            fontSize: 'clamp(1.8rem, 4vw, 2.8rem)',
            fontWeight: 700,
            letterSpacing: '-0.03em',
            textAlign: 'center',
            color: 'var(--ink)',
            marginBottom: '3.5rem',
            lineHeight: 1.2
          }}>Common questions</h2>

          {[
            { q: 'Does it support scanned PDFs?', a: 'Most scanned PDFs work with our OCR pipeline. Some older or low-resolution scans may have reduced accuracy. If parsing fails, you\'ll see a clear error message and can retry or contact us.' },
            { q: 'Do you store my files?', a: 'We store converted papers to enable shareable links. Original PDFs are processed and then discarded. You can request full deletion at any time by emailing contact@paperflow.app.' },
            { q: 'What does it cost?', a: 'Free during beta — no credit card required. We\'re collecting feedback to shape our pricing model. Early users will receive a discount when paid plans launch.' },
            { q: 'Which paper formats are supported?', a: 'We support any PDF, with best results on academic papers from arXiv, IEEE, ACM, Nature, and similar publishers. Papers with standard two-column layouts convert especially well.' }
          ].map((faq, i) => (
            <div key={i} style={{ borderBottom: '1px solid rgba(15,14,23,0.08)' }}>
              <div
                onClick={() => setOpenFaq(openFaq === i ? null : i)}
                style={{
                  padding: '1.4rem 0',
                  fontWeight: 500,
                  fontSize: '1rem',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  color: 'var(--ink)',
                  transition: 'color 0.24s',
                  userSelect: 'none'
                }}
              >
                {faq.q}
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{
                    color: openFaq === i ? 'var(--accent)' : 'var(--ink-faint)',
                    transform: openFaq === i ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: 'transform 0.24s, color 0.24s',
                    flexShrink: 0
                  }}
                >
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </div>
              <div style={{
                maxHeight: openFaq === i ? '200px' : '0',
                overflow: 'hidden',
                transition: 'max-height 0.35s ease, padding 0.2s ease',
                fontSize: '0.92rem',
                color: 'var(--ink-muted)',
                lineHeight: 1.75,
                paddingBottom: openFaq === i ? '1.25rem' : '0'
              }}>
                {faq.a}
              </div>
            </div>
          ))}
        </section>

        {/* Footer */}
        <footer style={{
          padding: '2.5rem 5%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderTop: '1px solid rgba(15,14,23,0.08)',
          fontSize: '0.85rem',
          color: 'var(--ink-muted)',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <a href="#" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontFamily: "'Fraunces', serif",
            fontSize: '1.1rem',
            fontWeight: 600,
            color: 'var(--ink)',
            textDecoration: 'none',
            letterSpacing: '-0.02em'
          }}>
            <div style={{
              width: '28px',
              height: '28px',
              background: 'linear-gradient(135deg, #5b4cf5 0%, #9b8af4 100%)',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <svg width="16" height="16" viewBox="0 0 20 20" fill="none">
                <path d="M4 3h8l4 4v10a1 1 0 01-1 1H4a1 1 0 01-1-1V4a1 1 0 011-1z" fill="rgba(255,255,255,0.25)" stroke="white" strokeWidth="1.2"/>
                <path d="M12 3v4h4" stroke="white" strokeWidth="1.2" strokeLinecap="round"/>
                <path d="M6 10h8M6 13h5" stroke="white" strokeWidth="1.2" strokeLinecap="round"/>
              </svg>
            </div>
            PaperFlow
          </a>
          <div style={{ display: 'flex', gap: '1.5rem' }}>
            <a href="/privacy" style={{ color: 'var(--ink-muted)', textDecoration: 'none', transition: 'color 0.24s' }}>Privacy</a>
            <a href="/terms" style={{ color: 'var(--ink-muted)', textDecoration: 'none', transition: 'color 0.24s' }}>Terms</a>
            <a href="mailto:contact@paperflow.app" style={{ color: 'var(--ink-muted)', textDecoration: 'none', transition: 'color 0.24s' }}>Contact</a>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--ink-faint)' }}>&copy; 2026 PaperFlow</span>
        </footer>
      </main>
    </>
  )
}
