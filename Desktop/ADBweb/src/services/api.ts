/**
 * API 服务�?- 统一管理后端接口调用
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

// 统一响应格式
interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

// 分页响应格式
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// 通用请求方法
async function request<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result: ApiResponse<T> = await response.json();
    
    if (result.code !== 200) {
      throw new Error(result.message || '请求失败');
    }

    return result.data;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// ==================== 仪表盘接�?====================

export interface DashboardData {
  statistics: {
    online_devices: number;
    total_devices: number;
    total_scripts: number;
    today_executions: number;
    success_rate: number;
  };
  device_status: Array<{
    id: number;
    model: string;
    battery: number;
    status: string;
  }>;
  execution_stats: {
    success_count: number;
    failed_count: number;
    running_count: number;
    total_count: number;
    success_percentage: number;
    failed_percentage: number;
    running_percentage: number;
  };
  recent_activities: Array<{
    id: number;
    activity_type: string;
    description: string;
    user_name: string;
    status: string;
    created_at: string;
  }>;
}

export const dashboardApi = {
  // 获取仪表盘概览数�?
  getOverview: () => request<DashboardData>('/dashboard/overview'),
};

// ==================== 设备管理接口 ====================

export interface Device {
  id: number;
  serial_number: string;
  model: string;
  android_version: string;
  resolution?: string;
  battery: number;
  status: 'online' | 'offline' | 'busy';
  last_connected_at?: string;
  created_at: string;
  updated_at: string;
}

export const deviceApi = {
  // 获取设备列表
  getList: (params?: { status?: string; page?: number; page_size?: number }) =>
    request<PaginatedResponse<Device>>(`/devices?${new URLSearchParams(params as any)}`),
  
  // 获取设备详情
  getDetail: (id: number) => request<Device>(`/devices/${id}`),
  
  // 刷新设备列表
  refresh: () => request('/devices/refresh', { method: 'POST' }),
  
  // 断开设备连接
  disconnect: (id: number) => request(`/devices/${id}/disconnect`, { method: 'POST' }),
  
  // 获取设备分组列表
  getGroups: () => request<string[]>('/devices/groups/list'),
  
  // 更新设备分组
  updateGroup: (id: number, group_name?: string) =>
    request<Device>(`/devices/${id}/group`, {
      method: 'PUT',
      body: JSON.stringify({ group_name }),
    }),
  
  // 获取设备截图
  getScreenshot: (id: number) =>
    request<{ device_id: number; screenshot_url: string; timestamp: string }>(
      `/devices/${id}/screenshot`
    ),
  
  // 获取设备性能数据
  getPerformance: (id: number) =>
    request<{
      device_id: number;
      cpu_usage: number;
      memory_usage: number;
      battery: number;
      temperature: number;
      timestamp: string;
    }>(`/devices/${id}/performance`),
  
  // 批量执行脚本
  batchExecute: (device_ids: number[], script_id: number) =>
    request('/devices/batch/execute', {
      method: 'POST',
      body: JSON.stringify({ device_ids, script_id }),
    }),
};

// ==================== 脚本管理接口 ====================

export interface Script {
  id: number;
  name: string;
  type: 'visual' | 'python' | 'batch';
  category: 'login' | 'test' | 'automation' | 'other';
  description?: string;
  file_path?: string;
  file_content?: string;
  steps_json?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const scriptApi = {
  // 获取脚本列表
  getList: (params?: {
    type?: string;
    category?: string;
    keyword?: string;
    page?: number;
    page_size?: number;
  }) => request<PaginatedResponse<Script>>(`/scripts?${new URLSearchParams(params as any)}`),
  
  // 获取脚本详情
  getDetail: (id: number) => request<Script>(`/scripts/${id}`),
  
  // 创建脚本
  create: (data: Partial<Script>) =>
    request<Script>('/scripts', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 更新脚本
  update: (id: number, data: Partial<Script>) =>
    request<Script>(`/scripts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  // 删除脚本
  delete: (id: number) => request(`/scripts/${id}`, { method: 'DELETE' }),
  
  // 验证脚本
  validate: (data: { script_type: string; content: string; filename?: string }) =>
    request<{
      passed: boolean;
      score: number;
      items: Array<{
        name: string;
        level: 'success' | 'warning' | 'error';
        message: string;
        details: string;
      }>;
      suggestions: string[];
    }>('/scripts/validate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// ==================== 模板市场接口 ====================

export interface Template {
  id: number;
  name: string;
  description: string;
  author: string;
  category: string;
  type: 'visual' | 'python' | 'batch';
  tags: string;
  content: string;
  preview: string;
  downloads: number;
  rating: number;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
}

export const templateApi = {
  // 获取模板列表
  getList: (params?: {
    category?: string;
    type?: string;
    keyword?: string;
    sort_by?: string;
    page?: number;
    page_size?: number;
  }) => request<PaginatedResponse<Template>>(`/templates?${new URLSearchParams(params as any)}`),
  
  // 获取模板详情
  getDetail: (id: number) => request<Template>(`/templates/${id}`),
  
  // 下载模板（转为脚本）
  download: (id: number, data: { script_name: string; category: string }) =>
    request(`/templates/${id}/download`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// ==================== 定时任务接口 ====================

export interface ScheduledTask {
  id: number;
  name: string;
  script_id: number;
  script_name?: string;
  device_id: number;
  device_name?: string;
  frequency: 'daily' | 'weekly' | 'monthly';
  schedule_time: string;
  schedule_day?: string;
  is_enabled: boolean;
  last_run_at?: string;
  next_run_at?: string;
  run_count: number;
  success_count: number;
  fail_count: number;
  created_at: string;
  updated_at: string;
}

export const scheduledTaskApi = {
  // 获取定时任务列表
  getList: (params?: { is_enabled?: boolean; page?: number; page_size?: number }) =>
    request<PaginatedResponse<ScheduledTask>>(
      `/scheduled-tasks?${new URLSearchParams(params as any)}`
    ),
  
  // 获取定时任务详情
  getDetail: (id: number) => request<ScheduledTask>(`/scheduled-tasks/${id}`),
  
  // 创建定时任务
  create: (data: Partial<ScheduledTask>) =>
    request<ScheduledTask>('/scheduled-tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 更新定时任务
  update: (id: number, data: Partial<ScheduledTask>) =>
    request<ScheduledTask>(`/scheduled-tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  // 删除定时任务
  delete: (id: number) => request(`/scheduled-tasks/${id}`, { method: 'DELETE' }),
  
  // 切换任务状�?
  toggle: (id: number, is_enabled: boolean) =>
    request(`/scheduled-tasks/${id}/toggle`, {
      method: 'PUT',
      body: JSON.stringify({ is_enabled }),
    }),
  
  // 立即执行任务
  execute: (id: number) =>
    request(`/scheduled-tasks/${id}/execute`, { method: 'POST' }),
};

// ==================== 任务执行接口 ====================

export interface TaskLog {
  id: number;
  task_name: string;
  script_id: number;
  device_id: number;
  scheduled_task_id?: number;
  status: 'running' | 'success' | 'failed';
  start_time: string;
  end_time?: string;
  duration?: number;
  log_content?: string;
  error_message?: string;
  screenshot_paths?: string;
  created_at: string;
}

export const taskApi = {
  // 执行脚本
  execute: (data: { task_name: string; script_id: number; device_id: number }) =>
    request('/tasks/execute', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 获取任务日志
  getLogs: (taskLogId: number) => request<TaskLog>(`/tasks/${taskLogId}/logs`),
  
  // 停止任务
  stop: (taskLogId: number) => request(`/tasks/${taskLogId}/stop`, { method: 'POST' }),
};

// ==================== 报告中心接口 ====================

export const reportApi = {
  // 获取报告列表
  getList: (params?: {
    status?: string;
    device_id?: number;
    script_id?: number;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }) => request<PaginatedResponse<TaskLog>>(`/reports?${new URLSearchParams(params as any)}`),
  
  // 获取报告详情
  getDetail: (id: number) => request<TaskLog>(`/reports/${id}`),
  
  // 删除报告
  delete: (id: number) => request(`/reports/${id}`, { method: 'DELETE' }),
};

// ==================== 系统设置接口 ====================

export interface SystemSettings {
  adb_path: string;
  python_path: string;
  auto_connect: string;
  auto_refresh: string;
  refresh_interval: string;
  log_level: string;
  max_log_lines: string;
  screenshot_quality: string;
  screenshot_format: string;
  enable_notification: string;
  enable_sound: string;
}

export const settingsApi = {
  // 获取所有配�?
  getAll: () => request<SystemSettings>('/settings'),
  
  // 批量更新配置
  updateAll: (data: Partial<SystemSettings>) =>
    request('/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  // 获取单个配置
  get: (key: string) => request(`/settings/${key}`),
  
  // 更新单个配置
  update: (key: string, value: string) =>
    request(`/settings/${key}`, {
      method: 'PUT',
      body: JSON.stringify({ config_value: value }),
    }),
  
  // 扫描ADB路径
  scanAdbPaths: () => request<Array<{ label: string; path: string }>>('/settings/scan/adb-paths'),
  
  // 扫描Python路径
  scanPythonPaths: () => request<Array<{ label: string; path: string }>>('/settings/scan/python-paths'),
};

// ==================== 活动日志接口 ====================

export interface ActivityLog {
  id: number;
  activity_type: string;
  description: string;
  user_name: string;
  related_id?: number;
  related_type?: string;
  status: string;
  created_at: string;
}

export const activityLogApi = {
  // 获取活动日志列表
  getList: (params?: { activity_type?: string; status?: string; limit?: number }) =>
    request<ActivityLog[]>(`/activity-logs?${new URLSearchParams(params as any)}`),
};

// ==================== 文件上传接口 ====================

export const uploadApi = {
  // 上传脚本文件
  uploadScript: async (file: File, scriptType: 'python' | 'batch') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('script_type', scriptType);

    const response = await fetch(`${API_BASE_URL}/upload/script`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    const result: ApiResponse = await response.json();
    return result.data;
  },

  // 上传截图文件
  uploadScreenshot: async (file: File, taskLogId: number) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('task_log_id', taskLogId.toString());

    const response = await fetch(`${API_BASE_URL}/upload/screenshot`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    const result: ApiResponse = await response.json();
    return result.data;
  },
};

// ==================== �豸�����Ƚӿ� ====================


export const deviceHealthApi = {
  getHealth: (deviceId: number) =>
    request<DeviceHealthRecord>(`/device-health/devices/${deviceId}/health`),
  getHistory: (deviceId: number, hours: number = 24) =>
    request<{ device_id: number; records: any[] }>(`/device-health/devices/${deviceId}/history?hours=${hours}`),
  getStats: (deviceId: number) =>
    request<{
      device_id: number;
      total_executions: number;
      success_executions: number;
      failed_executions: number;
      success_rate: number;
      avg_duration: number;
      last_execution_time?: string;
    }>(`/device-health/devices/${deviceId}/stats`),
  getAlerts: (params?: { device_id?: number; is_resolved?: boolean; severity?: string }) =>
    request<DeviceAlert[]>(`/device-health/alerts?${new URLSearchParams(params as any)}`),
  resolveAlert: (alertId: number) =>
    request(`/device-health/alerts/${alertId}/resolve`, { method: 'POST' }),
  getAlertRules: () => request<AlertRule[]>('/device-health/alert-rules'),
  createAlertRule: (data: Omit<AlertRule, 'id'>) =>
    request<AlertRule>('/device-health/alert-rules', { method: 'POST', body: JSON.stringify(data) }),
  updateAlertRule: (id: number, data: Partial<AlertRule>) =>
    request<AlertRule>(`/device-health/alert-rules/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteAlertRule: (id: number) =>
    request(`/device-health/alert-rules/${id}`, { method: 'DELETE' }),
  toggleAlertRule: (id: number, is_enabled: boolean) =>
    request(`/device-health/alert-rules/${id}/toggle`, { method: 'PUT', body: JSON.stringify({ is_enabled }) }),
  getOverview: () =>
    request<{ devices: DeviceHealthRecord[]; unresolved_alerts: number }>('/device-health/overview'),
};

export interface FailureAnalysis {
  id: number;
  task_log_id: number;
  failure_type: string;
  failure_icon: string;
  severity: string;
  failed_step_index: number;
  failed_step_name: string;
  error_message: string;
  suggestions: string[];
  confidence: number;
  screenshot_path: string | null;
  created_at: string;
}

export interface FailureOverview {
  total_failures: number;
  failure_by_type: Record<string, number>;
  most_common_failure: string | null;
  recent_failures: Array<{
    id: number;
    task_log_id: number;
    failure_type: string;
    failure_icon: string;
    error_message: string;
    created_at: string;
  }>;
}

export const failureAnalysisApi = {
  analyzeTask: (taskLogId: number) =>
    request<FailureAnalysis>(`/failure-analysis/tasks/${taskLogId}/analyze`, { method: 'POST' }),
  getTaskAnalysis: (taskLogId: number) =>
    request<FailureAnalysis>(`/failure-analysis/tasks/${taskLogId}`),
  getScriptStats: (scriptId: number) =>
    request<{
      script_id: number;
      total_failures: number;
      failure_by_type: Record<string, number>;
      most_common_failure: string | null;
      failure_rate: number;
      last_failure_time?: string;
    }>(`/failure-analysis/scripts/${scriptId}/stats`),
  getTrend: (params?: { script_id?: number; range?: string }) =>
    request<{
      range: string;
      total_failures: number;
      failure_by_type: Record<string, number>;
      start_date: string;
      end_date: string;
    }>(`/failure-analysis/trend?${new URLSearchParams(params as any)}`),
  getStepLogs: (taskLogId: number) =>
    request<Array<{
      step_index: number;
      step_name: string;
      step_type: string;
      status: string;
      duration: number;
      error_message?: string;
      start_time?: string;
      end_time?: string;
    }>>(`/failure-analysis/tasks/${taskLogId}/steps`),
  getOverview: (days: number = 7) =>
    request<FailureOverview>(`/failure-analysis/overview?days=${days}`),
};

export interface Example {
  id: number;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  script_type: string;
  code: string;
  tags: string;
  is_featured: boolean;
  view_count: number;
  download_count: number;
  created_at: string;
  updated_at: string;
}

export interface BestPractice {
  id: number;
  title: string;
  content: string;
  category: string;
  difficulty: string;
  tags: string;
  like_count: number;
  view_count: number;
  created_at: string;
  updated_at: string;
}

export interface Snippet {
  id: number;
  title: string;
  description: string;
  category: string;
  language: string;
  code: string;
  tags: string;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export const exampleApi = {
  getList: (params?: {
    page?: number;
    page_size?: number;
    category?: string;
    difficulty?: string;
    script_type?: string;
    keyword?: string;
    is_featured?: boolean;
  }) => request<PaginatedResponse<Example>>(`/examples?${new URLSearchParams(params as any)}`),
  getCategories: () => request<Array<{ name: string; count: number }>>('/examples/categories'),
  getDetail: (id: number) => request<Example>(`/examples/${id}`),
  create: (data: Partial<Example>) =>
    request<Example>('/examples', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: Partial<Example>) =>
    request<Example>(`/examples/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: number) => request(`/examples/${id}`, { method: 'DELETE' }),
  download: (id: number) => request<Example>(`/examples/${id}/download`, { method: 'POST' }),
  getBestPractices: (params?: {
    page?: number;
    page_size?: number;
    category?: string;
    difficulty?: string;
    keyword?: string;
  }) =>
    request<PaginatedResponse<BestPractice>>(`/examples/practices/list?${new URLSearchParams(params as any)}`),
  getBestPracticeDetail: (id: number) => request<BestPractice>(`/examples/practices/${id}`),
  createBestPractice: (data: Partial<BestPractice>) =>
    request<BestPractice>('/examples/practices', { method: 'POST', body: JSON.stringify(data) }),
  likeBestPractice: (id: number) =>
    request<BestPractice>(`/examples/practices/${id}/like`, { method: 'POST' }),
  getSnippets: (params?: {
    page?: number;
    page_size?: number;
    category?: string;
    language?: string;
    keyword?: string;
  }) =>
    request<PaginatedResponse<Snippet>>(`/examples/snippets/list?${new URLSearchParams(params as any)}`),
  getSnippetDetail: (id: number) => request<Snippet>(`/examples/snippets/${id}`),
  createSnippet: (data: Partial<Snippet>) =>
    request<Snippet>('/examples/snippets', { method: 'POST', body: JSON.stringify(data) }),
  useSnippet: (id: number) => request<Snippet>(`/examples/snippets/${id}/use`, { method: 'POST' }),
};

