import type { Metadata } from 'next'
import { Source_Serif_4, Noto_Serif_SC } from 'next/font/google'
import 'katex/dist/katex.min.css'
import './globals.css'

const sourceSerif = Source_Serif_4({ subsets: ['latin'], variable: '--font-serif', display: 'swap' })
const notoSerifSC = Noto_Serif_SC({ subsets: ['latin'], weight: ['400', '700'], variable: '--font-serif-sc', display: 'swap' })

export const metadata: Metadata = {
  title: 'PaperFlow — Read papers, not PDFs',
  description: 'Transform academic PDFs into beautiful, readable articles',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sourceSerif.variable} ${notoSerifSC.variable}`}>
      <body>{children}</body>
    </html>
  )
}
