import { useState, useEffect, useRef } from 'react'
import { Card, Button, Space, Progress, Tag } from 'antd'
import {
  PauseCircleOutlined,
  PlayCircleOutlined,
  StopOutlined,
  ClearOutlined,
} from '@ant-design/icons'
import type { LogEntry } from '../types'

const TaskMonitor = () => {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [isRunning, setIsRunning] = useState(true)
  const [isPaused, setIsPaused] = useState(false)
  const [progress, setProgress] = useState(0)
  const logContainerRef = useRef<HTMLDivElement>(null)

  // 模拟实时日志生成
  useEffect(() => {
    if (!isRunning || isPaused) return

    const logMessages = [
      { level: 'info' as const, message: '开始执行脚本...' },
      { level: 'info' as const, message: '连接设备: Xiaomi 12 Pro' },
      { level: 'success' as const, message: '步骤1: 点击登录按钮 - 成功' },
      { level: 'info' as const, message: '等待元素加载...' },
      { level: 'success' as const, message: '步骤2: 输入用户名 - 成功' },
      { level: 'success' as const, message: '步骤3: 输入密码 - 成功' },
      { level: 'warning' as const, message: '检测到网络延迟，重试中...' },
      { level: 'success' as const, message: '步骤4: 点击提交按钮 - 成功' },
      { level: 'info' as const, message: '等待页面跳转...' },
      { level: 'success' as const, message: '登录成功，进入主页' },
      { level: 'info' as const, message: '开始截图保存...' },
      { level: 'success' as const, message: '截图已保存: screenshot_001.png' },
      { level: 'success' as const, message: '脚本执行完成！' },
    ]

    let currentIndex = 0
    const interval = setInterval(() => {
      if (currentIndex < logMessages.length) {
        const newLog: LogEntry = {
          id: `log-${Date.now()}-${currentIndex}`,
          timestamp: new Date().toLocaleTimeString('zh-CN', { hour12: false }),
          ...logMessages[currentIndex],
        }
        setLogs((prev) => [...prev, newLog])
        setProgress(((currentIndex + 1) / logMessages.length) * 100)
        currentIndex++
      } else {
        setIsRunning(false)
        clearInterval(interval)
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [isRunning, isPaused])

  // 自动滚动到底部
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs])

  const getLevelColor = (level: LogEntry['level']) => {
    const colorMap = {
      info: '#3b82f6',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
    }
    return colorMap[level]
  }

  const getLevelTag = (level: LogEntry['level']) => {
    const tagMap = {
      info: { color: 'blue', text: 'INFO' },
      success: { color: 'success', text: 'SUCCESS' },
      warning: { color: 'warning', text: 'WARNING' },
      error: { color: 'error', text: 'ERROR' },
    }
    const { color, text } = tagMap[level]
    return <Tag color={color}>{text}</Tag>
  }

  const handlePause = () => {
    setIsPaused(!isPaused)
  }

  const handleStop = () => {
    setIsRunning(false)
    setIsPaused(false)
  }

  const handleClear = () => {
    setLogs([])
  }

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <h2 style={{ margin: 0, fontSize: 24, fontWeight: 600, marginBottom: 16, color: '#262626' }}>
          任务执行监控
        </h2>

        <Card
          style={{
            background: '#fff',
            border: '1px solid #e8e8e8',
            marginBottom: 16,
          }}
        >
          <div style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
              <span style={{ color: '#262626' }}>执行进度</span>
              <span style={{ color: '#262626' }}>{Math.round(progress)}%</span>
            </div>
            <Progress
              percent={progress}
              status={isRunning ? 'active' : progress === 100 ? 'success' : 'normal'}
              strokeColor={{
                '0%': '#3b82f6',
                '100%': '#10b981',
              }}
            />
          </div>

          <Space>
            {isRunning && (
              <Button
                icon={isPaused ? <PlayCircleOutlined /> : <PauseCircleOutlined />}
                onClick={handlePause}
              >
                {isPaused ? '继续' : '暂停'}
              </Button>
            )}
            <Button icon={<StopOutlined />} danger onClick={handleStop} disabled={!isRunning}>
              停止
            </Button>
            <Button icon={<ClearOutlined />} onClick={handleClear}>
              清空日志
            </Button>
          </Space>
        </Card>
      </div>

      <Card
        title={<span style={{ color: '#262626', fontWeight: 600 }}>执行日志</span>}
        extra={
          <Space>
            <span style={{ fontSize: 12, color: '#8c8c8c' }}>
              共 {logs.length} 条日志
            </span>
            <Tag color={isRunning ? 'processing' : 'default'}>
              {isRunning ? (isPaused ? '已暂停' : '运行中') : '已停止'}
            </Tag>
          </Space>
        }
        style={{
          background: '#fff',
          border: '1px solid #e8e8e8',
        }}
      >
        <div
          ref={logContainerRef}
          style={{
            height: 'calc(100vh - 400px)',
            minHeight: 400,
            overflow: 'auto',
            background: '#fafafa',
            padding: 16,
            borderRadius: 8,
            border: '1px solid #e8e8e8',
            fontFamily: 'Consolas, Monaco, monospace',
            fontSize: 13,
          }}
        >
          {logs.length === 0 ? (
            <div style={{ color: '#8c8c8c', textAlign: 'center', marginTop: 100 }}>
              暂无日志输出
            </div>
          ) : (
            logs.map((log) => (
              <div
                key={log.id}
                style={{
                  marginBottom: 8,
                  padding: '8px 12px',
                  background: '#fff',
                  borderLeft: `3px solid ${getLevelColor(log.level)}`,
                  borderRadius: 4,
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 12,
                  boxShadow: '0 1px 2px rgba(0, 0, 0, 0.03)',
                }}
              >
                <span style={{ color: '#8c8c8c', minWidth: 80 }}>[{log.timestamp}]</span>
                <span style={{ minWidth: 80 }}>{getLevelTag(log.level)}</span>
                <span style={{ color: '#262626', flex: 1 }}>
                  {log.message}
                </span>
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  )
}

export default TaskMonitor
