# ADBweb AI 功能使用指南

## 📋 文档信息

| 项目名称 | ADBweb AI 功能使用指南 |
|---------|----------------------|
| 文档版本 | v2.0.0 |
| 更新时间 | 2026-02-26 |
| 适用版本 | ADBweb v2.0.0+ |

---

## 🤖 AI 功能概览

ADBweb 集成了强大的 AI 脚本生成功能，支持将自然语言描述转换为可执行的自动化测试脚本。无论您是测试新手还是专家，都能通过简单的文字描述快速生成专业的测试脚本。

### 🎯 核心功能

| 功能 | 说明 | 支持语言 | 状态 |
|------|------|---------|------|
| **单个脚本生成** | 根据提示词生成单个脚本 | ADB, Python | ✅ |
| **批量脚本生成** | 同时生成多个脚本 | ADB, Python | ✅ |
| **工作流生成** | 生成有依赖关系的脚本流程 | ADB, Python | ✅ |
| **脚本模板库** | 预置常用模板，支持变量 | ADB, Python | ✅ |
| **脚本验证保存** | 自动验证并保存到脚本管理 | ADB, Python | ✅ |
| **提示词优化** | 智能优化用户输入的提示词 | - | ✅ |

---

## 🚀 快速开始

### 第一步：访问 AI 脚本生成页面

1. 登录 ADBweb 平台
2. 在左侧导航栏点击 "AI 脚本生成"
3. 进入 AI 脚本生成界面

### 第二步：配置 AI 服务（可选）

如果您想使用真实的 AI 服务而不是规则引擎，需要配置 API Key：

1. 点击页面右上角的 "AI 配置" 按钮
2. 选择 AI 服务提供商（OpenAI 或 DeepSeek）
3. 输入您的 API Key
4. 选择模型（如 gpt-3.5-turbo 或 deepseek-chat）
5. 点击 "保存配置"

### 第三步：生成您的第一个脚本

1. 在提示词输入框中输入：`测试微信登录功能`
2. 选择脚本语言：`ADB`
3. 点击 "生成脚本" 按钮
4. 等待生成完成，查看生成的脚本

---

## 🔧 AI 服务配置

### 支持的 AI 服务

#### 1. OpenAI (推荐)

**优势**：
- 智能程度高，理解能力强
- 支持复杂逻辑生成
- 生成质量稳定

**配置步骤**：
1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 创建 API Key
3. 在 ADBweb 中配置：
   ```
   API Key: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   模型: gpt-3.5-turbo (推荐) 或 gpt-4
   ```

**费用**：按使用量计费，约 $0.002/1K tokens

#### 2. DeepSeek (国产推荐)

**优势**：
- 中文理解能力强
- 成本相对较低
- 国内访问稳定

**配置步骤**：
1. 访问 [DeepSeek Platform](https://platform.deepseek.com/api_keys)
2. 创建 API Key
3. 在 ADBweb 中配置：
   ```
   API Key: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   模型: deepseek-chat
   ```

**费用**：按使用量计费，约 ¥0.001/1K tokens

#### 3. 规则引擎 (免费)

**优势**：
- 完全免费
- 响应速度快
- 无需网络连接
- 结果稳定可预测

**适用场景**：
- 简单的点击、输入操作
- 基础的测试流程
- 网络环境受限的情况

---

## 📝 脚本生成指南

### 单个脚本生成

#### 基础用法

**输入示例**：
```
测试淘宝商品搜索功能
```

**生成结果**：
```bash
# 启动淘宝应用
adb shell am start -n com.taobao.taobao/.activity.MainActivity
adb shell sleep 3

# 点击搜索框
adb shell input tap 540 200
adb shell sleep 1

# 输入搜索关键词
adb shell input text "手机"
adb shell sleep 1

# 点击搜索按钮
adb shell input keyevent 66
adb shell sleep 3

# 验证搜索结果
adb shell screencap /sdcard/search_result.png
```

#### 高级用法

**输入示例**：
```
测试微信登录功能，包括输入手机号、获取验证码、输入验证码、点击登录按钮，并验证登录成功
```

**生成结果**：
```bash
# 启动微信应用
adb shell am start -n com.tencent.mm/.ui.LauncherUI
adb shell sleep 3

# 点击登录按钮
adb shell input tap 540 800
adb shell sleep 2

# 点击手机号输入框
adb shell input tap 540 400
adb shell sleep 1

# 输入手机号
adb shell input text "13800138000"
adb shell sleep 1

# 点击获取验证码
adb shell input tap 800 400
adb shell sleep 2

# 点击验证码输入框
adb shell input tap 540 500
adb shell sleep 1

# 输入验证码（需要手动获取）
adb shell input text "123456"
adb shell sleep 1

# 点击登录按钮
adb shell input tap 540 600
adb shell sleep 3

# 验证登录成功（截图保存）
adb shell screencap /sdcard/login_success.png
```

### 批量脚本生成

#### 使用场景
- 生成多个相关的测试脚本
- 创建完整的测试套件
- 批量处理相似的测试需求

#### 操作步骤
1. 点击 "批量生成" 标签页
2. 在提示词列表中输入多个提示词（每行一个）：
   ```
   测试用户注册功能
   测试用户登录功能
   测试密码重置功能
   测试个人信息修改功能
   ```
3. 选择脚本语言
4. 勾选 "生成测试套件"（可选）
5. 点击 "批量生成" 按钮

#### 生成结果
- 每个提示词对应一个独立的脚本
- 提供详细的统计信息（成功/失败数量）
- 可选择生成测试套件（将所有脚本组合）

### 工作流生成

#### 使用场景
- 生成有步骤依赖关系的测试流程
- 创建端到端的测试场景
- 复杂业务流程的自动化

#### 操作步骤
1. 点击 "工作流生成" 标签页
2. 输入工作流步骤（每行一个步骤）：
   ```
   启动应用并进入登录页面
   输入用户名和密码
   点击登录按钮
   验证登录成功
   进入商品搜索页面
   搜索指定商品
   查看商品详情
   添加商品到购物车
   ```
3. 选择脚本语言
4. 点击 "生成工作流" 按钮

#### 生成结果
- 每个步骤对应一个独立的脚本
- 生成组合脚本（所有步骤的完整流程）
- 步骤间的依赖关系和等待时间

---

## 📚 脚本模板库

### 内置模板

#### 1. 应用登录测试模板

**模板内容**：
```bash
# 点击登录按钮
adb shell input tap {{login_x}} {{login_y}}
adb shell sleep 1

# 输入用户名
adb shell input text "{{username}}"
adb shell sleep 1

# 点击密码输入框
adb shell input tap {{password_x}} {{password_y}}
adb shell sleep 1

# 输入密码
adb shell input text "{{password}}"
adb shell sleep 1

# 点击登录确认按钮
adb shell input tap {{confirm_x}} {{confirm_y}}
adb shell sleep 3
```

**变量说明**：
- `login_x`, `login_y`: 登录按钮坐标
- `username`: 用户名
- `password_x`, `password_y`: 密码输入框坐标
- `password`: 密码
- `confirm_x`, `confirm_y`: 确认按钮坐标

#### 2. 搜索功能测试模板

**模板内容**：
```bash
# 点击搜索框
adb shell input tap {{search_x}} {{search_y}}
adb shell sleep 1

# 输入搜索关键词
adb shell input text "{{search_keyword}}"
adb shell sleep 1

# 点击搜索按钮或按回车
adb shell input keyevent 66
adb shell sleep 3

# 验证搜索结果
adb shell screencap /sdcard/search_result.png
```

**变量说明**：
- `search_x`, `search_y`: 搜索框坐标
- `search_keyword`: 搜索关键词

#### 3. Python UI 自动化模板

**模板内容**：
```python
import time
import subprocess

def test_{{app_name}}_automation():
    """{{app_name}} 自动化测试"""
    
    # 启动应用
    subprocess.run(['adb', 'shell', 'am', 'start', '-n', '{{package_name}}'])
    time.sleep({{wait_time}})
    
    # 执行测试步骤
    # TODO: 添加具体的测试步骤
    
    # 截图保存结果
    subprocess.run(['adb', 'shell', 'screencap', '/sdcard/test_result.png'])
    
    print("测试完成")

if __name__ == "__main__":
    test_{{app_name}}_automation()
```

**变量说明**：
- `app_name`: 应用名称
- `package_name`: 应用包名
- `wait_time`: 等待时间（秒）

### 使用模板

#### 操作步骤
1. 点击 "脚本模板" 标签页
2. 浏览可用的模板列表
3. 点击 "使用模板" 按钮
4. 在弹出的对话框中填写变量值：
   ```
   login_x: 540
   login_y: 400
   username: testuser
   password_x: 540
   password_y: 500
   password: testpass123
   confirm_x: 540
   confirm_y: 600
   ```
5. 点击 "生成脚本" 按钮

#### 创建自定义模板

1. 点击 "创建模板" 按钮
2. 填写模板信息：
   - 模板名称
   - 模板分类
   - 模板描述
   - 脚本语言
3. 编写模板内容（使用 `{{变量名}}` 格式）
4. 定义变量配置（JSON 格式）：
   ```json
   {
     "username": {
       "type": "text",
       "description": "用户名",
       "required": true,
       "default": "testuser"
     },
     "password": {
       "type": "password",
       "description": "密码",
       "required": true
     },
     "wait_time": {
       "type": "number",
       "description": "等待时间（秒）",
       "required": false,
       "default": "3"
     }
   }
   ```
5. 添加标签（可选）
6. 点击 "保存模板" 按钮

---

## ✅ 脚本验证与保存

### 自动验证功能

生成的脚本会自动进行以下验证：

#### 1. 语法检查
- **ADB 脚本**：检查 ADB 命令格式
- **Python 脚本**：检查 Python 语法

#### 2. 安全检查
- 检查是否包含危险命令
- 验证文件路径安全性
- 检查权限要求

#### 3. 最佳实践检查
- 检查是否包含适当的等待时间
- 验证错误处理机制
- 检查代码结构合理性

### 验证结果示例

```json
{
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
```

### 保存到脚本管理

验证通过的脚本可以一键保存到脚本管理系统：

1. 点击 "保存到脚本管理" 按钮
2. 填写脚本信息：
   - 脚本名称
   - 脚本分类
   - 脚本描述
3. 点击 "确认保存" 按钮
4. 脚本将出现在脚本管理页面，可以直接执行

---

## 🎯 最佳实践

### 提示词编写技巧

#### 1. 明确具体
❌ **不好的示例**：
```
测试登录
```

✅ **好的示例**：
```
测试微信登录功能，包括点击登录按钮、输入手机号13800138000、获取验证码、输入验证码、点击登录确认按钮，并验证登录成功
```

#### 2. 包含关键信息
- 应用名称（微信、淘宝、支付宝等）
- 具体操作步骤
- 测试数据（手机号、用户名等）
- 验证方式（截图、文本检查等）

#### 3. 使用结构化描述
```
测试场景：用户注册流程
前置条件：应用已安装并启动
测试步骤：
1. 点击注册按钮
2. 输入手机号13800138000
3. 点击获取验证码
4. 输入验证码123456
5. 设置密码test123456
6. 点击完成注册
验证结果：显示注册成功页面
```

### 脚本优化建议

#### 1. 添加适当的等待时间
```bash
# 好的做法
adb shell input tap 540 400
adb shell sleep 2  # 等待页面加载

# 不好的做法
adb shell input tap 540 400
adb shell input tap 540 500  # 没有等待时间
```

#### 2. 包含错误处理
```python
# Python 脚本示例
try:
    subprocess.run(['adb', 'shell', 'input', 'tap', '540', '400'], check=True)
    time.sleep(2)
except subprocess.CalledProcessError as e:
    print(f"操作失败: {e}")
    return False
```

#### 3. 添加验证步骤
```bash
# 执行操作后验证结果
adb shell input tap 540 400
adb shell sleep 2
adb shell screencap /sdcard/result.png
adb pull /sdcard/result.png ./result.png
```

### 常见问题解决

#### 1. 生成的脚本坐标不准确

**解决方案**：
- 使用相对坐标而不是绝对坐标
- 在提示词中指定屏幕分辨率
- 使用元素定位而不是坐标点击

**示例**：
```
测试登录功能，在1080x1920分辨率的设备上，登录按钮位于屏幕中央偏下位置
```

#### 2. 脚本执行速度过快

**解决方案**：
- 在提示词中强调添加等待时间
- 使用模板时设置合适的等待参数

**示例**：
```
测试登录功能，每个操作之间需要等待2-3秒，确保页面完全加载
```

#### 3. 缺少错误处理

**解决方案**：
- 在提示词中要求添加异常处理
- 使用 Python 模板时包含 try-catch 结构

**示例**：
```
测试登录功能，需要包含错误处理，如果登录失败要截图保存错误信息
```

---

## 🔍 故障排除

### 常见错误及解决方案

#### 1. AI 服务连接失败

**错误信息**：
```
连接 AI 服务失败，请检查网络连接和 API Key 配置
```

**解决步骤**：
1. 检查网络连接是否正常
2. 验证 API Key 是否正确
3. 确认 API Key 是否有足够的额度
4. 尝试切换到规则引擎模式

#### 2. 脚本生成超时

**错误信息**：
```
脚本生成超时，请稍后重试
```

**解决步骤**：
1. 简化提示词内容
2. 检查网络连接稳定性
3. 尝试分批生成（批量生成时）
4. 联系技术支持

#### 3. 脚本验证失败

**错误信息**：
```
脚本验证失败：语法错误
```

**解决步骤**：
1. 查看详细的验证报告
2. 手动修正语法错误
3. 重新生成脚本
4. 使用模板生成

#### 4. 模板变量配置错误

**错误信息**：
```
模板变量配置不完整
```

**解决步骤**：
1. 检查所有必填变量是否已填写
2. 验证变量值格式是否正确
3. 参考模板说明文档
4. 使用默认值进行测试

---

## 📊 使用统计与分析

### 生成统计

在 AI 脚本生成页面，您可以查看以下统计信息：

- **今日生成次数**：当天的脚本生成总数
- **成功率**：生成成功的脚本占比
- **平均生成时间**：每个脚本的平均生成时间
- **最常用语言**：ADB 或 Python 的使用比例
- **模板使用排行**：最受欢迎的模板

### 质量分析

系统会自动分析生成脚本的质量：

- **语法正确率**：语法检查通过的脚本比例
- **安全性评分**：脚本安全性的平均分数
- **最佳实践符合度**：符合编码规范的脚本比例

---

## 🚀 高级功能

### 提示词优化

系统可以自动优化您输入的提示词：

**原始提示词**：
```
登录
```

**优化后的提示词**：
```
测试应用登录功能，包括点击登录按钮、输入用户名和密码、点击确认登录按钮，并验证登录成功状态
```

### 脚本历史记录

系统会保存您的生成历史：

- 查看历史生成记录
- 重新使用之前的提示词
- 对比不同版本的生成结果
- 收藏常用的脚本

### 团队协作

- 分享脚本模板给团队成员
- 导出生成的脚本
- 批量导入测试用例
- 团队使用统计分析

---

## 📞 技术支持

### 获取帮助

如果您在使用 AI 功能时遇到问题，可以通过以下方式获取帮助：

1. **在线文档**：查看本使用指南和 FAQ
2. **技术支持**：发送邮件至 support@adbweb.com
3. **社区论坛**：访问 https://forum.adbweb.com
4. **微信群**：扫码加入技术交流群

### 反馈建议

我们欢迎您的反馈和建议：

- **功能建议**：新功能需求和改进建议
- **Bug 报告**：发现的问题和错误
- **使用体验**：使用过程中的感受和建议

---

## 📚 相关文档

- [ADBweb 项目 README](../README.md)
- [API 接口文档](./API接口文档.md)
- [脚本模板开发指南](./AI_SCRIPT_TEMPLATES.md)
- [测试套件使用指南](../tests/README.md)

---

**文档维护**: 本文档由 ADBweb 团队维护，定期更新  
**最后更新**: 2026-02-26  
**版本**: v2.0.0