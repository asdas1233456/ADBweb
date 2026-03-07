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
            # 获取所有在线设备，限制数量避免过载
            statement = select(Device).where(Device.status == 'online').limit(50)
            devices = session.exec(statement).all()
            
            if not devices:
                print(f"   没有在线设备需要采集")
                return
            
            print(f"   发现 {len(devices)} 个在线设备")
            
            alert_engine = AlertEngine(session)
            success_count = 0
            
            for device in devices:
                try:
                    # 采集设备指标 (优先使用真实数据，失败则使用模拟数据)
                    metrics = await self._collect_real_metrics(device)
                    if not metrics:
                        # 如果无法获取真实数据，使用模拟数据
                        metrics = self.health_service.generate_mock_metrics(device.id)
                    
                    # 计算健康度分数
                    health_score = self.health_service.calculate_health_score(metrics)
                    level_code, level_name, level_color = self.health_service.get_health_level(health_score)
                    
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
                    
                    # 检查告警（仅对异常情况）
                    if health_score < 60:  # 只对健康度低的设备检查告警
                        alerts = await alert_engine.check_alerts(device.id, metrics)
                        if alerts:
                            print(f"   ⚠️  设备 {device.id} 触发 {len(alerts)} 个告警")
                    
                    success_count += 1
                    
                except Exception as e:
                    print(f"   ❌ 采集设备 {device.id} 健康数据失败: {e}")
                    session.rollback()
                    continue
            
            # 批量提交
            try:
                session.commit()
                print(f"✅ 设备健康数据采集完成 (成功: {success_count}/{len(devices)})\n")
            except Exception as e:
                print(f"❌ 批量提交失败: {e}\n")
                session.rollback()
    async def _collect_real_metrics(self, device: Device) -> dict:
        """
        从真实设备采集指标数据

        Args:
            device: 设备对象

        Returns:
            指标字典，如果采集失败返回None
        """
        try:
            from app.services.adb_device_scanner import ADBDeviceScanner
            import subprocess
            import re

            scanner = ADBDeviceScanner()
            serial = device.serial_number

            # 获取电池电量
            battery_level = scanner._get_battery_level(serial)

            # 获取温度 (电池温度)
            temp_output = scanner._execute_shell_command(serial, "dumpsys battery | grep temperature")
            temperature = 0.0
            if temp_output:
                # 格式: temperature: 350 (表示35.0°C)
                match = re.search(r'temperature:\s*(\d+)', temp_output)
                if match:
                    temperature = int(match.group(1)) / 10.0

            # 获取CPU使用率 - 使用top命令
            cpu_usage = 0.0
            cpu_output = scanner._execute_shell_command(serial, "top -n 1 -b | head -5")
            if cpu_output:
                # 查找CPU行: 800%cpu   7%user   0%nice   7%sys 782%idle
                for line in cpu_output.split('\n'):
                    if 'cpu' in line.lower() and 'idle' in line.lower():
                        match = re.search(r'(\d+)%idle', line)
                        if match:
                            idle = int(match.group(1))
                            # 获取总CPU百分比（多核）
                            cpu_match = re.search(r'(\d+)%cpu', line)
                            if cpu_match:
                                total_cpu = int(cpu_match.group(1))
                                # 计算实际使用率: (总CPU - 空闲) / 总CPU * 100
                                if total_cpu > 0:
                                    cpu_usage = ((total_cpu - idle) / total_cpu) * 100
                                    # 确保在0-100范围内
                                    cpu_usage = max(0, min(100, cpu_usage))
                            else:
                                # 如果没有总CPU数据，假设单核
                                cpu_usage = max(0, min(100, 100 - idle))
                        break

            # 获取内存使用率 - 使用/proc/meminfo
            memory_usage = 0.0
            mem_output = scanner._execute_shell_command(serial, "cat /proc/meminfo | head -5")
            if mem_output:
                mem_total = 0
                mem_available = 0
                for line in mem_output.split('\n'):
                    if 'MemTotal:' in line:
                        match = re.search(r'(\d+)', line)
                        if match:
                            mem_total = int(match.group(1))
                    elif 'MemAvailable:' in line:
                        match = re.search(r'(\d+)', line)
                        if match:
                            mem_available = int(match.group(1))
                
                if mem_total > 0:
                    if mem_available > 0:
                        memory_usage = ((mem_total - mem_available) / mem_total) * 100
                    else:
                        memory_usage = 100.0
                    # 确保在0-100范围内
                    memory_usage = max(0, min(100, memory_usage))

            # 获取存储使用率 - 使用df命令
            storage_usage = 0.0
            storage_output = scanner._execute_shell_command(serial, "df /data")
            if storage_output:
                lines = storage_output.split('\n')
                if len(lines) >= 2:
                    # 第二行是数据
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        usage_str = parts[4].replace('%', '')
                        try:
                            storage_usage = float(usage_str)
                        except:
                            pass

            # 网络状态 (简单检查设备是否在线)
            network_status = 'connected' if device.status == 'online' else 'disconnected'

            return {
                'battery_level': battery_level,
                'temperature': temperature,
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'storage_usage': storage_usage,
                'network_status': network_status,
                'last_active_time': datetime.now()
            }

        except Exception as e:
            print(f"   ⚠️  采集设备 {device.id} 真实数据失败: {e}")
            return None

    
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
        
        # 延迟10秒后执行第一次采集，避免阻塞应用启动
        from datetime import timedelta
        first_run = datetime.now() + timedelta(seconds=10)
        self.scheduler.add_job(
            self.collect_device_health,
            'date',
            run_date=first_run,
            id='collect_device_health_first'
        )
        
        self.scheduler.start()
        print("✅ 健康度调度器已启动 (首次采集将在10秒后开始，之后每5分钟采集一次)")
    
    def shutdown(self):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("✅ 健康度调度器已关闭")


# 全局调度器实例
health_scheduler = HealthScheduler()
