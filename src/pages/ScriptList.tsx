import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
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
  Upload,
  message,
  Tabs,
  Spin,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  UploadOutlined,
  FileTextOutlined,
  CodeOutlined,
  FileOutlined,
  SearchOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { UploadFile } from 'antd/es/upload/interface'
import { scriptApi, uploadApi, Script, deviceApi, taskApi } from '../services/api'
import ScriptValidator from '../components/ScriptValidator'

type ScriptType = 'visual' | 'python' | 'batch'
type ScriptCategory = 'login' | 'test' | 'automation' | 'other'

const ScriptList = () => {
  const navigate = useNavigate()
  const [scripts, setScripts] = useState<Script[]>([])
  const [loading, setLoading] = useState(false)
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<ScriptCategory | 'all'>('all')
  const [searchText, setSearchText] = useState('')
  const [form] = Form.useForm()
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [uploading, setUploading] = useState(false)
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  })
  const [validationResult, setValidationResult] = useState<any>(null)
  const [validating, setValidating] = useState(false)
  const [forceCreate, setForceCreate] = useState(false)
  const [executeModalVisible, setExecuteModalVisible] = useState(false)
  const [selectedScript, setSelectedScript] = useState<Script | null>(null)
  const [devices, setDevices] = useState<any[]>([])
  const [executing, setExecuting] = useState(false)

  const scriptTypeMap: Record<ScriptType, { icon: any; color: string; text: string }> = {
    visual: { icon: <FileTextOutlined />, color: 'blue', text: '可视化' },
    python: { icon: <CodeOutlined />, color: 'green', text: 'Python' },
    batch: { icon: <FileOutlined />, color: 'orange', text: '批处理' },
  }

  const categoryMap: Record<ScriptCategory, { color: string; text: string }> = {
    login: { color: 'purple', text: '登录' },
    test: { color: 'cyan', text: '测试' },
    automation: { color: 'geekblue', text: '自动化' },
    other: { color: 'default', text: '其他' },
  }

  // 加载脚本列表
  const loadScripts = async (page = 1, pageSize = 20) => {
    try {
      setLoading(true)
      const params: any = {
        page,
        page_size: pageSize,
      }
      
      if (selectedCategory !== 'all') {
        params.category = selectedCategory
      }
      
      if (searchText.trim()) {
        params.keyword = searchText.trim()
      }

      const response = await scriptApi.getList(params)
      setScripts(response.items)
      setPagination({
        current: response.page,
        pageSize: response.page_size,
        total: response.total,
      })
    } catch (error) {
      message.error('加载脚本列表失败')
      console.error('Failed to load scripts:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadScripts()
    loadDevices()
  }, [selectedCategory, searchText])

  // 加载设备列表
  const loadDevices = async () => {
    try {
      const response = await deviceApi.getList({ page: 1, page_size: 100 })
      setDevices(response.items.filter((device: any) => device.status === 'online'))
    } catch (error) {
      console.error('Failed to load devices:', error)
    }
  }

  // 验证脚本
  const validateScript = async (file: File, scriptType: 'python' | 'batch') => {
    try {
      setValidating(true)
      setValidationResult(null)
      
      // 读取文件内容
      const content = await file.text()
      
      // 调用验证接口
      const result = await scriptApi.validate({
        script_type: scriptType,
        content: content,
        filename: file.name,
      })
      
      setValidationResult(result)
      
      if (!result.passed) {
        message.warning('脚本验证未通过，请查看详细信息')
      } else if (result.score < 70) {
        message.info('脚本验证通过，但建议优化代码质量')
      } else {
        message.success('脚本验证通过！')
      }
    } catch (error) {
      message.error('脚本验证失败')
      console.error('Failed to validate script:', error)
    } finally {
      setValidating(false)
    }
  }

  const handleCreateScript = async (values: any) => {
    // 如果是 Python 或 Batch 脚本，检查验证结果
    if ((values.type === 'python' || values.type === 'batch') && fileList.length > 0) {
      if (!validationResult) {
        message.warning('请先验证脚本')
        return
      }
      // 修复：验证未通过且未强制保存时才阻止
      if (!validationResult.passed && !forceCreate) {
        message.error('脚本验证未通过，无法保存。请修复问题或勾选"强制保存"')
        return
      }
    }
    
    try {
      setUploading(true)
      
      let scriptData: any = {
        name: values.name,
        type: values.type,
        category: values.category,
        description: values.description || '',
      }

      // 如果是 Python 或 Batch 脚本，需要先上传文件
      if ((values.type === 'python' || values.type === 'batch') && fileList.length > 0) {
        // 获取文件对象
        const file = fileList[0].originFileObj || fileList[0]
        if (!file) {
          message.error('文件对象不存在，请重新选择文件')
          return
        }
        
        console.log('Uploading file:', file.name, file.type, file.size)
        
        const uploadResult = await uploadApi.uploadScript(
          file as File,
          values.type === 'python' ? 'python' : 'batch'
        )
        
        console.log('Upload result:', uploadResult)
        
        scriptData.file_path = uploadResult.file_path
        scriptData.file_content = uploadResult.file_content
      } else if (values.type === 'visual') {
        // 可视化脚本初始化为空步骤
        scriptData.steps_json = '[]'
      }

      console.log('Creating script with data:', scriptData)
      
      await scriptApi.create(scriptData)
      message.success('脚本创建成功！')
      setCreateModalVisible(false)
      form.resetFields()
      setFileList([])
      setValidationResult(null)
      loadScripts()
    } catch (error: any) {
      const errorMsg = error?.message || '创建脚本失败'
      message.error(errorMsg)
      console.error('Failed to create script:', error)
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteScript = (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个脚本吗？',
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await scriptApi.delete(id)
          message.success('删除成功！')
          loadScripts()
        } catch (error) {
          message.error('删除失败')
          console.error('Failed to delete script:', error)
        }
      },
    })
  }

  const handleRunScript = (script: Script) => {
    setSelectedScript(script)
    setExecuteModalVisible(true)
  }

  const handleExecuteScript = async (values: any) => {
    if (!selectedScript) return

    try {
      setExecuting(true)
      const result = await taskApi.execute({
        task_name: `执行脚本: ${selectedScript.name}`,
        script_id: selectedScript.id,
        device_id: values.device_id,
      })
      
      message.success(
        <div>
          <div>脚本开始执行！</div>
          <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
            任务ID: {result.task_log_id}
          </div>
        </div>
      )
      setExecuteModalVisible(false)
      
      // 可以跳转到任务监控页面查看执行状态
      Modal.info({
        title: '脚本执行中',
        content: (
          <div>
            <div style={{ marginBottom: 8 }}>
              脚本 <strong>{selectedScript.name}</strong> 已开始执行
            </div>
            <div style={{ fontSize: 12, color: '#666' }}>
              任务ID: {result.task_log_id}
            </div>
            <div style={{ fontSize: 12, color: '#666', marginTop: 8 }}>
              您可以在任务监控页面查看执行进度和结果
            </div>
          </div>
        ),
        okText: '知道了',
      })
      
    } catch (error: any) {
      message.error(error?.message || '执行失败')
      console.error('Failed to execute script:', error)
    } finally {
      setExecuting(false)
    }
  }

  const handleEditScript = async (script: Script) => {
    if (script.type === 'visual') {
      navigate(`/scripts/${script.id}`)
    } else {
      // 获取脚本详情
      try {
        const detail = await scriptApi.getDetail(script.id)
        Modal.info({
          title: `编辑脚本 - ${detail.name}`,
          width: 800,
          content: (
            <div style={{ marginTop: 16 }}>
              <div style={{ marginBottom: 8 }}>
                <strong>文件路径：</strong> {detail.file_path || '无'}
              </div>
              <div style={{ marginBottom: 8 }}>
                <strong>脚本内容：</strong>
              </div>
              <pre
                style={{
                  background: '#1f1f1f',
                  padding: 16,
                  borderRadius: 8,
                  maxHeight: 400,
                  overflow: 'auto',
                  color: '#4ade80',
                  fontFamily: 'Consolas, Monaco, monospace',
                }}
              >
                {detail.file_content || '// 暂无内容'}
              </pre>
            </div>
          ),
        })
      } catch (error) {
        message.error('获取脚本详情失败')
        console.error('Failed to get script detail:', error)
      }
    }
  }

  const columns: ColumnsType<Script> = [
    {
      title: '脚本名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      ellipsis: {
        showTitle: false,
      },
      render: (name: string, record: Script) => {
        const typeInfo = scriptTypeMap[record.type as ScriptType]
        return (
          <Space>
            {typeInfo?.icon || <FileOutlined />}
            <span style={{ 
              maxWidth: '150px', 
              overflow: 'hidden', 
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              display: 'inline-block'
            }} title={name}>
              {name}
            </span>
          </Space>
        )
      },
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      align: 'center',
      render: (type: ScriptType) => {
        const typeInfo = scriptTypeMap[type]
        if (!typeInfo) {
          return <Tag>{type}</Tag>
        }
        return <Tag color={typeInfo.color}>{typeInfo.text}</Tag>
      },
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 100,
      align: 'center',
      render: (category: ScriptCategory) => {
        const categoryInfo = categoryMap[category]
        if (!categoryInfo) {
          return <Tag>{category}</Tag>
        }
        return <Tag color={categoryInfo.color}>{categoryInfo.text}</Tag>
      },
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 300,
      ellipsis: {
        showTitle: false,
      },
      render: (text: string) => (
        <span title={text || '-'} style={{
          display: 'inline-block',
          maxWidth: '280px',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap'
        }}>
          {text || '-'}
        </span>
      ),
    },
    {
      title: '步骤数',
      dataIndex: 'steps_json',
      key: 'steps_json',
      width: 80,
      align: 'center',
      render: (stepsJson: string) => {
        if (!stepsJson) return '-'
        try {
          const steps = JSON.parse(stepsJson)
          return Array.isArray(steps) ? steps.length : '-'
        } catch {
          return '-'
        }
      },
    },
    {
      title: '最后修改',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 160,
      render: (text: string) => new Date(text).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 220,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            size="small"
            onClick={() => handleEditScript(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            icon={<PlayCircleOutlined />}
            size="small"
            onClick={() => handleRunScript(record)}
            disabled={!devices.length}
          >
            运行
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            size="small"
            onClick={() => handleDeleteScript(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  // 计算各分类的数量
  const getCategoryCount = (category: ScriptCategory | 'all') => {
    if (category === 'all') return pagination.total
    return scripts.filter((s) => s.category === category).length
  }

  const tabItems = [
    { key: 'all', label: `全部 (${pagination.total})` },
    { key: 'login', label: `登录 (${getCategoryCount('login')})` },
    { key: 'test', label: `测试 (${getCategoryCount('test')})` },
    { key: 'automation', label: `自动化 (${getCategoryCount('automation')})` },
    { key: 'other', label: `其他 (${getCategoryCount('other')})` },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0, fontSize: 24, fontWeight: 600, color: '#262626' }}>脚本管理</h2>
        <Space>
          <Input
            placeholder="搜索脚本名称、描述"
            prefix={<SearchOutlined />}
            allowClear
            style={{ width: 260 }}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModalVisible(true)}>
            新建脚本
          </Button>
        </Space>
      </div>

      <Card
        style={{
          background: '#fff',
          border: '1px solid #e8e8e8',
          marginBottom: 16,
        }}
      >
        <Tabs
          activeKey={selectedCategory}
          onChange={(key) => setSelectedCategory(key as ScriptCategory | 'all')}
          items={tabItems}
        />
      </Card>

      <Card
        style={{
          background: '#fff',
          border: '1px solid #e8e8e8',
        }}
      >
        <Table
          columns={columns}
          dataSource={scripts}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200, y: 'calc(100vh - 450px)' }} // 动态高度，最大约20行
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            pageSizeOptions: ['10', '20', '50'],
            showTotal: (total) => `共 ${total} 个脚本`,
            onChange: (page, pageSize) => {
              setPagination({ ...pagination, current: page, pageSize: pageSize || 20 })
              loadScripts(page, pageSize)
            },
            onShowSizeChange: (current, size) => {
              setPagination({ ...pagination, current: 1, pageSize: size })
              loadScripts(1, size)
            },
          }}
        />
      </Card>

      <Modal
        title="新建脚本"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false)
          form.resetFields()
          setFileList([])
          setValidationResult(null)
          setForceCreate(false)
          setValidating(false)  // 重置验证状态
        }}
        onOk={() => form.submit()}
        confirmLoading={uploading}
        okButtonProps={{
          // 修复：只有在验证中，或者验证未通过且未勾选强制保存时才禁用
          disabled: validating || (validationResult && !validationResult.passed && !forceCreate),
        }}
        okText="确定"
        cancelText="取消"
        width={700}
        bodyStyle={{ maxHeight: '70vh', overflowY: 'auto' }}
      >
        <Form form={form} layout="vertical" onFinish={handleCreateScript}>
          <Form.Item
            label="脚本名称"
            name="name"
            rules={[{ required: true, message: '请输入脚本名称' }]}
          >
            <Input placeholder="输入脚本名称" />
          </Form.Item>

          <Form.Item
            label="脚本类型"
            name="type"
            rules={[{ required: true, message: '请选择脚本类型' }]}
          >
            <Select
              placeholder="选择脚本类型"
              onChange={(value) => {
                if (value !== 'visual') {
                  setFileList([])
                }
              }}
            >
              <Select.Option value="visual">
                <Space>
                  <FileTextOutlined />
                  可视化脚本
                </Space>
              </Select.Option>
              <Select.Option value="python">
                <Space>
                  <CodeOutlined />
                  Python 脚本 (.py)
                </Space>
              </Select.Option>
              <Select.Option value="batch">
                <Space>
                  <FileOutlined />
                  批处理脚本 (.bat)
                </Space>
              </Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="脚本分类"
            name="category"
            rules={[{ required: true, message: '请选择脚本分类' }]}
          >
            <Select placeholder="选择脚本分类">
              <Select.Option value="login">登录</Select.Option>
              <Select.Option value="test">测试</Select.Option>
              <Select.Option value="automation">自动化</Select.Option>
              <Select.Option value="other">其他</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item label="脚本描述" name="description">
            <Input.TextArea rows={3} placeholder="输入脚本描述（可选）" />
          </Form.Item>

          <Form.Item noStyle shouldUpdate={(prev, curr) => prev.type !== curr.type}>
            {({ getFieldValue }) => {
              const scriptType = getFieldValue('type')
              if (scriptType === 'python' || scriptType === 'batch') {
                return (
                  <Form.Item
                    label="上传脚本文件"
                    name="file"
                    rules={[{ required: true, message: '请上传脚本文件' }]}
                  >
                    <Upload
                      fileList={fileList}
                      beforeUpload={(file) => {
                        const isPy = file.name.endsWith('.py')
                        const isBat = file.name.endsWith('.bat')
                        if (scriptType === 'python' && !isPy) {
                          message.error('只能上传 .py 文件！')
                          return false
                        }
                        if (scriptType === 'batch' && !isBat) {
                          message.error('只能上传 .bat 文件！')
                          return false
                        }
                        setFileList([file])
                        setValidationResult(null)
                        // 自动触发验证
                        validateScript(file, scriptType)
                        return false
                      }}
                      onRemove={() => {
                        setFileList([])
                        setValidationResult(null)
                      }}
                      maxCount={1}
                    >
                      <Button icon={<UploadOutlined />}>
                        选择文件 ({scriptType === 'python' ? '.py' : '.bat'})
                      </Button>
                    </Upload>
                  </Form.Item>
                )
              }
              return null
            }}
          </Form.Item>

          {/* 显示验证结果 */}
          <Form.Item noStyle shouldUpdate={(prev, curr) => prev.type !== curr.type}>
            {({ getFieldValue }) => {
              const scriptType = getFieldValue('type')
              if (scriptType === 'python' || scriptType === 'batch') {
                return (
                  <>
                    <ScriptValidator
                      result={validationResult}
                      loading={validating}
                      onRevalidate={() => {
                        if (fileList.length > 0) {
                          const file = fileList[0].originFileObj as File
                          validateScript(file, scriptType)
                        }
                      }}
                    />
                    {validationResult && !validationResult.passed && (
                      <div style={{ marginTop: 16, padding: '12px', background: '#fff3cd', border: '1px solid #ffc107', borderRadius: 4 }}>
                        <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                          <input
                            type="checkbox"
                            checked={forceCreate}
                            onChange={(e) => setForceCreate(e.target.checked)}
                            style={{ marginRight: 8 }}
                          />
                          <span style={{ color: '#856404', fontWeight: 500 }}>
                            ⚠️ 我了解风险，忽略警告并强制保存
                          </span>
                        </label>
                        <div style={{ marginTop: 8, fontSize: 12, color: '#856404' }}>
                          注意：保存包含安全风险的脚本可能导致系统安全问题，请谨慎操作。
                        </div>
                      </div>
                    )}
                  </>
                )
              }
              return null
            }}
          </Form.Item>
        </Form>
      </Modal>

      {/* 执行脚本弹窗 */}
      <Modal
        title={`执行脚本 - ${selectedScript?.name}`}
        open={executeModalVisible}
        onCancel={() => {
          setExecuteModalVisible(false)
          setSelectedScript(null)
        }}
        footer={null}
        width={500}
      >
        <Form
          layout="vertical"
          onFinish={handleExecuteScript}
          initialValues={{ device_id: devices[0]?.id }}
        >
          <Form.Item
            label="选择设备"
            name="device_id"
            rules={[{ required: true, message: '请选择执行设备' }]}
          >
            <Select
              placeholder="选择在线设备"
              disabled={!devices.length}
              notFoundContent={devices.length === 0 ? "暂无在线设备" : "暂无数据"}
            >
              {devices.map((device) => (
                <Select.Option key={device.id} value={device.id}>
                  <Space>
                    <span>{device.serial_number}</span>
                    <Tag color="green" size="small">
                      {device.model}
                    </Tag>
                  </Space>
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          {selectedScript && (
            <div style={{ marginBottom: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
              <div style={{ marginBottom: 8 }}>
                <strong>脚本信息：</strong>
              </div>
              <div style={{ fontSize: 13, color: '#666' }}>
                <div>名称：{selectedScript.name}</div>
                <div>类型：{scriptTypeMap[selectedScript.type as ScriptType]?.text || selectedScript.type}</div>
                <div>分类：{categoryMap[selectedScript.category as ScriptCategory]?.text || selectedScript.category}</div>
                {selectedScript.description && (
                  <div>描述：{selectedScript.description}</div>
                )}
              </div>
            </div>
          )}

          {devices.length === 0 && (
            <div style={{ marginBottom: 16, padding: 12, background: '#fff3cd', border: '1px solid #ffc107', borderRadius: 4 }}>
              <div style={{ color: '#856404', fontSize: 13 }}>
                ⚠️ 暂无在线设备，无法执行脚本。请确保至少有一台设备在线。
              </div>
            </div>
          )}

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setExecuteModalVisible(false)}>
                取消
              </Button>
              <Button
                type="primary"
                htmlType="submit"
                loading={executing}
                disabled={!devices.length}
                icon={<PlayCircleOutlined />}
              >
                {executing ? '执行中...' : '开始执行'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ScriptList
