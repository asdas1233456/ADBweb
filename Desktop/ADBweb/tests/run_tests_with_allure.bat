@echo off
chcp 65001 >nul
echo ================================================================================
echo ADBweb 平台测试 - Allure 报告生成
echo ================================================================================
echo.

REM 检查 allure 是否安装
where allure >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Allure 命令行工具
    echo.
    echo 请先安装 Allure:
    echo 1. 下载 Allure: https://github.com/allure-framework/allure2/releases
    echo 2. 解压到任意目录
    echo 3. 将 bin 目录添加到系统 PATH
    echo.
    echo 或使用 Scoop 安装: scoop install allure
    echo.
    pause
    exit /b 1
)

echo [1/4] 清理旧的测试结果...
if exist allure-results rmdir /s /q allure-results
if exist allure-report rmdir /s /q allure-report
echo 完成!
echo.

echo [2/4] 运行测试套件...
python -m pytest test_all_features.py -v --alluredir=allure-results --clean-alluredir
if %errorlevel% neq 0 (
    echo.
    echo [警告] 部分测试失败，但仍会生成报告
    echo.
)
echo 完成!
echo.

echo [3/4] 生成 Allure 报告...
allure generate allure-results -o allure-report --clean
if %errorlevel% neq 0 (
    echo [错误] 报告生成失败
    pause
    exit /b 1
)
echo 完成!
echo.

echo [4/4] 打开 Allure 报告...
allure open allure-report
echo.

echo ================================================================================
echo 测试完成！报告已在浏览器中打开
echo ================================================================================
pause
