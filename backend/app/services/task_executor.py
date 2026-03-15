"""
任务执行器 - 支持实时推送
"""
import asyncio
import sys
from datetime import datetime
from app.core.websocket_manager import manager
from app.core.config import settings
from typing import List, Dict
from app.utils.time_utils import now_local


class TaskExecutor:
    """任务执行器"""
    
    async def _run_subprocess_windows(self, task_id: int, cmd_args: list, env: dict = None) -> tuple:
        """在Windows上运行subprocess（使用线程池避免NotImplementedError）"""
        import subprocess
        from concurrent.futures import ThreadPoolExecutor
        import threading
        
        def run_subprocess():
            """在线程中运行subprocess"""
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=0  # 无缓冲
            )
            
            stdout_lines = []
            stderr_lines = []
            
            def read_stdout():
                try:
                    for line in iter(process.stdout.readline, ''):
                        if not line:
                            break
                        output = line.rstrip('\n\r')
                        if output:
                            stdout_lines.append(output)
                finally:
                    process.stdout.close()
            
            def read_stderr():
                try:
                    for line in iter(process.stderr.readline, ''):
                        if not line:
                            break
                        output = line.rstrip('\n\r')
                        if output:
                            stderr_lines.append(output)
                finally:
                    process.stderr.close()
            
            # 启动两个线程同时读取stdout和stderr
            stdout_thread = threading.Thread(target=read_stdout, daemon=True)
            stderr_thread = threading.Thread(target=read_stderr, daemon=True)
            
            stdout_thread.start()
            stderr_thread.start()
            
            # 等待进程结束
            return_code = process.wait()
            
            # 等待读取线程结束（最多等待2秒）
            stdout_thread.join(timeout=2)
            stderr_thread.join(timeout=2)
            
            return return_code, stdout_lines, stderr_lines
        
        # 在线程池中执行
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return_code, stdout_lines, stderr_lines = await loop.run_in_executor(
                executor, run_subprocess
            )
        
        return return_code, stdout_lines, stderr_lines
    
    async def execute_script(
        self, 
        task_id: int, 
        script_id: int, 
        device_id: int, 
        steps: List[Dict]
    ):
        """执行脚本并实时推送进度"""
        total_steps = len(steps)
        
        # 初始化任务
        await manager.send_task_update(task_id, {
            "status": "running",
            "progress": 0,
            "current_step": 0,
            "total_steps": total_steps,
            "message": "任务开始执行",
            "start_time": now_local().isoformat()
        })
        
        try:
            for index, step in enumerate(steps):
                current_step = index + 1
                progress = int((current_step / total_steps) * 100)
                
                # 推送步骤开始
                await manager.send_task_update(task_id, {
                    "status": "running",
                    "progress": progress,
                    "current_step": current_step,
                    "total_steps": total_steps,
                    "message": f"正在执行第 {current_step} 步: {step.get('name', '未命名步骤')}",
                    "step_detail": step
                })
                
                # 推送日志
                await manager.send_task_update(task_id, {
                    "type": "log",
                    "message": f"[{now_local().strftime('%H:%M:%S')}] 开始执行: {step.get('name', '未命名步骤')}",
                    "level": "info"
                })
                
                # 执行步骤
                await self._execute_step(task_id, step, device_id)
                
                # 推送步骤完成
                await manager.send_task_update(task_id, {
                    "type": "log",
                    "message": f"[{now_local().strftime('%H:%M:%S')}] ✅ 第 {current_step} 步执行完成",
                    "level": "success"
                })
                
                # 模拟执行时间（增加到5秒以便测试停止功能）
                await asyncio.sleep(5)
            
            # 任务完成
            await manager.send_task_update(task_id, {
                "status": "success",
                "progress": 100,
                "current_step": total_steps,
                "total_steps": total_steps,
                "message": "✅ 任务执行成功",
                "end_time": now_local().isoformat()
            })
            
            return {"status": "success", "message": "任务执行成功"}
            
        except Exception as e:
            # 任务失败
            await manager.send_task_update(task_id, {
                "status": "failed",
                "progress": int((current_step / total_steps) * 100) if 'current_step' in locals() else 0,
                "current_step": current_step if 'current_step' in locals() else 0,
                "total_steps": total_steps,
                "message": f"❌ 任务执行失败: {str(e)}",
                "error": str(e),
                "end_time": now_local().isoformat()
            })
            
            return {"status": "failed", "message": str(e)}
    
    async def _execute_step(self, task_id: int, step: Dict, device_id: int):
        """执行单个步骤"""
        step_type = step.get("type")
        
        # 推送详细日志
        await manager.send_task_update(task_id, {
            "type": "log",
            "message": f"[{now_local().strftime('%H:%M:%S')}] 执行 {step_type} 操作",
            "level": "debug"
        })
        
        # 根据步骤类型执行不同操作
        if step_type == "click":
            await self._execute_click(task_id, step, device_id)
        elif step_type == "input":
            await self._execute_input(task_id, step, device_id)
        elif step_type == "swipe":
            await self._execute_swipe(task_id, step, device_id)
        elif step_type == "wait":
            await self._execute_wait(task_id, step, device_id)
        else:
            await asyncio.sleep(0.5)
    
    async def _execute_click(self, task_id: int, step: Dict, device_id: int):
        """执行点击操作"""
        config = step.get("config", {})
        x = config.get("x", 0)
        y = config.get("y", 0)
        selector = config.get("selector", "")
        
        # 模拟失败场景：如果selector包含"不存在"，则抛出异常
        if selector and "不存在" in selector:
            await manager.send_task_update(task_id, {
                "type": "log",
                "message": f"[{now_local().strftime('%H:%M:%S')}] ❌ 元素未找到: {selector}",
                "level": "error"
            })
            raise Exception(f"Element not found: {selector}")
        
        await manager.send_task_update(task_id, {
            "type": "log",
            "message": f"[{now_local().strftime('%H:%M:%S')}] 点击坐标 ({x}, {y})",
            "level": "debug"
        })
        
        # 实际 ADB 命令执行
        # subprocess.run(["adb", "-s", device_serial, "shell", "input", "tap", str(x), str(y)])
        
        await asyncio.sleep(0.5)
    
    async def _execute_input(self, task_id: int, step: Dict, device_id: int):
        """执行输入操作"""
        config = step.get("config", {})
        text = config.get("text", "")
        
        await manager.send_task_update(task_id, {
            "type": "log",
            "message": f"[{now_local().strftime('%H:%M:%S')}] 输入文本: {text}",
            "level": "debug"
        })
        
        await asyncio.sleep(0.5)
    
    async def _execute_swipe(self, task_id: int, step: Dict, device_id: int):
        """执行滑动操作"""
        config = step.get("config", {})
        x1 = config.get("x1", 0)
        y1 = config.get("y1", 0)
        x2 = config.get("x2", 0)
        y2 = config.get("y2", 0)
        
        await manager.send_task_update(task_id, {
            "type": "log",
            "message": f"[{now_local().strftime('%H:%M:%S')}] 滑动: ({x1},{y1}) -> ({x2},{y2})",
            "level": "debug"
        })
        
        await asyncio.sleep(0.5)
    
    async def _execute_wait(self, task_id: int, step: Dict, device_id: int):
        """执行等待操作"""
        config = step.get("config", {})
        duration = config.get("duration", 1000) / 1000  # 转换为秒
        
        await manager.send_task_update(task_id, {
            "type": "log",
            "message": f"[{now_local().strftime('%H:%M:%S')}] 等待 {duration} 秒",
            "level": "debug"
        })
        
        await asyncio.sleep(duration)
    
    async def execute_file_script(
        self, 
        task_id: int, 
        script, 
        device_id: int
    ):
        """执行文件脚本（Python/批处理）"""
        import subprocess
        import tempfile
        import os
        
        print(f"[DEBUG] execute_file_script 开始, task_id={task_id}, script.type={script.type}")
        
        if not settings.ENABLE_SCRIPT_EXECUTION:
            raise Exception("脚本执行已被管理员禁用")
        
        # 初始化任务
        await manager.send_task_update(task_id, {
            "status": "running",
            "progress": 0,
            "message": f"开始执行{script.type}脚本: {script.name}",
            "start_time": now_local().isoformat()
        })
        
        try:
            print(f"[DEBUG] 开始执行脚本内容")
            # 推送日志
            await manager.send_task_update(task_id, {
                "type": "log",
                "message": f"[{now_local().strftime('%H:%M:%S')}] 准备执行脚本: {script.name}",
                "level": "info"
            })
            
            # 获取设备信息
            from app.core.database import engine
            from sqlmodel import Session
            from app.models.device import Device
            
            with Session(engine) as db:
                device = db.get(Device, device_id)
                device_serial = device.serial_number if device else "unknown"
            
            print(f"[DEBUG] 设备序列号: {device_serial}")
            
            await manager.send_task_update(task_id, {
                "type": "log",
                "message": f"[{now_local().strftime('%H:%M:%S')}] 目标设备: {device_serial}",
                "level": "info"
            })
            
            # 更新进度
            await manager.send_task_update(task_id, {
                "status": "running",
                "progress": 25,
                "message": "正在准备执行环境..."
            })
            
            print(f"[DEBUG] 准备调用 _execute_{script.type}_script")
            
            if script.type == "python":
                await self._execute_python_script(task_id, script, device_serial)
            elif script.type == "batch":
                await self._execute_batch_script(task_id, script, device_serial)
            
            print(f"[DEBUG] 脚本执行成功")
            
            # 任务完成
            await manager.send_task_update(task_id, {
                "status": "success",
                "progress": 100,
                "message": f"✅ {script.type}脚本执行完成",
                "end_time": now_local().isoformat()
            })
            
            return {"status": "success", "message": f"{script.type}脚本执行成功"}
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"[DEBUG] execute_file_script 捕获异常:")
            print(f"[DEBUG] 错误类型: {type(e).__name__}")
            print(f"[DEBUG] 错误信息: {str(e)}")
            print(f"[DEBUG] 堆栈:\n{error_detail}")
            
            # 任务失败
            await manager.send_task_update(task_id, {
                "status": "failed",
                "progress": 50,
                "message": f"❌ {script.type}脚本执行失败: {str(e)}",
                "error": str(e),
                "end_time": now_local().isoformat()
            })
            
            return {"status": "failed", "message": str(e)}
    
    async def _execute_python_script(self, task_id: int, script, device_serial: str):
        """执行Python脚本（支持自动安装依赖）"""
        import tempfile
        import subprocess
        import os
        import re
        
        await manager.send_task_update(task_id, {
            "type": "log",
            "message": f"[{now_local().strftime('%H:%M:%S')}] 创建临时Python文件...",
            "level": "info"
        })
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            # 在脚本开头添加设备信息
            script_content = f"""# -*- coding: utf-8 -*-
# 自动生成的脚本执行文件
# 目标设备: {device_serial}
# 脚本名称: {script.name}

import os
import sys
import subprocess

# 设置标准输出为UTF-8编码（Windows兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 设备序列号
DEVICE_SERIAL = "{device_serial}"

# 原始脚本内容
{script.file_content or '# 脚本内容为空'}
"""
            f.write(script_content)
            temp_file = f.name
        
        try:
            await manager.send_task_update(task_id, {
                "status": "running",
                "progress": 50,
                "message": "正在执行Python脚本..."
            })
            
            await manager.send_task_update(task_id, {
                "type": "log",
                "message": f"[{now_local().strftime('%H:%M:%S')}] 执行命令: python {temp_file}",
                "level": "info"
            })
            
            # 首次执行Python脚本
            max_retries = 3  # 最多重试3次（用于安装依赖）
            retry_count = 0
            
            while retry_count < max_retries:
                # 设置环境变量，确保Python使用UTF-8编码和无缓冲输出
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                env['PYTHONUNBUFFERED'] = '1'  # 强制无缓冲输出
                
                # Windows兼容：在Windows上使用线程池执行subprocess
                if sys.platform == 'win32':
                    print(f"[DEBUG] Windows平台，使用线程池执行")
                    # 添加-u参数强制Python使用无缓冲输出
                    return_code, stdout_lines, stderr_lines = await self._run_subprocess_windows(
                        task_id, [sys.executable, '-u', temp_file], env
                    )
                    
                    print(f"[DEBUG] 进程返回码: {return_code}")
                    print(f"[DEBUG] stdout行数: {len(stdout_lines)}")
                    print(f"[DEBUG] stderr行数: {len(stderr_lines)}")
                    
                    # 异步推送日志
                    for output in stdout_lines:
                        print(f"[DEBUG] stdout: {output}")
                        if "SCREENSHOT:" in output:
                            await self._handle_screenshot(task_id, output)
                        else:
                            await manager.send_task_update(task_id, {
                                "type": "log",
                                "message": f"[{now_local().strftime('%H:%M:%S')}] {output}",
                                "level": "info"
                            })
                    
                    # 推送错误日志
                    has_error = False
                    for output in stderr_lines:
                        if output:
                            print(f"[DEBUG] stderr: {output}")
                            # 检查是否是真正的错误（不是警告）
                            if any(keyword in output for keyword in ['Traceback', 'Error:', 'Exception:', 'Failed']):
                                has_error = True
                            await manager.send_task_update(task_id, {
                                "type": "log",
                                "message": f"[{now_local().strftime('%H:%M:%S')}] [ERROR] {output}",
                                "level": "error"
                            })
                    
                    stderr = '\n'.join(stderr_lines)
                    
                    # 即使返回码是0，如果stderr包含错误信息，也应该报告
                    if return_code == 0 and has_error:
                        print(f"[DEBUG] 检测到错误信息，虽然返回码是0")
                        return_code = 1  # 强制设置为失败
                    
                else:
                    # Unix/Linux: 使用asyncio.create_subprocess_exec
                    process = await asyncio.create_subprocess_exec(
                        sys.executable, temp_file,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        env=env
                    )
                    
                    # 同时读取stdout和stderr，避免管道阻塞
                    async def read_stream(stream, is_stderr=False):
                        lines = []
                        while True:
                            line = await stream.readline()
                            if not line:
                                break
                            output = line.decode('utf-8', errors='replace').strip()
                            if output:
                                lines.append(output)
                                if not is_stderr:
                                    # 检测截图标记
                                    if "SCREENSHOT:" in output:
                                        await self._handle_screenshot(task_id, output)
                                    else:
                                        await manager.send_task_update(task_id, {
                                            "type": "log",
                                            "message": f"[{now_local().strftime('%H:%M:%S')}] {output}",
                                            "level": "info"
                                        })
                                else:
                                    # 实时显示错误输出
                                    await manager.send_task_update(task_id, {
                                        "type": "log",
                                        "message": f"[{now_local().strftime('%H:%M:%S')}] [ERROR] {output}",
                                        "level": "error"
                                    })
                        return lines
                    
                    # 并发读取stdout和stderr
                    stdout_task = asyncio.create_task(read_stream(process.stdout, False))
                    stderr_task = asyncio.create_task(read_stream(process.stderr, True))
                    
                    # 等待进程结束和所有输出读取完成
                    return_code = await process.wait()
                    stdout_lines = await stdout_task
                    stderr_lines = await stderr_task
                    
                    # 合并错误输出
                    stderr = '\n'.join(stderr_lines)
                
                # 检查是否是缺少依赖的错误
                if return_code != 0 and stderr:
                    # 匹配常见的模块缺失错误
                    # ModuleNotFoundError: No module named 'xxx'
                    # ImportError: No module named xxx
                    missing_module = None
                    
                    module_patterns = [
                        r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]",
                        r"ImportError: No module named ['\"]?([^'\"]+)['\"]?",
                    ]
                    
                    for pattern in module_patterns:
                        match = re.search(pattern, stderr)
                        if match:
                            missing_module = match.group(1)
                            break
                    
                    if missing_module and retry_count < max_retries - 1:
                        if not settings.ENABLE_AUTO_PIP_INSTALL:
                            raise Exception(f"缺少依赖: {missing_module}，已禁用自动安装")
                        if not settings.ENABLE_AUTO_PIP_INSTALL:
                            raise Exception(f"????: {missing_module}????????")
                        # 发现缺失模块，尝试安装
                        await manager.send_task_update(task_id, {
                            "type": "log",
                            "message": f"[{now_local().strftime('%H:%M:%S')}] ⚠️ 检测到缺失依赖: {missing_module}",
                            "level": "warning"
                        })
                        
                        # 更新进度：开始安装依赖
                        install_progress = 50 + (retry_count * 10)  # 50%, 60%, 70%
                        await manager.send_task_update(task_id, {
                            "status": "running",
                            "progress": install_progress,
                            "message": f"🔧 正在安装依赖: {missing_module}..."
                        })
                        
                        await manager.send_task_update(task_id, {
                            "type": "log",
                            "message": f"[{now_local().strftime('%H:%M:%S')}] 🔧 正在自动安装依赖: {missing_module}...",
                            "level": "info"
                        })
                        
                        # 安装依赖
                        install_success = await self._install_package(task_id, missing_module, install_progress)
                        
                        if install_success:
                            # 更新进度：安装完成
                            await manager.send_task_update(task_id, {
                                "status": "running",
                                "progress": install_progress + 5,
                                "message": f"✅ 依赖 {missing_module} 安装成功，重新执行脚本..."
                            })
                            
                            await manager.send_task_update(task_id, {
                                "type": "log",
                                "message": f"[{now_local().strftime('%H:%M:%S')}] ✅ 依赖安装成功，重新执行脚本...",
                                "level": "success"
                            })
                            retry_count += 1
                            continue  # 重新执行脚本
                        else:
                            await manager.send_task_update(task_id, {
                                "type": "log",
                                "message": f"[{now_local().strftime('%H:%M:%S')}] ❌ 依赖安装失败",
                                "level": "error"
                            })
                            raise Exception(f"无法安装依赖: {missing_module}")
                    else:
                        # 不是依赖问题或已达到最大重试次数
                        await manager.send_task_update(task_id, {
                            "type": "log",
                            "message": f"[{now_local().strftime('%H:%M:%S')}] 错误输出: {stderr}",
                            "level": "error"
                        })
                        # 提取实际的错误信息
                        error_detail = stderr.strip() if stderr else "未知错误"
                        # 只取最后几行关键错误信息
                        error_lines = error_detail.split('\n')
                        if len(error_lines) > 3:
                            error_detail = '\n'.join(error_lines[-3:])
                        raise Exception(f"Python脚本执行失败: {error_detail}")
                
                # 执行成功，跳出循环
                if return_code == 0:
                    await manager.send_task_update(task_id, {
                        "type": "log",
                        "message": f"[{now_local().strftime('%H:%M:%S')}] ✅ Python脚本执行成功",
                        "level": "success"
                    })
                    break
            
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass
    
    async def _install_package(self, task_id: int, package_name: str, base_progress: int = 50) -> bool:
        """安装Python包（带进度更新）"""
        try:
            # 使用asyncio异步执行pip安装
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pip", "install", package_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 同时读取stdout和stderr
            async def read_stream(stream, is_stderr=False):
                lines = []
                line_count = 0
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    output = line.decode('utf-8', errors='replace').strip()
                    if output:
                        lines.append(output)
                        if not is_stderr:
                            line_count += 1
                            # 每5行更新一次进度（避免过于频繁）
                            if line_count % 5 == 0:
                                # 进度在base_progress到base_progress+5之间变化
                                micro_progress = min(base_progress + (line_count // 5) % 5, base_progress + 4)
                                await manager.send_task_update(task_id, {
                                    "status": "running",
                                    "progress": micro_progress,
                                    "message": f"🔧 正在安装依赖: {package_name}..."
                                })
                            
                            await manager.send_task_update(task_id, {
                                "type": "log",
                                "message": f"[{now_local().strftime('%H:%M:%S')}] [pip] {output}",
                                "level": "debug"
                            })
                        else:
                            await manager.send_task_update(task_id, {
                                "type": "log",
                                "message": f"[{now_local().strftime('%H:%M:%S')}] [pip] [ERROR] {output}",
                                "level": "error"
                            })
                return lines
            
            # 并发读取stdout和stderr
            stdout_task = asyncio.create_task(read_stream(process.stdout, False))
            stderr_task = asyncio.create_task(read_stream(process.stderr, True))
            
            # 等待进程结束
            return_code = await process.wait()
            stdout_lines = await stdout_task
            stderr_lines = await stderr_task
            
            if return_code != 0:
                stderr = '\n'.join(stderr_lines)
                await manager.send_task_update(task_id, {
                    "type": "log",
                    "message": f"[{now_local().strftime('%H:%M:%S')}] [pip] 安装失败: {stderr}",
                    "level": "error"
                })
                return False
            
            return True
            
        except Exception as e:
            await manager.send_task_update(task_id, {
                "type": "log",
                "message": f"[{now_local().strftime('%H:%M:%S')}] 安装异常: {str(e)}",
                "level": "error"
            })
            return False
    
    async def _execute_batch_script(self, task_id: int, script, device_serial: str):
        """执行批处理脚本"""
        import tempfile
        import subprocess
        import os
        
        await manager.send_task_update(task_id, {
            "type": "log",
            "message": f"[{now_local().strftime('%H:%M:%S')}] 创建临时批处理文件...",
            "level": "info"
        })
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='utf-8') as f:
            # 在脚本开头添加设备信息
            script_content = f"""@echo off
REM 自动生成的脚本执行文件
REM 目标设备: {device_serial}
REM 脚本名称: {script.name}

REM 设置设备序列号
set DEVICE_SERIAL={device_serial}

REM 原始脚本内容
{script.file_content or 'REM 脚本内容为空'}
"""
            f.write(script_content)
            temp_file = f.name
        
        try:
            await manager.send_task_update(task_id, {
                "status": "running",
                "progress": 50,
                "message": "正在执行批处理脚本..."
            })
            
            await manager.send_task_update(task_id, {
                "type": "log",
                "message": f"[{now_local().strftime('%H:%M:%S')}] 执行命令: {temp_file}",
                "level": "info"
            })
            
            # 执行批处理脚本
            process = await asyncio.create_subprocess_exec(
                temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
            
            # 同时读取stdout和stderr，避免管道阻塞
            async def read_stream(stream, is_stderr=False):
                lines = []
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    output = line.decode('utf-8', errors='replace').strip()
                    if output:
                        lines.append(output)
                        if not is_stderr:
                            # 检测截图标记
                            if "SCREENSHOT:" in output:
                                await self._handle_screenshot(task_id, output)
                            else:
                                await manager.send_task_update(task_id, {
                                    "type": "log",
                                    "message": f"[{now_local().strftime('%H:%M:%S')}] {output}",
                                    "level": "info"
                                })
                        else:
                            # 实时显示错误输出
                            await manager.send_task_update(task_id, {
                                "type": "log",
                                "message": f"[{now_local().strftime('%H:%M:%S')}] [ERROR] {output}",
                                "level": "error"
                            })
                return lines
            
            # 并发读取stdout和stderr
            stdout_task = asyncio.create_task(read_stream(process.stdout, False))
            stderr_task = asyncio.create_task(read_stream(process.stderr, True))
            
            # 等待进程结束和所有输出读取完成
            return_code = await process.wait()
            stdout_lines = await stdout_task
            stderr_lines = await stderr_task
            
            # 合并错误输出
            stderr = '\n'.join(stderr_lines)
            if stderr:
                await manager.send_task_update(task_id, {
                    "type": "log",
                    "message": f"[{now_local().strftime('%H:%M:%S')}] 错误输出: {stderr}",
                    "level": "error"
                })
            
            if return_code != 0:
                # 提取实际的错误信息
                error_detail = stderr.strip() if stderr else "未知错误"
                # 只取最后几行关键错误信息
                error_lines = error_detail.split('\n')
                if len(error_lines) > 3:
                    error_detail = '\n'.join(error_lines[-3:])
                raise Exception(f"批处理脚本执行失败: {error_detail}")
            
            await manager.send_task_update(task_id, {
                "type": "log",
                "message": f"[{now_local().strftime('%H:%M:%S')}] 批处理脚本执行成功",
                "level": "success"
            })
            
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass

    
    async def _handle_screenshot(self, task_id: int, output_line: str):
        """处理截图标记，读取并推送截图"""
        import os
        import base64
        from PIL import Image
        import io
        
        try:
            # 提取文件名: "SCREENSHOT:step_01_app_started_1234567890.png"
            if "SCREENSHOT:" not in output_line:
                return
            
            filename = output_line.split("SCREENSHOT:")[1].strip()
            
            # 提取步骤名称
            step_name = filename.replace("step_", "").replace(".png", "")
            # 移除时间戳部分（最后的数字）
            parts = step_name.rsplit("_", 1)
            if len(parts) == 2 and parts[1].isdigit():
                step_name = parts[0]
            
            # 查找截图文件（可能在当前目录或uploads/screenshots目录）
            possible_paths = [
                filename,
                f"./{filename}",
                f"./uploads/screenshots/{filename}",
                f"uploads/screenshots/{filename}",
            ]
            
            screenshot_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    screenshot_path = path
                    break
            
            if not screenshot_path:
                await manager.send_task_update(task_id, {
                    "type": "log",
                    "message": f"[{now_local().strftime('%H:%M:%S')}] ⚠️ 截图文件未找到: {filename}",
                    "level": "warning"
                })
                return
            
            # 读取并压缩图片
            with Image.open(screenshot_path) as img:
                # 缩小到50%以减少传输量
                width, height = img.size
                new_size = (width // 2, height // 2)
                img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # 转换为JPEG并压缩
                buffer = io.BytesIO()
                if img_resized.mode == 'RGBA':
                    img_resized = img_resized.convert('RGB')
                img_resized.save(buffer, format='JPEG', quality=70, optimize=True)
                
                # 转换为base64
                image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # 推送截图到前端
            await manager.send_task_update(task_id, {
                "type": "screenshot",
                "step_name": step_name,
                "filename": filename,
                "image_data": image_data,
                "timestamp": now_local().isoformat()
            })
            
            await manager.send_task_update(task_id, {
                "type": "log",
                "message": f"[{now_local().strftime('%H:%M:%S')}] 📸 步骤截图: {step_name}",
                "level": "info"
            })
            
        except Exception as e:
            await manager.send_task_update(task_id, {
                "type": "log",
                "message": f"[{now_local().strftime('%H:%M:%S')}] ❌ 处理截图失败: {str(e)}",
                "level": "error"
            })
