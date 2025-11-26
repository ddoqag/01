/// <reference types="vitest" />

import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    // 测试环境配置
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],

    // 覆盖率配置
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.config.*',
        '**/*.stories.*',
        'coverage/',
        '.next/',
        'storybook-static/',
        'dist/',
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
      },
    },

    // 测试匹配模式
    include: [
      'tests/**/*.{test,spec}.{js,jsx,ts,tsx}',
      'src/**/__tests__/**/*.{test,spec}.{js,jsx,ts,tsx}',
      'src/**/*.{test,spec}.{js,jsx,ts,tsx}',
    ],

    // 排除模式
    exclude: [
      'node_modules/',
      'tests/e2e/',
      'tests/playwright/',
    ],

    // 测试超时
    testTimeout: 10000,

    // 钩子超时
    hookTimeout: 10000,

    // 串行模式（用于某些需要串行执行的测试）
    sequence: {
      concurrent: true,
      shuffle: false,
    },

    // 报告器
    reporter: ['default', 'html', 'json'],

    // 监听模式配置
    watchExclude: [
      'node_modules/',
      'dist/',
      'coverage/',
    ],
  },

  // 解析配置
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/lib': path.resolve(__dirname, './src/lib'),
      '@/types': path.resolve(__dirname, './src/types'),
      '@/styles': path.resolve(__dirname, './src/styles'),
      '@/hooks': path.resolve(__dirname, './src/lib/hooks'),
      '@/utils': path.resolve(__dirname, './src/lib/utils'),
    },
  },

  // CSS 处理
  css: {
    modules: {
      localsConvention: 'camelCase',
    },
  },

  // 定义全局常量
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'test'),
    'process.env.NEXT_PUBLIC_API_URL': JSON.stringify('http://localhost:3001'),
  },

  // 优化依赖
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-query',
      'zustand',
      'date-fns',
      'clsx',
      'tailwind-merge',
    ],
  },
})