# 提示词更新日志

## 2026-03-15 - 修复输出格式和应用识别问题

### 问题
1. AI生成的是JSON格式而不是直接的Python/Bash代码
2. "相机"被识别为控件而不是应用
3. 提示词优化功能过度复杂化用户需求

### 修复内容

#### 1. 修改输出格式
- **之前**: 要求返回JSON格式 `{"script": "...", "language": "...", ...}`
- **现在**: 直接返回可执行的脚本代码
- **影响文件**: 
  - `python_script_generation.txt`
  - `adb_script_generation.txt`

#### 2. 添加常用应用识别
在提示词中添加常用应用包名映射：
- 相机: com.android.camera
- 设置: com.android.settings
- 浏览器: com.android.chrome
- 联系人: com.android.contacts
- 短信: com.android.mms

#### 3. 优化提示词优化逻辑
- 添加应用名称识别规则
- 保持用户原意，不过度解读
- 提供更实用的优化建议

**示例**:
- 输入: "相机预览帧率查看"
- 优化后: "启动相机应用，查看预览界面的帧率信息"
- 改进点: 识别相机为应用而非控件

#### 4. 更新应用包名映射
在 `ai_script_generator.py` 中添加：
- 相机/摄像头
- 设置
- 浏览器/Chrome
- 联系人
- 短信
- 电话/拨号

### 兼容性
代码已有兼容处理，同时支持：
- 新格式：直接返回脚本
- 旧格式：JSON包裹的脚本
- 自动清理markdown代码块标记

### 测试建议
1. 测试"相机预览帧率查看"等包含应用名的需求
2. 验证生成的是可执行代码而不是JSON
3. 检查提示词优化是否合理


## 2026-03-15 - 步骤日志输出优化

### 问题
实时监控需要清晰的步骤INFO输出，方便用户查看执行进度。

### 优化内容

#### 1. 添加步骤日志规范
在核心规则中明确要求：
- 每个步骤前输出：`print("[步骤X] 操作描述...")`
- 每个步骤后输出：`print("[步骤X] 完成")`
- 避免使用特殊符号（✓✗），使用文字描述

#### 2. Python脚本示例
```python
print("[步骤1] 启动微信应用...")
d.app_start("com.tencent.mm")
time.sleep(3)
print("[步骤1] 完成")
take_screenshot(d, "01_app_started")
```

#### 3. ADB脚本示例
```bash
echo "[步骤1] 启动微信应用..."
adb shell am start -n com.tencent.mm/.ui.LauncherUI
sleep 3
echo "[步骤1] 完成"
take_screenshot "01_app_started"
```

#### 4. 编码问题修复
- 添加UTF-8编码声明：`# -*- coding: utf-8 -*-`
- Windows系统兼容性处理
- 修复截图函数参数（添加设备对象参数d）

### 影响范围
- `python_script_generation.txt` - 添加步骤日志规范和示例
- `adb_script_generation.txt` - 添加步骤日志规范和示例

### 用户体验提升
- ✅ 实时监控左侧显示清晰的步骤日志
- ✅ 每个步骤的开始和完成都有明确提示
- ✅ 日志格式统一，易于阅读
- ✅ 避免编码错误导致的乱码

### 测试建议
1. 生成新脚本，检查是否包含步骤日志
2. 执行脚本，查看实时监控的日志输出
3. 验证日志格式是否清晰易读
