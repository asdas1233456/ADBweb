/**
 * 设备分组管理组件
 */
import { useState, useEffect } from 'react'
import { Modal, Select, Input, message, Space, Tag } from 'antd'
import { FolderOutlined, PlusOutlined } from '@ant-design/icons'
import { deviceApi } from '../services/api'

interface DeviceGroupManagerProps {
  visible: boolean
  deviceId: number
  currentGroup?: string
  onClose: () => void
  onSuccess: () => void
}

const DeviceGroupManager = ({
  visible,
  deviceId,
  currentGroup,
  onClose,
  onSuccess
}: DeviceGroupManagerProps) => {
  const [groups, setGroups] = useState<string[]>([])
  const [selectedGroup, setSelectedGroup] = useState<string | undefined>(currentGroup)
  const [newGroupName, setNewGroupName] = useState('')
  const [loading, setLoading] = useState(false)
  const [showNewGroupInput, setShowNewGroupInput] = useState(false)

  // 加载分组列表
  useEffect(() => {
    if (visible) {
      loadGroups()
      setSelectedGroup(currentGroup)
    }
  }, [visible, currentGroup])

  const loadGroups = async () => {
    try {
      const groupList = await deviceApi.getGroups()
      setGroups(groupList)
    } catch (error) {
      console.error('加载分组列表失败:', error)
    }
  }

  const handleOk = async () => {
    try {
      setLoading(true)
      
      // 如果是新建分组
      let groupToSet = selectedGroup
      if (showNewGroupInput && newGroupName.trim()) {
        groupToSet = newGroupName.trim()
      }

      await deviceApi.updateGroup(deviceId, groupToSet)
      message.success('设备分组更新成功')
      onSuccess()
      onClose()
    } catch (error) {
      message.error('更新设备分组失败')
      console.error('更新设备分组失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setShowNewGroupInput(false)
    setNewGroupName('')
    onClose()
  }

  return (
    <Modal
      title={
        <Space>
          <FolderOutlined />
          设置设备分组
        </Space>
      }
      open={visible}
      onOk={handleOk}
      onCancel={handleCancel}
      confirmLoading={loading}
      okText="确定"
      cancelText="取消"
    >
      <div style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: 8, color: '#262626' }}>选择分组：</div>
        
        {!showNewGroupInput ? (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Select
              style={{ width: '100%' }}
              placeholder="选择已有分组或创建新分组"
              value={selectedGroup}
              onChange={setSelectedGroup}
              allowClear
              options={[
                ...groups.map(g => ({ label: g, value: g })),
                {
                  label: (
                    <Space>
                      <PlusOutlined />
                      创建新分组
                    </Space>
                  ),
                  value: '__new__'
                }
              ]}
              onSelect={(value) => {
                if (value === '__new__') {
                  setShowNewGroupInput(true)
                  setSelectedGroup(undefined)
                }
              }}
            />
            
            {selectedGroup && (
              <div style={{ marginTop: 8 }}>
                <Tag color="blue">{selectedGroup}</Tag>
              </div>
            )}
          </Space>
        ) : (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Input
              placeholder="输入新分组名称"
              value={newGroupName}
              onChange={(e) => setNewGroupName(e.target.value)}
              prefix={<FolderOutlined />}
              autoFocus
            />
            <Space>
              <a onClick={() => {
                setShowNewGroupInput(false)
                setNewGroupName('')
              }}>
                取消
              </a>
            </Space>
          </Space>
        )}
      </div>

      <div style={{ 
        padding: 12, 
        background: '#f5f5f5', 
        borderRadius: 4,
        fontSize: 12,
        color: '#8c8c8c'
      }}>
        <div>💡 提示：</div>
        <div>• 分组可以帮助你按项目或用途管理设备</div>
        <div>• 可以通过分组筛选设备列表</div>
        <div>• 留空表示不设置分组</div>
      </div>
    </Modal>
  )
}

export default DeviceGroupManager
