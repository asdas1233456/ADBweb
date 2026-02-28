import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Button, Space, Progress, Tag, List, message, Modal } from 'antd'
import {
  PauseCircleOutlined,
  PlayCircleOutlined,
  StopOutlined,
  ClearOutlined,
  ReloadOutlined,
  FileTextOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons'
import { taskApi } from '../services/api'

interface TaskLog {
  id: number
  task_name: string
  script_id: number
  device_id: number
  status: string
  start_time: string
  end_time?: string
  duration?: number
  error_message?: string
}

const TaskMonitor = () => {
  const navigate = useNavigate()
  const [taskLogs, setTaskLogs] = useState<TaskLog[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedTask, setSelectedTask] = useState<TaskLog | null>(null)
  const logContainerRef = useRef<HTMLDivElement>(null)

  // 加载任务列表
  const loadTaskLogs = async () => {
    try {
      setLoading(true)
      // 直接调用API
      const response = await fetch('/api/v1/tasks')
      const data = await response.json()
      
      if (data.code === 200) {
        setTaskLogs(data.data.items || [])
      } else {
        throw new Error(data.message || '获取任务列表失败')
      }
    } catch (error) {
      console.error('加载任务列表失败:', error)
      message.error('加载任务列表失败')
      // 如果API失败，清空列表
      setTaskLogs([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTaskLogs()
    // 定时刷新任务状态
    const interval = setInterval(loadTaskLogs, 5000)
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    const colorMap: Record<string, string> = {
      running: 'processing',
      success: 'success',
      failed: 'error',
      stopped: 'default',
    }
    return colorMap[status] || 'default'
  }

  const getStatusText = (status: string) => {
    const textMap: Record<string, string> = {
      running: '运行中',
      success: '成功',
      failed: '失败',
      stopped: '已停止',
    }
    return textMap[status] || status
  }

  const handleStopTask = async (taskId: number) => {
    try {
      const response = await fetch(`/api/v1/tasks/${taskId}/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      const data = await response.json()
      
      if (response.ok && data.code === 200) {
        message.success('任务已停止')
        loadTaskLogs()
      } else {
        throw new Error(data.message || '停止任务失败')
      }
    } catch (error: any) {
      console.error('停止任务失败:', error)
      message.error(error.message || '停止任务失败')
    }
  }

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '-'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}分${secs}秒`
  }

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h2 style={{ margin: 0, fontSize: 24, fontWeight: 600, color: '#262626' }}>
            任务执行监控
          </h2>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadTaskLogs}
            loading={loading}
          >
            刷新
          </Button>
        </div>

        <Card
          style={{
            background: '#fff',
            border: '1px solid #e8e8e8',
            height: '500px', // 固定高度
          }}
          bodyStyle={{
            height: 'calc(100% - 57px)', // 减去Card头部高度
            padding: 0, // 移除默认padding
            overflow: 'hidden' // 防止Card body溢出
          }}
        >
          <div 
            style={{ 
              height: '100%', 
              overflowY: 'auto',
              padding: '16px', // 在滚动容器内添加padding
            }}
          >
            <List
              loading={loading}
              dataSource={taskLogs}
              renderItem={(task) => (
                <List.Item
                  key={task.id}
                  actions={[
                    // 查看报告按钮
                    <Button
                      type="link"
                      size="small"
                      icon={<FileTextOutlined />}
                      onClick={() => {
                        // 跳转到报告中心，并筛选该任务的报告
                        navigate(`/reports?task_id=${task.id}`)
                      }}
                    >
                      查看报告
                    </Button>,
                    // 失败分析按钮（仅失败任务显示）
                    task.status === 'failed' && (
                      <Button
                        type="link"
                        size="small"
                        icon={<ExclamationCircleOutlined />}
                        style={{ color: '#ff4d4f' }}
                        onClick={() => {
                          Modal.confirm({
                            title: `任务失败分析 - ${task.task_name}`,
                            width: 800,
                            icon: <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />,
                            content: (
                              <div style={{ marginTop: 16 }}>
                                <div style={{ marginBottom: 16 }}>
                                  <div><strong>任务ID：</strong>{task.id}</div>
                                  <div><strong>失败时间：</strong>{task.end_time ? new Date(task.end_time).toLocaleString('zh-CN') : '-'}</div>
                                  <div><strong>错误信息：</strong>{task.error_message || '未知错误'}</div>
                                </div>
                                <div style={{ marginBottom: 12 }}>
                                  <strong>可能原因分析：</strong>
                                </div>
                                <div style={{ 
                                  background: '#f5f5f5', 
                                  padding: 12, 
                                  borderRadius: 4,
                                  fontSize: 13,
                                  lineHeight: '1.6'
                                }}>
                                  {task.error_message?.includes('Element not found') && (
                                    <div>• 目标元素未找到，可能是页面加载不完整或元素定位器有误</div>
                                  )}
                                  {task.error_message?.includes('timeout') && (
                                    <div>• 操作超时，建议增加等待时间或检查网络连接</div>
                                  )}
                                  {task.error_message?.includes('decode') && (
                                    <div>• 数据解析错误，可能是返回数据格式不正确</div>
                                  )}
                                  {!task.error_message && (
                                    <div>• 未知错误，建议查看详细日志进行排查</div>
                                  )}
                                  <div style={{ marginTop: 8, color: '#666' }}>
                                    建议：检查设备连接状态、脚本逻辑和目标应用状态
                                  </div>
                                </div>
                              </div>
                            ),
                            okText: '查看详细报告',
                            cancelText: '知道了',
                            onOk: () => {
                              navigate(`/reports?task_id=${task.id}&type=failure`)
                            },
                            onCancel: () => {
                              // 用户点击"知道了"，什么都不做，弹窗会自动关闭
                            }
                          })
                        }}
                      >
                        失败分析
                      </Button>
                    ),
                    // 停止按钮（仅运行中任务显示）
                    task.status === 'running' && (
                      <Button
                        type="link"
                        danger
                        size="small"
                        icon={<StopOutlined />}
                        onClick={() => handleStopTask(task.id)}
                      >
                        停止
                      </Button>
                    ),
                  ].filter(Boolean)}
                >
                  <List.Item.Meta
                    title={
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <span>{task.task_name}</span>
                        <Tag color={getStatusColor(task.status)}>
                          {getStatusText(task.status)}
                        </Tag>
                      </div>
                    }
                    description={
                      <div style={{ fontSize: 13, color: '#666' }}>
                        <div>任务ID: {task.id} | 脚本ID: {task.script_id} | 设备ID: {task.device_id}</div>
                        <div>
                          开始时间: {new Date(task.start_time).toLocaleString('zh-CN')}
                          {task.end_time && (
                            <span> | 结束时间: {new Date(task.end_time).toLocaleString('zh-CN')}</span>
                          )}
                          {task.duration && (
                            <span> | 执行时长: {formatDuration(task.duration)}</span>
                          )}
                        </div>
                        {task.error_message && (
                          <div style={{ color: '#ff4d4f', marginTop: 4 }}>
                            错误信息: {task.error_message}
                          </div>
                        )}
                      </div>
                    }
                  />
                  {task.status === 'running' && (
                    <div style={{ width: 200 }}>
                      <Progress percent={50} status="active" size="small" />
                    </div>
                  )}
                </List.Item>
              )}
              locale={{
                emptyText: '暂无执行任务'
              }}
            />
          </div>
        </Card>
      </div>

      {/* 实时日志区域 */}
      <Card
        title={<span style={{ color: '#262626', fontWeight: 600 }}>实时执行日志</span>}
        extra={
          <Space>
            <span style={{ fontSize: 12, color: '#8c8c8c' }}>
              实时更新中...
            </span>
            <Tag color="processing">WebSocket连接</Tag>
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
            minHeight: 300,
            background: '#fafafa',
            padding: 16,
            borderRadius: 8,
            border: '1px solid #e8e8e8',
            fontFamily: 'Consolas, Monaco, monospace',
            fontSize: 13,
          }}
        >
          <div style={{ color: '#8c8c8c', textAlign: 'center', marginTop: 100 }}>
            选择一个运行中的任务查看实时日志
            <br />
            <span style={{ fontSize: 12 }}>
              日志将通过WebSocket实时推送显示
            </span>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default TaskMonitor
