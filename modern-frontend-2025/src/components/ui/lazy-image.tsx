'use client'

import Image, { ImageProps } from 'next/image'
import { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'

interface LazyImageProps extends Omit<ImageProps, 'onLoad' | 'onError'> {
  fallback?: string
  placeholder?: 'blur' | 'empty'
  blurDataURL?: string
  onLoad?: () => void
  onError?: () => void
  className?: string
  containerClassName?: string
  aspectRatio?: 'square' | 'video' | 'portrait' | number
}

export function LazyImage({
  src,
  alt,
  fallback = '/placeholder.svg',
  placeholder = 'blur',
  blurDataURL,
  onLoad,
  onError,
  className,
  containerClassName,
  aspectRatio,
  priority = false,
  ...props
}: LazyImageProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [isInView, setIsInView] = useState(priority)
  const imgRef = useRef<HTMLDivElement>(null)

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (priority || !imgRef.current) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true)
          observer.disconnect()
        }
      },
      {
        rootMargin: '50px', // Start loading 50px before it comes into view
        threshold: 0.1,
      }
    )

    observer.observe(imgRef.current)

    return () => observer.disconnect()
  }, [priority])

  // 生成模糊占位符
  const getBlurDataURL = () => {
    if (blurDataURL) return blurDataURL

    // 生成一个简单的模糊占位符
    if (placeholder === 'blur') {
      return 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k='
    }

    return undefined
  }

  // 计算宽高比
  const getAspectRatioStyle = () => {
    if (!aspectRatio) return {}

    if (typeof aspectRatio === 'number') {
      return {
        aspectRatio: `${aspectRatio}`,
      }
    }

    const ratios = {
      square: '1',
      video: '16/9',
      portrait: '2/3',
    }

    return {
      aspectRatio: ratios[aspectRatio] || 'auto',
    }
  }

  // 处理图片加载成功
  const handleLoad = () => {
    setIsLoading(false)
    setHasError(false)
    onLoad?.()
  }

  // 处理图片加载失败
  const handleError = () => {
    setIsLoading(false)
    setHasError(true)
    onError?.()
  }

  // 如果不在视图中且不是优先级图片，显示占位符
  if (!isInView) {
    return (
      <div
        ref={imgRef}
        className={cn(
          'relative overflow-hidden bg-muted',
          containerClassName
        )}
        style={getAspectRatioStyle()}
      >
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-8 w-8 animate-pulse rounded-md bg-muted-foreground/20" />
        </div>
      </div>
    )
  }

  return (
    <div
      ref={imgRef}
      className={cn(
        'relative overflow-hidden',
        containerClassName
      )}
      style={getAspectRatioStyle()}
    >
      {/* 加载状态 */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted">
          <div className="h-8 w-8 animate-pulse rounded-md bg-muted-foreground/20" />
        </div>
      )}

      {/* 错误状态 */}
      {hasError && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted">
          <div className="flex flex-col items-center gap-2 text-muted-foreground">
            <svg
              className="h-8 w-8"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.314 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
            <span className="text-sm">图片加载失败</span>
          </div>
        </div>
      )}

      {/* 实际图片 */}
      <Image
        src={hasError ? fallback : src}
        alt={alt}
        className={cn(
          'transition-opacity duration-300',
          isLoading ? 'opacity-0' : 'opacity-100',
          hasError && 'opacity-50',
          className
        )}
        placeholder={placeholder}
        blurDataURL={getBlurDataURL()}
        onLoad={handleLoad}
        onError={handleError}
        priority={priority}
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        {...props}
      />

      {/* 渐进式加载效果 */}
      {isLoading && placeholder === 'blur' && !hasError && (
        <div
          className="absolute inset-0 opacity-30 transition-opacity duration-300"
          style={{
            backgroundImage: `url(${getBlurDataURL()})`,
            filter: 'blur(20px)',
            transform: 'scale(1.1)',
          }}
        />
      )}
    </div>
  )
}

// 批量图片预加载 Hook
export function useImagePreload(urls: string[]) {
  const [loadedImages, setLoadedImages] = useState<Set<string>>(new Set())
  const [loadingImages, setLoadingImages] = useState<Set<string>>(new Set())

  useEffect(() => {
    const preloadImage = (url: string) => {
      if (loadedImages.has(url) || loadingImages.has(url)) return

      setLoadingImages((prev) => new Set(prev).add(url))

      const img = new Image()
      img.onload = () => {
        setLoadedImages((prev) => new Set(prev).add(url))
        setLoadingImages((prev) => {
          const newSet = new Set(prev)
          newSet.delete(url)
          return newSet
        })
      }
      img.onerror = () => {
        setLoadingImages((prev) => {
          const newSet = new Set(prev)
          newSet.delete(url)
          return newSet
        })
      }
      img.src = url
    }

    // 延迟预加载，避免阻塞主要渲染
    const timer = setTimeout(() => {
      urls.forEach(preloadImage)
    }, 100)

    return () => clearTimeout(timer)
  }, [urls, loadedImages, loadingImages])

  return { loadedImages, loadingImages }
}

// 响应式图片组件
export function ResponsiveImage({
  src,
  alt,
  sizes,
  ...props
}: LazyImageProps & { sizes: string }) {
  return (
    <LazyImage
      src={src}
      alt={alt}
      sizes={sizes}
      fill
      style={{
        objectFit: 'cover',
      }}
      {...props}
    />
  )
}