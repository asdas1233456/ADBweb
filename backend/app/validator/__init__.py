"""
脚本验证器 V2.0 - 生产级验证系统
"""
from .validator_v2 import ScriptValidatorV2, get_validator
from .core.base import (
    ValidationResult,
    BatchValidationResult,
    ValidationIssue,
    ValidationLevel,
    RiskLevel,
    ScriptLanguage,
    RuleCategory
)

__version__ = "2.0.0"
__all__ = [
    "ScriptValidatorV2",
    "get_validator",
    "ValidationResult",
    "BatchValidationResult",
    "ValidationIssue",
    "ValidationLevel",
    "RiskLevel",
    "ScriptLanguage",
    "RuleCategory"
]
