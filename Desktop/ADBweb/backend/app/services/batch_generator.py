"""
批量脚本生成服务
"""
import asyncio
import json
from typing import List, Dict, Optional
from sqlmodel import Session
from app.services.ai_script_generator import AIScriptGenerator
from app.models.ai_script import AIScript


class BatchScriptGenerator:
    """批量脚本生成器"""
    
    def __init__(self, session: Session, api_key: Optional[str] = None, api_base: Optional[str] = None):
        self.session = session
        self.generator = AIScriptGenerator(api_key, api_base)
    
    async def generate_batch_scripts(
        self,
        prompts: List[str],
        language: str = "adb",
        generate_suite: bool = False
    ) -> Dict[str, any]:
        """
        批量生成脚本
        
        Args:
            prompts: 提示词列表
            language: 脚本语言
            generate_suite: 是否生成测试套件
            
        Returns:
            批量生成结果
        """
        results = []
        suite_script = ""
        
        # 并发生成脚本（限制并发数避免API限制）
        semaphore = asyncio.Semaphore(3)  # 最多3个并发请求
        
        async def generate_single(prompt: str, index: int):
            async with semaphore:
                try:
                    # 验证提示词
                    if not prompt or len(prompt.strip()) < 3:
                        raise ValueError("提示词过短或为空")
                    
                    # 生成脚本
                    script = self.generator.generate_script(prompt, language)
                    
                    # 验证生成的脚本
                    if not script or len(script.strip()) < 10:
                        raise ValueError("生成的脚本内容过短")
                    
                    suggestions = self.generator.optimize_script(script)
                    
                    # 保存到数据库
                    ai_script = AIScript(
                        prompt=prompt,
                        generated_script=script,
                        language=language,
                        optimization_suggestions=str(suggestions),
                        status="success"
                    )
                    self.session.add(ai_script)
                    self.session.commit()
                    self.session.refresh(ai_script)
                    
                    return {
                        "index": index,
                        "id": ai_script.id,
                        "prompt": prompt,
                        "script": script,
                        "suggestions": suggestions,
                        "status": "success"
                    }
                except Exception as e:
                    error_msg = str(e)
                    
                    # 针对规则引擎模式提供更友好的错误信息
                    if not self.generator.use_ai:
                        if "提示词过短" in error_msg:
                            error_msg = "提示词过短，请提供更详细的描述"
                        elif "生成的脚本内容过短" in error_msg:
                            error_msg = "规则引擎无法理解此提示词，建议配置AI Token或使用更具体的关键词"
                        else:
                            error_msg = f"规则引擎生成失败: {error_msg}。建议配置AI Token以获得更好的生成效果"
                    
                    # 记录失败
                    ai_script = AIScript(
                        prompt=prompt,
                        generated_script="",
                        language=language,
                        status="failed",
                        error_message=error_msg
                    )
                    self.session.add(ai_script)
                    self.session.commit()
                    
                    return {
                        "index": index,
                        "prompt": prompt,
                        "script": "",
                        "suggestions": [],
                        "status": "failed",
                        "error": error_msg
                    }
        
        # 创建并发任务
        tasks = [generate_single(prompt, i) for i, prompt in enumerate(prompts)]
        results = await asyncio.gather(*tasks)
        
        # 按索引排序
        results.sort(key=lambda x: x["index"])
        
        # 生成测试套件
        if generate_suite:
            suite_script = self._generate_test_suite(results, language)
        
        # 统计结果
        success_count = sum(1 for r in results if r["status"] == "success")
        failed_count = len(results) - success_count
        
        return {
            "results": results,
            "suite_script": suite_script,
            "statistics": {
                "total": len(results),
                "success": success_count,
                "failed": failed_count,
                "success_rate": success_count / len(results) if results else 0
            }
        }
    
    def _generate_test_suite(self, results: List[Dict], language: str) -> str:
        """生成测试套件脚本"""
        if language == "python":
            return self._generate_python_suite(results)
        else:
            return self._generate_adb_suite(results)
    
    def _generate_python_suite(self, results: List[Dict]) -> str:
        """生成Python测试套件"""
        suite_lines = [
            "#!/usr/bin/env python3",
            "# -*- coding: utf-8 -*-",
            '"""',
            "批量生成的测试套件",
            f"包含 {len(results)} 个测试脚本",
            '"""',
            "",
            "import subprocess",
            "import time",
            "import sys",
            "",
            "class TestSuite:",
            '    """测试套件类"""',
            "",
            "    def __init__(self):",
            "        self.results = []",
            "",
            "    def run_command(self, command):",
            '        """执行ADB命令"""',
            "        try:",
            "            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)",
            "            return result.returncode == 0, result.stdout, result.stderr",
            "        except subprocess.TimeoutExpired:",
            "            return False, '', 'Command timeout'",
            "        except Exception as e:",
            "            return False, '', str(e)",
            "",
        ]
        
        # 为每个脚本生成测试方法
        for i, result in enumerate(results):
            if result["status"] == "success":
                method_name = f"test_{i+1:02d}"
                suite_lines.extend([
                    f"    def {method_name}(self):",
                    f'        """测试: {result["prompt"]}"""',
                    f'        print(f"执行测试 {i+1}: {result["prompt"]}")',
                    "        success = True",
                    "        errors = []",
                    "",
                ])
                
                # 添加脚本命令
                script_lines = result["script"].split("\n")
                for line in script_lines:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if line.startswith("adb "):
                            suite_lines.append(f'        success_cmd, stdout, stderr = self.run_command("{line}")')
                            suite_lines.append("        if not success_cmd:")
                            suite_lines.append("            errors.append(f'命令失败: {line} - {stderr}')")
                            suite_lines.append("            success = False")
                        elif "sleep" in line:
                            if "time.sleep" in line:
                                suite_lines.append(f"        {line}")
                            else:
                                # 转换shell sleep为Python sleep
                                import re
                                match = re.search(r'sleep (\d+)', line)
                                if match:
                                    sleep_time = match.group(1)
                                    suite_lines.append(f"        time.sleep({sleep_time})")
                
                suite_lines.extend([
                    "",
                    "        self.results.append({",
                    f'            "test": "{method_name}",',
                    f'            "description": "{result["prompt"]}",',
                    '            "success": success,',
                    '            "errors": errors',
                    "        })",
                    f'        print(f"测试 {i+1} " + ("通过" if success else "失败"))',
                    "        return success",
                    "",
                ])
        
        # 添加运行所有测试的方法
        suite_lines.extend([
            "    def run_all_tests(self):",
            '        """运行所有测试"""',
            '        print("开始执行批量测试套件...")',
            "        start_time = time.time()",
            "        ",
        ])
        
        # 调用所有测试方法
        for i, result in enumerate(results):
            if result["status"] == "success":
                method_name = f"test_{i+1:02d}"
                suite_lines.append(f"        self.{method_name}()")
        
        suite_lines.extend([
            "",
            "        end_time = time.time()",
            "        duration = end_time - start_time",
            "        ",
            "        # 统计结果",
            "        total = len(self.results)",
            "        passed = sum(1 for r in self.results if r['success'])",
            "        failed = total - passed",
            "        ",
            '        print(f"\\n=== 测试结果统计 ===")',
            '        print(f"总计: {total} 个测试")',
            '        print(f"通过: {passed} 个")',
            '        print(f"失败: {failed} 个")',
            '        print(f"成功率: {passed/total*100:.1f}%")',
            '        print(f"执行时间: {duration:.2f} 秒")',
            "        ",
            "        # 显示失败的测试",
            "        if failed > 0:",
            '            print(f"\\n=== 失败的测试 ===")',
            "            for result in self.results:",
            "                if not result['success']:",
            '                    print(f"- {result[\'test\']}: {result[\'description\']}")',
            "                    for error in result['errors']:",
            '                        print(f"  错误: {error}")',
            "        ",
            "        return passed == total",
            "",
            "",
            'if __name__ == "__main__":',
            "    suite = TestSuite()",
            "    success = suite.run_all_tests()",
            "    sys.exit(0 if success else 1)",
        ])
        
        return "\n".join(suite_lines)
    
    def _generate_adb_suite(self, results: List[Dict]) -> str:
        """生成ADB测试套件"""
        suite_lines = [
            "#!/bin/bash",
            "# 批量生成的ADB测试套件",
            f"# 包含 {len([r for r in results if r['status'] == 'success'])} 个测试脚本",
            "",
            "# 颜色定义",
            "RED='\\033[0;31m'",
            "GREEN='\\033[0;32m'",
            "YELLOW='\\033[1;33m'",
            "NC='\\033[0m' # No Color",
            "",
            "# 统计变量",
            "TOTAL_TESTS=0",
            "PASSED_TESTS=0",
            "FAILED_TESTS=0",
            "",
            "# 日志函数",
            "log_info() {",
            '    echo -e "${YELLOW}[INFO]${NC} $1"',
            "}",
            "",
            "log_success() {",
            '    echo -e "${GREEN}[SUCCESS]${NC} $1"',
            "}",
            "",
            "log_error() {",
            '    echo -e "${RED}[ERROR]${NC} $1"',
            "}",
            "",
            "# 执行测试函数",
            "run_test() {",
            "    local test_name=$1",
            "    local test_desc=$2",
            "    ",
            '    echo ""',
            '    log_info "执行测试: $test_name - $test_desc"',
            "    TOTAL_TESTS=$((TOTAL_TESTS + 1))",
            "    ",
            "    # 执行测试脚本",
            "    if $test_name; then",
            '        log_success "测试通过: $test_name"',
            "        PASSED_TESTS=$((PASSED_TESTS + 1))",
            "        return 0",
            "    else",
            '        log_error "测试失败: $test_name"',
            "        FAILED_TESTS=$((FAILED_TESTS + 1))",
            "        return 1",
            "    fi",
            "}",
            "",
        ]
        
        # 为每个脚本生成测试函数
        for i, result in enumerate(results):
            if result["status"] == "success":
                function_name = f"test_{i+1:02d}"
                suite_lines.extend([
                    f"# 测试 {i+1}: {result['prompt']}",
                    f"{function_name}() {{",
                ])
                
                # 添加脚本命令
                script_lines = result["script"].split("\n")
                for line in script_lines:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if line.startswith("adb "):
                            suite_lines.append(f"    {line} || return 1")
                        elif "sleep" in line:
                            suite_lines.append(f"    {line}")
                        else:
                            suite_lines.append(f"    # {line}")
                
                suite_lines.extend([
                    "    return 0",
                    "}",
                    "",
                ])
        
        # 添加主执行函数
        suite_lines.extend([
            "# 主执行函数",
            "main() {",
            '    log_info "开始执行批量测试套件..."',
            "    START_TIME=$(date +%s)",
            "    ",
        ])
        
        # 调用所有测试函数
        for i, result in enumerate(results):
            if result["status"] == "success":
                function_name = f"test_{i+1:02d}"
                suite_lines.append(f'    run_test "{function_name}" "{result["prompt"]}"')
        
        suite_lines.extend([
            "    ",
            "    END_TIME=$(date +%s)",
            "    DURATION=$((END_TIME - START_TIME))",
            "    ",
            "    # 输出统计结果",
            '    echo ""',
            '    echo "=== 测试结果统计 ==="',
            '    echo "总计: $TOTAL_TESTS 个测试"',
            '    echo "通过: $PASSED_TESTS 个"',
            '    echo "失败: $FAILED_TESTS 个"',
            '    if [ $TOTAL_TESTS -gt 0 ]; then',
            '        SUCCESS_RATE=$(( PASSED_TESTS * 100 / TOTAL_TESTS ))',
            '        echo "成功率: ${SUCCESS_RATE}%"',
            '    fi',
            '    echo "执行时间: ${DURATION} 秒"',
            "    ",
            "    # 返回结果",
            "    if [ $FAILED_TESTS -eq 0 ]; then",
            '        log_success "所有测试通过！"',
            "        return 0",
            "    else",
            '        log_error "有 $FAILED_TESTS 个测试失败"',
            "        return 1",
            "    fi",
            "}",
            "",
            "# 执行主函数",
            "main",
            "exit $?",
        ])
        
        return "\n".join(suite_lines)
    
    def generate_workflow_scripts(
        self,
        workflow_steps: List[str],
        language: str = "adb"
    ) -> Dict[str, any]:
        """
        生成工作流脚本（步骤间有依赖关系）
        
        Args:
            workflow_steps: 工作流步骤列表
            language: 脚本语言
            
        Returns:
            工作流脚本结果
        """
        individual_scripts = []
        combined_script = ""
        
        # 生成各个步骤的脚本
        for i, step in enumerate(workflow_steps):
            try:
                # 验证步骤描述
                if not step or len(step.strip()) < 3:
                    raise ValueError("步骤描述过短或为空")
                
                script = self.generator.generate_script(step, language)
                
                # 验证生成的脚本
                if not script or len(script.strip()) < 10:
                    raise ValueError("生成的脚本内容过短")
                
                suggestions = self.generator.optimize_script(script)
                
                individual_scripts.append({
                    "step": i + 1,
                    "description": step,
                    "script": script,
                    "suggestions": suggestions
                })
            except Exception as e:
                error_msg = str(e)
                
                # 针对规则引擎模式提供更友好的错误信息
                if not self.generator.use_ai:
                    if "步骤描述过短" in error_msg:
                        error_msg = "步骤描述过短，请提供更详细的描述"
                    elif "生成的脚本内容过短" in error_msg:
                        error_msg = "规则引擎无法理解此步骤，建议配置AI Token或使用更具体的关键词"
                    else:
                        error_msg = f"规则引擎生成失败: {error_msg}。建议配置AI Token以获得更好的工作流生成效果"
                
                individual_scripts.append({
                    "step": i + 1,
                    "description": step,
                    "script": "",
                    "suggestions": [],
                    "error": error_msg
                })
        
        # 生成组合脚本
        combined_script = self._generate_workflow_script(individual_scripts, language)
        
        return {
            "individual_scripts": individual_scripts,
            "combined_script": combined_script,
            "workflow_steps": workflow_steps
        }
    
    def _generate_workflow_script(self, scripts: List[Dict], language: str) -> str:
        """生成工作流组合脚本"""
        if language == "python":
            return self._generate_python_workflow(scripts)
        else:
            return self._generate_adb_workflow(scripts)
    
    def _generate_python_workflow(self, scripts: List[Dict]) -> str:
        """生成Python工作流脚本"""
        workflow_lines = [
            "#!/usr/bin/env python3",
            "# -*- coding: utf-8 -*-",
            '"""',
            "自动生成的工作流脚本",
            f"包含 {len(scripts)} 个步骤",
            '"""',
            "",
            "import subprocess",
            "import time",
            "import sys",
            "",
            "class Workflow:",
            '    """工作流执行器"""',
            "",
            "    def __init__(self):",
            "        self.current_step = 0",
            "        self.results = []",
            "",
            "    def execute_command(self, command):",
            '        """执行命令"""',
            "        try:",
            "            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)",
            "            return result.returncode == 0, result.stdout, result.stderr",
            "        except Exception as e:",
            "            return False, '', str(e)",
            "",
            "    def run_workflow(self):",
            '        """执行完整工作流"""',
            '        print("开始执行工作流...")',
            "        start_time = time.time()",
            "",
        ]
        
        # 添加每个步骤
        for script in scripts:
            if "error" not in script:
                step_num = script["step"]
                workflow_lines.extend([
                    f"        # 步骤 {step_num}: {script['description']}",
                    f"        print(f'执行步骤 {step_num}: ' + script['description'])",
                    "        self.current_step = " + str(step_num),
                    "        step_success = True",
                    "",
                ])
                
                # 添加脚本命令
                script_lines = script["script"].split("\n")
                for line in script_lines:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if line.startswith("adb "):
                            workflow_lines.append(f'        success, stdout, stderr = self.execute_command("{line}")')
                            workflow_lines.append("        if not success:")
                            workflow_lines.append(f'            print(f"步骤 {step_num} 失败: {{stderr}}")')
                            workflow_lines.append("            step_success = False")
                            workflow_lines.append("            break")
                        elif "sleep" in line:
                            if "time.sleep" in line:
                                workflow_lines.append(f"        {line}")
                            else:
                                import re
                                match = re.search(r'sleep (\d+)', line)
                                if match:
                                    sleep_time = match.group(1)
                                    workflow_lines.append(f"        time.sleep({sleep_time})")
                
                workflow_lines.extend([
                    "",
                    "        self.results.append({",
                    f'            "step": {step_num},',
                    f"            \"description\": \"{script['description']}\",",
                    '            "success": step_success',
                    "        })",
                    "",
                    "        if not step_success:",
                    f'            print(f"工作流在步骤 {step_num} 失败，停止执行")',
                    "            return False",
                    "",
                ])
        
        workflow_lines.extend([
            "        end_time = time.time()",
            "        duration = end_time - start_time",
            '        print(f"工作流执行完成，耗时 {duration:.2f} 秒")',
            "        return True",
            "",
            "",
            'if __name__ == "__main__":',
            "    workflow = Workflow()",
            "    success = workflow.run_workflow()",
            "    sys.exit(0 if success else 1)",
        ])
        
        return "\n".join(workflow_lines)
    
    def _generate_adb_workflow(self, scripts: List[Dict]) -> str:
        """生成ADB工作流脚本"""
        workflow_lines = [
            "#!/bin/bash",
            "# 自动生成的ADB工作流脚本",
            f"# 包含 {len(scripts)} 个步骤",
            "",
            "# 颜色定义",
            "RED='\\033[0;31m'",
            "GREEN='\\033[0;32m'",
            "YELLOW='\\033[1;33m'",
            "NC='\\033[0m'",
            "",
            "# 当前步骤",
            "CURRENT_STEP=0",
            "",
            "# 日志函数",
            "log_info() {",
            '    echo -e "${YELLOW}[步骤 $CURRENT_STEP]${NC} $1"',
            "}",
            "",
            "log_success() {",
            '    echo -e "${GREEN}[成功]${NC} $1"',
            "}",
            "",
            "log_error() {",
            '    echo -e "${RED}[失败]${NC} $1"',
            "    exit 1",
            "}",
            "",
            "# 主工作流函数",
            "main() {",
            '    log_info "开始执行工作流..."',
            "    START_TIME=$(date +%s)",
            "",
        ]
        
        # 添加每个步骤
        for script in scripts:
            if "error" not in script:
                step_num = script["step"]
                workflow_lines.extend([
                    f"    # 步骤 {step_num}: {script['description']}",
                    f"    CURRENT_STEP={step_num}",
                    f"    log_info \"{script['description']}\"",
                    "",
                ])
                
                # 添加脚本命令
                script_lines = script["script"].split("\n")
                for line in script_lines:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if line.startswith("adb "):
                            workflow_lines.append(f"    {line} || log_error '步骤 {step_num} 执行失败'")
                        elif "sleep" in line:
                            workflow_lines.append(f"    {line}")
                        else:
                            workflow_lines.append(f"    # {line}")
                
                workflow_lines.extend([
                    f'    log_success "步骤 {step_num} 完成"',
                    "",
                ])
        
        workflow_lines.extend([
            "    END_TIME=$(date +%s)",
            "    DURATION=$((END_TIME - START_TIME))",
            '    log_success "工作流执行完成，耗时 ${DURATION} 秒"',
            "}",
            "",
            "# 执行主函数",
            "main",
        ])
        
        return "\n".join(workflow_lines)