"""
验证器V2测试套件
"""
import pytest
import time
from app.validator import (
    get_validator, ScriptLanguage, ValidationLevel, RiskLevel
)


class TestBasicValidation:
    """基础验证测试"""
    
    def test_safe_python_script(self):
        """测试安全的Python脚本"""
        validator = get_validator()
        
        code = """
import uiautomator2 as d2

# 连接设备
device = d2.connect()

# 点击按钮
device.click(100, 200)
print("操作完成")
"""
        
        result = validator.validate(code, ScriptLanguage.PYTHON)
        
        assert result.passed is True
        assert result.score >= 80
        assert result.risk_level in [RiskLevel.SAFE, RiskLevel.LOW]
    
    def test_dangerous_eval(self):
        """测试危险的eval函数"""
        validator = get_validator()
        
        code = """
user_input = input("输入表达式: ")
result = eval(user_input)  # 危险！
print(result)
"""
        
        result = validator.validate(code, ScriptLanguage.PYTHON)
        
        assert result.passed is False
        assert result.risk_score >= 800
        assert any(issue.rule_id == "SEC_PY_001" for issue in result.issues)
    
    def test_command_injection(self):
        """测试命令注入"""
        validator = get_validator()
        
        code = """
import os
filename = input("文件名: ")
os.system(f"cat {filename}")  # 命令注入风险
"""
        
        result = validator.validate(code, ScriptLanguage.PYTHON)
        
        assert result.passed is False
        assert result.risk_score >= 800
        assert any("os.system" in issue.message for issue in result.issues)
    
    def test_taint_analysis(self):
        """测试污点分析"""
        validator = get_validator()
        
        code = """
user_input = input("输入: ")
command = f"echo {user_input}"
import os
os.system(command)  # 污点数据流入危险函数
"""
        
        result = validator.validate(code, ScriptLanguage.PYTHON)
        
        assert result.passed is False
        # 应该检测到污点传播
        assert any("污点" in issue.message or "用户输入" in issue.message 
                  for issue in result.issues)


class TestObfuscationDetection:
    """混淆检测测试"""
    
    def test_base64_obfuscation(self):
        """测试Base64混淆检测"""
        validator = get_validator()
        
        code = """
import base64
encoded = "cHJpbnQoJ0hlbGxvJyk="
decoded = base64.b64decode(encoded)
exec(decoded)
"""
        
        result = validator.validate(code, ScriptLanguage.PYTHON)
        
        assert any("Base64" in issue.message for issue in result.issues)
        assert any("exec" in issue.message for issue in result.issues)
    
    def test_hex_obfuscation(self):
        """测试十六进制混淆检测"""
        validator = get_validator()
        
        code = r"""
data = "\x48\x65\x6c\x6c\x6f\x20\x57\x6f\x72\x6c\x64"
print(data)
"""
        
        result = validator.validate(code, ScriptLanguage.PYTHON)
        
        # 少量十六进制不应该触发
        assert result.passed is True


class TestBatchValidation:
    """批量验证测试"""
    
    def test_batch_validation(self):
        """测试批量验证"""
        validator = get_validator()
        
        scripts = [
            {"name": "safe1.py", "code": "print('Hello')", "language": "python"},
            {"name": "safe2.py", "code": "x = 1 + 1", "language": "python"},
            {"name": "danger1.py", "code": "eval('1+1')", "language": "python"},
            {"name": "danger2.py", "code": "import os\nos.system('ls')", "language": "python"},
        ]
        
        batch_result = validator.validate_batch(scripts)
        
        assert batch_result.total_scripts == 4
        assert batch_result.completed == 4
        assert batch_result.passed == 2
        assert batch_result.failed == 2
        assert batch_result.pass_rate == 50.0
    
    def test_batch_performance(self):
        """测试批量验证性能"""
        validator = get_validator()
        
        # 生成100个脚本
        scripts = [
            {
                "name": f"script_{i}.py",
                "code": f"print('Script {i}')",
                "language": "python"
            }
            for i in range(100)
        ]
        
        start_time = time.time()
        batch_result = validator.validate_batch(scripts, max_workers=10)
        elapsed = time.time() - start_time
        
        assert batch_result.completed == 100
        assert elapsed < 10.0  # 100个脚本应该在10秒内完成
        assert batch_result.avg_time < 0.1  # 平均每个<0.1秒


class TestBatchScriptValidation:
    """Batch脚本验证测试"""
    
    def test_safe_batch_script(self):
        """测试安全的Batch脚本"""
        validator = get_validator()
        
        code = """
@echo off
echo Hello World
adb devices
adb shell input tap 100 200
"""
        
        result = validator.validate(code, ScriptLanguage.BATCH)
        
        assert result.passed is True
    
    def test_dangerous_delete(self):
        """测试危险的删除命令"""
        validator = get_validator()
        
        code = """
@echo off
del /s /q C:\\temp\\*
"""
        
        result = validator.validate(code, ScriptLanguage.BATCH)
        
        assert result.passed is False
        assert result.risk_score >= 800
    
    def test_format_command(self):
        """测试格式化命令"""
        validator = get_validator()
        
        code = """
format C: /q
"""
        
        result = validator.validate(code, ScriptLanguage.BATCH)
        
        assert result.passed is False
        assert result.risk_score >= 900


class TestPerformance:
    """性能测试"""
    
    def test_single_script_performance(self):
        """测试单脚本验证性能"""
        validator = get_validator()
        
        code = """
import uiautomator2 as d2

device = d2.connect()
for i in range(100):
    device.click(100 + i, 200 + i)
    print(f"点击 {i}")
"""
        
        start_time = time.time()
        result = validator.validate(code, ScriptLanguage.PYTHON)
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0  # 单脚本验证应该<1秒
        assert result.metrics.total_time < 1.0
    
    def test_large_script_performance(self):
        """测试大脚本性能"""
        validator = get_validator()
        
        # 生成1000行代码
        lines = ["print(f'Line {i}')" for i in range(1000)]
        code = "\n".join(lines)
        
        start_time = time.time()
        result = validator.validate(code, ScriptLanguage.PYTHON)
        elapsed = time.time() - start_time
        
        assert elapsed < 2.0  # 1000行代码应该<2秒


class TestRiskScoring:
    """风险评分测试"""
    
    def test_risk_levels(self):
        """测试风险等级分类"""
        validator = get_validator()
        
        test_cases = [
            ("print('Hello')", RiskLevel.SAFE),
            ("import requests\nrequests.get('http://example.com')", RiskLevel.LOW),
            ("open('file.txt', 'w').write('data')", RiskLevel.MEDIUM),
            ("import subprocess\nsubprocess.run(['ls'], shell=True)", RiskLevel.HIGH),
            ("eval(input())", RiskLevel.CRITICAL),
        ]
        
        for code, expected_level in test_cases:
            result = validator.validate(code, ScriptLanguage.PYTHON)
            assert result.risk_level == expected_level or \
                   abs(result.risk_score - self._level_to_score(expected_level)) < 200
    
    def _level_to_score(self, level: RiskLevel) -> int:
        """风险等级转分数"""
        mapping = {
            RiskLevel.SAFE: 100,
            RiskLevel.LOW: 300,
            RiskLevel.MEDIUM: 500,
            RiskLevel.HIGH: 700,
            RiskLevel.CRITICAL: 900
        }
        return mapping.get(level, 0)


class TestStatistics:
    """统计功能测试"""
    
    def test_validator_stats(self):
        """测试验证器统计"""
        validator = get_validator()
        
        # 执行一些验证
        validator.validate("print('1')", ScriptLanguage.PYTHON)
        validator.validate("eval('1')", ScriptLanguage.PYTHON)
        validator.validate("print('2')", ScriptLanguage.PYTHON)
        
        stats = validator.get_stats()
        
        assert stats["total_validations"] >= 3
        assert "pass_rate" in stats
        assert "avg_time" in stats
        assert "rule_stats" in stats


# 性能基准测试
def test_performance_benchmark():
    """性能基准测试 - 1000个脚本"""
    validator = get_validator()
    
    # 生成1000个不同的脚本
    scripts = []
    for i in range(1000):
        if i % 4 == 0:
            code = f"print('Script {i}')"
        elif i % 4 == 1:
            code = f"import time\ntime.sleep(0.001)\nprint({i})"
        elif i % 4 == 2:
            code = f"x = {i}\ny = x * 2\nprint(y)"
        else:
            code = f"def func_{i}():\n    return {i}\nfunc_{i}()"
        
        scripts.append({
            "name": f"script_{i}.py",
            "code": code,
            "language": "python"
        })
    
    print("\n" + "="*60)
    print("性能基准测试: 1000个脚本批量验证")
    print("="*60)
    
    start_time = time.time()
    batch_result = validator.validate_batch(scripts, max_workers=10)
    elapsed = time.time() - start_time
    
    print(f"\n总脚本数: {batch_result.total_scripts}")
    print(f"完成数: {batch_result.completed}")
    print(f"通过数: {batch_result.passed}")
    print(f"失败数: {batch_result.failed}")
    print(f"通过率: {batch_result.pass_rate}%")
    print(f"\n总耗时: {elapsed:.2f}秒")
    print(f"平均耗时: {batch_result.avg_time*1000:.1f}毫秒/脚本")
    print(f"吞吐量: {1000/elapsed:.1f}脚本/秒")
    print(f"\n风险分布:")
    for level, count in batch_result.risk_distribution.items():
        print(f"  {level}: {count}")
    
    print("="*60)
    
    # 性能断言
    assert elapsed < 60.0  # 1000个脚本应该在60秒内完成
    assert batch_result.avg_time < 0.1  # 平均每个<100ms
    assert 1000/elapsed > 16  # 吞吐量>16脚本/秒


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
