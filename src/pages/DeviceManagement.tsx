import { useState, useEffect } from 'react'
import { Table, Button, Tag, Space, Modal, Progress, Card, message, Spin, Input, Popconfirm, Select, Dropdown } from 'antd'
import {
  ReloadOutlined,
  VideoCameraOutlined,
  InfoCircleOutlined,
  DisconnectOutlined,
  SearchOutlined,
  DeleteOutlined,
  AppstoreOutlined,
  PlayCircleOutlined,
  DownOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { deviceApi } from '../services/api'
import type { Device } from '../types'

const DeviceManagement = () => {
  const [devices, setDevices] = useState<Device[]>([])
  const [filteredDevices, setFilteredDevices] = useState<Device[]>([])
  const [loading, setLoading] = useState(false)
  const [screenModalVisible, setScreenModalVisible] = useState(false)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null)
  const [pageSize, setPageSize] = useState(20)
  const [currentPage, setCurrentPage] = useState(1)
  const [searchText, setSearchText] = useState('')
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [deviceGroups, setDeviceGroups] = useState<string[]>([])
  const [selectedGroup, setSelectedGroup] = useState<string | undefined>()
  const [groupModalVisible, setGroupModalVisible] = useState(false)
  const [newGroupName, setNewGroupName] = useState('')
  const [batchExecuteModalVisible, setBatchExecuteModalVisible] = useState(false)
  const [selectedScriptId, setSelectedScriptId] = useState<number | undefined>()
  const [scripts, setScripts] = useState<any[]>([])
  const [executingBatch, setExecutingBatch] = useState(false)
  const [addDeviceModalVisible, setAddDeviceModalVisible] = useState(false)
  const [availableDevices, setAvailableDevices] = useState<any[]>([])
  const [loadingAvailableDevices, setLoadingAvailableDevices] = useState(false)

  // 加载设备列表
  const loadDevices = async () => {
    setLoading(true)
    try {
      const response = await deviceApi.getList({ page: 1, page_size: 1000 })
      setDevices(response.items)
      setFilteredDevices(response.items)
      
      // 从后端 API 获取所有分组列表
      try {
        const groupsResponse = await deviceApi.getGroups()
        setDeviceGroups(groupsResponse)
      } catch (error) {
        console.error('加载分组列表失败:', error)
        // 如果 API 失败，回退到从设备列表提取
        const groups = Array.from(new Set(response.items.map(d => d.group_name).filter(Boolean))) as string[]
        setDeviceGroups(groups)
      }
    } catch (error) {
      message.error('加载设备列表失败')
      console.error('加载设备列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // 搜索过滤
  const handleSearch = (value: string) => {
    setSearchText(value)
    setCurrentPage(1)
    
    let filtered = devices
    
    // 按分组过滤
    if (selectedGroup) {
      filtered = filtered.filter(device => device.group_name === selectedGroup)
    }
    
    // 按搜索文本过滤
    if (value.trim()) {
      const searchLower = value.toLowerCase()
      filtered = filtered.filter(device => 
        device.model?.toLowerCase().includes(searchLower) ||
        device.serial_number?.toLowerCase().includes(searchLower) ||
        device.android_version?.toLowerCase().includes(searchLower)
      )
    }
    
    setFilteredDevices(filtered)
  }

  // 分组过滤
  const handleGroupFilter = (group: string | undefined) => {
    setSelectedGroup(group)
    setCurrentPage(1)
    
    let filtered = devices
    
    if (group) {
      filtered = filtered.filter(device => device.group_name === group)
    }
    
    if (searchText.trim()) {
      const searchLower = searchText.toLowerCase()
      filtered = filtered.filter(device => 
        device.model?.toLowerCase().includes(searchLower) ||
        device.serial_number?.toLowerCase().includes(searchLower) ||
        device.android_version?.toLowerCase().includes(searchLower)
      )
    }
    
    setFilteredDevices(filtered)
  }

  // 加载脚本列表
  const loadScripts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/scripts?page=1&page_size=100')
      const result = await response.json()
      if (result.code === 200) {
        setScripts(result.data.items)
      }
    } catch (error) {
      console.error('加载脚本列表失败:', error)
    }
  }

  // 打开批量执行对话框
  const handleBatchExecute = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择设备')
      return
    }
    
    await loadScripts()
    setBatchExecuteModalVisible(true)
  }

  // 确认批量执行
  const handleConfirmBatchExecute = async () => {
    if (!selectedScriptId) {
      message.warning('请选择要执行的脚本')
      return
    }

    setExecutingBatch(true)
    try {
      await deviceApi.batchExecute(
        selectedRowKeys.map(key => Number(key)),
        selectedScriptId
      )
      message.success(`已成功向 ${selectedRowKeys.length} 台设备发送执行任务`)
      setBatchExecuteModalVisible(false)
      setSelectedScriptId(undefined)
      setSelectedRowKeys([])
    } catch (error) {
      message.error('批量执行失败')
      console.error('批量执行失败:', error)
    } finally {
      setExecutingBatch(false)
    }
  }

  // 批量设置分组
  const handleBatchSetGroup = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择设备')
      return
    }
    setGroupModalVisible(true)
  }

  // 保存分组
  const handleSaveGroup = async () => {
    if (!newGroupName.trim()) {
      message.warning('请输入分组名称')
      return
    }
    
    try {
      // 批量更新设备分组
      for (const deviceId of selectedRowKeys) {
        await fetch(`http://localhost:8000/api/v1/devices/${deviceId}/group?group_name=${encodeURIComponent(newGroupName)}`, {
          method: 'PUT',
        })
      }
      
      message.success(`已将 ${selectedRowKeys.length} 台设备设置为分组: ${newGroupName}`)
      setGroupModalVisible(false)
      setNewGroupName('')
      setSelectedRowKeys([])
      loadDevices()
    } catch (error) {
      message.error('设置分组失败')
      console.error('设置分组失败:', error)
    }
  }

  // 加载可用设备列表（通过ADB扫描）
  const loadAvailableDevices = async () => {
    setLoadingAvailableDevices(true)
    try {
      // 调用刷新接口，这会扫描ADB设备
      await deviceApi.refresh()
      message.success('已扫描ADB设备')
      
      // 重新加载设备列表
      await loadDevices()
      
      // 获取所有设备
      const allDevicesResponse = await deviceApi.getList({ page: 1, page_size: 1000 })
      
      // 显示所有设备（包括已添加和未添加的）
      // 注意：这里显示所有设备是为了让用户看到扫描结果
      setAvailableDevices(allDevicesResponse.items)
    } catch (error) {
      message.error('扫描设备失败')
      console.error('扫描设备失败:', error)
    } finally {
      setLoadingAvailableDevices(false)
    }
  }

  // 打开添加设备对话框
  const handleAddDevice = async () => {
    setAddDeviceModalVisible(true)
    await loadAvailableDevices()
  }

  // 添加设备到系统（实际上设备已经通过refresh自动添加了）
  const handleConfirmAddDevice = async (device: any) => {
    try {
      // 由于refresh已经自动添加了设备，这里只需要确认
      message.info(`设备 ${device.model} 已在系统中，无需重复添加`)
      setAddDeviceModalVisible(false)
      await loadDevices()
    } catch (error) {
      message.error('操作失败')
      console.error('操作失败:', error)
    }
  }

  // 刷新设备列表
  const handleRefresh = async () => {
    try {
      await deviceApi.refresh()
      message.success('设备列表刷新成功')
      loadDevices()
    } catch (error) {
      message.error('刷新设备列表失败')
      console.error('刷新设备列表失败:', error)
    }
  }

  // 断开设备连接
  const handleDisconnect = async (device: Device) => {
    try {
      await deviceApi.disconnect(device.id)
      message.success(`设备 ${device.model} 已断开连接`)
      loadDevices()
    } catch (error) {
      message.error('断开设备连接失败')
      console.error('断开设备连接失败:', error)
    }
  }

  // 删除设备
  const handleDelete = async (device: Device) => {
    try {
      await fetch(`http://localhost:8000/api/v1/devices/${device.id}`, {
        method: 'DELETE',
      })
      message.success(`设备 ${device.model} 已删除`)
      loadDevices()
    } catch (error) {
      message.error('删除设备失败')
      console.error('删除设备失败:', error)
    }
  }

  useEffect(() => {
    loadDevices()
  }, [])

  const getStatusTag = (status: Device['status']) => {
    const statusMap = {
      online: { color: 'success', text: '在线 🟢' },
      offline: { color: 'error', text: '离线 🔴' },
      busy: { color: 'warning', text: '使用中 🟡' },
    }
    const { color, text } = statusMap[status]
    return <Tag color={color}>{text}</Tag>
  }

  const handleScreenCast = (device: Device) => {
    setSelectedDevice(device)
    setScreenModalVisible(true)
  }

  const handleShowDetail = (device: Device) => {
    setSelectedDevice(device)
    setDetailModalVisible(true)
  }

  const columns: ColumnsType<Device> = [
    {
      title: '序列号',
      dataIndex: 'serialNumber',
      key: 'serialNumber',
      width: 150,
    },
    {
      title: '设备型号',
      dataIndex: 'model',
      key: 'model',
      width: 180,
    },
    {
      title: 'Android 版本',
      dataIndex: 'androidVersion',
      key: 'androidVersion',
      width: 120,
      align: 'center',
    },
    {
      title: '屏幕分辨率',
      dataIndex: 'resolution',
      key: 'resolution',
      width: 140,
      align: 'center',
    },
    {
      title: '电池电量',
      dataIndex: 'battery',
      key: 'battery',
      width: 150,
      render: (battery: number) => (
        <Progress
          percent={battery}
          size="small"
          status={battery > 50 ? 'success' : battery > 20 ? 'normal' : 'exception'}
        />
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      align: 'center',
      render: (status: Device['status']) => getStatusTag(status),
    },
    {
      title: '操作',
      key: 'action',
      width: 320,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="primary"
            icon={<VideoCameraOutlined />}
            size="small"
            disabled={record.status === 'offline'}
            onClick={() => handleScreenCast(record)}
          >
            投屏
          </Button>
          <Button icon={<InfoCircleOutlined />} size="small" onClick={() => handleShowDetail(record)}>
            详情
          </Button>
          <Button
            icon={<DisconnectOutlined />}
            size="small"
            danger
            disabled={record.status === 'offline'}
            onClick={() => handleDisconnect(record)}
          >
            断开
          </Button>
          <Popconfirm
            title="确认删除"
            description={`确定要删除设备 ${record.model} 吗？此操作不可恢复。`}
            onConfirm={() => handleDelete(record)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              icon={<DeleteOutlined />}
              size="small"
              danger
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h2 style={{ margin: 0, fontSize: 24, fontWeight: 600 }}>设备管理</h2>
        <Space>
          <Input
            placeholder="搜索设备型号、序列号、版本"
            prefix={<SearchOutlined />}
            allowClear
            style={{ width: 280 }}
            value={searchText}
            onChange={(e) => handleSearch(e.target.value)}
          />
          <Select
            placeholder="设备分组"
            allowClear
            style={{ width: 150 }}
            value={selectedGroup}
            onChange={handleGroupFilter}
            options={deviceGroups.map(g => ({ label: g, value: g }))}
          />
          <Button icon={<ReloadOutlined />} onClick={handleRefresh} loading={loading}>
            刷新
          </Button>
          <Button type="primary" onClick={handleAddDevice}>添加设备</Button>
        </Space>
      </div>

      {selectedRowKeys.length > 0 && (
        <Card style={{ marginBottom: 16, background: '#e6f7ff', borderColor: '#91d5ff' }}>
          <Space>
            <span>已选择 {selectedRowKeys.length} 台设备</span>
            <Button
              type="primary"
              size="small"
              icon={<PlayCircleOutlined />}
              onClick={handleBatchExecute}
            >
              批量执行
            </Button>
            <Button
              size="small"
              icon={<AppstoreOutlined />}
              onClick={handleBatchSetGroup}
            >
              设置分组
            </Button>
            <Button
              size="small"
              onClick={() => setSelectedRowKeys([])}
            >
              取消选择
            </Button>
          </Space>
        </Card>
      )}

      <Card
        style={{
          background: '#fff',
          border: '1px solid #e8e8e8',
          borderRadius: 8,
        }}
      >
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={filteredDevices}
            rowKey="id"
            rowSelection={{
              selectedRowKeys,
              onChange: setSelectedRowKeys,
            }}
            scroll={{ x: 1000, y: 'calc(100vh - 400px)' }} // 动态高度，最大约20行
            pagination={{
              current: currentPage,
              pageSize: pageSize,
              showSizeChanger: true,
              pageSizeOptions: ['10', '20', '50'],
              showTotal: (total) => `共 ${total} 台设备`,
              onChange: (page, size) => {
                setCurrentPage(page)
                setPageSize(size)
              },
              onShowSizeChange: (current, size) => {
                setCurrentPage(1)
                setPageSize(size)
              },
            }}
            style={{
              background: 'transparent',
            }}
            locale={{
              emptyText: '暂无设备，请先连接ADB设备或点击"刷新"按钮'
            }}
          />
        </Spin>
      </Card>

      <Modal
        title={`设备投屏 - ${selectedDevice?.model}`}
        open={screenModalVisible}
        onCancel={() => setScreenModalVisible(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setScreenModalVisible(false)}>
            关闭
          </Button>,
        ]}
      >
        <div
          style={{
            height: 600,
            background: '#1f1f1f',
            borderRadius: 8,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#666',
            fontSize: 16,
          }}
        >
          <div style={{ textAlign: 'center' }}>
            <VideoCameraOutlined style={{ fontSize: 48, marginBottom: 16 }} />
            <div>投屏功能开发中...</div>
            <div style={{ fontSize: 14, marginTop: 8 }}>
              设备: {selectedDevice?.model}
            </div>
          </div>
        </div>
      </Modal>

      <Modal
        title={`设备详情 - ${selectedDevice?.model}`}
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        width={600}
        footer={[
          <Button key="close" type="primary" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
        ]}
      >
        {selectedDevice && (
          <div style={{ padding: '16px 0' }}>
            <Card size="small" style={{ marginBottom: 16 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: '12px 16px' }}>
                <div style={{ color: '#666' }}>序列号:</div>
                <div style={{ fontWeight: 500 }}>{selectedDevice.serialNumber}</div>
                
                <div style={{ color: '#666' }}>设备型号:</div>
                <div style={{ fontWeight: 500 }}>{selectedDevice.model}</div>
                
                <div style={{ color: '#666' }}>Android 版本:</div>
                <div>{selectedDevice.androidVersion}</div>
                
                <div style={{ color: '#666' }}>屏幕分辨率:</div>
                <div>{selectedDevice.resolution}</div>
                
                <div style={{ color: '#666' }}>电池电量:</div>
                <div>
                  <Progress
                    percent={selectedDevice.battery}
                    size="small"
                    status={selectedDevice.battery > 50 ? 'success' : selectedDevice.battery > 20 ? 'normal' : 'exception'}
                    style={{ maxWidth: 200 }}
                  />
                </div>
                
                <div style={{ color: '#666' }}>设备状态:</div>
                <div>{getStatusTag(selectedDevice.status)}</div>
              </div>
            </Card>
            
            <Card size="small" title="设备信息">
              <div style={{ color: '#666', fontSize: 14 }}>
                <div style={{ marginBottom: 8 }}>
                  <span style={{ fontWeight: 500 }}>连接方式:</span> USB
                </div>
                <div style={{ marginBottom: 8 }}>
                  <span style={{ fontWeight: 500 }}>最后更新:</span> {new Date().toLocaleString('zh-CN')}
                </div>
              </div>
            </Card>
          </div>
        )}
      </Modal>

      <Modal
        title="设置设备分组"
        open={groupModalVisible}
        onOk={handleSaveGroup}
        onCancel={() => {
          setGroupModalVisible(false)
          setNewGroupName('')
        }}
      >
        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8, color: '#666' }}>
            已选择 {selectedRowKeys.length} 台设备
          </div>
          <Select
            placeholder="选择现有分组或输入新分组名称"
            style={{ width: '100%' }}
            value={newGroupName}
            onChange={setNewGroupName}
            showSearch
            allowClear
            mode="tags"
            maxCount={1}
          >
            {deviceGroups.map(group => (
              <Select.Option key={group} value={group}>
                {group}
              </Select.Option>
            ))}
          </Select>
          <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
            提示：可以选择现有分组，或输入新的分组名称后按回车
          </div>
        </div>
      </Modal>

      {/* 添加设备弹窗 */}
      <Modal
        title="添加设备"
        open={addDeviceModalVisible}
        onCancel={() => setAddDeviceModalVisible(false)}
        width={800}
        footer={[
          <Button key="refresh" icon={<ReloadOutlined />} onClick={loadAvailableDevices} loading={loadingAvailableDevices}>
            重新扫描
          </Button>,
          <Button key="close" onClick={() => setAddDeviceModalVisible(false)}>
            关闭
          </Button>,
        ]}
      >
        <div style={{ marginBottom: 16 }}>
          <div style={{ padding: '12px', background: '#e6f7ff', borderRadius: 4, marginBottom: 16 }}>
            <InfoCircleOutlined style={{ color: '#1890ff', marginRight: 8 }} />
            <span style={{ color: '#666' }}>
              点击"重新扫描"会自动检测并添加通过ADB连接的设备。请确保设备已通过USB连接并开启USB调试。
            </span>
          </div>
        </div>

        <Spin spinning={loadingAvailableDevices}>
          {availableDevices.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              padding: '60px 20px',
              color: '#999'
            }}>
              <VideoCameraOutlined style={{ fontSize: 48, marginBottom: 16, color: '#d9d9d9' }} />
              <div style={{ fontSize: 16, marginBottom: 8 }}>未发现设备</div>
              <div style={{ fontSize: 14 }}>
                请检查：
                <div style={{ marginTop: 12, textAlign: 'left', display: 'inline-block' }}>
                  <div>1. 设备是否通过USB连接到电脑</div>
                  <div>2. 设备是否开启了USB调试模式</div>
                  <div>3. 是否已安装ADB驱动</div>
                  <div>4. 点击"重新扫描"按钮刷新设备列表</div>
                </div>
              </div>
            </div>
          ) : (
            <div>
              <div style={{ marginBottom: 12, color: '#666' }}>
                当前系统中有 {availableDevices.length} 台设备：
              </div>
              <div style={{ maxHeight: 400, overflowY: 'auto' }}>
                {availableDevices.map((device) => (
                  <Card
                    key={device.id}
                    size="small"
                    style={{ marginBottom: 12 }}
                    hoverable
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 16, fontWeight: 500, marginBottom: 8 }}>
                          {device.model}
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', fontSize: 14, color: '#666' }}>
                          <div>
                            <span style={{ color: '#999' }}>序列号：</span>
                            {device.serialNumber}
                          </div>
                          <div>
                            <span style={{ color: '#999' }}>Android：</span>
                            {device.androidVersion}
                          </div>
                          <div>
                            <span style={{ color: '#999' }}>分辨率：</span>
                            {device.resolution}
                          </div>
                          <div>
                            <span style={{ color: '#999' }}>电量：</span>
                            {device.battery}%
                          </div>
                        </div>
                        <div style={{ marginTop: 8 }}>
                          {getStatusTag(device.status)}
                        </div>
                      </div>
                      <div style={{ marginLeft: 16 }}>
                        <Tag color="success">已在系统中</Tag>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
              <div style={{ marginTop: 16, padding: '12px', background: '#f0f0f0', borderRadius: 4, fontSize: 14, color: '#666' }}>
                <InfoCircleOutlined style={{ marginRight: 8 }} />
                提示：所有通过ADB连接的设备会自动添加到系统中。如需添加新设备，请连接设备后点击"重新扫描"。
              </div>
            </div>
          )}
        </Spin>
      </Modal>

      {/* 批量执行弹窗 */}
      <Modal
        title="批量执行脚本"
        open={batchExecuteModalVisible}
        onOk={handleConfirmBatchExecute}
        onCancel={() => {
          setBatchExecuteModalVisible(false)
          setSelectedScriptId(undefined)
        }}
        confirmLoading={executingBatch}
      >
        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8, color: '#666' }}>
            已选择 {selectedRowKeys.length} 台设备
          </div>
          <Select
            placeholder="选择要执行的脚本"
            style={{ width: '100%' }}
            value={selectedScriptId}
            onChange={setSelectedScriptId}
            showSearch
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
            options={scripts.map(script => ({
              label: `${script.name} (${script.type})`,
              value: script.id,
            }))}
          />
        </div>
      </Modal>
    </div>
  )
}

export default DeviceManagement
