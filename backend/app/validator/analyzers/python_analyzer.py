"""
Python脚本分析器 - AST语义分析、符号执行、污点追踪、混淆检测
"""
import ast
import base64
import binascii
import re
from typing import List, Dict, Any, Set, Optional, Tuple
from dataclasses import dataclass, field

from ..core.base import ValidationIssue, ValidationLevel, RiskLevel, RuleCategory


@dataclass
class SymbolInfo:
    """符号信息"""
    name: str
    type: str  # variable, function, class, import
    value: Any = None
    line: int = 0
    is_tainted: bool = False  # 是否被污染
    taint_source: Optional[str] = None


class PythonASTAnalyzer:
    """Python AST分析器"""
    
    # 危险函数列表
    DANGEROUS_FUNCTIONS = {
        'eval': 1000,
        'exec': 1000,
        'compile': 800,
        '__import__': 800,
        'os.system': 1000,
        'subprocess.call': 600,
        'subprocess.run': 600,
        'subprocess.Popen': 600,
        'open': 200,  # 根据模式判断
    }
    
    # 污点源（用户输入）
    TAINT_SOURCES = {
        'input', 'raw_input', 'sys.argv', 'os.environ',
        'request.args', 'request.form', 'request.json'
    }
    
    # 污点汇（危险操作）
    TAINT_SINKS = {
        'eval', 'exec', 'compile', 'os.system',
        'subprocess.call', 'subprocess.run', 'subprocess.Popen'
    }
    
    def __init__(self):
        self.symbols: Dict[str, SymbolInfo] = {}
        self.tainted_vars: Set[str] = set()
        self.issues: List[ValidationIssue] = []
    
    def analyze(self, code: str) -> Tuple[ast.AST, List[ValidationIssue]]:
        """分析Python代码"""
        self.issues = []
        self.symbols = {}
        self.tainted_vars = set()
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            issue = ValidationIssue(
                rule_id="PY001",
                rule_name="语法错误",
                category=RuleCategory.SECURITY,
                level=ValidationLevel.ERROR,
                message=f"语法错误: {e.msg}",
                line_number=e.lineno,
                risk_score=500
            )
            self.issues.append(issue)
            return None, self.issues
        
        # 1. 符号表构建
        self._build_symbol_table(tree)
        
        # 2. 污点分析
        self._taint_analysis(tree)
        
        # 3. 危险函数检测
        self._detect_dangerous_calls(tree, code)
        
        # 4. 混淆检测
        self._detect_obfuscation(code)
        
        # 5. 行为分析
        self._behavior_analysis(tree)
        
        return tree, self.issues
    
    def _build_symbol_table(self, tree: ast.AST):
        """构建符号表"""
        for node in ast.walk(tree):
            # 变量赋值
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.symbols[target.id] = SymbolInfo(
                            name=target.id,
                            type="variable",
                            value=self._extract_value(node.value),
                            line=node.lineno
                        )
            
            # 函数定义
            elif isinstance(node, ast.FunctionDef):
                self.symbols[node.name] = SymbolInfo(
                    name=node.name,
                    type="function",
                    line=node.lineno
                )
            
            # 类定义
            elif isinstance(node, ast.ClassDef):
                self.symbols[node.name] = SymbolInfo(
                    name=node.name,
                    type="class",
                    line=node.lineno
                )
            
            # 导入
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.symbols[alias.name] = SymbolInfo(
                        name=alias.name,
                        type="import",
                        line=node.lineno
                    )
    
    def _extract_value(self, node: ast.AST) -> Any:
        """提取节点值"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        return None
    
    def _taint_analysis(self, tree: ast.AST):
        """污点分析"""
        # 标记污点源
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_function_name(node.func)
                
                # 检查是否是污点源
                if func_name in self.TAINT_SOURCES:
                    # 标记赋值目标为污点
                    parent = self._find_parent_assign(tree, node)
                    if parent:
                        for target in parent.targets:
                            if isinstance(target, ast.Name):
                                self.tainted_vars.add(target.id)
                                if target.id in self.symbols:
                                    self.symbols[target.id].is_tainted = True
                                    self.symbols[target.id].taint_source = func_name
        
        # 污点传播
        self._propagate_taint(tree)
        
        # 检查污点汇
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_function_name(node.func)
                
                if func_name in self.TAINT_SINKS:
                    # 检查参数是否被污染
                    for arg in node.args:
                        if isinstance(arg, ast.Name) and arg.id in self.tainted_vars:
                            issue = ValidationIssue(
                                rule_id="PY_TAINT_001",
                                rule_name="污点数据流入危险函数",
                                category=RuleCategory.SECURITY,
                                level=ValidationLevel.CRITICAL,
                                message=f"用户输入直接流入危险函数 {func_name}",
                                description=f"变量 {arg.id} 来自用户输入，直接传入 {func_name} 可能导致代码注入",
                                line_number=node.lineno,
                                risk_score=900,
                                suggestions=[
                                    "对用户输入进行严格验证和过滤",
                                    "使用白名单而不是黑名单",
                                    "避免使用eval/exec等危险函数"
                                ]
                            )
                            self.issues.append(issue)
    
    def _propagate_taint(self, tree: ast.AST):
        """污点传播"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # 检查右侧是否包含污点变量
                tainted = False
                for name_node in ast.walk(node.value):
                    if isinstance(name_node, ast.Name) and name_node.id in self.tainted_vars:
                        tainted = True
                        break
                
                # 传播污点到左侧
                if tainted:
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.tainted_vars.add(target.id)
    
    def _detect_dangerous_calls(self, tree: ast.AST, code: str):
        """检测危险函数调用"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_function_name(node.func)
                
                if func_name in self.DANGEROUS_FUNCTIONS:
                    risk_score = self.DANGEROUS_FUNCTIONS[func_name]
                    
                    # 特殊处理：open函数根据模式判断
                    if func_name == 'open':
                        risk_score = self._analyze_open_call(node)
                    
                    # 特殊处理：subprocess根据shell参数判断
                    if 'subprocess' in func_name:
                        risk_score = self._analyze_subprocess_call(node)
                    
                    if risk_score > 0:
                        level = ValidationLevel.CRITICAL if risk_score >= 800 else \
                                ValidationLevel.ERROR if risk_score >= 500 else \
                                ValidationLevel.WARNING
                        
                        issue = ValidationIssue(
                            rule_id=f"PY_DANGER_{func_name.upper().replace('.', '_')}",
                            rule_name=f"危险函数调用: {func_name}",
                            category=RuleCategory.SECURITY,
                            level=level,
                            message=f"检测到危险函数调用: {func_name}",
                            description=f"函数 {func_name} 可能导致安全风险",
                            line_number=node.lineno,
                            risk_score=risk_score,
                            suggestions=self._get_danger_suggestions(func_name)
                        )
                        self.issues.append(issue)
    
    def _analyze_open_call(self, node: ast.Call) -> int:
        """分析open函数调用"""
        # 检查模式参数
        for keyword in node.keywords:
            if keyword.arg == 'mode':
                if isinstance(keyword.value, ast.Constant):
                    mode = keyword.value.value
                    if 'w' in mode or 'a' in mode:
                        return 300  # 写入模式有风险
        
        # 检查位置参数
        if len(node.args) >= 2:
            if isinstance(node.args[1], ast.Constant):
                mode = node.args[1].value
                if isinstance(mode, str) and ('w' in mode or 'a' in mode):
                    return 300
        
        return 100  # 读取模式风险较低
    
    def _analyze_subprocess_call(self, node: ast.Call) -> int:
        """分析subprocess调用"""
        # 检查shell参数
        for keyword in node.keywords:
            if keyword.arg == 'shell':
                if isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                    return 900  # shell=True风险极高
        
        return 600  # 默认风险
    
    def _detect_obfuscation(self, code: str):
        """检测混淆代码"""
        # 1. Base64检测
        base64_pattern = r'base64\.b64decode\([\'"]([A-Za-z0-9+/=]+)[\'"]\)'
        for match in re.finditer(base64_pattern, code):
            try:
                decoded = base64.b64decode(match.group(1)).decode('utf-8', errors='ignore')
                issue = ValidationIssue(
                    rule_id="PY_OBFUS_001",
                    rule_name="Base64混淆检测",
                    category=RuleCategory.SECURITY,
                    level=ValidationLevel.WARNING,
                    message="检测到Base64编码内容",
                    description=f"解码内容: {decoded[:100]}...",
                    risk_score=400,
                    suggestions=["避免使用Base64混淆代码", "使用明文代码提高可读性"]
                )
                self.issues.append(issue)
            except:
                pass
        
        # 2. 十六进制检测
        hex_pattern = r'\\x[0-9a-fA-F]{2}'
        hex_matches = re.findall(hex_pattern, code)
        if len(hex_matches) > 10:
            issue = ValidationIssue(
                rule_id="PY_OBFUS_002",
                rule_name="十六进制混淆检测",
                category=RuleCategory.SECURITY,
                level=ValidationLevel.WARNING,
                message=f"检测到大量十六进制编码 ({len(hex_matches)}处)",
                risk_score=300,
                suggestions=["避免使用十六进制混淆代码"]
            )
            self.issues.append(issue)
        
        # 3. 字符串拼接检测（可能的混淆）
        concat_pattern = r'[\'"][^\'"]+[\'"](\s*\+\s*[\'"][^\'"]+[\'"]){3,}'
        if re.search(concat_pattern, code):
            issue = ValidationIssue(
                rule_id="PY_OBFUS_003",
                rule_name="字符串拼接混淆",
                category=RuleCategory.SECURITY,
                level=ValidationLevel.INFO,
                message="检测到复杂的字符串拼接",
                risk_score=100,
                suggestions=["使用f-string或format提高可读性"]
            )
            self.issues.append(issue)
    
    def _behavior_analysis(self, tree: ast.AST):
        """行为分析"""
        file_ops = 0
        network_ops = 0
        system_ops = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_function_name(node.func)
                
                # 文件操作
                if func_name in ['open', 'os.remove', 'os.unlink', 'shutil.rmtree']:
                    file_ops += 1
                
                # 网络操作
                if any(net in func_name for net in ['requests', 'urllib', 'socket', 'http']):
                    network_ops += 1
                
                # 系统操作
                if any(sys in func_name for sys in ['os.system', 'subprocess', 'os.exec']):
                    system_ops += 1
        
        # 异常行为检测：大量文件操作+网络请求
        if file_ops > 10 and network_ops > 5:
            issue = ValidationIssue(
                rule_id="PY_BEHAVIOR_001",
                rule_name="异常行为模式",
                category=RuleCategory.SECURITY,
                level=ValidationLevel.WARNING,
                message=f"检测到异常行为: {file_ops}次文件操作 + {network_ops}次网络请求",
                description="大量文件操作配合网络请求可能是数据窃取行为",
                risk_score=600,
                suggestions=["检查脚本是否有数据外传行为", "确认文件操作和网络请求的必要性"]
            )
            self.issues.append(issue)
    
    def _get_function_name(self, node: ast.AST) -> str:
        """获取函数名"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value_name = self._get_function_name(node.value)
            return f"{value_name}.{node.attr}" if value_name else node.attr
        return ""
    
    def _find_parent_assign(self, tree: ast.AST, target_node: ast.AST) -> Optional[ast.Assign]:
        """查找父赋值节点"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if target_node in ast.walk(node.value):
                    return node
        return None
    
    def _get_danger_suggestions(self, func_name: str) -> List[str]:
        """获取危险函数的修复建议"""
        suggestions_map = {
            'eval': ["使用ast.literal_eval替代", "避免执行用户输入", "使用JSON解析"],
            'exec': ["重构代码避免动态执行", "使用配置文件替代", "使用函数映射表"],
            'os.system': ["使用subprocess.run替代", "避免shell=True", "验证所有输入"],
            'subprocess': ["避免shell=True", "使用列表形式传参", "验证所有参数"],
            'open': ["使用with语句", "验证文件路径", "限制文件操作权限"]
        }
        
        for key, suggestions in suggestions_map.items():
            if key in func_name:
                return suggestions
        
        return ["请评估此操作的安全风险", "考虑使用更安全的替代方案"]
