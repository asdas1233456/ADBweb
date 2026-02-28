"""
API路由包
"""
from app.api.dashboard import router as dashboard_router
from app.api.devices import router as devices_router
from app.api.scripts import router as scripts_router
from app.api.templates import router as templates_router
from app.api.scheduled_tasks import router as scheduled_tasks_router
from app.api.tasks import router as tasks_router
from app.api.reports import router as reports_router
from app.api.settings import router as settings_router
from app.api.activity_logs import router as activity_logs_router
from app.api.upload import router as upload_router
from app.api.examples import router as examples_router

__all__ = [
    "dashboard_router",
    "devices_router",
    "scripts_router",
    "templates_router",
    "scheduled_tasks_router",
    "tasks_router",
    "reports_router",
    "settings_router",
    "activity_logs_router",
    "upload_router",
    "examples_router",
]
