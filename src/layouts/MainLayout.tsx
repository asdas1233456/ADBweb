import { useState, useEffect } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Avatar, Dropdown, Tooltip, theme, Badge, Popover, List, Button, Empty, message } from 'antd'
import {
  MobileOutlined,
  FileTextOutlined,
  PlayCircleOutlined,
  BarChartOutlined,
  LineChartOutlined,
  ClockCircleOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  BellOutlined,
  AppstoreOutlined,
  BgColorsOutlined,
  QuestionCircleOutlined,
  HeartOutlined,
  BugOutlined,
  HistoryOutlined,
  RobotOutlined,
  AimOutlined,
} from '@ant-design/icons'
import type { MenuProps } from 'antd'
import SettingsDrawer from '../components/SettingsDrawer'
import { GuideTour, dashboardTourSteps } from '../components/GuideTour'
import { getSettings } from '../utils/settings'
import { activityLogApi, type ActivityLog } from '../services/api'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const { Header, Sider, Content } = Layout

const MainLayout = () => {
  const { token } = theme.useToken() // 获取主题token
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [notificationOpen, setNotificationOpen] = useState(false)
  const [notifications, setNotifications] = useState<ActivityLog[]>([])
  const [loadingNotifications, setLoadingNotifications] = useState(false)
  const settings = getSettings()

  // 加载通知（活动日志）
  const loadNotifications = async () => {
    setLoadingNotifications(true)
    try {
      const logs = await activityLogApi.getList({ limit: 10 })
      setNotifications(logs)
    } catch (error) {
      console.error('加载通知失败:', error)
    } finally {
      setLoadingNotifications(false)
    }
  }

  // 组件挂载时加载通知
  useEffect(() => {
    loadNotifications()
    
    // 每30秒刷新一次通知
    const interval = setInterval(loadNotifications, 30000)
    return () => clearInterval(interval)
  }, [])

  // 打开通知面板时刷新
  const handleNotificationOpenChange = (open: boolean) => {
    setNotificationOpen(open)
    if (open) {
      loadNotifications()
    }
  }

  const menuItems: MenuProps['items'] = [
    {
      key: '/dashboard',
      icon: <BarChartOutlined />,
      label: '仪表盘',
      ['data-tour']: 'dashboard',
    },
    {
      key: 'device-group',
      icon: <MobileOutlined />,
      label: '设备中心',
      children: [
        {
          key: '/devices',
          icon: <MobileOutlined />,
          label: '设备管理',
          ['data-tour']: 'devices',
        },
        {
          key: '/device-health',
          icon: <HeartOutlined />,
          label: '设备健康度',
          ['data-tour']: 'device-health',
        },
      ],
    },
    {
      key: 'script-group',
      icon: <FileTextOutlined />,
      label: '脚本中心',
      children: [
        {
          key: '/scripts',
          icon: <FileTextOutlined />,
          label: '脚本管理',
          ['data-tour']: 'scripts',
        },
        {
          key: '/ai-script',
          icon: <RobotOutlined />,
          label: 'AI脚本生成',
        },
        {
          key: '/ai-element-locator',
          icon: <AimOutlined />,
          label: 'AI元素定位',
        },
        {
          key: '/workspace',
          icon: <AppstoreOutlined />,
          label: '工作台',
          ['data-tour']: 'workspace',
        },
      ],
    },
    {
      key: 'task-group',
      icon: <PlayCircleOutlined />,
      label: '任务中心',
      children: [
        {
          key: '/tasks/1',
          icon: <PlayCircleOutlined />,
          label: '任务执行',
        },
        {
          key: '/scheduled',
          icon: <ClockCircleOutlined />,
          label: '定时任务',
        },
      ],
    },
    {
      key: 'analysis-group',
      icon: <LineChartOutlined />,
      label: '分析中心',
      children: [
        {
          key: '/reports',
          icon: <LineChartOutlined />,
          label: '报告中心',
          ['data-tour']: 'reports',
        },
        {
          key: '/failure-analysis',
          icon: <BugOutlined />,
          label: '失败分析',
        },
        {
          key: '/activity-log',
          icon: <HistoryOutlined />,
          label: '活动日志',
        },
      ],
    },
    {
      key: '/alert-rules',
      icon: <BellOutlined />,
      label: '告警规则',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
  ]

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '个人设置',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  const handleRestartTour = () => {
    localStorage.removeItem('tour_completed_dashboard')
    window.location.reload()
  }

  const handleMarkAllRead = () => {
    // 清空通知列表
    setNotifications([])
    setNotificationOpen(false)
    message.success('已标记所有通知为已读')
  }

  // 获取活动类型的显示文本
  const getActivityTypeText = (type: string): string => {
    const typeMap: Record<string, string> = {
      'device_refresh': '设备刷新',
      'device_connect': '设备连接',
      'device_disconnect': '设备断开',
      'script_execute': '脚本执行',
      'script_create': '脚本创建',
      'script_update': '脚本更新',
      'task_start': '任务开始',
      'task_complete': '任务完成',
      'task_failed': '任务失败',
      'device_create': '设备添加',
      'device_delete': '设备删除',
      'device_scan': '设备扫描',
    }
    return typeMap[type] || type
  }

  const notificationContent = (
    <div style={{ width: 320 }}>
      <div style={{ 
        padding: '12px 16px', 
        borderBottom: `1px solid ${token.colorBorder}`,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <span style={{ fontWeight: 600, fontSize: 14 }}>通知中心</span>
        <Button type="link" size="small" onClick={handleMarkAllRead}>
          全部已读
        </Button>
      </div>
      {loadingNotifications ? (
        <div style={{ padding: '40px 0', textAlign: 'center' }}>
          <Empty description="加载中..." image={Empty.PRESENTED_IMAGE_SIMPLE} />
        </div>
      ) : notifications.length > 0 ? (
        <List
          dataSource={notifications}
          renderItem={(item) => (
            <List.Item
              style={{
                padding: '12px 16px',
                cursor: 'pointer',
                transition: 'background 0.3s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = token.colorBgTextHover
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent'
              }}
              onClick={() => {
                // 点击通知可以跳转到活动日志页面
                navigate('/activity-logs')
                setNotificationOpen(false)
              }}
            >
              <List.Item.Meta
                title={
                  <span style={{ fontSize: 14, fontWeight: 500 }}>
                    {getActivityTypeText(item.activity_type)}
                  </span>
                }
                description={
                  <div>
                    <div style={{ fontSize: 13, color: token.colorTextSecondary, marginBottom: 4 }}>
                      {item.description}
                    </div>
                    <div style={{ fontSize: 12, color: token.colorTextTertiary }}>
                      {dayjs(item.created_at).fromNow()}
                    </div>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      ) : (
        <Empty 
          description="暂无通知" 
          style={{ padding: '40px 0' }}
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      )}
      <div style={{ 
        padding: '8px 16px', 
        borderTop: `1px solid ${token.colorBorder}`,
        textAlign: 'center',
      }}>
        <Button 
          type="link" 
          size="small"
          onClick={() => {
            navigate('/activity-logs')
            setNotificationOpen(false)
          }}
        >
          查看全部通知
        </Button>
      </div>
    </div>
  )

  const getSelectedKey = () => {
    const path = location.pathname
    if (path.startsWith('/scripts')) return '/scripts'
    if (path.startsWith('/tasks')) return '/tasks/1'
    if (path === '/') return '/dashboard'
    return path
  }

  const getOpenKeys = () => {
    const path = location.pathname
    const openKeys: string[] = []
    
    if (path === '/devices' || path === '/device-health') {
      openKeys.push('device-group')
    }
    if (path === '/scripts' || path === '/workspace' || path === '/ai-script' || path.startsWith('/scripts')) {
      openKeys.push('script-group')
    }
    if (path.startsWith('/tasks') || path === '/scheduled') {
      openKeys.push('task-group')
    }
    if (path === '/reports' || path === '/failure-analysis' || path === '/activity-log') {
      openKeys.push('analysis-group')
    }
    
    return openKeys
  }

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        width={240}
        style={{
          background: '#fff',
          borderRight: '1px solid #e8e8e8',
          boxShadow: '2px 0 8px rgba(0, 0, 0, 0.04)',
        }}
        trigger={
          <div style={{ 
            background: '#fff', 
            borderTop: '1px solid #e8e8e8',
            color: '#595959',
          }}>
            {collapsed ? '▶' : '◀'}
          </div>
        }
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: collapsed ? 16 : 20,
            fontWeight: 700,
            color: '#1890ff',
            borderBottom: '1px solid #e8e8e8',
            padding: '0 16px',
            letterSpacing: '0.5px',
          }}
        >
          {collapsed ? '🤖' : '🤖 自动化测试平台'}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[getSelectedKey()]}
          defaultOpenKeys={getOpenKeys()}
          items={menuItems}
          onClick={handleMenuClick}
          style={{
            background: 'transparent',
            border: 'none',
            marginTop: 8,
          }}
        />
      </Sider>
      <Layout style={{ background: '#f0f2f5' }}>
        <Header
          style={{
            padding: '0 32px',
            background: '#fff',
            borderBottom: '1px solid #e8e8e8',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
            height: 64,
          }}
        >
          <div style={{ 
            fontSize: 18, 
            fontWeight: 600,
            color: token.colorText,
            display: 'flex',
            alignItems: 'center',
            gap: 12,
          }}>
            <span style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: '#52c41a',
              boxShadow: '0 0 8px rgba(82, 196, 26, 0.6)',
              animation: 'pulse 2s infinite',
            }} />
            手机自动化测试平台
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            <Tooltip title="重新开始引导">
              <div style={{ 
                position: 'relative',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                padding: '8px',
                borderRadius: '50%',
              }}
              onClick={handleRestartTour}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = token.colorBgTextHover
                const icon = e.currentTarget.querySelector('.anticon')
                if (icon) (icon as HTMLElement).style.color = token.colorPrimary
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent'
                const icon = e.currentTarget.querySelector('.anticon')
                if (icon) (icon as HTMLElement).style.color = token.colorTextSecondary
              }}
              >
                <QuestionCircleOutlined style={{ 
                  fontSize: 20, 
                  color: token.colorTextSecondary,
                  transition: 'color 0.3s ease',
                }} />
              </div>
            </Tooltip>

            <Tooltip title="个性化设置">
              <div style={{ 
                position: 'relative',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                padding: '8px',
                borderRadius: '50%',
              }}
              onClick={() => {
                console.log('设置按钮被点击')
                setSettingsOpen(true)
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = token.colorBgTextHover
                const icon = e.currentTarget.querySelector('.anticon')
                if (icon) (icon as HTMLElement).style.color = token.colorPrimary
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent'
                const icon = e.currentTarget.querySelector('.anticon')
                if (icon) (icon as HTMLElement).style.color = token.colorTextSecondary
              }}
              >
                <BgColorsOutlined style={{ 
                  fontSize: 20, 
                  color: token.colorTextSecondary,
                  transition: 'color 0.3s ease',
                }} />
              </div>
            </Tooltip>

            <Popover
              content={notificationContent}
              trigger="click"
              open={notificationOpen}
              onOpenChange={handleNotificationOpenChange}
              placement="bottomRight"
              overlayStyle={{ paddingTop: 8 }}
            >
              <Badge count={notifications.length} size="small">
                <div style={{ 
                  position: 'relative',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  padding: '8px',
                  borderRadius: '50%',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = token.colorBgTextHover
                  const icon = e.currentTarget.querySelector('.anticon')
                  if (icon) (icon as HTMLElement).style.color = token.colorPrimary
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent'
                  const icon = e.currentTarget.querySelector('.anticon')
                  if (icon) (icon as HTMLElement).style.color = token.colorTextSecondary
                }}
                >
                  <BellOutlined style={{ 
                    fontSize: 20, 
                    color: token.colorTextSecondary,
                    transition: 'color 0.3s ease',
                  }} />
                </div>
              </Badge>
            </Popover>
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 12, 
                cursor: 'pointer',
                padding: '8px 16px',
                borderRadius: 8,
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = token.colorBgTextHover
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent'
              }}
              >
                <Avatar 
                  icon={<UserOutlined />} 
                  style={{ 
                    background: token.colorPrimary,
                  }} 
                />
                <span style={{ fontWeight: 500, color: token.colorText }}>测试用户</span>
              </div>
            </Dropdown>
          </div>
        </Header>
        <Content
          style={{
            margin: '24px 24px 0',
            padding: 0,
            background: 'transparent',
            overflow: 'auto',
            minHeight: 'calc(100vh - 112px)',
          }}
        >
          <Outlet />
        </Content>
      </Layout>
      <style>{`
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
      `}</style>

      {/* 个性化设置抽屉 */}
      <SettingsDrawer open={settingsOpen} onClose={() => setSettingsOpen(false)} />

      {/* 新手引导 */}
      {settings.showGuide && location.pathname === '/dashboard' && (
        <GuideTour tourKey="dashboard" steps={dashboardTourSteps} />
      )}
    </Layout>
  )
}

export default MainLayout
