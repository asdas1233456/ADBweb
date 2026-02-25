@echo off
chcp 65001 >nul
echo ========================================
echo ADBweb 平台完整测试套件
echo ========================================
echo.

echo 📋 检查依赖...
pip show pytest >nul 2>&1
if errorlevel 1 (
    echo ❌ pytest未安装，正在安装依赖...
    pip install -r requirements.txt
) else (
    echo ✅ 依赖已安装
)
echo.

echo 🚀 运行完整测试套件...
echo.
pytest test_complete.py -v --tb=short -s
echo.

echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 💡 提示:
echo   - 查看HTML报告: pytest test_complete.py --html=report.html
echo   - 查看覆盖率: pytest test_complete.py --cov=../backend/app --cov-report=html
echo   - 并发运行: pytest test_complete.py -n auto
echo.
pause
