# 🚀 ADBweb - Android 自动化测试平台

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)](https://www.typescriptlang.org/)

一个功能强大的 Web 端 Android 自动化测试平台，支持 AI 脚本生成、设备管理、实时监控、健康度评估、失败分析等核心功能。

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [AI 功能](#-ai-功能) • [文档](#-文档)

</div>

---

## ✨ 功能特性

### 🤖 AI 功能

| 功能模块 | 核心特性 | 状态 |
|---------|---------|------|
| **AI 脚本生成** | 自然语言转脚本、支持 ADB/Python、规则引擎/真实AI | ✅ |
| **批量脚本生成** | 多提示词并发生成、测试套件生成、统计分析 | ✅ |
| **工作流生成** | 步骤依赖关系、组合脚本、流程自动化 | ✅ |
| **脚本模板库** | 内置模板、变量系统、分类管理、使用统计 | ✅ |
| **AI 元素定位器** | 图像识别、OCR文字识别、智能定位、坐标生成 | ✅ |

### 核心功能

| 功能模块 | 核心特性 | 状态 |
|---------|---------|------|
| **脚本验证器V2** | AST分析、污点追踪、混淆检测、规则引擎、风险评分 | ✅ |
| **批量设备操作** | 批量安装/卸载应用、推送文件、执行命令、重启设备 | ✅ |
| **报告导出增强** | 支持Excel/PDF/JSON/HTML多格式导出、自定义模板 | ✅ |
| **脚本管理** | 可视化编辑器、Python/批处理脚本、脚本验证 | ✅ |
| **设备管理** | 自动发现、状态监控、分组管理、批量操作 | ✅ |
| **任务执行** | 单任务/批量执行、定时调度、实时监控 | ✅ |
| **健康度监控** | 7 维度评分、智能告警、自动数据采集 | ✅ |
| **失败分析** | 7 种错误类型识别、失败步骤定位、智能建议 | ✅ |

---

## 🛠️ 技术栈

### 后端

- **FastAPI** 0.109+ - Web 框架
- **SQLModel** 0.0.14 - ORM
- **SQLite** - 数据库
- **WebSocket** - 实时通信
- **APScheduler** 3.10+ - 任务调度
- **Requests** 2.31.0 - HTTP 请求
- **PyYAML** 6.0.1 - 配置文件解析
- **OpenCV** 4.8.1 - 图像处理
- **PaddleOCR** 2.7.0 - OCR 文字识别
- **PaddlePaddle** 2.5.2 - 深度学习框架

### 前端

- **React** 18+ - UI 框架
- **TypeScript** 5+ - 开发语言
- **Ant Design** 5.12+ - UI 组件库
- **Vite** 5+ - 构建工具
- **React Router** 6.20+ - 路由管理

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 16+
- ADB (Android Debug Bridge)
- 内存：至少 4GB RAM
- 磁盘：至少 2GB 可用空间

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

---

## 📁 项目结构

```
ADBweb/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── api/               # API 路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   ├── utils/             # 工具函数
│   │   └── validator/         # 脚本验证器 V2.0
│   ├── uploads/               # 上传文件
│   ├── main.py                # 应用入口
│   ├── requirements.txt       # Python 依赖
│   ├── init_test_data.py      # 测试数据初始化
│   └── test_platform.db       # SQLite 数据库
│
├── src/                       # 前端源代码
│   ├── components/            # React 组件
│   ├── pages/                 # 页面组件
│   ├── hooks/                 # 自定义 Hooks
│   ├── services/              # 服务层
│   └── types/                 # TypeScript 类型
│
├── tests/                     # 测试套件
├── docs/                      # 项目文档
├── backup_database.bat        # 数据库备份脚本
├── restore_database.bat       # 数据库恢复脚本
├── package.json               # 前端依赖
└── README.md                  # 项目说明
```

---

## 🤖 AI 功能

### AI 脚本生成

支持自然语言转换为可执行的自动化脚本。

#### 支持的 AI 模式

| 模式 | 说明 | 优势 |
|------|------|------|
| **规则引擎** | 本地规则生成 | 快速、稳定、免费 |
| **OpenAI** | GPT 模型生成 | 智能、灵活 |
| **DeepSeek** | 国产 AI 模型 | 中文友好、成本低 |

#### 使用示例

```bash
# 单个脚本生成
POST /api/v1/ai-script/generate
{
  "prompt": "测试微信登录功能",
  "language": "adb"
}

# 批量脚本生成
POST /api/v1/ai-script/batch-generate
{
  "prompts": ["测试登录", "测试搜索", "测试支付"],
  "language": "adb",
  "generate_suite": true
}
```

### AI 元素定位器

使用计算机视觉和OCR自动识别屏幕元素。

#### 核心能力

- ✅ **图像分析** - OpenCV自动识别按钮、输入框等UI元素
- ✅ **OCR文字识别** - PaddleOCR识别按钮文字
- ✅ **智能定位** - 基于文本或自然语言描述查找元素
- ✅ **坐标生成** - 自动计算点击坐标
- ✅ **ADB命令生成** - 一键生成可执行的ADB命令

#### 使用示例

```bash
# 上传截图
POST /api/v1/ai-element-locator/upload-screenshot

# 分析截图
POST /api/v1/ai-element-locator/analyze
{
  "image_path": "uploads/screenshots/xxx.png"
}

# 查找元素
POST /api/v1/ai-element-locator/find-element
{
  "image_path": "uploads/screenshots/xxx.png",
  "query": "登录",
  "method": "auto"
}

# 生成ADB命令
POST /api/v1/ai-element-locator/generate-command
{
  "image_path": "uploads/screenshots/xxx.png",
  "action": "click",
  "query": "登录"
}
```

---

## 📖 API 文档

### API 端点统计

| 模块 | 端点数量 |
|------|---------|
| 设备管理 | 8 |
| 脚本管理 | 7 |
| AI 脚本生成 | 6 |
| AI 元素定位 | 14 |
| 任务执行 | 3 |
| 定时任务 | 5 |
| 设备健康度 | 5 |
| 失败分析 | 6 |
| 批量设备操作 | 7 |
| 报告导出 | 2 |
| **总计** | **81+** |

### 访问 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🗄️ 数据库管理

### 备份数据库

```bash
# Windows
backup_database.bat

# 备份文件保存在 backups/ 目录
# 文件名格式: test_platform_YYYYMMDD_HHMMSS.db
```

### 恢复数据库

```bash
# Windows
restore_database.bat

# 按提示选择要恢复的备份文件
```

### 初始化测试数据

```bash
cd backend
python init_test_data.py
```

这将创建：
- 5台测试设备
- 8个测试脚本
- 20条任务日志

---

## 📝 更新日志

### v2.4.0 (2026-03-08) - 健康度监控优化

#### 新增
- ✅ 点击"查看详情"时自动触发实时健康度数据采集
- ✅ 添加 httpx==0.27.0 依赖用于异步 HTTP 请求

#### 修复
- ✅ 修复 CPU 使用率计算公式，解决多核 CPU 计算错误导致的负值问题
- ✅ 修复内存使用率计算，添加边界检查确保值在 0-100 范围内
- ✅ 修复设备健康度历史数据 API 缺失路由装饰器的问题
- ✅ 修复 AI 失败分析环境变量加载问题

#### 优化
- ✅ 优化健康度数据查询性能，使用子查询获取最新记录
- ✅ 添加历史数据降采样功能，减少前端渲染压力
- ✅ 改进 ADB 设备扫描逻辑，更准确地解析设备信息
- ✅ 优化错误消息提取和失败步骤定位

#### 变更
- ✅ 将 AI 脚本生成从 requests 迁移到 httpx，提升异步性能
- ✅ 增强 AI 失败分析，支持 DeepSeek API 智能分析
- ✅ 改进错误模式识别，支持更多 Python 错误类型

#### 移除
- ✅ 删除临时测试脚本和调试文件
- ✅ 删除不必要的文档文件
- ✅ 优化项目结构

### v2.3.0 (2026-02-28) - 依赖完善

**📦 依赖更新**:
- ✅ 添加 requests==2.31.0 - HTTP请求库
- ✅ 添加 pyyaml==6.0.1 - YAML配置文件解析
- ✅ 添加 paddleocr==2.7.0 - OCR文字识别
- ✅ 添加 paddlepaddle==2.5.2 - PaddleOCR依赖

**🔧 项目清理**:
- ✅ 删除备份文件（*.bak）
- ✅ 删除异常文件
- ✅ 创建 .gitignore 文件
- ✅ 创建数据库备份/恢复脚本

**📚 文档更新**:
- ✅ 更新 README.md
- ✅ 完善依赖说明
- ✅ 添加数据库管理说明

### v2.2.0 (2026-02-27) - AI元素定位器

**🎯 AI智能元素定位器**:
- ✨ 图像分析和OCR文字识别
- ✨ 智能定位和坐标生成
- ✨ ADB命令生成
- ✨ 14个API端点

**🔧 批量设备操作**:
- ✨ 批量安装/卸载应用
- ✨ 批量推送文件和执行命令
- ✨ 并发执行支持

**📊 报告导出增强**:
- ✨ 支持Excel/PDF/JSON/HTML格式
- ✨ 自定义内容和统计摘要

### v2.1.0 (2026-02-26) - 功能增强

**🎯 定时任务增强**:
- ✨ 立即执行时支持选择设备
- ✨ 任务执行统计

**🔧 Python 依赖自动安装**:
- ✨ 自动检测和安装缺失依赖
- ✨ 实时显示安装进度

**⚡ 性能优化**:
- ✨ 应用启动时间从 >30秒 降至 <5秒
- ✨ API 响应时间优化

### v2.0.0 (2026-02-26) - AI 功能

**🤖 AI 功能**:
- ✨ AI 脚本生成
- ✨ 批量脚本生成和工作流生成
- ✨ 脚本模板库
- ✨ 脚本验证器 V2.0

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [README.md](./README.md) | 项目说明（本文档） |
| [API接口文档.md](./docs/API接口文档.md) | API 接口说明 |
| [数据库设计文档.md](./docs/数据库设计文档.md) | 数据库设计 |
| [AI_FEATURES_GUIDE.md](./docs/AI_FEATURES_GUIDE.md) | AI 功能使用指南 |

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

[MIT License](LICENSE)

---

## 📧 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star！⭐**

Made with ❤️ by ADBweb Team

</div>
