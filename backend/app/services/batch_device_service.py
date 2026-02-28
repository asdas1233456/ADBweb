"""
批量设备操作服务
支持批量安装/卸载应用、推送文件、执行命令等
"""
from sqlmodel import Session, select
from app.models import Device
from typing import List, Dict, Optional
import subprocess
import asyncio
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class BatchDeviceService:
    """批量设备操作服务"""
    
    def __init__(self, session: Session, max_workers: int = 5):
        """
        初始化批量设备服务
        
        Args:
            session: 数据库会话
            max_workers: 最大并发数
        """
        self.session = session
        self.max_workers = max_workers
    
    async def batch_install_app(
        self, 
        device_ids: List[int], 
        apk_path: str
    ) -> Dict:
        """
        批量安装应用
        
        Args:
            device_ids: 设备ID列表
            apk_path: APK文件路径
            
        Returns:
            操作结果字典
        """
        devices = self._get_devices(device_ids)
        results = {
            'total': len(devices),
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._install_app_single, device, apk_path): device
                for device in devices
            }
            
            for future in as_completed(futures):
                device = futures[future]
                try:
                    result = future.result()
                    if result['success']:
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                    results['details'].append(result)
                except Exception as e:
                    logger.error(f"设备 {device.serial_number} 安装失败: {e}")
                    results['failed'] += 1
                    results['details'].append({
                        'device_id': device.id,
                        'device_name': device.model,
                        'success': False,
                        'message': str(e)
                    })
        
        logger.info(f"批量安装完成: 成功 {results['success']}/{results['total']}")
        return results
    
    def _install_app_single(self, device: Device, apk_path: str) -> Dict:
        """单个设备安装应用"""
        try:
            result = subprocess.run(
                ['adb', '-s', device.serial_number, 'install', '-r', apk_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            success = result.returncode == 0 and 'Success' in result.stdout
            
            return {
                'device_id': device.id,
                'device_name': device.model,
                'serial_number': device.serial_number,
                'success': success,
                'message': result.stdout if success else result.stderr,
                'timestamp': datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                'device_id': device.id,
                'device_name': device.model,
                'serial_number': device.serial_number,
                'success': False,
                'message': '安装超时',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'device_id': device.id,
                'device_name': device.model,
                'serial_number': device.serial_number,
                'success': False,
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def batch_uninstall_app(
        self, 
        device_ids: List[int], 
        package_name: str
    ) -> Dict:
        """
        批量卸载应用
        
        Args:
            device_ids: 设备ID列表
            package_name: 应用包名
            
        Returns:
            操作结果字典
        """
        devices = self._get_devices(device_ids)
        results = {
            'total': len(devices),
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._uninstall_app_single, device, package_name): device
                for device in devices
            }
            
            for future in as_completed(futures):
                device = futures[future]
                try:
                    result = future.result()
                    if result['success']:
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                    results['details'].append(result)
                except Exception as e:
                    logger.error(f"设备 {device.serial_number} 卸载失败: {e}")
                    results['failed'] += 1
                    results['details'].append({
                        'device_id': device.id,
                        'device_name': device.model,
                        'success': False,
                        'message': str(e)
                    })
        
        logger.info(f"批量卸载完成: 成功 {results['success']}/{results['total']}")
        return results
    
    def _uninstall_app_single(self, device: Device, package_name: str) -> Dict:
        """单个设备卸载应用"""
        try:
            result = subprocess.run(
                ['adb', '-s', device.serial_number, 'uninstall', package_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0 and 'Success' in result.stdout
            
            return {
                'device_id': device.id,
                'device_name': device.model,
                'serial_number': device.serial_number,
                'success': success,
                'message': result.stdout if success else result.stderr,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'device_id': device.id,
                'device_name': device.model,
                'serial_number': device.serial_number,
                'success': False,
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def batch_push_file(
        self, 
        device_ids: List[int], 
        local_path: str,
        remote_path: str
    ) -> Dict:
        """
        批量推送文件
        
        Args:
            device_ids: 设备ID列表
            local_path: 本地文件路径
            remote_path: 设备目标路径
            
        Returns:
            操作结果字典
        """
        devices = self._get_devices(device_ids)
        results = {
            'total': len(devices),
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._push_file_single, device, local_path, remote_path): device
                for device in devices
            }
            
            for future in as_completed(futures):
                device = futures[future]
                try:
                    result = future.result()
                    if result['success']:
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                    results['details'].append(result)
                except Exception as e:
                    logger.error(f"设备 {device.serial_number} 推送文件失败: {e}")
                    results['failed'] += 1
        
        logger.info(f"批量推送文件完成: 成功 {results['success']}/{results['total']}")
        return results
    
    def _push_file_single(self, device: Device, local_path: str, remote_path: str) -> Dict:
        """单个设备推送文件"""
        try:
            result = subprocess.run(
                ['adb', '-s', device.serial_number, 'push', local_path, remote_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            success = result.returncode == 0
            
            return {
                'device_id': device.id,
                'device_name': device.model,
                'serial_number': device.serial_number,
                'success': success,
                'message': result.stdout if success else result.stderr,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'device_id': device.id,
                'device_name': device.model,
                'serial_number': device.serial_number,
                'success': False,
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def batch_execute_command(
        self, 
        device_ids: List[int], 
        command: str
    ) -> Dict:
        """
        批量执行Shell命令
        
        Args:
            device_ids: 设备ID列表
            command: Shell命令
            
        Returns:
            操作结果字典
        """
        devices = self._get_devices(device_ids)
        results = {
            'total': len(devices),
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._execute_command_single, device, command): device
                for device in devices
            }
            
            for future in as_completed(futures):
                device = futures[future]
                try:
                    result = future.result()
                    if result['success']:
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                    results['details'].append(result)
                except Exception as e:
                    logger.error(f"设备 {device.serial_number} 执行命令失败: {e}")
                    results['failed'] += 1
        
        logger.info(f"批量执行命令完成: 成功 {results['success']}/{results['total']}")
        return results
    
    def _execute_command_single(self, device: Device, command: str) -> Dict:
        """单个设备执行命令"""
        try:
            result = subprocess.run(
                ['adb', '-s', device.serial_number, 'shell', command],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            
            return {
                'device_id': device.id,
                'device_name': device.model,
                'serial_number': device.serial_number,
                'success': success,
                'output': result.stdout,
                'error': result.stderr,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'device_id': device.id,
                'device_name': device.model,
                'serial_number': device.serial_number,
                'success': False,
                'output': '',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def batch_reboot(self, device_ids: List[int]) -> Dict:
        """批量重启设备"""
        return await self.batch_execute_command(device_ids, 'reboot')
    
    async def batch_clear_cache(self, device_ids: List[int], package_name: str) -> Dict:
        """批量清除应用缓存"""
        command = f'pm clear {package_name}'
        return await self.batch_execute_command(device_ids, command)
    
    def _get_devices(self, device_ids: List[int]) -> List[Device]:
        """获取设备列表"""
        statement = select(Device).where(Device.id.in_(device_ids))
        devices = self.session.exec(statement).all()
        
        if len(devices) != len(device_ids):
            found_ids = {d.id for d in devices}
            missing_ids = set(device_ids) - found_ids
            logger.warning(f"部分设备不存在: {missing_ids}")
        
        return devices
