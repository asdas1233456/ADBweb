# 手机自动化测试平台 - API 接口文档

## 项目信息

- **项目名称**: 手机自动化测试平台
- **后端框架**: FastAPI
- **数据库**: SQLite + SQLModel
- **API 版本**: v1.0
- **Base URL**: `http://localhost:8000/api/v1`
- **文档日期**: 2026-02-16

---

## 目录

1. [通用说明](#通用说明)
2. [仪表盘接口](#仪表盘接口)
3. [设备管理接口](#设备管理接口)
4. [脚本管理接口](#脚本管理接口)
5. [模板市场接口](#模板市场接口)
6. [定时任务接口](#定时任务接口)
7. [任务执行接口](#任务执行接口)
8. [报告中心接口](#报告中心接口)
9. [系统设置接口](#系统设置接口)
10. [活动日志接口](#活动日志接口)
11. [文件上传接口](#文件上传接口)

---

## 通用说明

### 响应格式

所有接口统一返回格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 分页参数

```json
{
  "page": 1,
  "page_size": 10
}
```

### 分页响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "total_pages": 10
  }
}
```

---

## 仪表盘接口

### 1. 获取仪表盘数据（聚合接口）

**接口说明**: 一次性返回仪表盘所需的所有数据，包括统计卡片、设备状态、执行统计、最近活动。

**请求方式**: `GET`

**接口路径**: `/dashboard/overview`

**请求参数**: 无

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "statistics": {
      "online_devices": 3,
      "total_devices": 4,
      "total_scripts": 12,
      "today_executions": 28,
      "success_rate": 92.5
    },
    "device_status": [
      {
        "id": 1,
        "model": "Xiaomi 12 Pro",
        "battery": 85,
        "status": "online"
      },
      {
        "id": 2,
        "model": "Samsung Galaxy S23",
        "battery": 62,
        "status": "online"
      }
    ],
    "execution_stats": {
      "success_count": 156,
      "failed_count": 15,
      "running_count": 29,
      "total_count": 200,
      "success_percentage": 78.0,
      "failed_percentage": 7.5,
      "running_percentage": 14.5
    },
    "recent_activities": [
      {
        "id": 1,
        "activity_type": "script_execute",
        "description": "登录测试脚本在 Xiaomi 12 Pro 上执行成功",
        "user_name": "系统",
        "status": "success",
        "created_at": "2024-01-15 14:30:00"
      }
    ]
  }
}
```

---

## 设备管理接口

### 2. 获取设备列表

**请求方式**: `GET`

**接口路径**: `/devices`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | 否 | 设备状态筛选 (online/offline/busy) |
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认10 |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "serial_number": "ABC123456789",
        "model": "Xiaomi 12 Pro",
        "android_version": "13",
        "resolution": "1440x3200",
        "battery": 85,
        "status": "online",
        "last_connected_at": "2024-01-15 14:30:00",
        "created_at": "2024-01-10 10:00:00",
        "updated_at": "2024-01-15 14:30:00"
      }
    ],
    "total": 4,
    "page": 1,
    "page_size": 10
  }
}
```

### 3. 获取设备详情

**请求方式**: `GET`

**接口路径**: `/devices/{device_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| device_id | int | 是 | 设备ID |

**响应示例**: 同设备列表单项

### 4. 刷新设备列表

**请求方式**: `POST`

**接口路径**: `/devices/refresh`

**请求参数**: 无

**响应示例**:

```json
{
  "code": 200,
  "message": "设备列表已刷新",
  "data": {
    "new_devices": 1,
    "updated_devices": 2
  }
}
```

### 5. 断开设备连接

**请求方式**: `POST`

**接口路径**: `/devices/{device_id}/disconnect`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| device_id | int | 是 | 设备ID |

**响应示例**:

```json
{
  "code": 200,
  "message": "设备已断开连接",
  "data": null
}
```

---

## 脚本管理接口

### 6. 获取脚本列表

**请求方式**: `GET`

**接口路径**: `/scripts`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| type | string | 否 | 脚本类型 (visual/python/batch) |
| category | string | 否 | 脚本分类 (login/test/automation/other) |
| keyword | string | 否 | 搜索关键词 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "登录测试",
        "type": "visual",
        "category": "login",
        "description": "自动化登录测试脚本",
        "file_path": null,
        "file_content": null,
        "steps_json": "[{\"id\":\"s1\",\"type\":\"click\",\"name\":\"点击登录\",\"config\":{\"x\":100,\"y\":200}}]",
        "is_active": true,
        "created_at": "2024-01-15 10:30:00",
        "updated_at": "2024-01-15 14:20:00"
      }
    ],
    "total": 12,
    "page": 1,
    "page_size": 10
  }
}
```

### 7. 创建脚本

**请求方式**: `POST`

**接口路径**: `/scripts`

**请求体**:

```json
{
  "name": "登录测试",
  "type": "visual",
  "category": "login",
  "description": "自动化登录测试脚本",
  "file_path": null,
  "file_content": null,
  "steps_json": "[{\"id\":\"s1\",\"type\":\"click\"}]"
}
```

**响应示例**:

```json
{
  "code": 200,
  "message": "脚本创建成功",
  "data": {
    "id": 1,
    "name": "登录测试",
    "type": "visual",
    "category": "login"
  }
}
```

### 8. 更新脚本

**请求方式**: `PUT`

**接口路径**: `/scripts/{script_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| script_id | int | 是 | 脚本ID |

**请求体**: 同创建脚本

**响应示例**: 同创建脚本

### 9. 删除脚本

**请求方式**: `DELETE`

**接口路径**: `/scripts/{script_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| script_id | int | 是 | 脚本ID |

**响应示例**:

```json
{
  "code": 200,
  "message": "脚本删除成功",
  "data": null
}
```

### 10. 获取脚本详情

**请求方式**: `GET`

**接口路径**: `/scripts/{script_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| script_id | int | 是 | 脚本ID |

**响应示例**: 同脚本列表单项

---

## 模板市场接口

### 11. 获取模板列表

**请求方式**: `GET`

**接口路径**: `/templates`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| category | string | 否 | 模板分类 |
| type | string | 否 | 模板类型 (visual/python/batch) |
| keyword | string | 否 | 搜索关键词 |
| sort_by | string | 否 | 排序字段 (downloads/rating) |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "APP启动性能测试",
        "description": "自动测试APP启动时间、内存占用、CPU使用率等性能指标",
        "author": "测试专家",
        "category": "性能测试",
        "type": "python",
        "tags": "性能,启动,监控",
        "content": "import time\\nimport subprocess",
        "preview": "import time\\nimport subprocess",
        "downloads": 1250,
        "rating": 4.8,
        "is_featured": true,
        "created_at": "2024-01-10 10:00:00",
        "updated_at": "2024-01-15 14:00:00"
      }
    ],
    "total": 6,
    "page": 1,
    "page_size": 10
  }
}
```

### 12. 获取模板详情

**请求方式**: `GET`

**接口路径**: `/templates/{template_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| template_id | int | 是 | 模板ID |

**响应示例**: 同模板列表单项

### 13. 下载模板（转为脚本）

**请求方式**: `POST`

**接口路径**: `/templates/{template_id}/download`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| template_id | int | 是 | 模板ID |

**请求体**:

```json
{
  "script_name": "我的登录测试",
  "category": "login"
}
```

**响应示例**:

```json
{
  "code": 200,
  "message": "模板下载成功，已添加到脚本列表",
  "data": {
    "script_id": 10,
    "script_name": "我的登录测试"
  }
}
```

---

## 定时任务接口

### 14. 获取定时任务列表

**请求方式**: `GET`

**接口路径**: `/scheduled-tasks`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| is_enabled | boolean | 否 | 是否启用 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "每日登录测试",
        "script_id": 1,
        "script_name": "登录测试",
        "device_id": 1,
        "device_name": "Xiaomi 12 Pro",
        "frequency": "daily",
        "schedule_time": "09:00:00",
        "schedule_day": null,
        "is_enabled": true,
        "last_run_at": "2024-01-15 09:00:00",
        "next_run_at": "2024-01-16 09:00:00",
        "run_count": 30,
        "success_count": 28,
        "fail_count": 2,
        "created_at": "2024-01-01 10:00:00",
        "updated_at": "2024-01-15 09:00:00"
      }
    ],
    "total": 2,
    "page": 1,
    "page_size": 10
  }
}
```

### 15. 创建定时任务

**请求方式**: `POST`

**接口路径**: `/scheduled-tasks`

**请求体**:

```json
{
  "name": "每日登录测试",
  "script_id": 1,
  "device_id": 1,
  "frequency": "daily",
  "schedule_time": "09:00:00",
  "schedule_day": null
}
```

**字段说明**:
- `frequency`: 执行频率 (daily/weekly/monthly)
- `schedule_time`: 执行时间 (HH:MM:SS)
- `schedule_day`: 执行日期（weekly时为星期几，如Monday；monthly时为几号，如15）

**响应示例**:

```json
{
  "code": 200,
  "message": "定时任务创建成功",
  "data": {
    "id": 1,
    "name": "每日登录测试",
    "next_run_at": "2024-01-16 09:00:00"
  }
}
```

### 16. 更新定时任务

**请求方式**: `PUT`

**接口路径**: `/scheduled-tasks/{task_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | int | 是 | 任务ID |

**请求体**: 同创建定时任务

**响应示例**: 同创建定时任务

### 17. 删除定时任务

**请求方式**: `DELETE`

**接口路径**: `/scheduled-tasks/{task_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | int | 是 | 任务ID |

**响应示例**:

```json
{
  "code": 200,
  "message": "定时任务删除成功",
  "data": null
}
```

### 18. 切换定时任务状态（启用/禁用）

**请求方式**: `PUT`

**接口路径**: `/scheduled-tasks/{task_id}/toggle`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | int | 是 | 任务ID |

**请求体**:

```json
{
  "is_enabled": false
}
```

**响应示例**:

```json
{
  "code": 200,
  "message": "任务状态已更新",
  "data": {
    "id": 1,
    "is_enabled": false
  }
}
```

### 19. 立即执行定时任务

**请求方式**: `POST`

**接口路径**: `/scheduled-tasks/{task_id}/execute`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | int | 是 | 任务ID |

**请求参数**: 无

**响应示例**:

```json
{
  "code": 200,
  "message": "任务已开始执行",
  "data": {
    "task_log_id": 100,
    "status": "running"
  }
}
```

---

## 任务执行接口

### 20. 执行脚本

**请求方式**: `POST`

**接口路径**: `/tasks/execute`

**请求体**:

```json
{
  "task_name": "手动执行登录测试",
  "script_id": 1,
  "device_id": 1
}
```

**响应示例**:

```json
{
  "code": 200,
  "message": "任务已开始执行",
  "data": {
    "task_log_id": 100,
    "status": "running"
  }
}
```

### 21. 获取任务执行日志

**请求方式**: `GET`

**接口路径**: `/tasks/{task_log_id}/logs`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_log_id | int | 是 | 任务日志ID |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 100,
    "task_name": "手动执行登录测试",
    "script_id": 1,
    "device_id": 1,
    "status": "success",
    "start_time": "2024-01-15 14:30:00",
    "end_time": "2024-01-15 14:30:05",
    "duration": 5.2,
    "log_content": "[14:30:00] INFO 开始执行脚本\\n[14:30:01] SUCCESS 步骤1: 点击登录按钮 - 成功",
    "error_message": null,
    "screenshot_paths": "[\"screenshots/001.png\",\"screenshots/002.png\"]"
  }
}
```

### 22. 停止任务执行

**请求方式**: `POST`

**接口路径**: `/tasks/{task_log_id}/stop`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_log_id | int | 是 | 任务日志ID |

**响应示例**:

```json
{
  "code": 200,
  "message": "任务已停止",
  "data": null
}
```

---

## 报告中心接口

### 23. 获取报告列表

**请求方式**: `GET`

**接口路径**: `/reports`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | 否 | 执行状态 (success/failed) |
| device_id | int | 否 | 设备ID |
| script_id | int | 否 | 脚本ID |
| start_date | string | 否 | 开始日期 (YYYY-MM-DD) |
| end_date | string | 否 | 结束日期 (YYYY-MM-DD) |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "task_name": "登录测试",
        "script_id": 1,
        "script_name": "登录测试",
        "device_id": 1,
        "device_name": "Xiaomi 12 Pro",
        "status": "success",
        "start_time": "2024-01-15 14:30:00",
        "end_time": "2024-01-15 14:30:05",
        "duration": 5.2,
        "created_at": "2024-01-15 14:30:00"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 10
  }
}
```

### 24. 获取报告详情

**请求方式**: `GET`

**接口路径**: `/reports/{report_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| report_id | int | 是 | 报告ID（即task_log_id） |

**响应示例**: 同任务执行日志详情

---

## 系统设置接口

### 25. 获取系统配置

**请求方式**: `GET`

**接口路径**: `/settings`

**请求参数**: 无

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "adb_path": "C:\\platform-tools\\adb.exe",
    "python_path": "C:\\Python39\\python.exe",
    "auto_connect": true,
    "auto_refresh": true,
    "refresh_interval": 5,
    "log_level": "info",
    "max_log_lines": 1000,
    "screenshot_quality": "high",
    "screenshot_format": "png",
    "enable_notification": true,
    "enable_sound": false
  }
}
```

### 26. 更新系统配置

**请求方式**: `PUT`

**接口路径**: `/settings`

**请求体**:

```json
{
  "adb_path": "C:\\platform-tools\\adb.exe",
  "python_path": "C:\\Python39\\python.exe",
  "auto_connect": true,
  "auto_refresh": true,
  "refresh_interval": 5,
  "log_level": "info",
  "max_log_lines": 1000,
  "screenshot_quality": "high",
  "screenshot_format": "png",
  "enable_notification": true,
  "enable_sound": false
}
```

**响应示例**:

```json
{
  "code": 200,
  "message": "配置已保存",
  "data": null
}
```

### 27. 获取单个配置项

**请求方式**: `GET`

**接口路径**: `/settings/{config_key}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| config_key | string | 是 | 配置键名 |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "config_key": "adb_path",
    "config_value": "C:\\platform-tools\\adb.exe",
    "config_type": "string"
  }
}
```

### 28. 更新单个配置项

**请求方式**: `PUT`

**接口路径**: `/settings/{config_key}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| config_key | string | 是 | 配置键名 |

**请求体**:

```json
{
  "config_value": "D:\\tools\\adb.exe"
}
```

**响应示例**:

```json
{
  "code": 200,
  "message": "配置已更新",
  "data": null
}
```

---

## 活动日志接口

### 29. 获取活动日志列表

**请求方式**: `GET`

**接口路径**: `/activity-logs`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| activity_type | string | 否 | 活动类型 |
| status | string | 否 | 活动状态 (success/failed) |
| limit | int | 否 | 返回数量，默认20 |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "activity_type": "script_execute",
      "description": "登录测试脚本在 Xiaomi 12 Pro 上执行成功",
      "user_name": "系统",
      "related_id": 1,
      "related_type": "script",
      "status": "success",
      "created_at": "2024-01-15 14:30:00"
    }
  ]
}
```

---

## 文件上传接口

### 30. 上传脚本文件

**请求方式**: `POST`

**接口路径**: `/upload/script`

**Content-Type**: `multipart/form-data`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | file | 是 | 脚本文件 (.py 或 .bat) |
| script_type | string | 是 | 脚本类型 (python/batch) |

**响应示例**:

```json
{
  "code": 200,
  "message": "文件上传成功",
  "data": {
    "file_path": "uploads/scripts/20240115_143000_test.py",
    "file_name": "test.py",
    "file_size": 1024,
    "file_content": "import subprocess\\n\\ndef test():\\n    pass"
  }
}
```

### 31. 上传截图文件

**请求方式**: `POST`

**接口路径**: `/upload/screenshot`

**Content-Type**: `multipart/form-data`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | file | 是 | 截图文件 (.png 或 .jpg) |
| task_log_id | int | 是 | 任务日志ID |

**响应示例**:

```json
{
  "code": 200,
  "message": "截图上传成功",
  "data": {
    "file_path": "uploads/screenshots/20240115_143000_001.png",
    "file_name": "001.png",
    "file_size": 2048
  }
}
```

---

## WebSocket 接口

### 32. 实时日志推送

**连接地址**: `ws://localhost:8000/ws/logs/{task_log_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_log_id | int | 是 | 任务日志ID |

**消息格式**:

```json
{
  "type": "log",
  "data": {
    "id": "log-1",
    "timestamp": "14:30:01",
    "level": "info",
    "message": "开始执行脚本..."
  }
}
```

**日志级别**:
- `info`: 信息
- `success`: 成功
- `warning`: 警告
- `error`: 错误

### 33. 设备状态推送

**连接地址**: `ws://localhost:8000/ws/devices`

**消息格式**:

```json
{
  "type": "device_status",
  "data": {
    "device_id": 1,
    "status": "online",
    "battery": 85
  }
}
```

---

## 错误码说明

### 业务错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 设备不存在 |
| 1002 | 设备离线 |
| 1003 | 设备正在使用中 |
| 2001 | 脚本不存在 |
| 2002 | 脚本类型不支持 |
| 2003 | 脚本内容格式错误 |
| 3001 | 模板不存在 |
| 4001 | 定时任务不存在 |
| 4002 | 定时任务已禁用 |
| 5001 | 任务执行失败 |
| 5002 | 任务不存在 |
| 6001 | 配置项不存在 |
| 7001 | 文件类型不支持 |
| 7002 | 文件大小超限 |

### 错误响应示例

```json
{
  "code": 1001,
  "message": "设备不存在",
  "data": null
}
```

---

## 数据模型定义

### Device (设备)

```typescript
interface Device {
  id: number
  serial_number: string
  model: string
  android_version: string
  resolution: string
  battery: number
  status: 'online' | 'offline' | 'busy'
  last_connected_at: string
  created_at: string
  updated_at: string
}
```

### Script (脚本)

```typescript
interface Script {
  id: number
  name: string
  type: 'visual' | 'python' | 'batch'
  category: 'login' | 'test' | 'automation' | 'other'
  description: string
  file_path: string | null
  file_content: string | null
  steps_json: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}
```

### Template (模板)

```typescript
interface Template {
  id: number
  name: string
  description: string
  author: string
  category: string
  type: 'visual' | 'python' | 'batch'
  tags: string
  content: string
  preview: string
  downloads: number
  rating: number
  is_featured: boolean
  created_at: string
  updated_at: string
}
```

### ScheduledTask (定时任务)

```typescript
interface ScheduledTask {
  id: number
  name: string
  script_id: number
  device_id: number
  frequency: 'daily' | 'weekly' | 'monthly'
  schedule_time: string
  schedule_day: string | null
  is_enabled: boolean
  last_run_at: string | null
  next_run_at: string
  run_count: number
  success_count: number
  fail_count: number
  created_at: string
  updated_at: string
}
```

### TaskLog (任务日志)

```typescript
interface TaskLog {
  id: number
  task_name: string
  script_id: number
  device_id: number
  scheduled_task_id: number | null
  status: 'running' | 'success' | 'failed'
  start_time: string
  end_time: string | null
  duration: number | null
  log_content: string | null
  error_message: string | null
  screenshot_paths: string | null
  created_at: string
}
```

---

## FastAPI 实现示例

### 路由定义

```python
from fastapi import APIRouter, Depends, UploadFile, File
from sqlmodel import Session

router = APIRouter(prefix="/api/v1", tags=["API"])

# 仪表盘
@router.get("/dashboard/overview")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    pass

# 设备管理
@router.get("/devices")
async def get_devices(db: Session = Depends(get_db)):
    pass

# 脚本管理
@router.post("/scripts")
async def create_script(script: ScriptCreate, db: Session = Depends(get_db)):
    pass

# 定时任务
@router.post("/scheduled-tasks")
async def create_scheduled_task(task: ScheduledTaskCreate, db: Session = Depends(get_db)):
    pass

# 文件上传
@router.post("/upload/script")
async def upload_script(file: UploadFile = File(...), script_type: str = "python"):
    pass
```

---

## 附录

### 开发建议

1. **使用 Pydantic 模型**: 定义请求和响应的数据模型
2. **异常处理**: 统一的异常处理中间件
3. **日志记录**: 记录所有 API 请求和响应
4. **API 文档**: 使用 FastAPI 自动生成的 Swagger 文档
5. **CORS 配置**: 允许前端跨域请求
6. **认证授权**: 使用 JWT Token 进行身份验证（后续扩展）

### 测试建议

1. 使用 `pytest` 进行单元测试
2. 使用 `httpx` 进行 API 集成测试
3. 使用 Postman 或 Insomnia 进行手动测试

---

**文档版本**: v1.0  
**最后更新**: 2026-02-16  
**维护人员**: 开发团队
