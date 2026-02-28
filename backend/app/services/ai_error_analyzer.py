



"""
AI驱动的错误分析器
基于BERT-Tiny模型的智能错误分类和根因定位系统
"""
import re
import json
import hashlib
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LogPreprocessor:
    """日志预处理器"""
    
    # 敏感信息正则模式
    SENSITIVE_PATTERNS = {
        'serial': r'serial[:\s]+[A-Za-z0-9]{10,20}',  # 更精确的序列号匹配
        'device_id': r'\b[A-Z0-9]{15,20}\b',  # 只匹配长设备ID
        'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        'email': r'\b[\w\.-]+@[\w\.-]+\.\w+\b',
        'phone': r'\b1[3-9]\d{9}\b',
    }
    
    # 噪声模式
    NOISE_PATTERNS = [
        r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',  # 时间戳
        r'\[INFO\]|\[DEBUG\]|\[WARN\]|\[ERROR\]',  # 日志级别
        r'at\s+line\s+\d+',  # 行号
    ]
    
    def clean(self, log_text: str) -> str:
        """
        清洗日志文本
        
        Args:
            log_text: 原始日志文本
            
        Returns:
            清洗后的文本
        """
        if not log_text:
            return ""
        
        # 1. 脱敏处理
        cleaned = self._desensitize(log_text)
        
        # 2. 移除噪声
        cleaned = self._remove_noise(cleaned)
        
        # 3. 文本规范化
        cleaned = self._normalize(cleaned)
        
        return cleaned
    
    def _desensitize(self, text: str) -> str:
        """脱敏处理"""
        for key, pattern in self.SENSITIVE_PATTERNS.items():
            text = re.sub(pattern, f'[{key.upper()}]', text, flags=re.IGNORECASE)
        return text
    
    def _remove_noise(self, text: str) -> str:
        """移除噪声"""
        for pattern in self.NOISE_PATTERNS:
            text = re.sub(pattern, '', text)
        return text
    
    def _normalize(self, text: str) -> str:
        """文本规范化"""
        # 统一小写
        text = text.lower()
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符（保留基本标点和冒号）
        text = re.sub(r'[^\w\s\.\,\:\;\-\(\)]', '', text)
        return text.strip()
    
    def extract_features(self, log_text: str) -> Dict[str, any]:
        """
        提取日志特征
        
        Args:
            log_text: 日志文本
            
        Returns:
            特征字典
        """
        features = {
            'error_keywords': self._extract_error_keywords(log_text),
            'device_keywords': self._extract_device_keywords(log_text),
            'operation_keywords': self._extract_operation_keywords(log_text),
            'exception_types': self._extract_exception_types(log_text),
            'text_length': len(log_text),
            'has_stacktrace': 'traceback' in log_text.lower() or 'at ' in log_text,
        }
        return features
    
    def _extract_error_keywords(self, text: str) -> List[str]:
        """提取错误关键词"""
        keywords = ['error', 'failed', 'crash', 'timeout', 'exception', 'denied']
        return [kw for kw in keywords if kw in text.lower()]
    
    def _extract_device_keywords(self, text: str) -> List[str]:
        """提取设备关键词"""
        keywords = ['offline', 'disconnected', 'not found', 'unavailable']
        return [kw for kw in keywords if kw in text.lower()]
    
    def _extract_operation_keywords(self, text: str) -> List[str]:
        """提取操作关键词"""
        keywords = ['click', 'swipe', 'input', 'wait', 'scroll', 'tap']
        return [kw for kw in keywords if kw in text.lower()]
    
    def _extract_exception_types(self, text: str) -> List[str]:
        """提取异常类型"""
        pattern = r'(\w+Exception|\w+Error)'
        matches = re.findall(pattern, text)
        return list(set(matches))


class BERTTinyClassifier:
    """
    BERT-Tiny错误分类器
    
    注意: 这是一个简化的实现，实际部署时需要加载真实的BERT-Tiny模型
    """
    
    # 错误类型映射
    ERROR_TYPES = [
        'device_disconnected',
        'element_not_found',
        'permission_denied',
        'app_crash',
        'script_error',
        'network_timeout',
        'device_offline'
    ]
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化分类器
        
        Args:
            model_path: 模型文件路径（ONNX或TFLite）
        """
        self.model_path = model_path
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载模型"""
        if self.model_path:
            try:
                # 实际部署时使用ONNX Runtime或TFLite
                # import onnxruntime as ort
                # self.model = ort.InferenceSession(self.model_path)
                logger.info(f"模型加载成功: {self.model_path}")
            except Exception as e:
                logger.error(f"模型加载失败: {e}")
                self.model = None
        else:
            logger.warning("未指定模型路径，使用规则引擎作为后备")
    
    def predict(self, text: str, features: Dict = None) -> Tuple[str, float]:
        """
        预测错误类型
        
        Args:
            text: 清洗后的日志文本
            features: 提取的特征
            
        Returns:
            (错误类型, 置信度)
        """
        if self.model:
            return self._model_predict(text)
        else:
            # 后备方案: 使用规则引擎
            return self._rule_based_predict(text, features)
    
    def _model_predict(self, text: str) -> Tuple[str, float]:
        """
        使用BERT模型预测
        
        实际实现时的步骤:
        1. 文本分词 (tokenizer)
        2. 转换为input_ids
        3. 模型推理
        4. Softmax获取概率
        5. 返回最高概率的类别
        """
        # 这里是简化实现，实际需要真实的模型推理
        # tokenizer = BertTokenizer.from_pretrained('bert-tiny')
        # inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
        # outputs = self.model.run(None, {'input_ids': inputs['input_ids'].numpy()})
        # probs = softmax(outputs[0])
        # pred_idx = np.argmax(probs)
        # return self.ERROR_TYPES[pred_idx], float(probs[0][pred_idx])
        
        # 临时使用规则引擎
        return self._rule_based_predict(text, None)
    
    def _rule_based_predict(self, text: str, features: Dict = None) -> Tuple[str, float]:
        """基于规则的预测（后备方案）"""
        text_lower = text.lower()
        
        # 优化的规则匹配（按优先级排序）
        rules = [
            ('device_disconnected', [
                'device.*not found', 'device.*offline', 'no devices',
                'adb.*not found', 'device disconnected'
            ], 0.92),
            ('element_not_found', [
                'element.*not found', 'selector.*not found', 'no such element',
                'unable to locate', 'could not find.*element'
            ], 0.90),
            ('permission_denied', [
                'permission denied', 'permission denial', 'securityexception',
                'access denied', 'not permitted', 'requires.*permission',
                'unauthorized', 'lacks permission'
            ], 0.95),
            ('app_crash', [
                'app.*crashed', 'application.*stopped', 'force.*close',
                'anr', 'crash', 'fatal exception'
            ], 0.88),
            ('network_timeout', [
                'network.*error', 'connection.*failed', 'timeout',
                'timed out', 'dns.*failed', 'socket.*error'
            ], 0.85),
            ('script_error', [
                'syntax.*error', 'invalid.*command', 'undefined.*variable',
                'script.*error', 'parse.*error', 'indentation.*error'
            ], 0.93),
            ('device_offline', [
                'device.*offline', 'device.*unavailable', 'device.*not responding'
            ], 0.90),
        ]
        
        for error_type, patterns, base_confidence in rules:
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    # 根据匹配质量调整置信度
                    confidence = base_confidence
                    if features:
                        # 如果有特征，可以进一步调整置信度
                        if error_type.split('_')[0] in features.get('error_keywords', []):
                            confidence += 0.03
                    return (error_type, min(confidence, 0.99))
        
        return ('unknown', 0.50)



class RootCauseAnalyzer:
    """根因定位分析器"""
    
    def analyze(
        self,
        error_type: str,
        error_message: str,
        device_state: Dict = None,
        execution_context: Dict = None,
        historical_data: Dict = None
    ) -> Dict[str, str]:
        """
        多维度根因分析
        
        Args:
            error_type: 错误类型
            error_message: 错误消息
            device_state: 设备状态 (电量、内存、CPU等)
            execution_context: 执行上下文 (步骤、前置操作等)
            historical_data: 历史数据 (频率、趋势等)
            
        Returns:
            根因字典 {immediate, indirect, root}
        """
        # 1. 直接原因（从错误消息中提取）
        immediate_cause = self._extract_immediate_cause(error_type, error_message)
        
        # 2. 间接原因（结合执行上下文）
        indirect_cause = self._analyze_indirect_cause(
            error_type, execution_context
        )
        
        # 3. 根本原因（结合设备状态和历史数据）
        root_cause = self._analyze_root_cause(
            error_type, device_state, historical_data
        )
        
        return {
            'immediate': immediate_cause,
            'indirect': indirect_cause,
            'root': root_cause
        }
    
    def _extract_immediate_cause(self, error_type: str, error_message: str) -> str:
        """提取直接原因"""
        immediate_causes = {
            'device_disconnected': '设备连接断开',
            'element_not_found': '界面元素未找到',
            'permission_denied': '权限被拒绝',
            'app_crash': '应用程序崩溃',
            'script_error': '脚本语法错误',
            'network_timeout': '网络请求超时',
            'device_offline': '设备离线',
        }
        
        base_cause = immediate_causes.get(error_type, '未知错误')
        
        # 尝试从错误消息中提取更具体的信息
        if 'element' in error_message.lower():
            match = re.search(r'element[:\s]+([^\s,]+)', error_message, re.IGNORECASE)
            if match:
                return f"{base_cause}: {match.group(1)}"
        
        return base_cause
    
    def _analyze_indirect_cause(
        self, error_type: str, execution_context: Dict = None
    ) -> str:
        """分析间接原因"""
        if not execution_context:
            return "执行上下文信息不足"
        
        step_name = execution_context.get('step_name', '')
        previous_steps = execution_context.get('previous_steps', [])
        
        # 基于执行上下文的规则
        if error_type == 'element_not_found':
            if any('wait' not in step.lower() for step in previous_steps):
                return "界面加载未完成，缺少等待步骤"
            return "元素选择器可能不正确或界面已变化"
        
        elif error_type == 'network_timeout':
            if any('network' in step.lower() for step in previous_steps):
                return "连续网络请求导致超时"
            return "网络连接不稳定"
        
        elif error_type == 'app_crash':
            if len(previous_steps) > 5:
                return "长时间运行导致内存泄漏"
            return "应用状态异常"
        
        elif error_type == 'permission_denied':
            return "应用权限未正确配置"
        
        return f"执行步骤 '{step_name}' 时发生错误"
    
    def _analyze_root_cause(
        self,
        error_type: str,
        device_state: Dict = None,
        historical_data: Dict = None
    ) -> str:
        """分析根本原因"""
        if not device_state:
            return "设备状态信息不足"
        
        battery = device_state.get('battery', 100)
        memory_usage = device_state.get('memory_usage', 0)
        cpu_usage = device_state.get('cpu_usage', 0)
        
        # 设备状态规则
        if battery < 10:
            return "设备电量过低影响性能"
        
        if memory_usage > 85:
            if error_type in ['element_not_found', 'app_crash', 'network_timeout']:
                return "设备内存不足导致应用响应慢或崩溃"
        
        if cpu_usage > 90:
            return "设备CPU占用过高影响执行"
        
        # 历史数据规则
        if historical_data:
            failure_count = historical_data.get('failure_count', 0)
            if failure_count > 3:
                return "该设备频繁出现此类错误，可能存在兼容性问题"
        
        # 默认根因
        root_causes = {
            'device_disconnected': 'USB连接不稳定或ADB服务异常',
            'element_not_found': '应用版本更新导致界面变化',
            'permission_denied': '系统安全策略限制',
            'app_crash': '应用代码缺陷或设备兼容性问题',
            'script_error': '脚本逻辑错误或API变更',
            'network_timeout': '网络环境不稳定或服务器响应慢',
            'device_offline': '设备系统故障或电量耗尽',
        }
        
        return root_causes.get(error_type, "需要进一步分析")



class HealingSuggestionGenerator:
    """自愈建议生成器"""
    
    # ADB命令模板库
    HEALING_TEMPLATES = {
        'device_disconnected': [
            {
                'action': 'restart_adb',
                'command': 'adb kill-server && adb start-server',
                'description': '重启ADB服务',
                'success_rate': 0.85,
                'executable': True,
                'preconditions': []
            },
            {
                'action': 'reconnect_device',
                'command': 'adb reconnect {device_id}',
                'description': '重新连接设备',
                'success_rate': 0.75,
                'executable': True,
                'preconditions': []
            },
            {
                'action': 'check_usb',
                'command': None,
                'description': '检查USB连接线和端口',
                'success_rate': 0.60,
                'executable': False,
                'preconditions': []
            }
        ],
        'element_not_found': [
            {
                'action': 'wait_longer',
                'command': 'sleep 5',
                'description': '增加等待时间至5秒',
                'success_rate': 0.70,
                'executable': True,
                'preconditions': []
            },
            {
                'action': 'refresh_ui',
                'command': 'adb -s {device_id} shell input keyevent KEYCODE_HOME && adb -s {device_id} shell am start -n {package}/.MainActivity',
                'description': '刷新应用界面',
                'success_rate': 0.60,
                'executable': True,
                'preconditions': ['package']
            },
            {
                'action': 'take_screenshot',
                'command': 'adb -s {device_id} shell screencap -p /sdcard/screenshot.png',
                'description': '截图检查界面状态',
                'success_rate': 0.50,
                'executable': True,
                'preconditions': []
            }
        ],
        'permission_denied': [
            {
                'action': 'grant_permission',
                'command': 'adb -s {device_id} shell pm grant {package} {permission}',
                'description': '授予应用权限',
                'success_rate': 0.90,
                'executable': True,
                'preconditions': ['package', 'permission']
            },
            {
                'action': 'install_with_permissions',
                'command': 'adb -s {device_id} install -g {apk_path}',
                'description': '重新安装应用并授予所有权限',
                'success_rate': 0.85,
                'executable': True,
                'preconditions': ['apk_path']
            }
        ],
        'app_crash': [
            {
                'action': 'clear_cache',
                'command': 'adb -s {device_id} shell pm clear {package}',
                'description': '清除应用缓存和数据',
                'success_rate': 0.65,
                'executable': True,
                'preconditions': ['package']
            },
            {
                'action': 'restart_app',
                'command': 'adb -s {device_id} shell am force-stop {package} && adb -s {device_id} shell am start -n {package}/.MainActivity',
                'description': '强制停止并重启应用',
                'success_rate': 0.80,
                'executable': True,
                'preconditions': ['package']
            },
            {
                'action': 'free_memory',
                'command': 'adb -s {device_id} shell am kill-all',
                'description': '清理后台应用释放内存',
                'success_rate': 0.70,
                'executable': True,
                'preconditions': []
            }
        ],
        'network_timeout': [
            {
                'action': 'toggle_wifi',
                'command': 'adb -s {device_id} shell svc wifi disable && sleep 2 && adb -s {device_id} shell svc wifi enable',
                'description': '重启WiFi连接',
                'success_rate': 0.70,
                'executable': True,
                'preconditions': []
            },
            {
                'action': 'toggle_mobile_data',
                'command': 'adb -s {device_id} shell svc data disable && sleep 2 && adb -s {device_id} shell svc data enable',
                'description': '重启移动数据',
                'success_rate': 0.65,
                'executable': True,
                'preconditions': []
            },
            {
                'action': 'check_network',
                'command': 'adb -s {device_id} shell ping -c 4 8.8.8.8',
                'description': '检查网络连通性',
                'success_rate': 0.50,
                'executable': True,
                'preconditions': []
            }
        ],
        'script_error': [
            {
                'action': 'validate_script',
                'command': 'python -m py_compile {script_path}',
                'description': '验证脚本语法',
                'success_rate': 0.95,
                'executable': True,
                'preconditions': ['script_path']
            },
            {
                'action': 'check_dependencies',
                'command': 'pip list | grep {package_name}',
                'description': '检查依赖包是否安装',
                'success_rate': 0.85,
                'executable': True,
                'preconditions': ['package_name']
            }
        ],
        'device_offline': [
            {
                'action': 'reboot_device',
                'command': 'adb -s {device_id} reboot',
                'description': '重启设备',
                'success_rate': 0.85,
                'executable': True,
                'preconditions': ['battery_check']
            },
            {
                'action': 'wake_device',
                'command': 'adb -s {device_id} shell input keyevent KEYCODE_WAKEUP',
                'description': '唤醒设备屏幕',
                'success_rate': 0.75,
                'executable': True,
                'preconditions': []
            }
        ]
    }
    
    def generate(
        self,
        error_type: str,
        root_cause: Dict[str, str],
        device_state: Dict = None,
        context: Dict = None
    ) -> List[Dict]:
        """
        生成自愈建议
        
        Args:
            error_type: 错误类型
            root_cause: 根因分析结果
            device_state: 设备状态
            context: 上下文信息（包含package、device_id等）
            
        Returns:
            建议列表，按成功率排序
        """
        templates = self.HEALING_TEMPLATES.get(error_type, [])
        
        if not templates:
            return [{
                'action': 'manual_check',
                'command': None,
                'description': '需要人工检查和处理',
                'success_rate': 0.0,
                'executable': False
            }]
        
        # 过滤和排序建议
        suggestions = []
        for template in templates:
            # 检查前置条件
            if not self._check_preconditions(template, device_state, context):
                continue
            
            # 替换命令中的变量
            suggestion = template.copy()
            if suggestion['command'] and context:
                suggestion['command'] = self._replace_variables(
                    suggestion['command'], context
                )
            
            suggestions.append(suggestion)
        
        # 按成功率排序
        suggestions.sort(key=lambda x: x['success_rate'], reverse=True)
        
        return suggestions
    
    def _check_preconditions(
        self, template: Dict, device_state: Dict = None, context: Dict = None
    ) -> bool:
        """检查前置条件"""
        preconditions = template.get('preconditions', [])
        
        for condition in preconditions:
            if condition == 'battery_check':
                if device_state and device_state.get('battery', 100) < 10:
                    return False  # 电量过低不建议重启
            
            elif condition in ['package', 'device_id', 'permission', 'apk_path', 'script_path']:
                if not context or condition not in context:
                    return False  # 缺少必要参数
        
        return True
    
    def _replace_variables(self, command: str, context: Dict) -> str:
        """替换命令中的变量"""
        for key, value in context.items():
            placeholder = f'{{{key}}}'
            if placeholder in command:
                command = command.replace(placeholder, str(value))
        return command



class AIErrorAnalyzer:
    """AI错误分析器主类"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化分析器
        
        Args:
            model_path: BERT模型路径（可选）
        """
        self.preprocessor = LogPreprocessor()
        self.classifier = BERTTinyClassifier(model_path)
        self.root_cause_analyzer = RootCauseAnalyzer()
        self.suggestion_generator = HealingSuggestionGenerator()
        
        # 性能统计
        self.stats = {
            'total_analyzed': 0,
            'avg_inference_time_ms': 0,
            'accuracy': 0.0
        }
    
    def analyze(
        self,
        error_message: str,
        log_content: str = None,
        device_state: Dict = None,
        execution_context: Dict = None,
        historical_data: Dict = None,
        context: Dict = None
    ) -> Dict:
        """
        完整的错误分析流程
        
        Args:
            error_message: 错误消息
            log_content: 完整日志内容
            device_state: 设备状态
            execution_context: 执行上下文
            historical_data: 历史数据
            context: 其他上下文信息（device_id, package等）
            
        Returns:
            分析结果字典
        """
        start_time = datetime.now()
        
        # 1. 日志预处理
        cleaned_text = self.preprocessor.clean(error_message)
        features = self.preprocessor.extract_features(error_message)
        
        # 2. 错误分类
        error_type, confidence = self.classifier.predict(cleaned_text, features)
        
        # 3. 根因定位
        root_cause = self.root_cause_analyzer.analyze(
            error_type=error_type,
            error_message=error_message,
            device_state=device_state,
            execution_context=execution_context,
            historical_data=historical_data
        )
        
        # 4. 生成自愈建议
        suggestions = self.suggestion_generator.generate(
            error_type=error_type,
            root_cause=root_cause,
            device_state=device_state,
            context=context
        )
        
        # 计算分析耗时
        end_time = datetime.now()
        analysis_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # 更新统计
        self._update_stats(analysis_time_ms)
        
        return {
            'error_type': error_type,
            'confidence': confidence,
            'root_cause': root_cause,
            'healing_suggestions': suggestions,
            'features': features,
            'analysis_time_ms': analysis_time_ms,
            'analyzed_at': end_time.isoformat()
        }
    
    def batch_analyze(self, error_logs: List[Dict]) -> List[Dict]:
        """
        批量分析错误日志
        
        Args:
            error_logs: 错误日志列表
            
        Returns:
            分析结果列表
        """
        results = []
        for log in error_logs:
            try:
                result = self.analyze(
                    error_message=log.get('error_message', ''),
                    log_content=log.get('log_content'),
                    device_state=log.get('device_state'),
                    execution_context=log.get('execution_context'),
                    historical_data=log.get('historical_data'),
                    context=log.get('context')
                )
                result['task_log_id'] = log.get('task_log_id')
                results.append(result)
            except Exception as e:
                logger.error(f"分析失败 [task_log_id={log.get('task_log_id')}]: {e}")
                results.append({
                    'task_log_id': log.get('task_log_id'),
                    'error': str(e),
                    'success': False
                })
        
        return results
    
    def _update_stats(self, analysis_time_ms: int):
        """更新性能统计"""
        self.stats['total_analyzed'] += 1
        
        # 计算移动平均
        n = self.stats['total_analyzed']
        old_avg = self.stats['avg_inference_time_ms']
        self.stats['avg_inference_time_ms'] = (
            (old_avg * (n - 1) + analysis_time_ms) / n
        )
    
    def get_stats(self) -> Dict:
        """获取性能统计"""
        return self.stats.copy()
    
    def reset_stats(self):
        """重置统计"""
        self.stats = {
            'total_analyzed': 0,
            'avg_inference_time_ms': 0,
            'accuracy': 0.0
        }


# 缓存管理器
class AnalysisCache:
    """分析结果缓存"""
    
    def __init__(self, ttl: int = 3600):
        """
        初始化缓存
        
        Args:
            ttl: 缓存过期时间（秒）
        """
        self.cache = {}
        self.ttl = ttl
    
    def get(self, error_message: str) -> Optional[Dict]:
        """获取缓存的分析结果"""
        cache_key = self._generate_key(error_message)
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            
            # 检查是否过期
            if (datetime.now() - timestamp).total_seconds() < self.ttl:
                return cached_data
            else:
                # 删除过期缓存
                del self.cache[cache_key]
        
        return None
    
    def set(self, error_message: str, result: Dict):
        """缓存分析结果"""
        cache_key = self._generate_key(error_message)
        self.cache[cache_key] = (result, datetime.now())
    
    def _generate_key(self, error_message: str) -> str:
        """生成缓存键"""
        return hashlib.md5(error_message.encode()).hexdigest()
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
