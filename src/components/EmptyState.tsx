/**
 * 空状态组件 - 友好的空数据提示
 */
import React from 'react';
import { Empty, Button } from 'antd';
import {
  InboxOutlined,
  FileTextOutlined,
  MobileOutlined,
  ClockCircleOutlined,
  BarChartOutlined,
  PlusOutlined,
} from '@ant-design/icons';

interface EmptyStateProps {
  type?: 'device' | 'script' | 'task' | 'report' | 'template' | 'default';
  description?: string;
  actionText?: string;
  onAction?: () => void;
}

const emptyConfig = {
  device: {
    icon: <MobileOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />,
    description: '暂无设备',
    tip: '请连接 Android 设备并开启 USB 调试',
    actionText: '刷新设备列表',
  },
  script: {
    icon: <FileTextOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />,
    description: '暂无脚本',
    tip: '创建您的第一个自动化测试脚本',
    actionText: '创建脚本',
  },
  task: {
    icon: <ClockCircleOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />,
    description: '暂无任务',
    tip: '还没有执行任何任务',
    actionText: '执行任务',
  },
  report: {
    icon: <BarChartOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />,
    description: '暂无报告',
    tip: '执行任务后将生成测试报告',
    actionText: '查看任务',
  },
  template: {
    icon: <InboxOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />,
    description: '暂无模板',
    tip: '从模板市场下载或创建自己的模板',
    actionText: '浏览模板',
  },
  default: {
    icon: <InboxOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />,
    description: '暂无数据',
    tip: '',
    actionText: '刷新',
  },
};

export const EmptyState: React.FC<EmptyStateProps> = ({
  type = 'default',
  description,
  actionText,
  onAction,
}) => {
  const config = emptyConfig[type];

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 400,
        padding: '40px 20px',
      }}
    >
      <Empty
        image={config.icon}
        imageStyle={{ height: 80 }}
        description={
          <div>
            <div style={{ fontSize: 16, color: '#595959', marginBottom: 8 }}>
              {description || config.description}
            </div>
            {config.tip && (
              <div style={{ fontSize: 14, color: '#8c8c8c' }}>
                {config.tip}
              </div>
            )}
          </div>
        }
      >
        {onAction && (
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={onAction}
            size="large"
          >
            {actionText || config.actionText}
          </Button>
        )}
      </Empty>
    </div>
  );
};

export default EmptyState;
