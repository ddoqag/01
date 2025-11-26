# Modern Frontend 2025 🚀

一个基于 **React 19+** 和 **Next.js 15+** 的现代化前端应用架构，展示了 2025 年最新的前端开发最佳实践。

## ✨ 核心特性

### 🚀 React 19+ 最新特性
- **React Server Components (RSC)**: 服务器端组件优化渲染性能
- **React Compiler**: 自动优化和编译时性能提升
- **useOptimistic & useActionState**: 内置乐观更新和状态管理钩子
- **并发渲染**: 提升应用响应性和用户体验
- **新的 Suspense 功能**: 更强大的数据获取和加载状态处理

### ⚡ Next.js 15+ 企业级特性
- **Turbopack**: 默认启用，闪电般的构建速度
- **App Router**: 现代化的路由系统
- **Server Actions**: 服务器端数据变更操作
- **Partial Prerendering (PPR)**: 增量预渲染优化
- **增强的图像优化**: 自动 WebP/AVIF 格式转换
- **中间件支持**: 路由级别的请求处理

### 🎨 现代状态管理
- **Zustand 5.0+**: 轻量级状态管理，支持 TypeScript
- **TanStack Query 5.0+**: 强大的服务器状态管理
- **Jotai 2.0+**: 原子化状态管理
- **React 19 内置状态管理**: 利用新的 React 钩子

### 🎯 性能优化策略
- **Core Web Vitals 优化**: LCP < 2.5s, FID < 100ms, CLS < 0.1
- **自动代码分割**: 路由级别和组件级别分割
- **图片懒加载**: Next.js Image 组件优化
- **Bundle 分析**: 实时监控包大小
- **Service Worker**: 离线支持和缓存策略

### 🛠️ TypeScript 5.5+ 集成
- **严格类型检查**: 全面的类型安全
- **新语法特性**: 装饰器、const 断言等
- **智能提示**: 完整的 IDE 支持
- **类型生成**: API 类型自动生成

## 📁 项目结构

```
modern-frontend-2025/
├── src/
│   ├── app/                    # Next.js 15 App Router
│   │   ├── (auth)/            # 认证路由组
│   │   ├── dashboard/         # 仪表板页面
│   │   ├── api/               # API 路由
│   │   ├── layout.tsx         # 根布局组件
│   │   ├── page.tsx           # 首页
│   │   └── globals.css        # 全局样式
│   ├── components/
│   │   ├── ui/                # 可复用 UI 组件
│   │   ├── forms/             # 表单组件
│   │   ├── charts/            # 图表组件
│   │   ├── layout/            # 布局组件
│   │   └── providers.tsx      # 应用提供者
│   ├── lib/
│   │   ├── hooks/             # 自定义 React 钩子
│   │   ├── stores/            # 状态管理
│   │   ├── utils.ts           # 工具函数
│   │   ├── data-access.ts     # 数据访问层
│   │   └── performance.ts     # 性能优化工具
│   ├── types/
│   │   ├── index.ts           # 通用类型定义
│   │   ├── api.ts             # API 类型
│   │   └── ui.ts              # UI 组件类型
│   ├── styles/
│   │   ├── globals.css        # 全局样式
│   │   └── components.css     # 组件样式
│   └── public/                # 静态资源
├── tests/
│   ├── unit/                  # 单元测试
│   ├── integration/           # 集成测试
│   ├── e2e/                   # 端到端测试
│   └── visual/                # 视觉回归测试
├── .storybook/                # Storybook 配置
├── .github/
│   └── workflows/             # CI/CD 工作流
├── docs/                      # 项目文档
├── scripts/                   # 构建脚本
├── package.json               # 项目依赖
├── next.config.js             # Next.js 配置
├── tsconfig.json              # TypeScript 配置
├── tailwind.config.js         # Tailwind CSS 配置
├── vitest.config.ts           # 测试配置
└── playwright.config.ts       # E2E 测试配置
```

## 🚀 快速开始

### 环境要求

- Node.js 20.0.0+
- pnpm 9.0.0+ (推荐) 或 npm 9.0.0+

### 安装依赖

```bash
# 使用 pnpm (推荐)
pnpm install

# 或使用 npm
npm install
```

### 开发环境

```bash
# 启动开发服务器 (使用 Turbopack)
pnpm dev

# 启动 Storybook
pnpm storybook

# 运行测试
pnpm test

# 运行 E2E 测试
pnpm test:e2e
```

### 构建部署

```bash
# 构建生产版本
pnpm build

# 启动生产服务器
pnpm start

# 分析包大小
pnpm analyze:bundle
```

## 🏗️ 架构设计

### Server Components 架构

我们的架构充分利用了 React 19 Server Components 的优势：

```typescript
// app/page.tsx - Server Component
export default async function HomePage() {
  const data = await getHomePageData() // 服务器端数据获取

  return (
    <div>
      <HeroSection data={data.hero} /> {/* 完全服务器渲染 */}
      <Suspense fallback={<LoadingProducts />}>
        <ProductsShowcase /> {/* 流式渲染 */}
      </Suspense>
    </div>
  )
}
```

### 数据获取策略

1. **服务器端数据获取**: 使用 Next.js 15 的缓存策略
2. **客户端数据获取**: 使用 TanStack Query 管理服务器状态
3. **乐观更新**: 使用 React 19 的 `useOptimistic` 钩子
4. **错误边界**: 优雅的错误处理和恢复

### 状态管理方案

- **UI 状态**: Zustand (客户端状态)
- **服务器状态**: TanStack Query (API 数据)
- **表单状态**: React Hook Form + Zod
- **全局状态**: React Context (主题、语言等)

## 🎯 性能优化

### Core Web Vitals 优化

```typescript
// lib/performance.ts - 性能监控工具
export const webVitalsMonitor = new WebVitalsMonitor()
export const longTaskMonitor = new LongTaskMonitor()
export const memoryMonitor = new MemoryMonitor()
```

### 图片优化

```typescript
// components/ui/lazy-image.tsx - 懒加载图片组件
<LazyImage
  src={imageSrc}
  alt={imageAlt}
  placeholder="blur"
  aspectRatio="16/9"
  loading="lazy"
/>
```

### 代码分割

```typescript
// 动态导入组件
const HeavyComponent = dynamic(() => import('./heavy-component'), {
  loading: () => <div>Loading...</div>,
  ssr: false,
})
```

## 🧪 测试策略

### 测试金字塔

1. **单元测试** (70%): 组件逻辑和工具函数
2. **集成测试** (20%): 组件交互和数据流
3. **E2E 测试** (10%): 完整用户流程

### 测试工具

- **Vitest**: 单元测试和集成测试
- **Testing Library**: React 组件测试
- **Playwright**: 端到端测试
- **Storybook**: 组件开发测试

## 📊 监控和分析

### 性能监控

```typescript
// 自动性能监控
if (typeof window !== 'undefined') {
  // Core Web Vitals
  onCLS(console.warn) // Cumulative Layout Shift
  onFID(console.warn) // First Input Delay
  onLCP(console.warn) // Largest Contentful Paint

  // 长任务监控
  const observer = new PerformanceObserver((list) => {
    list.getEntries().forEach((entry) => {
      if (entry.duration > 50) {
        console.warn(`Long task: ${entry.duration}ms`)
      }
    })
  })
  observer.observe({ entryTypes: ['longtask'] })
}
```

### Bundle 分析

```bash
# 生成 bundle 分析报告
ANALYZE=true pnpm build
```

## 🚀 部署

### Vercel 部署 (推荐)

1. 连接 GitHub 仓库
2. 自动构建和部署
3. 边缘函数支持
4. 自动 HTTPS

### Docker 部署

```dockerfile
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine AS builder
WORKDIR /app
COPY . .
RUN npm ci
RUN npm run build

FROM base AS runner
COPY --from=builder /app/.next ./.next
EXPOSE 3000
CMD ["npm", "start"]
```

## 📈 性能指标

### Core Web Vitals 目标

- **Largest Contentful Paint (LCP)**: < 2.5s
- **First Input Delay (FID)**: < 100ms
- **Cumulative Layout Shift (CLS)**: < 0.1
- **First Contentful Paint (FCP)**: < 1.8s

### Bundle 大小目标

- **Initial Bundle**: < 100KB gzipped
- **Total Bundle**: < 300KB gzipped
- **Code Splitting**: 90%+ 代码分割

## 🛠️ 开发工具

### 推荐的 VS Code 扩展

- **ES7+ React/Redux/React-Native snippets**
- **TypeScript Importer**
- **Tailwind CSS IntelliSense**
- **ESLint**
- **Prettier**
- **GitLens**
- **Thunder Client** (API 测试)

### Git Hooks

```json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged",
      "pre-push": "npm run type-check && npm test"
    }
  },
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ]
  }
}
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [React](https://react.dev/) - 用户界面库
- [Next.js](https://nextjs.org/) - React 框架
- [Vercel](https://vercel.com/) - 部署平台
- [Tailwind CSS](https://tailwindcss.com/) - CSS 框架
- [TypeScript](https://www.typescriptlang.org/) - 类型安全的 JavaScript

---

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: [your-email@example.com]
- 🐦 Twitter: [@your-twitter]
- 💬 Discord: [Your Discord Server]

**Happy Coding! 🎉**