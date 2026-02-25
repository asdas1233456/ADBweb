"""
AI脚本生成服务
支持规则引擎和真实AI API（OpenAI/DeepSeek等）
"""
import re
import os
from typing import Dict, List, Tuple, Optional
import requests
import json


class AIScriptGenerator:
    """AI脚本生成器"""
    
    # 关键词到ADB命令的映射
    KEYWORD_MAPPINGS = {
        "点击": "input tap",
        "滑动": "input swipe",
        "输入": "input text",
        "返回": "input keyevent 4",
        "主页": "input keyevent 3",
        "截图": "screencap",
        "安装": "install",
        "卸载": "uninstall",
        "启动": "am start",
        "关闭": "am force-stop",
        "清除数据": "pm clear",
        "重启": "reboot",
        "重新启动": "reboot",
    }
    
    # 应用包名映射
    APP_PACKAGES = {
        "微信": "com.tencent.mm",
        "抖音": "com.ss.android.ugc.aweme",
        "淘宝": "com.taobao.taobao",
        "支付宝": "com.eg.android.AlipayGphone",
        "QQ": "com.tencent.mobileqq",
        "京东": "com.jingdong.app.mall",
    }
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """
        初始化AI脚本生成器
        
        Args:
            api_key: AI API密钥（可选，如果不提供则使用规则引擎）
            api_base: AI API基础URL（可选，默认使用OpenAI兼容接口）
        """
        self.api_key = api_key or os.getenv("AI_API_KEY")
        self.api_base = api_base or os.getenv("AI_API_BASE", "https://api.deepseek.com/v1")
        self.use_ai = bool(self.api_key)
    
    def generate_script(self, prompt: str, language: str = "adb") -> str:
        """
        根据自然语言生成脚本
        
        Args:
            prompt: 用户输入的自然语言描述
            language: 脚本语言类型 (adb/python)
            
        Returns:
            生成的脚本内容
        """
        # 如果配置了AI API，优先使用AI生成
        if self.use_ai:
            try:
                return self._generate_with_ai(prompt, language)
            except Exception as e:
                print(f"AI生成失败，回退到规则引擎: {str(e)}")
                # AI失败时回退到规则引擎
        
        # 使用规则引擎生成
        if language == "adb":
            return self._generate_adb_script(prompt)
        elif language == "python":
            return self._generate_python_script(prompt)
        else:
            return self._generate_adb_script(prompt)
    
    def _generate_with_ai(self, prompt: str, language: str) -> str:
        """使用AI API生成脚本"""
        system_prompt = f"""你是一个Android自动化测试脚本生成专家。
根据用户的自然语言描述，生成{'ADB Shell' if language == 'adb' else 'Python'}脚本。

要求：
1. 生成可直接执行的脚本
2. 包含必要的注释
3. 添加适当的等待时间
4. 使用合理的坐标或元素定位
5. {'生成ADB命令格式' if language == 'adb' else '生成Python代码，使用subprocess执行ADB命令'}

只返回脚本代码，不要有其他解释。"""

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                script = result["choices"][0]["message"]["content"]
                # 清理可能的markdown代码块标记
                script = script.replace("```bash", "").replace("```python", "").replace("```", "").strip()
                return script
            else:
                raise Exception(f"API返回错误: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"AI API调用失败: {str(e)}")
    
    def _generate_adb_script(self, prompt: str) -> str:
        """生成ADB脚本（规则引擎）"""
        commands = []
        
        # 检测应用启动
        app_detected = False
        for app_name, package in self.APP_PACKAGES.items():
            if app_name in prompt:
                commands.append(f"# 启动{app_name}")
                commands.append(f"adb shell am start -n {package}/.ui.LauncherUI")
                commands.append("adb shell sleep 2")
                app_detected = True
                break
        
        # 如果没有检测到具体应用，但提到了启动或打开
        if not app_detected and ("启动" in prompt or "打开" in prompt or "运行" in prompt):
            commands.extend([
                "# 启动应用",
                "adb shell am start -n com.example.app/.MainActivity",
                "adb shell sleep 2",
            ])
        
        # 检测操作类型
        if "重启" in prompt or "重新启动" in prompt:
            if "设备" in prompt:
                commands.extend([
                    "# 重启设备",
                    "adb reboot",
                    "# 等待设备重启完成",
                    "adb wait-for-device",
                    "# 等待系统启动",
                    "adb shell sleep 30",
                ])
            else:
                commands.extend([
                    "# 重启应用",
                    "adb shell am force-stop com.example.app",
                    "adb shell sleep 1",
                    "adb shell am start -n com.example.app/.MainActivity",
                ])
        elif "登录" in prompt:
            commands.extend([
                "# 点击登录按钮",
                "adb shell input tap 540 1200",
                "adb shell sleep 1",
                "# 输入账号",
                "adb shell input text 'testuser'",
                "adb shell sleep 0.5",
                "# 点击密码框",
                "adb shell input tap 540 1400",
                "adb shell sleep 0.5",
                "# 输入密码",
                "adb shell input text 'password123'",
                "adb shell sleep 0.5",
                "# 点击确认登录",
                "adb shell input tap 540 1600",
                "adb shell sleep 2",
                "# 验证登录成功",
                "adb shell screencap -p /sdcard/login_result.png",
            ])
        elif "搜索" in prompt:
            search_keyword = "test"
            # 尝试从提示词中提取搜索关键词
            if "搜索" in prompt:
                parts = prompt.split("搜索")
                if len(parts) > 1:
                    after_search = parts[1].strip()
                    if after_search and not any(x in after_search for x in ["功能", "测试", "页面"]):
                        search_keyword = after_search.split()[0] if after_search.split() else "test"
            
            commands.extend([
                "# 点击搜索框",
                "adb shell input tap 540 200",
                "adb shell sleep 1",
                f"# 输入搜索内容: {search_keyword}",
                f"adb shell input text '{search_keyword}'",
                "adb shell sleep 0.5",
                "# 点击搜索按钮",
                "adb shell input tap 1000 200",
                "adb shell sleep 2",
                "# 等待搜索结果加载",
                "adb shell sleep 1",
            ])
        elif "滑动" in prompt or "刷新" in prompt:
            if "上滑" in prompt:
                commands.extend([
                    "# 上滑操作",
                    "adb shell input swipe 540 1500 540 500 300",
                ])
            elif "下滑" in prompt or "刷新" in prompt:
                commands.extend([
                    "# 下拉刷新",
                    "adb shell input swipe 540 500 540 1500 300",
                ])
            else:
                commands.extend([
                    "# 滑动操作",
                    "adb shell input swipe 540 1000 540 500 300",
                ])
            commands.append("adb shell sleep 2")
        elif "截图" in prompt:
            commands.extend([
                "# 截图保存",
                "adb shell screencap -p /sdcard/screenshot.png",
                "adb pull /sdcard/screenshot.png ./screenshot.png",
                "echo '截图已保存到 ./screenshot.png'",
            ])
        elif "点击" in prompt:
            # 尝试识别点击位置
            if "中心" in prompt or "中央" in prompt:
                commands.extend([
                    "# 点击屏幕中心",
                    "adb shell input tap 540 960",
                ])
            elif "返回" in prompt or "后退" in prompt:
                commands.extend([
                    "# 点击返回按钮",
                    "adb shell input keyevent 4",
                ])
            elif "主页" in prompt or "首页" in prompt:
                commands.extend([
                    "# 点击主页按钮",
                    "adb shell input keyevent 3",
                ])
            else:
                commands.extend([
                    "# 点击操作",
                    "adb shell input tap 540 960",
                ])
            commands.append("adb shell sleep 1")
        elif "输入" in prompt:
            # 尝试提取输入内容
            input_text = "test"
            if "输入" in prompt:
                parts = prompt.split("输入")
                if len(parts) > 1:
                    after_input = parts[1].strip()
                    if after_input:
                        input_text = after_input.split()[0] if after_input.split() else "test"
            
            commands.extend([
                f"# 输入文本: {input_text}",
                f"adb shell input text '{input_text}'",
                "adb shell sleep 0.5",
            ])
        elif "支付" in prompt:
            commands.extend([
                "# 点击支付按钮",
                "adb shell input tap 540 1400",
                "adb shell sleep 1",
                "# 选择支付方式",
                "adb shell input tap 540 1200",
                "adb shell sleep 1",
                "# 确认支付",
                "adb shell input tap 540 1600",
                "adb shell sleep 3",
                "# 验证支付结果",
                "adb shell screencap -p /sdcard/payment_result.png",
            ])
        elif "播放" in prompt:
            commands.extend([
                "# 点击播放按钮",
                "adb shell input tap 540 960",
                "adb shell sleep 2",
                "# 等待播放开始",
                "adb shell sleep 3",
            ])
        elif "购物车" in prompt:
            commands.extend([
                "# 点击加入购物车",
                "adb shell input tap 540 1300",
                "adb shell sleep 1",
                "# 确认添加",
                "adb shell input tap 540 1500",
                "adb shell sleep 1",
            ])
        elif "注册" in prompt:
            commands.extend([
                "# 点击注册按钮",
                "adb shell input tap 540 1300",
                "adb shell sleep 1",
                "# 输入用户名",
                "adb shell input text 'newuser'",
                "adb shell sleep 0.5",
                "# 点击密码框",
                "adb shell input tap 540 1400",
                "adb shell sleep 0.5",
                "# 输入密码",
                "adb shell input text 'newpassword123'",
                "adb shell sleep 0.5",
                "# 点击确认注册",
                "adb shell input tap 540 1600",
                "adb shell sleep 2",
            ])
        else:
            # 默认生成基础操作
            commands.extend([
                "# 基础操作 - 点击屏幕中心",
                "adb shell input tap 540 960",
                "adb shell sleep 1",
                "# 等待响应",
                "adb shell sleep 1",
            ])
        
        # 添加返回操作
        if "返回" in prompt or "退出" in prompt:
            commands.extend([
                "# 返回操作",
                "adb shell input keyevent 4",
                "adb shell sleep 1",
            ])
        
        # 添加验证步骤
        if "验证" in prompt or "检查" in prompt:
            commands.extend([
                "# 验证操作结果",
                "adb shell screencap -p /sdcard/verification.png",
                "adb pull /sdcard/verification.png ./verification.png",
            ])
        
        return "\n".join(commands)
    
    def _generate_python_script(self, prompt: str) -> str:
        """生成Python脚本"""
        script_lines = [
            "#!/usr/bin/env python3",
            "# -*- coding: utf-8 -*-",
            "import subprocess",
            "import time",
            "import sys",
            "",
            "def execute_adb(command):",
            "    \"\"\"执行ADB命令\"\"\"",
            "    try:",
            "        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)",
            "        if result.returncode == 0:",
            "            print(f'✓ 命令执行成功: {command}')",
            "            return result.stdout",
            "        else:",
            "            print(f'✗ 命令执行失败: {command}')",
            "            print(f'错误信息: {result.stderr}')",
            "            return None",
            "    except subprocess.TimeoutExpired:",
            "        print(f'✗ 命令执行超时: {command}')",
            "        return None",
            "    except Exception as e:",
            "        print(f'✗ 命令执行异常: {command}, 错误: {str(e)}')",
            "        return None",
            "",
            "def wait_and_verify(seconds=1, description='操作'):",
            "    \"\"\"等待并验证\"\"\"",
            "    print(f'等待 {seconds} 秒，{description}...')",
            "    time.sleep(seconds)",
            "",
            "def main():",
            "    \"\"\"主函数\"\"\"",
            "    print('开始执行自动化脚本...')",
            "    success_count = 0",
            "    total_steps = 0",
            "",
        ]
        
        # 检测应用启动
        app_detected = False
        for app_name, package in self.APP_PACKAGES.items():
            if app_name in prompt:
                script_lines.extend([
                    f"    # 启动{app_name}",
                    f"    print('启动{app_name}应用...')",
                    f"    if execute_adb('adb shell am start -n {package}/.ui.LauncherUI'):",
                    "        success_count += 1",
                    "    total_steps += 1",
                    "    wait_and_verify(2, '应用启动')",
                    "",
                ])
                app_detected = True
                break
        
        # 如果没有检测到具体应用，但提到了启动或打开
        if not app_detected and ("启动" in prompt or "打开" in prompt or "运行" in prompt):
            script_lines.extend([
                "    # 启动应用",
                "    print('启动应用...')",
                "    if execute_adb('adb shell am start -n com.example.app/.MainActivity'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(2, '应用启动')",
                "",
            ])
        
        # 检测操作类型
        if "登录" in prompt:
            script_lines.extend([
                "    # 执行登录操作",
                "    print('开始登录流程...')",
                "    ",
                "    # 点击登录按钮",
                "    if execute_adb('adb shell input tap 540 1200'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(1, '点击登录按钮')",
                "    ",
                "    # 输入账号",
                "    if execute_adb('adb shell input text testuser'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(0.5, '输入账号')",
                "    ",
                "    # 点击密码框",
                "    if execute_adb('adb shell input tap 540 1400'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(0.5, '点击密码框')",
                "    ",
                "    # 输入密码",
                "    if execute_adb('adb shell input text password123'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(0.5, '输入密码')",
                "    ",
                "    # 点击确认登录",
                "    if execute_adb('adb shell input tap 540 1600'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(2, '确认登录')",
                "    ",
                "    # 验证登录结果",
                "    if execute_adb('adb shell screencap -p /sdcard/login_result.png'):",
                "        success_count += 1",
                "        print('登录结果截图已保存')",
                "    total_steps += 1",
                "",
            ])
        elif "搜索" in prompt:
            search_keyword = "test"
            # 尝试从提示词中提取搜索关键词
            if "搜索" in prompt:
                parts = prompt.split("搜索")
                if len(parts) > 1:
                    after_search = parts[1].strip()
                    if after_search and not any(x in after_search for x in ["功能", "测试", "页面"]):
                        search_keyword = after_search.split()[0] if after_search.split() else "test"
            
            script_lines.extend([
                "    # 执行搜索操作",
                f"    print('开始搜索: {search_keyword}...')",
                "    ",
                "    # 点击搜索框",
                "    if execute_adb('adb shell input tap 540 200'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(1, '点击搜索框')",
                "    ",
                f"    # 输入搜索内容: {search_keyword}",
                f"    if execute_adb('adb shell input text {search_keyword}'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(0.5, '输入搜索内容')",
                "    ",
                "    # 点击搜索按钮",
                "    if execute_adb('adb shell input tap 1000 200'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(2, '执行搜索')",
                "",
            ])
        elif "支付" in prompt:
            script_lines.extend([
                "    # 执行支付操作",
                "    print('开始支付流程...')",
                "    ",
                "    # 点击支付按钮",
                "    if execute_adb('adb shell input tap 540 1400'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(1, '点击支付按钮')",
                "    ",
                "    # 选择支付方式",
                "    if execute_adb('adb shell input tap 540 1200'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(1, '选择支付方式')",
                "    ",
                "    # 确认支付",
                "    if execute_adb('adb shell input tap 540 1600'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(3, '确认支付')",
                "    ",
                "    # 验证支付结果",
                "    if execute_adb('adb shell screencap -p /sdcard/payment_result.png'):",
                "        success_count += 1",
                "        print('支付结果截图已保存')",
                "    total_steps += 1",
                "",
            ])
        elif "注册" in prompt:
            script_lines.extend([
                "    # 执行注册操作",
                "    print('开始注册流程...')",
                "    ",
                "    # 点击注册按钮",
                "    if execute_adb('adb shell input tap 540 1300'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(1, '点击注册按钮')",
                "    ",
                "    # 输入用户名",
                "    if execute_adb('adb shell input text newuser'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(0.5, '输入用户名')",
                "    ",
                "    # 点击密码框",
                "    if execute_adb('adb shell input tap 540 1400'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(0.5, '点击密码框')",
                "    ",
                "    # 输入密码",
                "    if execute_adb('adb shell input text newpassword123'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(0.5, '输入密码')",
                "    ",
                "    # 点击确认注册",
                "    if execute_adb('adb shell input tap 540 1600'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(2, '确认注册')",
                "",
            ])
        elif "滑动" in prompt or "刷新" in prompt:
            if "上滑" in prompt:
                script_lines.extend([
                    "    # 执行上滑操作",
                    "    if execute_adb('adb shell input swipe 540 1500 540 500 300'):",
                    "        success_count += 1",
                    "    total_steps += 1",
                ])
            elif "下滑" in prompt or "刷新" in prompt:
                script_lines.extend([
                    "    # 执行下拉刷新",
                    "    if execute_adb('adb shell input swipe 540 500 540 1500 300'):",
                    "        success_count += 1",
                    "    total_steps += 1",
                ])
            else:
                script_lines.extend([
                    "    # 执行滑动操作",
                    "    if execute_adb('adb shell input swipe 540 1000 540 500 300'):",
                    "        success_count += 1",
                    "    total_steps += 1",
                ])
            script_lines.extend([
                "    wait_and_verify(2, '滑动操作')",
                "",
            ])
        elif "截图" in prompt:
            script_lines.extend([
                "    # 执行截图操作",
                "    print('开始截图...')",
                "    if execute_adb('adb shell screencap -p /sdcard/screenshot.png'):",
                "        success_count += 1",
                "        if execute_adb('adb pull /sdcard/screenshot.png ./screenshot.png'):",
                "            print('截图已保存到 ./screenshot.png')",
                "    total_steps += 1",
                "",
            ])
        else:
            # 默认生成基础操作
            script_lines.extend([
                "    # 执行基础操作",
                "    print('执行基础点击操作...')",
                "    if execute_adb('adb shell input tap 540 960'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(1, '基础操作')",
                "",
            ])
        
        # 添加返回操作
        if "返回" in prompt or "退出" in prompt:
            script_lines.extend([
                "    # 执行返回操作",
                "    if execute_adb('adb shell input keyevent 4'):",
                "        success_count += 1",
                "    total_steps += 1",
                "    wait_and_verify(1, '返回操作')",
                "",
            ])
        
        # 添加验证步骤
        if "验证" in prompt or "检查" in prompt:
            script_lines.extend([
                "    # 验证操作结果",
                "    if execute_adb('adb shell screencap -p /sdcard/verification.png'):",
                "        if execute_adb('adb pull /sdcard/verification.png ./verification.png'):",
                "            print('验证截图已保存到 ./verification.png')",
                "            success_count += 1",
                "    total_steps += 1",
                "",
            ])
        
        # 添加结果统计
        script_lines.extend([
            "    # 输出执行结果",
            "    print(f'\\n=== 脚本执行完成 ===')",
            "    print(f'总步骤数: {total_steps}')",
            "    print(f'成功步骤: {success_count}')",
            "    print(f'失败步骤: {total_steps - success_count}')",
            "    if total_steps > 0:",
            "        success_rate = (success_count / total_steps) * 100",
            "        print(f'成功率: {success_rate:.1f}%')",
            "    ",
            "    if success_count == total_steps:",
            "        print('✓ 所有步骤执行成功！')",
            "        return 0",
            "    else:",
            "        print('✗ 部分步骤执行失败')",
            "        return 1",
            "",
            "if __name__ == '__main__':",
            "    try:",
            "        exit_code = main()",
            "        sys.exit(exit_code)",
            "    except KeyboardInterrupt:",
            "        print('\\n用户中断执行')",
            "        sys.exit(1)",
            "    except Exception as e:",
            "        print(f'脚本执行异常: {str(e)}')",
            "        sys.exit(1)",
        ])
        
        return "\n".join(script_lines)
    
    def optimize_prompt(self, prompt: str, language: str = "adb") -> Dict[str, any]:
        """
        优化用户输入的提示词
        
        Args:
            prompt: 用户输入的原始提示词
            language: 脚本语言类型
            
        Returns:
            包含优化后的提示词和改进建议的字典
        """
        # 如果配置了AI，使用AI优化
        if self.use_ai:
            try:
                return self._optimize_prompt_with_ai(prompt, language)
            except Exception as e:
                print(f"AI优化失败，使用规则引擎: {str(e)}")
        
        # 使用规则引擎优化
        return self._optimize_prompt_with_rules(prompt, language)
    
    def _optimize_prompt_with_ai(self, prompt: str, language: str) -> Dict[str, any]:
        """使用AI优化提示词"""
        system_prompt = """你是一个Android自动化测试专家。帮助用户优化他们的脚本生成提示词。

分析用户的提示词，提供：
1. 优化后的提示词（更清晰、更具体、更易于生成准确脚本）
2. 改进建议（3-5条）
3. 缺失的关键信息

返回JSON格式：
{
  "optimized_prompt": "优化后的提示词",
  "improvements": ["改进点1", "改进点2", "改进点3"],
  "missing_info": ["缺失信息1", "缺失信息2"]
}"""

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"原始提示词：{prompt}\n脚本类型：{language}"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                # 尝试解析JSON
                try:
                    # 清理可能的markdown代码块
                    content = content.replace("```json", "").replace("```", "").strip()
                    data = json.loads(content)
                    return {
                        "optimized_prompt": data.get("optimized_prompt", prompt),
                        "improvements": data.get("improvements", []),
                        "missing_info": data.get("missing_info", []),
                        "original_prompt": prompt
                    }
                except json.JSONDecodeError:
                    # 如果解析失败，返回原始提示词
                    return self._optimize_prompt_with_rules(prompt, language)
            else:
                raise Exception(f"API返回错误: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"AI优化失败: {str(e)}")
    
    def _optimize_prompt_with_rules(self, prompt: str, language: str) -> Dict[str, any]:
        """使用规则引擎优化提示词"""
        improvements = []
        missing_info = []
        optimized_parts = []
        
        # 检查是否包含应用名称
        has_app = any(app in prompt for app in self.APP_PACKAGES.keys())
        if not has_app and "启动" in prompt:
            missing_info.append("未指定应用名称（如：微信、抖音、淘宝等）")
            improvements.append("建议明确指定要操作的应用名称")
        
        # 检查是否包含具体操作
        has_action = any(keyword in prompt for keyword in ["点击", "滑动", "输入", "搜索", "登录"])
        if not has_action:
            missing_info.append("未明确具体操作步骤")
            improvements.append("建议详细描述操作步骤，如：点击登录按钮、输入账号密码等")
        
        # 检查是否过于简短
        if len(prompt) < 5:
            improvements.append("提示词过于简短，建议提供更多细节")
            missing_info.append("缺少详细的操作描述")
        
        # 检查是否包含测试目标
        if "测试" not in prompt and "验证" not in prompt and "检查" not in prompt:
            improvements.append("建议说明测试目标或预期结果")
            missing_info.append("未说明测试目标")
        
        # 构建优化后的提示词
        optimized_prompt = prompt
        
        # 如果提示词太简单，尝试扩展
        if len(improvements) > 0:
            if "登录" in prompt and len(prompt) < 10:
                optimized_prompt = f"测试{prompt}功能：1. 启动应用 2. 点击登录按钮 3. 输入测试账号和密码 4. 点击确认登录 5. 验证登录成功"
            elif "搜索" in prompt and len(prompt) < 10:
                optimized_prompt = f"测试{prompt}功能：1. 点击搜索框 2. 输入搜索关键词 3. 点击搜索按钮 4. 验证搜索结果显示"
            elif len(prompt) < 5:
                optimized_prompt = f"{prompt}（建议补充：具体操作步骤、测试目标、预期结果）"
        
        # 如果没有改进建议，说明提示词已经不错
        if len(improvements) == 0:
            improvements.append("提示词描述清晰，包含了必要的操作信息")
        
        return {
            "optimized_prompt": optimized_prompt,
            "improvements": improvements,
            "missing_info": missing_info,
            "original_prompt": prompt
        }
    
    def optimize_script(self, script: str) -> List[Dict[str, str]]:
        """
        检测脚本问题并提供优化建议
        
        Args:
            script: 脚本内容
            
        Returns:
            优化建议列表
        """
        suggestions = []
        
        # 检测1: 缺少sleep导致操作过快
        if "input tap" in script or "input swipe" in script:
            sleep_count = len(re.findall(r'sleep|time\.sleep', script))
            action_count = len(re.findall(r'input (tap|swipe|text)', script))
            
            if action_count > sleep_count + 1:
                suggestions.append({
                    "type": "warning",
                    "title": "缺少等待时间",
                    "description": "检测到连续操作之间缺少等待，可能导致操作失败",
                    "suggestion": "建议在每个操作后添加 sleep 1 或 time.sleep(1)",
                    "line": None
                })
        
        # 检测2: 硬编码坐标
        tap_coords = re.findall(r'input tap (\d+) (\d+)', script)
        if len(tap_coords) > 2:
            suggestions.append({
                "type": "error",
                "title": "硬编码坐标过多",
                "description": f"检测到{len(tap_coords)}处硬编码坐标，不同设备分辨率可能导致点击失败",
                "suggestion": "建议使用 uiautomator2 或图像识别定位元素",
                "line": None
            })
        
        # 检测3: 缺少错误处理
        if "python" in script.lower() and "try" not in script.lower():
            suggestions.append({
                "type": "info",
                "title": "缺少异常处理",
                "description": "脚本未包含异常处理逻辑",
                "suggestion": "建议添加 try-except 块处理可能的异常",
                "line": None
            })
        
        return suggestions
