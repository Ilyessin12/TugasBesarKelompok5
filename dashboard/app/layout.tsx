import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Big data kelompok 5',
  description: 'Hafidh, Lyan, Eghis, Varrell, Ichsan',
  generator: 'Kelompok 5',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
