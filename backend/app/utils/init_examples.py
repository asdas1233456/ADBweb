"""
初始化示例库数据
"""
from sqlmodel import Session, select
from app.models.example import Example, BestPractice, Snippet


def init_examples(db: Session):
    """初始化示例脚本"""
    # 检查是否已有数据
    existing = db.exec(select(Example)).first()
    if existing:
        return
    
    examples = [
        {
            "title": "基础点击操作",
            "description": "演示如何使用 UIAutomator2 进行基础的点击操作",
            "category": "UI自动化",
            "difficulty": "beginner",
            "script_type": "python",
            "code": '''import uiautomator2 as u2

# 连接设备
d = u2.connect()

# 通过文本点击
d(text="登录").click()

# 通过资源ID点击
d(resourceId="com.example:id/button").click()

# 通过描述点击
d(description="提交按钮").click()

print("点击操作完成")''',
            "tags": "点击,基础,UIAutomator2",
            "use_case": "适用于需要模拟用户点击操作的场景",
            "prerequisites": "已安装 uiautomator2 库",
            "expected_result": "成功点击指定元素",
            "author": "系统",
            "is_featured": True
        },
        {
            "title": "文本输入操作",
            "description": "演示如何在输入框中输入文本",
            "category": "UI自动化",
            "difficulty": "beginner",
            "script_type": "python",
            "code": '''import uiautomator2 as u2

# 连接设备
d = u2.connect()

# 清空输入框并输入文本
d(resourceId="com.example:id/username").set_text("test@example.com")

# 追加文本
d(resourceId="com.example:id/password").send_keys("password123")

# 清空输入框
d(resourceId="com.example:id/search").clear_text()

print("文本输入完成")''',
            "tags": "输入,文本,表单",
            "use_case": "适用于登录、搜索、表单填写等场景",
            "prerequisites": "已安装 uiautomator2 库",
            "expected_result": "成功在输入框中输入文本",
            "author": "系统",
            "is_featured": True
        },
        {
            "title": "滑动操作",
            "description": "演示各种滑动操作",
            "category": "UI自动化",
            "difficulty": "intermediate",
            "script_type": "python",
            "code": '''import uiautomator2 as u2

# 连接设备
d = u2.connect()

# 向上滑动
d.swipe(500, 1500, 500, 500, 0.1)

# 向下滑动
d.swipe(500, 500, 500, 1500, 0.1)

# 向左滑动
d.swipe(800, 1000, 200, 1000, 0.1)

# 向右滑动
d.swipe(200, 1000, 800, 1000, 0.1)

# 滑动到元素可见
d(text="目标元素").scroll.to()

print("滑动操作完成")''',
            "tags": "滑动,手势,列表",
            "use_case": "适用于列表滚动、页面切换等场景",
            "prerequisites": "已安装 uiautomator2 库",
            "expected_result": "成功执行滑动操作",
            "author": "系统"
        },
        {
            "title": "等待元素出现",
            "description": "演示如何等待元素出现或消失",
            "category": "UI自动化",
            "difficulty": "intermediate",
            "script_type": "python",
            "code": '''import uiautomator2 as u2

# 连接设备
d = u2.connect()

# 等待元素出现（最多等待10秒）
d(text="加载完成").wait(timeout=10)

# 等待元素消失
d(text="加载中...").wait_gone(timeout=10)

# 检查元素是否存在
if d(text="登录").exists():
    print("登录按钮存在")
else:
    print("登录按钮不存在")

# 等待元素出现并点击
if d(text="确定").wait(timeout=5):
    d(text="确定").click()
    print("点击成功")
else:
    print("元素未出现")''',
            "tags": "等待,同步,超时",
            "use_case": "适用于需要等待页面加载或元素出现的场景",
            "prerequisites": "已安装 uiautomator2 库",
            "expected_result": "成功等待元素状态变化",
            "author": "系统",
            "is_featured": True
        },
        {
            "title": "截图操作",
            "description": "演示如何截取屏幕截图",
            "category": "UI自动化",
            "difficulty": "beginner",
            "script_type": "python",
            "code": '''import uiautomator2 as u2
from datetime import datetime

# 连接设备
d = u2.connect()

# 截取全屏
screenshot_path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
d.screenshot(screenshot_path)
print(f"截图已保存: {screenshot_path}")

# 截取指定元素
element = d(resourceId="com.example:id/image")
if element.exists():
    element.screenshot(f"element_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    print("元素截图已保存")''',
            "tags": "截图,图片,保存",
            "use_case": "适用于测试结果记录、问题定位等场景",
            "prerequisites": "已安装 uiautomator2 库",
            "expected_result": "成功保存截图文件",
            "author": "系统"
        },
        {
            "title": "应用启动和关闭",
            "description": "演示如何启动和关闭应用",
            "category": "应用管理",
            "difficulty": "beginner",
            "script_type": "python",
            "code": '''import uiautomator2 as u2
import time

# 连接设备
d = u2.connect()

# 启动应用
package_name = "com.example.app"
d.app_start(package_name)
print(f"已启动应用: {package_name}")

# 等待应用启动
time.sleep(2)

# 获取当前应用信息
current_app = d.app_current()
print(f"当前应用: {current_app}")

# 停止应用
d.app_stop(package_name)
print(f"已停止应用: {package_name}")

# 清除应用数据
d.app_clear(package_name)
print(f"已清除应用数据: {package_name}")''',
            "tags": "应用,启动,关闭",
            "use_case": "适用于应用测试的准备和清理工作",
            "prerequisites": "已安装 uiautomator2 库",
            "expected_result": "成功控制应用的启动和关闭",
            "author": "系统"
        }
    ]
    
    for example_data in examples:
        example = Example(**example_data)
        db.add(example)
    
    db.commit()
    print(f"[INFO] 已初始化 {len(examples)} 个示例脚本")


def init_best_practices(db: Session):
    """初始化最佳实践"""
    # 检查是否已有数据
    existing = db.exec(select(BestPractice)).first()
    if existing:
        return
    
    practices = [
        {
            "title": "脚本结构设计最佳实践",
            "category": "代码规范",
            "content": '''# 脚本结构设计最佳实践

## 1. 模块化设计

将脚本分解为独立的函数或类，每个函数只负责一个功能。

## 2. 配置分离

将配置信息（如包名、超时时间等）提取到配置文件或常量中。

## 3. 错误处理

使用 try-except 捕获异常，避免脚本因单个错误而中断。

## 4. 日志记录

记录关键操作和错误信息，便于问题定位。

## 5. 可维护性

使用清晰的命名、适当的注释和文档字符串。''',
            "code_examples": '''[
    {
        "title": "模块化示例",
        "code": "def login(d, username, password):\\n    d(resourceId=\\"username\\").set_text(username)\\n    d(resourceId=\\"password\\").set_text(password)\\n    d(text=\\"登录\\").click()"
    }
]''',
            "dos": '''["使用函数封装重复代码", "添加适当的注释", "使用有意义的变量名", "处理异常情况"]''',
            "donts": '''["硬编码配置信息", "忽略错误处理", "使用魔法数字", "编写过长的函数"]''',
            "tips": '''["使用 Page Object 模式", "编写可重用的工具函数", "定期重构代码"]''',
            "difficulty": "intermediate",
            "tags": "代码规范,架构,设计模式",
            "author": "系统"
        },
        {
            "title": "等待策略优化",
            "category": "性能优化",
            "content": '''# 等待策略优化

## 1. 显式等待优于隐式等待

使用 wait() 方法明确等待特定条件，而不是使用 time.sleep()。

## 2. 合理设置超时时间

根据实际情况设置超时时间，避免过长或过短。

## 3. 使用条件等待

等待特定条件满足，而不是固定时间。

## 4. 避免过度等待

只在必要时使用等待，减少测试执行时间。''',
            "code_examples": '''[
    {
        "title": "显式等待示例",
        "code": "# 好的做法\\nif d(text=\\"加载完成\\").wait(timeout=10):\\n    print(\\"页面加载完成\\")\\n\\n# 不好的做法\\nimport time\\ntime.sleep(10)"
    }
]''',
            "dos": '''["使用显式等待", "设置合理的超时时间", "检查等待结果"]''',
            "donts": '''["使用固定延时", "设置过长的超时", "忽略等待失败"]''',
            "tips": '''["使用 wait_gone() 等待元素消失", "结合 exists() 检查元素状态"]''',
            "difficulty": "intermediate",
            "tags": "性能,等待,优化",
            "author": "系统"
        }
    ]
    
    for practice_data in practices:
        practice = BestPractice(**practice_data)
        db.add(practice)
    
    db.commit()
    print(f"[INFO] 已初始化 {len(practices)} 个最佳实践")


def init_snippets(db: Session):
    """初始化代码片段"""
    # 检查是否已有数据
    existing = db.exec(select(Snippet)).first()
    if existing:
        return
    
    snippets = [
        {
            "title": "连接设备",
            "description": "连接到 Android 设备",
            "language": "python",
            "code": "import uiautomator2 as u2\nd = u2.connect()",
            "category": "初始化",
            "tags": "连接,设备,初始化",
            "shortcut": "conn",
            "author": "系统"
        },
        {
            "title": "通过文本定位",
            "description": "通过文本内容定位元素",
            "language": "python",
            "code": 'd(text="按钮文本")',
            "category": "元素定位",
            "tags": "定位,文本",
            "shortcut": "text",
            "author": "系统"
        },
        {
            "title": "通过资源ID定位",
            "description": "通过资源ID定位元素",
            "language": "python",
            "code": 'd(resourceId="com.example:id/button")',
            "category": "元素定位",
            "tags": "定位,ID",
            "shortcut": "rid",
            "author": "系统"
        },
        {
            "title": "等待元素出现",
            "description": "等待元素出现，最多等待指定秒数",
            "language": "python",
            "code": 'd(text="元素").wait(timeout=10)',
            "category": "等待操作",
            "tags": "等待,同步",
            "shortcut": "wait",
            "author": "系统"
        },
        {
            "title": "等待元素消失",
            "description": "等待元素消失，最多等待指定秒数",
            "language": "python",
            "code": 'd(text="加载中").wait_gone(timeout=10)',
            "category": "等待操作",
            "tags": "等待,消失",
            "shortcut": "waitgone",
            "author": "系统"
        },
        {
            "title": "检查元素存在",
            "description": "检查元素是否存在",
            "language": "python",
            "code": 'if d(text="按钮").exists():\n    print("元素存在")',
            "category": "断言验证",
            "tags": "验证,存在",
            "shortcut": "exists",
            "author": "系统"
        },
        {
            "title": "获取元素文本",
            "description": "获取元素的文本内容",
            "language": "python",
            "code": 'text = d(resourceId="result").get_text()',
            "category": "元素操作",
            "tags": "文本,获取",
            "shortcut": "gettext",
            "author": "系统"
        },
        {
            "title": "截取屏幕",
            "description": "截取当前屏幕并保存",
            "language": "python",
            "code": 'd.screenshot("screenshot.png")',
            "category": "截图操作",
            "tags": "截图,保存",
            "shortcut": "screenshot",
            "author": "系统"
        },
        {
            "title": "滑动屏幕",
            "description": "从一个坐标滑动到另一个坐标",
            "language": "python",
            "code": "d.swipe(500, 1500, 500, 500, 0.1)",
            "category": "手势操作",
            "tags": "滑动,手势",
            "shortcut": "swipe",
            "author": "系统"
        },
        {
            "title": "启动应用",
            "description": "启动指定包名的应用",
            "language": "python",
            "code": 'd.app_start("com.example.app")',
            "category": "应用管理",
            "tags": "启动,应用",
            "shortcut": "appstart",
            "author": "系统"
        }
    ]
    
    for snippet_data in snippets:
        snippet = Snippet(**snippet_data)
        db.add(snippet)
    
    db.commit()
    print(f"[INFO] 已初始化 {len(snippets)} 个代码片段")


def init_all_examples(db: Session):
    """初始化所有示例库数据"""
    init_examples(db)
    init_best_practices(db)
    init_snippets(db)
