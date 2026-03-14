"""
设备健康度评分算法 V2.0 - 优化版
Android 自动化测试平台 (ADBweb)

功能特性:
1. 7维度评分: 电量、温度、CPU、内存、存储、网络、活跃度
2. 支持固定权重和动态权重
3. 线性插值评分，更精确
4. 兼容真实ADB数据格式
5. 完整的参数校验和异常处理
6. 详细的日志和调试信息
"""

from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List
import re
import logging
from app.utils.time_utils import now_local

logger = logging.getLogger(__name__)


class DeviceHealthScorer:
    """设备健康度评分器"""
    
    # 默认权重配置 (总和必须为1.0)
    DEFAULT_WEIGHTS = {
        'battery': 0.25,      # 电量权重 25%
        'temperature': 0.20,  # 温度权重 20%
        'cpu': 0.15,          # CPU权重 15%
        'memory': 0.15,       # 内存权重 15%
        'storage': 0.10,      # 存储权重 10%
        'network': 0.10,      # 网络权重 10%
        'activity': 0.05,     # 活跃度权重 5%
    }
    
    # 评分阈值配置
    THRESHOLDS = {
        'battery': {
            'excellent': 80,  # ≥80% 优秀
            'good': 50,       # ≥50% 良好
            'fair': 20,       # ≥20% 一般
            'poor': 10,       # ≥10% 较差
        },
        'temperature': {
            'excellent': 35,  # ≤35℃ 优秀
            'good': 40,       # ≤40℃ 良好
            'fair': 45,       # ≤45℃ 一般
            'poor': 50,       # ≤50℃ 较差
        },
        'cpu': {
            'excellent': 30,  # ≤30% 优秀
            'good': 50,       # ≤50% 良好
            'fair': 70,       # ≤70% 一般
            'poor': 85,       # ≤85% 较差
        },
        'memory': {
            'excellent': 50,  # ≤50% 优秀
            'good': 70,       # ≤70% 良好
            'fair': 85,       # ≤85% 一般
            'poor': 95,       # ≤95% 较差
        },
        'storage': {
            'excellent': 70,  # ≤70% 优秀
            'good': 85,       # ≤85% 良好
            'fair': 95,       # ≤95% 一般
            'poor': 98,       # ≤98% 较差
        },
    }
    
    def __init__(self, custom_weights: Optional[Dict[str, float]] = None):
        """
        初始化评分器
        
        Args:
            custom_weights: 自定义权重配置，如果为None则使用默认权重
        """
        if custom_weights:
            self._validate_weights(custom_weights)
            self.weights = custom_weights
        else:
            self.weights = self.DEFAULT_WEIGHTS.copy()
        
        logger.info(f"设备健康度评分器已初始化，权重配置: {self.weights}")
    
    def _validate_weights(self, weights: Dict[str, float]) -> None:
        """
        验证权重配置
        
        Args:
            weights: 权重字典
            
        Raises:
            ValueError: 权重配置无效
        """
        # 检查必需的维度
        required_dims = set(self.DEFAULT_WEIGHTS.keys())
        provided_dims = set(weights.keys())
        
        if required_dims != provided_dims:
            missing = required_dims - provided_dims
            extra = provided_dims - required_dims
            raise ValueError(
                f"权重配置无效: 缺少维度 {missing}, 多余维度 {extra}"
            )
        
        # 检查权重总和
        total = sum(weights.values())
        if not (0.99 <= total <= 1.01):  # 允许浮点误差
            raise ValueError(f"权重总和必须为1.0，当前为 {total}")
        
        # 检查权重范围
        for dim, weight in weights.items():
            if not (0 <= weight <= 1):
                raise ValueError(f"维度 {dim} 的权重 {weight} 超出范围 [0, 1]")
    
    def parse_metrics(self, raw_data: Dict) -> Dict:
        """
        解析原始指标数据，兼容ADB格式
        
        Args:
            raw_data: 原始数据字典，可能包含字符串格式的数据
            
        Returns:
            解析后的数值数据字典
        """
        parsed = {}
        
        # 1. 解析电量 (支持 "85%", "85", 85)
        battery = raw_data.get('battery_level', raw_data.get('battery', 0))
        if isinstance(battery, str):
            battery = float(re.sub(r'[^\d.]', '', battery))
        parsed['battery_level'] = float(battery)
        
        # 2. 解析温度 (支持 "32.5℃", "32.5°C", "32.5", 32.5)
        temp = raw_data.get('temperature', raw_data.get('temp', 30))
        if isinstance(temp, str):
            temp = float(re.sub(r'[^\d.]', '', temp))
        parsed['temperature'] = float(temp)
        
        # 3. 解析CPU使用率 (支持 "45%", "45", 45)
        cpu = raw_data.get('cpu_usage', raw_data.get('cpu', 0))
        if isinstance(cpu, str):
            cpu = float(re.sub(r'[^\d.]', '', cpu))
        parsed['cpu_usage'] = float(cpu)
        
        # 4. 解析内存使用率
        memory = raw_data.get('memory_usage', raw_data.get('memory', 0))
        if isinstance(memory, str):
            memory = float(re.sub(r'[^\d.]', '', memory))
        parsed['memory_usage'] = float(memory)
        
        # 5. 解析存储使用率
        storage = raw_data.get('storage_usage', raw_data.get('storage', 0))
        if isinstance(storage, str):
            storage = float(re.sub(r'[^\d.]', '', storage))
        parsed['storage_usage'] = float(storage)
        
        # 6. 解析网络状态
        network = raw_data.get('network_status', raw_data.get('network', 'unknown'))
        if isinstance(network, str):
            network = network.lower()
        parsed['network_status'] = network
        
        # 7. 解析活跃时间
        last_active = raw_data.get('last_active_time', raw_data.get('last_active'))
        if isinstance(last_active, str):
            try:
                last_active = datetime.fromisoformat(last_active.replace('Z', '+00:00'))
            except:
                last_active = None
        parsed['last_active_time'] = last_active
        
        return parsed
    
    def _score_battery(self, level: float) -> float:
        """
        电量评分 (线性插值)
        
        评分规则:
        - 100分: 电量 ≥ 80%
        - 0分: 电量 ≤ 20%
        - 中间: 线性插值
        
        Args:
            level: 电量百分比 (0-100)
            
        Returns:
            评分 (0-100)
        """
        if level >= 80:
            return 100.0
        elif level <= 20:
            return 0.0
        else:
            # 线性插值: 20% -> 0分, 80% -> 100分
            return (level - 20) / (80 - 20) * 100
    
    def _score_temperature(self, temp: float) -> float:
        """
        温度评分 (线性插值)
        
        评分规则:
        - 100分: 温度 ≤ 35℃
        - 0分: 温度 ≥ 45℃
        - 中间: 线性插值
        
        Args:
            temp: 温度 (℃)
            
        Returns:
            评分 (0-100)
        """
        if temp <= 35:
            return 100.0
        elif temp >= 45:
            return 0.0
        else:
            # 线性插值: 35℃ -> 100分, 45℃ -> 0分
            return (45 - temp) / (45 - 35) * 100
    
    def _score_usage(self, usage: float, low_threshold: float = 30, 
                     high_threshold: float = 80) -> float:
        """
        使用率评分 (通用，适用于CPU、内存、存储)
        
        评分规则:
        - 100分: 使用率 ≤ low_threshold
        - 0分: 使用率 ≥ high_threshold
        - 中间: 线性插值
        
        Args:
            usage: 使用率 (0-100)
            low_threshold: 低阈值
            high_threshold: 高阈值
            
        Returns:
            评分 (0-100)
        """
        if usage <= low_threshold:
            return 100.0
        elif usage >= high_threshold:
            return 0.0
        else:
            return (high_threshold - usage) / (high_threshold - low_threshold) * 100

    
    def _score_network(self, status: str) -> float:
        """
        网络状态评分
        
        评分规则:
        - 100分: connected (已连接)
        - 50分: limited (受限)
        - 0分: disconnected/unknown (断开/未知)
        
        Args:
            status: 网络状态
            
        Returns:
            评分 (0-100)
        """
        status = status.lower()
        if status == 'connected':
            return 100.0
        elif status == 'limited':
            return 50.0
        else:
            return 0.0
    
    def _score_activity(self, last_active: Optional[datetime]) -> float:
        """
        活跃度评分
        
        评分规则:
        - 100分: 5分钟内活跃
        - 80分: 1小时内活跃
        - 50分: 24小时内活跃
        - 20分: 72小时内活跃
        - 0分: 超过72小时未活跃
        
        Args:
            last_active: 最后活跃时间
            
        Returns:
            评分 (0-100)
        """
        if not last_active:
            return 50.0  # 未知时返回中等分数
        
        hours_inactive = (now_local() - last_active).total_seconds() / 3600
        
        if hours_inactive < 0.083:  # 5分钟
            return 100.0
        elif hours_inactive < 1:  # 1小时
            return 80.0
        elif hours_inactive < 24:  # 24小时
            return 50.0
        elif hours_inactive < 72:  # 72小时
            return 20.0
        else:
            return 0.0
    
    def calculate_score(self, metrics: Dict) -> Dict:
        """
        计算设备健康度总分
        
        Args:
            metrics: 设备指标字典
            
        Returns:
            评分结果字典，包含:
            - total_score: 总分 (0-100)
            - dimension_scores: 各维度得分
            - level: 健康等级
            - level_name: 等级名称
            - level_color: 等级颜色
            - recommendations: 改进建议
        """
        # 解析指标数据
        parsed = self.parse_metrics(metrics)
        
        # 计算各维度得分
        dimension_scores = {
            'battery': self._score_battery(parsed['battery_level']),
            'temperature': self._score_temperature(parsed['temperature']),
            'cpu': self._score_usage(parsed['cpu_usage'], 30, 80),
            'memory': self._score_usage(parsed['memory_usage'], 50, 85),
            'storage': self._score_usage(parsed['storage_usage'], 70, 95),
            'network': self._score_network(parsed['network_status']),
            'activity': self._score_activity(parsed['last_active_time']),
        }
        
        # 加权计算总分
        total_score = sum(
            dimension_scores[dim] * self.weights[dim]
            for dim in dimension_scores
        )
        
        # 获取健康等级
        level, level_name, level_color = self._get_health_level(total_score)
        
        # 生成改进建议
        recommendations = self._generate_recommendations(parsed, dimension_scores)
        
        return {
            'total_score': round(total_score, 2),
            'dimension_scores': {k: round(v, 2) for k, v in dimension_scores.items()},
            'weighted_scores': {
                k: round(v * self.weights[k], 2) 
                for k, v in dimension_scores.items()
            },
            'level': level,
            'level_name': level_name,
            'level_color': level_color,
            'recommendations': recommendations,
            'metrics': parsed,
        }
    
    def _get_health_level(self, score: float) -> Tuple[str, str, str]:
        """
        根据总分获取健康等级
        
        Args:
            score: 总分 (0-100)
            
        Returns:
            (等级代码, 等级名称, 颜色代码)
        """
        if score >= 90:
            return ('excellent', '优秀', '#52c41a')
        elif score >= 80:
            return ('good', '良好', '#1890ff')
        elif score >= 60:
            return ('fair', '一般', '#faad14')
        elif score >= 40:
            return ('warning', '警告', '#ff7a45')
        else:
            return ('danger', '危险', '#f5222d')
    
    def _generate_recommendations(self, metrics: Dict, scores: Dict) -> List[str]:
        """
        生成改进建议
        
        Args:
            metrics: 解析后的指标数据
            scores: 各维度得分
            
        Returns:
            建议列表
        """
        recommendations = []
        
        # 电量建议
        if scores['battery'] < 50:
            battery = metrics['battery_level']
            if battery < 20:
                recommendations.append(f"⚠️ 电量严重不足 ({battery:.0f}%)，请立即充电")
            else:
                recommendations.append(f"🔋 电量偏低 ({battery:.0f}%)，建议充电")
        
        # 温度建议
        if scores['temperature'] < 50:
            temp = metrics['temperature']
            if temp > 45:
                recommendations.append(f"🔥 设备温度过高 ({temp:.1f}℃)，请停止使用并降温")
            else:
                recommendations.append(f"🌡️ 设备温度偏高 ({temp:.1f}℃)，建议减少负载")
        
        # CPU建议
        if scores['cpu'] < 50:
            cpu = metrics['cpu_usage']
            recommendations.append(f"💻 CPU使用率过高 ({cpu:.1f}%)，建议关闭后台应用")
        
        # 内存建议
        if scores['memory'] < 50:
            memory = metrics['memory_usage']
            recommendations.append(f"🧠 内存使用率过高 ({memory:.1f}%)，建议清理内存")
        
        # 存储建议
        if scores['storage'] < 50:
            storage = metrics['storage_usage']
            if storage > 95:
                recommendations.append(f"💾 存储空间严重不足 ({storage:.1f}%)，请清理文件")
            else:
                recommendations.append(f"💾 存储空间不足 ({storage:.1f}%)，建议清理")
        
        # 网络建议
        if scores['network'] < 50:
            recommendations.append("📡 网络连接异常，请检查网络设置")
        
        # 活跃度建议
        if scores['activity'] < 50:
            last_active = metrics['last_active_time']
            if last_active:
                hours = (now_local() - last_active).total_seconds() / 3600
                recommendations.append(f"⏰ 设备长时间未活跃 ({hours:.1f}小时)，建议重启")
        
        if not recommendations:
            recommendations.append("✅ 设备状态良好，无需特别维护")
        
        return recommendations
    
    def update_weights(self, new_weights: Dict[str, float]) -> None:
        """
        动态更新权重配置
        
        Args:
            new_weights: 新的权重配置
            
        Raises:
            ValueError: 权重配置无效
        """
        self._validate_weights(new_weights)
        self.weights = new_weights
        logger.info(f"权重配置已更新: {self.weights}")
    
    def get_weights(self) -> Dict[str, float]:
        """获取当前权重配置"""
        return self.weights.copy()
    
    def batch_calculate(self, devices_metrics: List[Dict]) -> List[Dict]:
        """
        批量计算多个设备的健康度
        
        Args:
            devices_metrics: 设备指标列表
            
        Returns:
            评分结果列表
        """
        results = []
        for metrics in devices_metrics:
            try:
                result = self.calculate_score(metrics)
                results.append(result)
            except Exception as e:
                logger.error(f"计算设备健康度失败: {e}")
                results.append({
                    'error': str(e),
                    'total_score': 0,
                    'level': 'unknown',
                })
        return results


# ============================================================================
# 测试用例
# ============================================================================

def run_test_cases():
    """运行测试用例"""
    print("=" * 80)
    print("设备健康度评分算法测试")
    print("=" * 80)
    
    # 创建评分器
    scorer = DeviceHealthScorer()
    
    # 测试用例1: 健康设备
    print("\n【测试用例1】健康设备 - 小米12 Pro")
    print("-" * 80)
    device1 = {
        'battery_level': '85%',      # 电量充足
        'temperature': '32.5℃',      # 温度正常
        'cpu_usage': '25%',          # CPU使用率低
        'memory_usage': '45%',       # 内存使用率正常
        'storage_usage': '60%',      # 存储空间充足
        'network_status': 'connected',  # 网络正常
        'last_active_time': now_local() - timedelta(minutes=10),  # 最近活跃
    }
    result1 = scorer.calculate_score(device1)
    print_result(result1, "小米12 Pro")
    
    # 测试用例2: 警告状态设备
    print("\n【测试用例2】警告状态设备 - Samsung Galaxy S23")
    print("-" * 80)
    device2 = {
        'battery': 35,               # 电量偏低
        'temp': 42.0,                # 温度偏高
        'cpu': 65,                   # CPU使用率较高
        'memory': 78,                # 内存使用率较高
        'storage': 88,               # 存储空间紧张
        'network': 'connected',      # 网络正常
        'last_active': now_local() - timedelta(hours=2),  # 2小时前活跃
    }
    result2 = scorer.calculate_score(device2)
    print_result(result2, "Samsung Galaxy S23")
    
    # 测试用例3: 危险状态设备
    print("\n【测试用例3】危险状态设备 - OPPO Find X5")
    print("-" * 80)
    device3 = {
        'battery_level': 15,         # 电量严重不足
        'temperature': 48.5,         # 温度过高
        'cpu_usage': 85,             # CPU使用率过高
        'memory_usage': 92,          # 内存使用率过高
        'storage_usage': 96,         # 存储空间严重不足
        'network_status': 'disconnected',  # 网络断开
        'last_active_time': now_local() - timedelta(days=3),  # 3天未活跃
    }
    result3 = scorer.calculate_score(device3)
    print_result(result3, "OPPO Find X5")
    
    # 测试动态权重
    print("\n【测试用例4】动态权重测试")
    print("-" * 80)
    print("原始权重:", scorer.get_weights())
    
    # 调整权重: 更重视电量和温度
    custom_weights = {
        'battery': 0.30,      # 提高到30%
        'temperature': 0.25,  # 提高到25%
        'cpu': 0.15,
        'memory': 0.15,
        'storage': 0.05,      # 降低到5%
        'network': 0.05,      # 降低到5%
        'activity': 0.05,
    }
    scorer.update_weights(custom_weights)
    print("新权重:", scorer.get_weights())
    
    result4 = scorer.calculate_score(device2)
    print(f"\n使用新权重重新计算设备2:")
    print(f"总分: {result4['total_score']:.2f} -> {result4['level_name']}")
    
    # 批量计算测试
    print("\n【测试用例5】批量计算测试")
    print("-" * 80)
    devices = [device1, device2, device3]
    results = scorer.batch_calculate(devices)
    print(f"批量计算 {len(results)} 个设备:")
    for i, result in enumerate(results, 1):
        print(f"  设备{i}: {result['total_score']:.2f}分 - {result['level_name']}")


def print_result(result: Dict, device_name: str):
    """打印评分结果"""
    print(f"\n设备名称: {device_name}")
    print(f"总分: {result['total_score']:.2f} / 100")
    print(f"健康等级: {result['level_name']} ({result['level']})")
    print(f"等级颜色: {result['level_color']}")
    
    print("\n各维度得分:")
    for dim, score in result['dimension_scores'].items():
        weighted = result['weighted_scores'][dim]
        weight = result['weighted_scores'][dim] / score * 100 if score > 0 else 0
        print(f"  {dim:12s}: {score:6.2f}分 (权重后: {weighted:5.2f}分)")
    
    print("\n原始指标:")
    metrics = result['metrics']
    print(f"  电量: {metrics['battery_level']:.1f}%")
    print(f"  温度: {metrics['temperature']:.1f}℃")
    print(f"  CPU: {metrics['cpu_usage']:.1f}%")
    print(f"  内存: {metrics['memory_usage']:.1f}%")
    print(f"  存储: {metrics['storage_usage']:.1f}%")
    print(f"  网络: {metrics['network_status']}")
    if metrics['last_active_time']:
        hours = (now_local() - metrics['last_active_time']).total_seconds() / 3600
        print(f"  活跃: {hours:.1f}小时前")
    
    print("\n改进建议:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec}")


if __name__ == "__main__":
    # 运行测试用例
    run_test_cases()


# ============================================================================
# 向后兼容 - 保持旧的类名和接口
# ============================================================================

class DeviceHealthService:
    """设备健康度服务 - 兼容旧接口"""
    
    def __init__(self):
        self.scorer = DeviceHealthScorer()
    
    def calculate_health_score(self, device_data: Dict) -> int:
        """
        计算设备健康度分数 (兼容旧接口)
        
        Args:
            device_data: 设备数据字典
            
        Returns:
            健康度分数 0-100 (整数)
        """
        result = self.scorer.calculate_score(device_data)
        return int(result['total_score'])
    
    def get_health_level(self, score: int) -> Tuple[str, str, str]:
        """
        根据分数获取健康等级 (兼容旧接口)
        
        Args:
            score: 健康度分数
            
        Returns:
            (等级代码, 等级名称, 颜色)
        """
        return self.scorer._get_health_level(score)
    
    def generate_mock_metrics(self, device_id: int) -> Dict:
        """
        生成模拟指标数据 (兼容旧接口)
        
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
            'last_active_time': now_local() - timedelta(hours=random.randint(0, 48))
        }
