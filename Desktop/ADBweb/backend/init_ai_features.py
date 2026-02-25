"""
初始化AI功能相关数据
包括测试用例和AI脚本表
"""
from sqlmodel import Session, select
from app.core.database import engine, create_db_and_tables
from app.models.test_case import TestCase
from app.models.ai_script import AIScript


def init_test_cases(session: Session):
    """初始化测试用例数据"""
    
    # 检查是否已有数据
    statement = select(TestCase)
    existing = session.exec(statement).first()
    if existing:
        print("[INFO] 测试用例数据已存在，跳过初始化")
        return
    
    # 小米14设备的测试用例
    xiaomi_cases = [
        TestCase(
            name="微信登录测试",
            description="测试微信应用的登录功能，包括账号密码输入和验证",
            device_model="小米14",
            priority=1,
            failure_count=15,
            success_count=85,
            script_template="adb shell am start -n com.tencent.mm/.ui.LauncherUI",
            tags="登录,微信,核心功能"
        ),
        TestCase(
            name="微信消息发送测试",
            description="测试微信发送文字消息功能",
            device_model="小米14",
            priority=2,
            failure_count=8,
            success_count=92,
            script_template="adb shell input text 'Hello'",
            tags="消息,微信,核心功能"
        ),
        TestCase(
            name="抖音视频播放测试",
            description="测试抖音视频播放和滑动功能",
            device_model="小米14",
            priority=2,
            failure_count=12,
            success_count=88,
            script_template="adb shell am start -n com.ss.android.ugc.aweme/.main.MainActivity",
            tags="视频,抖音,播放"
        ),
        TestCase(
            name="淘宝商品搜索测试",
            description="测试淘宝商品搜索功能",
            device_model="小米14",
            priority=3,
            failure_count=5,
            success_count=95,
            script_template="adb shell am start -n com.taobao.taobao/.MainActivity",
            tags="搜索,淘宝,购物"
        ),
        TestCase(
            name="支付宝扫码支付测试",
            description="测试支付宝扫码支付流程",
            device_model="小米14",
            priority=1,
            failure_count=20,
            success_count=80,
            script_template="adb shell am start -n com.eg.android.AlipayGphone/.AlipayLogin",
            tags="支付,支付宝,核心功能"
        ),
    ]
    
    # 华为Mate60设备的测试用例
    huawei_cases = [
        TestCase(
            name="微信登录测试",
            description="测试微信应用的登录功能",
            device_model="华为Mate60",
            priority=1,
            failure_count=10,
            success_count=90,
            script_template="adb shell am start -n com.tencent.mm/.ui.LauncherUI",
            tags="登录,微信,核心功能"
        ),
        TestCase(
            name="京东商品浏览测试",
            description="测试京东商品浏览和加购功能",
            device_model="华为Mate60",
            priority=2,
            failure_count=7,
            success_count=93,
            script_template="adb shell am start -n com.jingdong.app.mall/.main.MainActivity",
            tags="浏览,京东,购物"
        ),
        TestCase(
            name="QQ消息测试",
            description="测试QQ消息收发功能",
            device_model="华为Mate60",
            priority=2,
            failure_count=6,
            success_count=94,
            script_template="adb shell am start -n com.tencent.mobileqq/.activity.SplashActivity",
            tags="消息,QQ,社交"
        ),
    ]
    
    # OPPO Find X7设备的测试用例
    oppo_cases = [
        TestCase(
            name="微信视频通话测试",
            description="测试微信视频通话功能",
            device_model="OPPO Find X7",
            priority=1,
            failure_count=18,
            success_count=82,
            script_template="adb shell am start -n com.tencent.mm/.ui.LauncherUI",
            tags="视频通话,微信,核心功能"
        ),
        TestCase(
            name="抖音直播测试",
            description="测试抖音直播观看功能",
            device_model="OPPO Find X7",
            priority=3,
            failure_count=4,
            success_count=96,
            script_template="adb shell am start -n com.ss.android.ugc.aweme/.main.MainActivity",
            tags="直播,抖音,娱乐"
        ),
    ]
    
    # 添加所有测试用例
    all_cases = xiaomi_cases + huawei_cases + oppo_cases
    for case in all_cases:
        session.add(case)
    
    session.commit()
    print(f"[INFO] 成功初始化 {len(all_cases)} 条测试用例数据")


def main():
    """主函数"""
    print("[INFO] 开始初始化AI功能数据...")
    
    # 创建数据库表
    print("[INFO] 创建数据库表...")
    create_db_and_tables()
    
    # 初始化数据
    with Session(engine) as session:
        init_test_cases(session)
    
    print("[INFO] AI功能数据初始化完成！")


if __name__ == "__main__":
    main()
