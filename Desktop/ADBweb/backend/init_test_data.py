"""
初始化测试数据
用于测试环境的示例数据、报告数据、模板数据初始化
"""
from sqlmodel import Session, create_engine, select
from app.core.database import get_engine
from app.models.example import Example
from app.models.report import Report
from app.models.template import Template
from datetime import datetime
import json


def init_examples(session: Session):
    """初始化示例数据"""
    # 检查是否已有数据
    existing = session.exec(select(Example)).first()
    if existing:
        print("✅ 示例数据已存在，跳过初始化")
        return
    
    examples = [
        Example(
            title="UI自动化测试示例",
            description="演示如何进行UI自动化测试",
            category="UI测试",
            difficulty="初级",
            script_type="visual",
            script_content=json.dumps([
                {"action": "click", "selector": "com.example:id/button"},
                {"action": "input", "selector": "com.example:id/input", "text": "test"}
            ]),
            tags="UI,自动化,测试",
            is_featured=True,
            view_count=100,
            download_count=50
        ),
        Example(
            title="性能测试示例",
            description="演示如何进行性能测试",
            category="性能测试",
            difficulty="中级",
            script_type="python",
            script_content="# 性能测试脚本\nimport time\nstart = time.time()\n# 测试代码\nend = time.time()\nprint(f'耗时: {end-start}秒')",
            tags="性能,测试,监控",
            is_featured=True,
            view_count=80,
            download_count=30
        ),
        Example(
            title="接口测试示例",
            description="演示如何进行接口测试",
            category="接口测试",
            difficulty="初级",
            script_type="python",
            script_content="import requests\nresponse = requests.get('http://api.example.com')\nassert response.status_code == 200",
            tags="接口,API,测试",
            is_featured=False,
            view_count=60,
            download_count=20
        )
    ]
    
    for example in examples:
        session.add(example)
    
    session.commit()
    print(f"✅ 成功初始化 {len(examples)} 个示例数据")


def init_reports(session: Session):
    """初始化报告数据"""
    # 检查是否已有数据
    existing = session.exec(select(Report)).first()
    if existing:
        print("✅ 报告数据已存在，跳过初始化")
        return
    
    reports = [
        Report(
            title="自动化测试报告 - 2024-01",
            report_type="test",
            status="completed",
            summary="本月共执行100个测试用例，通过率95%",
            content=json.dumps({
                "total_tests": 100,
                "passed": 95,
                "failed": 5,
                "pass_rate": 95.0
            }),
            created_by="system",
            start_time=datetime.now(),
            end_time=datetime.now()
        ),
        Report(
            title="性能测试报告 - 2024-01",
            report_type="performance",
            status="completed",
            summary="系统平均响应时间200ms，满足性能要求",
            content=json.dumps({
                "avg_response_time": 200,
                "max_response_time": 500,
                "min_response_time": 50
            }),
            created_by="system",
            start_time=datetime.now(),
            end_time=datetime.now()
        )
    ]
    
    for report in reports:
        session.add(report)
    
    session.commit()
    print(f"✅ 成功初始化 {len(reports)} 个报告数据")


def init_templates(session: Session):
    """初始化模板数据"""
    # 检查是否已有数据
    existing = session.exec(select(Template)).first()
    if existing:
        print("✅ 模板数据已存在，跳过初始化")
        return
    
    templates = [
        Template(
            name="UI测试模板",
            description="标准UI自动化测试模板",
            category="UI测试",
            template_type="script",
            content=json.dumps([
                {"step": 1, "action": "启动应用", "type": "launch"},
                {"step": 2, "action": "点击按钮", "type": "click"},
                {"step": 3, "action": "验证结果", "type": "assert"}
            ]),
            tags="UI,模板,自动化",
            is_public=True,
            usage_count=50
        ),
        Template(
            name="接口测试模板",
            description="标准接口测试模板",
            category="接口测试",
            template_type="script",
            content=json.dumps({
                "method": "GET",
                "url": "http://api.example.com",
                "headers": {},
                "assertions": [
                    {"type": "status_code", "expected": 200}
                ]
            }),
            tags="接口,API,模板",
            is_public=True,
            usage_count=30
        )
    ]
    
    for template in templates:
        session.add(template)
    
    session.commit()
    print(f"✅ 成功初始化 {len(templates)} 个模板数据")


def main():
    """主函数"""
    print("="*80)
    print("开始初始化测试数据...")
    print("="*80)
    
    engine = get_engine()
    
    with Session(engine) as session:
        try:
            init_examples(session)
            init_reports(session)
            init_templates(session)
            
            print("="*80)
            print("✅ 测试数据初始化完成！")
            print("="*80)
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            session.rollback()
            raise


if __name__ == "__main__":
    main()
