# 🚀 ADBweb - Android 自动化测试平台

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)](https://www.typescriptlang.org/)
[![Tests](https://img.shields.io/badge/tests-107%20passed-brightgreen.svg)](tests/)

一个功能强大的 Web 端 Android 自动化测试平台，支持脚本管理、设备管理、实时监控、健康度评估、失败分析等核心功能。

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [文档](#-文档) • [测试](#-测试)

</div>

---

## ✨ 功能特性

### 核心功能

| 功能模块 | 核心特性 | 状态 |
|---------|---------|------|
| **脚本管理** | 可视化编辑器、Python/批处理脚本、脚本验证、模板市场 | ✅ |
| **设备管理** | 自动发现、状态监控、分组管理、批量操作 | ✅ |
| **任务执行** | 单任务/批量执行、定时调度、实时监控 | ✅ |
| **实时监控** | WebSocket 推送、进度可视化、实时日志流 | ✅ |
| **健康度监控** | 7 维度评分、智能告警、自动数据采集 | ✅ |
| **失败分析** | 7 种错误类型识别、失败步骤定位、智能建议 | ✅ |
| **测试报告** | 详细报告、统计分析、趋势图表 | ✅ |

### 健康度评分算法

```
总分 = 电量(25%) + 温度(20%) + CPU(15%) + 内存(15%) + 存储(10%) + 网络(10%) + 活跃度(5%)
```

| 等级 | 分数 | 状态 | 说明 |
|------|------|------|------|
| 🟢 优秀 | 90-100 | 极佳 | 设备状态完美 |
| 🔵 良好 | 75-89 | 正常 | 设备运行正常 |
| 🟠 一般 | 60-74 | 关注 | 需要关注 |
| 🔴 较差 | 40-59 | 维护 | 需要维护 |
| ⚫ 危险 | <40 | 紧急 | 立即处理 |

### 支持的错误类型

| 错误类型 | 图标 | 严重程度 | 说明 |
|---------|------|---------|------|
| device_disconnected | 🔌 | critical | 设备断开连接 |
| element_not_found | 🔍 | medium | 元素未找到 |
| timeout | ⏱️ | medium | 操作超时 |
| permission_denied | 🚫 | high | 权限拒绝 |
| app_crash | 💥 | high | 应用崩溃 |
| network_error | 🌐 | medium | 网络错误 |
| script_error | 📝 | high | 脚本错误 |

---

## 🛠️ 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.109+ | Web 框架 |
| SQLModel | 0.0.14 | ORM |
| SQLite | - | 数据库 |
| WebSocket | - | 实时通信 |
| APScheduler | 3.10+ | 任务调度 |
| ADB | - | 设备控制 |

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18+ | UI 框架 |
| TypeScript | 5+ | 开发语言 |
| Ant Design | 5.12+ | UI 组件库 |
| Ant Design Charts | 2.6+ | 图表库 |
| Vite | 5+ | 构建工具 |
| React Router | 6.20+ | 路由管理 |

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 16+
- ADB (Android Debug Bridge)

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/yourusername/ADBweb.git
cd ADBweb
```

#### 2. 后端安装

```bash
cd backend
pip install -r requirements.txt

# 初始化告警规则
python init_alert_rules.py

# 初始化测试数据（可选）
python init_test_data.py
```

#### 3. 前端安装

```bash
cd ..
npm install
```

#### 4. 启动服务

**Windows**:
```bash
start.bat
```

**Linux/Mac**:
```bash
chmod +x start.sh
./start.sh
```

#### 5. 访问应用

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## 📁 项目结构

```
ADBweb/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── api/               # API 路由 (10+ 模块)
│   │   │   ├── devices.py     # 设备管理
│   │   │   ├── scripts.py     # 脚本管理
│   │   │   ├── tasks.py       # 任务执行
│   │   │   ├── device_health.py  # 健康度监控
│   │   │   ├── failure_analysis.py  # 失败分析
│   │   │   └── ...
│   │   ├── core/              # 核心配置
│   │   │   ├── database.py    # 数据库配置
│   │   │   └── websocket_manager.py  # WebSocket 管理
│   │   ├── models/            # 数据模型 (10+ 模型)
│   │   ├── services/          # 业务逻辑 (10+ 服务)
│   │   └── utils/             # 工具函数
│   ├── uploads/               # 上传文件
│   ├── main.py                # 应用入口
│   ├── requirements.txt       # Python 依赖
│   └── test_platform.db       # SQLite 数据库
│
├── src/                       # 前端源代码
│   ├── components/            # React 组件
│   │   ├── DeviceCard.tsx     # 设备卡片
│   │   ├── ScriptEditor.tsx   # 脚本编辑器
│   │   ├── TaskMonitor.tsx    # 任务监控
│   │   └── ...
│   ├── pages/                 # 页面组件 (12 个)
│   │   ├── Dashboard.tsx      # 仪表盘
│   │   ├── DeviceManagement.tsx  # 设备管理
│   │   ├── ScriptManagement.tsx  # 脚本管理
│   │   ├── DeviceHealth.tsx   # 健康度监控
│   │   └── ...
│   ├── hooks/                 # 自定义 Hooks
│   │   └── useWebSocket.ts    # WebSocket Hook
│   ├── services/              # 服务层
│   │   └── api.ts             # API 调用
│   ├── types/                 # TypeScript 类型
│   └── utils/                 # 工具函数
│
├── tests/                     # 测试套件
│   ├── test_all_features.py   # 完整测试 (107 用例)
│   ├── conftest.py            # Pytest 配置
│   ├── pytest.ini             # Pytest 配置文件
│   ├── requirements.txt       # 测试依赖
│   ├── allure-results/        # Allure 测试结果
│   ├── allure-report/         # Allure HTML 报告
│   └── README.md              # 测试说明
│
├── docs/                      # 项目文档
│   ├── API接口文档.md         # API 接口说明
│   ├── 数据库设计文档.md      # 数据库设计
│   ├── 三大核心功能完成总结.md  # 核心功能说明
│   └── ...
│
├── install.bat                # 安装脚本
├── start.bat                  # 启动脚本
├── package.json               # 前端依赖
├── vite.config.ts             # Vite 配置
├── tsconfig.json              # TypeScript 配置
└── README.md                  # 项目说明（本文档）
```

---

## 📖 API 文档

### API 端点统计

| 模块 | 端点数量 | 说明 |
|------|---------|------|
| 健康检查 | 2 | 根端点、健康检查 |
| 设备管理 | 8 | CRUD、扫描、分组、截图等 |
| 脚本管理 | 7 | CRUD、搜索、验证等 |
| 任务执行 | 3 | 执行、日志、停止 |
| 定时任务 | 5 | CRUD、启用/禁用 |
| 设备健康度 | 5 | 健康度、历史、告警等 |
| 失败分析 | 6 | 分析、统计、趋势等 |
| 模板市场 | 3 | 列表、分类、下载 |
| 仪表盘 | 1 | 统计数据 |
| WebSocket | 1 | 实时通信 |
| **总计** | **41+** | - |

### 访问 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **离线文档**: [docs/API接口文档.md](./docs/API接口文档.md)

### 核心 API 示例

#### 执行任务

```bash
POST /api/v1/tasks/execute
Content-Type: application/json

{
  "task_name": "测试任务",
  "script_id": 1,
  "device_id": 1
}
```

#### 获取设备健康度

```bash
GET /api/v1/device-health/devices/{device_id}
```

#### 获取失败分析

```bash
GET /api/v1/failure-analysis/tasks/{task_log_id}
```

---

## 🧪 测试

### 测试统计

| 指标 | 数量/状态 |
|------|----------|
| 测试类 | 26 个 |
| 测试用例 | 107 个 |
| 通过测试 | **107 个** ✅ |
| 失败测试 | **0 个** |
| 通过率 | **100%** 🎉 |
| 执行时间 | ~13 秒 |
| 测试框架 | Pytest 7.4.0 |
| 报告工具 | Allure 2.37.0 |

### 测试覆盖

| 测试类别 | 测试数量 | 说明 |
|---------|---------|------|
| 健康检查和基础功能 | 3 | 服务器、健康检查、API 版本 |
| 设备管理 | 5 | CRUD、分组、截图、批量操作 |
| 脚本管理 | 5 | CRUD、验证、搜索 |
| 模板市场 | 2 | 列表、下载 |
| 定时任务 | 2 | 列表、创建 |
| 设备健康度 | 6 | 概览、详情、告警规则 |
| 失败分析 | 3 | 列表、统计、趋势 |
| 仪表盘 | 1 | 统计数据 |
| 数据一致性 | 4 | 格式验证、外键检查 |
| 性能测试 | 2 | API 响应时间、数据库查询 |
| 集成测试 | 2 | 完整业务流程 |
| 边界条件测试 | 7 | 异常处理、边界值 |
| 并发测试 | 2 | 并发创建、快速调用 |
| 数据完整性 | 2 | CRUD 一致性、事务 |
| 复杂业务场景 | 3 | 端到端流程 |
| 搜索和过滤 | 5 | 关键词、类型、分类 |
| 数据导出和报告 | 2 | 统计准确性 |
| 脚本步骤 | 7 | 各类步骤创建 |
| 设备操作 | 5 | 刷新、断开、性能监控 |
| 定时任务详细 | 6 | 每日/每周/每月任务 |
| 模板市场详细 | 6 | 过滤、排序、详情 |
| 健康度监控详细 | 5 | 评分计算、告警类型 |
| 脚本分类 | 7 | 登录、测试、自动化等 |
| 设备状态统计 | 5 | 在线、离线、电量分布 |
| 执行历史 | 5 | 日志、成功/失败统计 |
| 数据库完整性高级 | 5 | 孤立记录、重复检查 |

### 运行测试

```bash
# 进入测试目录
cd tests

# 运行所有测试
pytest test_all_features.py -v

# 运行测试并生成 Allure 报告
run_tests_with_allure.bat

# 查看 Allure 报告
allure open allure-report
```

详细说明: [tests/README.md](./tests/README.md)

---

## 📚 文档

### 核心文档

| 文档 | 说明 |
|------|------|
| [README.md](./README.md) | 项目说明（本文档） |
| [tests/README.md](./tests/README.md) | 测试文档 |
| [API接口文档.md](./docs/API接口文档.md) | API 接口说明 |
| [数据库设计文档.md](./docs/数据库设计文档.md) | 数据库设计 |
| [三大核心功能完成总结.md](./docs/三大核心功能完成总结.md) | 核心功能说明 |
| [新功能发布说明.md](./docs/新功能发布说明.md) | 版本发布说明 |
| [失败分析功能使用指南.md](./docs/失败分析功能使用指南.md) | 失败分析使用指南 |

---

## 🚢 部署

### Docker 部署（推荐）

```bash
# 构建镜像
docker build -t adbweb:latest .

# 运行容器
docker run -d -p 8000:8000 -p 5173:5173 adbweb:latest
```

### 手动部署

```bash
# 1. 安装依赖
pip install -r backend/requirements.txt
npm install

# 2. 构建前端
npm run build

# 3. 启动后端
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 4. 配置 Nginx 托管 dist 目录
```

---

## 📝 更新日志

### v1.2.0 (2026-02-24)

**测试完善**:
- ✅ 完整测试套件（107 个测试用例，100% 通过率）
- ✅ Allure 测试报告集成
- ✅ 26 个测试类，覆盖所有功能模块
- ✅ 包括 CRUD、边界、并发、性能、安全测试

### v1.1.0 (2026-02-22)

**新增功能**:
- ✨ 实时任务执行监控（WebSocket）
- ✨ 设备健康度监控和告警（7 维度评分）
- ✨ 脚本执行失败自动分析（7 种错误类型）

**改进**:
- 🔧 优化任务执行流程
- 🔧 完善错误处理
- 🔧 改进 API 响应格式

### v1.0.0 (2026-01-01)

**初始版本**:
- 🎉 基础功能实现
- 🎉 脚本管理
- 🎉 设备管理
- 🎉 任务执行
- 🎉 测试报告

---

## ❓ 常见问题

<details>
<summary><b>设备连接失败</b></summary>

1. 检查 USB 连接
2. 确认 USB 调试已启用
3. 运行 `adb devices` 检查设备
4. 重启 ADB 服务: `adb kill-server && adb start-server`
</details>

<details>
<summary><b>任务执行失败</b></summary>

1. 查看失败分析结果
2. 根据建议修改脚本
3. 检查设备状态
4. 查看详细日志
</details>

<details>
<summary><b>WebSocket 断开</b></summary>

1. 检查网络连接
2. 系统会自动重连
3. 检查防火墙设置
</details>

<details>
<summary><b>健康度数据异常</b></summary>

1. 当前使用模拟数据
2. 需要实际 ADB 设备
3. 后续版本集成真实采集
</details>

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [React](https://reactjs.org/) - 用户界面 JavaScript 库
- [Ant Design](https://ant.design/) - 企业级 UI 设计语言
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL 数据库的 Python 库
- [Vite](https://vitejs.dev/) - 下一代前端构建工具

---

<div align="center">

**Made with ❤️ by ADBweb Team**

如果这个项目对您有帮助，请给我们一个 Star ⭐

[⬆ 回到顶部](#-adbweb---android-自动化测试平台)

</div>
