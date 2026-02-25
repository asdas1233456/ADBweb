"""
设备健康度定时采集调度器
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import Session, select
from app.models.device import Device
from app.models.device_health import DeviceHealthRecord, DeviceUsageStats
from app.services.device_health import DeviceHealthService
from app.services.alert_engine import AlertEngine
from app.core.database import engine
from datetime import datetime


class HealthScheduler:
    """健康度调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.health_service = DeviceHealthService()
    
    async def collect_device_health(self):
        """定时采集设备健康数据"""
        print(f"\n🔍 [{datetime.now().strftime('%H:%M:%S')}] 开始采集设备健康数据...")
        
        with Session(engine) as session:
            # 获取所有在线设备
            statement = select(Device).where(Device.status == 'online')
            devices = session.exec(statement).all()
            
            print(f"   发现 {len(devices)} 个在线设备")
            
            alert_engine = AlertEngine(session)
            
            for device in devices:
                try:
                    # 采集设备指标 (使用模拟数据)
                    metrics = self.health_service.generate_mock_metrics(device.id)
                    
                    # 计算健康度分数
                    health_score = self.health_service.calculate_health_score(metrics)
                    level_code, level_name, level_color = self.health_service.get_health_level(health_score)
                    
                    print(f"   ✅ 设备 {device.id} ({device.model}): 健康度 {health_score}分 ({level_name})")
                    
                    # 更新设备信息
                    if 'battery_level' in metrics:
                        device.battery = metrics['battery_level']
                    device.cpu_usage = metrics.get('cpu_usage', device.cpu_usage)
                    device.memory_usage = metrics.get('memory_usage', device.memory_usage)
                    session.add(device)
                    
                    # 保存健康度记录
                    health_record = DeviceHealthRecord(
                        device_id=device.id,
                        health_score=health_score,
                        battery_level=metrics.get('battery_level'),
                        temperature=metrics.get('temperature'),
                        cpu_usage=metrics.get('cpu_usage'),
                        memory_usage=metrics.get('memory_usage'),
                        storage_usage=metrics.get('storage_usage'),
                        network_status=metrics.get('network_status'),
                        last_active_time=metrics.get('last_active_time')
                    )
                    session.add(health_record)
                    
                    # 检查告警
                    alerts = await alert_engine.check_alerts(device.id, metrics)
                    if alerts:
                        print(f"   ⚠️  触发 {len(alerts)} 个告警")
                    
                    session.commit()
                    
                except Exception as e:
                    print(f"   ❌ 采集设备 {device.id} 健康数据失败: {e}")
                    session.rollback()
        
        print(f"✅ 设备健康数据采集完成\n")
    
    def start(self):
        """启动调度器"""
        # 每5分钟采集一次设备健康数据
        self.scheduler.add_job(
            self.collect_device_health,
            'interval',
            minutes=5,
            id='collect_device_health',
            replace_existing=True
        )
        
        # 立即执行一次
        self.scheduler.add_job(
            self.collect_device_health,
            'date',
            run_date=datetime.now(),
            id='collect_device_health_now'
        )
        
        self.scheduler.start()
        print("✅ 健康度调度器已启动 (每5分钟采集一次)")
    
    def shutdown(self):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("✅ 健康度调度器已关闭")


# 全局调度器实例
health_scheduler = HealthScheduler()
