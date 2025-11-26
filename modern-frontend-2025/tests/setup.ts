import '@testing-library/jest-dom'
import { beforeAll, afterAll, beforeEach, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import { server } from './mocks/server'

// 全局测试设置
beforeAll(() => {
  // 启动 MSW 服务器
  server.listen({
    onUnhandledRequest: 'error',
  })
})

// 每个测试前的清理
beforeEach(() => {
  // 清理 DOM
  cleanup()

  // 重置所有处理程序
  server.resetHandlers()

  // 模拟必要的浏览器 API
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => {},
    }),
  })

  // 模拟 IntersectionObserver
  global.IntersectionObserver = class IntersectionObserver {
    constructor() {}
    observe() {}
    unobserve() {}
    disconnect() {}
  }

  // 模拟 ResizeObserver
  global.ResizeObserver = class ResizeObserver {
    constructor() {}
    observe() {}
    unobserve() {}
    disconnect() {}
  }

  // 模拟 requestIdleCallback
  global.requestIdleCallback = (callback) => {
    return setTimeout(callback, 0)
  }

  // 模拟 cancelIdleCallback
  global.cancelIdleCallback = (id) => {
    clearTimeout(id)
  }

  // 模拟 fetch API
  global.fetch = vi.fn()

  // 模拟 localStorage
  const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  }
  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
  })

  // 模拟 sessionStorage
  const sessionStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  }
  Object.defineProperty(window, 'sessionStorage', {
    value: sessionStorageMock,
  })

  // 模拟 performance API
  Object.defineProperty(window, 'performance', {
    value: {
      mark: vi.fn(),
      measure: vi.fn(),
      getEntriesByType: vi.fn(() => []),
      getEntriesByName: vi.fn(() => []),
      now: vi.fn(() => Date.now()),
    },
  })

  // 模拟 gtag
  Object.defineProperty(window, 'gtag', {
    value: vi.fn(),
  })

  // 模拟 Next.js 的 router
  const mockRouter = {
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn(),
    pathname: '/',
    query: {},
    asPath: '/',
    events: {
      on: vi.fn(),
      off: vi.fn(),
      emit: vi.fn(),
    },
  }

  vi.mock('next/router', () => ({
    useRouter: () => mockRouter,
    default: mockRouter,
  }))

  // 模拟 Next.js navigation
  vi.mock('next/navigation', () => ({
    useRouter: () => mockRouter,
    usePathname: () => '/',
    useSearchParams: () => new URLSearchParams(),
    notFound: vi.fn(),
    redirect: vi.fn(),
    permanentRedirect: vi.fn(),
  }))

  // 模拟 Next.js 的 image
  vi.mock('next/image', () => ({
    default: ({ alt, ...props }: any) => <img alt={alt} {...props} />,
  }))

  // 模拟 Next.js 的 font
  vi.mock('next/font/google', () => ({
    Inter: () => ({
      className: 'font-inter',
      style: { fontFamily: 'Inter, sans-serif' },
    }),
  }))
})

// 每个测试后的清理
afterEach(() => {
  cleanup()
})

// 全局测试清理
afterAll(() => {
  // 停止 MSW 服务器
  server.close()
})

// 全局测试超时
vi.setConfig({ testTimeout: 10000 })