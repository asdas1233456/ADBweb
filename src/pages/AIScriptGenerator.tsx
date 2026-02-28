import { useState, useEffect } from 'react'
import { Card, Input, Button, Select, message, Alert, Tag, List, Space, Tooltip, Modal, Tabs, Form, InputNumber, Divider, Progress, Collapse, Badge } from 'antd'
import { RobotOutlined, ThunderboltOutlined, BulbOutlined, HistoryOutlined, CopyOutlined, DeleteOutlined, SettingOutlined, BulbTwoTone, SaveOutlined, CheckCircleOutlined, AppstoreOutlined, PlusOutlined, UnorderedListOutlined, NodeIndexOutlined, DownloadOutlined, PlayCircleOutlined } from '@ant-design/icons'
import Editor from '@monaco-editor/react'
import { aiScriptApi, scriptTemplateApi, type AIScriptResponse, type PromptOptimizeResponse, type ScriptValidationResult, type ScriptTemplate, type BatchGenerateResult, type WorkflowGenerateResult } from '../services/api'

const { TextArea } = Input

const AIScriptGenerator = () => {
  const [prompt, setPrompt] = useState('')
  const [language, setLanguage] = useState<'adb' | 'python'>('adb')
  const [loading, setLoading] = useState(false)
  const [generatedScript, setGeneratedScript] = useState('')
  const [suggestions, setSuggestions] = useState<any[]>([])
  const [history, setHistory] = useState<AIScriptResponse[]>([])
  const [aiApiKey, setAiApiKey] = useState(localStorage.getItem('ai_api_key') || '')
  const [aiApiBase, setAiApiBase] = useState(localStorage.getItem('ai_api_base') || 'https://api.deepseek.com/v1')
  const [showApiConfig, setShowApiConfig] = useState(false)
  const [generationMode, setGenerationMode] = useState<string>('')
  const [aiModel, setAiModel] = useState<string>('')
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const [optimizing, setOptimizing] = useState(false)
  const [optimizeResult, setOptimizeResult] = useState<PromptOptimizeResponse | null>(null)
  const [showOptimizeModal, setShowOptimizeModal] = useState(false)
  const [showSaveModal, setShowSaveModal] = useState(false)
  const [saveLoading, setSaveLoading] = useState(false)
  const [validating, setValidating] = useState(false)
  const [validationResult, setValidationResult] = useState<ScriptValidationResult | null>(null)
  const [currentAiScriptId, setCurrentAiScriptId] = useState<number | null>(null)
  const [showTemplateModal, setShowTemplateModal] = useState(false)
  const [templates, setTemplates] = useState<ScriptTemplate[]>([])
  const [templateCategories, setTemplateCategories] = useState<Array<{ name: string; count: number }>>([])
  const [selectedTemplate, setSelectedTemplate] = useState<ScriptTemplate | null>(null)
  const [templateVariables, setTemplateVariables] = useState<Record<string, string>>({})
  const [showCreateTemplateModal, setShowCreateTemplateModal] = useState(false)
  const [createTemplateForm] = Form.useForm()
  
  // 批量生成相关状态
  const [showBatchModal, setShowBatchModal] = useState(false)
  const [batchPrompts, setBatchPrompts] = useState<string[]>([''])
  const [batchGenerating, setBatchGenerating] = useState(false)
  const [batchResult, setBatchResult] = useState<BatchGenerateResult | null>(null)
  const [showWorkflowModal, setShowWorkflowModal] = useState(false)
  const [workflowSteps, setWorkflowSteps] = useState<string[]>([''])
  const [workflowGenerating, setWorkflowGenerating] = useState(false)
  const [workflowResult, setWorkflowResult] = useState<WorkflowGenerateResult | null>(null)

  // 加载历史记录
  useEffect(() => {
    loadHistory()
    loadTemplates()
    loadTemplateCategories()
  }, [])

  const loadHistory = async () => {
    try {
      const data = await aiScriptApi.getHistory(5)  // 只加载5条历史记录
      setHistory(data)
    } catch (error) {
      message.error('加载历史记录失败')
    }
  }

  const loadTemplates = async () => {
    try {
      const data = await scriptTemplateApi.getList({ limit: 50 })
      setTemplates(data)
    } catch (error) {
      console.error('加载模板失败:', error)
    }
  }

  const loadTemplateCategories = async () => {
    try {
      const data = await scriptTemplateApi.getCategories()
      setTemplateCategories(data)
    } catch (error) {
      console.error('加载模板分类失败:', error)
    }
  }

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      message.warning('请输入脚本描述')
      return
    }
    
    const controller = new AbortController()
    setAbortController(controller)
    setLoading(true)
    
    // 清空之前的状态（在loading之后，确保UI更新）
    setGenerationMode('')
    setAiModel('')
    setGeneratedScript('')
    setSuggestions([])
    
    try {
      const result = await aiScriptApi.generate({
        prompt,
        language,
        ai_api_key: aiApiKey || undefined,
        ai_api_base: aiApiBase || undefined,
      })

      setGeneratedScript(result.generated_script)
      setSuggestions(result.optimization_suggestions)
      setCurrentAiScriptId(result.id) // 保存AI脚本ID
      
      // 使用setTimeout确保状态更新不会被批处理合并
      setTimeout(() => {
        const mode = result.generation_mode || 'rule_engine'
        const model = result.ai_model || ''
        setGenerationMode(mode)
        setAiModel(model)
        
        const modeText = mode === 'ai' 
          ? `AI模式 (${model})` 
          : '规则引擎模式'
        message.success(`脚本生成成功！使用: ${modeText}`)
      }, 100)
      
      // 刷新历史记录
      loadHistory()
    } catch (error: any) {
      if (error.name === 'AbortError') {
        message.info('已取消生成')
      } else {
        message.error('脚本生成失败')
      }
    } finally {
      setLoading(false)
      setAbortController(null)
    }
  }

  const handleCancelGenerate = () => {
    if (abortController) {
      abortController.abort()
      setLoading(false)
      setAbortController(null)
    }
  }

  const handleSaveApiConfig = () => {
    localStorage.setItem('ai_api_key', aiApiKey)
    localStorage.setItem('ai_api_base', aiApiBase)
    message.success('AI配置已保存')
    setShowApiConfig(false)
  }

  const handleCopyScript = () => {
    navigator.clipboard.writeText(generatedScript)
    message.success('脚本已复制到剪贴板')
  }

  const handleOptimizePrompt = async () => {
    if (!prompt.trim()) {
      message.warning('请先输入脚本描述')
      return
    }

    setOptimizing(true)
    try {
      const result = await aiScriptApi.optimizePrompt({
        prompt,
        language,
        ai_api_key: aiApiKey || undefined,
        ai_api_base: aiApiBase || undefined,
      })
      setOptimizeResult(result)
      setShowOptimizeModal(true)
    } catch (error) {
      message.error('提示词优化失败')
    } finally {
      setOptimizing(false)
    }
  }

  const handleApplyOptimizedPrompt = () => {
    if (optimizeResult) {
      setPrompt(optimizeResult.optimized_prompt)
      setShowOptimizeModal(false)
      message.success('已应用优化后的提示词')
    }
  }

  const handleValidateScript = async () => {
    if (!currentAiScriptId) {
      message.warning('请先生成脚本')
      return
    }

    setValidating(true)
    try {
      const result = await aiScriptApi.validateGenerated(currentAiScriptId)
      setValidationResult(result)
      
      if (result.passed) {
        message.success(`脚本验证通过！得分: ${result.score}分`)
      } else {
        message.warning(`脚本验证未通过，得分: ${result.score}分`)
      }
    } catch (error) {
      message.error('脚本验证失败')
    } finally {
      setValidating(false)
    }
  }

  const handleSaveScript = () => {
    if (!currentAiScriptId) {
      message.warning('请先生成脚本')
      return
    }
    setShowSaveModal(true)
  }

  const handleConfirmSave = async (values: any) => {
    if (!currentAiScriptId) return

    setSaveLoading(true)
    try {
      const result = await aiScriptApi.saveToScripts({
        ai_script_id: currentAiScriptId,
        name: values.name,
        category: values.category,
        description: values.description,
      })
      
      message.success(`脚本已保存到脚本管理！ID: ${result.script_id}`)
      setShowSaveModal(false)
    } catch (error) {
      message.error('保存脚本失败')
    } finally {
      setSaveLoading(false)
    }
  }

  const handleUseTemplate = async (template: ScriptTemplate) => {
    setSelectedTemplate(template)
    
    // 初始化模板变量
    const variables: Record<string, string> = {}
    if (template.variables) {
      Object.entries(template.variables).forEach(([key, config]) => {
        variables[key] = config.default || ''
      })
    }
    setTemplateVariables(variables)
    
    // 如果没有变量，直接使用模板
    if (!template.variables || Object.keys(template.variables).length === 0) {
      try {
        const result = await scriptTemplateApi.use({ template_id: template.id })
        setPrompt(`使用模板: ${template.name}`)
        setGeneratedScript(result.content)
        setLanguage(template.language as 'adb' | 'python')
        message.success(`已使用模板: ${template.name}`)
        setShowTemplateModal(false)
      } catch (error) {
        message.error('使用模板失败')
      }
    }
  }

  const handleApplyTemplate = async () => {
    if (!selectedTemplate) return

    try {
      const result = await scriptTemplateApi.use({
        template_id: selectedTemplate.id,
        variables: templateVariables
      })
      
      setPrompt(`使用模板: ${selectedTemplate.name}`)
      setGeneratedScript(result.content)
      setLanguage(selectedTemplate.language as 'adb' | 'python')
      message.success(`已使用模板: ${selectedTemplate.name}`)
      setShowTemplateModal(false)
      setSelectedTemplate(null)
    } catch (error) {
      message.error('使用模板失败')
    }
  }

  const handleCreateTemplate = async (values: any) => {
    if (!generatedScript) {
      message.warning('请先生成脚本')
      return
    }

    try {
      await scriptTemplateApi.create({
        name: values.name,
        category: values.category,
        description: values.description,
        language: language,
        template_content: generatedScript,
        tags: values.tags ? values.tags.split(',').map((t: string) => t.trim()) : []
      })
      
      message.success('模板创建成功')
      setShowCreateTemplateModal(false)
      createTemplateForm.resetFields()
      loadTemplates()
      loadTemplateCategories()
    } catch (error) {
      message.error('创建模板失败')
    }
  }

  // 批量生成处理函数
  const handleBatchGenerate = async (generateSuite: boolean = false) => {
    const validPrompts = batchPrompts.filter(p => p.trim())
    if (validPrompts.length === 0) {
      message.warning('请至少输入一个提示词')
      return
    }

    setBatchGenerating(true)
    try {
      const result = await aiScriptApi.batchGenerate({
        prompts: validPrompts,
        language,
        generate_suite: generateSuite,
        ai_api_key: aiApiKey || undefined,
        ai_api_base: aiApiBase || undefined,
      })

      setBatchResult(result)
      message.success(`批量生成完成！成功 ${result.statistics.success} 个，失败 ${result.statistics.failed} 个`)
    } catch (error) {
      message.error('批量生成失败')
    } finally {
      setBatchGenerating(false)
    }
  }

  const handleWorkflowGenerate = async () => {
    const validSteps = workflowSteps.filter(s => s.trim())
    if (validSteps.length === 0) {
      message.warning('请至少输入一个工作流步骤')
      return
    }

    setWorkflowGenerating(true)
    try {
      const result = await aiScriptApi.generateWorkflow({
        workflow_steps: validSteps,
        language,
        ai_api_key: aiApiKey || undefined,
        ai_api_base: aiApiBase || undefined,
      })

      setWorkflowResult(result)
      message.success(`工作流生成完成！包含 ${validSteps.length} 个步骤`)
    } catch (error) {
      message.error('工作流生成失败')
    } finally {
      setWorkflowGenerating(false)
    }
  }

  const addBatchPrompt = () => {
    setBatchPrompts([...batchPrompts, ''])
  }

  const removeBatchPrompt = (index: number) => {
    if (batchPrompts.length > 1) {
      setBatchPrompts(batchPrompts.filter((_, i) => i !== index))
    }
  }

  const updateBatchPrompt = (index: number, value: string) => {
    const newPrompts = [...batchPrompts]
    newPrompts[index] = value
    setBatchPrompts(newPrompts)
  }

  const addWorkflowStep = () => {
    setWorkflowSteps([...workflowSteps, ''])
  }

  const removeWorkflowStep = (index: number) => {
    if (workflowSteps.length > 1) {
      setWorkflowSteps(workflowSteps.filter((_, i) => i !== index))
    }
  }

  const updateWorkflowStep = (index: number, value: string) => {
    const newSteps = [...workflowSteps]
    newSteps[index] = value
    setWorkflowSteps(newSteps)
  }

  const downloadScript = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const getSuggestionColor = (type: string) => {
    switch (type) {
      case 'error': return 'red'
      case 'warning': return 'orange'
      case 'info': return 'blue'
      default: return 'default'
    }
  }

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <h2 className="page-title" style={{ margin: 0 }}>
            <RobotOutlined />
            AI脚本生成器
          </h2>
          {aiApiKey && (
            <Tag color="green" icon={<RobotOutlined />}>
              AI已配置
            </Tag>
          )}
          {!aiApiKey && (
            <Tag color="default">
              规则引擎
            </Tag>
          )}
          
          {/* 功能指引图标 */}
          <Tooltip 
            title={
              <div style={{ maxWidth: 300 }}>
                <div style={{ fontWeight: 600, marginBottom: 8 }}>三大核心功能</div>
                <div style={{ marginBottom: 6 }}>
                  <ThunderboltOutlined style={{ color: '#52c41a' }} /> <strong>生成脚本</strong>：单个脚本，智能理解
                </div>
                <div style={{ marginBottom: 6 }}>
                  <UnorderedListOutlined style={{ color: '#fa8c16' }} /> <strong>批量生成</strong>：多脚本并行，高效处理
                </div>
                <div>
                  <NodeIndexOutlined style={{ color: '#1890ff' }} /> <strong>工作流</strong>：步骤关联，端到端测试
                </div>
              </div>
            }
            placement="bottomLeft"
          >
            <Button 
              type="text" 
              icon={<BulbOutlined />} 
              size="small"
              style={{ color: '#1890ff' }}
            >
              功能说明
            </Button>
          </Tooltip>
        </div>
        <Button
          icon={<SettingOutlined />}
          onClick={() => setShowApiConfig(true)}
        >
          AI配置
        </Button>
      </div>

      {/* AI配置弹窗 */}
      <Modal
        title="AI API配置"
        open={showApiConfig}
        onOk={handleSaveApiConfig}
        onCancel={() => setShowApiConfig(false)}
        width={600}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Alert
            message="配置说明"
            description={
              <div>
                <p>支持OpenAI兼容的API接口，如DeepSeek、OpenAI等。</p>
                <p>如果不配置，将使用规则引擎生成脚本。</p>
                <p><strong>推荐使用DeepSeek API</strong>（性价比高）：</p>
                <ul>
                  <li>API Base: https://api.deepseek.com/v1</li>
                  <li>获取API Key: <a href="https://platform.deepseek.com" target="_blank" rel="noopener noreferrer">https://platform.deepseek.com</a></li>
                </ul>
              </div>
            }
            type="info"
            showIcon
          />
          
          <div>
            <div style={{ marginBottom: 8, fontWeight: 500 }}>API Key</div>
            <Input.Password
              value={aiApiKey}
              onChange={(e) => setAiApiKey(e.target.value)}
              placeholder="输入你的AI API Key"
            />
          </div>

          <div>
            <div style={{ marginBottom: 8, fontWeight: 500 }}>API Base URL</div>
            <Input
              value={aiApiBase}
              onChange={(e) => setAiApiBase(e.target.value)}
              placeholder="https://api.deepseek.com/v1"
            />
          </div>
        </Space>
      </Modal>

      {/* 优化提示词弹窗 */}
      <Modal
        title={
          <Space>
            <BulbTwoTone twoToneColor="#52c41a" />
            <span>提示词优化建议</span>
            {aiApiKey ? (
              <Tag color="green" style={{ fontSize: 11 }}>AI模式</Tag>
            ) : (
              <Tag color="default" style={{ fontSize: 11 }}>规则引擎</Tag>
            )}
          </Space>
        }
        open={showOptimizeModal}
        onCancel={() => setShowOptimizeModal(false)}
        width={700}
        footer={[
          <Button key="cancel" onClick={() => setShowOptimizeModal(false)}>
            取消
          </Button>,
          <Button key="apply" type="primary" onClick={handleApplyOptimizedPrompt}>
            应用优化后的提示词
          </Button>,
        ]}
      >
        {optimizeResult && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* 原始提示词 */}
            <div>
              <div style={{ marginBottom: 8, fontWeight: 500, color: '#666' }}>原始提示词</div>
              <div style={{ 
                padding: 12, 
                background: '#f5f5f5', 
                borderRadius: 4,
                fontSize: 14
              }}>
                {optimizeResult.original_prompt}
              </div>
            </div>

            {/* 优化后的提示词 */}
            <div>
              <div style={{ marginBottom: 8, fontWeight: 500, color: '#52c41a' }}>
                ✨ 优化后的提示词
              </div>
              <div style={{ 
                padding: 12, 
                background: '#f6ffed', 
                border: '1px solid #b7eb8f',
                borderRadius: 4,
                fontSize: 14
              }}>
                {optimizeResult.optimized_prompt}
              </div>
            </div>

            {/* 改进建议 */}
            {optimizeResult.improvements.length > 0 && (
              <div>
                <div style={{ marginBottom: 8, fontWeight: 500 }}>💡 改进建议</div>
                <List
                  size="small"
                  bordered
                  dataSource={optimizeResult.improvements}
                  renderItem={(item, index) => (
                    <List.Item>
                      <Space>
                        <Tag color="blue">{index + 1}</Tag>
                        <span>{item}</span>
                      </Space>
                    </List.Item>
                  )}
                />
              </div>
            )}

            {/* 缺失信息 */}
            {optimizeResult.missing_info.length > 0 && (
              <div>
                <div style={{ marginBottom: 8, fontWeight: 500 }}>⚠️ 缺失的关键信息</div>
                <List
                  size="small"
                  bordered
                  dataSource={optimizeResult.missing_info}
                  renderItem={(item, index) => (
                    <List.Item>
                      <Space>
                        <Tag color="orange">{index + 1}</Tag>
                        <span>{item}</span>
                      </Space>
                    </List.Item>
                  )}
                />
              </div>
            )}
          </Space>
        )}
      </Modal>

      {/* 保存脚本弹窗 */}
      <Modal
        title={<><SaveOutlined /> 保存到脚本管理</>}
        open={showSaveModal}
        onCancel={() => setShowSaveModal(false)}
        width={500}
        footer={null}
      >
        <div style={{ padding: '16px 0' }}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <div>
              <div style={{ marginBottom: 8, fontWeight: 500 }}>脚本名称</div>
              <Input
                placeholder="输入脚本名称"
                id="script-name"
                maxLength={100}
              />
            </div>

            <div>
              <div style={{ marginBottom: 8, fontWeight: 500 }}>脚本分类</div>
              <Select
                placeholder="选择分类"
                style={{ width: '100%' }}
                id="script-category"
                defaultValue="automation"
                options={[
                  { label: '自动化测试', value: 'automation' },
                  { label: '登录测试', value: 'login' },
                  { label: '功能测试', value: 'test' },
                  { label: '其他', value: 'other' },
                ]}
              />
            </div>

            <div>
              <div style={{ marginBottom: 8, fontWeight: 500 }}>脚本描述</div>
              <Input.TextArea
                placeholder="输入脚本描述（可选）"
                rows={3}
                id="script-description"
                maxLength={500}
              />
            </div>

            <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
              <Button onClick={() => setShowSaveModal(false)}>
                取消
              </Button>
              <Button
                type="primary"
                loading={saveLoading}
                onClick={() => {
                  const name = (document.getElementById('script-name') as HTMLInputElement)?.value
                  const category = (document.getElementById('script-category') as any)?.value || 'automation'
                  const description = (document.getElementById('script-description') as HTMLTextAreaElement)?.value

                  if (!name?.trim()) {
                    message.warning('请输入脚本名称')
                    return
                  }

                  handleConfirmSave({ name: name.trim(), category, description: description?.trim() })
                }}
              >
                保存脚本
              </Button>
            </div>
          </Space>
        </div>
      </Modal>

      {/* 模板选择弹窗 */}
      <Modal
        title={<><AppstoreOutlined /> 选择脚本模板</>}
        open={showTemplateModal}
        onCancel={() => {
          setShowTemplateModal(false)
          setSelectedTemplate(null)
        }}
        width={800}
        footer={
          selectedTemplate && selectedTemplate.variables && Object.keys(selectedTemplate.variables).length > 0 ? [
            <Button key="cancel" onClick={() => setShowTemplateModal(false)}>
              取消
            </Button>,
            <Button key="apply" type="primary" onClick={handleApplyTemplate}>
              使用模板
            </Button>,
          ] : null
        }
      >
        <Tabs
          items={[
            {
              key: 'all',
              label: `全部 (${templates.length})`,
              children: (
                <div style={{ maxHeight: 400, overflowY: 'auto' }}>
                  <List
                    size="small"
                    dataSource={templates}
                    renderItem={(template) => (
                      <List.Item
                        style={{ padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}
                        actions={[
                          <Button
                            type="link"
                            size="small"
                            onClick={() => handleUseTemplate(template)}
                          >
                            使用
                          </Button>
                        ]}
                      >
                        <List.Item.Meta
                          title={
                            <Space>
                              <span style={{ fontSize: 14, fontWeight: 500 }}>{template.name}</span>
                              <Tag color="blue" style={{ fontSize: 11 }}>{template.language}</Tag>
                              <Tag color="green" style={{ fontSize: 11 }}>{template.category}</Tag>
                              {template.is_builtin && (
                                <Tag color="gold" style={{ fontSize: 11 }}>内置</Tag>
                              )}
                            </Space>
                          }
                          description={
                            <div>
                              <div style={{ fontSize: 12, color: '#666', marginBottom: 4 }}>
                                {template.description}
                              </div>
                              <Space size={4}>
                                {template.tags?.map(tag => (
                                  <Tag key={tag} style={{ fontSize: 10 }}>{tag}</Tag>
                                ))}
                                <span style={{ fontSize: 11, color: '#999' }}>
                                  使用次数: {template.usage_count}
                                </span>
                              </Space>
                            </div>
                          }
                        />
                      </List.Item>
                    )}
                  />
                </div>
              )
            },
            ...templateCategories.map(category => ({
              key: category.name,
              label: `${category.name} (${category.count})`,
              children: (
                <div style={{ maxHeight: 400, overflowY: 'auto' }}>
                  <List
                    size="small"
                    dataSource={templates.filter(t => t.category === category.name)}
                    renderItem={(template) => (
                      <List.Item
                        style={{ padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}
                        actions={[
                          <Button
                            type="link"
                            size="small"
                            onClick={() => handleUseTemplate(template)}
                          >
                            使用
                          </Button>
                        ]}
                      >
                        <List.Item.Meta
                          title={
                            <Space>
                              <span style={{ fontSize: 14, fontWeight: 500 }}>{template.name}</span>
                              <Tag color="blue" style={{ fontSize: 11 }}>{template.language}</Tag>
                              {template.is_builtin && (
                                <Tag color="gold" style={{ fontSize: 11 }}>内置</Tag>
                              )}
                            </Space>
                          }
                          description={
                            <div>
                              <div style={{ fontSize: 12, color: '#666', marginBottom: 4 }}>
                                {template.description}
                              </div>
                              <Space size={4}>
                                {template.tags?.map(tag => (
                                  <Tag key={tag} style={{ fontSize: 10 }}>{tag}</Tag>
                                ))}
                                <span style={{ fontSize: 11, color: '#999' }}>
                                  使用次数: {template.usage_count}
                                </span>
                              </Space>
                            </div>
                          }
                        />
                      </List.Item>
                    )}
                  />
                </div>
              )
            }))
          ]}
        />
        
        {/* 模板变量配置 */}
        {selectedTemplate && selectedTemplate.variables && Object.keys(selectedTemplate.variables).length > 0 && (
          <div style={{ marginTop: 16, padding: 16, background: '#f9f9f9', borderRadius: 4 }}>
            <div style={{ marginBottom: 12, fontWeight: 500 }}>配置模板变量</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
              {Object.entries(selectedTemplate.variables).map(([key, config]) => (
                <div key={key}>
                  <div style={{ marginBottom: 4, fontSize: 12 }}>
                    {config.description}
                    {config.required && <span style={{ color: 'red' }}>*</span>}
                  </div>
                  {config.type === 'number' ? (
                    <InputNumber
                      size="small"
                      style={{ width: '100%' }}
                      value={Number(templateVariables[key]) || Number(config.default) || 0}
                      onChange={(value) => setTemplateVariables(prev => ({
                        ...prev,
                        [key]: String(value || 0)
                      }))}
                    />
                  ) : config.type === 'text' ? (
                    <Input.TextArea
                      size="small"
                      rows={2}
                      value={templateVariables[key] || config.default}
                      onChange={(e) => setTemplateVariables(prev => ({
                        ...prev,
                        [key]: e.target.value
                      }))}
                    />
                  ) : (
                    <Input
                      size="small"
                      value={templateVariables[key] || config.default}
                      onChange={(e) => setTemplateVariables(prev => ({
                        ...prev,
                        [key]: e.target.value
                      }))}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </Modal>

      {/* 创建模板弹窗 */}
      <Modal
        title={<><PlusOutlined /> 创建脚本模板</>}
        open={showCreateTemplateModal}
        onCancel={() => {
          setShowCreateTemplateModal(false)
          createTemplateForm.resetFields()
        }}
        width={600}
        footer={null}
      >
        <Form
          form={createTemplateForm}
          layout="vertical"
          onFinish={handleCreateTemplate}
        >
          <Form.Item
            name="name"
            label="模板名称"
            rules={[{ required: true, message: '请输入模板名称' }]}
          >
            <Input placeholder="输入模板名称" maxLength={100} />
          </Form.Item>

          <Form.Item
            name="category"
            label="模板分类"
            rules={[{ required: true, message: '请选择模板分类' }]}
          >
            <Select
              placeholder="选择分类"
              options={[
                { label: '登录测试', value: '登录测试' },
                { label: '功能测试', value: '功能测试' },
                { label: '自动化测试', value: '自动化测试' },
                { label: '性能测试', value: '性能测试' },
                { label: '其他', value: '其他' },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="description"
            label="模板描述"
          >
            <Input.TextArea
              placeholder="输入模板描述（可选）"
              rows={3}
              maxLength={500}
            />
          </Form.Item>

          <Form.Item
            name="tags"
            label="标签"
          >
            <Input
              placeholder="输入标签，用逗号分隔（可选）"
              maxLength={200}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setShowCreateTemplateModal(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                创建模板
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 批量生成弹窗 */}
      <Modal
        title={<><UnorderedListOutlined /> 批量脚本生成</>}
        open={showBatchModal}
        onCancel={() => {
          setShowBatchModal(false)
          setBatchResult(null)
        }}
        width={900}
        footer={null}
      >
        {!aiApiKey && (
          <Alert
            message="建议配置AI Token"
            description={
              <div>
                <p>批量生成功能在AI模式下效果更佳，建议先配置AI Token：</p>
                <ul style={{ marginBottom: 0 }}>
                  <li>AI模式：智能理解复杂场景，生成质量更高</li>
                  <li>规则引擎：仅支持基础关键词匹配，可能生成失败</li>
                </ul>
              </div>
            }
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
            action={
              <Button size="small" onClick={() => setShowApiConfig(true)}>
                配置AI
              </Button>
            }
          />
        )}
        
        <Tabs
          items={[
            {
              key: 'input',
              label: '输入提示词',
              children: (
                <div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ marginBottom: 8, fontWeight: 500 }}>批量提示词</div>
                    <div style={{ fontSize: 12, color: '#666', marginBottom: 12 }}>
                      输入多个脚本描述，系统将并发生成多个脚本。
                      <br />
                      <strong>示例：</strong>
                      <div style={{ marginTop: 4, padding: 8, background: '#f9f9f9', borderRadius: 4, fontSize: 11 }}>
                        1. 测试用户登录功能<br />
                        2. 测试商品搜索功能<br />
                        3. 测试购物车添加商品<br />
                        4. 测试订单提交流程
                      </div>
                    </div>
                    
                    <Space direction="vertical" style={{ width: '100%' }} size="small">
                      {batchPrompts.map((prompt, index) => (
                        <div key={index} style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                          <div style={{ 
                            minWidth: 24, 
                            height: 32, 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center',
                            background: '#f0f0f0',
                            borderRadius: 4,
                            fontSize: 12,
                            fontWeight: 500
                          }}>
                            {index + 1}
                          </div>
                          <Input.TextArea
                            value={prompt}
                            onChange={(e) => updateBatchPrompt(index, e.target.value)}
                            placeholder={`输入第 ${index + 1} 个脚本描述...`}
                            rows={2}
                            style={{ flex: 1 }}
                          />
                          <Button
                            type="text"
                            danger
                            icon={<DeleteOutlined />}
                            onClick={() => removeBatchPrompt(index)}
                            disabled={batchPrompts.length === 1}
                            style={{ marginTop: 4 }}
                          />
                        </div>
                      ))}
                    </Space>

                    <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
                      <Button
                        type="dashed"
                        icon={<PlusOutlined />}
                        onClick={addBatchPrompt}
                        block
                      >
                        添加提示词
                      </Button>
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
                    <Button onClick={() => setShowBatchModal(false)}>
                      取消
                    </Button>
                    <Button
                      onClick={() => handleBatchGenerate(false)}
                      loading={batchGenerating}
                      disabled={batchPrompts.filter(p => p.trim()).length === 0}
                    >
                      批量生成
                    </Button>
                    <Button
                      type="primary"
                      onClick={() => handleBatchGenerate(true)}
                      loading={batchGenerating}
                      disabled={batchPrompts.filter(p => p.trim()).length === 0}
                    >
                      生成测试套件
                    </Button>
                  </div>
                </div>
              )
            },
            {
              key: 'result',
              label: (
                <Space>
                  <span>生成结果</span>
                  {batchResult && (
                    <Badge count={batchResult.statistics.total} size="small" />
                  )}
                </Space>
              ),
              disabled: !batchResult,
              children: batchResult && (
                <div>
                  {/* 统计信息 */}
                  <Card size="small" style={{ marginBottom: 16 }}>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, textAlign: 'center' }}>
                      <div>
                        <div style={{ fontSize: 20, fontWeight: 600, color: '#1890ff' }}>
                          {batchResult.statistics.total}
                        </div>
                        <div style={{ fontSize: 12, color: '#666' }}>总计</div>
                      </div>
                      <div>
                        <div style={{ fontSize: 20, fontWeight: 600, color: '#52c41a' }}>
                          {batchResult.statistics.success}
                        </div>
                        <div style={{ fontSize: 12, color: '#666' }}>成功</div>
                      </div>
                      <div>
                        <div style={{ fontSize: 20, fontWeight: 600, color: '#ff4d4f' }}>
                          {batchResult.statistics.failed}
                        </div>
                        <div style={{ fontSize: 12, color: '#666' }}>失败</div>
                      </div>
                      <div>
                        <div style={{ fontSize: 20, fontWeight: 600, color: '#722ed1' }}>
                          {(batchResult.statistics.success_rate * 100).toFixed(1)}%
                        </div>
                        <div style={{ fontSize: 12, color: '#666' }}>成功率</div>
                      </div>
                    </div>
                  </Card>

                  {/* 测试套件 */}
                  {batchResult.suite_script && (
                    <Card 
                      size="small" 
                      title="测试套件脚本"
                      extra={
                        <Button
                          type="link"
                          size="small"
                          icon={<DownloadOutlined />}
                          onClick={() => downloadScript(
                            batchResult.suite_script,
                            `test_suite.${language === 'python' ? 'py' : 'sh'}`
                          )}
                        >
                          下载
                        </Button>
                      }
                      style={{ marginBottom: 16 }}
                    >
                      <div style={{ height: 200, border: '1px solid #d9d9d9', borderRadius: 4 }}>
                        <Editor
                          height="100%"
                          language={language === 'python' ? 'python' : 'shell'}
                          value={batchResult.suite_script}
                          theme="vs-light"
                          options={{
                            readOnly: true,
                            minimap: { enabled: false },
                            fontSize: 12,
                            scrollBeyondLastLine: false,
                          }}
                        />
                      </div>
                    </Card>
                  )}

                  {/* 生成结果列表 */}
                  <div style={{ maxHeight: 400, overflowY: 'auto' }}>
                    <Collapse
                      size="small"
                      items={batchResult.results.map((result, index) => ({
                        key: index,
                        label: (
                          <Space>
                            <Tag color={result.status === 'success' ? 'success' : 'error'}>
                              {result.status === 'success' ? '成功' : '失败'}
                            </Tag>
                            <span style={{ fontSize: 13 }}>
                              {result.prompt.length > 50 
                                ? `${result.prompt.substring(0, 50)}...` 
                                : result.prompt}
                            </span>
                          </Space>
                        ),
                        children: (
                          <div>
                            <div style={{ marginBottom: 8, fontSize: 12, color: '#666' }}>
                              提示词: {result.prompt}
                            </div>
                            
                            {result.status === 'success' ? (
                              <div>
                                <div style={{ height: 200, border: '1px solid #d9d9d9', borderRadius: 4, marginBottom: 8 }}>
                                  <Editor
                                    height="100%"
                                    language={language === 'python' ? 'python' : 'shell'}
                                    value={result.script}
                                    theme="vs-light"
                                    options={{
                                      readOnly: true,
                                      minimap: { enabled: false },
                                      fontSize: 12,
                                      scrollBeyondLastLine: false,
                                    }}
                                  />
                                </div>
                                
                                <div style={{ display: 'flex', gap: 8 }}>
                                  <Button
                                    size="small"
                                    icon={<CopyOutlined />}
                                    onClick={() => {
                                      navigator.clipboard.writeText(result.script)
                                      message.success('脚本已复制')
                                    }}
                                  >
                                    复制脚本
                                  </Button>
                                  <Button
                                    size="small"
                                    icon={<DownloadOutlined />}
                                    onClick={() => downloadScript(
                                      result.script,
                                      `script_${index + 1}.${language === 'python' ? 'py' : 'sh'}`
                                    )}
                                  >
                                    下载
                                  </Button>
                                </div>
                              </div>
                            ) : (
                              <Alert
                                message="生成失败"
                                description={result.error}
                                type="error"
                                showIcon
                                style={{ fontSize: 12 }}
                              />
                            )}
                          </div>
                        )
                      }))}
                    />
                  </div>
                </div>
              )
            }
          ]}
        />
      </Modal>

      {/* 工作流生成弹窗 */}
      <Modal
        title={<><NodeIndexOutlined /> 工作流脚本生成</>}
        open={showWorkflowModal}
        onCancel={() => {
          setShowWorkflowModal(false)
          setWorkflowResult(null)
        }}
        width={900}
        footer={null}
      >
        {!aiApiKey && (
          <Alert
            message="建议配置AI Token"
            description={
              <div>
                <p>工作流生成功能在AI模式下效果更佳，建议先配置AI Token：</p>
                <ul style={{ marginBottom: 0 }}>
                  <li>AI模式：理解步骤间依赖关系，生成连贯的工作流</li>
                  <li>规则引擎：仅支持简单步骤，复杂工作流可能失败</li>
                </ul>
              </div>
            }
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
            action={
              <Button size="small" onClick={() => setShowApiConfig(true)}>
                配置AI
              </Button>
            }
          />
        )}
        
        <Tabs
          items={[
            {
              key: 'input',
              label: '配置工作流',
              children: (
                <div>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ marginBottom: 8, fontWeight: 500 }}>工作流步骤</div>
                    <div style={{ fontSize: 12, color: '#666', marginBottom: 12 }}>
                      按顺序输入工作流步骤，系统将生成有依赖关系的组合脚本。
                      <br />
                      <strong>示例：</strong>
                      <div style={{ marginTop: 4, padding: 8, background: '#f9f9f9', borderRadius: 4, fontSize: 11 }}>
                        1. 打开应用并登录账户<br />
                        2. 搜索目标商品<br />
                        3. 将商品添加到购物车<br />
                        4. 进入购物车结算<br />
                        5. 完成支付并验证订单
                      </div>
                    </div>
                    
                    <Space direction="vertical" style={{ width: '100%' }} size="small">
                      {workflowSteps.map((step, index) => (
                        <div key={index} style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                          <div style={{ 
                            minWidth: 32, 
                            height: 32, 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center',
                            background: '#1890ff',
                            color: 'white',
                            borderRadius: 4,
                            fontSize: 12,
                            fontWeight: 500
                          }}>
                            {index + 1}
                          </div>
                          <Input.TextArea
                            value={step}
                            onChange={(e) => updateWorkflowStep(index, e.target.value)}
                            placeholder={`输入第 ${index + 1} 个步骤描述...`}
                            rows={2}
                            style={{ flex: 1 }}
                          />
                          <Button
                            type="text"
                            danger
                            icon={<DeleteOutlined />}
                            onClick={() => removeWorkflowStep(index)}
                            disabled={workflowSteps.length === 1}
                            style={{ marginTop: 4 }}
                          />
                        </div>
                      ))}
                    </Space>

                    <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
                      <Button
                        type="dashed"
                        icon={<PlusOutlined />}
                        onClick={addWorkflowStep}
                        block
                      >
                        添加步骤
                      </Button>
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
                    <Button onClick={() => setShowWorkflowModal(false)}>
                      取消
                    </Button>
                    <Button
                      type="primary"
                      icon={<PlayCircleOutlined />}
                      onClick={handleWorkflowGenerate}
                      loading={workflowGenerating}
                      disabled={workflowSteps.filter(s => s.trim()).length === 0}
                    >
                      生成工作流
                    </Button>
                  </div>
                </div>
              )
            },
            {
              key: 'result',
              label: (
                <Space>
                  <span>工作流结果</span>
                  {workflowResult && (
                    <Badge count={workflowResult.individual_scripts.length} size="small" />
                  )}
                </Space>
              ),
              disabled: !workflowResult,
              children: workflowResult && (
                <div>
                  {/* 组合脚本 */}
                  <Card 
                    size="small" 
                    title="完整工作流脚本"
                    extra={
                      <Button
                        type="link"
                        size="small"
                        icon={<DownloadOutlined />}
                        onClick={() => downloadScript(
                          workflowResult.combined_script,
                          `workflow.${language === 'python' ? 'py' : 'sh'}`
                        )}
                      >
                        下载
                      </Button>
                    }
                    style={{ marginBottom: 16 }}
                  >
                    <div style={{ height: 300, border: '1px solid #d9d9d9', borderRadius: 4 }}>
                      <Editor
                        height="100%"
                        language={language === 'python' ? 'python' : 'shell'}
                        value={workflowResult.combined_script}
                        theme="vs-light"
                        options={{
                          readOnly: true,
                          minimap: { enabled: false },
                          fontSize: 12,
                          scrollBeyondLastLine: false,
                        }}
                      />
                    </div>
                  </Card>

                  {/* 各步骤脚本 */}
                  <div style={{ maxHeight: 400, overflowY: 'auto' }}>
                    <Collapse
                      size="small"
                      items={workflowResult.individual_scripts.map((script, index) => ({
                        key: index,
                        label: (
                          <Space>
                            <div style={{ 
                              width: 20, 
                              height: 20, 
                              borderRadius: '50%', 
                              background: script.error ? '#ff4d4f' : '#52c41a',
                              color: 'white',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: 11,
                              fontWeight: 500
                            }}>
                              {script.step}
                            </div>
                            <span style={{ fontSize: 13 }}>
                              {script.description.length > 50 
                                ? `${script.description.substring(0, 50)}...` 
                                : script.description}
                            </span>
                          </Space>
                        ),
                        children: (
                          <div>
                            <div style={{ marginBottom: 8, fontSize: 12, color: '#666' }}>
                              步骤描述: {script.description}
                            </div>
                            
                            {script.error ? (
                              <Alert
                                message="生成失败"
                                description={script.error}
                                type="error"
                                showIcon
                                style={{ fontSize: 12 }}
                              />
                            ) : (
                              <div>
                                <div style={{ height: 200, border: '1px solid #d9d9d9', borderRadius: 4, marginBottom: 8 }}>
                                  <Editor
                                    height="100%"
                                    language={language === 'python' ? 'python' : 'shell'}
                                    value={script.script}
                                    theme="vs-light"
                                    options={{
                                      readOnly: true,
                                      minimap: { enabled: false },
                                      fontSize: 12,
                                      scrollBeyondLastLine: false,
                                    }}
                                  />
                                </div>
                                
                                <div style={{ display: 'flex', gap: 8 }}>
                                  <Button
                                    size="small"
                                    icon={<CopyOutlined />}
                                    onClick={() => {
                                      navigator.clipboard.writeText(script.script)
                                      message.success('脚本已复制')
                                    }}
                                  >
                                    复制脚本
                                  </Button>
                                  <Button
                                    size="small"
                                    icon={<DownloadOutlined />}
                                    onClick={() => downloadScript(
                                      script.script,
                                      `step_${script.step}.${language === 'python' ? 'py' : 'sh'}`
                                    )}
                                  >
                                    下载
                                  </Button>
                                </div>
                              </div>
                            )}
                          </div>
                        )
                      }))}
                    />
                  </div>
                </div>
              )
            }
          ]}
        />
      </Modal>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, alignItems: 'start' }}>
        {/* 左侧：输入区域 */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* 脚本生成卡片 */}
          <Card 
            title={
              <Space>
                <ThunderboltOutlined style={{ color: '#1890ff' }} />
                <span>生成脚本</span>
              </Space>
            }
            size="small"
          >
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <div>
                <div style={{ 
                  marginBottom: 8, 
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <span style={{ fontSize: 13, fontWeight: 500 }}>脚本描述</span>
                  <Button
                    type="text"
                    size="small"
                    icon={<BulbTwoTone twoToneColor="#52c41a" />}
                    onClick={handleOptimizePrompt}
                    loading={optimizing}
                    disabled={!prompt.trim() || optimizing}
                    style={{ fontSize: 12 }}
                  >
                    优化
                  </Button>
                </div>
                <TextArea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="例如：测试微信登录功能，包括输入用户名密码、点击登录按钮、验证登录成功"
                  rows={3}
                  maxLength={500}
                  showCount
                  style={{ fontSize: 13 }}
                />
                <div style={{ fontSize: 11, color: '#999', marginTop: 4 }}>
                  💡 提示：描述越详细，生成的脚本越准确。可以包含具体的操作步骤、元素定位、预期结果等。
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 12 }}>
                <div>
                  <div style={{ marginBottom: 6, fontSize: 13, fontWeight: 500 }}>脚本语言</div>
                  <Select
                    value={language}
                    onChange={setLanguage}
                    style={{ width: '100%' }}
                    size="middle"
                    options={[
                      { label: 'ADB Shell', value: 'adb' },
                      { label: 'Python', value: 'python' },
                    ]}
                  />
                </div>
              </div>

              <Space direction="vertical" style={{ width: '100%' }} size="small">
                <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                  <Tooltip 
                    title={
                      <div>
                        <div style={{ fontWeight: 600, marginBottom: 4 }}>生成脚本</div>
                        <div style={{ fontSize: 12 }}>根据描述生成单个完整脚本</div>
                        <div style={{ fontSize: 11, color: '#999', marginTop: 4 }}>
                          支持AI智能理解和规则引擎两种模式
                        </div>
                      </div>
                    }
                  >
                    <Button
                      type="primary"
                      icon={<ThunderboltOutlined />}
                      onClick={handleGenerate}
                      loading={loading}
                      disabled={loading}
                      style={{ flex: 1 }}
                    >
                      {loading ? '生成中...' : '生成脚本'}
                    </Button>
                  </Tooltip>
                  
                  <Tooltip title="选择预设的脚本模板快速开始">
                    <Button
                      icon={<AppstoreOutlined />}
                      onClick={() => setShowTemplateModal(true)}
                      disabled={loading}
                    >
                      模板
                    </Button>
                  </Tooltip>
                </Space>

                <Space style={{ width: '100%' }} size="small">
                  <Tooltip 
                    title={
                      <div>
                        <div style={{ fontWeight: 600, marginBottom: 4 }}>批量生成</div>
                        <div style={{ fontSize: 12 }}>同时生成多个独立脚本</div>
                        <div style={{ fontSize: 11, color: '#999', marginTop: 4 }}>
                          示例：登录测试、搜索测试、支付测试
                        </div>
                      </div>
                    }
                  >
                    <Button
                      icon={<UnorderedListOutlined />}
                      onClick={() => setShowBatchModal(true)}
                      disabled={loading}
                      style={{ flex: 1 }}
                    >
                      批量生成
                    </Button>
                  </Tooltip>
                  <Tooltip 
                    title={
                      <div>
                        <div style={{ fontWeight: 600, marginBottom: 4 }}>工作流生成</div>
                        <div style={{ fontSize: 12 }}>生成有依赖关系的工作流脚本</div>
                        <div style={{ fontSize: 11, color: '#999', marginTop: 4 }}>
                          示例：登录→搜索→购买→支付
                        </div>
                      </div>
                    }
                  >
                    <Button
                      icon={<NodeIndexOutlined />}
                      onClick={() => setShowWorkflowModal(true)}
                      disabled={loading}
                      style={{ flex: 1 }}
                    >
                      工作流
                    </Button>
                  </Tooltip>
                </Space>
                
                {loading && (
                  <Button
                    danger
                    block
                    size="small"
                    onClick={handleCancelGenerate}
                  >
                    取消生成
                  </Button>
                )}
              </Space>
              
              {/* 生成模式提示 */}
              {generationMode && (
                <Alert
                  message={
                    <span style={{ fontSize: 13 }}>
                      {generationMode === 'ai' 
                        ? `🤖 AI模式 ${aiModel ? `(${aiModel})` : ''}` 
                        : '⚙️ 规则引擎模式'}
                    </span>
                  }
                  description={
                    <span style={{ fontSize: 12 }}>
                      {generationMode === 'ai'
                        ? '使用AI智能生成'
                        : '使用规则引擎生成'}
                    </span>
                  }
                  type={generationMode === 'ai' ? 'success' : 'info'}
                  showIcon
                  closable
                  onClose={() => setGenerationMode('')}
                  style={{ marginTop: 0 }}
                />
              )}
            </Space>
          </Card>

          {/* 生成历史 */}
          <Card 
            title={
              <Space>
                <HistoryOutlined style={{ color: '#722ed1' }} />
                <span>生成历史</span>
              </Space>
            }
            size="small"
            extra={
              <Button 
                type="text" 
                size="small" 
                onClick={loadHistory}
                style={{ fontSize: 12 }}
              >
                刷新历史
              </Button>
            }
          >
            <div style={{ maxHeight: 300, overflowY: 'auto' }}>
              {history.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '20px 0', color: '#999', fontSize: 12 }}>
                  暂无历史记录
                </div>
              ) : (
                <List
                  size="small"
                  dataSource={history}
                  renderItem={(item) => (
                    <List.Item
                      style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}
                      actions={[
                        <Tooltip title="使用">
                          <Button
                            type="text"
                            size="small"
                            icon={<CopyOutlined style={{ fontSize: 12 }} />}
                            onClick={() => {
                              setPrompt(item.prompt)
                              setGeneratedScript(item.generated_script)
                              setSuggestions(item.optimization_suggestions)
                              setCurrentAiScriptId(item.id)
                              message.success('已加载脚本')
                            }}
                            style={{ padding: 0 }}
                          />
                        </Tooltip>,
                        <Tooltip title="删除">
                          <Button
                            type="text"
                            size="small"
                            danger
                            icon={<DeleteOutlined style={{ fontSize: 12 }} />}
                            onClick={async () => {
                              try {
                                await aiScriptApi.delete(item.id)
                                message.success('删除成功')
                                loadHistory()
                              } catch (error) {
                                message.error('删除失败')
                              }
                            }}
                            style={{ padding: 0 }}
                          />
                        </Tooltip>
                      ]}
                    >
                      <List.Item.Meta
                        title={
                          <div style={{ 
                            fontSize: 13, 
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            maxWidth: '320px'
                          }}>
                            {item.prompt}
                          </div>
                        }
                        description={
                          <Space size={4}>
                            <Tag style={{ fontSize: 10, padding: '0 4px' }}>{item.language}</Tag>
                            {item.device_model && (
                              <Tag color="blue" style={{ fontSize: 10, padding: '0 4px' }}>
                                {item.device_model}
                              </Tag>
                            )}
                          </Space>
                        }
                      />
                    </List.Item>
                  )}
                />
              )}
            </div>
          </Card>
        </div>

        {/* 右侧：输出区域 */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* 生成的脚本 */}
          <Card
            title={
              <Space>
                <span>生成的脚本</span>
                {generatedScript && (
                  <Tag color="success" style={{ fontSize: 11 }}>已生成</Tag>
                )}
              </Space>
            }
            size="small"
            extra={
              generatedScript && (
                <Space size="small">
                  <Button
                    type="text"
                    size="small"
                    icon={<CheckCircleOutlined />}
                    onClick={handleValidateScript}
                    loading={validating}
                    style={{ fontSize: 12 }}
                  >
                    验证
                  </Button>
                  <Button
                    type="text"
                    size="small"
                    icon={<SaveOutlined />}
                    onClick={handleSaveScript}
                    style={{ fontSize: 12 }}
                  >
                    保存
                  </Button>
                  <Button
                    type="text"
                    size="small"
                    icon={<PlusOutlined />}
                    onClick={() => setShowCreateTemplateModal(true)}
                    style={{ fontSize: 12 }}
                  >
                    存为模板
                  </Button>
                  <Button
                    type="text"
                    size="small"
                    icon={<CopyOutlined />}
                    onClick={handleCopyScript}
                    style={{ fontSize: 12 }}
                  >
                    复制
                  </Button>
                </Space>
              )
            }
          >
            <div style={{ height: 420, border: '1px solid #d9d9d9', borderRadius: 4 }}>
              <Editor
                height="100%"
                language={language === 'python' ? 'python' : 'shell'}
                value={generatedScript || '// 生成的脚本将显示在这里'}
                theme="vs-light"
                options={{
                  readOnly: false,
                  minimap: { enabled: false },
                  fontSize: 13,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  padding: { top: 8, bottom: 8 },
                }}
              />
            </div>

            {/* 验证结果 */}
            {validationResult && (
              <div style={{ marginTop: 12 }}>
                <Alert
                  message={
                    <Space>
                      <span style={{ fontSize: 13, fontWeight: 500 }}>
                        脚本验证结果
                      </span>
                      <Tag color={validationResult.passed ? 'success' : 'error'} style={{ fontSize: 11 }}>
                        {validationResult.passed ? '通过' : '未通过'}
                      </Tag>
                      <Tag color="blue" style={{ fontSize: 11 }}>
                        得分: {validationResult.score}分
                      </Tag>
                    </Space>
                  }
                  description={
                    <div style={{ fontSize: 12, marginTop: 8 }}>
                      {validationResult.items.map((item, index) => (
                        <div key={index} style={{ marginBottom: 4 }}>
                          <Tag 
                            color={item.level === 'success' ? 'green' : item.level === 'warning' ? 'orange' : 'red'}
                            style={{ fontSize: 10, marginRight: 6 }}
                          >
                            {item.name}
                          </Tag>
                          <span style={{ color: item.level === 'error' ? '#ff4d4f' : '#666' }}>
                            {item.message}
                          </span>
                        </div>
                      ))}
                      {validationResult.suggestions.length > 0 && (
                        <div style={{ marginTop: 8, color: '#52c41a' }}>
                          💡 建议: {validationResult.suggestions.join('；')}
                        </div>
                      )}
                    </div>
                  }
                  type={validationResult.passed ? 'success' : 'warning'}
                  showIcon
                  style={{ fontSize: 12 }}
                />
              </div>
            )}
          </Card>

          {/* 优化建议 */}
          {suggestions.length > 0 && (
            <Card 
              title={
                <Space>
                  <BulbOutlined style={{ color: '#faad14' }} />
                  <span>优化建议</span>
                  <Tag color="warning" style={{ fontSize: 11 }}>{suggestions.length}</Tag>
                </Space>
              }
              size="small"
            >
              <Space direction="vertical" style={{ width: '100%' }} size="small">
                {suggestions.map((suggestion, index) => (
                  <Alert
                    key={index}
                    message={
                      <Space size="small">
                        <Tag color={getSuggestionColor(suggestion.type)} style={{ fontSize: 10 }}>
                          {suggestion.type.toUpperCase()}
                        </Tag>
                        <span style={{ fontSize: 12, fontWeight: 500 }}>{suggestion.title}</span>
                      </Space>
                    }
                    description={
                      <div style={{ fontSize: 12 }}>
                        <div style={{ marginBottom: 4, color: '#666' }}>{suggestion.description}</div>
                        <div style={{ color: '#52c41a' }}>
                          💡 {suggestion.suggestion}
                        </div>
                      </div>
                    }
                    type={suggestion.type === 'error' ? 'error' : suggestion.type === 'warning' ? 'warning' : 'info'}
                    showIcon
                    style={{ padding: '8px 12px' }}
                  />
                ))}
              </Space>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

export default AIScriptGenerator
