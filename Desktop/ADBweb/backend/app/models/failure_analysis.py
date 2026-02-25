"""
失败分析相关模型
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class FailureAnalysis(SQLModel, table=True):
    """失败分析表"""
    __tablename__ = "failure_analysis"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    task_log_id: int = Field(foreign_key="task_log.id", description="任务日志ID")
    failure_type: str = Field(max_length=50, description="失败类型")
    failed_step_index: Optional[int] = Field(default=None, description="失败步骤索引")
    failed_step_name: Optional[str] = Field(default=None, max_length=200, description="失败步骤名称")
    error_message: Optional[str] = Field(default=None, description="错误消息")
    stack_trace: Optional[str] = Field(default=None, description="堆栈跟踪")
    screenshot_path: Optional[str] = Field(default=None, max_length=500, description="失败截图路径")
    suggestions: Optional[str] = Field(default=None, description="解决建议(逗号分隔)")
    confidence: Optional[float] = Field(default=None, description="分类置信度")
    is_auto_analyzed: bool = Field(default=True, description="是否自动分析")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class ScriptFailureStats(SQLModel, table=True):
    """脚本失败统计表"""
    __tablename__ = "script_failure_stats"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    script_id: int = Field(foreign_key="script.id", unique=True, description="脚本ID")
    total_failures: int = Field(default=0, description="总失败次数")
    failure_by_type: Optional[str] = Field(default=None, description="按类型统计(JSON)")
    most_common_failure: Optional[str] = Field(default=None, max_length=50, description="最常见失败类型")
    failure_rate: Optional[float] = Field(default=None, description="失败率")
    last_failure_time: Optional[datetime] = Field(default=None, description="最后失败时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class StepExecutionLog(SQLModel, table=True):
    """步骤执行日志表"""
    __tablename__ = "step_execution_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    task_log_id: int = Field(foreign_key="task_log.id", description="任务日志ID")
    step_index: int = Field(description="步骤索引")
    step_name: Optional[str] = Field(default=None, max_length=200, description="步骤名称")
    step_type: Optional[str] = Field(default=None, max_length=50, description="步骤类型")
    status: str = Field(max_length=20, description="状态: success/failed/skipped")
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    duration: Optional[float] = Field(default=None, description="执行时长(秒)")
    error_message: Optional[str] = Field(default=None, description="错误消息")
    screenshot_path: Optional[str] = Field(default=None, max_length=500, description="截图路径")
