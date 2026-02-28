"""
生产级脚本验证器 V2.0
支持AST分析、规则引擎、污点追踪、混淆检测、批量验证、性能监控
"""
import time
import yaml
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from .core.base import (
    ValidationResult, BatchValidationResult, ValidationMetrics,
    ScriptLanguage, RiskLevel
)
from .core.rule_engine import RuleEngine
from .analyzers.python_analyzer import PythonASTAnalyzer


class ScriptValidatorV2:
    """生产级脚本验证器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化验证器"""
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 初始化规则引擎
        self.rule_engine = RuleEngine(self.config)
        
        # 初始化分析器
        self.python_analyzer = PythonASTAnalyzer()
        
        # 性能配置
        self.single_timeout = self.config.get("performance", {}).get("single_timeout", 1.0)
        self.batch_timeout = self.config.get("performance", {}).get("batch_timeout", 60.0)
        self.max_workers = self.config.get("performance", {}).get("max_workers", 10)
        
        # 安全配置
        self.risk_thresholds = self.config.get("security", {}).get("risk_thresholds", {})
        self.environment = self.config.get("system", {}).get("environment", "production")
        
        # 统计信息
        self.stats = {
            "total_validations": 0,
            "total_passed": 0,
            "total_failed": 0,
            "total_time": 0.0,
            "avg_time": 0.0
        }
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "validator_config.yaml"
        else:
            config_path = Path(config_path)
        
        if not config_path.exists():
            return self._get_default_config()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "system": {"environment": "production"},
            "performance": {
                "single_timeout": 1.0,
                "batch_timeout": 60.0,
                "max_workers": 10
            },
            "security": {
                "risk_thresholds": {
                    "production": 200,
                    "staging": 500,
                    "development": 800
                }
            },
            "rules": {
                "hot_reload": False,
                "rules_path": "app/validator/rules"
            }
        }
    
    def validate(self, 
                 code: str, 
                 language: ScriptLanguage = ScriptLanguage.PYTHON,
                 script_name: str = "script",
                 metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """验证单个脚本"""
        start_time = time.time()
        
        # 创建结果对象
        result = ValidationResult(
            script_name=script_name,
            language=language,
            metadata=metadata or {}
        )
        
        try:
            # 1. 输入验证
            self._validate_input(code, result)
            
            # 2. 语言特定分析
            if language == ScriptLanguage.PYTHON:
                self._validate_python(code, result)
            elif language == ScriptLanguage.BATCH:
                self._validate_batch(code, result)
            elif language == ScriptLanguage.SHELL:
                self._validate_shell(code, result)
            elif language == ScriptLanguage.VISUAL:
                self._validate_visual(code, result)
            
            # 3. 计算指标
            result.calculate_risk_level()
            result.calculate_score()
            
            # 4. 风险阈值检查
            threshold = self.risk_thresholds.get(self.environment, 200)
            if result.risk_score > threshold:
                result.passed = False
                result.suggestions.append(
                    f"风险分({result.risk_score})超过{self.environment}环境阈值({threshold})"
                )
            
            # 5. 更新统计
            self.stats["total_validations"] += 1
            if result.passed:
                self.stats["total_passed"] += 1
            else:
                self.stats["total_failed"] += 1
            
        except Exception as e:
            result.passed = False
            result.suggestions.append(f"验证过程出错: {str(e)}")
        
        # 记录耗时
        result.metrics.total_time = time.time() - start_time
        self.stats["total_time"] += result.metrics.total_time
        self.stats["avg_time"] = self.stats["total_time"] / self.stats["total_validations"]
        
        return result
    
    def _validate_input(self, code: str, result: ValidationResult):
        """输入验证"""
        max_size = self.config.get("security", {}).get("input_validation", {}).get("max_script_size", 1024)
        max_lines = self.config.get("security", {}).get("input_validation", {}).get("max_lines", 10000)
        
        # 检查大小
        size_kb = len(code.encode('utf-8')) / 1024
        if size_kb > max_size:
            result.passed = False
            result.suggestions.append(f"脚本大小({size_kb:.1f}KB)超过限制({max_size}KB)")
        
        # 检查行数
        lines = code.split('\n')
        if len(lines) > max_lines:
            result.passed = False
            result.suggestions.append(f"脚本行数({len(lines)})超过限制({max_lines})")
        
        # 统计代码行
        result.metrics.total_lines = len(lines)
        result.metrics.blank_lines = sum(1 for line in lines if not line.strip())
        result.metrics.comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        result.metrics.code_lines = result.metrics.total_lines - result.metrics.blank_lines - result.metrics.comment_lines
    
    def _validate_python(self, code: str, result: ValidationResult):
        """验证Python脚本"""
        parse_start = time.time()
        
        # AST分析
        ast_tree, ast_issues = self.python_analyzer.analyze(code)
        result.metrics.parse_time = time.time() - parse_start
        
        # 添加AST分析发现的问题
        for issue in ast_issues:
            result.add_issue(issue)
        
        # 规则引擎检查
        rule_start = time.time()
        rule_issues = self.rule_engine.execute_rules(code, ScriptLanguage.PYTHON, ast_tree)
        result.metrics.rule_check_time = time.time() - rule_start
        
        # 添加规则检查发现的问题
        for issue in rule_issues:
            result.add_issue(issue)
        
        result.metrics.rules_executed = len(self.rule_engine.get_rules(language=ScriptLanguage.PYTHON))
        result.metrics.rules_matched = len(rule_issues)
    
    def _validate_batch(self, code: str, result: ValidationResult):
        """验证Batch脚本"""
        rule_start = time.time()
        
        # 规则引擎检查
        rule_issues = self.rule_engine.execute_rules(code, ScriptLanguage.BATCH)
        result.metrics.rule_check_time = time.time() - rule_start
        
        # 添加规则检查发现的问题
        for issue in rule_issues:
            result.add_issue(issue)
        
        result.metrics.rules_executed = len(self.rule_engine.get_rules(language=ScriptLanguage.BATCH))
        result.metrics.rules_matched = len(rule_issues)
    
    def _validate_shell(self, code: str, result: ValidationResult):
        """验证Shell脚本"""
        # 类似Batch的处理
        self._validate_batch(code, result)
    
    def _validate_visual(self, code: str, result: ValidationResult):
        """验证可视化脚本"""
        import json
        
        try:
            steps = json.loads(code)
            if not isinstance(steps, list):
                result.passed = False
                result.suggestions.append("可视化脚本必须是数组格式")
                return
            
            # 检查步骤完整性
            for i, step in enumerate(steps):
                if not isinstance(step, dict):
                    result.suggestions.append(f"步骤{i+1}格式错误")
                elif 'action' not in step:
                    result.suggestions.append(f"步骤{i+1}缺少action字段")
                elif 'target' not in step:
                    result.suggestions.append(f"步骤{i+1}缺少target字段")
            
            result.metrics.total_lines = len(steps)
            
        except json.JSONDecodeError as e:
            result.passed = False
            result.suggestions.append(f"JSON解析失败: {e.msg}")
    
    def validate_batch(self, 
                       scripts: List[Dict[str, Any]],
                       max_workers: Optional[int] = None) -> BatchValidationResult:
        """批量验证脚本"""
        batch_result = BatchValidationResult(
            total_scripts=len(scripts),
            metadata={"environment": self.environment}
        )
        
        start_time = time.time()
        workers = max_workers or self.max_workers
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # 提交所有任务
            future_to_script = {
                executor.submit(
                    self.validate,
                    script["code"],
                    ScriptLanguage(script.get("language", "python")),
                    script.get("name", f"script_{i}"),
                    script.get("metadata")
                ): script
                for i, script in enumerate(scripts)
            }
            
            # 收集结果
            for future in as_completed(future_to_script):
                try:
                    result = future.result(timeout=self.single_timeout)
                    batch_result.add_result(result)
                except Exception as e:
                    # 创建失败结果
                    script = future_to_script[future]
                    failed_result = ValidationResult(
                        script_name=script.get("name", "unknown"),
                        passed=False
                    )
                    failed_result.suggestions.append(f"验证失败: {str(e)}")
                    batch_result.add_result(failed_result)
        
        batch_result.total_time = time.time() - start_time
        batch_result.calculate_metrics()
        
        return batch_result
    
    async def validate_async(self, 
                            code: str, 
                            language: ScriptLanguage = ScriptLanguage.PYTHON,
                            script_name: str = "script") -> ValidationResult:
        """异步验证"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.validate, code, language, script_name)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "pass_rate": round(self.stats["total_passed"] / self.stats["total_validations"] * 100, 2) 
                        if self.stats["total_validations"] > 0 else 0,
            "rule_stats": self.rule_engine.get_rule_stats()
        }
    
    def reload_rules(self):
        """重新加载规则"""
        self.rule_engine.reload_rules()
    
    def shutdown(self):
        """关闭验证器"""
        self.rule_engine.stop()


# 全局验证器实例
_validator_instance: Optional[ScriptValidatorV2] = None


def get_validator(config_path: Optional[str] = None) -> ScriptValidatorV2:
    """获取验证器实例（单例模式）"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = ScriptValidatorV2(config_path)
    return _validator_instance
