import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Card, Button, Space, Input, Select, Form, InputNumber, Row, Col, Empty, message } from 'antd'
import {
  SaveOutlined,
  PlayCircleOutlined,
  PlusOutlined,
  DeleteOutlined,
  DragOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons'
import { scriptApi } from '../services/api'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import type { ScriptStep } from '../types'

interface SortableStepProps {
  step: ScriptStep
  index: number
  onSelect: (step: ScriptStep) => void
  onDelete: (id: string) => void
  isSelected: boolean
}

const SortableStep = ({ step, index, onSelect, onDelete, isSelected }: SortableStepProps) => {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({
    id: step.id,
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  const stepTypeMap: Record<string, string> = {
    click: '点击',
    swipe: '滑动',
    input: '输入',
    wait: '等待',
    screenshot: '截图',
    assert: '断言',
  }

  return (
    <div
      ref={setNodeRef}
      style={{
        ...style,
        marginBottom: 8,
        padding: '12px 16px',
        background: isSelected ? '#e6f7ff' : '#fafafa',
        border: `1px solid ${isSelected ? '#1890ff' : '#e8e8e8'}`,
        borderRadius: 8,
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        transition: 'all 0.3s ease',
      }}
      onClick={() => onSelect(step)}
    >
      <div {...attributes} {...listeners} style={{ cursor: 'grab', color: '#8c8c8c' }}>
        <DragOutlined />
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 500, color: '#262626' }}>
          {index + 1}. {step.name}
        </div>
        <div style={{ fontSize: 12, color: '#8c8c8c', marginTop: 4 }}>
          类型: {stepTypeMap[step.type]}
        </div>
      </div>
      <Button
        type="text"
        danger
        size="small"
        icon={<DeleteOutlined />}
        onClick={(e) => {
          e.stopPropagation()
          onDelete(step.id)
        }}
      />
    </div>
  )
}

const ScriptEditor = () => {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [scriptName, setScriptName] = useState('新建脚本')
  const [scriptCategory, setScriptCategory] = useState<'login' | 'test' | 'automation' | 'other'>('test')
  const [scriptDescription, setScriptDescription] = useState('')
  const [steps, setSteps] = useState<ScriptStep[]>([])
  const [selectedStep, setSelectedStep] = useState<ScriptStep | null>(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [form] = Form.useForm()

  // 加载脚本数据（如果是编辑模式）
  useEffect(() => {
    if (id) {
      loadScript(parseInt(id))
    }
  }, [id])

  const loadScript = async (scriptId: number) => {
    try {
      setLoading(true)
      const script = await scriptApi.getDetail(scriptId)
      setScriptName(script.name)
      setScriptCategory(script.category)
      setScriptDescription(script.description || '')
      
      if (script.steps_json) {
        try {
          const parsedSteps = JSON.parse(script.steps_json)
          // 确保 parsedSteps 是数组
          if (Array.isArray(parsedSteps)) {
            setSteps(parsedSteps)
            if (parsedSteps.length > 0) {
              setSelectedStep(parsedSteps[0])
            }
          } else {
            console.error('steps_json is not an array:', parsedSteps)
            setSteps([])
            message.warning('脚本步骤数据格式不正确，已重置为空')
          }
        } catch (error) {
          console.error('Failed to parse steps:', error)
          setSteps([])
          message.error('脚本步骤数据解析失败，已重置为空')
        }
      } else {
        setSteps([])
      }
    } catch (error) {
      message.error('加载脚本失败')
      console.error('Failed to load script:', error)
      setSteps([])
    } finally {
      setLoading(false)
    }
  }

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event

    if (over && active.id !== over.id) {
      setSteps((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id)
        const newIndex = items.findIndex((item) => item.id === over.id)
        return arrayMove(items, oldIndex, newIndex)
      })
    }
  }

  const handleAddStep = (type: ScriptStep['type']) => {
    const newStep: ScriptStep = {
      id: `s${Date.now()}`,
      type,
      name: `新步骤 ${steps.length + 1}`,
      config: {},
    }
    setSteps([...steps, newStep])
    setSelectedStep(newStep)
  }

  const handleDeleteStep = (id: string) => {
    const newSteps = steps.filter((s) => s.id !== id)
    setSteps(newSteps)
    if (selectedStep?.id === id) {
      setSelectedStep(newSteps[0] || null)
    }
  }

  const handleUpdateStep = (values: any) => {
    if (!selectedStep || !steps) return
    const updatedSteps = steps.map((s) =>
      s.id === selectedStep.id
        ? { ...s, name: values.name, config: values }
        : s
    )
    setSteps(updatedSteps)
    setSelectedStep({ ...selectedStep, name: values.name, config: values })
  }

  const handleSave = async () => {
    if (!scriptName.trim()) {
      message.error('请输入脚本名称')
      return
    }

    try {
      setSaving(true)
      const scriptData = {
        name: scriptName,
        type: 'visual' as const,
        category: scriptCategory,
        description: scriptDescription,
        steps_json: JSON.stringify(steps),
      }

      if (id) {
        // 更新现有脚本
        await scriptApi.update(parseInt(id), scriptData)
        message.success('脚本保存成功！')
      } else {
        // 创建新脚本
        const newScript = await scriptApi.create(scriptData)
        message.success('脚本创建成功！')
        // 创建成功后跳转到编辑模式
        navigate(`/scripts/${newScript.id}`, { replace: true })
      }
    } catch (error) {
      message.error('保存脚本失败')
      console.error('Failed to save script:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleBack = () => {
    navigate('/scripts')
  }

  const renderStepConfig = () => {
    if (!selectedStep) {
      return (
        <Empty
          description="请选择一个步骤进行编辑"
          style={{ marginTop: 100 }}
        />
      )
    }

    form.setFieldsValue({
      name: selectedStep.name,
      ...selectedStep.config,
    })

    const commonFields = (
      <Form.Item
        label="步骤名称"
        name="name"
        rules={[{ required: true, message: '请输入步骤名称' }]}
      >
        <Input placeholder="输入步骤名称" />
      </Form.Item>
    )

    switch (selectedStep.type) {
      case 'click':
        return (
          <>
            {commonFields}
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item label="X 坐标" name="x">
                  <InputNumber style={{ width: '100%' }} placeholder="100" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="Y 坐标" name="y">
                  <InputNumber style={{ width: '100%' }} placeholder="200" />
                </Form.Item>
              </Col>
            </Row>
            <Form.Item label="点击类型" name="clickType">
              <Select
                placeholder="选择点击类型"
                options={[
                  { label: '单击', value: 'single' },
                  { label: '双击', value: 'double' },
                  { label: '长按', value: 'long' },
                ]}
              />
            </Form.Item>
          </>
        )
      case 'swipe':
        return (
          <>
            {commonFields}
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item label="起始 X" name="x1">
                  <InputNumber style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="起始 Y" name="y1">
                  <InputNumber style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item label="结束 X" name="x2">
                  <InputNumber style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="结束 Y" name="y2">
                  <InputNumber style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            </Row>
            <Form.Item label="滑动时长(ms)" name="duration">
              <InputNumber style={{ width: '100%' }} placeholder="500" />
            </Form.Item>
          </>
        )
      case 'input':
        return (
          <>
            {commonFields}
            <Form.Item label="输入内容" name="text">
              <Input.TextArea rows={3} placeholder="输入文本内容" />
            </Form.Item>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item label="X 坐标" name="x">
                  <InputNumber style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="Y 坐标" name="y">
                  <InputNumber style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            </Row>
          </>
        )
      case 'wait':
        return (
          <>
            {commonFields}
            <Form.Item label="等待时长(ms)" name="duration">
              <InputNumber style={{ width: '100%' }} placeholder="2000" />
            </Form.Item>
          </>
        )
      default:
        return commonFields
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space size="large">
          <Button icon={<ArrowLeftOutlined />} onClick={handleBack}>
            返回
          </Button>
          <div>
            <Input
              value={scriptName}
              onChange={(e) => setScriptName(e.target.value)}
              style={{ width: 300, fontSize: 20, fontWeight: 600, marginBottom: 8 }}
              bordered={false}
              placeholder="输入脚本名称"
            />
            <Space>
              <Select
                value={scriptCategory}
                onChange={setScriptCategory}
                style={{ width: 120 }}
                size="small"
              >
                <Select.Option value="login">登录</Select.Option>
                <Select.Option value="test">测试</Select.Option>
                <Select.Option value="automation">自动化</Select.Option>
                <Select.Option value="other">其他</Select.Option>
              </Select>
              <Input
                value={scriptDescription}
                onChange={(e) => setScriptDescription(e.target.value)}
                placeholder="脚本描述（可选）"
                style={{ width: 200 }}
                size="small"
              />
            </Space>
          </div>
        </Space>
        <Space>
          <Button 
            icon={<SaveOutlined />} 
            type="primary"
            onClick={handleSave}
            loading={saving}
          >
            保存
          </Button>
          <Button icon={<PlayCircleOutlined />}>运行</Button>
        </Space>
      </div>

      <Row gutter={16}>
        <Col xs={24} lg={10}>
          <Card
            title="步骤列表"
            extra={
              <Select
                placeholder="添加步骤"
                style={{ width: 120 }}
                onChange={(value) => handleAddStep(value as ScriptStep['type'])}
                value={undefined}
                options={[
                  { label: '点击', value: 'click' },
                  { label: '滑动', value: 'swipe' },
                  { label: '输入', value: 'input' },
                  { label: '等待', value: 'wait' },
                  { label: '截图', value: 'screenshot' },
                  { label: '断言', value: 'assert' },
                ]}
              />
            }
            style={{
              background: '#fff',
              border: '1px solid #e8e8e8',
              height: 'calc(100vh - 200px)',
              overflow: 'auto',
            }}
          >
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragEnd={handleDragEnd}
            >
              <SortableContext items={(steps || []).map((s) => s.id)} strategy={verticalListSortingStrategy}>
                {(steps || []).map((step, index) => (
                  <SortableStep
                    key={step.id}
                    step={step}
                    index={index}
                    onSelect={setSelectedStep}
                    onDelete={handleDeleteStep}
                    isSelected={selectedStep?.id === step.id}
                  />
                ))}
              </SortableContext>
            </DndContext>

            {(!steps || steps.length === 0) && (
              <Empty description="暂无步骤，请添加步骤" style={{ marginTop: 50 }} />
            )}
          </Card>
        </Col>

        <Col xs={24} lg={14}>
          <Card
            title="步骤配置"
            style={{
              background: '#fff',
              border: '1px solid #e8e8e8',
              height: 'calc(100vh - 200px)',
              overflow: 'auto',
            }}
          >
            <Form
              form={form}
              layout="vertical"
              onValuesChange={(_, allValues) => handleUpdateStep(allValues)}
            >
              {renderStepConfig()}
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default ScriptEditor
