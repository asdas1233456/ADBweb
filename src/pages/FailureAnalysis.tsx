import { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Table, Tag, Button, Space, Modal, Descriptions, Timeline, Empty, Spin, Select, message, Tooltip } from 'antd'
import {
  WarningOutlined,
  BugOutlined,
  FireOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  EyeOutlined,
  ReloadOutlined,
  LineChartOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import { failureAnalysisApi, type FailureAnalysis, type FailureOverview } from '../services/api'

// 失败类型映射
const FAILURE_TYPE_MAP: Record<string, { label: string; color: string }> = {
  'device_disconnected': { label: '设备断连', color: 'red' },
  'element_not_found': { label: '元素未找到', color: 'orange' },
  'timeout': { label: '超时', color: 'gold' },
  'permission_denied': { label: '权限拒绝', color: 'volcano' },
  'app_crash': { label: '应用崩溃', color: 'magenta' },
  'network_error': { label: '网络错误', color: 'blue' },
  'script_error': { label: '脚本错误', color: 'purple' },
  'device_offline': { label: '设备离线', color: 'red' },
  'unknown': { label: '未知错误', color: 'default' },
}

const FailureAnalysis = () => {
  const [loading, setLoading] = useState(false)
  const [overview, setOverview] = useState<FailureOverview | null>(null)
  const [selectedDays, setSelectedDays] = useState(7)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedFailure, setSelectedFailure] = useState<FailureAnalysis | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)

  // 加载失败分析总览
  const loadOverview = async () => {
    setLoading(true)
    try {
      const data = await failureAnalysisApi.getOverview(selectedDays)
      setOverview(data)
    } catch (error) {
      message.error('加载失败分析数据失败')
      console.error('加载失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // 查看失败详情
  const handleViewDetail = async (taskLogId: number) => {
    setDetailLoading(true)
    setDetailModalVisible(true)
    
    try {
      const data = await failureAnalysisApi.getTaskAnalysis(taskLogId)
      setSelectedFailure(data)
    } catch (error) {
      message.error('加载失败详情失败')
      console.error('加载失败:', error)
    } finally {
      setDetailLoading(false)
    }
  }

  useEffect(() => {
    loadOverview()
  }, [selectedDays])

  // 获取失败类型图标
  const getFailureIcon = (icon: string) => {
    const iconMap: Record<string, any> = {
      '🐛': <BugOutlined style={{ fontSize: 24 }} />,
      '⚠️': <WarningOutlined style={{ fontSize: 24 }} />,
      '🔥': <FireOutlined style={{ fontSize: 24 }} />,
      '⚡': <ThunderboltOutlined style={{ fontSize: 24 }} />,
    }
    return iconMap[icon] || <BugOutlined style={{ fontSize: 24 }} />
  }

  // 获取严重程度标签
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

  // 最近失败表格列
  const columns: ColumnsType<FailureOverview['recent_failures'][0]> = [
    {
      title: '任务ID',
      dataIndex: 'task_log_id',
      key: 'task_log_id',
      width: 100,
    },
    {
      title: '失败类型',
      dataIndex: 'failure_type',
      key: 'failure_type',
      width: 150,
      render: (type, record) => {
        const typeInfo = FAILURE_TYPE_MAP[type] || FAILURE_TYPE_MAP['unknown']
        return (
          <Tooltip title={type}>
            <Space size={4}>
              <span style={{ fontSize: 16 }}>{record.failure_icon}</span>
              <Tag color={typeInfo.color}>{typeInfo.label}</Tag>
            </Space>
          </Tooltip>
        )
      },
    },
    {
      title: '错误信息',
      dataIndex: 'error_message',
      key: 'error_message',
      ellipsis: {
        showTitle: false,
      },
      render: (message) => (
        <span title={message} style={{ cursor: 'pointer' }}>
          {message}
        </span>
      ),
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (time) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          size="small"
          onClick={() => handleViewDetail(record.task_log_id)}
        >
          查看详情
        </Button>
      ),
    },
  ]

  if (loading && !overview) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    )
  }

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0, fontSize: 24, fontWeight: 600 }}>
          <BugOutlined style={{ marginRight: 8 }} />
          失败分析
        </h2>
        <Space>
          <Select
            value={selectedDays}
            onChange={setSelectedDays}
            style={{ width: 150 }}
            data-tour="failure-range"
            options={[
              { label: '最近7天', value: 7 },
              { label: '最近30天', value: 30 },
              { label: '最近90天', value: 90 },
            ]}
          />
          <Button icon={<ReloadOutlined />} onClick={loadOverview} loading={loading} data-tour="failure-refresh">
            刷新
          </Button>
        </Space>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }} data-tour="failure-stats">
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总失败次数"
              value={overview?.total_failures || 0}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="失败类型数"
              value={Object.keys(overview?.failure_by_type || {}).length}
              prefix={<LineChartOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={12}>
          <Card>
            <Statistic
              title="最常见失败"
              value={overview?.most_common_failure || '暂无'}
              prefix={<FireOutlined />}
              valueStyle={{ color: '#1890ff', fontSize: 20 }}
            />
          </Card>
        </Col>
      </Row>

      {/* 失败类型分布 */}
      <Card title="失败类型分布" style={{ marginBottom: 24 }}>
        {overview && Object.keys(overview.failure_by_type).length > 0 ? (
          <Row gutter={[16, 16]}>
            {Object.entries(overview.failure_by_type).map(([type, count]) => (
              <Col xs={24} sm={12} md={8} lg={6} key={type}>
                <Card size="small" hoverable>
                  <Statistic
                    title={type}
                    value={count}
                    suffix="次"
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Card>
              </Col>
            ))}
          </Row>
        ) : (
          <Empty description="暂无失败数据" />
        )}
      </Card>

      {/* 最近失败列表 */}
      <Card title="最近失败">
        data-tour="failure-table"
        {overview && overview.recent_failures.length > 0 ? (
          <Table
            columns={columns}
            dataSource={overview.recent_failures}
            rowKey="id"
            pagination={false}
            scroll={{ x: 800 }}
          />
        ) : (
          <Empty description="暂无失败记录" />
        )}
      </Card>

      {/* 失败详情模态框 */}
      <Modal
        title="失败详情"
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false)
          setSelectedFailure(null)
        }}
        width={800}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
        ]}
      >
        {detailLoading ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" />
          </div>
        ) : selectedFailure ? (
          <div>
            <Descriptions bordered column={2}>
              <Descriptions.Item label="任务ID" span={2}>
                {selectedFailure.task_log_id}
              </Descriptions.Item>
              <Descriptions.Item label="失败类型">
                <Space>
                  <span style={{ fontSize: 20 }}>{selectedFailure.failure_icon}</span>
                  <span>{selectedFailure.failure_type}</span>
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="严重程度">
                {getSeverityTag(selectedFailure.severity)}
              </Descriptions.Item>
              <Descriptions.Item label="失败步骤">
                步骤 {selectedFailure.failed_step_index}: {selectedFailure.failed_step_name}
              </Descriptions.Item>
              <Descriptions.Item label="置信度">
                {(selectedFailure.confidence * 100).toFixed(0)}%
              </Descriptions.Item>
              <Descriptions.Item label="错误信息" span={2}>
                <div style={{ color: '#ff4d4f', fontFamily: 'monospace' }}>
                  {selectedFailure.error_message}
                </div>
              </Descriptions.Item>
              <Descriptions.Item label="分析时间" span={2}>
                {dayjs(selectedFailure.created_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
            </Descriptions>

            {selectedFailure.suggestions && selectedFailure.suggestions.length > 0 && (
              <div style={{ marginTop: 24 }}>
                <h3>💡 修复建议</h3>
                <Timeline
                  items={selectedFailure.suggestions.map((suggestion, index) => ({
                    color: 'blue',
                    children: (
                      <div>
                        <strong>建议 {index + 1}:</strong> {suggestion}
                      </div>
                    ),
                  }))}
                />
              </div>
            )}

            {selectedFailure.screenshot_path && (
              <div style={{ marginTop: 24 }}>
                <h3>📸 失败截图</h3>
                <img
                  src={`http://localhost:8000${selectedFailure.screenshot_path}`}
                  alt="失败截图"
                  style={{ maxWidth: '100%', border: '1px solid #d9d9d9', borderRadius: 4 }}
                />
              </div>
            )}
          </div>
        ) : (
          <Empty description="暂无数据" />
        )}
      </Modal>
    </div>
  )
}

export default FailureAnalysis
