# AI失败分析功能说明

## 功能概述

系统现在支持使用AI智能分析任务失败原因，提供更准确、更具体的失败分析和解决建议。

## 工作原理

### 1. 双模式分析
- **AI模式**：如果配置了AI API Key，系统会优先使用AI分析
- **规则引擎模式**：如果未配置AI或AI分析失败，自动回退到规则引擎

### 2. AI分析优势
- ✅ 更准确的错误类型识别
- ✅ 更具体的失败步骤描述
- ✅ 更实用的解决建议
- ✅ 能理解代码上下文
- ✅ 针对具体错误给出修复方法

### 3. 分析内容
AI会分析以下信息：
- 错误消息
- 完整日志内容（最多2000字符）
- 脚本内容（最多1000字符）

## 配置方法

### 方法1：环境变量（推荐）
在 `.env` 文件中添加：
```env
AI_API_KEY=sk-your-api-key-here
AI_API_BASE=https://api.deepseek.com/v1
```

### 方法2：系统配置
在数据库的 `system_config` 表中添加：
- key: `ai_api_key`
- value: `sk-your-api-key-here`

## 使用示例

### 场景1：Python语法错误
**错误信息**：
```
IndentationError: expected an indented block after 'if' statement on line 117
```

**AI分析结果**：
- **失败类型**：script_error
- **失败步骤**：IndentationError (第117行)
- **根本原因**：Python代码第117行的if语句后缺少缩进的代码块
- **解决建议**：
  1. 检查第117行if语句后是否有正确缩进的代码
  2. 确保使用4个空格或1个Tab进行缩进（不要混用）
  3. 在if语句后添加至少一行缩进的代码或使用pass占位

### 场景2：模块未找到
**错误信息**：
```
ModuleNotFoundError: No module named 'uiautomator2'
```

**AI分析结果**：
- **失败类型**：script_error
- **失败步骤**：ModuleNotFoundError
- **根本原因**：Python环境中未安装uiautomator2库
- **解决建议**：
  1. 运行命令安装：pip install uiautomator2
  2. 确认Python环境路径正确
  3. 如果使用虚拟环境，确保已激活

### 场景3：设备连接问题
**错误信息**：
```
device not found
```

**AI分析结果**：
- **失败类型**：device_disconnected
- **失败步骤**：设备连接失败
- **根本原因**：ADB无法找到目标设备
- **解决建议**：
  1. 检查USB连接是否正常
  2. 确认设备已开启USB调试
  3. 运行 adb devices 检查设备列表
  4. 尝试重启ADB服务：adb kill-server && adb start-server

## 技术细节

### AI提示词设计
系统使用专门设计的提示词，要求AI：
1. 准确识别失败类型（8种预定义类型）
2. 提供简洁明了的根本原因分析（1-2句话）
3. 给出3-5条具体可操作的解决建议
4. 评估错误严重程度（critical/high/medium/low）

### 返回格式
AI返回JSON格式的分析结果：
```json
{
  "failure_type": "script_error",
  "failed_step": "IndentationError (第117行)",
  "root_cause": "Python代码第117行的if语句后缺少缩进的代码块",
  "suggestions": [
    "检查第117行if语句后是否有正确缩进的代码",
    "确保使用4个空格或1个Tab进行缩进",
    "在if语句后添加至少一行缩进的代码或使用pass占位"
  ],
  "severity": "low"
}
```

### 性能优化
- 超时设置：30秒
- 温度参数：0.3（更准确的分析）
- Token限制：1000（控制成本）
- 日志截断：2000字符（避免超出限制）
- 脚本截断：1000字符（提供足够上下文）

## 注意事项

1. **API成本**：每次AI分析会消耗API tokens，建议使用DeepSeek API（性价比高）
2. **回退机制**：AI分析失败时自动使用规则引擎，不影响功能
3. **缓存机制**：已分析的失败任务不会重复分析
4. **隐私保护**：日志和脚本内容会发送到AI API，请注意敏感信息

## 测试方法

1. 配置AI API Key（使用你的DeepSeek API Key）
2. 运行一个会失败的测试任务
3. 在"任务执行监控"页面点击"失败分析"
4. 查看AI生成的分析结果

## 对比效果

### 规则引擎分析
- 失败类型：unknown
- 失败步骤：（空）
- 建议：通用建议（检查日志、重新执行、联系支持）

### AI智能分析
- 失败类型：script_error
- 失败步骤：IndentationError (第117行)
- 建议：具体的代码修复方法

## 推荐配置

使用DeepSeek API（性价比最高）：
- API Base: https://api.deepseek.com/v1
- 获取API Key: https://platform.deepseek.com
- 价格：约 ¥0.001/次分析（非常便宜）

## 后续优化方向

1. 支持批量分析历史失败任务
2. 添加AI分析结果的评分和反馈机制
3. 根据反馈持续优化提示词
4. 支持自定义AI模型选择
5. 添加AI分析统计和成本追踪
