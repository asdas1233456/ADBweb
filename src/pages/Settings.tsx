import { Card, Form, Input, Switch, Button, Select, Space, message, Divider, Spin } from 'antd'
import { SaveOutlined, ReloadOutlined, SearchOutlined } from '@ant-design/icons'
import { useEffect, useState } from 'react'
import { settingsApi, SystemSettings } from '../services/api'

const Settings = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [scanningAdb, setScanningAdb] = useState(false)
  const [scanningPython, setScanningPython] = useState(false)
  const [adbPaths, setAdbPaths] = useState<Array<{ label: string; path: string }>>([])
  const [pythonPaths, setPythonPaths] = useState<Array<{ label: string; path: string }>>([])

  // 扫描ADB路径
  const handleScanAdb = async () => {
    try {
      setScanningAdb(true)
      const paths = await settingsApi.scanAdbPaths()
      setAdbPaths(paths)
      
      if (paths.length > 0) {
        message.success(`找到 ${paths.length} 个ADB路径`)
        // 如果当前没有设置路径，自动选择第一个
        if (!form.getFieldValue('adbPath')) {
          form.setFieldValue('adbPath', paths[0].path)
        }
      } else {
        message.warning('未找到ADB路径，请手动输入')
      }
    } catch (error) {
      message.error('扫描ADB路径失败')
      console.error('Failed to scan ADB paths:', error)
    } finally {
      setScanningAdb(false)
    }
  }

  // 扫描Python路径
  const handleScanPython = async () => {
    try {
      setScanningPython(true)
      const paths = await settingsApi.scanPythonPaths()
      setPythonPaths(paths)
      
      if (paths.length > 0) {
        message.success(`找到 ${paths.length} 个Python路径`)
        // 如果当前没有设置路径，自动选择第一个
        if (!form.getFieldValue('pythonPath')) {
          form.setFieldValue('pythonPath', paths[0].path)
        }
      } else {
        message.warning('未找到Python路径，请手动输入')
      }
    } catch (error) {
      message.error('扫描Python路径失败')
      console.error('Failed to scan Python paths:', error)
    } finally {
      setScanningPython(false)
    }
  }

  // 加载系统配置
  const loadSettings = async () => {
    try {
      setLoading(true)
      const settings = await settingsApi.getAll()
      
      // 转换配置值类型
      const formValues = {
        adbPath: settings.adb_path,
        pythonPath: settings.python_path,
        autoConnect: settings.auto_connect === 'true',
        autoRefresh: settings.auto_refresh === 'true',
        refreshInterval: parseInt(settings.refresh_interval),
        logLevel: settings.log_level,
        maxLogLines: parseInt(settings.max_log_lines),
        screenshotQuality: settings.screenshot_quality,
        screenshotFormat: settings.screenshot_format,
        enableNotification: settings.enable_notification === 'true',
        enableSound: settings.enable_sound === 'true',
      }
      
      form.setFieldsValue(formValues)
    } catch (error) {
      message.error('加载系统配置失败')
      console.error('Failed to load settings:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSettings()
  }, [])

  const handleSave = async (values: any) => {
    try {
      setSaving(true)
      
      // 转换为后端格式
      const settings: Partial<SystemSettings> = {
        adb_path: values.adbPath,
        python_path: values.pythonPath,
        auto_connect: values.autoConnect ? 'true' : 'false',
        auto_refresh: values.autoRefresh ? 'true' : 'false',
        refresh_interval: values.refreshInterval.toString(),
        log_level: values.logLevel,
        max_log_lines: values.maxLogLines.toString(),
        screenshot_quality: values.screenshotQuality,
        screenshot_format: values.screenshotFormat,
        enable_notification: values.enableNotification ? 'true' : 'false',
        enable_sound: values.enableSound ? 'true' : 'false',
      }
      
      await settingsApi.updateAll(settings)
      message.success('设置已保存！')
    } catch (error) {
      message.error('保存设置失败')
      console.error('Failed to save settings:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    loadSettings()
    message.info('已重置为当前保存的设置')
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    )
  }

  return (
    <div>
      <h2 style={{ margin: 0, fontSize: 24, fontWeight: 600, marginBottom: 16 }}>
        系统设置
      </h2>

      <Card
        style={{
          background: '#fff',
          border: '1px solid #e8e8e8',
          marginBottom: 16,
        }}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
        >
          <Divider orientation="left">ADB 配置</Divider>
          
          <Form.Item
            label="ADB 路径"
            name="adbPath"
            tooltip="ADB 工具的安装路径"
            rules={[{ required: true, message: '请输入ADB路径' }]}
          >
            {adbPaths.length > 0 ? (
              <Select
                placeholder="选择ADB路径或手动输入"
                showSearch
                allowClear
                options={adbPaths.map(item => ({
                  label: `${item.label} - ${item.path}`,
                  value: item.path
                }))}
                dropdownRender={(menu) => (
                  <>
                    {menu}
                    <Divider style={{ margin: '8px 0' }} />
                    <Space style={{ padding: '0 8px 4px' }}>
                      <Button
                        type="text"
                        icon={<SearchOutlined />}
                        loading={scanningAdb}
                        onClick={handleScanAdb}
                      >
                        重新扫描
                      </Button>
                    </Space>
                  </>
                )}
              />
            ) : (
              <Input 
                placeholder="C:\platform-tools\adb.exe" 
                addonAfter={
                  <Button
                    type="link"
                    icon={<SearchOutlined />}
                    loading={scanningAdb}
                    onClick={handleScanAdb}
                    style={{ padding: 0 }}
                  >
                    扫描
                  </Button>
                }
              />
            )}
          </Form.Item>

          <Form.Item
            label="自动连接设备"
            name="autoConnect"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            label="自动刷新设备列表"
            name="autoRefresh"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            label="刷新间隔（秒）"
            name="refreshInterval"
            tooltip="设备列表自动刷新的时间间隔"
          >
            <Select>
              <Select.Option value={3}>3秒</Select.Option>
              <Select.Option value={5}>5秒</Select.Option>
              <Select.Option value={10}>10秒</Select.Option>
              <Select.Option value={30}>30秒</Select.Option>
            </Select>
          </Form.Item>

          <Divider orientation="left">脚本执行配置</Divider>

          <Form.Item
            label="Python 路径"
            name="pythonPath"
            tooltip="Python 解释器的安装路径"
            rules={[{ required: true, message: '请输入Python路径' }]}
          >
            {pythonPaths.length > 0 ? (
              <Select
                placeholder="选择Python路径或手动输入"
                showSearch
                allowClear
                options={pythonPaths.map(item => ({
                  label: `${item.label} - ${item.path}`,
                  value: item.path
                }))}
                dropdownRender={(menu) => (
                  <>
                    {menu}
                    <Divider style={{ margin: '8px 0' }} />
                    <Space style={{ padding: '0 8px 4px' }}>
                      <Button
                        type="text"
                        icon={<SearchOutlined />}
                        loading={scanningPython}
                        onClick={handleScanPython}
                      >
                        重新扫描
                      </Button>
                    </Space>
                  </>
                )}
              />
            ) : (
              <Input 
                placeholder="C:\Python39\python.exe" 
                addonAfter={
                  <Button
                    type="link"
                    icon={<SearchOutlined />}
                    loading={scanningPython}
                    onClick={handleScanPython}
                    style={{ padding: 0 }}
                  >
                    扫描
                  </Button>
                }
              />
            )}
          </Form.Item>

          <Form.Item
            label="日志级别"
            name="logLevel"
          >
            <Select>
              <Select.Option value="debug">Debug</Select.Option>
              <Select.Option value="info">Info</Select.Option>
              <Select.Option value="warning">Warning</Select.Option>
              <Select.Option value="error">Error</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="最大日志行数"
            name="maxLogLines"
            tooltip="日志显示的最大行数，超过后自动清理"
          >
            <Select>
              <Select.Option value={500}>500行</Select.Option>
              <Select.Option value={1000}>1000行</Select.Option>
              <Select.Option value={2000}>2000行</Select.Option>
              <Select.Option value={5000}>5000行</Select.Option>
            </Select>
          </Form.Item>

          <Divider orientation="left">截图配置</Divider>

          <Form.Item
            label="截图质量"
            name="screenshotQuality"
          >
            <Select>
              <Select.Option value="low">低（快速）</Select.Option>
              <Select.Option value="medium">中等</Select.Option>
              <Select.Option value="high">高（清晰）</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="截图格式"
            name="screenshotFormat"
          >
            <Select>
              <Select.Option value="png">PNG</Select.Option>
              <Select.Option value="jpg">JPG</Select.Option>
            </Select>
          </Form.Item>

          <Divider orientation="left">通知设置</Divider>

          <Form.Item
            label="启用桌面通知"
            name="enableNotification"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            label="启用提示音"
            name="enableSound"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={saving}
              >
                保存设置
              </Button>
              <Button icon={<ReloadOutlined />} onClick={handleReset}>
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default Settings
