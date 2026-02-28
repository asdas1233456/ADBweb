#!/bin/bash

echo "=========================================="
echo "🔄 重启 ADBweb 服务"
echo "=========================================="

# 获取项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# 停止现有服务
echo "⏹️  停止现有服务..."

# 停止后端
pkill -f "uvicorn main:app" && echo "✅ 后端已停止" || echo "ℹ️  后端未运行"

# 停止前端
pkill -f "vite" && echo "✅ 前端已停止" || echo "ℹ️  前端未运行"

# 等待进程完全停止
sleep 2

# 清理日志文件（可选）
# rm -f backend.log frontend.log

# 启动后端
echo "🚀 启动后端服务..."
cd "$PROJECT_DIR/backend"
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端已启动 (PID: $BACKEND_PID)"

# 启动前端
echo "🚀 启动前端服务..."
cd "$PROJECT_DIR"
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ 前端已启动 (PID: $FRONTEND_PID)"

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo "🏥 检查服务状态..."

# 检查后端
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端服务正常 (http://localhost:8000)"
else
    echo "⚠️  后端服务可能未完全启动，请检查日志: tail -f backend.log"
fi

# 检查前端
if curl -f http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ 前端服务正常 (http://localhost:5173)"
else
    echo "⚠️  前端服务可能未完全启动，请检查日志: tail -f frontend.log"
fi

echo "=========================================="
echo "🎉 服务重启完成！"
echo "=========================================="
echo ""
echo "📊 查看日志："
echo "  后端: tail -f $PROJECT_DIR/backend.log"
echo "  前端: tail -f $PROJECT_DIR/frontend.log"
echo ""
echo "🔍 查看进程："
echo "  ps aux | grep uvicorn"
echo "  ps aux | grep vite"
echo ""
echo "⏹️  停止服务："
echo "  pkill -f uvicorn"
echo "  pkill -f vite"
