

/**
 * API 鏈嶅姟灞?- 缁熶竴绠＄悊鍚庣鎺ュ彛璋冪敤
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

// 缁熶竴鍝嶅簲鏍煎紡
interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

// 鍒嗛〉鍝嶅簲鏍煎紡
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// 閫氱敤璇锋眰鏂规硶
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
      throw new Error(result.message || '璇锋眰澶辫触');
    }

    return result.data;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// ==================== 浠〃鐩樻帴鍙?====================

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
  // 鑾峰彇浠〃鐩樻瑙堟暟鎹?
  getOverview: () => request<DashboardData>('/dashboard/overview'),
};

// ==================== 璁惧绠＄悊鎺ュ彛 ====================

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
  // 鑾峰彇璁惧鍒楄〃
  getList: (params?: { status?: string; page?: number; page_size?: number }) =>
    request<PaginatedResponse<Device>>(`/devices?${new URLSearchParams(params as any)}`),
  
  // 鑾峰彇璁惧璇︽儏
  getDetail: (id: number) => request<Device>(`/devices/${id}`),
  
  // 鍒锋柊璁惧鍒楄〃
  refresh: () => request('/devices/refresh', { method: 'POST' }),
  
  // 鏂紑璁惧杩炴帴
  disconnect: (id: number) => request(`/devices/${id}/disconnect`, { method: 'POST' }),
  
  // 鑾峰彇璁惧鍒嗙粍鍒楄〃
  getGroups: () => request<string[]>('/devices/groups/list'),
  
  // 鏇存柊璁惧鍒嗙粍
  updateGroup: (id: number, group_name?: string) =>
    request<Device>(`/devices/${id}/group`, {
      method: 'PUT',
      body: JSON.stringify({ group_name }),
    }),
  
  // 鑾峰彇璁惧鎴浘
  getScreenshot: (id: number) =>
    request<{ device_id: number; screenshot_url: string; timestamp: string }>(
      `/devices/${id}/screenshot`
    ),
  
  // 鑾峰彇璁惧鎬ц兘鏁版嵁
  getPerformance: (id: number) =>
    request<{
      device_id: number;
      cpu_usage: number;
      memory_usage: number;
      battery: number;
      temperature: number;
      timestamp: string;
    }>(`/devices/${id}/performance`),
  
  // 鎵归噺鎵ц鑴氭湰
  batchExecute: (device_ids: number[], script_id: number) =>
    request('/devices/batch/execute', {
      method: 'POST',
      body: JSON.stringify({ device_ids, script_id }),
    }),
};

// ==================== 鑴氭湰绠＄悊鎺ュ彛 ====================

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
  // 鑾峰彇鑴氭湰鍒楄〃
  getList: (params?: {
    type?: string;
    category?: string;
    keyword?: string;
    page?: number;
    page_size?: number;
  }) => request<PaginatedResponse<Script>>(`/scripts?${new URLSearchParams(params as any)}`),
  
  // 鑾峰彇鑴氭湰璇︽儏
  getDetail: (id: number) => request<Script>(`/scripts/${id}`),
  
  // 鍒涘缓鑴氭湰
  create: (data: Partial<Script>) =>
    request<Script>('/scripts', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 鏇存柊鑴氭湰
  update: (id: number, data: Partial<Script>) =>
    request<Script>(`/scripts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  // 鍒犻櫎鑴氭湰
  delete: (id: number) => request(`/scripts/${id}`, { method: 'DELETE' }),
  
  // 楠岃瘉鑴氭湰
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

// ==================== 妯℃澘甯傚満鎺ュ彛 ====================

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
  // 鑾峰彇妯℃澘鍒楄〃
  getList: (params?: {
    category?: string;
    type?: string;
    keyword?: string;
    sort_by?: string;
    page?: number;
    page_size?: number;
  }) => request<PaginatedResponse<Template>>(`/templates?${new URLSearchParams(params as any)}`),
  
  // 鑾峰彇妯℃澘璇︽儏
  getDetail: (id: number) => request<Template>(`/templates/${id}`),
  
  // 涓嬭浇妯℃澘锛堣浆涓鸿剼鏈級
  download: (id: number, data: { script_name: string; category: string }) =>
    request(`/templates/${id}/download`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// ==================== 瀹氭椂浠诲姟鎺ュ彛 ====================

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
  // 鑾峰彇瀹氭椂浠诲姟鍒楄〃
  getList: (params?: { is_enabled?: boolean; page?: number; page_size?: number }) =>
    request<PaginatedResponse<ScheduledTask>>(
      `/scheduled-tasks?${new URLSearchParams(params as any)}`
    ),
  
  // 鑾峰彇瀹氭椂浠诲姟璇︽儏
  getDetail: (id: number) => request<ScheduledTask>(`/scheduled-tasks/${id}`),
  
  // 鍒涘缓瀹氭椂浠诲姟
  create: (data: Partial<ScheduledTask>) =>
    request<ScheduledTask>('/scheduled-tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 鏇存柊瀹氭椂浠诲姟
  update: (id: number, data: Partial<ScheduledTask>) =>
    request<ScheduledTask>(`/scheduled-tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  // 鍒犻櫎瀹氭椂浠诲姟
  delete: (id: number) => request(`/scheduled-tasks/${id}`, { method: 'DELETE' }),
  
  // 鍒囨崲浠诲姟鐘舵€?
  toggle: (id: number, is_enabled: boolean) =>
    request(`/scheduled-tasks/${id}/toggle`, {
      method: 'PUT',
      body: JSON.stringify({ is_enabled }),
    }),
  
  // 绔嬪嵆鎵ц浠诲姟
  execute: (id: number) =>
    request(`/scheduled-tasks/${id}/execute`, { method: 'POST' }),
};

// ==================== 浠诲姟鎵ц鎺ュ彛 ====================

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
  // 鎵ц鑴氭湰
  execute: (data: { task_name: string; script_id: number; device_id: number }) =>
    request('/tasks/execute', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 鑾峰彇浠诲姟鏃ュ織
  getLogs: (taskLogId: number) => request<TaskLog>(`/tasks/${taskLogId}/logs`),
  
  // 鍋滄浠诲姟
  stop: (taskLogId: number) => request(`/tasks/${taskLogId}/stop`, { method: 'POST' }),
};

// ==================== 鎶ュ憡涓績鎺ュ彛 ====================

export const reportApi = {
  // 鑾峰彇鎶ュ憡鍒楄〃
  getList: (params?: {
    status?: string;
    device_id?: number;
    script_id?: number;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }) => request<PaginatedResponse<TaskLog>>(`/reports?${new URLSearchParams(params as any)}`),
  
  // 鑾峰彇鎶ュ憡璇︽儏
  getDetail: (id: number) => request<TaskLog>(`/reports/${id}`),
  
  // 鍒犻櫎鎶ュ憡
  delete: (id: number) => request(`/reports/${id}`, { method: 'DELETE' }),
  
  // 批量删除报告
  batchDelete: (params: {
    status?: string;
    start_date?: string;
    end_date?: string;
  }) => request(`/reports/batch-delete?${new URLSearchParams(params as any)}`, { method: 'DELETE' }),
};

// ==================== 绯荤粺璁剧疆鎺ュ彛 ====================

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
  // 鑾峰彇鎵€鏈夐厤缃?
  getAll: () => request<SystemSettings>('/settings'),
  
  // 鎵归噺鏇存柊閰嶇疆
  updateAll: (data: Partial<SystemSettings>) =>
    request('/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  // 鑾峰彇鍗曚釜閰嶇疆
  get: (key: string) => request(`/settings/${key}`),
  
  // 鏇存柊鍗曚釜閰嶇疆
  update: (key: string, value: string) =>
    request(`/settings/${key}`, {
      method: 'PUT',
      body: JSON.stringify({ config_value: value }),
    }),
  
  // 鎵弿ADB璺緞
  scanAdbPaths: () => request<Array<{ label: string; path: string }>>('/settings/scan/adb-paths'),
  
  // 鎵弿Python璺緞
  scanPythonPaths: () => request<Array<{ label: string; path: string }>>('/settings/scan/python-paths'),
};

// ==================== 娲诲姩鏃ュ織鎺ュ彛 ====================

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
  // 鑾峰彇娲诲姩鏃ュ織鍒楄〃
  getList: (params?: { activity_type?: string; status?: string; limit?: number }) =>
    request<ActivityLog[]>(`/activity-logs?${new URLSearchParams(params as any)}`),
};

// ==================== 鏂囦欢涓婁紶鎺ュ彛 ====================

export const uploadApi = {
  // 涓婁紶鑴氭湰鏂囦欢
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

  // 涓婁紶鎴浘鏂囦欢
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

// ==================== 设备健康度接口 ====================

export interface DeviceHealthRecord {
  device_id: number;
  device_name: string;
  health_score: number;
  level_code: string;
  level_name: string;
  level_color: string;
  battery_level: number;
  temperature: number;
  cpu_usage: number;
  memory_usage: number;
  storage_usage: number;
  network_status: string;
  last_check_time: string;
}

export interface DeviceAlert {
  id: number;
  device_id: number;
  alert_type: string;
  severity: string;
  message: string;
  is_resolved: boolean;
  created_at: string;
  resolved_at?: string;
}

export interface AlertRule {
  id: number;
  rule_name: string;
  rule_type: string;
  condition_field: string;
  operator: string;
  threshold_value: number;
  severity: string;
  is_enabled: boolean;
}

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
  triggerCollection: () =>
    request('/device-health/collect', { method: 'POST' }),
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



// ==================== 脚本模板接口 ====================

export interface ScriptTemplate {
  id: number;
  name: string;
  category: string;
  description?: string;
  language: string;
  template_content: string;
  variables?: Record<string, {
    type: string;
    description: string;
    required: boolean;
    default: string;
  }>;
  tags?: string[];
  usage_count: number;
  is_builtin: boolean;
  created_by: string;
  created_at: string;
}

export interface TemplateUseRequest {
  template_id: number;
  variables?: Record<string, string>;
}

export const scriptTemplateApi = {
  getList: (params?: {
    category?: string;
    language?: string;
    keyword?: string;
    limit?: number;
  }) => request<ScriptTemplate[]>(`/script-templates?${new URLSearchParams(params as any)}`),
  
  getCategories: () => request<Array<{ name: string; count: number }>>('/script-templates/categories'),
  
  getDetail: (id: number) => request<ScriptTemplate>(`/script-templates/${id}`),
  
  use: (data: TemplateUseRequest) =>
    request<{ content: string }>('/script-templates/use', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  create: (data: {
    name: string;
    category: string;
    description?: string;
    language: string;
    template_content: string;
    variables?: Record<string, any>;
    tags?: string[];
  }) =>
    request<ScriptTemplate>('/script-templates', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  delete: (id: number) =>
    request<{ id: number }>(`/script-templates/${id}`, {
      method: 'DELETE',
    }),
};

// ==================== AI脚本生成接口 ====================

export interface ScriptGenerateRequest {
  prompt: string;
  language: 'adb' | 'python';
  device_model?: string;
  ai_api_key?: string;
  ai_api_base?: string;
}

export interface OptimizationSuggestion {
  type: 'error' | 'warning' | 'info';
  title: string;
  description: string;
  suggestion: string;
  line: number | null;
}

export interface AIScriptResponse {
  id: number;
  prompt: string;
  generated_script: string;
  language: string;
  optimization_suggestions: OptimizationSuggestion[];
  device_model?: string;
  generation_mode?: string;
  ai_model?: string;
}

export interface PromptOptimizeRequest {
  prompt: string;
  language: 'adb' | 'python';
  ai_api_key?: string;
  ai_api_base?: string;
}

export interface PromptOptimizeResponse {
  original_prompt: string;
  optimized_prompt: string;
  improvements: string[];
  missing_info: string[];
}

export interface ScriptSaveRequest {
  ai_script_id: number;
  name: string;
  category: string;
  description?: string;
}

export interface ScriptValidationResult {
  passed: boolean;
  score: number;
  items: Array<{
    name: string;
    level: 'success' | 'warning' | 'error';
    message: string;
    details: string;
  }>;
  suggestions: string[];
}

export interface BatchGenerateRequest {
  prompts: string[];
  language: 'adb' | 'python';
  generate_suite: boolean;
  ai_api_key?: string;
  ai_api_base?: string;
}

export interface WorkflowGenerateRequest {
  workflow_steps: string[];
  language: 'adb' | 'python';
  ai_api_key?: string;
  ai_api_base?: string;
}

export interface BatchGenerateResult {
  results: Array<{
    index: number;
    id: number;
    prompt: string;
    script: string;
    suggestions: OptimizationSuggestion[];
    status: 'success' | 'failed';
    error?: string;
  }>;
  suite_script: string;
  statistics: {
    total: number;
    success: number;
    failed: number;
    success_rate: number;
  };
}

export interface WorkflowGenerateResult {
  individual_scripts: Array<{
    step: number;
    description: string;
    script: string;
    suggestions: OptimizationSuggestion[];
    error?: string;
  }>;
  combined_script: string;
  workflow_steps: string[];
}

export const aiScriptApi = {
  generate: (data: ScriptGenerateRequest) =>
    request<AIScriptResponse>('/ai-script/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  batchGenerate: (data: BatchGenerateRequest) =>
    request<BatchGenerateResult>('/ai-script/batch-generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  generateWorkflow: (data: WorkflowGenerateRequest) =>
    request<WorkflowGenerateResult>('/ai-script/workflow-generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  optimizePrompt: (data: PromptOptimizeRequest) =>
    request<PromptOptimizeResponse>('/ai-script/optimize-prompt', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  saveToScripts: (data: ScriptSaveRequest) =>
    request<{ script_id: number; name: string; type: string; category: string }>('/ai-script/save-to-scripts', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  validateGenerated: (aiScriptId: number) =>
    request<ScriptValidationResult>(`/ai-script/validate-generated?ai_script_id=${aiScriptId}`, {
      method: 'POST',
    }),
  getHistory: (limit: number = 10) =>
    request<AIScriptResponse[]>(`/ai-script/history?limit=${limit}`),
  delete: (id: number) =>
    request<{ message: string }>(`/ai-script/${id}`, {
      method: 'DELETE',
    }),
};

// ==================== 测试用例推荐接口 ====================

export interface TestCaseResponse {
  id: number;
  name: string;
  description?: string;
  device_model: string;
  priority: number;
  failure_count: number;
  success_count: number;
  script_template?: string;
  tags?: string;
  failure_rate: number;
}

export interface RecommendResponse {
  recommendations: TestCaseResponse[];
  statistics: {
    total_cases: number;
    total_failures: number;
    total_successes: number;
    avg_failure_rate: number;
  };
}

export const testCaseApi = {
  recommend: (deviceModel: string, limit: number = 3) =>
    request<RecommendResponse>(
      `/test-case/recommend?device_model=${encodeURIComponent(deviceModel)}&limit=${limit}`
    ),
  list: (deviceModel?: string, limit: number = 20) => {
    const params = new URLSearchParams();
    if (deviceModel) params.append('device_model', deviceModel);
    params.append('limit', limit.toString());
    return request<TestCaseResponse[]>(`/test-case/list?${params.toString()}`);
  },
  create: (data: Partial<TestCaseResponse>) =>
    request<TestCaseResponse>('/test-case/create', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  getDeviceModels: () => request<string[]>('/test-case/devices'),
};
