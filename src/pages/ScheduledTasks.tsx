import { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  TimePicker,
  Switch,
  message,
  Spin,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  ClockCircleOutlined,
  SearchOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import { scheduledTaskApi, scriptApi, deviceApi, ScheduledTask } from '../services/api'

const ScheduledTasks = () => {
  const [tasks, setTasks] = useState<ScheduledTask[]>([])
  const [filteredTasks, setFilteredTasks] = useState<ScheduledTask[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [form] = Form.useForm()
  const [scripts, setScripts] = useState<any[]>([])
  const [devices, setDevices] = useState<any[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [searchText, setSearchText] = useState('')
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  })

  // 加载定时任务列表
  const loadTasks = async (page = 1, pageSize = 10) => {
    try {
      setLoading(true)
      const response = await scheduledTaskApi.getList({
        page,
        page_size: pageSize,
      })
      setTasks(response.items)
      setFilteredTasks(response.items)
      setPagination({
        current: response.page,
        pageSize: response.page_size,
        total: response.total,
      })
    } catch (error) {
      message.error('加载定时任务列表失败')
      console.error('Failed to load scheduled tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  // 搜索过滤
  const handleSearch = (value: string) => {
    setSearchText(value)
    
    if (!value.trim()) {
      setFilteredTasks(tasks)
      return
    }
    
    const searchLower = value.toLowerCase()
    const filtered = tasks.filter(task => 
      task.name?.toLowerCase().includes(searchLower) ||
      task.script_name?.toLowerCase().includes(searchLower) ||
      task.device_name?.toLowerCase().includes(searchLower)
    )
    setFilteredTasks(filtered)
  }

  // 加载脚本列表
  const loadScripts = async () => {
    try {
      const response = await scriptApi.getList({ page: 1, page_size: 100 })
      setScripts(response.items)
    } catch (error) {
      console.error('Failed to load scripts:', error)
    }
  }

  // 加载设备列表
  const loadDevices = async () => {
    try {
      const response = await deviceApi.getList({ page: 1, page_size: 100 })
      setDevices(response.items)
    } catch (error) {
      console.error('Failed to load devices:', error)
    }
  }

  useEffect(() => {
    loadTasks()
    loadScripts()
    loadDevices()
  }, [])

  const handleCreateTask = async (values: any) => {
    try {
      setSubmitting(true)
      
      // 解析频率
      let frequency = 'daily'
      let schedule_day = null
      
      if (values.frequency === '每天') {
        frequency = 'daily'
      } else if (values.frequency.startsWith('每周')) {
        frequency = 'weekly'
        const dayMap: Record<string, string> = {
          '每周一': 'Monday',
          '每周二': 'Tuesday',
          '每周三': 'Wednesday',
          '每周四': 'Thursday',
          '每周五': 'Friday',
          '每周六': 'Saturday',
          '每周日': 'Sunday',
        }
        schedule_day = dayMap[values.frequency]
      }

      await scheduledTaskApi.create({
        name: values.name,
        script_id: values.script_id,
        device_id: values.device_id,
        frequency,
        schedule_time: values.time.format('HH:mm:00'),
        schedule_day,
      })
      
      message.success('定时任务创建成功！')
      setModalVisible(false)
      form.resetFields()
      loadTasks()
    } catch (error) {
      message.error('创建定时任务失败')
      console.error('Failed to create scheduled task:', error)
    } finally {
      setSubmitting(false)
    }
  }

  // 切换任务状态（启用/禁用）
  const handleToggleTask = async (task: ScheduledTask) => {
    try {
      await scheduledTaskApi.toggle(task.id, !task.is_enabled)
      message.success(`任务已${task.is_enabled ? '禁用' : '启用'}`)
      loadTasks()
    } catch (error) {
      message.error('切换任务状态失败')
      console.error('Failed to toggle task:', error)
    }
  }

  // 立即执行任务
  const handleExecuteTask = async (task: ScheduledTask) => {
    let selectedDeviceId = task.device_id
    
    // 显示设备选择弹窗
    Modal.confirm({
      title: `立即执行任务 - ${task.name}`,
      width: 600,
      content: (
        <div style={{ marginTop: 16 }}>
          <div style={{ marginBottom: 16 }}>
            <strong>选择执行设备：</strong>
          </div>
          <Select
            placeholder="选择在线设备"
            style={{ width: '100%' }}
            defaultValue={task.device_id}
            showSearch
            optionFilterProp="children"
            onChange={(value) => {
              selectedDeviceId = value
            }}
          >
            {devices
              .filter((device) => device.status === 'online' || device.status === 'idle')
              .map((device) => (
                <Select.Option key={device.id} value={device.id}>
                  <Space>
                    <span>{device.model}</span>
                    <span style={{ color: '#999' }}>({device.serial_number})</span>
                    <Tag color="green" size="small">
                      {device.status}
                    </Tag>
                  </Space>
                </Select.Option>
              ))}
          </Select>
          
          {devices.filter((d) => d.status === 'online' || d.status === 'idle').length === 0 && (
            <div style={{ 
              marginTop: 12, 
              padding: 12, 
              background: '#fff3cd', 
              border: '1px solid #ffc107', 
              borderRadius: 4,
              color: '#856404'
            }}>
              ⚠️ 暂无在线设备，无法执行任务
            </div>
          )}
          
          <div style={{ 
            marginTop: 16, 
            padding: 12, 
            background: '#f5f5f5', 
            borderRadius: 4,
            fontSize: 13
          }}>
            <div><strong>任务信息：</strong></div>
            <div style={{ color: '#666', marginTop: 4 }}>
              脚本：{task.script_name || `脚本ID ${task.script_id}`}
            </div>
            <div style={{ color: '#666' }}>
              原定设备：{task.device_name || `设备ID ${task.device_id}`}
            </div>
          </div>
        </div>
      ),
      okText: '开始执行',
      cancelText: '取消',
      okButtonProps: {
        disabled: devices.filter((d) => d.status === 'online' || d.status === 'idle').length === 0,
      },
      onOk: async () => {
        try {
          // 调用执行API，传入选择的设备ID
          const response = await fetch(`/api/v1/scheduled-tasks/${task.id}/execute?device_id=${selectedDeviceId}`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
          })
          
          const data = await response.json()
          
          if (response.ok && data.code === 200) {
            message.success('任务已开始执行')
            loadTasks()
          } else {
            throw new Error(data.detail || data.message || '执行任务失败')
          }
        } catch (error: any) {
          const errorMsg = error?.message || '执行任务失败'
          message.error(errorMsg)
          console.error('Failed to execute task:', error)
        }
      },
    })
  }

  const handleDeleteTask = (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个定时任务吗？',
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await scheduledTaskApi.delete(id)
          message.success('删除成功！')
          loadTasks()
        } catch (error) {
          message.error('删除失败')
          console.error('Failed to delete task:', error)
        }
      },
    })
  }

  const getStatusTag = (task: ScheduledTask) => {
    if (!task.is_enabled) {
      return <Tag color="warning">已暂停</Tag>
    }
    return <Tag color="success">运行中</Tag>
  }

  // 格式化执行计划
  const formatSchedule = (task: ScheduledTask) => {
    const frequencyMap: Record<string, string> = {
      daily: '每天',
      weekly: '每周',
      monthly: '每月',
    }
    
    let schedule = frequencyMap[task.frequency] || task.frequency
    
    if (task.schedule_day) {
      const dayMap: Record<string, string> = {
        Monday: '一',
        Tuesday: '二',
        Wednesday: '三',
        Thursday: '四',
        Friday: '五',
        Saturday: '六',
        Sunday: '日',
      }
      schedule += dayMap[task.schedule_day] || task.schedule_day
    }
    
    schedule += ` ${task.schedule_time.substring(0, 5)}`
    return schedule
  }

  const columns: ColumnsType<ScheduledTask> = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      width: 180,
      render: (name: string) => (
        <Space>
          <ClockCircleOutlined />
          {name}
        </Space>
      ),
    },
    {
      title: '脚本',
      dataIndex: 'script_name',
      key: 'script_name',
      width: 150,
      render: (text: string) => text || '-',
    },
    {
      title: '设备',
      dataIndex: 'device_name',
      key: 'device_name',
      width: 150,
      render: (text: string) => text || '-',
    },
    {
      title: '执行计划',
      key: 'schedule',
      width: 150,
      render: (_, record) => formatSchedule(record),
    },
    {
      title: '状态',
      key: 'status',
      width: 100,
      align: 'center',
      render: (_, record) => getStatusTag(record),
    },
    {
      title: '启用',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 80,
      align: 'center',
      render: (enabled: boolean, record: ScheduledTask) => (
        <Switch checked={enabled} onChange={() => handleToggleTask(record)} />
      ),
    },
    {
      title: '执行次数',
      dataIndex: 'run_count',
      key: 'run_count',
      width: 100,
      align: 'center',
      render: (count: number, record: ScheduledTask) => (
        <span>
          {count} <span style={{ color: '#4ade80' }}>({record.success_count})</span>
        </span>
      ),
    },
    {
      title: '上次运行',
      dataIndex: 'last_run_at',
      key: 'last_run_at',
      width: 180,
      render: (time?: string) => time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-',
    },
    {
      title: '下次运行',
      dataIndex: 'next_run_at',
      key: 'next_run_at',
      width: 180,
      render: (time?: string) => time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<PlayCircleOutlined />}
            size="small"
            onClick={() => handleExecuteTask(record)}
          >
            立即执行
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            size="small"
            onClick={() => handleDeleteTask(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0, fontSize: 24, fontWeight: 600 }}>定时任务</h2>
        <Space>
          <Input
            placeholder="搜索任务名称、脚本、设备"
            prefix={<SearchOutlined />}
            allowClear
            style={{ width: 260 }}
            value={searchText}
            onChange={(e) => handleSearch(e.target.value)}
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
            新建定时任务
          </Button>
        </Space>
      </div>

      <Card
        style={{
          background: '#fff',
          border: '1px solid #e8e8e8',
        }}
      >
        <Table
          columns={columns}
          dataSource={filteredTasks}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1400, y: 600 }}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            pageSizeOptions: ['10', '20', '50'],
            showTotal: (total) => `共 ${total} 个定时任务`,
            onChange: (page, pageSize) => {
              setPagination({ ...pagination, current: page, pageSize: pageSize || 10 })
              loadTasks(page, pageSize)
            },
            onShowSizeChange: (current, size) => {
              setPagination({ ...pagination, current: 1, pageSize: size })
              loadTasks(1, size)
            },
          }}
        />
      </Card>

      <Modal
        title="新建定时任务"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        onOk={() => form.submit()}
        confirmLoading={submitting}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleCreateTask}>
          <Form.Item
            label="任务名称"
            name="name"
            rules={[{ required: true, message: '请输入任务名称' }]}
          >
            <Input placeholder="输入任务名称" />
          </Form.Item>

          <Form.Item
            label="选择脚本"
            name="script_id"
            rules={[{ required: true, message: '请选择脚本' }]}
          >
            <Select placeholder="选择要执行的脚本" showSearch optionFilterProp="children">
              {scripts.map((script) => (
                <Select.Option key={script.id} value={script.id}>
                  {script.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="选择设备"
            name="device_id"
            rules={[{ required: true, message: '请选择设备' }]}
          >
            <Select placeholder="选择执行设备" showSearch optionFilterProp="children">
              {devices.map((device) => (
                <Select.Option key={device.id} value={device.id}>
                  {device.model} ({device.serial_number})
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="执行频率"
            name="frequency"
            rules={[{ required: true, message: '请选择执行频率' }]}
          >
            <Select placeholder="选择执行频率">
              <Select.Option value="每天">每天</Select.Option>
              <Select.Option value="每周一">每周一</Select.Option>
              <Select.Option value="每周二">每周二</Select.Option>
              <Select.Option value="每周三">每周三</Select.Option>
              <Select.Option value="每周四">每周四</Select.Option>
              <Select.Option value="每周五">每周五</Select.Option>
              <Select.Option value="每周六">每周六</Select.Option>
              <Select.Option value="每周日">每周日</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="执行时间"
            name="time"
            rules={[{ required: true, message: '请选择执行时间' }]}
          >
            <TimePicker format="HH:mm" style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ScheduledTasks
