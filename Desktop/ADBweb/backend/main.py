"""
FastAPI 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.core.database import create_db_and_tables
from app.utils.init_data import init_system_config, init_templates
from app.utils.init_examples import init_all_examples
from app.services.scheduler_service import scheduler_service
from app.api import (
    dashboard_router,
    devices_router,
    scripts_router,
    templates_router,
    scheduled_tasks_router,
    tasks_router,
    reports_router,
    settings_router,
    activity_logs_router,
    upload_router,
    examples_router,
)
from app.api.websocket import router as websocket_router
from app.api.device_health import router as device_health_router
from app.api.failure_analysis import router as failure_analysis_router
from app.api.ai_script import router as ai_script_router
from app.api.test_case import router as test_case_router
from app.api.script_templates import router as script_templates_router
from app.services.health_scheduler import health_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("[INFO] 正在初始化数据库...")
    create_db_and_tables()
    
    # 创建数据库会话用于初始化
    from app.core.database import engine
    from sqlmodel import Session
    
    with Session(engine) as db:
        print("[INFO] 正在初始化系统配置...")
        init_system_config(db)
        
        print("[INFO] 正在初始化模板数据...")
        init_templates(db)
        
        print("[INFO] 正在初始化脚本模板...")
        from app.services.template_service import init_builtin_templates
        init_builtin_templates(db)
        
        print("[INFO] 正在初始化示例库数据...")
        init_all_examples(db)
    
    print("[INFO] 正在创建上传目录...")
    os.makedirs("uploads/scripts", exist_ok=True)
    os.makedirs("uploads/screenshots", exist_ok=True)
    
    print("[INFO] 正在启动定时任务调度器...")
    # 延迟加载定时任务，避免阻塞启动
    # scheduler_service.load_tasks_from_db()
    
    print("[INFO] 正在启动健康度监控调度器...")
    health_scheduler.start()
    
    print("[INFO] 应用启动完成！")
    
    yield
    
    # 关闭时执行
    print("[INFO] 正在关闭定时任务调度器...")
    scheduler_service.shutdown()
    print("[INFO] 正在关闭健康度监控调度器...")
    health_scheduler.shutdown()
    print("[INFO] 应用已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="手机自动化测试平台 API",
    description="基于 FastAPI + SQLModel + UIAutomator2 的手机自动化测试平台",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # 允许的前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册路由
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(devices_router, prefix="/api/v1")
app.include_router(scripts_router, prefix="/api/v1")
app.include_router(templates_router, prefix="/api/v1")
app.include_router(scheduled_tasks_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
app.include_router(activity_logs_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(examples_router, prefix="/api/v1")
app.include_router(websocket_router, prefix="/api/v1")  # WebSocket 路由
app.include_router(device_health_router, prefix="/api/v1")  # 设备健康度路由
app.include_router(failure_analysis_router, prefix="/api/v1")  # 失败分析路由
app.include_router(ai_script_router, prefix="/api/v1")  # AI脚本生成路由
app.include_router(test_case_router, prefix="/api/v1")  # 测试用例推荐路由
app.include_router(script_templates_router, prefix="/api/v1")  # 脚本模板路由


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "手机自动化测试平台 API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    )
