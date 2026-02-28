import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Table, Card, Button, Space, Tag, DatePicker, Select, message, Modal } from 'antd'
import { EyeOutlined, DeleteOutlined, DownloadOutlined, ReloadOutlined, ExclamationCircleOutlined } from '@ant-design/icons'
import { reportApi, TaskLog } from '../services/api'
import dayjs from 'dayjs'

const { RangePicker } = DatePicker
const { Option } = Select

const ReportCenter = () => {
  const navigate = useNavigate()
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
  const [batchDeleteModalVisible, setBatchDeleteModalVisible] = useState(false)
  const [batchDeleteFilters, setBatchDeleteFilters] = useState({
    status: '',
    start_date: '',
    end_date: '',
  })
  const [batchDeleting, setBatchDeleting] = useState(false)

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

  const handleFailureAnalysis = (report: TaskLog) => {
    Modal.confirm({
      title: `任务失败分析 - ${report.task_name}`,
      width: 800,
      icon: <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />,
      content: (
        <div style={{ marginTop: 16 }}>
          <div style={{ marginBottom: 16 }}>
            <div><strong>任务ID：</strong>{report.id}</div>
            <div><strong>失败时间：</strong>{report.end_time ? new Date(report.end_time).toLocaleString('zh-CN', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
              hour12: false
            }) : '-'}</div>
            <div><strong>错误信息：</strong>{report.error_message || '未知错误'}</div>
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
            {report.error_message?.includes('Element not found') && (
              <div>• 目标元素未找到，可能是页面加载不完整或元素定位器有误</div>
            )}
            {report.error_message?.includes('timeout') && (
              <div>• 操作超时，建议增加等待时间或检查网络连接</div>
            )}
            {report.error_message?.includes('decode') && (
              <div>• 数据解析错误，可能是返回数据格式不正确</div>
            )}
            {report.error_message?.includes('can\'t decode') && (
              <div>• 数据解析错误，可能是返回数据格式不正确</div>
            )}
            {!report.error_message && (
              <div>• 未知错误，建议查看详细日志进行排查</div>
            )}
            <div style={{ marginTop: 8, color: '#666' }}>
              建议：检查设备连接状态、脚本逻辑和目标应用状态
            </div>
          </div>
        </div>
      ),
      okText: '查看失败分析',
      cancelText: '知道了',
      onOk: () => {
        navigate(`/failure-analysis?task_id=${report.id}`)
      },
      onCancel: () => {
        // 用户点击"知道了"，什么都不做，弹窗会自动关闭
      }
    })
  }

  const handleBatchDelete = async () => {
    if (!batchDeleteFilters.status && !batchDeleteFilters.start_date && !batchDeleteFilters.end_date) {
      message.warning('请至少选择一个删除条件')
      return
    }

    try {
      setBatchDeleting(true)
      const params: any = {}
      
      if (batchDeleteFilters.status) params.status = batchDeleteFilters.status
      if (batchDeleteFilters.start_date) params.start_date = batchDeleteFilters.start_date
      if (batchDeleteFilters.end_date) params.end_date = batchDeleteFilters.end_date

      await reportApi.batchDelete(params)
      message.success('批量删除成功')
      setBatchDeleteModalVisible(false)
      setBatchDeleteFilters({ status: '', start_date: '', end_date: '' })
      loadReports()
    } catch (error) {
      message.error('批量删除失败')
      console.error('Failed to batch delete:', error)
    } finally {
      setBatchDeleting(false)
    }
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
              <strong>开始时间：</strong> {report.start_time ? new Date(report.start_time).toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
              }) : '-'}
            </div>
            {report.end_time && (
              <div style={{ marginBottom: 12 }}>
                <strong>结束时间：</strong> {new Date(report.end_time).toLocaleString('zh-CN', {
                  year: 'numeric',
                  month: '2-digit',
                  day: '2-digit',
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit',
                  hour12: false
                })}
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
            {report.status === 'failed' && (
              <div style={{ marginBottom: 12 }}>
                <strong>失败原因分析：</strong>
                <div style={{ 
                  background: '#fff3cd', 
                  border: '1px solid #ffc107',
                  padding: 12, 
                  borderRadius: 4, 
                  marginTop: 8,
                  fontSize: 13,
                  lineHeight: '1.6'
                }}>
                  {report.error_message?.includes('Element not found') && (
                    <div>• 目标元素未找到，可能是页面加载不完整或元素定位器有误</div>
                  )}
                  {report.error_message?.includes('timeout') && (
                    <div>• 操作超时，建议增加等待时间或检查网络连接</div>
                  )}
                  {report.error_message?.includes('decode') && (
                    <div>• 数据解析错误，可能是返回数据格式不正确</div>
                  )}
                  {report.error_message?.includes('can\'t decode') && (
                    <div>• 数据解析错误，可能是返回数据格式不正确</div>
                  )}
                  {!report.error_message?.includes('Element not found') && 
                   !report.error_message?.includes('timeout') && 
                   !report.error_message?.includes('decode') && (
                    <div>• 未知错误，建议查看详细日志进行排查</div>
                  )}
                  <div style={{ marginTop: 8, color: '#856404' }}>
                    <strong>建议：</strong>检查设备连接状态、脚本逻辑和目标应用状态
                  </div>
                  <div style={{ marginTop: 12, textAlign: 'right' }}>
                    <Button 
                      type="primary" 
                      size="small"
                      onClick={() => {
                        Modal.destroyAll()
                        navigate(`/failure-analysis?task_id=${report.id}`)
                      }}
                    >
                      查看详细失败分析
                    </Button>
                  </div>
                </div>
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
      render: (time: string) => {
        if (!time) return '-'
        return new Date(time).toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        })
      },
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
            
            <Button 
              danger 
              icon={<DeleteOutlined />} 
              onClick={() => setBatchDeleteModalVisible(true)}
            >
              批量删除
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

      {/* 批量删除弹窗 */}
      <Modal
        title="批量删除报告"
        open={batchDeleteModalVisible}
        onCancel={() => {
          setBatchDeleteModalVisible(false)
          setBatchDeleteFilters({ status: '', start_date: '', end_date: '' })
        }}
        onOk={handleBatchDelete}
        confirmLoading={batchDeleting}
        okText="确认删除"
        cancelText="取消"
        okButtonProps={{ danger: true }}
        width={600}
      >
        <div style={{ marginTop: 16 }}>
          <div style={{ 
            background: '#fff3cd', 
            border: '1px solid #ffc107',
            padding: 12, 
            borderRadius: 4,
            marginBottom: 16,
            color: '#856404'
          }}>
            ⚠️ 警告：批量删除操作不可恢复，请谨慎操作！
          </div>
          
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <div>
              <div style={{ marginBottom: 8 }}>
                <strong>按状态删除：</strong>
              </div>
              <Select
                placeholder="选择要删除的报告状态"
                style={{ width: '100%' }}
                allowClear
                value={batchDeleteFilters.status || undefined}
                onChange={(value) => setBatchDeleteFilters({ ...batchDeleteFilters, status: value || '' })}
              >
                <Option value="success">成功</Option>
                <Option value="failed">失败</Option>
                <Option value="running">运行中</Option>
              </Select>
            </div>

            <div>
              <div style={{ marginBottom: 8 }}>
                <strong>按时间区间删除：</strong>
              </div>
              <RangePicker
                style={{ width: '100%' }}
                onChange={(dates) => {
                  if (dates) {
                    setBatchDeleteFilters({
                      ...batchDeleteFilters,
                      start_date: dates[0]?.format('YYYY-MM-DD') || '',
                      end_date: dates[1]?.format('YYYY-MM-DD') || '',
                    })
                  } else {
                    setBatchDeleteFilters({ ...batchDeleteFilters, start_date: '', end_date: '' })
                  }
                }}
              />
            </div>

            <div style={{ 
              background: '#f5f5f5', 
              padding: 12, 
              borderRadius: 4,
              fontSize: 13,
              color: '#666'
            }}>
              <div><strong>删除规则：</strong></div>
              <div>• 可以单独按状态删除</div>
              <div>• 可以单独按时间区间删除</div>
              <div>• 可以同时选择状态和时间区间，删除同时满足两个条件的报告</div>
              <div>• 至少需要选择一个删除条件</div>
            </div>
          </Space>
        </div>
      </Modal>
    </div>
  )
}

export default ReportCenter
