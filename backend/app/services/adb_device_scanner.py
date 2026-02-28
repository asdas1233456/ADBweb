"""
ADB设备扫描服务
负责扫描、检测和添加ADB设备到系统
"""
import subprocess
import re
import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlmodel import Session, select
from app.models import Device, SystemConfig

logger = logging.getLogger(__name__)


class ADBDeviceScanner:
    """ADB设备扫描器"""
    
    def __init__(self, adb_path: Optional[str] = None):
        """
        初始化扫描器
        
        Args:
            adb_path: ADB可执行文件路径，如果为None则使用系统PATH中的adb
        """
        self.adb_path = adb_path or "adb"
    
    def scan_devices(self) -> List[Dict[str, any]]:
        """
        扫描所有连接的ADB设备
        
        Returns:
            设备信息列表
        """
        try:
            # 执行 adb devices 命令
            result = subprocess.run(
                [self.adb_path, "devices", "-l"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"ADB命令执行失败: {result.stderr}")
                return []
            
            # 解析设备列表
            devices = self._parse_devices_output(result.stdout)
            
            # 获取每个设备的详细信息
            device_details = []
            for device_serial in devices:
                try:
                    details = self._get_device_details(device_serial)
                    if details:
                        device_details.append(details)
                except Exception as e:
                    logger.error(f"获取设备 {device_serial} 详情失败: {e}")
                    continue
            
            return device_details
            
        except subprocess.TimeoutExpired:
            logger.error("ADB命令执行超时")
            return []
        except FileNotFoundError:
            logger.error(f"ADB可执行文件未找到: {self.adb_path}")
            return []
        except Exception as e:
            logger.error(f"扫描设备失败: {e}")
            return []
    
    def _parse_devices_output(self, output: str) -> List[str]:
        """
        解析 adb devices 命令输出
        
        Args:
            output: adb devices 命令的输出
            
        Returns:
            设备序列号列表
        """
        devices = []
        lines = output.strip().split('\n')
        
        for line in lines[1:]:  # 跳过第一行 "List of devices attached"
            if line.strip() and '\tdevice' in line:
                # 格式: serial_number    device
                serial = line.split('\t')[0].strip()
                if serial:
                    devices.append(serial)
        
        return devices
    
    def _get_device_details(self, serial: str) -> Optional[Dict[str, any]]:
        """
        获取设备详细信息
        
        Args:
            serial: 设备序列号
            
        Returns:
            设备详细信息字典
        """
        try:
            # 获取设备型号
            model = self._execute_shell_command(serial, "getprop ro.product.model")
            
            # 获取Android版本
            android_version = self._execute_shell_command(serial, "getprop ro.build.version.release")
            
            # 获取屏幕分辨率
            resolution = self._get_screen_resolution(serial)
            
            # 获取电池电量
            battery = self._get_battery_level(serial)
            
            # 获取CPU使用率
            cpu_usage = self._get_cpu_usage(serial)
            
            # 获取内存使用率
            memory_usage = self._get_memory_usage(serial)
            
            return {
                "serial_number": serial,
                "model": model or "Unknown",
                "android_version": android_version or "Unknown",
                "resolution": resolution or "Unknown",
                "battery": battery,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "status": "online"
            }
            
        except Exception as e:
            logger.error(f"获取设备 {serial} 详情失败: {e}")
            return None
    
    def _execute_shell_command(self, serial: str, command: str) -> Optional[str]:
        """
        在设备上执行shell命令
        
        Args:
            serial: 设备序列号
            command: shell命令
            
        Returns:
            命令输出结果
        """
        try:
            result = subprocess.run(
                [self.adb_path, "-s", serial, "shell", command],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            return None
            
        except Exception as e:
            logger.error(f"执行命令失败 [{serial}] {command}: {e}")
            return None
    
    def _get_screen_resolution(self, serial: str) -> Optional[str]:
        """获取屏幕分辨率"""
        try:
            output = self._execute_shell_command(serial, "wm size")
            if output:
                # 格式: Physical size: 1080x2400
                match = re.search(r'(\d+x\d+)', output)
                if match:
                    return match.group(1)
            return None
        except Exception:
            return None
    
    def _get_battery_level(self, serial: str) -> int:
        """获取电池电量"""
        try:
            output = self._execute_shell_command(serial, "dumpsys battery | grep level")
            if output:
                # 格式: level: 85
                match = re.search(r'level:\s*(\d+)', output)
                if match:
                    return int(match.group(1))
            return 0
        except Exception:
            return 0
    
    def _get_cpu_usage(self, serial: str) -> float:
        """获取CPU使用率"""
        try:
            output = self._execute_shell_command(serial, "top -n 1 | grep 'CPU:'")
            if output:
                # 尝试解析CPU使用率
                match = re.search(r'(\d+)%', output)
                if match:
                    return float(match.group(1))
            return 0.0
        except Exception:
            return 0.0
    
    def _get_memory_usage(self, serial: str) -> float:
        """获取内存使用率"""
        try:
            output = self._execute_shell_command(serial, "dumpsys meminfo | grep 'Total RAM'")
            if output:
                # 解析内存信息
                # 这是一个简化版本，实际可能需要更复杂的解析
                return 0.0
            return 0.0
        except Exception:
            return 0.0


def scan_and_add_devices(db: Session, adb_path: Optional[str] = None) -> Dict[str, int]:
    """
    扫描ADB设备并添加到数据库
    
    Args:
        db: 数据库会话
        adb_path: ADB可执行文件路径
        
    Returns:
        统计信息: {"new_devices": 新增设备数, "updated_devices": 更新设备数}
    """
    # 如果没有指定ADB路径，尝试从系统配置中获取
    if not adb_path:
        config = db.exec(
            select(SystemConfig).where(SystemConfig.config_key == "adb_path")
        ).first()
        if config:
            adb_path = config.config_value
    
    # 创建扫描器
    scanner = ADBDeviceScanner(adb_path)
    
    # 扫描设备
    scanned_devices = scanner.scan_devices()
    
    logger.info(f"扫描到 {len(scanned_devices)} 台设备")
    
    new_count = 0
    updated_count = 0
    
    for device_info in scanned_devices:
        try:
            # 检查设备是否已存在
            existing_device = db.exec(
                select(Device).where(Device.serial_number == device_info["serial_number"])
            ).first()
            
            if existing_device:
                # 更新现有设备
                existing_device.model = device_info["model"]
                existing_device.android_version = device_info["android_version"]
                existing_device.resolution = device_info["resolution"]
                existing_device.battery = device_info["battery"]
                existing_device.cpu_usage = device_info.get("cpu_usage", 0.0)
                existing_device.memory_usage = device_info.get("memory_usage", 0.0)
                existing_device.status = "online"
                existing_device.updated_at = datetime.now()
                
                db.add(existing_device)
                updated_count += 1
                
                logger.info(f"更新设备: {device_info['model']} ({device_info['serial_number']})")
            else:
                # 添加新设备
                new_device = Device(
                    serial_number=device_info["serial_number"],
                    model=device_info["model"],
                    android_version=device_info["android_version"],
                    resolution=device_info["resolution"],
                    battery=device_info["battery"],
                    cpu_usage=device_info.get("cpu_usage", 0.0),
                    memory_usage=device_info.get("memory_usage", 0.0),
                    status="online"
                )
                
                db.add(new_device)
                new_count += 1
                
                logger.info(f"添加新设备: {device_info['model']} ({device_info['serial_number']})")
        
        except Exception as e:
            logger.error(f"处理设备失败: {e}")
            continue
    
    # 提交所有更改
    try:
        db.commit()
        logger.info(f"设备扫描完成: 新增 {new_count} 台, 更新 {updated_count} 台")
    except Exception as e:
        db.rollback()
        logger.error(f"提交数据库更改失败: {e}")
        raise
    
    return {
        "new_devices": new_count,
        "updated_devices": updated_count
    }
