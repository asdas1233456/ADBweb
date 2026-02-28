/**
 * 批量执行脚本弹窗组件
 */
import { useState, useEffect } from 'react'
import { Modal, Select, message, Alert, Space, Tag } from 'antd'
import { ThunderboltOutlined, MobileOutlined, CodeOutlined } from '@ant-design/icons'
import { deviceApi, scriptApi } from '../services/api'
import type { Script } from '../services/api'

interface BatchExecuteModalProps {
  visible: boolean
  deviceIds: number[]
  onClose: () => void
  onSuccess: () => void
}

const BatchExecuteModal = ({
  visible,
  deviceIds,
  onClose,
  onSuccess
}: BatchExecuteModalProps) => {
  const [scripts, setScripts] = useState<Script[]>([])
  const [selectedScriptId, setSelectedScriptId] = useState<number | undefined>()
  const [loading, setLoading] = useState(false)
  const [loadingScripts, setLoadingScripts] = useState(false)

  // 加载脚本列表
  useEffect(() => {
    if (visible) {
      loadScripts()
    }
  }, [visible])

  const loadScripts = async () => {
    try {
      setLoadingScripts(true)
      const response = await scriptApi.getList({ page: 1, page_size: 100 })
      setScripts(response.items.filter(s => s.is_active))
    } catch (error) {
      message.error('加载脚本列表失败')
      console.error('加载脚本列表失败:', error)
    } finally {
      setLoadingScripts(false)
    }
  }

  const handleOk = async () => {
    if (!selectedScriptId) {
      message.warning('请选择要执行的脚本')
      return
    }

    try {
      setLoading(true)
      const result = await deviceApi.batchExecute(deviceIds, selectedScriptId)
      message.success(`已向 ${result.device_count} 个设备发送执行任务`)
      onSuccess()
      onClose()
    } catch (error) {
      message.error('批量执行失败')
      console.error('批量执行失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setSelectedScriptId(undefined)
    onClose()
  }

  const selectedScript = scripts.find(s => s.id === selectedScriptId)

  return (
    <Modal
      title={
        <Space>
          <ThunderboltOutlined />
          批量执行脚本
        </Space>
      }
      open={visible}
      onOk={handleOk}
      onCancel={handleCancel}
      confirmLoading={loading}
      okText="开始执行"
      cancelText="取消"
      width={600}
    >
      <Alert
        message={
          <Space>
            <MobileOutlined />
            已选择 {deviceIds.length} 个设备
          </Space>
        }
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <div style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: 8, color: '#262626', fontWeight: 500 }}>
          <CodeOutlined /> 选择脚本：
        </div>
        <Select
          style={{ width: '100%' }}
          placeholder="请选择要执行的脚本"
          value={selectedScriptId}
          onChange={setSelectedScriptId}
          loading={loadingScripts}
          showSearch
          filterOption={(input, option) =>
            (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
          }
          options={scripts.map(script => ({
            label: script.name,
            value: script.id,
            desc: script.description
          }))}
          optionRender={(option) => (
            <div>
              <div>{option.label}</div>
              {option.data.desc && (
                <div style={{ fontSize: 12, color: '#8c8c8c' }}>
                  {option.data.desc}
                </div>
              )}
            </div>
          )}
        />
      </div>

      {selectedScript && (
        <div style={{ 
          padding: 12, 
          background: '#f5f5f5', 
          borderRadius: 4,
          marginBottom: 16
        }}>
          <div style={{ marginBottom: 8, fontWeight: 500 }}>脚本信息：</div>
          <Space direction="vertical" size={4}>
            <div>
              <span style={{ color: '#8c8c8c' }}>名称：</span>
              {selectedScript.name}
            </div>
            <div>
              <span style={{ color: '#8c8c8c' }}>类型：</span>
              <Tag color="blue">{selectedScript.type}</Tag>
            </div>
            <div>
              <span style={{ color: '#8c8c8c' }}>分类：</span>
              <Tag>{selectedScript.category}</Tag>
            </div>
            {selectedScript.description && (
              <div>
                <span style={{ color: '#8c8c8c' }}>描述：</span>
                {selectedScript.description}
              </div>
            )}
          </Space>
        </div>
      )}

      <Alert
        message="注意事项"
        description={
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            <li>脚本将同时在所有选中的设备上执行</li>
            <li>请确保脚本与所有设备兼容</li>
            <li>执行过程中可以在任务监控页面查看进度</li>
            <li>建议先在单个设备上测试脚本</li>
          </ul>
        }
        type="warning"
        showIcon
      />
    </Modal>
  )
}

export default BatchExecuteModal
