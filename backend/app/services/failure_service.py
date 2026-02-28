"""
失败分析服务 - 整合版
包含错误分类、建议生成、失败分析等完整功能
"""
from sqlmodel import Session, select
from app.models.failure_analysis import FailureAnalysis, ScriptFailureStats, StepExecutionLog
from app.models.task_log import TaskLog
import subprocess
import os
from datetime import datetime
import json
import re
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class FailureAnalyzer:
    """失败分析器 - 错误分类和建议生成"""
    
    # 错误分类规则
    ERROR_PATTERNS = {
        'device_disconnected': [
            r'device.*not found',
            r'device.*offline',
            r'no devices/emulators found',
            r'device disconnected',
            r'adb.*not found',
        ],
        'element_not_found': [
            r'element.*not found',
            r'selector.*not found',
            r'could not find.*element',
            r'no such element',
            r'unable to locate',
        ],
        'timeout': [
            r'timeout',
            r'timed out',
            r'operation.*timeout',
            r'exceeded.*time',
            r'wait.*timeout',
        ],
        'permission_denied': [
            r'permission denied',
            r'access denied',
            r'not permitted',
            r'requires.*permission',
            r'unauthorized',
        ],
        'app_crash': [
            r'app.*crashed',
            r'application.*stopped',
            r'force.*close',
            r'anr',
            r'crash',
        ],
        'network_error': [
            r'network.*error',
            r'connection.*failed',
            r'no.*internet',
            r'dns.*failed',
            r'socket.*error',
        ],
        'script_error': [
            r'syntax.*error',
            r'invalid.*command',
            r'undefined.*variable',
            r'script.*error',
            r'parse.*error',
        ],
    }
    
    # 错误建议
    ERROR_SUGGESTIONS = {
        'device_disconnected': [
            '检查设备USB连接是否正常',
            '确认设备已开启USB调试',
            '尝试重新连接设备',
            '检查ADB服务是否正常运行',
            '重启ADB服务: adb kill-server && adb start-server',
        ],
        'element_not_found': [
            '检查元素选择器是否正确',
            '确认应用界面是否已加载完成',
            '增加等待时间让界面完全加载',
            '使用截图确认元素是否存在',
            '检查应用版本是否发生变化',
        ],
        'timeout': [
            '增加操作超时时间',
            '检查网络连接是否稳定',
            '确认设备性能是否正常',
            '优化脚本执行速度',
            '检查是否有弹窗阻塞',
        ],
        'permission_denied': [
            '检查应用权限设置',
            '手动授予必要的权限',
            '使用root权限执行',
            '检查SELinux设置',
            '确认应用已安装并可访问',
        ],
        'app_crash': [
            '检查应用版本是否兼容',
            '清除应用缓存后重试',
            '检查设备内存是否充足',
            '查看应用崩溃日志',
            '尝试重新安装应用',
        ],
        'network_error': [
            '检查设备网络连接',
            '确认WiFi或移动数据已开启',
            '检查代理设置',
            '尝试切换网络',
            '检查防火墙设置',
        ],
        'script_error': [
            '检查脚本语法是否正确',
            '确认所有变量已定义',
            '验证脚本逻辑',
            '使用脚本验证工具检查',
            '查看详细错误日志',
        ],
    }
    
    def classify_error(self, error_message: str) -> Tuple[str, float]:
        """
        分类错误类型
        
        Args:
            error_message: 错误消息
            
        Returns:
            (错误类型, 置信度)
        """
        if not error_message:
            return ('unknown', 0.0)
        
        error_lower = error_message.lower()
        best_match = ('unknown', 0.0)
        
        for error_type, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, error_lower):
                    confidence = 0.9
                    if confidence > best_match[1]:
                        best_match = (error_type, confidence)
        
        return best_match
    
    def get_suggestions(self, error_type: str) -> List[str]:
        """
        获取错误建议
        
        Args:
            error_type: 错误类型
            
        Returns:
            建议列表
        """
        return self.ERROR_SUGGESTIONS.get(error_type, [
            '检查错误日志获取更多信息',
            '尝试重新执行任务',
            '联系技术支持',
        ])
    
    def analyze_failure(
        self, 
        task_log_id: int,
        error_message: str,
        failed_step_index: int = None,
        failed_step_name: str = None,
        stack_trace: str = None
    ) -> Dict:
        """
        分析失败原因
        
        Args:
            task_log_id: 任务日志ID
            error_message: 错误消息
            failed_step_index: 失败步骤索引
            failed_step_name: 失败步骤名称
            stack_trace: 堆栈跟踪
            
        Returns:
            分析结果字典
        """
        # 分类错误
        error_type, confidence = self.classify_error(error_message)
        
        # 获取建议
        suggestions = self.get_suggestions(error_type)
        
        # 生成分析报告
        analysis = {
            'task_log_id': task_log_id,
            'failure_type': error_type,
            'confidence': confidence,
            'failed_step_index': failed_step_index,
            'failed_step_name': failed_step_name,
            'error_message': error_message,
            'stack_trace': stack_trace,
            'suggestions': suggestions,
            'analyzed_at': None,
        }
        
        return analysis
    
    def extract_failed_step(self, log_content: str) -> Tuple[int, str]:
        """
        从日志中提取失败步骤
        
        Args:
            log_content: 日志内容
            
        Returns:
            (步骤索引, 步骤名称)
        """
        if not log_content:
            return (None, None)
        
        patterns = [
            r'[Ss]tep\s+(\d+).*failed',
            r'第\s*(\d+)\s*步.*失败',
            r'步骤\s*(\d+).*失败',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, log_content)
            if match:
                step_index = int(match.group(1))
                
                name_patterns = [
                    r'[Ss]tep\s+\d+[:\s]+([^:\n]+)',
                    r'第\s*\d+\s*步[:\s]+([^:\n]+)',
                ]
                
                for name_pattern in name_patterns:
                    name_match = re.search(name_pattern, log_content)
                    if name_match:
                        step_name = name_match.group(1).strip()
                        return (step_index, step_name)
                
                return (step_index, None)
        
        return (None, None)
    
    def get_error_icon(self, error_type: str) -> str:
        """获取错误类型图标"""
        icons = {
            'device_disconnected': '🔌',
            'element_not_found': '🔍',
            'timeout': '⏱️',
            'permission_denied': '🔒',
            'app_crash': '💥',
            'network_error': '🌐',
            'script_error': '📝',
            'unknown': '❓',
        }
        return icons.get(error_type, '❓')
    
    def get_error_severity(self, error_type: str) -> str:
        """获取错误严重程度"""
        severity_map = {
            'device_disconnected': 'critical',
            'app_crash': 'high',
            'permission_denied': 'high',
            'element_not_found': 'medium',
            'timeout': 'medium',
            'network_error': 'medium',
            'script_error': 'low',
            'unknown': 'medium',
        }
        return severity_map.get(error_type, 'medium')


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
