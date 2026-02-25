/**
 * 实时任务监控测试页面
 */
import React, { useState } from 'react';
import { Card, Button, Space, Form, Select, Input, message, Modal } from 'antd';
import { PlayCircleOutlined, EyeOutlined } from '@ant-design/icons';
import TaskMonitor from '../components/TaskMonitor';

const { Option } = Select;

const RealtimeTaskTest: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [monitorVisible, setMonitorVisible] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState<number | null>(null);

  const handleExecute = async (values: any) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/tasks/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_name: values.task_name,
          script_id: parseInt(values.script_id),
          device_id: parseInt(values.device_id),
        }),
      });

      const result = await response.json();

      if (result.code === 200) {
        message.success('任务已开始执行');
        setCurrentTaskId(result.data.task_log_id);
        setMonitorVisible(true);
      } else {
        message.error(result.message || '任务执行失败');
      }
    } catch (error) {
      message.error('网络错误');
      console.error('执行任务失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskComplete = (status: string) => {
    if (status === 'success') {
      message.success('任务执行成功！');
    } else {
      message.error('任务执行失败！');
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ marginBottom: 24 }}>实时任务监控测试</h2>

      <Card title="执行任务" style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleExecute}
          initialValues={{
            task_name: '测试任务',
            script_id: '1',
            device_id: '1',
          }}
        >
          <Form.Item
            label="任务名称"
            name="task_name"
            rules={[{ required: true, message: '请输入任务名称' }]}
          >
            <Input placeholder="输入任务名称" />
          </Form.Item>

          <Form.Item
            label="脚本ID"
            name="script_id"
            rules={[{ required: true, message: '请选择脚本' }]}
          >
            <Select placeholder="选择脚本">
              <Option value="1">测试脚本 1</Option>
              <Option value="2">测试脚本 2</Option>
              <Option value="3">测试脚本 3</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="设备ID"
            name="device_id"
            rules={[{ required: true, message: '请选择设备' }]}
          >
            <Select placeholder="选择设备">
              <Option value="1">设备 1</Option>
              <Option value="2">设备 2</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<PlayCircleOutlined />}
                loading={loading}
              >
                执行任务
              </Button>
              {currentTaskId && (
                <Button
                  icon={<EyeOutlined />}
                  onClick={() => setMonitorVisible(true)}
                >
                  查看监控
                </Button>
              )}
            </Space>
          </Form.Item>
        </Form>
      </Card>

      {/* 任务监控弹窗 */}
      <Modal
        title="任务实时监控"
        open={monitorVisible}
        onCancel={() => setMonitorVisible(false)}
        width={900}
        footer={null}
        destroyOnClose
      >
        {currentTaskId && (
          <TaskMonitor
            taskId={currentTaskId}
            onComplete={handleTaskComplete}
          />
        )}
      </Modal>
    </div>
  );
};

export default RealtimeTaskTest;
