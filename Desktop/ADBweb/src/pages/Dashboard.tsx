import { Card, Row, Col, Statistic, Progress, Table, Spin, message, theme } from 'antd'
import {
  MobileOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  RiseOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useState } from 'react'
import { dashboardApi, DashboardData } from '../services/api'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

interface RecentActivity {
  id: number
  activity_type: string
  description: string
  created_at: string
  status: 'success' | 'failed'
}

const Dashboard = () => {
  const { token } = theme.useToken() // 获取主题token
  const [loading, setLoading] = useState(true)
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)

  // 加载仪表盘数据
  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const data = await dashboardApi.getOverview()
      setDashboardData(data)
    } catch (error) {
      message.error('加载仪表盘数据失败')
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDashboardData()
    
    // 每30秒自动刷新一次
    const interval = setInterval(loadDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading || !dashboardData) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        minHeight: '60vh',
      }}>
        <Spin size="large" tip="加载中..." />
      </div>
    )
  }

  const { statistics, device_status, execution_stats, recent_activities } = dashboardData

  const columns: ColumnsType<RecentActivity> = [
    {
      title: '类型',
      dataIndex: 'activity_type',
      key: 'activity_type',
      width: 120,
      render: (type: string) => {
        const typeMap: Record<string, string> = {
          script_execute: '脚本执行',
          device_connect: '设备连接',
          device_disconnect: '设备断开',
          script_create: '创建脚本',
          script_update: '更新脚本',
          script_delete: '删除脚本',
          scheduled_task_create: '创建定时任务',
          template_download: '下载模板',
        }
        return typeMap[type] || type
      },
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (time: string) => dayjs(time).fromNow(),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) =>
        status === 'success' ? (
          <CheckCircleOutlined style={{ color: '#4ade80', fontSize: 18 }} />
        ) : (
          <CloseCircleOutlined style={{ color: '#ef4444', fontSize: 18 }} />
        ),
    },
  ]

  // 设备状态颜色映射
  const getDeviceStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return '#10b981'
      case 'busy':
        return '#f59e0b'
      case 'offline':
        return '#ef4444'
      default:
        return '#6b7280'
    }
  }

  // 设备状态文本映射
  const getDeviceStatusText = (status: string) => {
    switch (status) {
      case 'online':
        return '在线'
      case 'busy':
        return '使用中'
      case 'offline':
        return '离线'
      default:
        return '未知'
    }
  }

  return (
    <div>
      {/* 页面标题 */}
      <div className="page-header">
        <h2 className="page-title">
          <ThunderboltOutlined />
          仪表盘
        </h2>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card
            className="stat-card"
            bordered={false}
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none',
            }}
          >
            <Statistic
              title={<span style={{ color: 'rgba(255,255,255,0.9)', fontSize: 14 }}>在线设备</span>}
              value={statistics.online_devices}
              suffix={<span style={{ fontSize: 16, color: 'rgba(255,255,255,0.7)' }}>/ {statistics.total_devices}</span>}
              prefix={<MobileOutlined style={{ fontSize: 32 }} />}
              valueStyle={{ color: '#fff', fontSize: 32, fontWeight: 700 }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card
            className="stat-card"
            bordered={false}
            style={{
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              border: 'none',
            }}
          >
            <Statistic
              title={<span style={{ color: 'rgba(255,255,255,0.9)', fontSize: 14 }}>脚本总数</span>}
              value={statistics.total_scripts}
              prefix={<FileTextOutlined style={{ fontSize: 32 }} />}
              valueStyle={{ color: '#fff', fontSize: 32, fontWeight: 700 }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card
            className="stat-card"
            bordered={false}
            style={{
              background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
              border: 'none',
            }}
          >
            <Statistic
              title={<span style={{ color: 'rgba(255,255,255,0.9)', fontSize: 14 }}>今日执行</span>}
              value={statistics.today_executions}
              prefix={<ClockCircleOutlined style={{ fontSize: 32 }} />}
              valueStyle={{ color: '#fff', fontSize: 32, fontWeight: 700 }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card
            className="stat-card"
            bordered={false}
            style={{
              background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
              border: 'none',
            }}
          >
            <Statistic
              title={<span style={{ color: 'rgba(255,255,255,0.9)', fontSize: 14 }}>成功率</span>}
              value={statistics.success_rate}
              suffix={<span style={{ fontSize: 16, color: 'rgba(255,255,255,0.7)' }}>%</span>}
              prefix={<RiseOutlined style={{ fontSize: 32 }} />}
              valueStyle={{ color: '#fff', fontSize: 32, fontWeight: 700 }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]}>
        {/* 设备状态 */}
        <Col xs={24} lg={8}>
          <Card
            title={
              <span style={{ fontSize: 16, fontWeight: 600, color: token.colorText }}>
                <MobileOutlined style={{ marginRight: 8 }} />
                设备状态
              </span>
            }
            style={{
              background: token.colorBgContainer,
              border: `1px solid ${token.colorBorder}`,
              height: '100%',
            }}
            bodyStyle={{ padding: '16px 24px' }}
          >
            <div 
              style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                gap: 16,
                maxHeight: '600px', // 增加高度以显示更多设备
                overflowY: 'auto',
                overflowX: 'hidden',
                paddingRight: '4px',
              }}
              className="custom-scrollbar"
            >
              {device_status.map((device) => (
                <div
                  key={device.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: 16,
                    background: token.colorBgElevated,
                    borderRadius: 8,
                    border: `1px solid ${token.colorBorder}`,
                    transition: 'all 0.3s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#667eea'
                    e.currentTarget.style.transform = 'translateX(4px)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = token.colorBorder
                    e.currentTarget.style.transform = 'translateX(0)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div
                      style={{
                        width: 48,
                        height: 48,
                        borderRadius: 8,
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <MobileOutlined style={{ fontSize: 24, color: '#fff' }} />
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4, color: token.colorText }}>
                        {device.model}
                      </div>
                      <div style={{ fontSize: 12, color: token.colorTextSecondary }}>
                        电量: {device.battery}%
                      </div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <Progress
                      type="circle"
                      percent={device.battery}
                      width={48}
                      strokeColor={{
                        '0%': '#667eea',
                        '100%': '#764ba2',
                      }}
                      format={(percent) => `${percent}%`}
                    />
                    <div
                      style={{
                        padding: '4px 12px',
                        borderRadius: 6,
                        background: `${getDeviceStatusColor(device.status)}20`,
                        color: getDeviceStatusColor(device.status),
                        fontSize: 12,
                        fontWeight: 600,
                      }}
                    >
                      {getDeviceStatusText(device.status)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </Col>

        {/* 执行统计 */}
        <Col xs={24} lg={16}>
          <Card
            title={
              <span style={{ fontSize: 16, fontWeight: 600, color: token.colorText }}>
                <RiseOutlined style={{ marginRight: 8 }} />
                执行统计
              </span>
            }
            style={{
              background: token.colorBgContainer,
              border: `1px solid ${token.colorBorder}`,
              height: '100%',
            }}
            bodyStyle={{ padding: '24px' }}
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ color: token.colorTextSecondary }}>成功</span>
                  <span style={{ fontWeight: 600, color: '#52c41a' }}>
                    {execution_stats.success_count} ({execution_stats.success_percentage.toFixed(1)}%)
                  </span>
                </div>
                <Progress
                  percent={execution_stats.success_percentage}
                  strokeColor="#52c41a"
                  showInfo={false}
                  strokeWidth={12}
                />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ color: token.colorTextSecondary }}>失败</span>
                  <span style={{ fontWeight: 600, color: '#ff4d4f' }}>
                    {execution_stats.failed_count} ({execution_stats.failed_percentage.toFixed(1)}%)
                  </span>
                </div>
                <Progress
                  percent={execution_stats.failed_percentage}
                  strokeColor="#ff4d4f"
                  showInfo={false}
                  strokeWidth={12}
                />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ color: token.colorTextSecondary }}>运行中</span>
                  <span style={{ fontWeight: 600, color: '#faad14' }}>
                    {execution_stats.running_count} ({execution_stats.running_percentage.toFixed(1)}%)
                  </span>
                </div>
                <Progress
                  percent={execution_stats.running_percentage}
                  strokeColor="#faad14"
                  showInfo={false}
                  strokeWidth={12}
                />
              </div>

              <div
                style={{
                  marginTop: 8,
                  padding: 16,
                  background: token.colorBgElevated,
                  borderRadius: 8,
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: 12, color: token.colorTextSecondary, marginBottom: 4 }}>总执行次数</div>
                <div style={{ fontSize: 32, fontWeight: 700, color: token.colorText }}>
                  {execution_stats.total_count}
                </div>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 最近活动 */}
      <Card
        title={
          <span style={{ fontSize: 16, fontWeight: 600, color: '#262626' }}>
            <ClockCircleOutlined style={{ marginRight: 8 }} />
            最近活动
          </span>
        }
        style={{
          background: '#fff',
          border: '1px solid #e8e8e8',
          marginTop: 24,
        }}
      >
        <Table
          columns={columns}
          dataSource={recent_activities}
          rowKey="id"
          scroll={{ x: 1000, y: 400 }}
          pagination={false}
          size="middle"
        />
      </Card>
    </div>
  )
}

export default Dashboard
