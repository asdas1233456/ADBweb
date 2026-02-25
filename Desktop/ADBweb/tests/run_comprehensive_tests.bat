@echo off
chcp 65001 > nul
echo ========================================
echo ADBweb 全面测试套件
echo ========================================
echo.

REM 设置环境变量
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM 检查 Python 环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖
echo 检查测试依赖...
pip show pytest >nul 2>&1
if errorlevel 1 (
    echo 安装测试依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

REM 创建报告目录
if not exist "reports" mkdir reports
if not exist "allure-results" mkdir allure-results

echo.
echo 开始运行测试...
echo ========================================

REM 运行测试（限制失败数量，避免过多输出）
python -m pytest test_comprehensive.py --alluredir=allure-results -v --html=reports/report.html --self-contained-html --maxfail=10 --tb=short

REM 检查测试结果
if errorlevel 1 (
    echo.
    echo ❌ 测试执行失败
    echo 请查看上方错误信息
) else (
    echo.
    echo ✅ 测试执行完成
)

echo.
echo ========================================
echo 报告生成
echo ========================================

REM 检查 Allure 是否安装
allure --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Allure 未安装，跳过 Allure 报告生成
    echo 💡 安装 Allure: https://docs.qameta.io/allure/#_installing_a_commandline
    echo 📊 HTML 报告已生成: reports/report.html
) else (
    echo 生成 Allure 报告...
    allure generate allure-results -o allure-report --clean
    if errorlevel 1 (
        echo ❌ Allure 报告生成失败
    ) else (
        echo ✅ Allure 报告生成成功
        echo 📊 报告位置: allure-report/index.html
        
        REM 询问是否打开报告
        set /p choice="是否打开 Allure 报告? (y/n): "
        if /i "%choice%"=="y" (
            allure open allure-report
        )
    )
)

echo.
echo ========================================
echo 测试完成
echo ========================================
echo 📁 HTML 报告: reports/report.html
echo 📁 Allure 报告: allure-report/index.html
echo 📁 测试结果: allure-results/
echo.

pause