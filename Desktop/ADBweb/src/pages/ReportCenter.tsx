import { useState, useEffect } from 'react'
import { Table, Card, Button, Space, Tag, DatePicker, Select, message, Modal } from 'antd'
import { EyeOutlined, DeleteOutlined, DownloadOutlined, ReloadOutlined } from '@ant-design/icons'
import { reportApi, TaskLog } from '../services/api'
import dayjs from 'dayjs'

const { RangePicker } = DatePicker
const { Option } = Select

const ReportCenter = () => {
  const [reports, setReports] = useState<TaskLog[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(10)
  const [filters, setFilters] = useState({
    status: '',
    device_id: undefined as number | undefined,
    script_id: undefined as number | undefined,
    start_date: '',
    end_date: '',
  })

  const loadReports = async () => {
    try {
      setLoading(true)
      const params: any = {
        page,
        page_size: pageSize,
      }
      
      if (filters.status) params.status = filters.status
      if (filters.device_id) params.device_id = filters.device_id
      if (filters.script_id) params.script_id = filters.script_id
      if (filters.start_date) params.start_date = filters.start_date
      if (filters.end_date) params.end_date = filters.end_date

      const response = await reportApi.getList(params)
      setReports(response.items)
      setTotal(response.total)
    } catch (error) {
      message.error('加载报告列表失败')
      console.error('Failed to load reports:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadReports()
  }, [page, filters])

  const handleDelete = (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个报告吗？此操作不可恢复。',
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await reportApi.delete(id)
          message.success('删除成功')
          loadReports()
        } catch (error) {
          message.error('删除失败')
        }
      },
    })
  }

  const handleViewDetail = async (id: number) => {
    try {
      const report = await reportApi.getDetail(id)
      Modal.info({
        title: `报告详情 - ${report.task_name}`,
        width: 800,
        content: (
          <div style={{ marginTop: 16 }}>
            <div style={{ marginBottom: 12 }}>
              <strong>任务名称：</strong> {report.task_name}
            </div>
            <div style={{ marginBottom: 12 }}>
              <strong>状态：</strong> {getStatusTag(report.status)}
            </div>
            <div style={{ marginBottom: 12 }}>
              <strong>开始时间：</strong> {report.start_time}
            </div>
            {report.end_time && (
              <div style={{ marginBottom: 12 }}>
                <strong>结束时间：</strong> {report.end_time}
              </div>
            )}
            {report.duration && (
              <div style={{ marginBottom: 12 }}>
                <strong>执行时长：</strong> {report.duration}秒
              </div>
            )}
            {report.error_message && (
              <div style={{ marginBottom: 12 }}>
                <strong>错误信息：</strong>
                <pre style={{ background: '#f5f5f5', padding: 8, borderRadius: 4, marginTop: 8 }}>
                  {report.error_message}
                </pre>
              </div>
            )}
            {report.log_content && (
              <div>
                <strong>执行日志：</strong>
                <pre style={{ 
                  background: '#1f1f1f', 
                  color: '#4ade80', 
                  padding: 12, 
                  borderRadius: 4, 
                  marginTop: 8,
                  maxHeight: 400,
                  overflow: 'auto'
                }}>
                  {report.log_content}
                </pre>
              </div>
            )}
          </div>
        ),
      })
    } catch (error) {
      message.error('加载报告详情失败')
    }
  }

  const getStatusTag = (status: string) => {
    const statusMap = {
      success: { color: 'success', text: '成功' },
      failed: { color: 'error', text: '失败' },
      running: { color: 'processing', text: '运行中' },
    }
    const config = statusMap[status as keyof typeof statusMap] || { color: 'default', text: status }
    return <Tag color={config.color}>{config.text}</Tag>
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '任务名称',
      dataIndex: 'task_name',
      key: 'task_name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
    },
    {
      title: '执行时长',
      dataIndex: 'duration',
      key: 'duration',
      render: (duration: number) => duration ? `${duration}秒` : '-',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: TaskLog) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record.id)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <h2 style={{ margin: 0, fontSize: 24, fontWeight: 600, marginBottom: 16 }}>
        报告中心
      </h2>

      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Space wrap>
            <Select
              placeholder="选择状态"
              style={{ width: 120 }}
              allowClear
              value={filters.status || undefined}
              onChange={(value) => setFilters({ ...filters, status: value || '' })}
            >
              <Option value="success">成功</Option>
              <Option value="failed">失败</Option>
              <Option value="running">运行中</Option>
            </Select>

            <RangePicker
              onChange={(dates) => {
                if (dates) {
                  setFilters({
                    ...filters,
                    start_date: dates[0]?.format('YYYY-MM-DD') || '',
                    end_date: dates[1]?.format('YYYY-MM-DD') || '',
                  })
                } else {
                  setFilters({ ...filters, start_date: '', end_date: '' })
                }
              }}
            />

            <Button icon={<ReloadOutlined />} onClick={loadReports}>
              刷新
            </Button>
          </Space>
        </Space>
      </Card>

      <Card>
        <Table
          columns={columns}
          dataSource={reports}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            onChange: (newPage) => setPage(newPage),
            showSizeChanger: false,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>
    </div>
  )
}

export default ReportCenter
