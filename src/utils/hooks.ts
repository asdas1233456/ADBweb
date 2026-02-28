/**
 * 自定义 React Hooks - 性能优化
 */
import { useEffect, useRef, useState, useCallback } from 'react'

/**
 * 防抖 Hook
 * @param value 需要防抖的值
 * @param delay 延迟时间（毫秒）
 */
export function useDebounce<T>(value: T, delay: number = 500): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

/**
 * 节流 Hook
 * @param callback 需要节流的函数
 * @param delay 延迟时间（毫秒）
 */
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number = 500
): T {
  const lastRun = useRef(Date.now())

  return useCallback(
    ((...args) => {
      const now = Date.now()
      if (now - lastRun.current >= delay) {
        lastRun.current = now
        return callback(...args)
      }
    }) as T,
    [callback, delay]
  )
}

/**
 * 虚拟滚动 Hook
 * @param items 所有数据项
 * @param itemHeight 每项高度
 * @param containerHeight 容器高度
 */
export function useVirtualScroll<T>(
  items: T[],
  itemHeight: number,
  containerHeight: number
) {
  const [scrollTop, setScrollTop] = useState(0)

  const startIndex = Math.floor(scrollTop / itemHeight)
  const endIndex = Math.min(
    startIndex + Math.ceil(containerHeight / itemHeight) + 1,
    items.length
  )

  const visibleItems = items.slice(startIndex, endIndex)
  const offsetY = startIndex * itemHeight
  const totalHeight = items.length * itemHeight

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop)
  }, [])

  return {
    visibleItems,
    offsetY,
    totalHeight,
    handleScroll,
    startIndex,
    endIndex,
  }
}

/**
 * 图片懒加载 Hook
 */
export function useLazyImage(src: string, placeholder: string = '') {
  const [imageSrc, setImageSrc] = useState(placeholder)
  const [isLoading, setIsLoading] = useState(true)
  const imgRef = useRef<HTMLImageElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const img = new Image()
            img.src = src
            img.onload = () => {
              setImageSrc(src)
              setIsLoading(false)
            }
            img.onerror = () => {
              setIsLoading(false)
            }
            if (imgRef.current) {
              observer.unobserve(imgRef.current)
            }
          }
        })
      },
      { threshold: 0.01 }
    )

    if (imgRef.current) {
      observer.observe(imgRef.current)
    }

    return () => {
      if (imgRef.current) {
        observer.unobserve(imgRef.current)
      }
    }
  }, [src])

  return { imageSrc, isLoading, imgRef }
}

/**
 * 轮询 Hook
 * @param callback 轮询执行的函数
 * @param interval 轮询间隔（毫秒）
 * @param immediate 是否立即执行
 */
export function usePolling(
  callback: () => void | Promise<void>,
  interval: number = 5000,
  immediate: boolean = true
) {
  const savedCallback = useRef(callback)
  const [isPolling, setIsPolling] = useState(false)

  useEffect(() => {
    savedCallback.current = callback
  }, [callback])

  useEffect(() => {
    if (!isPolling) return

    if (immediate) {
      savedCallback.current()
    }

    const timer = setInterval(() => {
      savedCallback.current()
    }, interval)

    return () => clearInterval(timer)
  }, [interval, immediate, isPolling])

  const start = useCallback(() => setIsPolling(true), [])
  const stop = useCallback(() => setIsPolling(false), [])

  return { start, stop, isPolling }
}

/**
 * 本地存储 Hook
 * @param key 存储键名
 * @param initialValue 初始值
 */
export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      console.error('Error reading from localStorage:', error)
      return initialValue
    }
  })

  const setValue = useCallback(
    (value: T | ((val: T) => T)) => {
      try {
        const valueToStore = value instanceof Function ? value(storedValue) : value
        setStoredValue(valueToStore)
        window.localStorage.setItem(key, JSON.stringify(valueToStore))
      } catch (error) {
        console.error('Error writing to localStorage:', error)
      }
    },
    [key, storedValue]
  )

  return [storedValue, setValue] as const
}
