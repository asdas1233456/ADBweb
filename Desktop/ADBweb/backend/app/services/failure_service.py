"""
失败分析服务
"""
from sqlmodel import Session, select
from app.models.failure_analysis import FailureAnalysis, ScriptFailureStats, StepExecutionLog
from app.models.task_log import TaskLog
from app.services.failure_analyzer import FailureAnalyzer
import subprocess
import os
from datetime import datetime
import json


class FailureService:
    """失败分析服务"""
    
    def __init__(self, session: Session):
        self.session = session
        self.analyzer = FailureAnalyzer()
    
    async def analyze_task_failure(self, task_log_id: int) -> FailureAnalysis:
        """
        分析任务失败
        
        Args:
            task_log_id: 任务日志ID
            
        Returns:
            失败分析记录
        """
        # 获取任务日志
        task_log = self.session.get(TaskLog, task_log_id)
        if not task_log or task_log.status != 'failed':
            return None
        
        # 检查是否已分析
        statement = select(FailureAnalysis).where(
            FailureAnalysis.task_log_id == task_log_id
        )
        existing = self.session.exec(statement).first()
        if existing:
            return existing
        
        # 提取失败步骤
        failed_step_index, failed_step_name = self.analyzer.extract_failed_step(
            task_log.log_content or ''
        )
        
        # 分析失败原因
        analysis_result = self.analyzer.analyze_failure(
            task_log_id=task_log_id,
            error_message=task_log.error_message or '',
            failed_step_index=failed_step_index,
            failed_step_name=failed_step_name,
            stack_trace=None
        )
        
        # 自动截图
        screenshot_path = None
        if task_log.device_id:
            screenshot_path = await self._capture_failure_screenshot(
                task_log.device_id,
                task_log_id
            )
        
        # 保存分析结果
        failure_analysis = FailureAnalysis(
            task_log_id=task_log_id,
            failure_type=analysis_result['failure_type'],
            failed_step_index=failed_step_index,
            failed_step_name=failed_step_name,
            error_message=analysis_result['error_message'],
            stack_trace=analysis_result['stack_trace'],
            screenshot_path=screenshot_path,
            suggestions=','.join(analysis_result['suggestions']),
            confidence=analysis_result['confidence'],
            is_auto_analyzed=True
        )
        
        self.session.add(failure_analysis)
        self.session.commit()
        self.session.refresh(failure_analysis)
        
        # 更新脚本失败统计
        if task_log.script_id:
            await self._update_failure_stats(
                task_log.script_id, 
                analysis_result['failure_type']
            )
        
        print(f"📊 失败分析完成: 任务{task_log_id}, 类型: {analysis_result['failure_type']}")
        
        return failure_analysis
    
    async def _capture_failure_screenshot(self, device_id: int, task_log_id: int) -> str:
        """
        捕获失败时的截图
        
        Args:
            device_id: 设备ID
            task_log_id: 任务日志ID
            
        Returns:
            截图路径
        """
        try:
            from app.models.device import Device
            device = self.session.get(Device, device_id)
            if not device:
                return None
            
            # 创建截图目录
            screenshot_dir = 'uploads/screenshots/failures'
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # 生成截图文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'failure_{task_log_id}_{timestamp}.png'
            filepath = os.path.join(screenshot_dir, filename)
            
            # 执行截图命令 (模拟)
            # 实际环境中使用:
            # result = subprocess.run(
            #     ['adb', '-s', device.serial_number, 'exec-out', 'screencap', '-p'],
            #     stdout=open(filepath, 'wb'),
            #     timeout=10
            # )
            
            # 模拟截图成功
            print(f"📸 失败截图已保存: {filepath}")
            return filepath
        
        except Exception as e:
            print(f'⚠️ 截图失败: {e}')
        
        return None
    
    async def _update_failure_stats(self, script_id: int, failure_type: str):
        """
        更新脚本失败统计
        
        Args:
            script_id: 脚本ID
            failure_type: 失败类型
        """
        # 获取或创建统计记录
        statement = select(ScriptFailureStats).where(
            ScriptFailureStats.script_id == script_id
        )
        stats = self.session.exec(statement).first()
        
        if not stats:
            stats = ScriptFailureStats(
                script_id=script_id,
                total_failures=0,
                failure_by_type='{}',
                most_common_failure=failure_type
            )
            self.session.add(stats)
        
        # 更新统计
        stats.total_failures += 1
        
        # 更新失败类型统计
        failure_by_type = json.loads(stats.failure_by_type) if stats.failure_by_type else {}
        failure_by_type[failure_type] = failure_by_type.get(failure_type, 0) + 1
        stats.failure_by_type = json.dumps(failure_by_type)
        
        # 更新最常见失败类型
        most_common = max(failure_by_type.items(), key=lambda x: x[1])
        stats.most_common_failure = most_common[0]
        
        # 计算失败率
        from app.models.task_log import TaskLog
        total_executions = self.session.exec(
            select(TaskLog).where(TaskLog.script_id == script_id)
        ).all()
        if total_executions:
            stats.failure_rate = (stats.total_failures / len(total_executions)) * 100
        
        stats.last_failure_time = datetime.now()
        stats.updated_at = datetime.now()
        
        self.session.commit()
    
    def log_step_execution(
        self,
        task_log_id: int,
        step_index: int,
        step_name: str,
        step_type: str,
        status: str,
        start_time: datetime = None,
        end_time: datetime = None,
        error_message: str = None
    ):
        """
        记录步骤执行日志
        
        Args:
            task_log_id: 任务日志ID
            step_index: 步骤索引
            step_name: 步骤名称
            step_type: 步骤类型
            status: 状态
            start_time: 开始时间
            end_time: 结束时间
            error_message: 错误消息
        """
        duration = None
        if start_time and end_time:
            duration = (end_time - start_time).total_seconds()
        
        step_log = StepExecutionLog(
            task_log_id=task_log_id,
            step_index=step_index,
            step_name=step_name,
            step_type=step_type,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            error_message=error_message
        )
        
        self.session.add(step_log)
        self.session.commit()
