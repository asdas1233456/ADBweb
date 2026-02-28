/**
 * 个性化设置工具
 */

export interface UserSettings {
  theme: 'light' | 'dark';
  layout: 'side' | 'top';
  primaryColor: string;
  fontSize: number;
  compactMode: boolean;
  showGuide: boolean;
  language: 'zh-CN' | 'en-US';
}

const DEFAULT_SETTINGS: UserSettings = {
  theme: 'light',
  layout: 'side',
  primaryColor: '#1890ff',
  fontSize: 14,
  compactMode: false,
  showGuide: true,
  language: 'zh-CN',
};

const SETTINGS_KEY = 'user_settings';

export const getSettings = (): UserSettings => {
  try {
    const saved = localStorage.getItem(SETTINGS_KEY);
    if (saved) {
      return { ...DEFAULT_SETTINGS, ...JSON.parse(saved) };
    }
  } catch (error) {
    console.error('读取设置失败:', error);
  }
  return DEFAULT_SETTINGS;
};

export const saveSettings = (settings: Partial<UserSettings>): void => {
  try {
    const current = getSettings();
    const updated = { ...current, ...settings };
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(updated));
    
    // 触发自定义事件，通知其他组件设置已更新
    window.dispatchEvent(new CustomEvent('settingsChanged', { detail: updated }));
  } catch (error) {
    console.error('保存设置失败:', error);
  }
};

export const resetSettings = (): void => {
  localStorage.removeItem(SETTINGS_KEY);
  window.dispatchEvent(new CustomEvent('settingsChanged', { detail: DEFAULT_SETTINGS }));
};

export const applyTheme = (theme: 'light' | 'dark'): void => {
  document.documentElement.setAttribute('data-theme', theme);
  if (theme === 'dark') {
    document.body.style.background = '#141414';
  } else {
    document.body.style.background = '#f0f2f5';
  }
};

export const applyFontSize = (fontSize: number): void => {
  document.documentElement.style.fontSize = `${fontSize}px`;
};
