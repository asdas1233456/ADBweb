"""
任务执行器 - 支持实时推送
"""
import asyncio
import sys
from datetime import datetime
from app.core.websocket_manager import manager
from typing import List, Dict


class TaskExecutor:
    """任务执行器"""
    
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
            "start_time": datetime.now().isoformat()
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
                    "message": f"[{datetime.now().strftime('%H:%M:%S')}] 开始执行: {step.get('name', '未命名步骤')}",
                    "level": "info"
                })
                
                # 执行步骤
                await self._execute_step(task_id, step, device_id)
                
                # 推送步骤完成
                await manager.send_task_update(task_id, {
                    "type": "log",
                    "message": f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 第 {current_step} 步执行完成",
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
                "end_time": datetime.now().isoformat()
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
                "end_time": datetime.now().isoformat()
            })
            
            return {"status": "failed", "message": str(e)}
    
    async def _execute_step(self, task_id: int, step: Dict, device_id: int):
        """执行单个步骤"""
        step_type = step.get("type")
        
        # 推送详细日志
        await manager.send_task_update(task_id, {
            "type": "log",
            "message": f"[{datetime.now().strftime('%H:%M:%S')}] 执行 {step_type} 操作",
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
                "message": f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 元素未找到: {selector}",
                "level": "error"
            })
            raise Exception(f"Element not found: {selector}")
        
        await manager.send_task_update(task_id, {
            "type": "log",
            "message": f"[{datetime.now().strftime('%H:%M:%S')}] 点击坐标 ({x}, {y})",
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
            "message": f"[{datetime.now().strftime('%H:%M:%S')}] 输入文本: {text}",
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
            "message": f"[{datetime.now().strftime('%H:%M:%S')}] 滑动: ({x1},{y1}) -> ({x2},{y2})",
            "level": "debug"
        })
        
        await asyncio.sleep(0.5)
    
    async def _execute_wait(self, task_id: int, step: Dict, device_id: int):
        """执行等待操作"""
        config = step.get("config", {})
        duration = config.get("duration", 1000) / 1000  # 转换为秒
        
        await manager.send_task_update(task_id, {
            "type": "log",
            "message": f"[{datetime.now().strftime('%H:%M:%S')}] 等待 {duration} 秒",
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
        
        # 初始化任务
        await manager.send_task_update(task_id, {
            "status": "running",
            "progress": 0,
            "message": f"开始执行{script.type}脚本: {script.name}",
            "start_time": datetime.now().isoformat()
        })
        
        try:
            # 推送日志
            await manager.send_task_update(task_id, {
                "type": "log",
                "message": f"[{datetime.now().strftime('%H:%M:%S')}] 准备执行脚本: {script.name}",
                "level": "info"
            })
            
            # 获取设备信息
            from app.core.database import engine
            from sqlmodel import Session
            from app.models.device import Device
            
            with Session(engine) as db:
                device = db.get(Device, device_id)
                device_serial = device.serial_number if device else "unknown"
            
            await manager.send_task_update(task_id, {
                "type": "log",
                "message": f"[{datetime.now().strftime('%H:%M:%S')}] 目标设备: {device_serial}",
                "level": "info"
            })
            
            # 更新进度
            await manager.send_task_update(task_id, {
                "status": "running",
                "progress": 25,
                "message": "正在准备执行环境..."
            })
            
            if script.type == "python":
                await self._execute_python_script(task_id, script, device_serial)
            elif script.type == "batch":
                await self._execute_batch_script(task_id, script, device_serial)
            
            # 任务完成
            await manager.send_task_update(task_id, {
                "status": "success",
                "progress": 100,
                "message": f"✅ {script.type}脚本执行完成",
                "end_time": datetime.now().isoformat()
            })
            
            return {"status": "success", "message": f"{script.type}脚本执行成功"}
            
        except Exception as e:
            # 任务失败
            await manager.send_task_update(task_id, {
                "status": "failed",
                "progress": 50,
                "message": f"❌ {script.type}脚本执行失败: {str(e)}",
                "error": str(e),
                "end_time": datetime.now().isoformat()
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
            "message": f"[{datetime.now().strftime('%H:%M:%S')}] 创建临时Python文件...",
            "level": "info"
        })
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            # 在脚本开头添加设备信息
            script_content = f"""# 自动生成的脚本执行文件
# 目标设备: {device_serial}
# 脚本名称: {script.name}

import os
import sys
import subprocess

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
                "message": f"[{datetime.now().strftime('%H:%M:%S')}] 执行命令: python {temp_file}",
                "level": "info"
            })
            
            # 首次执行Python脚本
            max_retries = 3  # 最多重试3次（用于安装依赖）
            retry_count = 0
            
            while retry_count < max_retries:
                process = subprocess.Popen(
                    [sys.executable, temp_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8'
                )
                
                # 实时读取输出
                stdout_lines = []
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        stdout_lines.append(output.strip())
                        await manager.send_task_update(task_id, {
                            "type": "log",
                            "message": f"[{datetime.now().strftime('%H:%M:%S')}] {output.strip()}",
                            "level": "info"
                        })
                
                # 获取返回码
                return_code = process.poll()
                
                # 获取错误输出
                stderr = process.stderr.read()
                
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
                        # 发现缺失模块，尝试安装
                        await manager.send_task_update(task_id, {
                            "type": "log",
                            "message": f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ 检测到缺失依赖: {missing_module}",
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
                            "message": f"[{datetime.now().strftime('%H:%M:%S')}] 🔧 正在自动安装依赖: {missing_module}...",
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
                                "message": f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 依赖安装成功，重新执行脚本...",
                                "level": "success"
                            })
                            retry_count += 1
                            continue  # 重新执行脚本
                        else:
                            await manager.send_task_update(task_id, {
                                "type": "log",
                                "message": f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 依赖安装失败",
                                "level": "error"
                            })
                            raise Exception(f"无法安装依赖: {missing_module}")
                    else:
                        # 不是依赖问题或已达到最大重试次数
                        await manager.send_task_update(task_id, {
                            "type": "log",
                            "message": f"[{datetime.now().strftime('%H:%M:%S')}] 错误输出: {stderr}",
                            "level": "error"
                        })
                        raise Exception(f"Python脚本执行失败，返回码: {return_code}")
                
                # 执行成功，跳出循环
                if return_code == 0:
                    await manager.send_task_update(task_id, {
                        "type": "log",
                        "message": f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Python脚本执行成功",
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
        import subprocess
        
        try:
            # 使用pip安装包
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            # 实时读取安装输出并更新进度
            line_count = 0
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
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
                        "message": f"[{datetime.now().strftime('%H:%M:%S')}] [pip] {output.strip()}",
                        "level": "debug"
                    })
            
            return_code = process.poll()
            
            if return_code != 0:
                stderr = process.stderr.read()
                await manager.send_task_update(task_id, {
                    "type": "log",
                    "message": f"[{datetime.now().strftime('%H:%M:%S')}] [pip] 错误: {stderr}",
                    "level": "error"
                })
                return False
            
            return True
            
        except Exception as e:
            await manager.send_task_update(task_id, {
                "type": "log",
                "message": f"[{datetime.now().strftime('%H:%M:%S')}] 安装异常: {str(e)}",
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
            "message": f"[{datetime.now().strftime('%H:%M:%S')}] 创建临时批处理文件...",
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
                "message": f"[{datetime.now().strftime('%H:%M:%S')}] 执行命令: {temp_file}",
                "level": "info"
            })
            
            # 执行批处理脚本
            process = subprocess.Popen(
                temp_file,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                shell=True
            )
            
            # 实时读取输出
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    await manager.send_task_update(task_id, {
                        "type": "log",
                        "message": f"[{datetime.now().strftime('%H:%M:%S')}] {output.strip()}",
                        "level": "info"
                    })
            
            # 获取返回码
            return_code = process.poll()
            
            # 获取错误输出
            stderr = process.stderr.read()
            if stderr:
                await manager.send_task_update(task_id, {
                    "type": "log",
                    "message": f"[{datetime.now().strftime('%H:%M:%S')}] 错误输出: {stderr}",
                    "level": "error"
                })
            
            if return_code != 0:
                raise Exception(f"批处理脚本执行失败，返回码: {return_code}")
            
            await manager.send_task_update(task_id, {
                "type": "log",
                "message": f"[{datetime.now().strftime('%H:%M:%S')}] 批处理脚本执行成功",
                "level": "success"
            })
            
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass
