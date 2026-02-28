# 🎯 AI智能元素定位器 - 完整指南

> ADBweb v2.3.1 | 最后更新：2024-02-28

## 📖 目录

1. [功能介绍](#功能介绍)
2. [快速开始](#快速开始)
3. [元素识别](#元素识别)
4. [元素查找](#元素查找)
5. [可视化功能](#可视化功能)
6. [API接口](#api接口)
7. [使用示例](#使用示例)
8. [常见问题](#常见问题)

---

## 1. 功能介绍

AI智能元素定位器结合计算机视觉（OpenCV）和OCR技术（PaddleOCR），自动识别Android应用截图中的UI元素。

### ✨ 核心特性

- 🎯 **自动识别** - 无需手动指定坐标
- 📝 **OCR识别** - 识别按钮文字（准确率>95%）
- 💬 **自然语言** - 支持"蓝色的登录按钮"等描述
- 🔄 **跨设备适配** - 自动适应不同分辨率
- ⚡ **快速响应** - 1-2秒完成识别
- �� **可视化标注** - 编号圆圈标注，智能避免重叠

### 📊 支持的元素（12种类型 + 9种状态）

**元素类型**：按钮、输入框、文本、复选框、单选按钮、开关、滑块等  
**元素状态**：正常、选中、未选中、启用、禁用、聚焦等

---

## 2. 快速开始

### 步骤1：上传截图

在前端界面点击"选择截图文件"，或使用API：

```python
import requests

with open("screenshot.png", "rb") as f:
    files = {"file": ("screenshot.png", f, "image/png")}
    response = requests.post(
        "http://localhost:8000/api/v1/ai-element-locator/upload-screenshot",
        files=files
    )
image_path = response.json()["data"]["file_path"]
```

### 步骤2：分析截图

```python
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/analyze",
    json={"image_path": image_path}
)
elements = response.json()["data"]["elements"]
print(f"识别到 {len(elements)} 个元素")
```

### 步骤3：查找元素

```python
# 方法1：按文本查找
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/find-element",
    json={"image_path": image_path, "query": "登录", "method": "text"}
)

# 方法2：自然语言描述
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/find-element",
    json={"image_path": image_path, "query": "蓝色的登录按钮", "method": "description"}
)
```

### 步骤4：获取坐标并执行

```python
# 获取坐标
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/get-coordinates",
    json={"image_path": image_path, "query": "登录"}
)
coords = response.json()["data"]

# 生成ADB命令
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/generate-command",
    json={"image_path": image_path, "action": "click", "query": "登录"}
)
command = response.json()["data"]["command"]
print(f"ADB命令: {command}")

# 执行点击
import subprocess
subprocess.run(command, shell=True)
```

---

## 3. 元素识别

### 3.1 元素类型详解

| 类型 | 检测特征 | 识别方法 |
|------|---------|---------|
| **BUTTON** | 矩形、宽高比0.3-5 | 边缘检测 + 轮廓分析 |
| **INPUT** | 长条形、宽高比>2 | 形状检测 |
| **TEXT** | 文字内容 | OCR识别 |
| **CHECKBOX** | 正方形、宽高比0.8-1.2 | 形状检测 + 亮度判断 |
| **RADIO** | 圆形 | 霍夫圆检测 + 亮度判断 |
| **SWITCH** | 椭圆形、宽高比1.5-3 | 形状检测 + 颜色判断 |
| **SLIDER** | 长条形、宽高比>5 | 形状检测 |

### 3.2 状态识别

**复选框状态**：
- 选中：内部亮度 < 200（较暗）
- 未选中：内部亮度 >= 200（较亮）

**开关状态**：
- 开启：蓝色/绿色（RGB值>150）
- 关闭：灰色

**单选按钮状态**：
- 选中：圆形内部有填充（亮度<200）
- 未选中：圆形内部空白

---

## 4. 元素查找

### 4.1 文本匹配

精确匹配元素上的文字：

```python
find_element(image_path, "登录", method="text")
```

### 4.2 自然语言描述

支持颜色、位置、类型描述：

```python
find_element(image_path, "蓝色的提交按钮", method="description")
find_element(image_path, "顶部的搜索框", method="description")
```

### 4.3 相对位置查找 ⭐

根据锚点元素查找相对位置的元素：

```python
# 查找"登录"按钮右边的元素
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/find-relative",
    json={
        "image_path": image_path,
        "anchor_query": "登录",
        "direction": "right",  # left, right, top, bottom, above, below
        "distance_threshold": 200
    }
)
```

### 4.4 区域查找 ⭐

在指定区域内查找元素：

```python
# 在顶部区域查找按钮
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/find-in-region",
    json={
        "image_path": image_path,
        "region": [0, 0, 1080, 200],  # [x1, y1, x2, y2]
        "element_type": "button"
    }
)
```

### 4.5 状态筛选 ⭐

按元素状态筛选：

```python
# 查找所有选中的复选框
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/filter-by-state",
    json={
        "image_path": image_path,
        "element_type": "checkbox",
        "state": "checked"
    }
)
```

---

## 5. 可视化功能

### 5.1 标注方式

- **编号圆圈**：在元素中心显示编号（...）
- **颜色边框**：不同类型使用不同颜色
- **文字标签**：显示元素类型和文本（可选）
- **统计图例**：左上角显示元素类型统计

### 5.2 可配置选项

```python
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/visualize",
    json={
        "image_path": image_path,
        "show_labels": True,      # 是否显示文字标签
        "show_center": False,     # 是否显示中心点
        "min_confidence": 0.0     # 最小置信度阈值
    }
)
```

### 5.3 颜色方案

| 元素类型 | 颜色 | 色值 |
|---------|------|------|
| BUTTON | 红色 | #FF4444 |
| INPUT | 蓝色 | #4444FF |
| TEXT | 绿色 | #44FF44 |
| CHECKBOX | 紫色 | #FF44FF |
| RADIO | 橙色 | #FFAA00 |
| SWITCH | 青色 | #00FFFF |
| SLIDER | 深橙色 | #FF8800 |

---

## 6. API接口

### 6.1 基础接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /upload-screenshot | POST | 上传截图 |
| /analyze | POST | 分析截图 |
| /find-element | POST | 查找元素 |
| /get-coordinates | POST | 获取坐标 |
| /generate-command | POST | 生成ADB命令 |
| /visualize | POST | 可视化标注 |
| /smart-click | POST | 智能点击 |

### 6.2 增强接口 ⭐

| 接口 | 方法 | 说明 |
|------|------|------|
| /find-relative | POST | 相对位置查找 |
| /find-in-region | POST | 区域查找 |
| /filter-by-state | POST | 状态筛选 |
| /element-types | GET | 获取元素类型列表 |
| /element-states | GET | 获取元素状态列表 |

---

## 7. 使用示例

### 示例1：自动化登录

```python
def auto_login(username, password):
    # 1. 获取截图
    screenshot = capture_screenshot()
    image_path = upload_screenshot(screenshot)
    
    # 2. 点击用户名输入框
    smart_click(image_path, "用户名")
    adb_input_text(username)
    
    # 3. 点击密码输入框
    smart_click(image_path, "密码")
    adb_input_text(password)
    
    # 4. 勾选"记住密码"
    smart_click(image_path, "记住密码")
    
    # 5. 点击登录按钮
    smart_click(image_path, "登录")
```

### 示例2：表单自动填写

```python
def auto_fill_form(image_path):
    # 1. 查找用户名输入框并填写
    smart_click(image_path, "用户名")
    # 输入...
    
    # 2. 查找用户名下方的密码输入框
    response = requests.post(
        f"{BASE_URL}/find-relative",
        json={
            "image_path": image_path,
            "anchor_query": "用户名",
            "direction": "below"
        }
    )
    # 点击密码输入框...
    
    # 3. 勾选所有复选框
    response = requests.post(
        f"{BASE_URL}/filter-by-state",
        json={
            "image_path": image_path,
            "element_type": "checkbox",
            "state": "unchecked"
        }
    )
    for checkbox in response.json()["data"]["elements"]:
        # 点击复选框...
        pass
```

### 示例3：跨设备测试

```python
def test_on_multiple_devices(devices):
    for device in devices:
        set_current_device(device)
        screenshot = capture_screenshot()
        image_path = upload_screenshot(screenshot)
        
        # 使用相同的查询，自动适配不同分辨率
        smart_click(image_path, "开始测试")
        run_test_cases()
```

---

## 8. 常见问题

### Q1: 为什么识别不到元素？

**可能原因**：
- 截图质量差（模糊、压缩）
- 元素太小或太大
- 元素颜色对比度低

**解决方案**：
1. 使用高质量截图（推荐1080p）
2. 确保元素清晰可见
3. 使用可视化功能查看识别结果

### Q2: OCR识别不准确怎么办？

**解决方案**：
1. 确保截图清晰
2. 检查文字是否水平（倾斜会降低准确率）
3. 避免使用特殊字体
4. 适当放大截图

### Q3: 找不到我要的元素怎么办？

**解决方案**：
1. 尝试不同的查询条件（文本、描述、相对位置）
2. 使用可视化功能查看识别结果
3. 检查截图是否完整
4. 使用区域查找缩小范围

### Q4: 坐标不准确怎么办？

**解决方案**：
1. 使用可视化功能查看标注
2. 尝试重新上传截图
3. 检查元素边界是否清晰

### Q5: 性能较慢怎么办？

**解决方案**：
1. 首次使用会下载模型（~5秒），后续会快很多
2. 复用已上传的截图
3. 使用批量分析而不是多次单独查询
4. 考虑降低截图分辨率

---

## 📊 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 上传截图 | <500ms | 取决于网络和文件大小 |
| 分析截图 | 1-2秒 | 首次需下载模型（~5秒） |
| 查找元素 | <100ms | 基于已分析结果 |
| 生成命令 | <50ms | 纯计算 |
| 智能点击 | 2-3秒 | 包含分析+执行 |
| OCR识别准确率 | >95% | 标准中文 |
| 元素检测准确率 | >90% | 标准UI设计 |

---

## 🔧 技术实现

### 技术栈

- **计算机视觉**：OpenCV 4.x
- **OCR识别**：PaddleOCR 2.7.3 + PaddlePaddle 2.6.2
- **图像处理**：Pillow, NumPy
- **后端框架**：FastAPI
- **前端框架**：React + TypeScript

### 核心算法

1. **边缘检测**：Canny算法
2. **轮廓分析**：findContours
3. **圆形检测**：霍夫圆变换
4. **文字识别**：PaddleOCR
5. **状态判断**：亮度分析、颜色分析

---

## 📚 相关文档

- [项目README](./README.md)
- [Docker部署指南](./DOCKER_部署注意事项_中文版.md)
- [OCR安装报告](./OCR_INSTALLATION_COMPLETE.md)
- [后端重启指南](./RESTART_BACKEND_GUIDE.md)
- [API接口文档](./docs/API接口文档.md)

---

## 💡 最佳实践

### 1. 截图质量
- ✅ 使用清晰的截图（推荐1080p）
- ✅ 确保文字清晰可见
- ❌ 不要使用过小的截图（<720p）

### 2. 元素查询
- ✅ 使用明确的文本（如"登录"、"确定"）
- ✅ 使用自然语言描述（如"蓝色的登录按钮"）
- ❌ 避免使用模糊的描述（如"那个按钮"）

### 3. 性能优化
- ✅ 复用已上传的截图
- ✅ 批量分析多个元素
- ✅ 缓存识别结果

### 4. 错误处理
- ✅ 添加重试机制
- ✅ 验证操作结果
- ✅ 记录详细日志

---

**祝你使用愉快！** 🎉

如有问题，请查看文档或联系技术支持。
| ENABLED | 启用状态 | 所有元素 |
| DISABLED | 禁用状态 | 所有元素 |
| FOCUSED | 聚焦状态 | input, button |
| LOADING | 加载状态 | button |
| UNKNOWN | 未知状态 | 默认状态 |

---

## 快速开始

### 步骤1：准备环境

确保已安装OCR功能（v2.3.0已默认安装）：

```bash
# 检查安装状态
python -c "import paddleocr; print('✅ PaddleOCR已安装')"
python -c "import cv2; print('✅ OpenCV已安装')"
```

### 步骤2：获取截图

```bash
# 方法1：使用ADB命令
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png

# 方法2：使用设备管理页面的截图功能
# 访问 http://localhost:5173 → 设备管理 → 点击截图按钮
```

### 步骤3：上传截图

在前端界面：
1. 进入"AI元素定位器"页面
2. 点击"选择截图文件"按钮
3. 选择截图文件（支持PNG、JPG格式）
4. 系统自动上传并分析

### 步骤4：查看分析结果

上传成功后，你会看到：
- **截图预览**：左侧显示原始截图
- **分析统计**：识别元素总数、按钮数量、输入框数量
- **元素列表**：表格显示所有识别的元素详情

### 步骤5：查找元素

切换到"元素查找"标签页：
1. 输入查询条件（如"登录"、"蓝色的提交按钮"）
2. 选择查找方法（自动/文本/描述）
3. 点击"查找元素"按钮
4. 获取坐标和ADB命令

---

## 核心功能

### 1. 元素查找方式

#### 1.1 文本匹配
精确匹配元素上的文字内容

```python
# API调用
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/find-element",
    json={
        "image_path": "screenshot.png",
        "query": "登录",
        "method": "text"
    }
)
```

#### 1.2 自然语言描述
支持颜色、位置等自然语言描述

```python
# API调用
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/find-element",
    json={
        "image_path": "screenshot.png",
        "query": "蓝色的登录按钮",
        "method": "description"
    }
)
```

#### 1.3 相对位置查找 ⭐新增
根据锚点元素查找其相对位置的元素

**支持的方向**：
- left/左边/左侧
- right/右边/右侧
- top/above/上方/上面
- bottom/below/下方/下面

```python
# 查找"登录"按钮右边的元素
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/find-relative",
    json={
        "image_path": "screenshot.png",
        "anchor_query": "登录",
        "direction": "right",
        "distance_threshold": 200
    }
)
```

#### 1.4 区域查找 ⭐新增
在指定矩形区域内查找元素

```python
# 在顶部区域查找按钮
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/find-in-region",
    json={
        "image_path": "screenshot.png",
        "region": [0, 0, 800, 400],  # [x1, y1, x2, y2]
        "element_type": "button"
    }
)
```

#### 1.5 状态筛选 ⭐新增
按元素状态筛选

```python
# 查找所有选中的复选框
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/filter-by-state",
    json={
        "image_path": "screenshot.png",
        "element_type": "checkbox",
        "state": "checked"
    }
)
```

### 2. 可视化功能 ⭐优化

#### 2.1 标注方式
- **编号圆圈**：在元素中心显示清晰编号
- **颜色边框**：不同类型使用不同颜色
- **文字标签**：显示元素类型和文本（可选）
- **统计图例**：左上角显示元素类型统计

#### 2.2 可配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| show_labels | bool | True | 是否显示文字标签 |
| show_center | bool | False | 是否显示中心点 |
| min_confidence | float | 0.0 | 最小置信度阈值 |

#### 2.3 使用示例

**默认模式（显示标签）**：
```python
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/visualize",
    json={
        "image_path": "screenshot.png",
        "show_labels": True,
        "show_center": False,
        "min_confidence": 0.0
    }
)
```

**简洁模式（不显示标签）**：
```python
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/visualize",
    json={
        "image_path": "screenshot.png",
        "show_labels": False,
        "show_center": True,
        "min_confidence": 0.0
    }
)
```

**过滤模式（高置信度）**：
```python
response = requests.post(
    "http://localhost:8000/api/v1/ai-element-locator/visualize",
    json={
        "image_path": "screenshot.png",
        "show_labels": True,
        "show_center": False,
        "min_confidence": 0.7  # 只显示置信度>0.7的元素
    }
)
```

#### 2.4 颜色方案

| 元素类型 | 颜色 | 色值 |
|---------|------|------|
| BUTTON | 红色 | #FF4444 |
| INPUT | 蓝色 | #4444FF |
| TEXT | 绿色 | #44FF44 |
| CHECKBOX | 紫色 | #FF44FF |
| RADIO | 橙色 | #FFAA00 |
| SWITCH | 青色 | #00FFFF |
| SLIDER | 深橙色 | #FF8800 |

---

## API接口

### 1. 上传截图
```http
POST /api/v1/ai-element-locator/upload-screenshot
Content-Type: multipart/form-data

file: <image_file>
```

**响应**：
```json
{
  "code": 200,
  "message": "截图上传成功",
  "data": {
    "file_path": "uploads/screenshots/ai_analysis/screenshot_xxx.png",
    "file_size": 123456
  }
}
```

### 2. 分析截图
```http
POST /api/v1/ai-element-locator/analyze
Content-Type: application/json

{
  "image_path": "uploads/screenshots/xxx.png"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "分析完成",
  "data": {
    "elements": [
      {
        "type": "button",
        "text": "登录",
        "confidence": 0.95,
        "center": [540, 850],
        "bbox": [400, 800, 680, 900],
        "state": "normal"
      }
    ],
    "statistics": {
      "total": 15,
      "button": 5,
      "input": 3,
      "text": 7
    }
  }
}
```

### 3. 查找元素
```http
POST /api/v1/ai-element-locator/find-element
Content-Type: application/json

{
  "image_path": "uploads/screenshots/xxx.png",
  "query": "登录",
  "method": "auto"
}
```

### 4. 获取坐标
```http
POST /api/v1/ai-element-locator/get-coordinates
Content-Type: application/json

{
  "image_path": "uploads/screenshots/xxx.png",
  "query": "登录"
}
```

### 5. 生成ADB命令
```http
POST /api/v1/ai-element-locator/generate-command
Content-Type: application/json

{
  "image_path": "uploads/screenshots/xxx.png",
  "action": "click",
  "query": "登录"
}
```

### 6. 智能点击
```http
POST /api/v1/ai-element-locator/smart-click
Content-Type: application/json

{
  "image_path": "uploads/screenshots/xxx.png",
  "query": "登录"
}
```

### 7. 可视化元素
```http
POST /api/v1/ai-element-locator/visualize
Content-Type: application/json

{
  "image_path": "uploads/screenshots/xxx.png",
  "show_labels": true,
  "show_center": false,
  "min_confidence": 0.0
}
```

### 8. 相对位置查找 ⭐新增
```http
POST /api/v1/ai-element-locator/find-relative
Content-Type: application/json

{
  "image_path": "uploads/screenshots/xxx.png",
  "anchor_query": "登录",
  "direction": "right",
  "distance_threshold": 200
}
```

### 9. 区域查找 ⭐新增
```http
POST /api/v1/ai-element-locator/find-in-region
Content-Type: application/json

{
  "image_path": "uploads/screenshots/xxx.png",
  "region": [0, 0, 800, 400],
  "element_type": "button"
}
```

### 10. 状态筛选 ⭐新增
```http
POST /api/v1/ai-element-locator/filter-by-state
Content-Type: application/json

{
  "image_path": "uploads/screenshots/xxx.png",
  "element_type": "checkbox",
  "state": "checked"
}
```

### 11. 获取元素类型列表
```http
GET /api/v1/ai-element-locator/element-types
```

### 12. 获取元素状态列表
```http
GET /api/v1/ai-element-locator/element-states
```

---

## 使用示例

### 示例1：自动化登录测试

```python
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_login(username, password):
    # 1. 获取截图
    screenshot_path = capture_screenshot()
    
    # 2. 上传截图
    with open(screenshot_path, "rb") as f:
        files = {"file": ("screenshot.png", f, "image/png")}
        response = requests.post(
            f"{BASE_URL}/ai-element-locator/upload-screenshot",
            files=files
        )
    image_path = response.json()["data"]["file_path"]
    
    # 3. 点击用户名输入框
    requests.post(
        f"{BASE_URL}/ai-element-locator/smart-click",
        params={"image_path": image_path, "query": "用户名"}
    )
    time.sleep(0.5)
    
    # 4. 输入用户名
    adb_input_text(username)
    
    # 5. 点击密码输入框
    requests.post(
        f"{BASE_URL}/ai-element-locator/smart-click",
        params={"image_path": image_path, "query": "密码"}
    )
    time.sleep(0.5)
    
    # 6. 输入密码
    adb_input_text(password)
    
    # 7. 点击登录按钮
    requests.post(
        f"{BASE_URL}/ai-element-locator/smart-click",
        params={"image_path": image_path, "query": "登录"}
    )
```

### 示例2：表单自动填写

```python
def auto_fill_form(image_path):
    """自动填写表单"""
    
    # 1. 分析截图
    response = requests.post(
        f"{BASE_URL}/ai-element-locator/analyze",
        json={"image_path": image_path}
    )
    elements = response.json()["data"]["elements"]
    
    # 2. 查找用户名输入框并填写
    response = requests.post(
        f"{BASE_URL}/ai-element-locator/smart-click",
        params={"image_path": image_path, "query": "用户名"}
    )
    adb_input_text("testuser")
    
    # 3. 查找用户名输入框下方的密码输入框
    response = requests.post(
        f"{BASE_URL}/ai-element-locator/find-relative",
        json={
            "image_path": image_path,
            "anchor_query": "用户名",
            "direction": "below"
        }
    )
    password_coords = response.json()["data"]["relative"]["center"]
    adb_tap(password_coords[0], password_coords[1])
    adb_input_text("password123")
    
    # 4. 勾选"记住密码"复选框
    response = requests.post(
        f"{BASE_URL}/ai-element-locator/smart-click",
        params={"image_path": image_path, "query": "记住密码"}
    )
    
    # 5. 点击登录按钮
    response = requests.post(
        f"{BASE_URL}/ai-element-locator/smart-click",
        params={"image_path": image_path, "query": "登录"}
    )
```

### 示例3：设置页面自动化

```python
def auto_configure_settings(image_path):
    """自动配置设置"""
    
    # 1. 查找所有开关
    response = requests.post(
        f"{BASE_URL}/ai-element-locator/analyze",
        json={"image_path": image_path}
    )
    elements = response.json()["data"]["elements"]
    switches = [e for e in elements if e["type"] == "switch"]
    
    # 2. 查找所有开启的开关
    response = requests.post(
        f"{BASE_URL}/ai-element-locator/filter-by-state",
        json={
            "image_path": image_path,
            "element_type": "switch",
            "state": "checked"
        }
    )
    enabled_switches = response.json()["data"]["elements"]
    print(f"已开启 {len(enabled_switches)} 个开关")
    
    # 3. 在设置区域查找所有复选框
    response = requests.post(
        f"{BASE_URL}/ai-element-locator/find-in-region",
        json={
            "image_path": image_path,
            "region": [0, 200, 1080, 1920],
            "element_type": "checkbox"
        }
    )
    checkboxes = response.json()["data"]["elements"]
    
    # 4. 勾选所有未选中的复选框
    for checkbox in checkboxes:
        if checkbox["state"] == "unchecked":
            coords = checkbox["center"]
            adb_tap(coords[0], coords[1])
```

### 示例4：跨设备测试

```python
def test_on_multiple_devices(devices):
    """在多个设备上执行相同测试"""
    for device in devices:
        # 切换到当前设备
        set_current_device(device)
        
        # 获取截图（不同设备分辨率不同）
        screenshot = capture_screenshot()
        image_path = upload_screenshot(screenshot)
        
        # 使用相同的查询，自动适配不同分辨率
        smart_click(image_path, "开始测试")
        
        # 执行测试...
        run_test_cases()
```

---

## 技术实现

### 1. 复选框检测算法

```python
def detect_checkboxes(self, image_path: str) -> List[Dict]:
    """检测复选框"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    checkboxes = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 100 or area > 2000:
            continue
        
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h if h > 0 else 0
        
        # 复选框是正方形（宽高比0.8-1.2）
        if 0.8 < aspect_ratio < 1.2:
            # 检测是否选中（基于内部亮度）
            roi = gray[y:y+h, x:x+w]
            mean_intensity = np.mean(roi)
            is_checked = mean_intensity < 200
            
            checkboxes.append({
                'bbox': (x, y, x + w, y + h),
                'center': (x + w // 2, y + h // 2),
                'checked': is_checked,
                'state': 'checked' if is_checked else 'unchecked'
            })
    
    return checkboxes
```

### 2. 单选按钮检测算法

```python
def detect_radio_buttons(self, image_path: str) -> List[Dict]:
    """检测单选按钮"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 使用霍夫圆检测
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=20,
        param1=50,
        param2=30,
        minRadius=5,
        maxRadius=30
    )
    
    radio_buttons = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            x, y, r = circle
            
            # 检测是否选中（基于内部亮度）
            roi = gray[max(0, y-r):min(gray.shape[0], y+r), 
                      max(0, x-r):min(gray.shape[1], x+r)]
            mean_intensity = np.mean(roi)
            is_selected = mean_intensity < 200
            
            radio_buttons.append({
                'bbox': (x-r, y-r, x+r, y+r),
                'center': (x, y),
                'selected': is_selected,
                'state': 'selected' if is_selected else 'normal'
            })
    
    return radio_buttons
```

### 3. 开关检测算法

```python
def detect_switches(self, image_path: str) -> List[Dict]:
    """检测开关"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    switches = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 500 or area > 5000:
            continue
        
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h if h > 0 else 0
        
        # 开关是椭圆形（宽高比1.5-3）
        if 1.5 < aspect_ratio < 3:
            # 检测是否开启（基于颜色：蓝色/绿色表示开启）
            roi = img[y:y+h, x:x+w]
            mean_color = np.mean(roi, axis=(0, 1))
            is_on = mean_color[2] > 150 or mean_color[1] > 150
            
            switches.append({
                'bbox': (x, y, x + w, y + h),
                'center': (x + w // 2, y + h // 2),
                'on': is_on,
                'state': 'checked' if is_on else 'unchecked'
            })
    
    return switches
```

### 4. 可视化优化

#### 智能标签布局算法
```python
# 记录已使用的标签位置
label_positions = []

for element in elements:
    label_x = x1
    label_y = y1 - 22
    
    # 检查是否与已有标签重叠
    for used_pos in label_positions:
        if abs(label_x - used_pos[0]) < 100 and abs(label_y - used_pos[1]) < 25:
            label_y += 25  # 向下移动避免重叠
    
    # 确保不超出边界
    if label_y < 0:
        label_y = y2 + 5
    
    # 记录位置
    label_positions.append((label_x, label_y))
```

#### 编号圆圈绘制
```python
# 绘制圆圈背景
cx, cy = element.center
radius = 12
draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), 
            fill=color, outline='white', width=2)

# 绘制居中的编号文字
number_text = str(i+1)
text_bbox = draw.textbbox((0, 0), number_text, font=font)
text_width = text_bbox[2] - text_bbox[0]
text_height = text_bbox[3] - text_bbox[1]
text_x = cx - text_width // 2
text_y = cy - text_height // 2
draw.text((text_x, text_y), number_text, fill='white', font=font)
```

---

## 常见问题

### Q1: 为什么识别不到元素？

**可能原因**：
- 截图质量差、模糊
- 元素太小或太大
- 元素颜色对比度低

**解决方案**：
1. 使用高质量截图（推荐1080p）
2. 确保元素清晰可见
3. 尝试不同的查询方式
4. 使用可视化功能查看识别结果

### Q2: 为什么找不到我要的元素？

**可能原因**：
- 查询条件不匹配
- 元素类型不支持
- 元素被遮挡

**解决方案**：
1. 尝试不同的查询条件
2. 使用可视化功能查看识别结果
3. 检查截图是否完整
4. 尝试使用相对位置查找

### Q3: 坐标不准确怎么办？

**可能原因**：
- 元素边界识别不准
- 截图分辨率问题

**解决方案**：
1. 使用可视化功能查看标注
2. 尝试重新上传截图
3. 手动微调坐标

### Q4: OCR识别准确度低怎么办？

**解决方案**：
1. 确保截图清晰（推荐1080p）
2. 检查文字是否水平（倾斜会降低准确率）
3. 避免使用特殊字体
4. 适当放大截图

### Q5: 性能较慢怎么办？

**解决方案**：
1. 首次使用会下载模型（~5秒），后续会快很多
2. 复用已上传的截图
3. 使用批量分析而不是多次单独查询
4. 考虑降低截图分辨率

### Q6: 如何处理动态界面？

**解决方案**：
1. 在操作前重新获取截图
2. 使用智能点击的重试机制
3. 添加适当的等待时间
4. 验证操作结果

---

## 💡 使用技巧

### 技巧1：提高识别准确率

✅ **使用清晰的截图**
- 避免模糊、压缩的图片
- 确保截图完整，没有裁剪
- 推荐分辨率：1080p

✅ **截图包含完整UI**
- 确保要识别的元素完整显示
- 避免元素被遮挡或重叠

### 技巧2：优化查询条件

✅ **文本匹配**
- 使用元素的实际文本
- 例如：按钮上写着"登录"，就搜索"登录"

✅ **描述匹配**
- 使用颜色、位置等描述词
- 例如："蓝色的提交按钮"、"顶部的搜索框"

✅ **自动模式**
- 让系统智能选择
- 适合不确定用哪种方式的情况

### 技巧3：使用可视化功能

点击"可视化元素"按钮：
- 查看所有识别的元素
- 确认识别结果是否准确
- 对比原始截图和标注结果

### 技巧4：性能优化

- ✅ 复用已上传的截图
- ✅ 批量分析多个元素
- ✅ 缓存识别结果
- ❌ 避免频繁上传相同截图

---

## 📊 性能指标

| 操作 | 耗时 | 说明 |
|------|------|------|
| 上传截图 | <500ms | 取决于网络和文件大小 |
| 分析截图 | 1-2秒 | 首次需下载模型（~5秒） |
| 查找元素 | <100ms | 基于已分析结果 |
| 生成命令 | <50ms | 纯计算 |
| 智能点击 | 2-3秒 | 包含分析+执行 |
| OCR识别准确率 | >95% | 标准中文字体 |
| 元素检测准确率 | >90% | 标准UI设计 |

---

## 🎯 应用场景

### 场景1：自动化测试脚本
传统方式需要手动指定坐标，AI方式自动识别

### 场景2：跨设备适配
同一个脚本，适配不同分辨率的设备

### 场景3：界面变更适配
应用改版后，按钮位置变化，无需修改测试脚本

### 场景4：表单自动填写
自动识别输入框位置并填写

### 场景5：设置页面自动化
批量配置开关和复选框

---

## 📚 相关文档

- [项目README](./README.md)
- [OCR安装完成报告](./OCR_INSTALLATION_COMPLETE.md)
- [后端重启指南](./RESTART_BACKEND_GUIDE.md)
- [API接口文档](./docs/API接口文档.md)
- [v2.3.0发布说明](./docs/v2.3.0发布说明.md)

---

## 🔗 快速链接

- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **GitHub**: https://github.com/yourusername/ADBweb

---

<div align="center">

**让Android自动化测试更智能**

ADBweb v2.3.1 | © 2024

</div>
