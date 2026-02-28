/**
 * 个性化设置抽屉
 */
import React, { useState, useEffect } from 'react';
import {
  Drawer,
  Space,
  Switch,
  Select,
  Slider,
  Button,
  Divider,
  message,
  Radio,
  ColorPicker,
} from 'antd';
import {
  BgColorsOutlined,
  FontSizeOutlined,
  LayoutOutlined,
  GlobalOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { getSettings, saveSettings, resetSettings, applyTheme, applyFontSize, UserSettings } from '../utils/settings';
import type { Color } from 'antd/es/color-picker';

interface SettingsDrawerProps {
  open: boolean;
  onClose: () => void;
}

export const SettingsDrawer: React.FC<SettingsDrawerProps> = ({ open, onClose }) => {
  const [settings, setSettings] = useState<UserSettings>(getSettings());

  useEffect(() => {
    setSettings(getSettings());
  }, [open]);

  const handleSettingChange = (key: keyof UserSettings, value: any) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    saveSettings({ [key]: value });

    // 立即应用某些设置
    if (key === 'theme') {
      applyTheme(value);
    } else if (key === 'fontSize') {
      applyFontSize(value);
    }

    message.success('设置已保存');
  };

  const handleReset = () => {
    resetSettings();
    const defaultSettings = getSettings();
    setSettings(defaultSettings);
    applyTheme(defaultSettings.theme);
    applyFontSize(defaultSettings.fontSize);
    message.success('已恢复默认设置');
  };

  return (
    <Drawer
      title="个性化设置"
      placement="right"
      width={360}
      onClose={onClose}
      open={open}
      extra={
        <Button icon={<ReloadOutlined />} onClick={handleReset}>
          恢复默认
        </Button>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* 主题设置 */}
        <div>
          <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
            <BgColorsOutlined />
            <span style={{ fontWeight: 500 }}>主题模式</span>
          </div>
          <Radio.Group
            value={settings.theme}
            onChange={(e) => handleSettingChange('theme', e.target.value)}
            buttonStyle="solid"
            style={{ width: '100%' }}
          >
            <Radio.Button value="light" style={{ width: '50%', textAlign: 'center' }}>
              浅色
            </Radio.Button>
            <Radio.Button value="dark" style={{ width: '50%', textAlign: 'center' }}>
              深色
            </Radio.Button>
          </Radio.Group>
        </div>

        <Divider style={{ margin: 0 }} />

        {/* 主题色 */}
        <div>
          <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
            <BgColorsOutlined />
            <span style={{ fontWeight: 500 }}>主题色</span>
          </div>
          <Space wrap>
            {['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2'].map((color) => (
              <div
                key={color}
                onClick={() => handleSettingChange('primaryColor', color)}
                style={{
                  width: 40,
                  height: 40,
                  background: color,
                  borderRadius: 8,
                  cursor: 'pointer',
                  border: settings.primaryColor === color ? '3px solid #000' : '1px solid #d9d9d9',
                  transition: 'all 0.3s',
                }}
              />
            ))}
          </Space>
        </div>

        <Divider style={{ margin: 0 }} />

        {/* 布局模式 */}
        <div>
          <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
            <LayoutOutlined />
            <span style={{ fontWeight: 500 }}>布局模式</span>
          </div>
          <Radio.Group
            value={settings.layout}
            onChange={(e) => handleSettingChange('layout', e.target.value)}
            buttonStyle="solid"
            style={{ width: '100%' }}
          >
            <Radio.Button value="side" style={{ width: '50%', textAlign: 'center' }}>
              侧边栏
            </Radio.Button>
            <Radio.Button value="top" style={{ width: '50%', textAlign: 'center' }}>
              顶部栏
            </Radio.Button>
          </Radio.Group>
        </div>

        <Divider style={{ margin: 0 }} />

        {/* 字体大小 */}
        <div>
          <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
            <FontSizeOutlined />
            <span style={{ fontWeight: 500 }}>字体大小</span>
            <span style={{ marginLeft: 'auto', color: '#8c8c8c' }}>{settings.fontSize}px</span>
          </div>
          <Slider
            min={12}
            max={18}
            value={settings.fontSize}
            onChange={(value) => handleSettingChange('fontSize', value)}
            marks={{
              12: '小',
              14: '中',
              16: '大',
              18: '特大',
            }}
          />
        </div>

        <Divider style={{ margin: 0 }} />

        {/* 紧凑模式 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontWeight: 500 }}>紧凑模式</span>
          <Switch
            checked={settings.compactMode}
            onChange={(checked) => handleSettingChange('compactMode', checked)}
          />
        </div>

        <Divider style={{ margin: 0 }} />

        {/* 显示引导 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontWeight: 500 }}>显示新手引导</span>
          <Switch
            checked={settings.showGuide}
            onChange={(checked) => handleSettingChange('showGuide', checked)}
          />
        </div>

        <Divider style={{ margin: 0 }} />

        {/* 语言设置 */}
        <div>
          <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
            <GlobalOutlined />
            <span style={{ fontWeight: 500 }}>语言</span>
          </div>
          <Select
            value={settings.language}
            onChange={(value) => handleSettingChange('language', value)}
            style={{ width: '100%' }}
            options={[
              { label: '简体中文', value: 'zh-CN' },
              { label: 'English', value: 'en-US' },
            ]}
          />
        </div>

        <Divider style={{ margin: 0 }} />

        {/* 提示信息 */}
        <div
          style={{
            padding: 16,
            background: '#f0f2f5',
            borderRadius: 8,
            fontSize: 12,
            color: '#8c8c8c',
          }}
        >
          💡 提示：某些设置需要刷新页面后生效
        </div>
      </Space>
    </Drawer>
  );
};

export default SettingsDrawer;
