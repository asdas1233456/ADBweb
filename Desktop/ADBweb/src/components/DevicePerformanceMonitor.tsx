/**
 * 设备性能监控组件
 */
import { useEffect, useState } from 'react'
import { Card, Progress, Row, Col, Statistic, Space, Button } from 'antd'
import { SyncOutlined, ThunderboltOutlined, DatabaseOutlined, BatteryOutlined, FireOutlined } from '@ant-design/icons'
import { deviceApi } from '../services/api'
import { usePolling } from '../utils/hooks'

interface DevicePerformanceMonitorProps {
  deviceId: number
  autoRefresh?: boolean
  refreshInterval?: number
}

interface PerformanceData {
  cpu_usage: number
  memory_usage: number
  battery: number
  temperature: number
  timestamp: string
}

const DevicePerformanceMonitor = ({ 
  deviceId, 
  autoRefresh = true,
  refreshInterval = 5000 
}: DevicePerformanceMonitorProps) => {
  const [performance, setPerformance] = useState<PerformanceData | null>(null)
  const [loading, setLoading] = useState(false)

  // 获取性能数据
  const fetchPerformance = async () => {
    try {
      setLoading(true)
      const data = await deviceApi.getPerformance(deviceId)
      setPerformance(data)
    } catch (error) {
      console.error('获取性能数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // 使用轮询 Hook
  const { start, stop, isPolling } = usePolling(
    fetchPerformance,
    refreshInterval,
    true
  )

  useEffect(() => {
    if (autoRefresh) {
      start()
    }
    return () => stop()
  }, [autoRefresh])

  // 获取进度条颜色
  const getProgressColor = (value: number, type: 'cpu' | 'memory' | 'battery' | 'temp') => {
    if (type === 'battery') {
      if (value > 50) return '#52c41a'
      if (value > 20) return '#faad14'
      return '#ff4d4f'
    }
    if (type === 'temp') {
      if (value < 40) return '#52c41a'
      if (value < 50) return '#faad14'
      return '#ff4d4f'
    }
    // CPU 和内存
    if (value < 60) return '#52c41a'
    if (value < 80) return '#faad14'
    return '#ff4d4f'
  }

  if (!performance) {
    return (
      <Card loading={loading}>
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          暂无性能数据
        </div>
      </Card>
    )
  }

  return (
    <Card
      title={
        <Space>
          <ThunderboltOutlined />
          设备性能监控
        </Space>
      }
      extra={
        <Button
          type="text"
          icon={<SyncOutlined spin={loading} />}
          onClick={fetchPerformance}
          disabled={loading}
        >
          {isPolling ? '自动刷新中' : '手动刷新'}
        </Button>
      }
      style={{ background: '#fff', border: '1px solid #e8e8e8' }}
    >
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card size="small" style={{ background: '#fafafa' }}>
            <Statistic
              title={
                <Space>
                  <ThunderboltOutlined style={{ color: '#1890ff' }} />
                  CPU 使用率
                </Space>
              }
              value={performance.cpu_usage}
              suffix="%"
              valueStyle={{ color: getProgressColor(performance.cpu_usage, 'cpu') }}
            />
            <Progress
              percent={performance.cpu_usage}
              strokeColor={getProgressColor(performance.cpu_usage, 'cpu')}
              showInfo={false}
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>

        <Col span={12}>
          <Card size="small" style={{ background: '#fafafa' }}>
            <Statistic
              title={
                <Space>
                  <DatabaseOutlined style={{ color: '#1890ff' }} />
                  内存使用率
                </Space>
              }
              value={performance.memory_usage}
              suffix="%"
              valueStyle={{ color: getProgressColor(performance.memory_usage, 'memory') }}
            />
            <Progress
              percent={performance.memory_usage}
              strokeColor={getProgressColor(performance.memory_usage, 'memory')}
              showInfo={false}
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>

        <Col span={12}>
          <Card size="small" style={{ background: '#fafafa' }}>
            <Statistic
              title={
                <Space>
                  <BatteryOutlined style={{ color: '#1890ff' }} />
                  电池电量
                </Space>
              }
              value={performance.battery}
              suffix="%"
              valueStyle={{ color: getProgressColor(performance.battery, 'battery') }}
            />
            <Progress
              percent={performance.battery}
              strokeColor={getProgressColor(performance.battery, 'battery')}
              showInfo={false}
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>

        <Col span={12}>
          <Card size="small" style={{ background: '#fafafa' }}>
            <Statistic
              title={
                <Space>
                  <FireOutlined style={{ color: '#1890ff' }} />
                  设备温度
                </Space>
              }
              value={performance.temperature}
              suffix="°C"
              valueStyle={{ color: getProgressColor(performance.temperature, 'temp') }}
            />
            <Progress
              percent={(performance.temperature / 60) * 100}
              strokeColor={getProgressColor(performance.temperature, 'temp')}
              showInfo={false}
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
      </Row>

      <div style={{ marginTop: 16, textAlign: 'center', color: '#8c8c8c', fontSize: 12 }}>
        最后更新: {new Date(performance.timestamp).toLocaleString()}
      </div>
    </Card>
  )
}

export default DevicePerformanceMonitor
