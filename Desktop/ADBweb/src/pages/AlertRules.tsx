import { useState, useEffect } from 'react'
import { Card, Table, Button, Space, Tag, Switch, message, Modal, Form, Input, Select, InputNumber } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined, BellOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { deviceHealthApi, type AlertRule } from '../services/api'

const AlertRules = () => {
  const [loading, setLoading] = useState(false)
  const [rules, setRules] = useState<AlertRule[]>([])
  const [modalVisible, setModalVisible] = useState(false)
  const [editingRule, setEditingRule] = useState<AlertRule | null>(null)
  const [form] = Form.useForm()

  // 加载告警规则
  const loadRules = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/device-health/alert-rules')
      const result = await response.json()
      
      if (result.code === 200) {
        setRules(result.data)
      } else {
        message.error('加载告警规则失败')
      }
    } catch (error) {
      message.error('加载告警规则失败')
      console.error('加载失败:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRules()
  }, [])

  // 切换规则启用状态
  const handleToggleEnabled = async (id: number, enabled: boolean) => {
    try {
      // TODO: 实现启用/禁用API
      message.success(enabled ? '规则已启用' : '规则已禁用')
      loadRules()
    } catch (error) {
      message.error('操作失败')
    }
  }

  // 打开编辑模态框
  const handleEdit = (rule: AlertRule) => {
    setEditingRule(rule)
    form.setFieldsValue(rule)
    setModalVisible(true)
  }

  // 打开新建模态框
  const handleAdd = () => {
    setEditingRule(null)
    form.resetFields()
    setModalVisible(true)
  }

  // 保存规则
  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      // TODO: 实现创建/更新API
      message.success(editingRule ? '规则更新成功' : '规则创建成功')
      setModalVisible(false)
      loadRules()
    } catch (error) {
      console.error('保存失败:', error)
    }
  }

  // 删除规则
  const handleDelete = (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这条告警规则吗？',
      onOk: async () => {
        try {
          // TODO: 实现删除API
          message.success('规则删除成功')
          loadRules()
        } catch (error) {
          message.error('删除失败')
        }
      },
    })
  }

  const columns: ColumnsType<AlertRule> = [
    {
      title: '规则名称',
      dataIndex: 'rule_name',
      key: 'rule_name',
    },
    {
      title: '规则类型',
      dataIndex: 'rule_type',
      key: 'rule_type',
      render: (type) => {
        const typeMap: Record<string, { color: string; text: string }> = {
          health_score: { color: 'blue', text: '健康分数' },
          battery: { color: 'orange', text: '电池电量' },
          temperature: { color: 'red', text: '设备温度' },
          cpu_usage: { color: 'purple', text: 'CPU使用率' },
          memory_usage: { color: 'cyan', text: '内存使用率' },
        }
        const { color, text } = typeMap[type] || { color: 'default', text: type }
        return <Tag color={color}>{text}</Tag>
      },
    },
    {
      title: '条件',
      key: 'condition',
      render: (_, record) => (
        <span>
          {record.condition_field} {record.operator} {record.threshold_value}
        </span>
      ),
    },
    {
      title: '严重程度',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity) => {
        const severityMap: Record<string, { color: string; text: string }> = {
          critical: { color: 'error', text: '严重' },
          high: { color: 'warning', text: '高' },
          medium: { color: 'default', text: '中' },
          low: { color: 'success', text: '低' },
        }
        const { color, text } = severityMap[severity] || { color: 'default', text: severity }
        return <Tag color={color}>{text}</Tag>
      },
    },
    {
      title: '状态',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      render: (enabled, record) => (
        <Switch
          checked={enabled}
          onChange={(checked) => handleToggleEnabled(record.id, checked)}
        />
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            size="small"
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            size="small"
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
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0, fontSize: 24, fontWeight: 600 }}>
          <BellOutlined style={{ marginRight: 8 }} />
          告警规则管理
        </h2>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadRules} loading={loading}>
            刷新
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新建规则
          </Button>
        </Space>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={rules}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            pageSizeOptions: ['10', '20', '50'],
          }}
        />
      </Card>

      {/* 编辑/新建模态框 */}
      <Modal
        title={editingRule ? '编辑告警规则' : '新建告警规则'}
        open={modalVisible}
        onOk={handleSave}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="rule_name"
            label="规则名称"
            rules={[{ required: true, message: '请输入规则名称' }]}
          >
            <Input placeholder="请输入规则名称" />
          </Form.Item>

          <Form.Item
            name="rule_type"
            label="规则类型"
            rules={[{ required: true, message: '请选择规则类型' }]}
          >
            <Select
              placeholder="请选择规则类型"
              options={[
                { label: '健康分数', value: 'health_score' },
                { label: '电池电量', value: 'battery' },
                { label: '设备温度', value: 'temperature' },
                { label: 'CPU使用率', value: 'cpu_usage' },
                { label: '内存使用率', value: 'memory_usage' },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="condition_field"
            label="条件字段"
            rules={[{ required: true, message: '请输入条件字段' }]}
          >
            <Input placeholder="例如: health_score" />
          </Form.Item>

          <Form.Item
            name="operator"
            label="操作符"
            rules={[{ required: true, message: '请选择操作符' }]}
          >
            <Select
              placeholder="请选择操作符"
              options={[
                { label: '小于 (<)', value: '<' },
                { label: '小于等于 (<=)', value: '<=' },
                { label: '等于 (=)', value: '=' },
                { label: '大于等于 (>=)', value: '>=' },
                { label: '大于 (>)', value: '>' },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="threshold_value"
            label="阈值"
            rules={[{ required: true, message: '请输入阈值' }]}
          >
            <InputNumber
              placeholder="请输入阈值"
              style={{ width: '100%' }}
              min={0}
              max={100}
            />
          </Form.Item>

          <Form.Item
            name="severity"
            label="严重程度"
            rules={[{ required: true, message: '请选择严重程度' }]}
          >
            <Select
              placeholder="请选择严重程度"
              options={[
                { label: '严重', value: 'critical' },
                { label: '高', value: 'high' },
                { label: '中', value: 'medium' },
                { label: '低', value: 'low' },
              ]}
            />
          </Form.Item>

          <Form.Item name="is_enabled" label="启用状态" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default AlertRules
