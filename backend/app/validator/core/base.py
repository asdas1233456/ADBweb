"""
核心基础类 - 定义验证器的基础数据结构和接口
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import uuid


class ValidationLevel(str, Enum):
    """验证级别"""
    SUCCESS = "success"      # 通过
    INFO = "info"           # 信息
    WARNING = "warning"     # 警告
    ERROR = "error"         # 错误
    CRITICAL = "critical"   # 严重错误


class RiskLevel(str, Enum):
    """风险等级"""
    SAFE = "safe"           # 安全（0-200）
    LOW = "low"             # 低风险（201-400）
    MEDIUM = "medium"       # 中风险（401-600）
    HIGH = "high"           # 高风险（601-800）
    CRITICAL = "critical"   # 严重风险（801-1000）


class RuleCategory(str, Enum):
    """规则分类"""
    SECURITY = "security"           # 安全规则
    QUALITY = "quality"             # 质量规则
    BEST_PRACTICE = "best_practice" # 最佳实践
    BUSINESS = "business"           # 业务规则
    PERFORMANCE = "performance"     # 性能规则


class ScriptLanguage(str, Enum):
    """脚本语言"""
    PYTHON = "python"
    BATCH = "batch"
    SHELL = "shell"
    VISUAL = "visual"  # 可视化JSON


@dataclass
class ValidationIssue:
    """验证问题"""
    # 基本信息
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str = ""
    rule_name: str = ""
    category: RuleCategory = RuleCategory.SECURITY
    
    # 问题详情
    level: ValidationLevel = ValidationLevel.WARNING
    message: str = ""
    description: str = ""
    
    # 位置信息
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    code_snippet: Optional[str] = None
    
    # 风险信息
    risk_score: int = 0  # 0-1000
    risk_level: RiskLevel = RiskLevel.SAFE
    
    # 修复建议
    suggestions: List[str] = field(default_factory=list)
    fix_examples: List[str] = field(default_factory=list)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "category": self.category.value,
            "level": self.level.value,
            "message": self.message,
            "description": self.description,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "code_snippet": self.code_snippet,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level.value,
            "suggestions": self.suggestions,
            "fix_examples": self.fix_examples,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ValidationMetrics:
    """验证指标"""
    # 性能指标
    total_time: float = 0.0  # 总耗时（秒）
    parse_time: float = 0.0  # 解析耗时
    analysis_time: float = 0.0  # 分析耗时
    rule_check_time: float = 0.0  # 规则检查耗时
    
    # 统计指标
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    
    # 检测指标
    total_issues: int = 0
    critical_issues: int = 0
    error_issues: int = 0
    warning_issues: int = 0
    info_issues: int = 0
    
    # 规则指标
    rules_executed: int = 0
    rules_matched: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "performance": {
                "total_time": round(self.total_time, 3),
                "parse_time": round(self.parse_time, 3),
                "analysis_time": round(self.analysis_time, 3),
                "rule_check_time": round(self.rule_check_time, 3)
            },
            "statistics": {
                "total_lines": self.total_lines,
                "code_lines": self.code_lines,
                "comment_lines": self.comment_lines,
                "blank_lines": self.blank_lines
            },
            "issues": {
                "total": self.total_issues,
                "critical": self.critical_issues,
                "error": self.error_issues,
                "warning": self.warning_issues,
                "info": self.info_issues
            },
            "rules": {
                "executed": self.rules_executed,
                "matched": self.rules_matched
            }
        }


@dataclass
class ValidationResult:
    """验证结果"""
    # 基本信息
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    script_name: str = ""
    language: ScriptLanguage = ScriptLanguage.PYTHON
    
    # 验证状态
    passed: bool = True
    score: int = 100  # 0-100分
    risk_score: int = 0  # 0-1000分
    risk_level: RiskLevel = RiskLevel.SAFE
    
    # 问题列表
    issues: List[ValidationIssue] = field(default_factory=list)
    
    # 建议列表
    suggestions: List[str] = field(default_factory=list)
    
    # 指标数据
    metrics: ValidationMetrics = field(default_factory=ValidationMetrics)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    # 审计信息
    audit_info: Dict[str, Any] = field(default_factory=dict)
    
    def add_issue(self, issue: ValidationIssue):
        """添加问题"""
        self.issues.append(issue)
        self.metrics.total_issues += 1
        
        # 更新问题计数
        if issue.level == ValidationLevel.CRITICAL:
            self.metrics.critical_issues += 1
            self.passed = False
        elif issue.level == ValidationLevel.ERROR:
            self.metrics.error_issues += 1
            self.passed = False
        elif issue.level == ValidationLevel.WARNING:
            self.metrics.warning_issues += 1
        elif issue.level == ValidationLevel.INFO:
            self.metrics.info_issues += 1
        
        # 更新风险分
        self.risk_score += issue.risk_score
    
    def calculate_risk_level(self):
        """计算风险等级"""
        if self.risk_score <= 200:
            self.risk_level = RiskLevel.SAFE
        elif self.risk_score <= 400:
            self.risk_level = RiskLevel.LOW
        elif self.risk_score <= 600:
            self.risk_level = RiskLevel.MEDIUM
        elif self.risk_score <= 800:
            self.risk_level = RiskLevel.HIGH
        else:
            self.risk_level = RiskLevel.CRITICAL
    
    def calculate_score(self):
        """计算质量分数"""
        # 基础分100
        score = 100
        
        # 扣分规则
        score -= self.metrics.critical_issues * 50
        score -= self.metrics.error_issues * 20
        score -= self.metrics.warning_issues * 5
        
        # 风险分影响
        score -= min(self.risk_score // 20, 30)
        
        self.score = max(0, min(100, score))
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "id": self.id,
            "script_name": self.script_name,
            "language": self.language.value,
            "passed": self.passed,
            "score": self.score,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level.value,
            "issues": [issue.to_dict() for issue in self.issues],
            "suggestions": self.suggestions,
            "metrics": self.metrics.to_dict(),
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }
        
        # 包含敏感信息（审计日志）
        if include_sensitive:
            result["audit_info"] = self.audit_info
        
        return result


@dataclass
class BatchValidationResult:
    """批量验证结果"""
    # 基本信息
    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    total_scripts: int = 0
    
    # 验证状态
    completed: int = 0
    passed: int = 0
    failed: int = 0
    
    # 结果列表
    results: List[ValidationResult] = field(default_factory=list)
    
    # 统计信息
    total_time: float = 0.0
    avg_time: float = 0.0
    
    # 风险统计
    risk_distribution: Dict[str, int] = field(default_factory=dict)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def add_result(self, result: ValidationResult):
        """添加结果"""
        self.results.append(result)
        self.completed += 1
        
        if result.passed:
            self.passed += 1
        else:
            self.failed += 1
        
        # 更新风险分布
        risk_level = result.risk_level.value
        self.risk_distribution[risk_level] = self.risk_distribution.get(risk_level, 0) + 1
    
    def calculate_metrics(self):
        """计算指标"""
        if self.completed > 0:
            self.avg_time = self.total_time / self.completed
    
    @property
    def pass_rate(self) -> float:
        """计算通过率"""
        return round(self.passed / self.completed * 100, 2) if self.completed > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "batch_id": self.batch_id,
            "total_scripts": self.total_scripts,
            "completed": self.completed,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": self.pass_rate,
            "total_time": round(self.total_time, 3),
            "avg_time": round(self.avg_time, 3),
            "risk_distribution": self.risk_distribution,
            "results": [result.to_dict() for result in self.results],
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }
