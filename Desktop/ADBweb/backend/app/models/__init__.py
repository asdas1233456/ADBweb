"""
数据模型包
"""
from app.models.device import Device
from app.models.script import Script
from app.models.template import Template
from app.models.scheduled_task import ScheduledTask
from app.models.task_log import TaskLog
from app.models.system_config import SystemConfig
from app.models.activity_log import ActivityLog
from app.models.test_case import TestCase
from app.models.ai_script import AIScript

__all__ = [
    "Device",
    "Script",
    "Template",
    "ScheduledTask",
    "TaskLog",
    "SystemConfig",
    "ActivityLog",
    "TestCase",
    "AIScript",
]
