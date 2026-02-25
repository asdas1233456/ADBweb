"""
任务执行器 - 支持实时推送
"""
import asyncio
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
                
                # 模拟执行时间
                await asyncio.sleep(1)
            
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
