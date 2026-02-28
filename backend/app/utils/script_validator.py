"""
脚本验证器
提供脚本的静态检查、安全检查、依赖检查等功能
"""
import ast
import re
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(str, Enum):
    """验证级别"""
    SUCCESS = "success"  # 通过
    WARNING = "warning"  # 警告
    ERROR = "error"      # 错误


@dataclass
class ValidationItem:
    """验证项"""
    name: str
    level: ValidationLevel
    message: str
    details: str = ""


@dataclass
class ValidationResult:
    """验证结果"""
    passed: bool
    score: int  # 0-100分
    items: List[ValidationItem]
    suggestions: List[str]


class ScriptValidator:
    """脚本验证器"""
    
    # 危险的Python函数/模块
    DANGEROUS_IMPORTS = [
        'os.system', 'subprocess', 'eval', 'exec', 'compile',
        '__import__', 'open', 'file'
    ]
    
    # 警告的Python函数/模块
    WARNING_IMPORTS = [
        'requests', 'urllib', 'socket', 'shutil.rmtree'
    ]
    
    # 必需的依赖
    REQUIRED_IMPORTS = {
        'python': ['uiautomator2'],
        'batch': []
    }
    
    # 危险的批处理命令
    DANGEROUS_BATCH_COMMANDS = [
        r'del\s+/[sq]',
        r'format\s+',
        r'rd\s+/s',
        r'reg\s+delete',
        r'net\s+user.*delete',
        r'shutdown',
        r'taskkill\s+/f'
    ]
    
    def validate_python(self, code: str, filename: str = "script.py") -> ValidationResult:
        """验证Python脚本"""
        items = []
        suggestions = []
        score = 100
        
        # 1. 语法检查
        syntax_result = self._check_python_syntax(code, filename)
        items.append(syntax_result)
        if syntax_result.level == ValidationLevel.ERROR:
            score -= 50
        
        # 2. 安全检查
        security_result = self._check_python_security(code)
        items.append(security_result)
        if security_result.level == ValidationLevel.ERROR:
            score -= 30
        elif security_result.level == ValidationLevel.WARNING:
            score -= 10
        
        # 3. 依赖检查
        dependency_result = self._check_python_dependencies(code)
        items.append(dependency_result)
        if dependency_result.level == ValidationLevel.WARNING:
            score -= 5
            suggestions.append("请确保设备已安装所需的Python库")
        
        # 4. 代码质量检查
        quality_result = self._check_python_quality(code)
        items.append(quality_result)
        if quality_result.level == ValidationLevel.WARNING:
            score -= 5
        
        # 5. 最佳实践检查
        practice_result = self._check_python_best_practices(code)
        items.append(practice_result)
        if practice_result.level == ValidationLevel.WARNING:
            score -= 5
            suggestions.extend([
                "建议添加异常处理（try-except）",
                "建议添加日志输出",
                "建议设置操作超时"
            ])
        
        # 判断是否通过
        passed = all(item.level != ValidationLevel.ERROR for item in items)
        score = max(0, min(100, score))
        
        return ValidationResult(
            passed=passed,
            score=score,
            items=items,
            suggestions=suggestions
        )
    
    def _check_python_syntax(self, code: str, filename: str) -> ValidationItem:
        """检查Python语法"""
        try:
            ast.parse(code, filename=filename)
            return ValidationItem(
                name="语法检查",
                level=ValidationLevel.SUCCESS,
                message="语法正确",
                details="Python语法验证通过"
            )
        except SyntaxError as e:
            return ValidationItem(
                name="语法检查",
                level=ValidationLevel.ERROR,
                message=f"语法错误: {e.msg}",
                details=f"第{e.lineno}行: {e.text}"
            )
        except Exception as e:
            return ValidationItem(
                name="语法检查",
                level=ValidationLevel.ERROR,
                message=f"解析失败: {str(e)}",
                details=""
            )
    
    def _check_python_security(self, code: str) -> ValidationItem:
        """检查Python安全性"""
        dangerous_found = []
        warning_found = []
        
        # 检查真正危险的函数（不包括open和file）
        truly_dangerous = ['os.system', 'subprocess', 'eval', 'exec', 'compile', '__import__']
        for dangerous in truly_dangerous:
            if dangerous in code:
                dangerous_found.append(dangerous)
        
        # 检查open和file的使用 - 只在写入模式时警告
        if re.search(r"open\s*\([^)]*['\"]w", code):
            warning_found.append("open(写入模式)")
        elif re.search(r"open\s*\([^)]*['\"]a", code):
            warning_found.append("open(追加模式)")
        
        # 检查其他警告函数
        for warning in self.WARNING_IMPORTS:
            if warning in code:
                warning_found.append(warning)
        
        if dangerous_found:
            return ValidationItem(
                name="安全检查",
                level=ValidationLevel.ERROR,
                message=f"发现危险操作: {', '.join(dangerous_found)}",
                details="脚本包含可能危害系统的操作，请移除这些代码"
            )
        elif warning_found:
            return ValidationItem(
                name="安全检查",
                level=ValidationLevel.WARNING,
                message=f"发现敏感操作: {', '.join(warning_found)}",
                details="脚本包含文件或网络操作，请确保这些操作是必需的"
            )
        else:
            return ValidationItem(
                name="安全检查",
                level=ValidationLevel.SUCCESS,
                message="未发现安全问题",
                details="脚本不包含危险操作"
            )
    
    def _check_python_dependencies(self, code: str) -> ValidationItem:
        """检查Python依赖"""
        # 提取import语句
        imports = self._extract_python_imports(code)
        
        # 检查必需的依赖
        missing = []
        for required in self.REQUIRED_IMPORTS['python']:
            if required not in imports and 'd2' not in imports:  # d2是uiautomator2的别名
                missing.append(required)
        
        if missing:
            return ValidationItem(
                name="依赖检查",
                level=ValidationLevel.WARNING,
                message=f"缺少推荐的依赖: {', '.join(missing)}",
                details="建议导入uiautomator2库以进行设备操作"
            )
        else:
            return ValidationItem(
                name="依赖检查",
                level=ValidationLevel.SUCCESS,
                message="依赖完整",
                details=f"已导入: {', '.join(imports) if imports else '无'}"
            )
    
    def _extract_python_imports(self, code: str) -> List[str]:
        """提取Python的import语句"""
        imports = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except:
            pass
        return imports
    
    def _check_python_quality(self, code: str) -> ValidationItem:
        """检查Python代码质量"""
        lines = code.split('\n')
        total_lines = len(lines)
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        empty_lines = sum(1 for line in lines if not line.strip())
        code_lines = total_lines - comment_lines - empty_lines
        
        # 计算注释率
        comment_rate = comment_lines / code_lines if code_lines > 0 else 0
        
        # 检查函数定义
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            function_count = len(functions)
        except:
            function_count = 0
        
        issues = []
        if comment_rate < 0.1:
            issues.append("注释较少")
        if function_count == 0 and code_lines > 20:
            issues.append("建议将代码封装为函数")
        if code_lines > 200:
            issues.append("代码较长，建议拆分")
        
        if issues:
            return ValidationItem(
                name="代码质量",
                level=ValidationLevel.WARNING,
                message=f"发现 {len(issues)} 个问题",
                details="; ".join(issues)
            )
        else:
            return ValidationItem(
                name="代码质量",
                level=ValidationLevel.SUCCESS,
                message="代码质量良好",
                details=f"代码行数: {code_lines}, 注释率: {comment_rate:.1%}"
            )
    
    def _check_python_best_practices(self, code: str) -> ValidationItem:
        """检查Python最佳实践"""
        issues = []
        
        # 检查异常处理
        if 'try:' not in code and 'except' not in code:
            issues.append("缺少异常处理")
        
        # 检查日志输出
        if 'print(' not in code and 'logging' not in code and 'logger' not in code:
            issues.append("缺少日志输出")
        
        # 检查超时设置
        if 'timeout' not in code.lower() and 'sleep' not in code:
            issues.append("建议添加超时或等待")
        
        if issues:
            return ValidationItem(
                name="最佳实践",
                level=ValidationLevel.WARNING,
                message=f"发现 {len(issues)} 个改进点",
                details="; ".join(issues)
            )
        else:
            return ValidationItem(
                name="最佳实践",
                level=ValidationLevel.SUCCESS,
                message="符合最佳实践",
                details="代码包含异常处理、日志和超时设置"
            )
    
    def validate_batch(self, code: str) -> ValidationResult:
        """验证Batch脚本"""
        items = []
        suggestions = []
        score = 100
        
        # 1. 基本格式检查
        format_result = self._check_batch_format(code)
        items.append(format_result)
        if format_result.level == ValidationLevel.ERROR:
            score -= 30
        
        # 2. 安全检查
        security_result = self._check_batch_security(code)
        items.append(security_result)
        if security_result.level == ValidationLevel.ERROR:
            score -= 50
        elif security_result.level == ValidationLevel.WARNING:
            score -= 20
        
        # 3. 命令检查
        command_result = self._check_batch_commands(code)
        items.append(command_result)
        if command_result.level == ValidationLevel.WARNING:
            score -= 10
        
        passed = all(item.level != ValidationLevel.ERROR for item in items)
        score = max(0, min(100, score))
        
        if not passed:
            suggestions.append("请修复错误后重新上传")
        
        return ValidationResult(
            passed=passed,
            score=score,
            items=items,
            suggestions=suggestions
        )
    
    def _check_batch_format(self, code: str) -> ValidationItem:
        """检查Batch格式"""
        if not code.strip():
            return ValidationItem(
                name="格式检查",
                level=ValidationLevel.ERROR,
                message="脚本为空",
                details="批处理脚本不能为空"
            )
        
        return ValidationItem(
            name="格式检查",
            level=ValidationLevel.SUCCESS,
            message="格式正确",
            details="批处理脚本格式验证通过"
        )
    
    def _check_batch_security(self, code: str) -> ValidationItem:
        """检查Batch安全性"""
        dangerous_found = []
        
        for pattern in self.DANGEROUS_BATCH_COMMANDS:
            if re.search(pattern, code, re.IGNORECASE):
                dangerous_found.append(pattern)
        
        if dangerous_found:
            return ValidationItem(
                name="安全检查",
                level=ValidationLevel.ERROR,
                message=f"发现危险命令",
                details="脚本包含可能危害系统的命令，请移除这些代码"
            )
        else:
            return ValidationItem(
                name="安全检查",
                level=ValidationLevel.SUCCESS,
                message="未发现安全问题",
                details="脚本不包含危险命令"
            )
    
    def _check_batch_commands(self, code: str) -> ValidationItem:
        """检查Batch命令"""
        lines = [line.strip() for line in code.split('\n') if line.strip() and not line.strip().startswith('::')]
        
        if len(lines) > 100:
            return ValidationItem(
                name="命令检查",
                level=ValidationLevel.WARNING,
                message="脚本较长",
                details=f"脚本包含{len(lines)}行命令，建议拆分"
            )
        
        return ValidationItem(
            name="命令检查",
            level=ValidationLevel.SUCCESS,
            message="命令检查通过",
            details=f"脚本包含{len(lines)}行命令"
        )
    
    def validate_visual(self, steps_json: str) -> ValidationResult:
        """验证可视化脚本"""
        items = []
        suggestions = []
        score = 100
        
        # 1. JSON格式检查
        json_result, steps = self._check_visual_json(steps_json)
        items.append(json_result)
        if json_result.level == ValidationLevel.ERROR:
            score -= 50
            return ValidationResult(
                passed=False,
                score=score,
                items=items,
                suggestions=["请修复JSON格式错误"]
            )
        
        # 2. 步骤完整性检查
        completeness_result = self._check_visual_completeness(steps)
        items.append(completeness_result)
        if completeness_result.level == ValidationLevel.WARNING:
            score -= 10
        
        # 3. 步骤逻辑检查
        logic_result = self._check_visual_logic(steps)
        items.append(logic_result)
        if logic_result.level == ValidationLevel.WARNING:
            score -= 10
            suggestions.append("建议优化步骤顺序和逻辑")
        
        passed = all(item.level != ValidationLevel.ERROR for item in items)
        score = max(0, min(100, score))
        
        return ValidationResult(
            passed=passed,
            score=score,
            items=items,
            suggestions=suggestions
        )
    
    def _check_visual_json(self, steps_json: str) -> Tuple[ValidationItem, List]:
        """检查可视化脚本JSON格式"""
        try:
            steps = json.loads(steps_json)
            if not isinstance(steps, list):
                return ValidationItem(
                    name="JSON格式",
                    level=ValidationLevel.ERROR,
                    message="格式错误",
                    details="步骤必须是数组格式"
                ), []
            
            return ValidationItem(
                name="JSON格式",
                level=ValidationLevel.SUCCESS,
                message="格式正确",
                details=f"包含{len(steps)}个步骤"
            ), steps
        except json.JSONDecodeError as e:
            return ValidationItem(
                name="JSON格式",
                level=ValidationLevel.ERROR,
                message=f"JSON解析失败: {e.msg}",
                details=f"位置: {e.pos}"
            ), []
    
    def _check_visual_completeness(self, steps: List) -> ValidationItem:
        """检查可视化脚本完整性"""
        if not steps:
            return ValidationItem(
                name="步骤完整性",
                level=ValidationLevel.WARNING,
                message="步骤为空",
                details="脚本没有定义任何步骤"
            )
        
        incomplete = []
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                incomplete.append(f"步骤{i+1}: 格式错误")
            elif 'action' not in step:
                incomplete.append(f"步骤{i+1}: 缺少action字段")
            elif 'target' not in step:
                incomplete.append(f"步骤{i+1}: 缺少target字段")
        
        if incomplete:
            return ValidationItem(
                name="步骤完整性",
                level=ValidationLevel.WARNING,
                message=f"发现{len(incomplete)}个不完整的步骤",
                details="; ".join(incomplete[:3])  # 只显示前3个
            )
        
        return ValidationItem(
            name="步骤完整性",
            level=ValidationLevel.SUCCESS,
            message="步骤完整",
            details=f"所有{len(steps)}个步骤都包含必需字段"
        )
    
    def _check_visual_logic(self, steps: List) -> ValidationItem:
        """检查可视化脚本逻辑"""
        if len(steps) > 50:
            return ValidationItem(
                name="步骤逻辑",
                level=ValidationLevel.WARNING,
                message="步骤过多",
                details=f"脚本包含{len(steps)}个步骤，建议拆分"
            )
        
        return ValidationItem(
            name="步骤逻辑",
            level=ValidationLevel.SUCCESS,
            message="逻辑合理",
            details=f"脚本包含{len(steps)}个步骤"
        )


# 全局验证器实例
validator = ScriptValidator()
