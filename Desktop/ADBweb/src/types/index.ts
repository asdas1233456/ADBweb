export interface Device {
  id: string
  serialNumber: string
  model: string
  androidVersion: string
  resolution: string
  battery: number
  status: 'online' | 'offline' | 'busy'
  group_name?: string
  cpu_usage?: number
  memory_usage?: number
  last_connected_at?: string
}

export interface DevicePerformance {
  device_id: string
  cpu_usage: number
  memory_usage: number
  battery: number
  temperature: number
  timestamp: string
}

export interface ScriptStep {
  id: string
  type: 'click' | 'swipe' | 'input' | 'wait' | 'screenshot' | 'assert'
  name: string
  config: Record<string, any>
}

export type ScriptType = 'visual' | 'python' | 'batch'
export type ScriptCategory = 'login' | 'test' | 'automation' | 'other'

export interface Script {
  id: string
  name: string
  type: ScriptType
  category: ScriptCategory
  description?: string
  filePath?: string
  fileContent?: string
  steps: ScriptStep[]
  createdAt: string
  updatedAt: string
}

export interface ScheduledTask {
  id: string
  name: string
  script_id: string
  device_id: string
  frequency: string
  schedule_time: string
  schedule_day?: string
  cron_expression?: string
  priority: number
  max_retry: number
  retry_count: number
  depends_on?: string
  is_enabled: boolean
  last_run_at?: string
  next_run_at?: string
  run_count: number
  success_count: number
  fail_count: number
}

export interface LogEntry {
  id: string
  timestamp: string
  level: 'info' | 'success' | 'warning' | 'error'
  message: string
}

export interface Report {
  id: string
  taskName: string
  deviceId: string
  scriptId: string
  status: 'success' | 'failed'
  startTime: string
  duration: number
}
