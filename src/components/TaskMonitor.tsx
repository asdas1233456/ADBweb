/**
 * 任务实时监控组件
 */
import React, { useEffect, useState } from 'react';
import { Card, Progress, Timeline, Tag, Badge, Space, Typography, Empty } from 'antd';
import { 
  PlayCircleOutlined, 
  CheckCircleOutlined, 
  CloseCircleOutlined,
  LoadingOutlined,
  WifiOutlined
} from '@ant-design/icons';
import { useWebSocket } from '../hooks/useWebSocket';

const { Text, Title } = Typography;

interface TaskStatus {
  status: 'running' | 'success' | 'failed';
  progress: number;
  current_step: number;
  total_steps: number;
  message: string;
  logs: Array<{ time: string; message: string; level: string }>;
}

interface TaskMonitorProps {
  taskId: number;
  onComplete?: (status: string) => void;
}

export const TaskMonitor: React.FC<TaskMonitorProps> = ({ taskId, onComplete }) => {
  const clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const { isConnected, lastMessage, subscribeTask } = useWebSocket(
    'ws://localhost:8000/api/v1/ws',
    clientId
  );
  
  const [taskStatus, setTaskStatus] = useState<TaskStatus>({
    status: 'running',
    progress: 0,
    current_step: 0,
    total_steps: 0,
    message: '等待任务开始...',
    logs: [],
  });

  useEffect(() => {
    if (isConnected) {
      subscribeTask(taskId);
    }
  }, [isConnected, taskId, subscribeTask]);

  useEffect(() => {
    if (lastMessage && lastMessage.task_id === taskId) {
      const data = lastMessage.data;
      
      if (data.type === 'log') {
        // 添加日志
        setTaskStatus(prev => ({
          ...prev,
          logs: [...prev.logs, {
            time: new Date().toLocaleTimeString(),
            message: data.message,
            level: data.level || 'info',
          }].slice(-50), // 只保留最近50条日志
        }));
      } else {
        // 更新任务状态
        setTaskStatus(prev => ({
          ...prev,
          status: data.status || prev.status,
          progress: data.progress !== undefined ? data.progress : prev.progress,
          current_step: data.current_step !== undefined ? data.current_step : prev.current_step,
          total_steps: data.total_steps !== undefined ? data.total_steps : prev.total_steps,
          message: data.message || prev.message,
        }));
        
        // 任务完成回调
        if ((data.status === 'success' || data.status === 'failed') && onComplete) {
          onComplete(data.status);
        }
      }
    }
  }, [lastMessage, taskId, onComplete]);

  const getStatusIcon = () => {
    switch (taskStatus.status) {
      case 'running':
        return <LoadingOutlined style={{ color: '#1890ff', fontSize: 20 }} spin />;
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 20 }} />;
      case 'failed':
        return <CloseCircleOutlined style={{ color: '#ff4d4f', fontSize: 20 }} />;
      default:
        return <PlayCircleOutlined style={{ fontSize: 20 }} />;
    }
  };

  const getStatusColor = (): any => {
    switch (taskStatus.status) {
      case 'running':
        return 'processing';
      case 'success':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getLogColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'red';
      case 'warning':
        return 'orange';
      case 'success':
        return 'green';
      case 'debug':
        return 'gray';
      default:
        return 'blue';
    }
  };

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      {/* 任务状态卡片 */}
      <Card>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Space>
              {getStatusIcon()}
              <Title level={4} style={{ margin: 0 }}>
                任务 #{taskId}
              </Title>
            </Space>
            <Space>
              <Badge 
                status={getStatusColor()} 
                text={taskStatus.message} 
              />
              <Tag 
                icon={<WifiOutlined />}
                color={isConnected ? 'success' : 'error'}
              >
                {isConnected ? '已连接' : '未连接'}
              </Tag>
            </Space>
          </div>
          
          <Progress 
            percent={taskStatus.progress} 
            status={taskStatus.status === 'failed' ? 'exception' : taskStatus.status === 'success' ? 'success' : 'active'}
            format={() => `${taskStatus.current_step}/${taskStatus.total_steps} 步`}
          />
          
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Text type="secondary">
              当前进度: {taskStatus.current_step}/{taskStatus.total_steps}
            </Text>
            <Text type="secondary">
              完成度: {taskStatus.progress}%
            </Text>
          </div>
        </Space>
      </Card>

      {/* 实时日志 */}
      <Card 
        title="执行日志" 
        style={{ 
          maxHeight: 500, 
          overflow: 'auto' 
        }}
        className="custom-scrollbar"
      >
        {taskStatus.logs.length > 0 ? (
          <Timeline
            items={taskStatus.logs.map((log, index) => ({
              color: getLogColor(log.level),
              children: (
                <div key={index}>
                  <Text type="secondary" style={{ fontSize: 12 }}>{log.time}</Text>
                  <br />
                  <Text style={{ fontFamily: 'monospace', fontSize: 13 }}>{log.message}</Text>
                </div>
              ),
            }))}
          />
        ) : (
          <Empty 
            description="暂无日志" 
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}
      </Card>
    </Space>
  );
};

export default TaskMonitor;
