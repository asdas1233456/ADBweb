"""
数据模型包
"""
from app.models.device import Device
from app.models.script import Script
from app.models.scheduled_task import ScheduledTask
from app.models.task_log import TaskLog
from app.models.system_config import SystemConfig
from app.models.activity_log import ActivityLog
from app.models.ai_script import AIScript
from app.models.script_version import ScriptVersion
from app.models.device_health import DeviceHealthRecord, DeviceUsageStats, DeviceAlert, AlertRule
from app.models.failure_analysis import FailureAnalysis, ScriptFailureStats, StepExecutionLog

__all__ = [
    "Device",
    "Script",
    "ScheduledTask",
    "TaskLog",
    "SystemConfig",
    "ActivityLog",
    "AIScript",
    "ScriptVersion",
    "DeviceHealthRecord",
    "DeviceUsageStats", 
    "DeviceAlert",
    "AlertRule",
    "FailureAnalysis",
    "ScriptFailureStats",
    "StepExecutionLog",
]
