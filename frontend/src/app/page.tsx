'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import UploadZone from '@/components/UploadZone'
import { analytics } from '@/lib/analytics'
import './landing.css'

export default function Home() {
  const router = useRouter()
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  useEffect(() => {
    analytics.visitHome()
  }, [])

  const toggleFaq = (index: number) => {
    setOpenFaq(openFaq === index ? null : index)
  }

  return (
    <>
      {/* Header */}
      <header className="landing-header">
        <a href="#" className="logo">
          <div className="logo-icon">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 3h8l4 4v10a1 1 0 01-1 1H4a1 1 0 01-1-1V4a1 1 0 011-1z" fill="rgba(255,255,255,0.25)" stroke="white" strokeWidth="1.2"/>
              <path d="M12 3v4h4" stroke="white" strokeWidth="1.2" strokeLinecap="round"/>
              <path d="M6 10h8M6 13h5" stroke="white" strokeWidth="1.2" strokeLinecap="round"/>
            </svg>
          </div>
          PaperFlow
        </a>
        <nav className="landing-nav">
          <a href="#features">Features</a>
          <a href="#how-it-works">How it works</a>
          <a href="#faq">FAQ</a>
        </nav>
      </header>

      {/* Banner */}
      <div className="banner">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>
        </svg>
        <span>Private &amp; secure — we never use your data to train AI</span>
      </div>

      {/* Hero */}
      <section className="hero">
        <div className="hero-badge">
          <span className="dot"></span>
          Free during beta
        </div>
        <h1>Read papers without<br/>scroll-back hell.</h1>
        <p className="hero-sub">Click any figure, table, or citation inline — keep your place, keep context. Turn any academic PDF into a clean, shareable reading link.</p>
        <p className="hero-hint">Built for researchers, students, and anyone who reads papers on their phone.</p>

        <div className="upload-card">
          <UploadZone onComplete={id => router.push(`/read/${id}`)} />

          <div className="upload-perks">
            <div className="perk">
              <svg className="perk-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
              </svg>
              Click citations &amp; figures inline
            </div>
            <div className="perk">
              <svg className="perk-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/>
              </svg>
              Highlight &amp; export to Markdown
            </div>
            <div className="perk">
              <svg className="perk-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
              </svg>
              Copy with auto-citation
            </div>
            <div className="perk">
              <svg className="perk-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
                <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
              </svg>
              Shareable link per paper
            </div>
          </div>
        </div>
      </section>

      {/* Comparison */}
      <section className="comparison">
        <p className="section-label">The difference</p>
        <h2 className="section-title">From chaos to clarity</h2>
        <div className="comparison-grid">
          {/* Before */}
          <div className="cmp-card before">
            <div className="cmp-head">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
              Regular PDF Reader
            </div>
            <div className="cmp-mock">
              <div className="mock-pdf">
                <div className="mock-line full"></div>
                <div className="mock-line mid"></div>
                <div className="mock-line long"></div>
                <div className="mock-line short"></div>
                <div className="mock-line full"></div>
                <div className="mock-line mid"></div>
                <div className="mock-line long"></div>
                <div className="mock-line full"></div>
                <div className="mock-line short"></div>
                <div className="mock-line mid"></div>
                <div className="mock-line full"></div>
                <div className="mock-line long"></div>
              </div>
              <div className="mock-scroll-indicator"><div className="mock-scroll-thumb"></div></div>
            </div>
            <div className="cmp-body">
              <ul className="cmp-list">
                <li>
                  <svg className="cmp-icon" viewBox="0 0 24 24" fill="none" stroke="#e8614d" strokeWidth="2.5" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  Scroll endlessly to check references
                </li>
                <li>
                  <svg className="cmp-icon" viewBox="0 0 24 24" fill="none" stroke="#e8614d" strokeWidth="2.5" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  Lose your place constantly
                </li>
                <li>
                  <svg className="cmp-icon" viewBox="0 0 24 24" fill="none" stroke="#e8614d" strokeWidth="2.5" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  Figures buried pages away
                </li>
                <li>
                  <svg className="cmp-icon" viewBox="0 0 24 24" fill="none" stroke="#e8614d" strokeWidth="2.5" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  Poor mobile reading experience
                </li>
              </ul>
            </div>
          </div>

          {/* After */}
          <div className="cmp-card after">
            <div className="cmp-head">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              PaperFlow
            </div>
            <div className="cmp-mock">
              <div className="mock-pdf" style={{background:'#f8f7ff'}}>
                <div className="mock-line full" style={{background: 'linear-gradient(90deg, #c4bbf8 0%, #ddd8fc 100%)'}}></div>
                <div className="mock-line mid" style={{background: 'linear-gradient(90deg, #c4bbf8 0%, #ddd8fc 100%)'}}></div>
                <div className="mock-line long" style={{background: 'linear-gradient(90deg, #c4bbf8 0%, #ddd8fc 100%)'}}></div>
                <div className="mock-line short" style={{background: 'linear-gradient(90deg, #c4bbf8 0%, #ddd8fc 100%)'}}></div>
                <div className="mock-line full" style={{background: 'linear-gradient(90deg, #c4bbf8 0%, #ddd8fc 100%)'}}></div>
              </div>
              <div className="mock-ref-popup">
                <div className="mock-ref-tag">[12] Smith et al.</div>
                <div className="mock-ref-line" style={{width:'90%'}}></div>
                <div className="mock-ref-line" style={{width:'70%'}}></div>
                <div className="mock-ref-line" style={{width:'80%'}}></div>
              </div>
            </div>
            <div className="cmp-body">
              <ul className="cmp-list">
                <li>
                  <svg className="cmp-icon" viewBox="0 0 24 24" fill="none" stroke="#2ec4a0" strokeWidth="2.5" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                  Click any citation to view inline
                </li>
                <li>
                  <svg className="cmp-icon" viewBox="0 0 24 24" fill="none" stroke="#2ec4a0" strokeWidth="2.5" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                  Never lose your reading position
                </li>
                <li>
                  <svg className="cmp-icon" viewBox="0 0 24 24" fill="none" stroke="#2ec4a0" strokeWidth="2.5" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                  Figures &amp; tables appear instantly
                </li>
                <li>
                  <svg className="cmp-icon" viewBox="0 0 24 24" fill="none" stroke="#2ec4a0" strokeWidth="2.5" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                  Perfect mobile reading experience
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features" id="features">
        <p className="section-label">Features</p>
        <h2 className="section-title">Everything you need to<br/>actually understand a paper</h2>
        <div className="features-grid">
          <div className="feat-card">
            <div className="feat-icon-wrap">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
                <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
              </svg>
            </div>
            <h3>Inline Everything</h3>
            <p>Click citations, figures, and tables to expand them right where you are. No jumping, no scrolling, no lost context.</p>
          </div>
          <div className="feat-card">
            <div className="feat-icon-wrap">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/>
              </svg>
            </div>
            <h3>Smart Knowledge Capture</h3>
            <p>Highlight text and export instantly to Markdown. Copy with auto-generated citations — perfect for Slack, Notion, or your notes app.</p>
          </div>
          <div className="feat-card">
            <div className="feat-icon-wrap">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
                <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
                <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
              </svg>
            </div>
            <h3>Share &amp; Collaborate</h3>
            <p>Every paper gets a clean shareable link. Send it to a teammate or study group — they get the same seamless reading experience.</p>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="how-it-works" id="how-it-works">
        <p className="section-label">How it works</p>
        <h2 className="section-title">Three steps to clarity</h2>
        <div className="steps">
          <div className="step">
            <div className="step-num">1</div>
            <h3>Upload a PDF</h3>
            <p>Drop your academic paper. We start processing it immediately — no sign-up required.</p>
          </div>
          <div className="step">
            <div className="step-num">2</div>
            <h3>We convert it</h3>
            <p>Our AI extracts structure, links citations, figures, and tables into a clean reading page.</p>
          </div>
          <div className="step">
            <div className="step-num">3</div>
            <h3>Read without friction</h3>
            <p>Tap any citation or figure inline. Share your link. Highlight &amp; export what matters.</p>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="faq" id="faq">
        <p className="section-label">FAQ</p>
        <h2 className="section-title">Common questions</h2>

        <div className={`faq-item ${openFaq === 0 ? 'open' : ''}`}>
          <div className="faq-question" onClick={() => toggleFaq(0)}>
            Does it support scanned PDFs?
            <svg className="faq-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
          </div>
          <div className="faq-answer">Most scanned PDFs work with our OCR pipeline. Some older or low-resolution scans may have reduced accuracy. If parsing fails, you&apos;ll see a clear error message and can retry or contact us.</div>
        </div>

        <div className={`faq-item ${openFaq === 1 ? 'open' : ''}`}>
          <div className="faq-question" onClick={() => toggleFaq(1)}>
            Do you store my files?
            <svg className="faq-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
          </div>
          <div className="faq-answer">We store converted papers to enable shareable links. Original PDFs are processed and then discarded. You can request full deletion at any time by emailing contact@paperflow.app.</div>
        </div>

        <div className={`faq-item ${openFaq === 2 ? 'open' : ''}`}>
          <div className="faq-question" onClick={() => toggleFaq(2)}>
            What does it cost?
            <svg className="faq-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
          </div>
          <div className="faq-answer">Free during beta — no credit card required. We&apos;re collecting feedback to shape our pricing model. Early users will receive a discount when paid plans launch.</div>
        </div>

        <div className={`faq-item ${openFaq === 3 ? 'open' : ''}`}>
          <div className="faq-question" onClick={() => toggleFaq(3)}>
            Which paper formats are supported?
            <svg className="faq-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
          </div>
          <div className="faq-answer">We support any PDF, with best results on academic papers from arXiv, IEEE, ACM, Nature, and similar publishers. Papers with standard two-column layouts convert especially well.</div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <a href="#" className="logo" style={{WebkitTextFillColor: 'var(--ink)', color: 'var(--ink)', background: 'none'}}>
          <div className="logo-icon">
            <svg width="16" height="16" viewBox="0 0 20 20" fill="none">
              <path d="M4 3h8l4 4v10a1 1 0 01-1 1H4a1 1 0 01-1-1V4a1 1 0 011-1z" fill="rgba(255,255,255,0.25)" stroke="white" strokeWidth="1.2"/>
              <path d="M12 3v4h4" stroke="white" strokeWidth="1.2" strokeLinecap="round"/>
              <path d="M6 10h8M6 13h5" stroke="white" strokeWidth="1.2" strokeLinecap="round"/>
            </svg>
          </div>
          PaperFlow
        </a>
        <div className="footer-links">
          <a href="#">Privacy</a>
          <a href="#">Terms</a>
          <a href="mailto:contact@paperflow.app">Contact</a>
        </div>
        <span style={{fontSize:'0.8rem', color: 'var(--ink-faint)'}}>&copy; 2026 PaperFlow</span>
      </footer>
    </>
  )
}
