"""
告警规则引擎
"""
from typing import List, Dict
from sqlmodel import Session, select
from app.models.device_health import DeviceAlert, AlertRule
from app.core.websocket_manager import manager
from datetime import datetime
import json
from app.utils.time_utils import now_local


class AlertEngine:
    """告警引擎"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def check_alerts(self, device_id: int, metrics: Dict) -> List[DeviceAlert]:
        """
        检查设备指标是否触发告警
        
        Args:
            device_id: 设备ID
            metrics: 设备指标
            
        Returns:
            触发的告警列表
        """
        # 获取所有启用的告警规则
        statement = select(AlertRule).where(AlertRule.is_enabled == True)
        rules = self.session.exec(statement).all()
        
        triggered_alerts = []
        
        for rule in rules:
            if self._evaluate_rule(rule, metrics):
                alert = await self._create_alert(device_id, rule, metrics)
                if alert:
                    triggered_alerts.append(alert)
        
        return triggered_alerts
    
    def _evaluate_rule(self, rule: AlertRule, metrics: Dict) -> bool:
        """
        评估规则是否触发
        
        Args:
            rule: 告警规则
            metrics: 设备指标
            
        Returns:
            是否触发
        """
        field_value = metrics.get(rule.condition_field)
        if field_value is None:
            return False
        
        threshold = rule.threshold_value
        operator = rule.operator
        
        try:
            if operator == '<':
                return float(field_value) < threshold
            elif operator == '>':
                return float(field_value) > threshold
            elif operator == '<=':
                return float(field_value) <= threshold
            elif operator == '>=':
                return float(field_value) >= threshold
            elif operator == '==':
                return str(field_value) == str(threshold)
        except (ValueError, TypeError):
            return False
        
        return False
    
    async def _create_alert(
        self, 
        device_id: int, 
        rule: AlertRule, 
        metrics: Dict
    ) -> DeviceAlert:
        """
        创建告警记录
        
        Args:
            device_id: 设备ID
            rule: 告警规则
            metrics: 设备指标
            
        Returns:
            告警记录
        """
        # 检查是否已存在未解决的相同告警
        statement = select(DeviceAlert).where(
            DeviceAlert.device_id == device_id,
            DeviceAlert.alert_type == rule.rule_type,
            DeviceAlert.is_resolved == False
        )
        existing_alert = self.session.exec(statement).first()
        
        if existing_alert:
            # 已存在未解决的告警，不重复创建
            return None
        
        # 创建新告警
        alert = DeviceAlert(
            device_id=device_id,
            alert_type=rule.rule_type,
            severity=rule.severity,
            message=self._generate_alert_message(rule, metrics),
            is_resolved=False
        )
        
        self.session.add(alert)
        self.session.commit()
        self.session.refresh(alert)
        
        # 发送通知
        await self._send_notifications(alert, rule, device_id)
        
        return alert
    
    def _generate_alert_message(self, rule: AlertRule, metrics: Dict) -> str:
        """
        生成告警消息
        
        Args:
            rule: 告警规则
            metrics: 设备指标
            
        Returns:
            告警消息
        """
        field_value = metrics.get(rule.condition_field)
        
        messages = {
            'low_battery': f'设备电量过低: {field_value}%',
            'high_temp': f'设备温度过高: {field_value}°C',
            'high_cpu': f'CPU使用率过高: {field_value}%',
            'high_memory': f'内存使用率过高: {field_value}%',
            'storage_full': f'存储空间不足: 已使用{field_value}%',
            'offline': '设备离线',
            'network_error': '网络连接异常',
        }
        
        return messages.get(
            rule.rule_type, 
            f'{rule.rule_name}: {field_value} {rule.operator} {rule.threshold_value}'
        )
    
    async def _send_notifications(
        self, 
        alert: DeviceAlert, 
        rule: AlertRule,
        device_id: int
    ):
        """
        发送告警通知
        
        Args:
            alert: 告警记录
            rule: 告警规则
            device_id: 设备ID
        """
        channels = []
        if rule.notification_channels:
            try:
                channels = json.loads(rule.notification_channels)
            except:
                channels = []
        
        # WebSocket 推送
        if 'websocket' in channels or not channels:  # 默认使用websocket
            await manager.broadcast(json.dumps({
                'type': 'device_alert',
                'data': {
                    'alert_id': alert.id,
                    'device_id': device_id,
                    'alert_type': alert.alert_type,
                    'severity': alert.severity,
                    'message': alert.message,
                    'created_at': alert.created_at.isoformat()
                }
            }))
            print(f"📢 告警通知已发送: {alert.message}")
        
        # 邮件通知
        if 'email' in channels:
            # TODO: 实现邮件发送
            print(f"📧 邮件通知: {alert.message}")
        
        # 短信通知
        if 'sms' in channels:
            # TODO: 实现短信发送
            print(f"📱 短信通知: {alert.message}")
    
    def resolve_alert(self, alert_id: int) -> bool:
        """
        解决告警
        
        Args:
            alert_id: 告警ID
            
        Returns:
            是否成功
        """
        alert = self.session.get(DeviceAlert, alert_id)
        if alert and not alert.is_resolved:
            alert.is_resolved = True
            alert.resolved_at = now_local()
            self.session.add(alert)
            self.session.commit()
            return True
        return False
