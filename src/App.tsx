import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, theme, App as AntApp, Spin } from 'antd'
import { lazy, Suspense, useEffect, useState } from 'react'
import MainLayout from './layouts/MainLayout'
import ErrorBoundary from './components/ErrorBoundary'
import { getSettings, applyTheme, applyFontSize, UserSettings } from './utils/settings'
import zhCN from 'antd/locale/zh_CN'
import enUS from 'antd/locale/en_US'

// 路由懒加载
const Dashboard = lazy(() => import('./pages/Dashboard'))
const DeviceManagement = lazy(() => import('./pages/DeviceManagement'))
const DeviceHealth = lazy(() => import('./pages/DeviceHealth'))
const ScriptList = lazy(() => import('./pages/ScriptList'))
const ScriptEditor = lazy(() => import('./pages/ScriptEditor'))
const Workspace = lazy(() => import('./pages/Workspace'))
const TaskMonitor = lazy(() => import('./pages/TaskMonitor'))
const ScheduledTasks = lazy(() => import('./pages/ScheduledTasks'))
const ReportCenter = lazy(() => import('./pages/ReportCenter'))
const FailureAnalysis = lazy(() => import('./pages/FailureAnalysis'))
const AlertRules = lazy(() => import('./pages/AlertRules'))
const ActivityLog = lazy(() => import('./pages/ActivityLog'))
const Settings = lazy(() => import('./pages/Settings'))
const RealtimeTaskTest = lazy(() => import('./pages/RealtimeTaskTest'))
const AIScriptGenerator = lazy(() => import('./pages/AIScriptGenerator'))
const AIElementLocator = lazy(() => import('./pages/AIElementLocator'))

// 加载中组件
const LoadingFallback = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    minHeight: '400px',
    width: '100%'
  }}>
    <Spin size="large" tip="加载中..." />
  </div>
)

function App() {
  const [settings, setSettings] = useState<UserSettings>(getSettings());

  useEffect(() => {
    // 应用初始设置
    applyTheme(settings.theme);
    applyFontSize(settings.fontSize);

    // 监听设置变化
    const handleSettingsChange = (e: CustomEvent) => {
      setSettings(e.detail);
    };

    window.addEventListener('settingsChanged', handleSettingsChange as EventListener);
    return () => {
      window.removeEventListener('settingsChanged', handleSettingsChange as EventListener);
    };
  }, []);

  // 根据主题选择算法
  const algorithm = settings.theme === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm;
  
  // 根据语言选择 locale
  const locale = settings.language === 'en-US' ? enUS : zhCN;

  return (
    <ErrorBoundary>
      <ConfigProvider
        locale={locale}
        theme={{
          algorithm,
          token: {
            colorPrimary: settings.primaryColor,
            colorSuccess: '#52c41a',
            colorWarning: '#faad14',
            colorError: '#ff4d4f',
            colorInfo: settings.primaryColor,
            colorBgBase: settings.theme === 'dark' ? '#141414' : '#f0f2f5',
            colorBgContainer: settings.theme === 'dark' ? '#1f1f1f' : '#ffffff',
            colorBorder: settings.theme === 'dark' ? '#434343' : '#d9d9d9',
            borderRadius: 6,
            fontSize: settings.fontSize,
          },
          components: settings.compactMode ? {
            Table: {
              cellPaddingBlock: 8,
              cellPaddingInline: 8,
            },
            Card: {
              paddingLG: 16,
            },
          } : undefined,
        }}
      >
        <AntApp>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<MainLayout />}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <Dashboard />
                  </Suspense>
                } />
                <Route path="devices" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <DeviceManagement />
                  </Suspense>
                } />
                <Route path="device-health" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <DeviceHealth />
                  </Suspense>
                } />
                <Route path="scripts" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <ScriptList />
                  </Suspense>
                } />
                <Route path="scripts/:id" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <ScriptEditor />
                  </Suspense>
                } />
                <Route path="workspace" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <Workspace />
                  </Suspense>
                } />
                <Route path="tasks/:id" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <TaskMonitor />
                  </Suspense>
                } />
                <Route path="scheduled" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <ScheduledTasks />
                  </Suspense>
                } />
                <Route path="reports" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <ReportCenter />
                  </Suspense>
                } />
                <Route path="failure-analysis" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <FailureAnalysis />
                  </Suspense>
                } />
                <Route path="alert-rules" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <AlertRules />
                  </Suspense>
                } />
                <Route path="activity-log" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <ActivityLog />
                  </Suspense>
                } />
                <Route path="settings" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <Settings />
                  </Suspense>
                } />
                <Route path="realtime-test" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <RealtimeTaskTest />
                  </Suspense>
                } />
                <Route path="ai-script" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <AIScriptGenerator />
                  </Suspense>
                } />
                <Route path="ai-element-locator" element={
                  <Suspense fallback={<LoadingFallback />}>
                    <AIElementLocator />
                  </Suspense>
                } />
              </Route>
            </Routes>
          </BrowserRouter>
        </AntApp>
      </ConfigProvider>
    </ErrorBoundary>
  )
}

export default App
