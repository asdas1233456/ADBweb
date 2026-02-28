"""
设备健康度相关模型
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class DeviceHealthRecord(SQLModel, table=True):
    """设备健康度记录表"""
    __tablename__ = "device_health_records"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: int = Field(foreign_key="device.id", description="设备ID")
    health_score: int = Field(description="健康度分数 0-100")
    battery_level: Optional[int] = Field(default=None, description="电量百分比")
    temperature: Optional[float] = Field(default=None, description="温度(摄氏度)")
    cpu_usage: Optional[float] = Field(default=None, description="CPU使用率")
    memory_usage: Optional[float] = Field(default=None, description="内存使用率")
    storage_usage: Optional[float] = Field(default=None, description="存储使用率")
    network_status: Optional[str] = Field(default=None, description="网络状态")
    last_active_time: Optional[datetime] = Field(default=None, description="最后活跃时间")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class DeviceUsageStats(SQLModel, table=True):
    """设备使用统计表"""
    __tablename__ = "device_usage_stats"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: int = Field(foreign_key="device.id", unique=True, description="设备ID")
    total_executions: int = Field(default=0, description="总执行次数")
    success_executions: int = Field(default=0, description="成功执行次数")
    failed_executions: int = Field(default=0, description="失败执行次数")
    total_duration: int = Field(default=0, description="总执行时长(秒)")
    avg_duration: Optional[float] = Field(default=None, description="平均执行时长")
    success_rate: Optional[float] = Field(default=None, description="成功率")
    last_execution_time: Optional[datetime] = Field(default=None, description="最后执行时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class DeviceAlert(SQLModel, table=True):
    """设备告警记录表"""
    __tablename__ = "device_alerts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: int = Field(foreign_key="device.id", description="设备ID")
    alert_type: str = Field(max_length=50, description="告警类型")
    severity: str = Field(max_length=20, description="严重程度: critical/warning/info")
    message: str = Field(description="告警消息")
    is_resolved: bool = Field(default=False, description="是否已解决")
    resolved_at: Optional[datetime] = Field(default=None, description="解决时间")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class AlertRule(SQLModel, table=True):
    """告警规则配置表"""
    __tablename__ = "alert_rules"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    rule_name: str = Field(max_length=100, description="规则名称")
    rule_type: str = Field(max_length=50, description="规则类型")
    condition_field: str = Field(max_length=50, description="条件字段")
    operator: str = Field(max_length=10, description="操作符: <, >, <=, >=, ==")
    threshold_value: float = Field(description="阈值")
    severity: str = Field(max_length=20, description="严重程度")
    is_enabled: bool = Field(default=True, description="是否启用")
    notification_channels: Optional[str] = Field(default=None, description="通知渠道(JSON)")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
