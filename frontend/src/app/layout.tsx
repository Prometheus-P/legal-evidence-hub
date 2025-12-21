/**
 * Root Layout
 * Plan 3.19.2 - SEO Optimization
 *
 * Features:
 * - SEO metadata configuration
 * - Font optimization with Pretendard
 * - Global styles
 */

import type { Metadata } from 'next';
import { Toaster } from 'react-hot-toast';
import './globals.css';
import Footer from '@/components/common/Footer';
import { AppProviders } from './providers';
import { BRAND } from '@/config/brand';

const APP_BASE_URL =
  process.env.NEXT_PUBLIC_APP_BASE_URL ||
  process.env.NEXT_PUBLIC_SITE_URL ||
  'https://legalevidence.hub';

export const metadata: Metadata = {
  metadataBase: new URL(APP_BASE_URL),
  icons: {
    icon: '/logo.svg',
    apple: '/logo.svg',
  },
  title: `${BRAND.fullName} - AI 이혼 소송 증거 분석 솔루션`,
  description:
    'AI 기반 이혼 소송 증거 자동 분석 및 답변서 초안 생성 서비스. 증거 정리 시간 90% 단축, 14일 무료 체험.',
  keywords: [
    '이혼소송',
    '증거분석',
    'AI법률',
    '답변서',
    '법률문서',
    '이혼변호사',
    '증거관리',
    '소송지원',
  ],
  authors: [{ name: BRAND.name }],
  openGraph: {
    title: `${BRAND.fullName} - AI 이혼 소송 증거 분석`,
    description: '증거 정리 시간 90% 단축. AI가 이혼 소송 증거를 자동 분석하고 초안을 작성합니다.',
    url: APP_BASE_URL,
    siteName: BRAND.name,
    locale: 'ko_KR',
    type: 'website',
    images: [
      {
        url: `${APP_BASE_URL}/images/og-image.png`,
        width: 1200,
        height: 630,
        alt: `${BRAND.fullName} - AI 이혼 소송 증거 분석`,
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: `${BRAND.fullName} - AI 이혼 소송 증거 분석`,
    description: '증거 정리 시간 90% 단축. AI가 이혼 소송 증거를 자동 분석하고 초안을 작성합니다.',
    images: [`${APP_BASE_URL}/images/twitter-image.png`],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'google-site-verification-code',
    // yandex: 'yandex-verification-code',
    // yahoo: 'yahoo-verification-code',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <head>
        {/* Dark mode disabled - ensure light mode only */}
        {/* Structured Data - Organization */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'Organization',
              name: BRAND.name,
              alternateName: BRAND.nameKo,
              url: APP_BASE_URL,
              logo: `${APP_BASE_URL}/logo.svg`,
              description:
                'AI 기반 이혼 소송 증거 자동 분석 및 답변서 초안 생성 서비스',
              address: {
                '@type': 'PostalAddress',
                addressCountry: 'KR',
                addressLocality: '서울특별시',
                addressRegion: '강남구',
                streetAddress: '테헤란로 123, 10층',
              },
              contactPoint: {
                '@type': 'ContactPoint',
                telephone: '+82-2-1234-5678',
                contactType: 'customer service',
                email: 'contact@legalevidence.hub',
                availableLanguage: 'Korean',
              },
              sameAs: [
                'https://twitter.com/legalevhub',
                'https://linkedin.com/company/legalevhub',
                'https://github.com/legalevhub',
              ],
            }),
          }}
        />
        {/* Structured Data - Product */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'Product',
              name: BRAND.name,
              description:
                'AI 기반 이혼 소송 증거 자동 분석 및 답변서 초안 생성 서비스',
              brand: {
                '@type': 'Brand',
                name: BRAND.name,
              },
              offers: {
                '@type': 'AggregateOffer',
                priceCurrency: 'KRW',
                lowPrice: '49000',
                highPrice: '199000',
                offerCount: '3',
              },
              aggregateRating: {
                '@type': 'AggregateRating',
                ratingValue: '5.0',
                reviewCount: '50',
              },
            }),
          }}
        />
      </head>
      <body className="font-pretendard antialiased">
        <AppProviders>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#22c55e',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
          <div className="flex flex-col min-h-screen">
            <main className="flex-grow">{children}</main>
            <Footer />
          </div>
        </AppProviders>
      </body>
    </html>
  );
}
