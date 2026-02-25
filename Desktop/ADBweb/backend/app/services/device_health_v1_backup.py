"""
设备健康度服务
"""
from datetime import datetime, timedelta
from typing import Dict, Tuple
import subprocess
import re


class DeviceHealthService:
    """设备健康度服务"""
    
    # 健康度权重配置
    WEIGHTS = {
        'battery': 0.25,      # 电量权重 25%
        'temperature': 0.20,  # 温度权重 20%
        'cpu': 0.15,          # CPU权重 15%
        'memory': 0.15,       # 内存权重 15%
        'storage': 0.10,      # 存储权重 10%
        'network': 0.10,      # 网络权重 10%
        'activity': 0.05,     # 活跃度权重 5%
    }
    
    def calculate_health_score(self, device_data: Dict) -> int:
        """
        计算设备健康度分数 (0-100)
        
        Args:
            device_data: 设备数据字典
            
        Returns:
            健康度分数 0-100
        """
        scores = {}
        
        # 1. 电量评分 (0-100)
        battery = device_data.get('battery_level', 0)
        if battery >= 80:
            scores['battery'] = 100
        elif battery >= 50:
            scores['battery'] = 80
        elif battery >= 20:
            scores['battery'] = 50
        else:
            scores['battery'] = 20
        
        # 2. 温度评分 (0-100)
        temp = device_data.get('temperature', 30)
        if temp <= 35:
            scores['temperature'] = 100
        elif temp <= 40:
            scores['temperature'] = 80
        elif temp <= 45:
            scores['temperature'] = 50
        else:
            scores['temperature'] = 20
        
        # 3. CPU 使用率评分 (0-100)
        cpu = device_data.get('cpu_usage', 0)
        scores['cpu'] = max(0, 100 - cpu)
        
        # 4. 内存使用率评分 (0-100)
        memory = device_data.get('memory_usage', 0)
        scores['memory'] = max(0, 100 - memory)
        
        # 5. 存储使用率评分 (0-100)
        storage = device_data.get('storage_usage', 0)
        scores['storage'] = max(0, 100 - storage)
        
        # 6. 网络状态评分 (0-100)
        network = device_data.get('network_status', 'unknown')
        scores['network'] = 100 if network == 'connected' else 0
        
        # 7. 活跃度评分 (0-100)
        last_active = device_data.get('last_active_time')
        if last_active:
            if isinstance(last_active, str):
                try:
                    last_active = datetime.fromisoformat(last_active)
                except:
                    last_active = None
            
            if last_active:
                hours_inactive = (datetime.now() - last_active).total_seconds() / 3600
                if hours_inactive < 1:
                    scores['activity'] = 100
                elif hours_inactive < 24:
                    scores['activity'] = 80
                elif hours_inactive < 72:
                    scores['activity'] = 50
                else:
                    scores['activity'] = 20
            else:
                scores['activity'] = 0
        else:
            scores['activity'] = 50  # 默认中等分数
        
        # 加权计算总分
        total_score = sum(
            scores.get(key, 0) * weight 
            for key, weight in self.WEIGHTS.items()
        )
        
        return int(total_score)
    
    def get_health_level(self, score: int) -> Tuple[str, str, str]:
        """
        根据分数获取健康等级
        
        Returns:
            (等级代码, 等级名称, 颜色)
        """
        if score >= 90:
            return ('excellent', '优秀', 'green')
        elif score >= 75:
            return ('good', '良好', 'blue')
        elif score >= 60:
            return ('fair', '一般', 'orange')
        elif score >= 40:
            return ('poor', '较差', 'red')
        else:
            return ('critical', '危险', 'red')
    
    async def collect_device_metrics(self, device_serial: str) -> Dict:
        """
        采集设备性能指标
        
        Args:
            device_serial: 设备序列号
            
        Returns:
            设备指标字典
        """
        metrics = {}
        
        try:
            # 1. 获取电量和温度
            result = subprocess.run(
                ["adb", "-s", device_serial, "shell", "dumpsys", "battery"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split('\n'):
                if 'level:' in line:
                    metrics['battery_level'] = int(line.split(':')[1].strip())
                elif 'temperature:' in line:
                    # 温度通常是摄氏度 * 10
                    temp_raw = int(line.split(':')[1].strip())
                    metrics['temperature'] = temp_raw / 10
            
            # 2. 获取 CPU 使用率 (简化版)
            result = subprocess.run(
                ["adb", "-s", device_serial, "shell", "top", "-n", "1"],
                capture_output=True, text=True, timeout=5
            )
            # 解析 CPU 使用率
            for line in result.stdout.split('\n'):
                if 'CPU:' in line or '%cpu' in line.lower():
                    # 尝试提取数字
                    numbers = re.findall(r'\d+\.?\d*', line)
                    if numbers:
                        metrics['cpu_usage'] = float(numbers[0])
                    break
            
            # 3. 获取内存使用率
            result = subprocess.run(
                ["adb", "-s", device_serial, "shell", "cat", "/proc/meminfo"],
                capture_output=True, text=True, timeout=5
            )
            mem_total = 0
            mem_available = 0
            for line in result.stdout.split('\n'):
                if 'MemTotal:' in line:
                    mem_total = int(line.split()[1])
                elif 'MemAvailable:' in line:
                    mem_available = int(line.split()[1])
            
            if mem_total > 0:
                metrics['memory_usage'] = ((mem_total - mem_available) / mem_total) * 100
            
            # 4. 获取存储使用率
            result = subprocess.run(
                ["adb", "-s", device_serial, "shell", "df", "/data"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    usage_str = parts[4].replace('%', '')
                    metrics['storage_usage'] = float(usage_str)
            
            # 5. 检查网络状态
            result = subprocess.run(
                ["adb", "-s", device_serial, "shell", "ping", "-c", "1", "-W", "2", "8.8.8.8"],
                capture_output=True, text=True, timeout=5
            )
            metrics['network_status'] = 'connected' if result.returncode == 0 else 'disconnected'
            
        except subprocess.TimeoutExpired:
            print(f"⚠️ 采集设备 {device_serial} 指标超时")
        except Exception as e:
            print(f"⚠️ 采集设备 {device_serial} 指标失败: {e}")
        
        return metrics
    
    def generate_mock_metrics(self, device_id: int) -> Dict:
        """
        生成模拟指标数据(用于测试)
        
        Args:
            device_id: 设备ID
            
        Returns:
            模拟指标字典
        """
        import random
        
        return {
            'battery_level': random.randint(20, 100),
            'temperature': random.uniform(30, 45),
            'cpu_usage': random.uniform(10, 80),
            'memory_usage': random.uniform(30, 85),
            'storage_usage': random.uniform(40, 90),
            'network_status': random.choice(['connected', 'connected', 'disconnected']),
            'last_active_time': datetime.now() - timedelta(hours=random.randint(0, 48))
        }
