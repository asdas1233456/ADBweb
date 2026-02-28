# ADBweb - Android 自动化测试平台 API 接口文档

## 项目信息

- **项目名称**: ADBweb - Android 自动化测试平台
- **后端框架**: FastAPI
- **数据库**: SQLite + SQLModel
- **API 版本**: v2.0.0
- **Base URL**: `http://localhost:8000/api/v1`
- **文档日期**: 2026-02-26
- **新增功能**: AI 脚本生成、脚本模板库、设备健康度监控、失败分析

---

## 目录

1. [通用说明](#通用说明)
2. [仪表盘接口](#仪表盘接口)
3. [设备管理接口](#设备管理接口)
4. [脚本管理接口](#脚本管理接口)
5. [**AI 脚本生成接口**](#ai-脚本生成接口) ⭐ **新增**
6. [**脚本模板接口**](#脚本模板接口) ⭐ **新增**
7. [模板市场接口](#模板市场接口)
8. [定时任务接口](#定时任务接口)
9. [任务执行接口](#任务执行接口)
10. [**设备健康度接口**](#设备健康度接口) ⭐ **新增**
11. [**失败分析接口**](#失败分析接口) ⭐ **新增**
12. [报告中心接口](#报告中心接口)
13. [系统设置接口](#系统设置接口)
14. [活动日志接口](#活动日志接口)
15. [文件上传接口](#文件上传接口)
16. [WebSocket 接口](#websocket-接口) ⭐ **新增**

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

## AI 脚本生成接口

### 5. AI 脚本生成

**接口说明**: 使用 AI 或规则引擎生成自动化测试脚本

**请求方式**: `POST`

**接口路径**: `/ai-script/generate`

**请求参数**:

```json
{
  "prompt": "测试微信登录功能，包括输入手机号、获取验证码、输入验证码、点击登录按钮",
  "language": "adb",
  "generation_mode": "rule_engine",
  "ai_model": "gpt-3.5-turbo",
  "device_model": "Xiaomi 12 Pro"
}
```

**字段说明**:
- `prompt`: 用户提示词，描述要生成的脚本功能
- `language`: 脚本语言，可选值: `adb`, `python`
- `generation_mode`: 生成模式，可选值: `rule_engine`, `ai`
- `ai_model`: AI 模型名称（AI 模式时必填）
- `device_model`: 设备型号（可选）

**响应示例**:

```json
{
  "code": 200,
  "message": "脚本生成成功",
  "data": {
    "id": 123,
    "generated_script": "# 测试微信登录功能\nadb shell am start -n com.tencent.mm/.ui.LauncherUI\nadb shell sleep 3\n\n# 点击登录按钮\nadb shell input tap 540 800\nadb shell sleep 2\n\n# 输入手机号\nadb shell input tap 540 400\nadb shell input text \"13800138000\"\nadb shell sleep 1\n\n# 获取验证码\nadb shell input tap 800 400\nadb shell sleep 2\n\n# 输入验证码\nadb shell input tap 540 500\nadb shell input text \"123456\"\nadb shell sleep 1\n\n# 点击登录按钮\nadb shell input tap 540 600\nadb shell sleep 3\n\n# 截图保存\nadb shell screencap /sdcard/login_success.png",
    "generation_mode": "rule_engine",
    "ai_model": null,
    "device_model": "Xiaomi 12 Pro",
    "created_at": "2026-02-26T10:30:00"
  }
}
```

### 6. 批量脚本生成

**接口说明**: 批量生成多个脚本，支持并发生成和测试套件生成

**请求方式**: `POST`

**接口路径**: `/ai-script/batch-generate`

**请求参数**:

```json
{
  "prompts": [
    "测试用户注册功能",
    "测试用户登录功能", 
    "测试密码重置功能",
    "测试个人信息修改功能"
  ],
  "language": "adb",
  "generation_mode": "rule_engine",
  "generate_suite": true
}
```

**字段说明**:
- `prompts`: 提示词列表
- `language`: 脚本语言
- `generation_mode`: 生成模式
- `generate_suite`: 是否生成测试套件

**响应示例**:

```json
{
  "code": 200,
  "message": "批量生成完成",
  "data": {
    "results": [
      {
        "prompt": "测试用户注册功能",
        "status": "success",
        "script": "# 注册功能脚本...",
        "script_id": 124
      },
      {
        "prompt": "测试用户登录功能",
        "status": "success", 
        "script": "# 登录功能脚本...",
        "script_id": 125
      }
    ],
    "statistics": {
      "total": 4,
      "success": 3,
      "failed": 1,
      "duration": 12.5
    },
    "suite_script": "#!/bin/bash\n# 自动生成的测试套件\necho '开始执行测试套件...'\n# 执行各个测试脚本..."
  }
}
```

### 7. 工作流生成

**接口说明**: 生成有依赖关系的工作流脚本

**请求方式**: `POST`

**接口路径**: `/ai-script/workflow-generate`

**请求参数**:

```json
{
  "workflow_steps": [
    "启动应用并进入登录页面",
    "输入用户名和密码",
    "点击登录按钮",
    "验证登录成功",
    "进入商品搜索页面",
    "搜索指定商品",
    "查看商品详情",
    "添加商品到购物车"
  ],
  "language": "adb"
}
```

**响应示例**:

```json
{
  "code": 200,
  "message": "工作流生成成功",
  "data": {
    "workflow_id": 456,
    "steps": [
      {
        "step_index": 1,
        "step_name": "启动应用并进入登录页面",
        "script": "# 启动应用脚本...",
        "dependencies": []
      },
      {
        "step_index": 2,
        "step_name": "输入用户名和密码",
        "script": "# 输入凭据脚本...",
        "dependencies": [1]
      }
    ],
    "combined_script": "# 完整工作流脚本..."
  }
}
```

### 8. 脚本验证

**接口说明**: 验证生成脚本的语法和质量

**请求方式**: `POST`

**接口路径**: `/ai-script/validate`

**请求参数**:

```json
{
  "script_content": "adb shell am start -n com.tencent.mm/.ui.LauncherUI\nadb shell sleep 3",
  "script_type": "adb",
  "filename": "test_script.sh"
}
```

**响应示例**:

```json
{
  "code": 200,
  "message": "脚本验证完成",
  "data": {
    "passed": true,
    "score": 85,
    "issues": [
      {
        "type": "warning",
        "message": "建议在点击操作后添加等待时间",
        "line": 5
      }
    ],
    "suggestions": [
      "添加错误处理机制",
      "增加操作结果验证"
    ]
  }
}
```

### 9. 保存脚本到脚本管理

**接口说明**: 将 AI 生成的脚本保存到脚本管理系统

**请求方式**: `POST`

**接口路径**: `/ai-script/save-to-scripts`

**请求参数**:

```json
{
  "ai_script_id": 123,
  "script_name": "微信登录测试脚本",
  "script_category": "login",
  "script_description": "测试微信应用的登录功能"
}
```

**响应示例**:

```json
{
  "code": 200,
  "message": "脚本保存成功",
  "data": {
    "script_id": 789,
    "script_name": "微信登录测试脚本",
    "created_at": "2026-02-26T10:35:00"
  }
}
```

### 10. 提示词优化

**接口说明**: 智能优化用户输入的提示词

**请求方式**: `POST`

**接口路径**: `/ai-script/optimize-prompt`

**请求参数**:

```json
{
  "original_prompt": "登录",
  "language": "adb"
}
```

**响应示例**:

```json
{
  "code": 200,
  "message": "提示词优化成功",
  "data": {
    "original_prompt": "登录",
    "optimized_prompt": "测试应用登录功能，包括点击登录按钮、输入用户名和密码、点击确认登录按钮，并验证登录成功状态",
    "improvements": [
      "添加了具体的操作步骤",
      "包含了验证环节",
      "明确了测试目标"
    ]
  }
}
```

---

## 脚本模板接口

### 11. 获取模板列表

**接口说明**: 获取所有可用的脚本模板

**请求方式**: `GET`

**接口路径**: `/script-templates`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| category | string | 否 | 模板分类 |
| language | string | 否 | 脚本语言 |
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
        "name": "应用登录测试模板",
        "category": "login",
        "description": "通用的应用登录测试模板，支持用户名密码登录",
        "language": "adb",
        "template_content": "# 点击登录按钮\nadb shell input tap {{login_x}} {{login_y}}\nadb shell sleep 1\n\n# 输入用户名\nadb shell input text \"{{username}}\"\nadb shell sleep 1",
        "variables": {
          "login_x": {
            "type": "number",
            "description": "登录按钮X坐标",
            "required": true,
            "default": "540"
          },
          "login_y": {
            "type": "number", 
            "description": "登录按钮Y坐标",
            "required": true,
            "default": "400"
          },
          "username": {
            "type": "text",
            "description": "用户名",
            "required": true
          }
        },
        "tags": ["登录", "基础", "通用"],
        "usage_count": 156,
        "is_builtin": true,
        "created_at": "2026-02-26T09:00:00"
      }
    ],
    "total": 4,
    "page": 1,
    "page_size": 10,
    "total_pages": 1
  }
}
```

### 12. 使用模板生成脚本

**接口说明**: 使用模板和变量值生成具体的脚本

**请求方式**: `POST`

**接口路径**: `/script-templates/use`

**请求参数**:

```json
{
  "template_id": 1,
  "variables": {
    "login_x": "540",
    "login_y": "400", 
    "username": "testuser",
    "password": "testpass123"
  }
}
```

**响应示例**:

```json
{
  "code": 200,
  "message": "脚本生成成功",
  "data": {
    "generated_script": "# 点击登录按钮\nadb shell input tap 540 400\nadb shell sleep 1\n\n# 输入用户名\nadb shell input text \"testuser\"\nadb shell sleep 1\n\n# 输入密码\nadb shell input text \"testpass123\"\nadb shell sleep 1",
    "template_name": "应用登录测试模板",
    "used_variables": {
      "login_x": "540",
      "login_y": "400",
      "username": "testuser", 
      "password": "testpass123"
    }
  }
}
```

### 13. 创建自定义模板

**接口说明**: 创建新的脚本模板

**请求方式**: `POST`

**接口路径**: `/script-templates`

**请求参数**:

```json
{
  "name": "自定义搜索模板",
  "category": "search",
  "description": "自定义的搜索功能测试模板",
  "language": "adb",
  "template_content": "# 点击搜索框\nadb shell input tap {{search_x}} {{search_y}}\nadb shell sleep 1\n\n# 输入搜索关键词\nadb shell input text \"{{keyword}}\"\nadb shell sleep 1\n\n# 点击搜索按钮\nadb shell input keyevent 66",
  "variables": {
    "search_x": {
      "type": "number",
      "description": "搜索框X坐标",
      "required": true,
      "default": "540"
    },
    "search_y": {
      "type": "number",
      "description": "搜索框Y坐标", 
      "required": true,
      "default": "200"
    },
    "keyword": {
      "type": "text",
      "description": "搜索关键词",
      "required": true
    }
  },
  "tags": ["搜索", "自定义"]
}
```

**响应示例**:

```json
{
  "code": 200,
  "message": "模板创建成功",
  "data": {
    "id": 5,
    "name": "自定义搜索模板",
    "created_at": "2026-02-26T11:00:00"
  }
}
```

### 14. 获取模板分类

**接口说明**: 获取所有模板分类

**请求方式**: `GET`

**接口路径**: `/script-templates/categories`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "category": "login",
      "name": "登录测试",
      "count": 3
    },
    {
      "category": "search", 
      "name": "搜索功能",
      "count": 2
    },
    {
      "category": "ui_automation",
      "name": "UI自动化",
      "count": 4
    },
    {
      "category": "performance",
      "name": "性能测试",
      "count": 1
    }
  ]
}
```

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

## 设备健康度接口

### 15. 获取设备健康度

**接口说明**: 获取指定设备的健康度信息

**请求方式**: `GET`

**接口路径**: `/device-health/devices/{device_id}`

**路径参数**:
- `device_id`: 设备ID

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "device_id": 1,
    "device_name": "Xiaomi 12 Pro",
    "health_score": 85,
    "health_level": "good",
    "health_level_name": "良好",
    "health_color": "#1890ff",
    "metrics": {
      "battery_level": 75,
      "temperature": 38.5,
      "cpu_usage": 45.2,
      "memory_usage": 62.8,
      "storage_usage": 58.3,
      "network_status": "connected",
      "last_active_time": "2026-02-26T10:25:00"
    },
    "score_breakdown": {
      "battery_score": 20,
      "temperature_score": 15,
      "cpu_score": 12,
      "memory_score": 12,
      "storage_score": 10,
      "network_score": 10,
      "activity_score": 5
    },
    "last_updated": "2026-02-26T10:30:00"
  }
}
```

### 16. 获取设备健康度历史

**接口说明**: 获取设备健康度历史记录

**请求方式**: `GET`

**接口路径**: `/device-health/devices/{device_id}/history`

**路径参数**:
- `device_id`: 设备ID

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| start_date | string | 否 | 开始日期 (YYYY-MM-DD) |
| end_date | string | 否 | 结束日期 (YYYY-MM-DD) |
| limit | int | 否 | 返回数量，默认100 |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "device_id": 1,
    "records": [
      {
        "id": 1001,
        "health_score": 85,
        "battery_level": 75,
        "temperature": 38.5,
        "cpu_usage": 45.2,
        "memory_usage": 62.8,
        "storage_usage": 58.3,
        "network_status": "connected",
        "recorded_at": "2026-02-26T10:30:00"
      },
      {
        "id": 1002,
        "health_score": 82,
        "battery_level": 70,
        "temperature": 39.2,
        "cpu_usage": 48.1,
        "memory_usage": 65.3,
        "storage_usage": 58.8,
        "network_status": "connected",
        "recorded_at": "2026-02-26T10:25:00"
      }
    ],
    "total": 48,
    "date_range": {
      "start_date": "2026-02-25",
      "end_date": "2026-02-26"
    }
  }
}
```

### 17. 获取所有设备健康度概览

**接口说明**: 获取所有设备的健康度概览

**请求方式**: `GET`

**接口路径**: `/device-health/overview`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_devices": 5,
    "health_distribution": {
      "excellent": 1,
      "good": 2,
      "fair": 1,
      "poor": 1,
      "critical": 0
    },
    "average_score": 78.2,
    "devices": [
      {
        "device_id": 1,
        "device_name": "Xiaomi 12 Pro",
        "health_score": 85,
        "health_level": "good",
        "last_updated": "2026-02-26T10:30:00"
      },
      {
        "device_id": 2,
        "device_name": "iPhone 14 Pro",
        "health_score": 92,
        "health_level": "excellent",
        "last_updated": "2026-02-26T10:28:00"
      }
    ]
  }
}
```

### 18. 获取设备告警

**接口说明**: 获取设备告警信息

**请求方式**: `GET`

**接口路径**: `/device-health/alerts`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| device_id | int | 否 | 设备ID |
| severity | string | 否 | 告警级别 (info/warning/error/critical) |
| is_resolved | boolean | 否 | 是否已解决 |
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
        "id": 501,
        "device_id": 1,
        "device_name": "Xiaomi 12 Pro",
        "alert_type": "high_temperature",
        "severity": "warning",
        "message": "设备温度过高 (42.5°C)，建议降低使用频率",
        "is_resolved": false,
        "created_at": "2026-02-26T10:15:00",
        "resolved_at": null
      },
      {
        "id": 502,
        "device_id": 2,
        "device_name": "iPhone 14 Pro",
        "alert_type": "low_battery",
        "severity": "error",
        "message": "设备电量过低 (15%)，建议立即充电",
        "is_resolved": true,
        "created_at": "2026-02-26T09:30:00",
        "resolved_at": "2026-02-26T10:00:00"
      }
    ],
    "total": 12,
    "page": 1,
    "page_size": 10,
    "total_pages": 2
  }
}
```

### 19. 解决设备告警

**接口说明**: 标记设备告警为已解决

**请求方式**: `PUT`

**接口路径**: `/device-health/alerts/{alert_id}/resolve`

**路径参数**:
- `alert_id`: 告警ID

**响应示例**:

```json
{
  "code": 200,
  "message": "告警已解决",
  "data": {
    "alert_id": 501,
    "resolved_at": "2026-02-26T10:35:00"
  }
}
```

---

## 失败分析接口

### 20. 获取任务失败分析

**接口说明**: 获取指定任务的失败分析结果

**请求方式**: `GET`

**接口路径**: `/failure-analysis/tasks/{task_log_id}`

**路径参数**:
- `task_log_id`: 任务日志ID

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 301,
    "task_log_id": 1001,
    "task_name": "微信登录测试",
    "device_name": "Xiaomi 12 Pro",
    "script_name": "微信登录脚本",
    "failure_type": "element_not_found",
    "failure_type_name": "元素未找到",
    "severity": "medium",
    "severity_name": "中等",
    "error_message": "Error: element not found - 无法找到登录按钮元素",
    "confidence": 0.85,
    "failed_step_index": 3,
    "failed_step_name": "点击登录按钮",
    "suggestions": [
      "检查元素选择器是否正确",
      "确认应用界面是否已加载完成",
      "增加等待时间让界面完全加载",
      "使用截图确认元素是否存在",
      "检查应用版本是否发生变化"
    ],
    "matched_keywords": ["element not found"],
    "screenshot_path": "/uploads/screenshots/failure_1001_20260226103000.png",
    "created_at": "2026-02-26T10:30:00"
  }
}
```

### 21. 获取失败分析统计

**接口说明**: 获取失败分析的统计信息

**请求方式**: `GET`

**接口路径**: `/failure-analysis/statistics`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| start_date | string | 否 | 开始日期 (YYYY-MM-DD) |
| end_date | string | 否 | 结束日期 (YYYY-MM-DD) |
| device_id | int | 否 | 设备ID |
| script_id | int | 否 | 脚本ID |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_failures": 45,
    "failure_types": {
      "element_not_found": {
        "count": 18,
        "percentage": 40.0,
        "severity": "medium"
      },
      "timeout": {
        "count": 12,
        "percentage": 26.7,
        "severity": "medium"
      },
      "device_disconnected": {
        "count": 8,
        "percentage": 17.8,
        "severity": "critical"
      },
      "app_crash": {
        "count": 4,
        "percentage": 8.9,
        "severity": "high"
      },
      "permission_denied": {
        "count": 2,
        "percentage": 4.4,
        "severity": "high"
      },
      "script_error": {
        "count": 1,
        "percentage": 2.2,
        "severity": "high"
      }
    },
    "severity_distribution": {
      "critical": 8,
      "high": 7,
      "medium": 30,
      "low": 0
    },
    "top_failed_scripts": [
      {
        "script_id": 15,
        "script_name": "微信登录测试",
        "failure_count": 8,
        "main_failure_type": "element_not_found"
      },
      {
        "script_id": 23,
        "script_name": "淘宝搜索测试",
        "failure_count": 6,
        "main_failure_type": "timeout"
      }
    ],
    "date_range": {
      "start_date": "2026-02-20",
      "end_date": "2026-02-26"
    }
  }
}
```

### 22. 获取失败趋势分析

**接口说明**: 获取失败趋势分析数据

**请求方式**: `GET`

**接口路径**: `/failure-analysis/trends`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| period | string | 否 | 时间周期 (daily/weekly/monthly)，默认daily |
| days | int | 否 | 天数，默认7 |

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "period": "daily",
    "trends": [
      {
        "date": "2026-02-20",
        "total_tasks": 45,
        "failed_tasks": 8,
        "failure_rate": 17.8,
        "main_failure_types": ["element_not_found", "timeout"]
      },
      {
        "date": "2026-02-21",
        "total_tasks": 52,
        "failed_tasks": 6,
        "failure_rate": 11.5,
        "main_failure_types": ["device_disconnected", "timeout"]
      },
      {
        "date": "2026-02-22",
        "total_tasks": 38,
        "failed_tasks": 4,
        "failure_rate": 10.5,
        "main_failure_types": ["element_not_found"]
      }
    ],
    "summary": {
      "average_failure_rate": 13.3,
      "trend_direction": "decreasing",
      "improvement_percentage": 6.3
    }
  }
}
```

### 23. 批量分析失败任务

**接口说明**: 批量分析多个失败任务

**请求方式**: `POST`

**接口路径**: `/failure-analysis/batch-analyze`

**请求参数**:

```json
{
  "task_log_ids": [1001, 1002, 1003, 1004],
  "force_reanalyze": false
}
```

**字段说明**:
- `task_log_ids`: 任务日志ID列表
- `force_reanalyze`: 是否强制重新分析（已分析过的任务）

**响应示例**:

```json
{
  "code": 200,
  "message": "批量分析完成",
  "data": {
    "total": 4,
    "analyzed": 3,
    "skipped": 1,
    "results": [
      {
        "task_log_id": 1001,
        "status": "analyzed",
        "failure_type": "element_not_found",
        "confidence": 0.85
      },
      {
        "task_log_id": 1002,
        "status": "analyzed",
        "failure_type": "timeout",
        "confidence": 0.92
      },
      {
        "task_log_id": 1003,
        "status": "analyzed",
        "failure_type": "device_disconnected",
        "confidence": 0.98
      },
      {
        "task_log_id": 1004,
        "status": "skipped",
        "reason": "已存在分析结果"
      }
    ]
  }
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

### 24. WebSocket 连接

**接口说明**: 建立 WebSocket 连接，用于实时数据推送

**连接地址**: `ws://localhost:8000/api/v1/ws/{client_id}`

**路径参数**:
- `client_id`: 客户端唯一标识符

**连接示例**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/client-123');

ws.onopen = function() {
    console.log('WebSocket 连接已建立');
    
    // 订阅任务更新
    ws.send(JSON.stringify({
        type: 'subscribe',
        task_id: 1001
    }));
};

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    console.log('收到消息:', message);
};
```

### 25. 任务进度推送

**消息类型**: `task_progress`

**消息格式**:
```json
{
  "type": "task_progress",
  "data": {
    "task_log_id": 1001,
    "current_step": 3,
    "total_steps": 8,
    "progress": 37,
    "status": "running",
    "message": "正在执行: 点击登录按钮",
    "timestamp": "2026-02-26T10:30:15"
  }
}
```

**状态说明**:
- `started`: 任务开始
- `running`: 正在执行
- `completed`: 任务完成
- `failed`: 任务失败
- `stopped`: 任务停止

### 26. 任务日志推送

**消息类型**: `task_log`

**消息格式**:
```json
{
  "type": "task_log",
  "data": {
    "task_log_id": 1001,
    "level": "info",
    "message": "✅ 点击登录按钮 - 完成",
    "timestamp": "10:30:15"
  }
}
```

**日志级别**:
- `info`: 信息日志
- `success`: 成功日志
- `warning`: 警告日志
- `error`: 错误日志

### 27. 设备状态推送

**消息类型**: `device_status`

**消息格式**:
```json
{
  "type": "device_status",
  "data": {
    "device_id": 1,
    "device_name": "Xiaomi 12 Pro",
    "status": "online",
    "battery_level": 75,
    "temperature": 38.5,
    "last_active": "2026-02-26T10:30:00"
  }
}
```

### 28. 设备告警推送

**消息类型**: `device_alert`

**消息格式**:
```json
{
  "type": "device_alert",
  "data": {
    "alert_id": 501,
    "device_id": 1,
    "device_name": "Xiaomi 12 Pro",
    "alert_type": "high_temperature",
    "severity": "warning",
    "message": "设备温度过高 (42.5°C)，建议降低使用频率",
    "created_at": "2026-02-26T10:30:00"
  }
}
```

### 29. 健康度更新推送

**消息类型**: `health_update`

**消息格式**:
```json
{
  "type": "health_update",
  "data": {
    "device_id": 1,
    "device_name": "Xiaomi 12 Pro",
    "health_score": 85,
    "health_level": "good",
    "previous_score": 82,
    "updated_at": "2026-02-26T10:30:00"
  }
}
```

### 30. 客户端消息

**订阅任务更新**:
```json
{
  "type": "subscribe",
  "task_id": 1001
}
```

**取消订阅**:
```json
{
  "type": "unsubscribe", 
  "task_id": 1001
}
```

**心跳消息**:
```json
{
  "type": "ping",
  "timestamp": 1708934400000
}
```

**心跳响应**:
```json
{
  "type": "pong",
  "timestamp": 1708934400000
}
```

### 31. 连接管理

**连接确认**:
```json
{
  "type": "connected",
  "client_id": "client-123",
  "message": "WebSocket 连接成功"
}
```

**订阅确认**:
```json
{
  "type": "subscribed",
  "task_id": 1001,
  "message": "已订阅任务 1001"
}
```

**错误消息**:
```json
{
  "type": "error",
  "code": "INVALID_MESSAGE",
  "message": "无效的消息格式"
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

## API 端点统计

### v2.0.0 新增接口

| 模块 | 新增端点 | 说明 |
|------|---------|------|
| **AI 脚本生成** | 6个 | 单个生成、批量生成、工作流生成、验证、保存、优化 |
| **脚本模板** | 4个 | 列表、使用、创建、分类 |
| **设备健康度** | 5个 | 健康度查询、历史记录、概览、告警管理 |
| **失败分析** | 4个 | 分析结果、统计、趋势、批量分析 |
| **WebSocket** | 8个消息类型 | 任务进度、日志、设备状态、告警、健康度更新 |

### 总计端点数量

| 版本 | 端点数量 | 新增 | 说明 |
|------|---------|------|------|
| v1.0.0 | 33个 | - | 基础功能 |
| **v2.0.0** | **52个** | **+19个** | **AI功能 + 监控分析** |

---

## 更新日志

### v2.0.0 (2026-02-26) - AI 功能重大更新

**🤖 新增 AI 功能接口**:
- ✨ AI 脚本生成接口 (6个)
- ✨ 脚本模板管理接口 (4个)
- ✨ 提示词优化接口

**📊 新增监控分析接口**:
- ✨ 设备健康度监控接口 (5个)
- ✨ 失败分析接口 (4个)
- ✨ 实时告警推送

**🔄 增强 WebSocket 功能**:
- ✨ 任务进度实时推送
- ✨ 设备状态实时更新
- ✨ 健康度变化通知
- ✨ 告警实时推送

**🔧 接口优化**:
- 🔧 统一响应格式
- 🔧 完善错误处理
- 🔧 增加参数验证
- 🔧 优化性能

### v1.0.0 (2026-02-16) - 基础版本

**基础功能**:
- 设备管理接口
- 脚本管理接口
- 任务执行接口
- 报告中心接口
- 系统设置接口

---

**文档版本**: v2.0.0  
**最后更新**: 2026-02-26  
**维护人员**: ADBweb 开发团队  
**API 总数**: 52+ 个接口
