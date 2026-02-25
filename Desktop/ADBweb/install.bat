@echo off
chcp 65001 >nul
echo ========================================
echo   手机自动化测试平台 - 安装脚本
echo ========================================
echo.

echo [1/4] 检查环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到 Node.js，请先安装 Node.js 16+
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.

echo [2/4] 安装前端依赖...
call npm install
if %errorlevel% neq 0 (
    echo ❌ 前端依赖安装失败
    pause
    exit /b 1
)
echo ✅ 前端依赖安装完成
echo.

echo [3/4] 安装后端依赖...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 后端依赖安装失败
    cd ..
    pause
    exit /b 1
)
cd ..
echo ✅ 后端依赖安装完成
echo.

echo [4/4] 初始化数据库...
cd backend
python migrate_db.py
if %errorlevel% neq 0 (
    echo ⚠️  数据库迁移失败，可能已经初始化过
) else (
    echo ✅ 数据库初始化完成
)
cd ..
echo.

echo ========================================
echo   🎉 安装完成！
echo ========================================
echo.
echo 下一步:
echo   1. 运行 start.bat 启动服务
echo   2. 访问 http://localhost:5173
echo.
pause
