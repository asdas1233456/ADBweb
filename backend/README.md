# 手机自动化测试平台 - 后端

基于 FastAPI + SQLModel + SQLite 的手机自动化测试平台后端服务。

## 技术栈

- **FastAPI**: 现代化的 Python Web 框架
- **SQLModel**: 基于 Pydantic 和 SQLAlchemy 的 ORM
- **SQLite**: 轻量级数据库
- **APScheduler**: 定时任务调度
- **UIAutomator2**: Android 自动化测试（预留接口）

## 项目结构

```
backend/
├── app/
│   ├── api/              # API 路由
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── devices.py
│   │   ├── scripts.py
│   │   ├── templates.py
│   │   ├── scheduled_tasks.py
│   │   ├── tasks.py
│   │   ├── reports.py
│   │   ├── settings.py
│   │   ├── activity_logs.py
│   │   └── upload.py
│   ├── core/             # 核心配置
│   │   ├── config.py
│   │   └── database.py
│   ├── models/           # 数据模型
│   │   ├── __init__.py
│   │   ├── device.py
│   │   ├── script.py
│   │   ├── template.py
│   │   ├── scheduled_task.py
│   │   ├── task_log.py
│   │   ├── system_config.py
│   │   └── activity_log.py
│   ├── schemas/          # 数据模式
│   │   ├── common.py
│   │   └── dashboard.py
│   ├── services/         # 业务逻辑
│   │   ├── dashboard_service.py
│   │   └── scheduler_service.py
│   └── utils/            # 工具函数
│       ├── file_handler.py
│       └── init_data.py
├── main.py               # 应用入口
├── requirements.txt      # 依赖包
├── .env.example          # 环境变量示例
└── README.md             # 项目文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

### 3. 启动服务

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 数据库

项目使用 SQLite 数据库，数据库文件位于 `test_platform.db`。

首次启动时会自动创建数据库表并初始化系统配置和模板数据。

## API 接口

详细的 API 接口文档请参考根目录下的 `API接口文档.md`。

主要接口包括：

- **仪表盘**: `/api/v1/dashboard/overview` - 获取仪表盘聚合数据
- **设备管理**: `/api/v1/devices` - 设备列表、详情、刷新、断开
- **脚本管理**: `/api/v1/scripts` - 脚本增删改查
- **模板市场**: `/api/v1/templates` - 模板列表、详情、下载
- **定时任务**: `/api/v1/scheduled-tasks` - 定时任务增删改查、启用/禁用、立即执行
- **任务执行**: `/api/v1/tasks` - 执行脚本、获取日志、停止任务
- **报告中心**: `/api/v1/reports` - 报告列表、详情
- **系统设置**: `/api/v1/settings` - 获取/更新系统配置
- **活动日志**: `/api/v1/activity-logs` - 活动日志列表
- **文件上传**: `/api/v1/upload` - 脚本文件、截图上传

## 已实现功能

✅ 完整的 REST API 接口（33个端点）  
✅ 数据库模型和表结构（7个表）  
✅ 仪表盘数据聚合服务  
✅ 定时任务调度服务（APScheduler）  
✅ 文件上传处理  
✅ 系统配置管理  
✅ 分页查询支持  
✅ CORS 跨域配置  
✅ 自动初始化数据  
✅ 统一响应格式  
✅ 错误处理  

## 开发说明

### 添加新的 API 路由

1. 在 `app/api/` 目录下创建新的路由文件
2. 定义路由和处理函数
3. 在 `app/api/__init__.py` 中导出路由
4. 在 `main.py` 中注册路由

### 添加新的数据模型

1. 在 `app/models/` 目录下创建新的模型文件
2. 继承 `SQLModel` 并定义字段
3. 在 `app/models/__init__.py` 中导出模型

### 添加新的业务逻辑

1. 在 `app/services/` 目录下创建新的服务文件
2. 实现业务逻辑函数
3. 在路由中调用服务函数

## 注意事项

1. **脚本执行**: 当前脚本执行功能为预留接口，实际执行逻辑需要集成 UIAutomator2
2. **WebSocket**: WebSocket 实时推送功能待实现
3. **文件上传**: 上传的文件保存在 `uploads/` 目录下
4. **定时任务**: 使用 APScheduler 实现，任务调度逻辑在 `scheduler_service.py` 中
5. **数据库**: 首次启动会自动创建表和初始化数据

## 待实现功能

- [ ] UIAutomator2 集成（脚本执行）
- [ ] WebSocket 实时日志推送
- [ ] WebSocket 设备状态推送
- [ ] 用户认证和权限管理
- [ ] 数据库迁移工具（Alembic）
- [ ] 单元测试和集成测试
- [ ] Docker 容器化部署

## 测试

启动服务后，可以通过以下方式测试：

1. 访问 Swagger UI: http://localhost:8000/docs
2. 使用 Postman 或 Insomnia 导入 API 文档
3. 前端项目连接后端进行集成测试

## 许可证

MIT License
