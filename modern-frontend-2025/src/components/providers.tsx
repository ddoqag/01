'use client'

import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { ThemeProvider } from 'next-themes'
import { Toaster } from 'sonner'
import { useEffect, useState } from 'react'
import { queryClient } from '@/lib/stores/user-store'
import { ErrorBoundary } from './error-boundary'

interface ProvidersProps {
  children: React.ReactNode
}

export function Providers({ children }: ProvidersProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)

    // 性能监控
    if (typeof window !== 'undefined') {
      // 监控页面加载性能
      const measurePageLoad = () => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
        const loadTime = navigation.loadEventEnd - navigation.loadEventStart

        if (loadTime > 3000) {
          console.warn(`Slow page load detected: ${loadTime}ms`)
        }
      }

      // 监控 Core Web Vitals
      const measureWebVitals = () => {
        if ('web-vitals' in window) {
          import('web-vitals').then(({ onCLS, onFID, onFCP, onLCP, onTTFB }) => {
            onCLS((metric) => {
              if (metric.value > 0.1) {
                console.warn(`CLS threshold exceeded: ${metric.value}`)
              }
            })

            onFID((metric) => {
              if (metric.value > 100) {
                console.warn(`FID threshold exceeded: ${metric.value}ms`)
              }
            })

            onFCP((metric) => {
              if (metric.value > 1800) {
                console.warn(`FCP threshold exceeded: ${metric.value}ms`)
              }
            })

            onLCP((metric) => {
              if (metric.value > 2500) {
                console.warn(`LCP threshold exceeded: ${metric.value}ms`)
              }
            })

            onTTFB((metric) => {
              if (metric.value > 800) {
                console.warn(`TTFB threshold exceeded: ${metric.value}ms`)
              }
            })
          })
        }
      }

      // 页面加载完成后执行测量
      if (document.readyState === 'complete') {
        measurePageLoad()
        measureWebVitals()
      } else {
        window.addEventListener('load', measurePageLoad)
        window.addEventListener('load', measureWebVitals)
      }

      // 监控长任务
      if ('PerformanceObserver' in window) {
        const observer = new PerformanceObserver((list) => {
          list.getEntries().forEach((entry) => {
            if (entry.duration > 50) {
              console.warn(`Long task detected: ${entry.duration}ms`, entry)
            }
          })
        })

        observer.observe({ entryTypes: ['longtask'] })
      }

      // 预加载关键资源
      const preloadCriticalResources = () => {
        const criticalResources = [
          { href: '/fonts/inter-var.woff2', as: 'font', type: 'font/woff2' },
        ]

        criticalResources.forEach(resource => {
          const link = document.createElement('link')
          link.rel = 'preload'
          link.href = resource.href
          link.as = resource.as
          if (resource.type) link.type = resource.type
          link.crossOrigin = 'anonymous'
          document.head.appendChild(link)
        })
      }

      preloadCriticalResources()
    }
  }, [])

  if (!mounted) {
    return null
  }

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange={false}
        >
          {children}

          <Toaster
            position="top-right"
            richColors
            closeButton
            expand
            visibleToasts={5}
            toastOptions={{
              classNames: {
                toast: 'group toast group-[.toaster]:bg-background group-[.toaster]:text-foreground group-[.toaster]:border-border group-[.toaster]:shadow-lg',
                description: 'group-[.toast]:text-muted-foreground',
                actionButton:
                  'group-[.toast]:bg-primary group-[.toast]:text-primary-foreground',
                cancelButton:
                  'group-[.toast]:bg-muted group-[.toast]:text-muted-foreground',
              },
            }}
          />

          {process.env.NODE_ENV === 'development' && (
            <ReactQueryDevtools
              initialIsOpen={false}
              buttonPosition="bottom-left"
            />
          )}
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}