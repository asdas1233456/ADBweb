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

// ==================== 文件上传接口 ====================

export const uploadApi = {
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
