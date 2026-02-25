"""
设备健康度算法集成示例
展示如何在 ADBweb 系统中集成新的健康度评分算法
"""

from datetime import datetime, timedelta
from typing import Dict, List
from sqlmodel import Session, select
from device_health_v2 import DeviceHealthScorer
from app.models.device import Device
from app.models.device_health import DeviceHealthRecord


class HealthMonitorService:
    """健康度监控服务 - 集成示例"""
    
    def __init__(self, session: Session):
        self.session = session
        self.scorer = DeviceHealthScorer()
    
    def collect_and_score_device(self, device: Device) -> Dict:
        """
        采集设备指标并计算健康度
        
        Args:
            device: 设备对象
            
        Returns:
            评分结果字典
        """
        # 1. 采集设备指标（这里使用模拟数据，实际应该调用ADB命令）
        metrics = self._collect_device_metrics(device)
        
        # 2. 计算健康度
        result = self.scorer.calculate_score(metrics)
        
        # 3. 保存健康度记录
        self._save_health_record(device.id, result)
        
        # 4. 更新设备信息
        self._update_device_info(device, result)
        
        return result
    
    def _collect_device_metrics(self, device: Device) -> Dict:
        """
        采集设备指标
        
        实际使用时应该调用真实的ADB命令:
        - adb shell dumpsys battery (电量和温度)
        - adb shell top -n 1 (CPU使用率)
        - adb shell cat /proc/meminfo (内存使用率)
        - adb shell df /data (存储使用率)
        - adb shell ping -c 1 8.8.8.8 (网络状态)
        """
        import random
        
        # 模拟数据（实际应该从ADB获取）
        return {
            'battery_level': f"{random.randint(20, 100)}%",
            'temperature': f"{random.uniform(30, 45):.1f}℃",
            'cpu_usage': f"{random.uniform(10, 80):.1f}%",
            'memory_usage': random.uniform(30, 85),
            'storage_usage': random.uniform(40, 90),
            'network_status': random.choice(['connected', 'connected', 'disconnected']),
            'last_active_time': datetime.now() - timedelta(hours=random.randint(0, 48))
        }
    
    def _save_health_record(self, device_id: int, result: Dict) -> None:
        """保存健康度记录到数据库"""
        metrics = result['metrics']
        
        record = DeviceHealthRecord(
            device_id=device_id,
            health_score=int(result['total_score']),
            battery_level=int(metrics['battery_level']),
            temperature=metrics['temperature'],
            cpu_usage=metrics['cpu_usage'],
            memory_usage=metrics['memory_usage'],
            storage_usage=metrics['storage_usage'],
            network_status=metrics['network_status'],
            last_active_time=metrics['last_active_time']
        )
        
        self.session.add(record)
        self.session.commit()
    
    def _update_device_info(self, device: Device, result: Dict) -> None:
        """更新设备信息"""
        metrics = result['metrics']
        
        device.battery = int(metrics['battery_level'])
        device.cpu_usage = metrics['cpu_usage']
        device.memory_usage = metrics['memory_usage']
        
        self.session.add(device)
        self.session.commit()
    
    def batch_monitor_devices(self, status: str = 'online') -> List[Dict]:
        """
        批量监控设备
        
        Args:
            status: 设备状态筛选
            
        Returns:
            评分结果列表
        """
        # 获取所有在线设备
        statement = select(Device).where(Device.status == status)
        devices = self.session.exec(statement).all()
        
        results = []
        for device in devices:
            try:
                result = self.collect_and_score_device(device)
                result['device_id'] = device.id
                result['device_model'] = device.model
                results.append(result)
                
                print(f"✅ 设备 {device.model} (ID:{device.id}): "
                      f"{result['total_score']:.1f}分 - {result['level_name']}")
                
            except Exception as e:
                print(f"❌ 监控设备 {device.id} 失败: {e}")
        
        return results
    
    def get_health_trend(self, device_id: int, days: int = 7) -> Dict:
        """
        获取设备健康度趋势
        
        Args:
            device_id: 设备ID
            days: 天数
            
        Returns:
            趋势数据
        """
        start_date = datetime.now() - timedelta(days=days)
        
        statement = select(DeviceHealthRecord).where(
            DeviceHealthRecord.device_id == device_id,
            DeviceHealthRecord.created_at >= start_date
        ).order_by(DeviceHealthRecord.created_at)
        
        records = self.session.exec(statement).all()
        
        return {
            'device_id': device_id,
            'period': f'{days}天',
            'data_points': len(records),
            'scores': [r.health_score for r in records],
            'timestamps': [r.created_at.isoformat() for r in records],
            'avg_score': sum(r.health_score for r in records) / len(records) if records else 0,
            'min_score': min(r.health_score for r in records) if records else 0,
            'max_score': max(r.health_score for r in records) if records else 0,
        }
    
    def get_low_health_devices(self, threshold: int = 60) -> List[Dict]:
        """
        获取健康度低于阈值的设备
        
        Args:
            threshold: 健康度阈值
            
        Returns:
            设备列表
        """
        # 获取每个设备的最新健康度记录
        from sqlalchemy import func
        
        subquery = (
            select(
                DeviceHealthRecord.device_id,
                func.max(DeviceHealthRecord.created_at).label('max_time')
            )
            .group_by(DeviceHealthRecord.device_id)
            .subquery()
        )
        
        statement = (
            select(DeviceHealthRecord, Device)
            .join(Device, DeviceHealthRecord.device_id == Device.id)
            .join(
                subquery,
                (DeviceHealthRecord.device_id == subquery.c.device_id) &
                (DeviceHealthRecord.created_at == subquery.c.max_time)
            )
            .where(DeviceHealthRecord.health_score < threshold)
        )
        
        results = self.session.exec(statement).all()
        
        low_health_devices = []
        for record, device in results:
            low_health_devices.append({
                'device_id': device.id,
                'device_model': device.model,
                'health_score': record.health_score,
                'battery': record.battery_level,
                'temperature': record.temperature,
                'last_check': record.created_at.isoformat(),
            })
        
        return low_health_devices


# ============================================================================
# 使用示例
# ============================================================================

def example_usage():
    """使用示例"""
    from app.core.database import engine
    
    print("=" * 80)
    print("设备健康度监控服务集成示例")
    print("=" * 80)
    
    with Session(engine) as session:
        service = HealthMonitorService(session)
        
        # 示例1: 监控单个设备
        print("\n【示例1】监控单个设备")
        print("-" * 80)
        device = session.exec(select(Device).limit(1)).first()
        if device:
            result = service.collect_and_score_device(device)
            print(f"设备: {device.model}")
            print(f"健康度: {result['total_score']:.1f}分 - {result['level_name']}")
            print(f"建议: {', '.join(result['recommendations'])}")
        
        # 示例2: 批量监控所有在线设备
        print("\n【示例2】批量监控在线设备")
        print("-" * 80)
        results = service.batch_monitor_devices('online')
        print(f"共监控 {len(results)} 个设备")
        
        # 示例3: 获取健康度趋势
        print("\n【示例3】获取健康度趋势")
        print("-" * 80)
        if device:
            trend = service.get_health_trend(device.id, days=7)
            print(f"设备ID: {trend['device_id']}")
            print(f"数据点: {trend['data_points']}")
            print(f"平均分: {trend['avg_score']:.1f}")
            print(f"最低分: {trend['min_score']}")
            print(f"最高分: {trend['max_score']}")
        
        # 示例4: 获取低健康度设备
        print("\n【示例4】获取低健康度设备")
        print("-" * 80)
        low_devices = service.get_low_health_devices(threshold=60)
        print(f"健康度低于60分的设备: {len(low_devices)}个")
        for dev in low_devices:
            print(f"  - {dev['device_model']}: {dev['health_score']}分")


# ============================================================================
# API 集成示例
# ============================================================================

def api_integration_example():
    """API 集成示例"""
    from fastapi import APIRouter, Depends
    from sqlmodel import Session
    from app.core.database import get_session
    
    router = APIRouter(prefix="/api/v1/health", tags=["设备健康度"])
    
    @router.get("/devices/{device_id}/score")
    async def get_device_health_score(
        device_id: int,
        db: Session = Depends(get_session)
    ):
        """获取设备健康度评分"""
        service = HealthMonitorService(db)
        device = db.get(Device, device_id)
        
        if not device:
            return {"error": "设备不存在"}
        
        result = service.collect_and_score_device(device)
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "device_id": device.id,
                "device_model": device.model,
                "health_score": result['total_score'],
                "level": result['level'],
                "level_name": result['level_name'],
                "dimension_scores": result['dimension_scores'],
                "recommendations": result['recommendations'],
            }
        }
    
    @router.get("/devices/low-health")
    async def get_low_health_devices(
        threshold: int = 60,
        db: Session = Depends(get_session)
    ):
        """获取低健康度设备列表"""
        service = HealthMonitorService(db)
        devices = service.get_low_health_devices(threshold)
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "threshold": threshold,
                "count": len(devices),
                "devices": devices
            }
        }
    
    @router.get("/devices/{device_id}/trend")
    async def get_device_health_trend(
        device_id: int,
        days: int = 7,
        db: Session = Depends(get_session)
    ):
        """获取设备健康度趋势"""
        service = HealthMonitorService(db)
        trend = service.get_health_trend(device_id, days)
        
        return {
            "code": 200,
            "message": "success",
            "data": trend
        }


if __name__ == "__main__":
    # 运行示例
    example_usage()
