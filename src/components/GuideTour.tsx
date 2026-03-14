import React, { useEffect, useMemo, useState } from 'react'
import { Tour } from 'antd'
import type { TourStepProps } from 'antd'
import { GUIDE_START_EVENT, isGuideCompleted, markGuideCompleted, type GuideKey } from '../utils/guide'

interface GuideTourProps {
  tourKey: GuideKey
  steps: TourStepProps[]
  autoStart?: boolean
  delayMs?: number
  onFinish?: () => void
}

export const GuideTour: React.FC<GuideTourProps> = ({
  tourKey,
  steps,
  autoStart = true,
  delayMs = 500,
  onFinish,
}) => {
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (!autoStart || isGuideCompleted(tourKey)) {
      return
    }
    const timer = setTimeout(() => {
      setOpen(true)
    }, delayMs)
    return () => clearTimeout(timer)
  }, [autoStart, delayMs, tourKey])

  useEffect(() => {
    const handler = (event: Event) => {
      const detail = (event as CustomEvent).detail
      if (detail?.key === tourKey) {
        setOpen(true)
      }
    }
    window.addEventListener(GUIDE_START_EVENT, handler)
    return () => window.removeEventListener(GUIDE_START_EVENT, handler)
  }, [tourKey])

  const safeSteps = useMemo(
    () =>
      steps.map((step) => ({
        ...step,
        target: step.target
          ? () => {
              try {
                return step.target?.() || null
              } catch {
                return null
              }
            }
          : undefined,
      })),
    [steps]
  )

  const handleFinish = () => {
    setOpen(false)
    markGuideCompleted(tourKey)
    onFinish?.()
  }

  return (
    <Tour
      open={open}
      onClose={handleFinish}
      onFinish={handleFinish}
      steps={safeSteps}
      indicatorsRender={(current, total) => (
        <span>
          {current + 1} / {total}
        </span>
      )}
    />
  )
}

export const dashboardTourSteps: TourStepProps[] = [
  {
    title: '欢迎使用自动化测试平台',
    description: '让我们快速了解主要功能入口。',
    target: null,
  },
  {
    title: '设备管理',
    description: '在这里查看和管理已连接的 Android 设备。',
    target: () => document.querySelector('[data-tour="devices"]') as HTMLElement,
  },
  {
    title: '脚本管理',
    description: '创建、编辑和管理你的自动化测试脚本。',
    target: () => document.querySelector('[data-tour="scripts"]') as HTMLElement,
  },
  {
    title: '工作台',
    description: '模板市场、示例脚本与最佳实践汇总入口。',
    target: () => document.querySelector('[data-tour="workspace"]') as HTMLElement,
  },
  {
    title: '报告中心',
    description: '查看测试执行报告与统计分析。',
    target: () => document.querySelector('[data-tour="reports"]') as HTMLElement,
  },
]

export const deviceManagementTourSteps: TourStepProps[] = [
  {
    title: '设备管理概览',
    description: '这里可以查看在线与离线设备，并进行批量操作。',
    target: () => document.querySelector('[data-tour="devices-table"]') as HTMLElement,
  },
  {
    title: '搜索设备',
    description: '支持按型号、序列号或系统版本搜索设备。',
    target: () => document.querySelector('[data-tour="devices-search"]') as HTMLElement,
  },
  {
    title: '设备分组',
    description: '按分组过滤设备，方便管理。',
    target: () => document.querySelector('[data-tour="devices-group"]') as HTMLElement,
  },
  {
    title: '刷新与添加',
    description: '扫描刷新 ADB 设备或添加设备。',
    target: () => document.querySelector('[data-tour="devices-actions"]') as HTMLElement,
  },
]

export const deviceHealthTourSteps: TourStepProps[] = [
  {
    title: '健康概览',
    description: '查看设备健康评分与趋势概览。',
    target: () => document.querySelector('[data-tour="health-stats"]') as HTMLElement,
  },
  {
    title: '搜索设备',
    description: '按设备名称或健康等级过滤。',
    target: () => document.querySelector('[data-tour="health-search"]') as HTMLElement,
  },
  {
    title: '立即采集',
    description: '触发采集并刷新健康数据。',
    target: () => document.querySelector('[data-tour="health-collect"]') as HTMLElement,
  },
  {
    title: '健康列表',
    description: '查看每台设备的详细指标。',
    target: () => document.querySelector('[data-tour="health-table"]') as HTMLElement,
  },
  {
    title: '告警列表',
    description: '关注未解决的健康告警。',
    target: () => document.querySelector('[data-tour="health-alerts"]') as HTMLElement,
  },
]

export const scriptListTourSteps: TourStepProps[] = [
  {
    title: '脚本管理',
    description: '集中管理可视化与代码脚本。',
    target: () => document.querySelector('[data-tour="scripts-table"]') as HTMLElement,
  },
  {
    title: '搜索脚本',
    description: '按名称或描述快速定位脚本。',
    target: () => document.querySelector('[data-tour="scripts-search"]') as HTMLElement,
  },
  {
    title: '分类筛选',
    description: '按分类查看不同脚本。',
    target: () => document.querySelector('[data-tour="scripts-tabs"]') as HTMLElement,
  },
  {
    title: '新建脚本',
    description: '创建可视化或代码脚本。',
    target: () => document.querySelector('[data-tour="scripts-new"]') as HTMLElement,
  },
]

export const scheduledTasksTourSteps: TourStepProps[] = [
  {
    title: '定时任务概览',
    description: '查看已配置的定时任务列表。',
    target: () => document.querySelector('[data-tour="scheduled-table"]') as HTMLElement,
  },
  {
    title: '搜索任务',
    description: '按任务名、脚本或设备搜索。',
    target: () => document.querySelector('[data-tour="scheduled-search"]') as HTMLElement,
  },
  {
    title: '创建任务',
    description: '配置脚本、设备与执行时间。',
    target: () => document.querySelector('[data-tour="scheduled-new"]') as HTMLElement,
  },
]

export const aiScriptTourSteps: TourStepProps[] = [
  {
    title: '输入需求',
    description: '描述你的自动化需求，越详细越好。',
    target: () => document.querySelector('[data-tour="ai-prompt"]') as HTMLElement,
  },
  {
    title: '生成脚本',
    description: '一键生成脚本，支持批量与工作流。',
    target: () => document.querySelector('[data-tour="ai-generate"]') as HTMLElement,
  },
  {
    title: '模板与优化',
    description: '使用模板快速开始，并优化提示词。',
    target: () => document.querySelector('[data-tour="ai-templates"]') as HTMLElement,
  },
  {
    title: '脚本输出',
    description: '查看、复制或保存生成结果。',
    target: () => document.querySelector('[data-tour="ai-output"]') as HTMLElement,
  },
  {
    title: '生成历史',
    description: '快速复用历史结果。',
    target: () => document.querySelector('[data-tour="ai-history"]') as HTMLElement,
  },
]

export const aiElementLocatorTourSteps: TourStepProps[] = [
  {
    title: '上传截图',
    description: '上传设备截图进行识别。',
    target: () => document.querySelector('[data-tour="locator-upload"]') as HTMLElement,
  },
  {
    title: '分析结果',
    description: '识别出的元素会在此展示。',
    target: () => document.querySelector('[data-tour="locator-results"]') as HTMLElement,
  },
  {
    title: '元素查询',
    description: '输入关键词查找目标元素。',
    target: () => document.querySelector('[data-tour="locator-search"]') as HTMLElement,
  },
  {
    title: '可视化标注',
    description: '生成标注图，便于定位。',
    target: () => document.querySelector('[data-tour="locator-visualize"]') as HTMLElement,
  },
]

export const reportCenterTourSteps: TourStepProps[] = [
  {
    title: '报告筛选',
    description: '按状态和时间范围筛选报告。',
    target: () => document.querySelector('[data-tour="reports-filters"]') as HTMLElement,
  },
  {
    title: '刷新数据',
    description: '手动刷新报告列表。',
    target: () => document.querySelector('[data-tour="reports-refresh"]') as HTMLElement,
  },
  {
    title: '报告列表',
    description: '查看执行记录与详情。',
    target: () => document.querySelector('[data-tour="reports-table"]') as HTMLElement,
  },
  {
    title: '批量删除',
    description: '按条件清理历史报告。',
    target: () => document.querySelector('[data-tour="reports-batch"]') as HTMLElement,
  },
]

export const failureAnalysisTourSteps: TourStepProps[] = [
  {
    title: '时间范围',
    description: '选择分析时间范围。',
    target: () => document.querySelector('[data-tour="failure-range"]') as HTMLElement,
  },
  {
    title: '刷新数据',
    description: '手动刷新分析结果。',
    target: () => document.querySelector('[data-tour="failure-refresh"]') as HTMLElement,
  },
  {
    title: '统计概览',
    description: '查看失败统计与趋势。',
    target: () => document.querySelector('[data-tour="failure-stats"]') as HTMLElement,
  },
  {
    title: '失败列表',
    description: '查看失败详情。',
    target: () => document.querySelector('[data-tour="failure-table"]') as HTMLElement,
  },
]

export const activityLogTourSteps: TourStepProps[] = [
  {
    title: '搜索日志',
    description: '按关键字快速定位。',
    target: () => document.querySelector('[data-tour="activity-search"]') as HTMLElement,
  },
  {
    title: '筛选条件',
    description: '按类型与状态过滤日志。',
    target: () => document.querySelector('[data-tour="activity-filters"]') as HTMLElement,
  },
  {
    title: '刷新列表',
    description: '拉取最新日志。',
    target: () => document.querySelector('[data-tour="activity-refresh"]') as HTMLElement,
  },
  {
    title: '日志列表',
    description: '查看详细操作记录。',
    target: () => document.querySelector('[data-tour="activity-table"]') as HTMLElement,
  },
]

export const workspaceTourSteps: TourStepProps[] = [
  {
    title: '工作台导航',
    description: '模板、示例、最佳实践与片段入口。',
    target: () => document.querySelector('[data-tour="workspace-tabs"]') as HTMLElement,
  },
  {
    title: '内容搜索',
    description: '快速检索模板或示例。',
    target: () => document.querySelector('[data-tour="workspace-search"]') as HTMLElement,
  },
  {
    title: '内容列表',
    description: '浏览并查看详情。',
    target: () => document.querySelector('[data-tour="workspace-grid"]') as HTMLElement,
  },
]

export const taskMonitorTourSteps: TourStepProps[] = [
  {
    title: '任务列表',
    description: '查看当前运行与历史任务。',
    target: () => document.querySelector('[data-tour="tasks-list"]') as HTMLElement,
  },
  {
    title: '任务操作',
    description: '查看报告、停止任务或分析失败。',
    target: () => document.querySelector('[data-tour="tasks-actions"]') as HTMLElement,
  },
  {
    title: '实时日志',
    description: 'WebSocket 实时日志区域。',
    target: () => document.querySelector('[data-tour="tasks-logs"]') as HTMLElement,
  },
  {
    title: '刷新任务',
    description: '手动刷新任务状态。',
    target: () => document.querySelector('[data-tour="tasks-refresh"]') as HTMLElement,
  },
]

export default GuideTour
