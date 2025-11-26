import { Suspense } from 'react'
import { Metadata } from 'next'
import { notFound, redirect } from 'next/navigation'
import {
  getHomePageData,
  getFeaturedProducts,
  getUserPreferences
} from '@/lib/data-access'
import { HomePage } from '@/components/home-page'
import { HeroSection } from '@/components/sections/hero-section'
import { FeaturesSection } from '@/components/sections/features-section'
import { ProductsShowcase } from '@/components/sections/products-showcase'
import { LoadingProducts } from '@/components/ui/loading-products'
import { ErrorBoundary } from '@/components/error-boundary'

// SEO 元数据
export const metadata: Metadata = {
  title: '首页 - 现代前端应用 2025',
  description: '探索使用 React 19+ 和 Next.js 15+ 构建的现代前端应用，体验最新的 Server Components、Turbopack 和性能优化技术。',
  openGraph: {
    title: '首页 - 现代前端应用 2025',
    description: '探索使用 React 19+ 和 Next.js 15+ 构建的现代前端应用',
    images: [
      {
        url: '/og-home.png',
        width: 1200,
        height: 630,
        alt: 'Modern Frontend 2025 Home',
      },
    ],
  },
}

// 服务器组件数据获取
async function getServerSideData() {
  try {
    // 并行数据获取以提高性能
    const [pageData, featuredProducts, userPrefs] = await Promise.all([
      getHomePageData({
        cache: 'force-cache',
        next: { revalidate: 3600, tags: ['homepage'] }
      }),
      getFeaturedProducts({
        cache: 'no-store', // 每次请求获取最新数据
        next: { tags: ['products'] }
      }),
      getUserPreferences().catch(() => null) // 用户偏好获取失败不影响页面
    ])

    return {
      pageData,
      featuredProducts,
      userPrefs
    }
  } catch (error) {
    console.error('Server-side data fetch error:', error)

    // 失败时的降级策略
    return {
      pageData: {
        hero: {
          title: '现代前端开发',
          subtitle: '基于 React 19+ 和 Next.js 15+'
        }
      },
      featuredProducts: [],
      userPrefs: null
    }
  }
}

// 首页组件
export default async function Home() {
  const data = await getServerSideData()
  const { pageData, featuredProducts, userPrefs } = data

  // 根据用户偏好重定向（如果存在）
  if (userPrefs?.preferredLanguage && userPrefs.preferredLanguage !== 'zh-CN') {
    redirect(`/${userPrefs.preferredLanguage}`)
  }

  return (
    <main className="flex-1">
      {/* 英雄区域 - 完全服务器渲染 */}
      <HeroSection data={pageData.hero} />

      {/* 特性展示 - 流式渲染 */}
      <section className="py-20">
        <Suspense
          fallback={
            <div className="container mx-auto px-4">
              <div className="animate-pulse">
                <div className="h-8 bg-gray-200 rounded w-1/3 mb-8"></div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-64 bg-gray-200 rounded"></div>
                  ))}
                </div>
              </div>
            </div>
          }
        >
          <FeaturesSection />
        </Suspense>
      </section>

      {/* 产品展示 - 支持流式更新 */}
      <section className="py-20 bg-gray-50">
        <ErrorBoundary fallback={<ProductsErrorFallback />}>
          <Suspense fallback={<LoadingProducts count={6} />}>
            <ProductsShowcase
              products={featuredProducts}
              initialLimit={userPrefs?.displayPreferences?.itemsPerPage || 6}
            />
          </Suspense>
        </ErrorBoundary>
      </section>

      {/* 客户端增强的交互组件 */}
      <section className="py-20">
        <Suspense
          fallback={
            <div className="container mx-auto px-4">
              <div className="h-96 bg-gray-200 rounded animate-pulse"></div>
            </div>
          }
        >
          <HomePage
            serverData={pageData}
            userPreferences={userPrefs}
          />
        </Suspense>
      </section>
    </main>
  )
}

// 生成静态参数（如果使用动态路由）
export async function generateStaticParams() {
  return []
}

// 产品区域错误回退
function ProductsErrorFallback() {
  return (
    <section className="py-20">
      <div className="container mx-auto px-4 text-center">
        <h2 className="text-2xl font-bold mb-4">产品展示暂时不可用</h2>
        <p className="text-gray-600">请稍后重试，或浏览其他内容</p>
      </div>
    </section>
  )
}