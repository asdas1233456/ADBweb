"""
脚本模板服务
"""
import json
import re
from typing import List, Dict, Optional
from sqlmodel import Session, select
from app.models.script_template import ScriptTemplate


class TemplateService:
    """脚本模板服务"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_templates(
        self, 
        category: Optional[str] = None,
        language: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: int = 20
    ) -> List[ScriptTemplate]:
        """获取模板列表"""
        query = select(ScriptTemplate).where(ScriptTemplate.is_active == True)
        
        if category:
            query = query.where(ScriptTemplate.category == category)
        if language:
            query = query.where(ScriptTemplate.language == language)
        if keyword:
            query = query.where(
                ScriptTemplate.name.contains(keyword) |
                ScriptTemplate.description.contains(keyword) |
                ScriptTemplate.tags.contains(keyword)
            )
        
        query = query.order_by(ScriptTemplate.usage_count.desc()).limit(limit)
        return self.session.exec(query).all()
    
    def get_template(self, template_id: int) -> Optional[ScriptTemplate]:
        """获取单个模板"""
        return self.session.get(ScriptTemplate, template_id)
    
    def use_template(self, template_id: int, variables: Dict[str, str] = None) -> str:
        """使用模板生成脚本"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError("模板不存在")
        
        # 增加使用次数
        template.usage_count += 1
        self.session.add(template)
        self.session.commit()
        
        # 替换变量
        content = template.template_content
        if variables and template.variables:
            try:
                template_vars = json.loads(template.variables)
                for var_name, var_info in template_vars.items():
                    if var_name in variables:
                        placeholder = f"{{{{{var_name}}}}}"
                        content = content.replace(placeholder, variables[var_name])
            except json.JSONDecodeError:
                pass
        
        return content
    
    def create_template(
        self,
        name: str,
        category: str,
        template_content: str,
        language: str = "adb",
        description: str = None,
        variables: Dict[str, Dict] = None,
        tags: List[str] = None,
        created_by: str = "user"
    ) -> ScriptTemplate:
        """创建模板"""
        template = ScriptTemplate(
            name=name,
            category=category,
            description=description,
            language=language,
            template_content=template_content,
            variables=json.dumps(variables) if variables else None,
            tags=",".join(tags) if tags else None,
            created_by=created_by
        )
        
        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)
        return template
    
    def get_categories(self) -> List[Dict[str, any]]:
        """获取模板分类"""
        query = select(ScriptTemplate.category).distinct().where(ScriptTemplate.is_active == True)
        categories = self.session.exec(query).all()
        
        result = []
        for category in categories:
            count_query = select(ScriptTemplate).where(
                ScriptTemplate.category == category,
                ScriptTemplate.is_active == True
            )
            count = len(self.session.exec(count_query).all())
            result.append({"name": category, "count": count})
        
        return result
    
    def extract_variables(self, content: str) -> Dict[str, Dict]:
        """从模板内容中提取变量"""
        # 匹配 {{variable_name}} 格式的变量
        pattern = r'\{\{(\w+)\}\}'
        variables = {}
        
        for match in re.finditer(pattern, content):
            var_name = match.group(1)
            variables[var_name] = {
                "type": "string",
                "description": f"请输入{var_name}",
                "required": True,
                "default": ""
            }
        
        return variables


def init_builtin_templates(session: Session):
    """初始化内置模板"""
    service = TemplateService(session)
    
    # 检查是否已经初始化
    existing = session.exec(
        select(ScriptTemplate).where(ScriptTemplate.is_builtin == True)
    ).first()
    if existing:
        return
    
    builtin_templates = [
        {
            "name": "应用登录测试",
            "category": "登录测试",
            "language": "adb",
            "description": "通用应用登录测试模板",
            "template_content": """# 启动应用
adb shell am start -n {{package_name}}/{{activity_name}}
adb shell sleep 2

# 点击登录按钮
adb shell input tap {{login_button_x}} {{login_button_y}}
adb shell sleep 1

# 输入用户名
adb shell input tap {{username_x}} {{username_y}}
adb shell sleep 0.5
adb shell input text '{{username}}'
adb shell sleep 0.5

# 输入密码
adb shell input tap {{password_x}} {{password_y}}
adb shell sleep 0.5
adb shell input text '{{password}}'
adb shell sleep 0.5

# 点击确认登录
adb shell input tap {{confirm_x}} {{confirm_y}}
adb shell sleep 3

# 验证登录成功
adb shell screencap -p /sdcard/login_result.png
adb pull /sdcard/login_result.png ./login_result.png""",
            "variables": {
                "package_name": {"type": "string", "description": "应用包名", "required": True, "default": "com.example.app"},
                "activity_name": {"type": "string", "description": "启动Activity", "required": True, "default": ".MainActivity"},
                "login_button_x": {"type": "number", "description": "登录按钮X坐标", "required": True, "default": "540"},
                "login_button_y": {"type": "number", "description": "登录按钮Y坐标", "required": True, "default": "1200"},
                "username_x": {"type": "number", "description": "用户名输入框X坐标", "required": True, "default": "540"},
                "username_y": {"type": "number", "description": "用户名输入框Y坐标", "required": True, "default": "800"},
                "password_x": {"type": "number", "description": "密码输入框X坐标", "required": True, "default": "540"},
                "password_y": {"type": "number", "description": "密码输入框Y坐标", "required": True, "default": "900"},
                "confirm_x": {"type": "number", "description": "确认按钮X坐标", "required": True, "default": "540"},
                "confirm_y": {"type": "number", "description": "确认按钮Y坐标", "required": True, "default": "1000"},
                "username": {"type": "string", "description": "测试用户名", "required": True, "default": "testuser"},
                "password": {"type": "string", "description": "测试密码", "required": True, "default": "password123"}
            },
            "tags": ["登录", "测试", "自动化"]
        },
        {
            "name": "搜索功能测试",
            "category": "功能测试",
            "language": "adb",
            "description": "通用搜索功能测试模板",
            "template_content": """# 点击搜索框
adb shell input tap {{search_box_x}} {{search_box_y}}
adb shell sleep 1

# 输入搜索关键词
adb shell input text '{{search_keyword}}'
adb shell sleep 0.5

# 点击搜索按钮
adb shell input tap {{search_button_x}} {{search_button_y}}
adb shell sleep 2

# 验证搜索结果
adb shell screencap -p /sdcard/search_result.png
adb pull /sdcard/search_result.png ./search_result.png

# 点击第一个搜索结果
adb shell input tap {{first_result_x}} {{first_result_y}}
adb shell sleep 2""",
            "variables": {
                "search_box_x": {"type": "number", "description": "搜索框X坐标", "required": True, "default": "540"},
                "search_box_y": {"type": "number", "description": "搜索框Y坐标", "required": True, "default": "200"},
                "search_button_x": {"type": "number", "description": "搜索按钮X坐标", "required": True, "default": "1000"},
                "search_button_y": {"type": "number", "description": "搜索按钮Y坐标", "required": True, "default": "200"},
                "first_result_x": {"type": "number", "description": "第一个结果X坐标", "required": True, "default": "540"},
                "first_result_y": {"type": "number", "description": "第一个结果Y坐标", "required": True, "default": "400"},
                "search_keyword": {"type": "string", "description": "搜索关键词", "required": True, "default": "测试"}
            },
            "tags": ["搜索", "功能测试"]
        },
        {
            "name": "Python UI自动化模板",
            "category": "自动化测试",
            "language": "python",
            "description": "基于uiautomator2的Python自动化测试模板",
            "template_content": """import uiautomator2 as u2
import time

def test_{{test_name}}():
    # 连接设备
    d = u2.connect()
    
    try:
        # 启动应用
        d.app_start("{{package_name}}")
        time.sleep(2)
        
        # 等待元素出现
        d(text="{{target_text}}").wait(timeout=10)
        
        # 点击目标元素
        d(text="{{target_text}}").click()
        time.sleep(1)
        
        # 验证结果
        assert d(text="{{expected_text}}").exists, "验证失败：未找到预期文本"
        
        print("测试通过：{{test_name}}")
        
    except Exception as e:
        print(f"测试失败：{e}")
        # 截图保存错误现场
        d.screenshot("error_{{test_name}}.png")
        raise
    
    finally:
        # 清理：返回主页
        d.press("home")

if __name__ == "__main__":
    test_{{test_name}}()""",
            "variables": {
                "test_name": {"type": "string", "description": "测试名称", "required": True, "default": "example"},
                "package_name": {"type": "string", "description": "应用包名", "required": True, "default": "com.example.app"},
                "target_text": {"type": "string", "description": "目标元素文本", "required": True, "default": "登录"},
                "expected_text": {"type": "string", "description": "预期结果文本", "required": True, "default": "登录成功"}
            },
            "tags": ["Python", "uiautomator2", "自动化"]
        },
        {
            "name": "应用性能测试",
            "category": "性能测试",
            "language": "adb",
            "description": "应用性能监控测试模板",
            "template_content": """# 启动应用
adb shell am start -n {{package_name}}/{{activity_name}}
adb shell sleep 3

# 获取应用PID
PID=$(adb shell pidof {{package_name}})
echo "应用PID: $PID"

# 监控CPU使用率
echo "=== CPU使用率 ==="
adb shell top -p $PID -n 1 | grep {{package_name}}

# 监控内存使用
echo "=== 内存使用 ==="
adb shell dumpsys meminfo {{package_name}}

# 监控网络流量
echo "=== 网络流量 ==="
adb shell cat /proc/net/xt_qtaguid/stats | grep $PID

# 执行操作并监控
{{operations}}

# 再次检查性能
echo "=== 操作后性能 ==="
adb shell top -p $PID -n 1 | grep {{package_name}}
adb shell dumpsys meminfo {{package_name}}""",
            "variables": {
                "package_name": {"type": "string", "description": "应用包名", "required": True, "default": "com.example.app"},
                "activity_name": {"type": "string", "description": "启动Activity", "required": True, "default": ".MainActivity"},
                "operations": {"type": "text", "description": "测试操作步骤", "required": True, "default": "# 在这里添加测试操作\nadb shell input tap 540 960\nadb shell sleep 2"}
            },
            "tags": ["性能测试", "监控"]
        }
    ]
    
    for template_data in builtin_templates:
        template = ScriptTemplate(
            name=template_data["name"],
            category=template_data["category"],
            language=template_data["language"],
            description=template_data["description"],
            template_content=template_data["template_content"],
            variables=json.dumps(template_data["variables"]),
            tags=",".join(template_data["tags"]),
            is_builtin=True,
            created_by="system"
        )
        session.add(template)
    
    session.commit()
    print("✅ 内置模板初始化完成")