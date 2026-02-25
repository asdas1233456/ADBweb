@echo off
chcp 65001 >nul
echo ================================================================================
echo 快速生成 Allure 报告（使用现有测试结果）
echo ================================================================================
echo.

REM 检查是否存在测试结果
if not exist allure-results (
    echo [错误] 未找到测试结果目录 allure-results
    echo 请先运行测试: python -m pytest test_all_features.py --alluredir=allure-results
    echo.
    pause
    exit /b 1
)

echo [1/2] 生成报告...
allure generate allure-results -o allure-report --clean
if %errorlevel% neq 0 (
    echo [错误] 报告生成失败
    pause
    exit /b 1
)
echo 完成!
echo.

echo [2/2] 打开报告...
allure open allure-report
echo.

echo ================================================================================
echo 报告已在浏览器中打开
echo ================================================================================
