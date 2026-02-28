/**
 * 新手引导组件
 */
import React, { useState, useEffect } from 'react';
import { Tour, TourProps } from 'antd';
import type { TourStepProps } from 'antd';

interface GuideTourProps {
  tourKey: string;
  steps: TourStepProps[];
  onFinish?: () => void;
}

export const GuideTour: React.FC<GuideTourProps> = ({ tourKey, steps, onFinish }) => {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    // 检查是否已经完成过引导
    const hasCompletedTour = localStorage.getItem(`tour_completed_${tourKey}`);
    if (!hasCompletedTour) {
      // 延迟显示，等待页面渲染完成
      const timer = setTimeout(() => {
        setOpen(true);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [tourKey]);

  const handleClose = () => {
    setOpen(false);
    localStorage.setItem(`tour_completed_${tourKey}`, 'true');
    onFinish?.();
  };

  return (
    <Tour
      open={open}
      onClose={handleClose}
      steps={steps}
      indicatorsRender={(current, total) => (
        <span>
          {current + 1} / {total}
        </span>
      )}
    />
  );
};

// 预定义的引导步骤
export const dashboardTourSteps: TourStepProps[] = [
  {
    title: '欢迎使用自动化测试平台',
    description: '让我们快速了解一下主要功能',
    target: null,
  },
  {
    title: '设备管理',
    description: '在这里可以查看和管理所有连接的 Android 设备',
    target: () => document.querySelector('[data-tour="devices"]') as HTMLElement,
  },
  {
    title: '脚本管理',
    description: '创建、编辑和管理您的自动化测试脚本',
    target: () => document.querySelector('[data-tour="scripts"]') as HTMLElement,
  },
  {
    title: '工作台',
    description: '浏览模板市场、示例脚本和最佳实践',
    target: () => document.querySelector('[data-tour="workspace"]') as HTMLElement,
  },
  {
    title: '报告中心',
    description: '查看所有测试执行报告和统计数据',
    target: () => document.querySelector('[data-tour="reports"]') as HTMLElement,
  },
];

export default GuideTour;
