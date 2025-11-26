import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import { notFound } from 'next/navigation'
import { Suspense } from 'react'
import './globals.css'
import { cn } from '@/lib/utils'
import { Providers } from '@/components/providers'
import { Toaster } from '@/components/ui/toaster'
import { LoadingScreen } from '@/components/ui/loading-screen'
import { ErrorBoundary } from '@/components/error-boundary'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  fallback: ['system-ui', 'arial'],
  preload: true,
  variable: '--font-inter'
})

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'),
  title: {
    default: 'Modern Frontend 2025',
    template: '%s | Modern Frontend 2025'
  },
  description: 'A cutting-edge React 19+ and Next.js 15+ application showcasing modern frontend development practices.',
  keywords: ['React 19', 'Next.js 15', 'Server Components', 'TypeScript', 'Modern Frontend'],
  authors: [{ name: 'Frontend Team' }],
  creator: 'Frontend Team',
  publisher: 'Frontend Team',
  robots: {
    index: true,
    follow: true,
    nocache: true,
    googleBot: {
      index: true,
      follow: true,
      noimageindex: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'zh_CN',
    url: '/',
    siteName: 'Modern Frontend 2025',
    title: 'Modern Frontend 2025',
    description: 'A cutting-edge React 19+ and Next.js 15+ application',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Modern Frontend 2025',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Modern Frontend 2025',
    description: 'A cutting-edge React 19+ and Next.js 15+ application',
    images: ['/twitter-image.png'],
  },
  verification: {
    google: process.env.GOOGLE_SITE_VERIFICATION,
    yandex: process.env.YANDEX_VERIFICATION,
  },
  alternates: {
    canonical: '/',
    languages: {
      'zh-CN': '/zh-CN',
      'en-US': '/en-US',
    },
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
  colorScheme: 'light dark',
}

interface RootLayoutProps {
  children: React.ReactNode
  params: Promise<{ locale: string }>
}

// 服务器端布局数据获取
async function getLayoutData(locale: string) {
  try {
    // 模拟布局数据获取
    const data = await fetch(`${process.env.API_BASE_URL}/api/layout?locale=${locale}`, {
      cache: 'force-cache',
      next: {
        tags: ['layout'],
        revalidate: 3600 // 1小时重新验证
      }
    })

    if (!data.ok) {
      throw new Error('Failed to fetch layout data')
    }

    return data.json()
  } catch (error) {
    console.error('Layout data fetch error:', error)
    return null
  }
}

export default async function RootLayout({
  children,
  params,
}: RootLayoutProps) {
  const { locale } = await params
  const layoutData = await getLayoutData(locale)

  // 验证支持的 locale
  const supportedLocales = ['zh-CN', 'en-US', 'zh']
  if (!supportedLocales.includes(locale)) {
    notFound()
  }

  return (
    <html
      lang={locale}
      suppressHydrationWarning
      className={cn(
        inter.variable,
        'h-full scroll-smooth'
      )}
    >
      <head>
        {/* 预加载关键资源 */}
        <link
          rel="preload"
          href="/fonts/inter-var.woff2"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />

        {/* DNS 预解析外部域名 */}
        <link rel="dns-prefetch" href="//fonts.googleapis.com" />
        <link rel="dns-prefetch" href="//www.googletagmanager.com" />

        {/* 预连接到关键域 */}
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
      </head>

      <body
        className={cn(
          'min-h-screen bg-background font-sans antialiased',
          'selection:bg-primary selection:text-primary-foreground'
        )}
        suppressHydrationWarning
      >
        <ErrorBoundary>
          <Providers>
            <div className="relative flex min-h-screen flex-col">
              {/* 加载状态回退 */}
              <Suspense fallback={<LoadingScreen />}>
                {children}
              </Suspense>
            </div>

            {/* 全局通知组件 */}
            <Toaster />
          </Providers>
        </ErrorBoundary>

        {/* 性能监控脚本 */}
        {process.env.NODE_ENV === 'production' && (
          <script
            dangerouslySetInnerHTML={{
              __html: `
                // Web Vitals 监控
                if ('requestIdleCallback' in window) {
                  requestIdleCallback(() => {
                    // 延迟加载分析脚本
                    const script = document.createElement('script');
                    script.src = '/analytics.js';
                    script.async = true;
                    document.head.appendChild(script);
                  });
                }
              `,
            }}
          />
        )}
      </body>
    </html>
  )
}