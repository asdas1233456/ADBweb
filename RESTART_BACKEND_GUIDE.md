# 🔄 后端服务重启指南

## ⚠️ 重要提示

AI元素定位器的路由已经添加到代码中，但需要**重启后端服务**才能生效！

## 📋 问题现象

- 前端上传截图时显示"上传失败"
- API返回404错误
- 访问 `/api/v1/ai-element-locator/*` 返回 `{"detail":"Not Found"}`

## ✅ 解决方案

### 方法1：重启后端服务（推荐）

#### Windows:

1. **停止当前服务**
   - 在运行后端的终端按 `Ctrl + C`
   - 或者找到进程并结束：
     ```bash
     # 查找进程
     netstat -ano | findstr :8000
     
     # 结束进程（替换PID为实际进程ID）
     taskkill /F /PID <PID>
     ```

2. **重新启动服务**
   ```bash
   cd ADBweb/backend
   python main.py
   ```

3. **验证服务**
   ```bash
   # 测试API是否可用
   curl http://localhost:8000/api/v1/ai-element-locator/capabilities
   
   # 或访问API文档
   # 打开浏览器: http://localhost:8000/docs
   # 搜索 "AI元素定位" 标签
   ```

#### Linux/Mac:

1. **停止当前服务**
   ```bash
   # 按 Ctrl + C
   # 或者
   pkill -f "python main.py"
   ```

2. **重新启动服务**
   ```bash
   cd ADBweb/backend
   python main.py
   ```

### 方法2：使用热重载（如果已配置）

如果后端使用了 `--reload` 参数启动，修改代码后会自动重载：

```bash
cd ADBweb/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 验证步骤

### 1. 测试API端点

```bash
cd ADBweb/backend
python test_upload_api.py
```

预期输出：
```
✅ 上传成功
✅ 文件已保存
✅ 分析成功
✅ 查询成功
```

### 2. 访问API文档

打开浏览器访问：`http://localhost:8000/docs`

应该能看到：
- **AI元素定位** 标签
- 9个API端点：
  - POST /api/v1/ai-element-locator/upload-screenshot
  - POST /api/v1/ai-element-locator/analyze
  - POST /api/v1/ai-element-locator/find-element
  - POST /api/v1/ai-element-locator/get-coordinates
  - POST /api/v1/ai-element-locator/generate-command
  - POST /api/v1/ai-element-locator/visualize
  - POST /api/v1/ai-element-locator/smart-click
  - GET /api/v1/ai-element-locator/capabilities
  - GET /api/v1/ai-element-locator/examples

### 3. 测试前端页面

1. 确保前端服务正在运行：
   ```bash
   cd ADBweb
   npm run dev
   ```

2. 访问：`http://localhost:5173/ai-element-locator`

3. 上传一张截图，应该能成功上传并分析

## 🐛 常见问题

### Q1: 重启后还是404

**解决方案**：
1. 检查 `main.py` 中是否有导入错误
2. 查看终端输出的错误信息
3. 确认 `app/api/ai_element_locator.py` 文件存在

### Q2: 导入错误

**可能的错误**：
```python
ImportError: cannot import name 'router' from 'app.api.ai_element_locator'
```

**解决方案**：
检查 `app/api/ai_element_locator.py` 文件是否正确定义了 `router`：
```python
router = APIRouter(prefix="/ai-element-locator", tags=["AI元素定位"])
```

### Q3: 端口被占用

**错误信息**：
```
OSError: [Errno 98] Address already in use
```

**解决方案**：
```bash
# Windows
netstat -ano | findstr :8000
taskkill /F /PID <PID>

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

## 📝 完整启动流程

### 1. 停止所有服务

```bash
# 停止后端（Ctrl + C 或 kill进程）
# 停止前端（Ctrl + C）
```

### 2. 启动后端

```bash
cd ADBweb/backend
python main.py
```

等待看到：
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. 启动前端

```bash
cd ADBweb
npm run dev
```

等待看到：
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

### 4. 访问应用

打开浏览器：`http://localhost:5173/ai-element-locator`

## ✅ 成功标志

重启成功后，你应该能够：

1. ✅ 访问 API 文档看到 AI元素定位 标签
2. ✅ 前端页面能够上传截图
3. ✅ 上传后自动分析并显示结果
4. ✅ 能够查找元素并获取坐标
5. ✅ 能够生成 ADB 命令

## 🎉 开始使用

重启完成后，参考以下文档开始使用：

- [快速启动指南](./AI_ELEMENT_LOCATOR_QUICKSTART.md)
- [使用指南](./docs/AI元素定位器使用指南.md)
- [实现总结](./AI_ELEMENT_LOCATOR_SUMMARY.md)

---

**如果还有问题，请检查：**
1. Python 依赖是否完整：`pip install -r requirements.txt`
2. 文件是否都已保存
3. 是否在正确的目录运行命令
4. 终端是否有错误信息输出
