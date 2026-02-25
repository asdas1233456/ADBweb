@echo off
chcp 65001 >nul
echo ========================================
echo   手机自动化测试平台 - 启动脚本
echo ========================================
echo.

echo [1/3] 检查环境...
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

echo [2/3] 启动后端服务...
cd backend
start "后端服务" cmd /k "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
cd ..
echo ✅ 后端服务已启动 (http://localhost:8000)
echo.

timeout /t 3 /nobreak >nul

echo [3/3] 启动前端服务...
start "前端服务" cmd /k "npm run dev"
echo ✅ 前端服务已启动 (http://localhost:5173)
echo.

echo ========================================
echo   🎉 启动完成！
echo ========================================
echo.
echo 📌 后端服务: http://localhost:8000
echo 📌 前端服务: http://localhost:5173
echo 📌 API 文档: http://localhost:8000/docs
echo.
echo 按任意键打开浏览器...
pause >nul

start http://localhost:5173

echo.
echo 提示: 关闭此窗口不会停止服务
echo 要停止服务，请关闭对应的命令行窗口
echo.
pause
