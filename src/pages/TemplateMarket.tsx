import { useState, useEffect } from 'react'
import { Card, Row, Col, Button, Tag, Space, Modal, message, Input, Form, Select, Spin } from 'antd'
import {
  DownloadOutlined,
  StarOutlined,
  EyeOutlined,
  SearchOutlined,
} from '@ant-design/icons'
import { templateApi, Template } from '../services/api'

const TemplateMarket = () => {
  const [searchText, setSearchText] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(false)
  const [downloadModalVisible, setDownloadModalVisible] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [downloadForm] = Form.useForm()
  const [downloading, setDownloading] = useState(false)

  const categories = ['all', '性能测试', '功能测试', 'UI测试', '设备管理', '兼容性测试']

  // 加载模板列表
  const loadTemplates = async () => {
    try {
      setLoading(true)
      const params: any = {
        page: 1,
        page_size: 100, // 加载所有模板
      }
      
      if (selectedCategory !== 'all') {
        params.category = selectedCategory
      }
      
      if (searchText) {
        params.keyword = searchText
      }

      const response = await templateApi.getList(params)
      setTemplates(response.items)
    } catch (error) {
      message.error('加载模板列表失败')
      console.error('Failed to load templates:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTemplates()
  }, [selectedCategory, searchText])

  const handleDownloadClick = (template: Template) => {
    setSelectedTemplate(template)
    setDownloadModalVisible(true)
    downloadForm.setFieldsValue({
      script_name: template.name,
      category: 'other',
    })
  }

  const handleDownloadConfirm = async (values: any) => {
    if (!selectedTemplate) return

    try {
      setDownloading(true)
      await templateApi.download(selectedTemplate.id, {
        script_name: values.script_name,
        category: values.category,
      })
      
      message.success(`模板 "${selectedTemplate.name}" 已添加到脚本列表！下载量 +1`)
      setDownloadModalVisible(false)
      downloadForm.resetFields()
      
      // 重新加载模板列表以更新下载量
      loadTemplates()
    } catch (error) {
      message.error('下载模板失败')
      console.error('Failed to download template:', error)
    } finally {
      setDownloading(false)
    }
  }

  const handlePreview = (template: Template) => {
    Modal.info({
      title: `预览 - ${template.name}`,
      width: 800,
      content: (
        <div style={{ marginTop: 16 }}>
          <div style={{ marginBottom: 16 }}>
            <strong>描述：</strong>
            <p style={{ marginTop: 8, color: '#9ca3af' }}>{template.description}</p>
          </div>
          <div style={{ marginBottom: 16 }}>
            <strong>作者：</strong>
            <span style={{ marginLeft: 8, color: '#9ca3af' }}>{template.author}</span>
          </div>
          <div style={{ marginBottom: 16 }}>
            <strong>分类：</strong>
            <span style={{ marginLeft: 8, color: '#9ca3af' }}>{template.category}</span>
          </div>
          <div style={{ marginBottom: 16 }}>
            <strong>标签：</strong>
            <div style={{ marginTop: 8 }}>
              <Space wrap>
                {template.tags.split(',').map((tag) => (
                  <Tag key={tag} color="blue">
                    {tag.trim()}
                  </Tag>
                ))}
              </Space>
            </div>
          </div>
          <div>
            <strong>代码预览：</strong>
            <pre
              style={{
                marginTop: 8,
                background: '#1f1f1f',
                padding: 16,
                borderRadius: 8,
                color: '#4ade80',
                fontFamily: 'Consolas, Monaco, monospace',
                maxHeight: 300,
                overflow: 'auto',
              }}
            >
              {template.preview || template.content}
            </pre>
          </div>
        </div>
      ),
    })
  }

  const getTypeTag = (type: Template['type']) => {
    const typeMap = {
      visual: { color: 'blue', text: '可视化' },
      python: { color: 'green', text: 'Python' },
      batch: { color: 'orange', text: '批处理' },
    }
    return <Tag color={typeMap[type].color}>{typeMap[type].text}</Tag>
  }

  if (loading && templates.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    )
  }

  return (
    <div>
      <h2 style={{ margin: 0, fontSize: 24, fontWeight: 600, marginBottom: 16 }}>
        脚本模板市场
      </h2>

      <Card
        style={{
          background: '#fff',
          border: '1px solid #e8e8e8',
          marginBottom: 16,
        }}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Input
            placeholder="搜索模板名称、描述或标签..."
            prefix={<SearchOutlined />}
            size="large"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            allowClear
          />

          <Space wrap>
            {categories.map((cat) => (
              <Button
                key={cat}
                type={selectedCategory === cat ? 'primary' : 'default'}
                onClick={() => setSelectedCategory(cat)}
              >
                {cat === 'all' ? '全部' : cat}
              </Button>
            ))}
          </Space>
        </Space>
      </Card>

      <Row gutter={[16, 16]}>
        {templates.map((template) => (
          <Col xs={24} sm={12} lg={8} key={template.id}>
            <Card
              hoverable
              style={{
                background: '#fff',
                border: '1px solid #e8e8e8',
                height: '100%',
              }}
              actions={[
                <Button
                  type="link"
                  icon={<EyeOutlined />}
                  onClick={() => handlePreview(template)}
                >
                  预览
                </Button>,
                <Button
                  type="link"
                  icon={<DownloadOutlined />}
                  onClick={() => handleDownloadClick(template)}
                >
                  下载
                </Button>,
              ]}
            >
              <div style={{ marginBottom: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <h3 style={{ margin: 0, fontSize: 18, fontWeight: 600 }}>
                    {template.name}
                  </h3>
                  {getTypeTag(template.type)}
                </div>
              </div>

              <p style={{ color: '#9ca3af', fontSize: 14, marginBottom: 12, minHeight: 60 }}>
                {template.description}
              </p>

              <div style={{ marginBottom: 12 }}>
                <Space wrap>
                  {template.tags.split(',').slice(0, 3).map((tag) => (
                    <Tag key={tag} color="blue" style={{ margin: 0 }}>
                      {tag.trim()}
                    </Tag>
                  ))}
                </Space>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: '#9ca3af' }}>
                <span>
                  <DownloadOutlined /> {template.downloads}
                </span>
                <span>
                  <StarOutlined /> {template.rating.toFixed(1)}
                </span>
                <span>作者: {template.author}</span>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {templates.length === 0 && !loading && (
        <Card
          style={{
            background: '#fff',
            border: '1px solid #e8e8e8',
            textAlign: 'center',
            padding: 60,
          }}
        >
          <div style={{ color: '#666', fontSize: 16 }}>
            <SearchOutlined style={{ fontSize: 48, marginBottom: 16 }} />
            <div>未找到匹配的模板</div>
          </div>
        </Card>
      )}

      {/* 下载模板对话框 */}
      <Modal
        title={`下载模板 - ${selectedTemplate?.name}`}
        open={downloadModalVisible}
        onCancel={() => {
          setDownloadModalVisible(false)
          downloadForm.resetFields()
        }}
        onOk={() => downloadForm.submit()}
        confirmLoading={downloading}
        okText="下载"
        cancelText="取消"
      >
        {selectedTemplate && (
          <div>
            <div style={{ marginBottom: 16, padding: 12, background: '#fff', borderRadius: 8 }}>
              <div style={{ marginBottom: 8 }}>
                <strong>作者：</strong> {selectedTemplate.author}
              </div>
              <div style={{ marginBottom: 8 }}>
                <strong>类型：</strong> {selectedTemplate.type}
              </div>
              <div style={{ marginBottom: 8 }}>
                <strong>下载量：</strong> {selectedTemplate.downloads}
              </div>
              <div>
                <strong>评分：</strong> {selectedTemplate.rating.toFixed(1)} ⭐
              </div>
            </div>

            <Form form={downloadForm} layout="vertical" onFinish={handleDownloadConfirm}>
              <Form.Item
                label="脚本名称"
                name="script_name"
                rules={[{ required: true, message: '请输入脚本名称' }]}
              >
                <Input placeholder="输入脚本名称" />
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
            </Form>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default TemplateMarket
