import { useState, useEffect, useRef } from 'react'
import { Card, Row, Col, Table, Progress, Tag, Spin, message, Button, Space, Statistic, Empty, Input } from 'antd'
import {
  HeartOutlined,
  ThunderboltOutlined,
  FireOutlined,
  DashboardOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ReloadOutlined,
  SearchOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { Line } from '@ant-design/charts'
import { deviceHealthApi, type DeviceHealthRecord, type DeviceAlert } from '../services/api'

const DeviceHealth = () => {
  const [loading, setLoading] = useState(false)
  const [devices, setDevices] = useState<DeviceHealthRecord[]>([])
  const [filteredDevices, setFilteredDevices] = useState<DeviceHealthRecord[]>([])
  const [alerts, setAlerts] = useState<DeviceAlert[]>([])
  const [selectedDevice, setSelectedDevice] = useState<DeviceHealthRecord | null>(null)
  const [historyData, setHistoryData] = useState<any[]>([])
  const [pageSize, setPageSize] = useState(20)
  const [currentPage, setCurrentPage] = useState(1)
  const [searchText, setSearchText] = useState('')
  const detailCardRef = useRef<HTMLDivElement>(null)

  // 加载设备健康度数据
  const loadDeviceHealth = async () => {
    setLoading(true)
    try {
      const data = await deviceHealthApi.getOverview()
      setDevices(data.devices || [])
      setFilteredDevices(data.devices || [])
    } catch (error) {
      message.error(`加载设备健康度数据失败: ${error instanceof Error ? error.message : '未知错误'}`)
      console.error('加载失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // 加载告警数据
  const loadAlerts = async () => {
    try {
      const data = await deviceHealthApi.getAlerts({ is_resolved: false })
      setAlerts(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('加载告警失败:', error)
    }
  }

  // 加载设备历史数据
  const loadDeviceHistory = async (deviceId: number) => {
    try {
      const data = await deviceHealthApi.getHistory(deviceId, 24)
      
      if (data.records) {
        // 转换数据格式用于图表，并四舍五入数值
        const chartData = data.records.flatMap((record: any) => [
          {
            time: new Date(record.created_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
            type: '健康度',
            value: Math.round(record.health_score)
          },
          {
            time: new Date(record.created_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
            type: 'CPU使用率',
            value: Math.round(record.cpu_usage)
          },
          {
            time: new Date(record.created_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
            type: '内存使用率',
            value: Math.round(record.memory_usage)
          }
        ])
        setHistoryData(chartData)
      }
    } catch (error) {
      console.error('加载历史数据失败:', error)
    }
  }

  useEffect(() => {
    loadDeviceHealth()
    loadAlerts()
    
    // 每30秒刷新一次
    const interval = setInterval(() => {
      loadDeviceHealth()
      loadAlerts()
    }, 30000)
    
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (selectedDevice) {
      loadDeviceHistory(selectedDevice.device_id)
      // 滚动到详情卡片
      setTimeout(() => {
        detailCardRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 100)
    }
  }, [selectedDevice])

  // 获取健康等级图标
  const getHealthIcon = (levelCode: string) => {
    switch (levelCode) {
      case 'excellent':
        return <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 24 }} />
      case 'good':
        return <ThunderboltOutlined style={{ color: '#1890ff', fontSize: 24 }} />
      case 'fair':
        return <DashboardOutlined style={{ color: '#faad14', fontSize: 24 }} />
      case 'poor':
        return <WarningOutlined style={{ color: '#ff7a45', fontSize: 24 }} />
      case 'critical':
        return <FireOutlined style={{ color: '#ff4d4f', fontSize: 24 }} />
      default:
        return <HeartOutlined style={{ color: '#8c8c8c', fontSize: 24 }} />
    }
  }

  // 告警严重程度标签
  const getSeverityTag = (severity: string) => {
    const severityMap: Record<string, { color: string; text: string }> = {
      critical: { color: 'error', text: '严重' },
      high: { color: 'warning', text: '高' },
      medium: { color: 'default', text: '中' },
      low: { color: 'success', text: '低' },
    }
    const { color, text } = severityMap[severity] || { color: 'default', text: severity }
    return <Tag color={color}>{text}</Tag>
  }

  // 设备健康度表格列
  const columns: ColumnsType<DeviceHealthRecord> = [
    {
      title: '设备',
      dataIndex: 'device_name',
      key: 'device_name',
      width: 180,
      render: (text, record) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {getHealthIcon(record.level_code)}
          <span style={{ fontWeight: 500 }}>{text}</span>
        </div>
      )
    },
    {
      title: '健康度',
      dataIndex: 'health_score',
      key: 'health_score',
      width: 150,
      sorter: (a, b) => a.health_score - b.health_score,
      render: (score, record) => (
        <div>
          <Progress
            percent={Math.round(score)}
            strokeColor={record.level_color}
            format={(percent) => `${percent}分`}
          />
          <Tag color={record.level_color} style={{ marginTop: 4 }}>
            {record.level_name}
          </Tag>
        </div>
      )
    },
    {
      title: '电量',
      dataIndex: 'battery_level',
      key: 'battery_level',
      width: 120,
      sorter: (a, b) => a.battery_level - b.battery_level,
      render: (battery) => (
        <Progress
          percent={Math.round(battery)}
          size="small"
          status={battery > 50 ? 'success' : battery > 20 ? 'normal' : 'exception'}
        />
      )
    },
    {
      title: '温度',
      dataIndex: 'temperature',
      key: 'temperature',
      width: 100,
      sorter: (a, b) => a.temperature - b.temperature,
      render: (temp) => (
        <span style={{ color: temp > 45 ? '#ff4d4f' : temp > 40 ? '#faad14' : '#52c41a' }}>
          {Math.round(temp)}°C
        </span>
      )
    },
    {
      title: 'CPU',
      dataIndex: 'cpu_usage',
      key: 'cpu_usage',
      width: 120,
      sorter: (a, b) => a.cpu_usage - b.cpu_usage,
      render: (cpu) => (
        <Progress
          percent={Math.round(cpu)}
          size="small"
          strokeColor={cpu > 80 ? '#ff4d4f' : cpu > 60 ? '#faad14' : '#52c41a'}
        />
      )
    },
    {
      title: '内存',
      dataIndex: 'memory_usage',
      key: 'memory_usage',
      width: 120,
      sorter: (a, b) => a.memory_usage - b.memory_usage,
      render: (memory) => (
        <Progress
          percent={Math.round(memory)}
          size="small"
          strokeColor={memory > 85 ? '#ff4d4f' : memory > 70 ? '#faad14' : '#52c41a'}
        />
      )
    },
    {
      title: '存储',
      dataIndex: 'storage_usage',
      key: 'storage_usage',
      width: 120,
      sorter: (a, b) => a.storage_usage - b.storage_usage,
      render: (storage) => (
        <Progress
          percent={Math.round(storage)}
          size="small"
          strokeColor={storage > 90 ? '#ff4d4f' : storage > 75 ? '#faad14' : '#52c41a'}
        />
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          onClick={() => setSelectedDevice(record)}
        >
          查看详情
        </Button>
      )
    }
  ]

  // 告警表格列
  const alertColumns: ColumnsType<DeviceAlert> = [
    {
      title: '严重程度',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity) => getSeverityTag(severity)
    },
    {
      title: '告警类型',
      dataIndex: 'alert_type',
      key: 'alert_type',
      width: 120,
    },
    {
      title: '告警信息',
      dataIndex: 'message',
      key: 'message',
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (time) => new Date(time).toLocaleString('zh-CN')
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          onClick={() => handleResolveAlert(record.id)}
        >
          解决
        </Button>
      )
    }
  ]

  const handleResolveAlert = async (alertId: number) => {
    try {
      await deviceHealthApi.resolveAlert(alertId)
      message.success('告警已解决')
      loadAlerts()
    } catch (error) {
      message.error('解决告警失败')
    }
  }

  // 统计数据
  const stats = {
    total: devices.length,
    excellent: devices.filter(d => d.level_code === 'excellent').length,
    good: devices.filter(d => d.level_code === 'good').length,
    fair: devices.filter(d => d.level_code === 'fair').length,
    poor: devices.filter(d => d.level_code === 'poor').length,
    critical: devices.filter(d => d.level_code === 'critical').length,
    avgScore: devices.length > 0 ? Math.round(devices.reduce((sum, d) => sum + d.health_score, 0) / devices.length) : 0
  }

  // 搜索过滤
  const handleSearch = (value: string) => {
    setSearchText(value)
    setCurrentPage(1)
    
    if (!value.trim()) {
      setFilteredDevices(devices)
      return
    }
    
    const searchLower = value.toLowerCase()
    const filtered = devices.filter(device => 
      device.device_name?.toLowerCase().includes(searchLower) ||
      device.level_name?.toLowerCase().includes(searchLower)
    )
    setFilteredDevices(filtered)
  }

  // 图表配置
  const chartConfig = {
    data: historyData,
    xField: 'time',
    yField: 'value',
    seriesField: 'type',
    smooth: true,
    animation: {
      appear: {
        animation: 'path-in',
        duration: 1000,
      },
    },
    yAxis: {
      max: 100,
      min: 0,
      label: {
        formatter: (v: string) => `${Math.round(Number(v))}`,
      },
    },
    meta: {
      value: {
        formatter: (v: number) => {
          return `${Math.round(v)}`
        },
      },
    },
  }

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0, fontSize: 24, fontWeight: 600 }}>
          <HeartOutlined style={{ marginRight: 8 }} />
          设备健康度监控
        </h2>
        <Space>
          <Input
            placeholder="搜索设备名称、健康等级"
            prefix={<SearchOutlined />}
            allowClear
            style={{ width: 260 }}
            value={searchText}
            onChange={(e) => handleSearch(e.target.value)}
          />
          <Button icon={<ReloadOutlined />} onClick={loadDeviceHealth} loading={loading}>
            刷新
          </Button>
        </Space>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="设备总数"
              value={stats.total}
              prefix={<DashboardOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="平均健康度"
              value={stats.avgScore}
              suffix="分"
              valueStyle={{ color: stats.avgScore > 80 ? '#52c41a' : stats.avgScore > 60 ? '#faad14' : '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="优秀"
              value={stats.excellent}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="良好"
              value={stats.good}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="一般"
              value={stats.fair}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Statistic
              title="危险"
              value={stats.poor + stats.critical}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 设备健康度列表 */}
      <Card
        title="设备健康度列表"
        style={{ marginBottom: 24 }}
      >
        <Spin spinning={loading}>
          {filteredDevices.length > 0 ? (
            <div style={{ paddingBottom: 60 }}>
              <Table
                columns={columns}
                dataSource={filteredDevices}
                rowKey="device_id"
                scroll={{ y: 500 }}
                pagination={{
                  current: currentPage,
                  pageSize: pageSize,
                  showSizeChanger: true,
                  pageSizeOptions: ['10', '20', '50'],
                  showTotal: (total) => `共 ${total} 台设备`,
                  position: ['bottomCenter'],
                  onChange: (page, size) => {
                    setCurrentPage(page)
                    setPageSize(size)
                  },
                  onShowSizeChange: (current, size) => {
                    setCurrentPage(1)
                    setPageSize(size)
                  },
                }}
              />
            </div>
          ) : (
            <Empty description="暂无设备健康度数据" />
          )}
        </Spin>
      </Card>

      {/* 设备详情和历史趋势 */}
      {selectedDevice && (
        <div ref={detailCardRef}>
          <Card
            title={`${selectedDevice.device_name} - 健康度趋势（最近24小时）`}
            extra={
              <Button size="small" onClick={() => setSelectedDevice(null)}>
                关闭
              </Button>
            }
            style={{ marginBottom: 24 }}
          >
            {historyData.length > 0 ? (
              <Line {...chartConfig} />
            ) : (
              <Empty description="暂无历史数据" />
            )}
          </Card>
        </div>
      )}

      {/* 未解决的告警 */}
      <Card
        title={
          <span>
            <WarningOutlined style={{ marginRight: 8, color: '#ff4d4f' }} />
            未解决的告警 ({alerts.length})
          </span>
        }
      >
        {alerts.length > 0 ? (
          <Table
            columns={alertColumns}
            dataSource={alerts}
            rowKey="id"
            pagination={false}
          />
        ) : (
          <Empty description="暂无告警" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        )}
      </Card>
    </div>
  )
}

export default DeviceHealth
