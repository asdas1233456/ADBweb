"""
规则引擎 - 支持规则热加载、优先级、组合、白名单
"""
import re
import ast
import yaml
import json
from typing import List, Dict, Any, Optional, Callable, Set
from pathlib import Path
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import threading
import time
from datetime import datetime

from .base import (
    ValidationIssue, ValidationLevel, RiskLevel, 
    RuleCategory, ScriptLanguage
)


@dataclass
class Rule:
    """规则定义"""
    # 基本信息
    id: str
    name: str
    category: RuleCategory
    description: str
    
    # 规则配置
    enabled: bool = True
    priority: int = 500  # 优先级（越高越先执行）
    severity: ValidationLevel = ValidationLevel.WARNING
    risk_score: int = 0  # 风险分（0-1000）
    
    # 适用范围
    languages: List[ScriptLanguage] = field(default_factory=list)
    
    # 规则逻辑
    pattern: Optional[str] = None  # 正则模式
    ast_check: Optional[Callable] = None  # AST检查函数
    custom_check: Optional[Callable] = None  # 自定义检查函数
    
    # 修复建议
    suggestions: List[str] = field(default_factory=list)
    fix_examples: List[str] = field(default_factory=list)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    author: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def matches(self, code: str, language: ScriptLanguage, ast_tree: Any = None) -> List[Dict[str, Any]]:
        """检查规则是否匹配"""
        matches = []
        
        # 检查语言适用性
        if self.languages and language not in self.languages:
            return matches
        
        # 正则模式匹配
        if self.pattern:
            for match in re.finditer(self.pattern, code, re.MULTILINE | re.IGNORECASE):
                line_num = code[:match.start()].count('\n') + 1
                matches.append({
                    "line": line_num,
                    "column": match.start() - code.rfind('\n', 0, match.start()),
                    "matched_text": match.group(),
                    "match_obj": match
                })
        
        # AST检查
        if self.ast_check and ast_tree:
            try:
                ast_matches = self.ast_check(ast_tree, code)
                if ast_matches:
                    matches.extend(ast_matches)
            except Exception as e:
                pass
        
        # 自定义检查
        if self.custom_check:
            try:
                custom_matches = self.custom_check(code, language, ast_tree)
                if custom_matches:
                    matches.extend(custom_matches)
            except Exception as e:
                pass
        
        return matches
    
    def create_issue(self, match_info: Dict[str, Any]) -> ValidationIssue:
        """创建验证问题"""
        return ValidationIssue(
            rule_id=self.id,
            rule_name=self.name,
            category=self.category,
            level=self.severity,
            message=self.description,
            description=self.metadata.get("detailed_description", self.description),
            line_number=match_info.get("line"),
            column_number=match_info.get("column"),
            code_snippet=match_info.get("matched_text"),
            risk_score=self.risk_score,
            suggestions=self.suggestions,
            fix_examples=self.fix_examples,
            metadata={"rule_version": self.version, **match_info.get("metadata", {})}
        )


class RuleLoader:
    """规则加载器"""
    
    def __init__(self, rules_path: str):
        self.rules_path = Path(rules_path)
        self.rules: Dict[str, Rule] = {}
        self.last_load_time: Dict[str, float] = {}
    
    def load_rules(self) -> Dict[str, Rule]:
        """加载所有规则"""
        rules = {}
        
        if not self.rules_path.exists():
            return rules
        
        # 加载YAML规则文件
        for rule_file in self.rules_path.glob("**/*.yaml"):
            try:
                file_rules = self._load_yaml_rules(rule_file)
                rules.update(file_rules)
                self.last_load_time[str(rule_file)] = rule_file.stat().st_mtime
            except Exception as e:
                print(f"Failed to load rules from {rule_file}: {e}")
        
        # 加载JSON规则文件
        for rule_file in self.rules_path.glob("**/*.json"):
            try:
                file_rules = self._load_json_rules(rule_file)
                rules.update(file_rules)
                self.last_load_time[str(rule_file)] = rule_file.stat().st_mtime
            except Exception as e:
                print(f"Failed to load rules from {rule_file}: {e}")
        
        self.rules = rules
        return rules
    
    def _load_yaml_rules(self, file_path: Path) -> Dict[str, Rule]:
        """加载YAML规则文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return self._parse_rules(data)
    
    def _load_json_rules(self, file_path: Path) -> Dict[str, Rule]:
        """加载JSON规则文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return self._parse_rules(data)
    
    def _parse_rules(self, data: Dict[str, Any]) -> Dict[str, Rule]:
        """解析规则数据"""
        rules = {}
        
        for rule_data in data.get("rules", []):
            try:
                rule = Rule(
                    id=rule_data["id"],
                    name=rule_data["name"],
                    category=RuleCategory(rule_data.get("category", "security")),
                    description=rule_data["description"],
                    enabled=rule_data.get("enabled", True),
                    priority=rule_data.get("priority", 500),
                    severity=ValidationLevel(rule_data.get("severity", "warning")),
                    risk_score=rule_data.get("risk_score", 0),
                    languages=[ScriptLanguage(lang) for lang in rule_data.get("languages", [])],
                    pattern=rule_data.get("pattern"),
                    suggestions=rule_data.get("suggestions", []),
                    fix_examples=rule_data.get("fix_examples", []),
                    metadata=rule_data.get("metadata", {}),
                    version=rule_data.get("version", "1.0.0"),
                    author=rule_data.get("author", "")
                )
                rules[rule.id] = rule
            except Exception as e:
                print(f"Failed to parse rule {rule_data.get('id', 'unknown')}: {e}")
        
        return rules
    
    def check_updates(self) -> List[str]:
        """检查规则文件更新"""
        updated_files = []
        
        for file_path, last_mtime in self.last_load_time.items():
            path = Path(file_path)
            if path.exists():
                current_mtime = path.stat().st_mtime
                if current_mtime > last_mtime:
                    updated_files.append(file_path)
        
        return updated_files


class RuleEngine:
    """规则引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rules: Dict[str, Rule] = {}
        self.rule_loader: Optional[RuleLoader] = None
        self.whitelist: Set[str] = set()  # 规则白名单
        self.blacklist: Set[str] = set()  # 规则黑名单
        
        # 热加载配置
        self.hot_reload_enabled = config.get("rules", {}).get("hot_reload", False)
        self.reload_interval = config.get("rules", {}).get("reload_interval", 60)
        self.reload_thread: Optional[threading.Thread] = None
        self.stop_reload = threading.Event()
        
        # 初始化
        self._initialize()
    
    def _initialize(self):
        """初始化规则引擎"""
        # 加载规则
        rules_path = self.config.get("rules", {}).get("rules_path", "app/validator/rules")
        self.rule_loader = RuleLoader(rules_path)
        self.rules = self.rule_loader.load_rules()
        
        # 启动热加载
        if self.hot_reload_enabled:
            self._start_hot_reload()
    
    def _start_hot_reload(self):
        """启动热加载线程"""
        def reload_worker():
            while not self.stop_reload.is_set():
                try:
                    updated_files = self.rule_loader.check_updates()
                    if updated_files:
                        print(f"Reloading rules from updated files: {updated_files}")
                        self.rules = self.rule_loader.load_rules()
                except Exception as e:
                    print(f"Hot reload error: {e}")
                
                time.sleep(self.reload_interval)
        
        self.reload_thread = threading.Thread(target=reload_worker, daemon=True)
        self.reload_thread.start()
    
    def stop(self):
        """停止规则引擎"""
        if self.hot_reload_enabled:
            self.stop_reload.set()
            if self.reload_thread:
                self.reload_thread.join(timeout=5)
    
    def get_rules(self, 
                   language: Optional[ScriptLanguage] = None,
                   category: Optional[RuleCategory] = None,
                   enabled_only: bool = True) -> List[Rule]:
        """获取规则列表"""
        rules = list(self.rules.values())
        
        # 过滤禁用的规则
        if enabled_only:
            rules = [r for r in rules if r.enabled]
        
        # 过滤语言
        if language:
            rules = [r for r in rules if not r.languages or language in r.languages]
        
        # 过滤分类
        if category:
            rules = [r for r in rules if r.category == category]
        
        # 应用白名单/黑名单
        if self.whitelist:
            rules = [r for r in rules if r.id in self.whitelist]
        if self.blacklist:
            rules = [r for r in rules if r.id not in self.blacklist]
        
        # 按优先级排序
        rules.sort(key=lambda r: r.priority, reverse=True)
        
        return rules
    
    def execute_rules(self, 
                      code: str, 
                      language: ScriptLanguage,
                      ast_tree: Any = None,
                      category: Optional[RuleCategory] = None) -> List[ValidationIssue]:
        """执行规则检查"""
        issues = []
        rules = self.get_rules(language=language, category=category)
        
        for rule in rules:
            try:
                matches = rule.matches(code, language, ast_tree)
                for match in matches:
                    issue = rule.create_issue(match)
                    issues.append(issue)
            except Exception as e:
                print(f"Rule execution error ({rule.id}): {e}")
        
        return issues
    
    def add_to_whitelist(self, rule_ids: List[str]):
        """添加到白名单"""
        self.whitelist.update(rule_ids)
    
    def add_to_blacklist(self, rule_ids: List[str]):
        """添加到黑名单"""
        self.blacklist.update(rule_ids)
    
    def reload_rules(self):
        """手动重新加载规则"""
        if self.rule_loader:
            self.rules = self.rule_loader.load_rules()
    
    def get_rule_stats(self) -> Dict[str, Any]:
        """获取规则统计信息"""
        total = len(self.rules)
        enabled = sum(1 for r in self.rules.values() if r.enabled)
        
        by_category = {}
        by_language = {}
        
        for rule in self.rules.values():
            # 按分类统计
            cat = rule.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
            
            # 按语言统计
            for lang in rule.languages:
                lang_val = lang.value
                by_language[lang_val] = by_language.get(lang_val, 0) + 1
        
        return {
            "total": total,
            "enabled": enabled,
            "disabled": total - enabled,
            "by_category": by_category,
            "by_language": by_language,
            "whitelist_size": len(self.whitelist),
            "blacklist_size": len(self.blacklist)
        }
