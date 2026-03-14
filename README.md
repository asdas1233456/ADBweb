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
| **AI 元素定位器** | 12种元素类型、OCR文字识别、自然语言查找、相对位置查找、区域查找、状态筛选 | ✅ |
| **AI 失败分析** | 智能分析失败原因、8种错误类型识别、解决建议生成、DeepSeek API集成 | ✅ |
| **AI 脚本生成** | 自然语言转脚本、支持 ADB/Python、规则引擎/真实AI | ✅ |
| **批量脚本生成** | 多提示词并发生成、测试套件生成、统计分析 | ✅ |
| **工作流生成** | 步骤依赖关系、组合脚本、流程自动化 | ✅ |
| **脚本模板库** | 内置模板、变量系统、分类管理、使用统计 | ✅ |

### 核心功能

| 功能模块 | 核心特性 | 状态 |
|---------|---------|------|
| **脚本验证器V2** | AST分析、污点追踪、混淆检测、YAML规则引擎、风险评分 | ✅ |
| **批量设备操作** | 批量安装/卸载应用、推送文件、执行命令、重启设备 | ✅ |
| **报告导出增强** | 支持Excel/PDF/JSON/HTML多格式导出、自定义模板 | ✅ |
| **脚本管理** | Monaco编辑器、Python/批处理脚本、实时验证、版本控制 | ✅ |
| **设备管理** | 自动发现、状态监控、分组管理、批量操作、健康检查 | ✅ |
| **任务执行** | 单任务/批量执行、定时调度、实时监控、WebSocket推送 | ✅ |
| **健康度监控** | 7维度评分、智能告警、自动数据采集、历史趋势分析 | ✅ |
| **失败分析** | AI智能分析、8种错误类型识别、失败步骤定位、解决建议 | ✅ |

---

## 🛠️ 技术栈

### 后端

- **FastAPI** 0.109.0 - Web 框架
- **uvicorn** 0.27.0 - ASGI 服务器
- **SQLModel** 0.0.14 - ORM
- **SQLite** - 数据库
- **WebSocket** - 实时通信
- **APScheduler** 3.10.4 - 任务调度
- **Pydantic** 2.5.3 - 数据验证
- **python-dotenv** 1.0.0 - 环境变量管理
- **Requests** 2.31.0 - HTTP 请求
- **httpx** 0.27.0 - 异步HTTP客户端
- **PyYAML** 6.0.2 - 配置文件解析
- **OpenCV** 4.6.0.66 - 计算机视觉
- **PaddleOCR** 2.7.3 - OCR 文字识别
- **PaddlePaddle** 2.6.2 - 深度学习框架
- **Pillow** 12.1.0 - 图像处理
- **NumPy** 1.26.4 - 数值计算
- **openpyxl** 3.1.2 - Excel文件处理
- **reportlab** 4.0.7 - PDF报告生成
- **python-multipart** 0.0.6 - 文件上传支持

### 前端

- **React** 18.2.0 - UI 框架
- **TypeScript** 5.2.2 - 开发语言
- **Ant Design** 5.12.0 - UI 组件库
- **Vite** 5.0.8 - 构建工具
- **React Router** 6.20.0 - 路由管理
- **Monaco Editor** 4.7.0 - 代码编辑器
- **Ant Design Charts** 2.6.7 - 图表组件
- **Recharts** 3.7.0 - 图表库
- **dayjs** 1.11.19 - 日期处理
- **@dnd-kit** - 拖拽功能

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 16+
- ADB (Android Debug Bridge)
- 内存：至少 4GB RAM（推荐8GB，用于PaddleOCR模型）
- 磁盘：至少 3GB 可用空间（包含AI模型）
- 操作系统：Windows 10+、Linux、macOS

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

使用计算机视觉和OCR自动识别屏幕元素，支持12种元素类型和9种状态识别。

#### 核心能力

- ✅ **12种元素类型**：按钮、输入框、文本、复选框、单选按钮、开关、滑块、图标、图片、列表项、卡片、容器
- ✅ **9种元素状态**：正常、选中、未选中、启用、禁用、聚焦、加载中、错误、未知
- ✅ **OCR文字识别**：PaddleOCR识别准确率>95%，支持中英文混合
- ✅ **自然语言查找**：支持"蓝色的登录按钮"、"顶部的搜索框"等描述
- ✅ **相对位置查找**：根据锚点元素查找左/右/上/下方向的元素
- ✅ **区域查找**：在指定矩形区域内查找特定类型元素
- ✅ **状态筛选**：按元素状态筛选（如查找所有选中的复选框）
- ✅ **可视化标注**：编号圆圈、颜色分类、智能避免重叠、统计图例
- ✅ **坐标生成**：自动计算点击坐标
- ✅ **ADB命令生成**：一键生成可执行的ADB命令

#### 使用示例

```bash
# 上传截图
POST /api/v1/ai-element-locator/upload-screenshot

# 分析截图（识别所有元素）
POST /api/v1/ai-element-locator/analyze
{
  "image_path": "uploads/screenshots/xxx.png"
}

# 文本查找
POST /api/v1/ai-element-locator/find-element
{
  "image_path": "uploads/screenshots/xxx.png",
  "query": "登录",
  "method": "text"
}

# 自然语言查找
POST /api/v1/ai-element-locator/find-element
{
  "image_path": "uploads/screenshots/xxx.png",
  "query": "蓝色的登录按钮",
  "method": "description"
}

# 相对位置查找
POST /api/v1/ai-element-locator/find-relative
{
  "image_path": "uploads/screenshots/xxx.png",
  "anchor_query": "用户名",
  "direction": "below",
  "distance_threshold": 200
}

# 区域查找
POST /api/v1/ai-element-locator/find-in-region
{
  "image_path": "uploads/screenshots/xxx.png",
  "region": [0, 0, 1080, 400],
  "element_type": "button"
}

# 状态筛选
POST /api/v1/ai-element-locator/filter-by-state
{
  "image_path": "uploads/screenshots/xxx.png",
  "element_type": "checkbox",
  "state": "checked"
}

# 生成ADB命令
POST /api/v1/ai-element-locator/generate-command
{
  "image_path": "uploads/screenshots/xxx.png",
  "action": "click",
  "query": "登录"
}

# 可视化标注
POST /api/v1/ai-element-locator/visualize
{
  "image_path": "uploads/screenshots/xxx.png",
  "show_labels": true,
  "show_center": false,
  "min_confidence": 0.0
}
```

#### 性能指标

| 操作 | 耗时 | 说明 |
|------|------|------|
| 上传截图 | <500ms | 取决于网络和文件大小 |
| 分析截图 | 1-2秒 | 首次需下载模型（~5秒） |
| 查找元素 | <100ms | 基于已分析结果 |
| 生成命令 | <50ms | 纯计算 |
| OCR识别准确率 | >95% | 标准中文字体 |
| 元素检测准确率 | >90% | 标准UI设计 |

#### 详细文档

查看完整文档：[AI元素定位器完整指南.md](./AI元素定位器完整指南.md)

### AI 失败分析

智能分析任务失败原因，提供具体的解决建议。

#### 核心能力

- ✅ **双模式分析**：AI智能分析 + 规则引擎回退
- ✅ **DeepSeek API集成**：性价比高（约¥0.001/次），中文友好
- ✅ **8种失败类型**：脚本错误、设备断连、超时、元素未找到、权限拒绝、应用崩溃、网络错误、未知错误
- ✅ **智能建议**：提供3-5条具体可操作的解决方案
- ✅ **严重程度评估**：critical/high/medium/low四级分类
- ✅ **上下文分析**：分析错误消息、完整日志（最多2000字符）、脚本内容（最多1000字符）

#### 配置方法

在 `.env` 文件中添加：
```env
AI_API_KEY=sk-your-deepseek-api-key
AI_API_BASE=https://api.deepseek.com/v1
```

#### 使用示例

```bash
# 分析失败任务
POST /api/v1/failure-analysis/analyze/{task_id}

# 批量分析
POST /api/v1/failure-analysis/batch-analyze
{
  "task_ids": [1, 2, 3]
}

# 获取分析结果
GET /api/v1/failure-analysis/result/{task_id}
```

#### 分析示例

**场景：Python语法错误**

错误信息：
```
IndentationError: expected an indented block after 'if' statement on line 117
```

AI分析结果：
```json
{
  "failure_type": "script_error",
  "failed_step": "IndentationError (第117行)",
  "root_cause": "Python代码第117行的if语句后缺少缩进的代码块",
  "suggestions": [
    "检查第117行if语句后是否有正确缩进的代码",
    "确保使用4个空格或1个Tab进行缩进（不要混用）",
    "在if语句后添加至少一行缩进的代码或使用pass占位"
  ],
  "severity": "low"
}
```

#### 详细文档

查看完整文档：[AI失败分析功能说明.md](./AI失败分析功能说明.md)

---

## 📖 API 文档

### API 端点统计

| 模块 | 端点数量 |
|------|---------|
| 设备管理 | 8 |
| 脚本管理 | 7 |
| AI 脚本生成 | 6 |
| AI 元素定位 | 20 |
| AI 失败分析 | 6 |
| 任务执行 | 3 |
| 定时任务 | 5 |
| 设备健康度 | 5 |
| 批量设备操作 | 7 |
| 报告导出 | 2 |
| 脚本验证器 | 3 |
| 活动日志 | 2 |
| **总计** | **100+** |

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

### v2.5.0 (2026-03-15) - AI功能全面升级 🎉

#### 🤖 AI元素定位器完整实现
- ✅ **12种元素类型识别**：按钮、输入框、文本、复选框、单选按钮、开关、滑块、图标、图片、列表项、卡片、容器
- ✅ **9种元素状态识别**：正常、选中、未选中、启用、禁用、聚焦、加载中等
- ✅ **PaddleOCR集成**：文字识别准确率>95%，支持中英文混合识别
- ✅ **自然语言查找**：支持"蓝色的登录按钮"、"顶部的搜索框"等描述
- ✅ **相对位置查找**：根据锚点元素查找左/右/上/下方向的元素
- ✅ **区域查找**：在指定矩形区域内查找特定类型元素
- ✅ **状态筛选**：按元素状态筛选（如查找所有选中的复选框）
- ✅ **可视化优化**：编号圆圈标注、智能避免重叠、颜色分类、统计图例

#### 🔍 AI失败分析功能上线
- ✅ **双模式分析**：AI智能分析 + 规则引擎回退机制
- ✅ **DeepSeek API集成**：性价比高（约¥0.001/次），中文友好
- ✅ **8种失败类型识别**：脚本错误、设备断连、超时、元素未找到、权限拒绝、应用崩溃、网络错误、未知错误
- ✅ **智能建议生成**：提供3-5条具体可操作的解决方案
- ✅ **严重程度评估**：critical/high/medium/low四级分类
- ✅ **上下文分析**：分析错误消息、完整日志、脚本内容

#### 🛡️ 脚本验证器V2架构
- ✅ **YAML规则配置**：灵活的规则定义系统
- ✅ **Python AST分析**：静态代码分析，检测潜在风险
- ✅ **安全规则检查**：危险函数调用、文件操作、网络请求、命令执行
- ✅ **代码质量检查**：代码复杂度、命名规范、最佳实践
- ✅ **可扩展架构**：支持自定义规则和分析器

#### 🔧 系统优化
- ✅ 完善设备管理功能（自动扫描、连接状态监控、健康检查）
- ✅ 优化定时任务调度逻辑（避免4月前执行测试任务）
- ✅ 统一时区配置（默认Asia/Shanghai，解决时间显示问题）
- ✅ Windows启动脚本优化（日志分离：backend.log + frontend.log）
- ✅ 文件上传安全增强（路径安全检查、URL安全验证）
- ✅ 错误处理改进（更详细的错误信息、堆栈追踪）

#### 🎨 前端改进
- ✅ 新增AI元素定位器页面（截图上传、可视化标注、元素查找）
- ✅ 新增失败分析页面（智能分析、解决建议、历史记录）
- ✅ 优化任务监控界面（实时状态更新、WebSocket推送）
- ✅ 改进设备健康监控（性能指标图表、历史趋势分析）
- ✅ 增强脚本编辑器（语法高亮、代码提示、实时验证）

#### 📦 技术栈更新
- ✅ FastAPI 0.109.0 + uvicorn 0.27.0（Web框架和ASGI服务器）
- ✅ OpenCV 4.6.0.66（计算机视觉和图像处理）
- ✅ PaddleOCR 2.7.3 + PaddlePaddle 2.6.2（OCR识别引擎）
- ✅ Pillow 12.1.0 + NumPy 1.26.4（图像处理和数值计算）
- ✅ httpx 0.27.0 + requests 2.31.0（HTTP客户端）
- ✅ openpyxl 3.1.2 + reportlab 4.0.7（报告导出）
- ✅ PyYAML 6.0.2（配置文件解析）
- ✅ APScheduler 3.10.4（任务调度）
- ✅ Pydantic 2.5.3（数据验证）

#### 📚 文档完善
- ✅ 新增《AI元素定位器完整指南》（40+页详细文档）
- ✅ 新增《AI失败分析功能说明》
- ✅ 更新API接口文档（新增20+个端点）
- ✅ 完善项目README（功能特性、使用示例）

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
| [AI元素定位器完整指南.md](./AI元素定位器完整指南.md) | AI元素定位器详细使用指南（40+页） |
| [AI失败分析功能说明.md](./AI失败分析功能说明.md) | AI失败分析功能说明 |
| [DOCKER_部署注意事项_中文版.md](./DOCKER_部署注意事项_中文版.md) | Docker部署指南 |
| [API接口文档](http://localhost:8000/docs) | Swagger API文档（需启动服务） |

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
