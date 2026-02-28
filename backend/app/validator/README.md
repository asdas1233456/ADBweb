# 脚本验证器 V2.0 - 使用手册

## 概述

生产级脚本验证系统，支持Python、Batch、Shell、可视化JSON脚本的全方位安全检测和质量分析。

### 核心特性

- ✅ **AST语义分析** - 深度代码理解，精准检测安全风险
- ✅ **符号执行** - 追踪变量流向，识别污点数据
- ✅ **混淆检测** - 识别Base64、十六进制等混淆手段
- ✅ **规则引擎** - 100+内置规则，支持热加载和自定义
- ✅ **批量验证** - 支持1000+脚本并发验证
- ✅ **性能优化** - 单脚本<1秒，批量验证高效并发
- ✅ **风险量化** - 0-1000分风险评分，可配置阈值
- ✅ **全链路监控** - QPS、通过率、耗时等实时指标

## 快速开始

### 1. 基本使用

```python
from app.validator import get_validator, ScriptLanguage

# 获取验证器实例
validator = get_validator()

# 验证Python脚本
code = """
import os
os.system('ls')  # 危险操作
"""

result = validator.validate(
    code=code,
    language=ScriptLanguage.PYTHON,
    script_name="test_script.py"
)

# 检查结果
print(f"通过: {result.passed}")
print(f"质量分: {result.score}/100")
print(f"风险分: {result.risk_score}/1000")
print(f"风险等级: {result.risk_level}")

# 查看问题
for issue in result.issues:
    print(f"[{issue.level}] {issue.message}")
    print(f"  位置: 第{issue.line_number}行")
    print(f"  风险分: {issue.risk_score}")
    print(f"  建议: {', '.join(issue.suggestions)}")
```

### 2. 批量验证

```python
# 准备脚本列表
scripts = [
    {
        "name": "script1.py",
        "code": "print('Hello')",
        "language": "python"
    },
    {
        "name": "script2.py",
        "code": "import os\nos.system('ls')",
        "language": "python"
    }
]

# 批量验证
batch_result = validator.validate_batch(scripts, max_workers=10)

print(f"总数: {batch_result.total_scripts}")
print(f"通过: {batch_result.passed}")
print(f"失败: {batch_result.failed}")
print(f"通过率: {batch_result.pass_rate}%")
print(f"总耗时: {batch_result.total_time:.2f}秒")
print(f"平均耗时: {batch_result.avg_time:.3f}秒")

# 风险分布
print("风险分布:", batch_result.risk_distribution)
```

### 3. 异步验证

```python
import asyncio

async def validate_async_example():
    validator = get_validator()
    
    result = await validator.validate_async(
        code="print('Hello')",
        language=ScriptLanguage.PYTHON
    )
    
    return result

# 运行
result = asyncio.run(validate_async_example())
```

## 配置说明

### 配置文件位置

`app/validator/config/validator_config.yaml`

### 关键配置项

#### 1. 风险阈值配置

```yaml
security:
  risk_thresholds:
    production: 200    # 生产环境：风险分>200拒绝
    staging: 500       # 测试环境：风险分>500拒绝
    development: 800   # 开发环境：风险分>800拒绝
```

#### 2. 性能配置

```yaml
performance:
  single_timeout: 1.0      # 单脚本超时（秒）
  batch_timeout: 60.0      # 批量超时（秒）
  max_workers: 10          # 最大并发数
  ast_cache_size: 1000     # AST缓存大小
```

#### 3. 规则引擎配置

```yaml
rules:
  hot_reload: true         # 启用热加载
  reload_interval: 60      # 检查间隔（秒）
  rules_path: "app/validator/rules"
  
  builtin_rules:
    security: true         # 安全规则（50+）
    quality: true          # 质量规则（30+）
    best_practice: true    # 最佳实践（20+）
```

## 规则系统

### 内置规则分类

1. **安全规则（50+）**
   - 代码注入（eval, exec, compile）
   - 命令注入（os.system, subprocess）
   - SQL注入
   - 路径遍历
   - 反序列化漏洞
   - 密码学问题
   - XML外部实体注入
   - 等等...

2. **质量规则（30+）**
   - 代码复杂度
   - 注释率
   - 函数长度
   - 命名规范
   - 等等...

3. **最佳实践规则（20+）**
   - 异常处理
   - 日志输出
   - 资源管理
   - 等等...

### 自定义规则

创建规则文件：`custom_rules/my_rules.yaml`

```yaml
rules:
  - id: CUSTOM_001
    name: "禁止使用time.sleep"
    category: best_practice
    description: "不建议使用time.sleep阻塞线程"
    severity: warning
    risk_score: 100
    priority: 500
    enabled: true
    languages: [python]
    pattern: 'time\.sleep\s*\('
    suggestions:
      - "使用asyncio.sleep替代"
      - "考虑使用定时器"
    fix_examples:
      - "# 不推荐: time.sleep(1)"
      - "# 推荐: await asyncio.sleep(1)"
```

加载自定义规则：

```python
validator = ScriptValidatorV2(config_path="custom_config.yaml")
```

## 高级功能

### 1. 规则白名单/黑名单

```python
# 只使用特定规则
validator.rule_engine.add_to_whitelist(["SEC_PY_001", "SEC_PY_002"])

# 排除特定规则
validator.rule_engine.add_to_blacklist(["SEC_PY_080"])
```

### 2. 手动重载规则

```python
# 更新规则文件后
validator.reload_rules()
```

### 3. 获取统计信息

```python
stats = validator.get_stats()
print(f"总验证次数: {stats['total_validations']}")
print(f"通过率: {stats['pass_rate']}%")
print(f"平均耗时: {stats['avg_time']:.3f}秒")
print(f"规则统计: {stats['rule_stats']}")
```

### 4. 结果导出

```python
# 导出为JSON
result_dict = result.to_dict()

# 导出为JSON（包含敏感信息）
result_dict = result.to_dict(include_sensitive=True)

# 保存到文件
import json
with open('validation_result.json', 'w') as f:
    json.dump(result_dict, f, indent=2, ensure_ascii=False)
```

## API集成

### FastAPI集成示例

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.validator import get_validator, ScriptLanguage

router = APIRouter(prefix="/api/v2/validator")

class ValidateRequest(BaseModel):
    code: str
    language: str = "python"
    script_name: str = "script"

@router.post("/validate")
async def validate_script(request: ValidateRequest):
    """验证脚本"""
    try:
        validator = get_validator()
        
        result = await validator.validate_async(
            code=request.code,
            language=ScriptLanguage(request.language),
            script_name=request.script_name
        )
        
        return {
            "success": True,
            "data": result.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate/batch")
async def validate_batch(scripts: List[Dict[str, Any]]):
    """批量验证"""
    validator = get_validator()
    
    batch_result = validator.validate_batch(scripts)
    
    return {
        "success": True,
        "data": batch_result.to_dict()
    }

@router.get("/stats")
async def get_stats():
    """获取统计信息"""
    validator = get_validator()
    return validator.get_stats()
```

## 性能优化建议

### 1. 批量验证优化

```python
# 调整并发数
batch_result = validator.validate_batch(
    scripts,
    max_workers=20  # 根据CPU核心数调整
)
```

### 2. 缓存优化

```yaml
performance:
  ast_cache_size: 2000     # 增加缓存
  rule_cache_size: 1000
```

### 3. 规则优化

```python
# 只启用必要的规则分类
validator.rule_engine.get_rules(
    language=ScriptLanguage.PYTHON,
    category=RuleCategory.SECURITY  # 只检查安全规则
)
```

## 监控和告警

### 1. 获取实时指标

```python
stats = validator.get_stats()

# QPS计算
qps = stats['total_validations'] / stats['total_time']

# 通过率
pass_rate = stats['pass_rate']

# 平均耗时
avg_latency = stats['avg_time']
```

### 2. 风险分布分析

```python
batch_result = validator.validate_batch(scripts)

# 风险分布
distribution = batch_result.risk_distribution
print(f"安全: {distribution.get('safe', 0)}")
print(f"低风险: {distribution.get('low', 0)}")
print(f"中风险: {distribution.get('medium', 0)}")
print(f"高风险: {distribution.get('high', 0)}")
print(f"严重: {distribution.get('critical', 0)}")
```

## 故障排查

### 1. 验证失败

```python
if not result.passed:
    print("失败原因:")
    for suggestion in result.suggestions:
        print(f"  - {suggestion}")
    
    print("\n问题列表:")
    for issue in result.issues:
        if issue.level in [ValidationLevel.ERROR, ValidationLevel.CRITICAL]:
            print(f"  [{issue.level}] {issue.message}")
```

### 2. 性能问题

```python
# 检查耗时分布
print(f"解析耗时: {result.metrics.parse_time:.3f}秒")
print(f"分析耗时: {result.metrics.analysis_time:.3f}秒")
print(f"规则检查耗时: {result.metrics.rule_check_time:.3f}秒")
```

### 3. 规则问题

```python
# 查看规则统计
rule_stats = validator.rule_engine.get_rule_stats()
print(f"总规则数: {rule_stats['total']}")
print(f"启用规则: {rule_stats['enabled']}")
print(f"按分类: {rule_stats['by_category']}")
```

## 最佳实践

1. **生产环境配置**
   - 设置合理的风险阈值（建议200）
   - 启用规则热加载
   - 配置监控和告警

2. **批量验证**
   - 根据服务器性能调整并发数
   - 设置合理的超时时间
   - 实现失败重试机制

3. **规则管理**
   - 定期更新规则库
   - 根据业务需求自定义规则
   - 使用白名单控制规则范围

4. **性能优化**
   - 启用缓存
   - 异步验证
   - 合理的并发控制

## 版本历史

### V2.0.0 (2026-02-26)
- ✨ 全新架构设计
- ✨ AST语义分析
- ✨ 符号执行和污点追踪
- ✨ 混淆检测
- ✨ 规则引擎（100+规则）
- ✨ 批量验证支持
- ✨ 性能优化（<1秒/脚本）
- ✨ 风险量化评估
- ✨ 全链路监控

## 技术支持

- 文档：本README
- 配置示例：`config/validator_config.yaml`
- 规则示例：`rules/security_rules.yaml`
- 测试用例：`tests/test_validator_v2.py`

## License

MIT License
