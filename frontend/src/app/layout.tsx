import type { Metadata } from 'next'
import { Source_Serif_4, Noto_Serif_SC, Fraunces, DM_Sans } from 'next/font/google'
import 'katex/dist/katex.min.css'
import './globals.css'
import AnalyticsProvider from '@/components/AnalyticsProvider'

const sourceSerif = Source_Serif_4({ subsets: ['latin'], variable: '--font-serif', display: 'swap' })
const notoSerifSC = Noto_Serif_SC({ subsets: ['latin'], weight: ['400', '700'], variable: '--font-serif-sc', display: 'swap' })
const fraunces = Fraunces({ subsets: ['latin'], weight: ['300', '600', '800'], style: ['normal', 'italic'], variable: '--font-fraunces', display: 'swap' })
const dmSans = DM_Sans({ subsets: ['latin'], weight: ['300', '400', '500', '600'], variable: '--font-dm-sans', display: 'swap' })

export const metadata: Metadata = {
  title: 'PaperFlow — Read papers, not PDFs',
  description: 'Transform academic PDFs into beautiful, readable articles',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sourceSerif.variable} ${notoSerifSC.variable} ${fraunces.variable} ${dmSans.variable}`}>
      <body>
        <AnalyticsProvider>
          {children}
        </AnalyticsProvider>
      </body>
    </html>
  )
}
