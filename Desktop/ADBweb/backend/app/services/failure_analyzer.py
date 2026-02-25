"""
失败分析器 - 错误分类和建议生成
"""
from typing import Dict, List, Tuple
import re


class FailureAnalyzer:
    """失败分析器"""
    
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
                    # 简单的置信度计算
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
            'analyzed_at': None,  # 将在保存时设置
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
        
        # 查找类似 "Step 3 failed" 或 "第3步失败" 的模式
        patterns = [
            r'[Ss]tep\s+(\d+).*failed',
            r'第\s*(\d+)\s*步.*失败',
            r'步骤\s*(\d+).*失败',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, log_content)
            if match:
                step_index = int(match.group(1))
                
                # 尝试提取步骤名称
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
        """
        获取错误类型图标
        
        Args:
            error_type: 错误类型
            
        Returns:
            图标emoji
        """
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
        """
        获取错误严重程度
        
        Args:
            error_type: 错误类型
            
        Returns:
            严重程度: critical/high/medium/low
        """
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
