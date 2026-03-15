# Python语法错误修复指南

## 🐛 常见错误：SyntaxError: expected 'except' or 'finally' block

### 错误原因
Python的`try`语句必须配合`except`或`finally`使用，不能单独存在。

### 错误示例
```python
def test():
    try:
        print("test")
    # 缺少except或finally - 语法错误！
```

### 正确写法
```python
def test():
    try:
        print("test")
    except Exception as e:
        print(f"错误: {e}")
```

## 🔧 如何修复AI生成的脚本

### 方法1：重新生成脚本（推荐）
1. 删除有问题的脚本
2. 使用AI脚本生成器重新生成
3. 新版本提示词已修复此问题

### 方法2：手动修复脚本
如果脚本中有不完整的try语句，添加except块：

**修复前**
```python
def download_app():
    try:
        print("开始下载")
        # ... 你的代码
    # 缺少except
```

**修复后**
```python
def download_app():
    try:
        print("开始下载")
        # ... 你的代码
    except Exception as e:
        print(f"执行失败: {e}")
        return False
```

## 📋 完整的脚本模板

```python
# -*- coding: utf-8 -*-
import uiautomator2 as u2
import time
import sys
import io

# Windows系统UTF-8编码设置
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def take_screenshot(d, step_name):
    """每个步骤后截图"""
    timestamp = int(time.time() * 1000)
    filename = f"step_{step_name}_{timestamp}.png"
    d.screenshot(filename)
    print(f"SCREENSHOT:{filename}")
    return filename

def main():
    try:
        # 连接设备
        d = u2.connect()
        print("设备连接成功")
        
        # 步骤1：你的操作
        print("[步骤1] 操作描述...")
        # ... 你的代码
        print("[步骤1] 完成")
        take_screenshot(d, "01_step_name")
        
        # 更多步骤...
        
        return True
        
    except Exception as e:
        print(f"执行失败: {e}")
        try:
            take_screenshot(d, "error")
        except:
            pass
        return False

if __name__ == "__main__":
    main()
```

## ✅ 检查清单

在执行脚本前，检查：
- [ ] 每个`try`后面都有`except`或`finally`
- [ ] 缩进正确（Python对缩进敏感）
- [ ] 没有多余的空行在try-except之间
- [ ] except块中有实际的错误处理代码

## 🎯 提示词已优化

最新版本的提示词已经添加了明确的异常处理规范：
- ✅ 强调try-except必须完整
- ✅ 提供完整的模板
- ✅ 添加语法检查提示

重新生成的脚本将不会再出现此问题。

## 💡 快速解决方案

如果遇到此错误：
1. 在脚本列表中找到失败的脚本
2. 点击"删除"
3. 重新使用AI生成器生成脚本
4. 新脚本将包含完整的try-except结构

---

**更新时间**：2026-03-15  
**版本**：v2.7.1
