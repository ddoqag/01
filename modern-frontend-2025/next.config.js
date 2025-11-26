/** @type {import('next').NextConfig} */
const bundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

const nextConfig = {
  // 启用 Turbopack（Next.js 15+ 默认）
  experimental: {
    turbopack: true,
    // 启用 React 编译器（实验性）
    reactCompiler: true,
    // 启用 PPR（Partial Prerendering）
    ppr: 'incremental',
    // 启用优化包导入
    optimizePackageImports: [
      'lucide-react',
      'date-fns',
      '@radix-ui/react-icons'
    ],
    // 启用静态生成优化
    staticWorkerRequestDeduping: true,
    // 启用服务器组件 HMR
    serverComponentsHmrCache: true,
  },

  // 图片优化配置
  images: {
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    domains: [],
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },

  // 编译配置
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // 实验性服务器操作
  experimental: {
    serverActions: {
      bodySizeLimit: '5mb',
    },
    webVitalsAttribution: ['CLS', 'LCP'],
  },

  // 压缩配置
  compress: true,

  // 强制静态生成
  output: 'standalone',

  // 头部配置
  headers: async () => [
    {
      source: '/(.*)',
      headers: [
        {
          key: 'X-Frame-Options',
          value: 'DENY',
        },
        {
          key: 'X-Content-Type-Options',
          value: 'nosniff',
        },
        {
          key: 'Referrer-Policy',
          value: 'origin-when-cross-origin',
        },
        {
          key: 'Permissions-Policy',
          value: 'camera=(), microphone=(), geolocation=()',
        },
      ],
    },
    {
      source: '/api/(.*)',
      headers: [
        {
          key: 'Cache-Control',
          value: 'public, max-age=60, s-maxage=60',
        },
      ],
    },
  ],

  // 重定向配置
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/',
        permanent: true,
      },
    ]
  },

  // 重写配置
  async rewrites() {
    return [
      {
        source: '/api/proxy/:path*',
        destination: `${process.env.API_BASE_URL}/:path*`,
      },
    ]
  },

  // Webpack 配置（用于高级优化）
  webpack: (config, { dev, isServer }) => {
    // 生产环境优化
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        minSize: 20000,
        maxSize: 244000,
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 10,
          },
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            priority: 5,
            reuseExistingChunk: true,
          },
        },
      }
    }

    // 解析别名
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': './src',
      '@/components': './src/components',
      '@/lib': './src/lib',
      '@/types': './src/types',
      '@/styles': './src/styles',
    }

    return config
  },

  // 环境变量
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },

  // 生成 etags
  generateEtags: true,

  // powered by header
  poweredByHeader: false,

  // React 严格模式
  reactStrictMode: true,

  // SWC 压缩
  swcMinify: true,

  // 页面扩展
  pageExtensions: ['ts', 'tsx', 'js', 'jsx'],

  // 实验性功能
  experimental: {
    // 优化 CSS
    optimizeCss: true,
    // 优化服务器组件
    optimizeServerReact: true,
    // 启用滚动条优化
    scrollRestoration: true,
  },
}

module.exports = bundleAnalyzer(nextConfig)