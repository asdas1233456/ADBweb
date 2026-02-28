import { useState, useEffect } from 'react'
import { Card, Table, Tag, Space, Select, Button, Input, message, Timeline } from 'antd'
import { ReloadOutlined, HistoryOutlined, SearchOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import { activityLogApi, type ActivityLog } from '../services/api'

const ActivityLog = () => {
  const [loading, setLoading] = useState(false)
  const [logs, setLogs] = useState<ActivityLog[]>([])
  const [filteredLogs, setFilteredLogs] = useState<ActivityLog[]>([])
  const [activityType, setActivityType] = useState<string | undefined>()
  const [status, setStatus] = useState<string | undefined>()
  const [searchText, setSearchText] = useState('')

  // 加载活动日志
  const loadLogs = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (activityType) params.append('activity_type', activityType)
      if (status) params.append('status', status)
      params.append('limit', '100')

      const response = await fetch(`http://localhost:8000/api/v1/activity-logs?${params}`)
      const result = await response.json()
      
      if (result.code === 200) {
        setLogs(result.data)
        setFilteredLogs(result.data)
      } else {
        message.error('加载活动日志失败')
      }
    } catch (error) {
      message.error('加载活动日志失败')
      console.error('加载失败:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadLogs()
  }, [activityType, status])

  // 搜索过滤
  useEffect(() => {
    if (!searchText) {
      setFilteredLogs(logs)
      return
    }

    const filtered = logs.filter(log =>
      log.description.toLowerCase().includes(searchText.toLowerCase()) ||
      log.activity_type.toLowerCase().includes(searchText.toLowerCase())
    )
    setFilteredLogs(filtered)
  }, [searchText, logs])

  // 获取活动类型标签
  const getActivityTypeTag = (type: string) => {
    const typeMap: Record<string, { color: string; text: string }> = {
      device_connect: { color: 'blue', text: '设备连接' },
      device_disconnect: { color: 'default', text: '设备断开' },
      device_create: { color: 'green', text: '设备创建' },
      device_delete: { color: 'red', text: '设备删除' },
      device_refresh: { color: 'cyan', text: '设备刷新' },
      device_scan: { color: 'purple', text: '设备扫描' },
      script_create: { color: 'green', text: '脚本创建' },
      script_update: { color: 'blue', text: '脚本更新' },
      script_delete: { color: 'red', text: '脚本删除' },
      script_execute: { color: 'orange', text: '脚本执行' },
      task_start: { color: 'blue', text: '任务开始' },
      task_complete: { color: 'green', text: '任务完成' },
      task_fail: { color: 'red', text: '任务失败' },
    }
    const { color, text } = typeMap[type] || { color: 'default', text: type }
    return <Tag color={color}>{text}</Tag>
  }

  // 获取状态标签
  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      success: { color: 'success', text: '成功' },
      failed: { color: 'error', text: '失败' },
      pending: { color: 'processing', text: '进行中' },
    }
    const { color, text } = statusMap[status] || { color: 'default', text: status }
    return <Tag color={color}>{text}</Tag>
  }

  const columns: ColumnsType<ActivityLog> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '活动类型',
      dataIndex: 'activity_type',
      key: 'activity_type',
      width: 150,
      render: (type) => getActivityTypeTag(type),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '关联对象',
      key: 'related',
      width: 150,
      render: (_, record) => {
        if (record.related_id && record.related_type) {
          return (
            <span>
              {record.related_type} #{record.related_id}
            </span>
          )
        }
        return '-'
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => getStatusTag(status),
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (time) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0, fontSize: 24, fontWeight: 600 }}>
          <HistoryOutlined style={{ marginRight: 8 }} />
          活动日志
        </h2>
        <Space>
          <Input
            placeholder="搜索日志..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 250 }}
            allowClear
          />
          <Select
            placeholder="活动类型"
            value={activityType}
            onChange={setActivityType}
            style={{ width: 150 }}
            allowClear
            options={[
              { label: '设备连接', value: 'device_connect' },
              { label: '设备断开', value: 'device_disconnect' },
              { label: '设备创建', value: 'device_create' },
              { label: '设备删除', value: 'device_delete' },
              { label: '脚本创建', value: 'script_create' },
              { label: '脚本更新', value: 'script_update' },
              { label: '脚本删除', value: 'script_delete' },
              { label: '脚本执行', value: 'script_execute' },
              { label: '任务开始', value: 'task_start' },
              { label: '任务完成', value: 'task_complete' },
              { label: '任务失败', value: 'task_fail' },
            ]}
          />
          <Select
            placeholder="状态"
            value={status}
            onChange={setStatus}
            style={{ width: 120 }}
            allowClear
            options={[
              { label: '成功', value: 'success' },
              { label: '失败', value: 'failed' },
              { label: '进行中', value: 'pending' },
            ]}
          />
          <Button icon={<ReloadOutlined />} onClick={loadLogs} loading={loading}>
            刷新
          </Button>
        </Space>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={filteredLogs}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            pageSizeOptions: ['10', '20', '50'],
            defaultPageSize: 20,
          }}
        />
      </Card>
    </div>
  )
}

export default ActivityLog
