
"""
AI智能元素定位器
使用计算机视觉和OCR自动识别屏幕元素，无需手动指定坐标

技术栈：
- PaddleOCR: 文字识别
- OpenCV: 图像处理
- PIL: 图像操作
"""
import os
import re
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ElementType(Enum):
    """UI元素类型"""
    BUTTON = "button"
    INPUT = "input"
    TEXT = "text"
    IMAGE = "image"
    ICON = "icon"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SWITCH = "switch"
    SLIDER = "slider"
    DROPDOWN = "dropdown"
    TAB = "tab"
    UNKNOWN = "unknown"


class ElementState(Enum):
    """UI元素状态"""
    NORMAL = "normal"
    CHECKED = "checked"
    UNCHECKED = "unchecked"
    ENABLED = "enabled"
    DISABLED = "disabled"
    FOCUSED = "focused"
    SELECTED = "selected"
    LOADING = "loading"
    UNKNOWN = "unknown"


@dataclass
class UIElement:
    """UI元素数据类"""
    element_type: ElementType
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    center: Tuple[int, int]  # (x, y)
    description: str
    attributes: Dict = None
    state: ElementState = ElementState.UNKNOWN  # 新增：元素状态
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'type': self.element_type.value,
            'text': self.text,
            'confidence': round(self.confidence, 3),
            'bbox': self.bbox,
            'center': self.center,
            'description': self.description,
            'attributes': self.attributes or {},
            'state': self.state.value  # 新增：状态信息
        }


class OCREngine:
    """OCR识别引擎"""
    
    def __init__(self):
        """初始化OCR引擎"""
        self.ocr = None
        self._init_paddleocr()
    
    def _init_paddleocr(self):
        """初始化PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            
            # 使用轻量级模型
            # 注意：PaddleOCR 3.x版本参数有变化
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang='ch'  # 中文+英文
            )
            logger.info("PaddleOCR初始化成功")
        except ImportError:
            logger.warning("PaddleOCR未安装，OCR功能将不可用")
            logger.warning("安装命令: pip install paddleocr paddlepaddle")
            self.ocr = None
        except Exception as e:
            logger.error(f"PaddleOCR初始化失败: {e}")
            self.ocr = None
    
    def recognize(self, image_path: str) -> List[Dict]:
        """
        识别图像中的文字
        
        Args:
            image_path: 图像路径
            
        Returns:
            识别结果列表 [{'text': str, 'bbox': tuple, 'confidence': float}]
        """
        if not self.ocr:
            logger.warning("OCR引擎未初始化")
            return []
        
        try:
            # PaddleOCR 3.x版本使用predict方法
            result = self.ocr.ocr(image_path)
            
            if not result or not result[0]:
                return []
            
            # 解析结果
            ocr_results = []
            for line in result[0]:
                bbox = line[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                text_info = line[1]  # (text, confidence)
                
                # 计算边界框
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                x1, y1 = int(min(x_coords)), int(min(y_coords))
                x2, y2 = int(max(x_coords)), int(max(y_coords))
                
                ocr_results.append({
                    'text': text_info[0],
                    'bbox': (x1, y1, x2, y2),
                    'confidence': float(text_info[1])
                })
            
            return ocr_results
        
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return []


class ImageAnalyzer:
    """图像分析器"""
    
    def __init__(self):
        """初始化图像分析器"""
        pass
    
    def detect_buttons(self, image_path: str) -> List[Dict]:
        """
        检测按钮元素
        
        使用颜色、形状、边缘检测等方法识别按钮
        
        Args:
            image_path: 图像路径
            
        Returns:
            按钮列表
        """
        try:
            # 读取图像
            img = cv2.imread(image_path)
            if img is None:
                return []
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 边缘检测
            edges = cv2.Canny(gray, 50, 150)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            buttons = []
            for contour in contours:
                # 计算轮廓面积
                area = cv2.contourArea(contour)
                
                # 过滤太小或太大的区域
                if area < 1000 or area > 100000:
                    continue
                
                # 获取边界框
                x, y, w, h = cv2.boundingRect(contour)
                
                # 计算宽高比
                aspect_ratio = w / h if h > 0 else 0
                
                # 按钮通常是矩形，宽高比在0.3-5之间
                if 0.3 < aspect_ratio < 5:
                    buttons.append({
                        'bbox': (x, y, x + w, y + h),
                        'center': (x + w // 2, y + h // 2),
                        'area': area,
                        'aspect_ratio': aspect_ratio
                    })
            
            return buttons
        
        except Exception as e:
            logger.error(f"按钮检测失败: {e}")
            return []
    
    def detect_input_fields(self, image_path: str) -> List[Dict]:
        """
        检测输入框元素
        
        输入框通常是长条形的矩形区域
        
        Args:
            image_path: 图像路径
            
        Returns:
            输入框列表
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return []
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 边缘检测
            edges = cv2.Canny(gray, 30, 100)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            input_fields = []
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # 输入框面积适中
                if area < 2000 or area > 50000:
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # 输入框通常是横向长条形，宽高比 > 2
                if aspect_ratio > 2:
                    input_fields.append({
                        'bbox': (x, y, x + w, y + h),
                        'center': (x + w // 2, y + h // 2),
                        'area': area,
                        'aspect_ratio': aspect_ratio
                    })
            
            return input_fields
        
        except Exception as e:
            logger.error(f"输入框检测失败: {e}")
            return []
    
    def detect_checkboxes(self, image_path: str) -> List[Dict]:
        """
        检测复选框元素
        
        复选框通常是小的正方形区域
        
        Args:
            image_path: 图像路径
            
        Returns:
            复选框列表
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return []
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            checkboxes = []
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # 复选框面积较小
                if area < 100 or area > 2000:
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # 复选框通常是正方形，宽高比接近1
                if 0.8 < aspect_ratio < 1.2:
                    # 检测是否选中（通过检测内部是否有标记）
                    roi = gray[y:y+h, x:x+w]
                    mean_intensity = np.mean(roi)
                    
                    # 判断状态
                    is_checked = mean_intensity < 200  # 选中的复选框通常较暗
                    
                    checkboxes.append({
                        'bbox': (x, y, x + w, y + h),
                        'center': (x + w // 2, y + h // 2),
                        'area': area,
                        'aspect_ratio': aspect_ratio,
                        'checked': is_checked,
                        'state': 'checked' if is_checked else 'unchecked'
                    })
            
            return checkboxes
        
        except Exception as e:
            logger.error(f"复选框检测失败: {e}")
            return []
    
    def detect_switches(self, image_path: str) -> List[Dict]:
        """
        检测开关元素
        
        开关通常是椭圆形或圆角矩形
        
        Args:
            image_path: 图像路径
            
        Returns:
            开关列表
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return []
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            switches = []
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # 开关面积适中
                if area < 500 or area > 5000:
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # 开关通常是横向椭圆形，宽高比在1.5-3之间
                if 1.5 < aspect_ratio < 3:
                    # 检测开关状态（通过颜色判断）
                    roi = img[y:y+h, x:x+w]
                    mean_color = np.mean(roi, axis=(0, 1))
                    
                    # 简单判断：蓝色/绿色通常表示开启
                    is_on = mean_color[2] > 150 or mean_color[1] > 150
                    
                    switches.append({
                        'bbox': (x, y, x + w, y + h),
                        'center': (x + w // 2, y + h // 2),
                        'area': area,
                        'aspect_ratio': aspect_ratio,
                        'on': is_on,
                        'state': 'checked' if is_on else 'unchecked'
                    })
            
            return switches
        
        except Exception as e:
            logger.error(f"开关检测失败: {e}")
            return []
    
    def detect_sliders(self, image_path: str) -> List[Dict]:
        """
        检测滑块元素
        
        滑块通常是长条形带有滑动按钮
        
        Args:
            image_path: 图像路径
            
        Returns:
            滑块列表
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return []
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 30, 100)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            sliders = []
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # 滑块轨道面积适中
                if area < 1000 or area > 20000:
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # 滑块通常是很长的横向条形，宽高比 > 5
                if aspect_ratio > 5:
                    sliders.append({
                        'bbox': (x, y, x + w, y + h),
                        'center': (x + w // 2, y + h // 2),
                        'area': area,
                        'aspect_ratio': aspect_ratio,
                        'state': 'normal'
                    })
            
            return sliders
        
        except Exception as e:
            logger.error(f"滑块检测失败: {e}")
            return []
    
    def detect_radio_buttons(self, image_path: str) -> List[Dict]:
        """
        检测单选按钮元素
        
        单选按钮通常是小的圆形区域
        
        Args:
            image_path: 图像路径
            
        Returns:
            单选按钮列表
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return []
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 使用霍夫圆检测
            circles = cv2.HoughCircles(
                gray,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=20,
                param1=50,
                param2=30,
                minRadius=5,
                maxRadius=30
            )
            
            radio_buttons = []
            if circles is not None:
                circles = np.uint16(np.around(circles))
                for circle in circles[0, :]:
                    x, y, r = int(circle[0]), int(circle[1]), int(circle[2])
                    
                    # 检测是否选中
                    roi = gray[max(0, y-r):min(gray.shape[0], y+r), 
                              max(0, x-r):min(gray.shape[1], x+r)]
                    mean_intensity = float(np.mean(roi))
                    
                    is_selected = mean_intensity < 200
                    
                    radio_buttons.append({
                        'bbox': (x-r, y-r, x+r, y+r),
                        'center': (x, y),
                        'radius': r,
                        'selected': bool(is_selected),
                        'state': 'selected' if is_selected else 'normal'
                    })
            
            return radio_buttons
        
        except Exception as e:
            logger.error(f"单选按钮检测失败: {e}")
            return []
    
    def detect_in_region(
        self, 
        image_path: str, 
        region: Tuple[int, int, int, int],
        element_type: str = "all"
    ) -> List[Dict]:
        """
        在指定区域内检测元素
        
        Args:
            image_path: 图像路径
            region: 区域坐标 (x1, y1, x2, y2)
            element_type: 元素类型 (button, input, checkbox, etc.)
            
        Returns:
            区域内的元素列表
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return []
            
            x1, y1, x2, y2 = region
            
            # 裁剪区域
            roi = img[y1:y2, x1:x2]
            
            # 保存临时图像
            temp_path = image_path.replace('.png', '_temp_roi.png')
            cv2.imwrite(temp_path, roi)
            
            # 在裁剪区域内检测元素
            elements = []
            if element_type == "all" or element_type == "button":
                buttons = self.detect_buttons(temp_path)
                for btn in buttons:
                    # 调整坐标到原图
                    btn['bbox'] = (
                        btn['bbox'][0] + x1,
                        btn['bbox'][1] + y1,
                        btn['bbox'][2] + x1,
                        btn['bbox'][3] + y1
                    )
                    btn['center'] = (
                        btn['center'][0] + x1,
                        btn['center'][1] + y1
                    )
                    elements.append(btn)
            
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return elements
        
        except Exception as e:
            logger.error(f"区域检测失败: {e}")
            return []
    
    def get_image_info(self, image_path: str) -> Dict:
        """
        获取图像基本信息
        
        Args:
            image_path: 图像路径
            
        Returns:
            图像信息字典
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {}
            
            height, width = img.shape[:2]
            
            return {
                'width': width,
                'height': height,
                'aspect_ratio': width / height if height > 0 else 0,
                'size': (width, height)
            }
        
        except Exception as e:
            logger.error(f"获取图像信息失败: {e}")
            return {}


class ElementMatcher:
    """元素匹配器"""
    
    def __init__(self):
        """初始化元素匹配器"""
        pass
    
    def match_by_text(
        self, 
        query: str, 
        elements: List[UIElement],
        fuzzy: bool = True
    ) -> List[UIElement]:
        """
        根据文本匹配元素
        
        Args:
            query: 查询文本
            elements: 元素列表
            fuzzy: 是否模糊匹配
            
        Returns:
            匹配的元素列表
        """
        matched = []
        query_lower = query.lower()
        
        for element in elements:
            if not element.text:
                continue
            
            text_lower = element.text.lower()
            
            if fuzzy:
                # 模糊匹配：包含关系
                if query_lower in text_lower or text_lower in query_lower:
                    matched.append(element)
            else:
                # 精确匹配
                if query_lower == text_lower:
                    matched.append(element)
        
        return matched
    
    def match_by_description(
        self, 
        description: str, 
        elements: List[UIElement]
    ) -> List[UIElement]:
        """
        根据自然语言描述匹配元素
        
        支持的描述格式：
        - "登录按钮"
        - "蓝色的提交按钮"
        - "包含确认的按钮"
        
        Args:
            description: 自然语言描述
            elements: 元素列表
            
        Returns:
            匹配的元素列表
        """
        # 提取关键词
        keywords = self._extract_keywords(description)
        
        matched = []
        for element in elements:
            score = self._calculate_match_score(element, keywords)
            if score > 0.5:  # 匹配度阈值
                matched.append(element)
        
        # 按匹配度排序
        matched.sort(key=lambda e: self._calculate_match_score(e, keywords), reverse=True)
        
        return matched
    
    def find_relative_element(
        self,
        anchor_element: UIElement,
        direction: str,
        elements: List[UIElement],
        distance_threshold: int = 200
    ) -> Optional[UIElement]:
        """
        查找相对位置的元素
        
        Args:
            anchor_element: 锚点元素
            direction: 方向 (left, right, top, bottom, above, below)
            elements: 元素列表
            distance_threshold: 距离阈值（像素）
            
        Returns:
            找到的元素
        """
        anchor_x, anchor_y = anchor_element.center
        candidates = []
        
        for element in elements:
            if element == anchor_element:
                continue
            
            elem_x, elem_y = element.center
            distance = self._calculate_distance(anchor_element.center, element.center)
            
            if distance > distance_threshold:
                continue
            
            # 根据方向筛选
            if direction in ["right", "右边", "右侧"]:
                if elem_x > anchor_x and abs(elem_y - anchor_y) < 100:
                    candidates.append((element, distance))
            
            elif direction in ["left", "左边", "左侧"]:
                if elem_x < anchor_x and abs(elem_y - anchor_y) < 100:
                    candidates.append((element, distance))
            
            elif direction in ["top", "above", "上方", "上面"]:
                if elem_y < anchor_y and abs(elem_x - anchor_x) < 100:
                    candidates.append((element, distance))
            
            elif direction in ["bottom", "below", "下方", "下面"]:
                if elem_y > anchor_y and abs(elem_x - anchor_x) < 100:
                    candidates.append((element, distance))
        
        # 返回最近的元素
        if candidates:
            candidates.sort(key=lambda x: x[1])
            return candidates[0][0]
        
        return None
    
    def find_in_region(
        self,
        region: Tuple[int, int, int, int],
        elements: List[UIElement]
    ) -> List[UIElement]:
        """
        查找指定区域内的元素
        
        Args:
            region: 区域坐标 (x1, y1, x2, y2)
            elements: 元素列表
            
        Returns:
            区域内的元素列表
        """
        x1, y1, x2, y2 = region
        matched = []
        
        for element in elements:
            elem_x, elem_y = element.center
            
            # 检查元素中心是否在区域内
            if x1 <= elem_x <= x2 and y1 <= elem_y <= y2:
                matched.append(element)
        
        return matched
    
    def find_similar_elements(
        self,
        reference_element: UIElement,
        elements: List[UIElement],
        similarity_threshold: float = 0.8
    ) -> List[UIElement]:
        """
        查找相似的元素
        
        Args:
            reference_element: 参考元素
            elements: 元素列表
            similarity_threshold: 相似度阈值
            
        Returns:
            相似元素列表
        """
        similar = []
        
        for element in elements:
            if element == reference_element:
                continue
            
            # 计算相似度
            similarity = self._calculate_similarity(reference_element, element)
            
            if similarity >= similarity_threshold:
                similar.append(element)
        
        return similar
    
    def filter_by_state(
        self,
        elements: List[UIElement],
        state: ElementState
    ) -> List[UIElement]:
        """
        按状态筛选元素
        
        Args:
            elements: 元素列表
            state: 目标状态
            
        Returns:
            符合状态的元素列表
        """
        return [e for e in elements if e.state == state]
    
    def _calculate_distance(
        self,
        point1: Tuple[int, int],
        point2: Tuple[int, int]
    ) -> float:
        """计算两点之间的距离"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def _calculate_similarity(
        self,
        elem1: UIElement,
        elem2: UIElement
    ) -> float:
        """
        计算两个元素的相似度
        
        考虑因素：
        - 元素类型
        - 大小
        - 文本相似度
        """
        score = 0.0
        
        # 类型相同 +0.4
        if elem1.element_type == elem2.element_type:
            score += 0.4
        
        # 大小相似 +0.3
        size1 = (elem1.bbox[2] - elem1.bbox[0]) * (elem1.bbox[3] - elem1.bbox[1])
        size2 = (elem2.bbox[2] - elem2.bbox[0]) * (elem2.bbox[3] - elem2.bbox[1])
        size_ratio = min(size1, size2) / max(size1, size2) if max(size1, size2) > 0 else 0
        score += 0.3 * size_ratio
        
        # 文本相似 +0.3
        if elem1.text and elem2.text:
            text_similarity = len(set(elem1.text) & set(elem2.text)) / len(set(elem1.text) | set(elem2.text))
            score += 0.3 * text_similarity
        
        return score
    
    def _extract_keywords(self, description: str) -> Dict[str, List[str]]:
        """
        从描述中提取关键词
        
        Args:
            description: 描述文本
            
        Returns:
            关键词字典 {'type': [], 'text': [], 'color': [], 'position': []}
        """
        keywords = {
            'type': [],
            'text': [],
            'color': [],
            'position': []
        }
        
        # 元素类型关键词
        type_keywords = {
            '按钮': ElementType.BUTTON,
            'button': ElementType.BUTTON,
            '输入框': ElementType.INPUT,
            'input': ElementType.INPUT,
            '文本': ElementType.TEXT,
            'text': ElementType.TEXT,
        }
        
        for keyword, elem_type in type_keywords.items():
            if keyword in description.lower():
                keywords['type'].append(elem_type.value)
        
        # 颜色关键词
        color_keywords = ['红色', '蓝色', '绿色', '黄色', '白色', '黑色', 'red', 'blue', 'green']
        for color in color_keywords:
            if color in description.lower():
                keywords['color'].append(color)
        
        # 位置关键词
        position_keywords = ['顶部', '底部', '左侧', '右侧', '中间', 'top', 'bottom', 'left', 'right', 'center']
        for pos in position_keywords:
            if pos in description.lower():
                keywords['position'].append(pos)
        
        # 提取文本内容（去除类型、颜色、位置词后的剩余部分）
        text_content = description
        for keyword_list in [type_keywords.keys(), color_keywords, position_keywords]:
            for keyword in keyword_list:
                text_content = text_content.replace(keyword, '')
        
        text_content = text_content.strip()
        if text_content:
            keywords['text'].append(text_content)
        
        return keywords
    
    def _calculate_match_score(self, element: UIElement, keywords: Dict) -> float:
        """
        计算元素与关键词的匹配度
        
        Args:
            element: UI元素
            keywords: 关键词字典
            
        Returns:
            匹配度分数 (0-1)
        """
        score = 0.0
        total_weight = 0.0
        
        # 类型匹配 (权重: 0.3)
        if keywords['type']:
            if element.element_type.value in keywords['type']:
                score += 0.3
            total_weight += 0.3
        
        # 文本匹配 (权重: 0.5)
        if keywords['text'] and element.text:
            for text_keyword in keywords['text']:
                if text_keyword.lower() in element.text.lower():
                    score += 0.5
                    break
            total_weight += 0.5
        
        # 位置匹配 (权重: 0.2)
        if keywords['position']:
            # 简化的位置匹配逻辑
            total_weight += 0.2
        
        return score / total_weight if total_weight > 0 else 0.0


class AIElementLocator:
    """AI智能元素定位器主类"""
    
    def __init__(self):
        """初始化元素定位器"""
        self.ocr_engine = OCREngine()
        self.image_analyzer = ImageAnalyzer()
        self.element_matcher = ElementMatcher()
        
        logger.info("AI元素定位器初始化完成")
    
    def analyze_screenshot(self, image_path: str, detect_all: bool = True) -> List[UIElement]:
        """
        分析截图，识别所有UI元素
        
        Args:
            image_path: 截图路径
            detect_all: 是否检测所有类型的元素
            
        Returns:
            UI元素列表
        """
        if not os.path.exists(image_path):
            logger.error(f"图像文件不存在: {image_path}")
            return []
        
        elements = []
        
        # 1. OCR文字识别
        ocr_results = self.ocr_engine.recognize(image_path)
        for ocr_result in ocr_results:
            element = UIElement(
                element_type=self._infer_element_type(ocr_result['text']),
                text=ocr_result['text'],
                confidence=ocr_result['confidence'],
                bbox=ocr_result['bbox'],
                center=self._calculate_center(ocr_result['bbox']),
                description=f"文本: {ocr_result['text']}",
                attributes={'source': 'ocr'},
                state=ElementState.NORMAL
            )
            elements.append(element)
        
        # 2. 按钮检测
        buttons = self.image_analyzer.detect_buttons(image_path)
        for button in buttons:
            overlapping_text = self._find_overlapping_text(button['bbox'], ocr_results)
            
            element = UIElement(
                element_type=ElementType.BUTTON,
                text=overlapping_text,
                confidence=0.8,
                bbox=button['bbox'],
                center=button['center'],
                description=f"按钮{': ' + overlapping_text if overlapping_text else ''}",
                attributes={'source': 'vision', 'area': button['area']},
                state=ElementState.NORMAL
            )
            elements.append(element)
        
        # 3. 输入框检测
        input_fields = self.image_analyzer.detect_input_fields(image_path)
        for input_field in input_fields:
            overlapping_text = self._find_overlapping_text(input_field['bbox'], ocr_results)
            
            element = UIElement(
                element_type=ElementType.INPUT,
                text=overlapping_text,
                confidence=0.75,
                bbox=input_field['bbox'],
                center=input_field['center'],
                description=f"输入框{': ' + overlapping_text if overlapping_text else ''}",
                attributes={'source': 'vision', 'area': input_field['area']},
                state=ElementState.NORMAL
            )
            elements.append(element)
        
        if detect_all:
            # 4. 复选框检测
            checkboxes = self.image_analyzer.detect_checkboxes(image_path)
            for checkbox in checkboxes:
                overlapping_text = self._find_overlapping_text(checkbox['bbox'], ocr_results)
                state = ElementState.CHECKED if checkbox.get('checked') else ElementState.UNCHECKED
                
                element = UIElement(
                    element_type=ElementType.CHECKBOX,
                    text=overlapping_text,
                    confidence=0.7,
                    bbox=checkbox['bbox'],
                    center=checkbox['center'],
                    description=f"复选框{': ' + overlapping_text if overlapping_text else ''} ({checkbox.get('state', 'unknown')})",
                    attributes={'source': 'vision', 'checked': bool(checkbox.get('checked', False))},
                    state=state
                )
                elements.append(element)
            
            # 5. 开关检测
            switches = self.image_analyzer.detect_switches(image_path)
            for switch in switches:
                overlapping_text = self._find_overlapping_text(switch['bbox'], ocr_results)
                state = ElementState.CHECKED if switch.get('on') else ElementState.UNCHECKED
                
                element = UIElement(
                    element_type=ElementType.SWITCH,
                    text=overlapping_text,
                    confidence=0.7,
                    bbox=switch['bbox'],
                    center=switch['center'],
                    description=f"开关{': ' + overlapping_text if overlapping_text else ''} ({switch.get('state', 'unknown')})",
                    attributes={'source': 'vision', 'on': bool(switch.get('on', False))},
                    state=state
                )
                elements.append(element)
            
            # 6. 滑块检测
            sliders = self.image_analyzer.detect_sliders(image_path)
            for slider in sliders:
                overlapping_text = self._find_overlapping_text(slider['bbox'], ocr_results)
                
                element = UIElement(
                    element_type=ElementType.SLIDER,
                    text=overlapping_text,
                    confidence=0.65,
                    bbox=slider['bbox'],
                    center=slider['center'],
                    description=f"滑块{': ' + overlapping_text if overlapping_text else ''}",
                    attributes={'source': 'vision'},
                    state=ElementState.NORMAL
                )
                elements.append(element)
            
            # 7. 单选按钮检测
            radio_buttons = self.image_analyzer.detect_radio_buttons(image_path)
            for radio in radio_buttons:
                overlapping_text = self._find_overlapping_text(radio['bbox'], ocr_results)
                state = ElementState.SELECTED if radio.get('selected') else ElementState.NORMAL
                
                element = UIElement(
                    element_type=ElementType.RADIO,
                    text=overlapping_text,
                    confidence=0.7,
                    bbox=radio['bbox'],
                    center=radio['center'],
                    description=f"单选按钮{': ' + overlapping_text if overlapping_text else ''} ({radio.get('state', 'unknown')})",
                    attributes={'source': 'vision', 'selected': bool(radio.get('selected', False))},
                    state=state
                )
                elements.append(element)
        
        logger.info(f"识别到 {len(elements)} 个UI元素")
        return elements
    
    def find_element(
        self, 
        image_path: str, 
        query: str,
        method: str = 'auto'
    ) -> Optional[UIElement]:
        """
        查找指定元素
        
        Args:
            image_path: 截图路径
            query: 查询条件（文本或描述）
            method: 查找方法 ('text', 'description', 'auto')
            
        Returns:
            找到的元素，如果没找到返回None
        """
        # 分析截图
        elements = self.analyze_screenshot(image_path)
        
        if not elements:
            logger.warning("未识别到任何元素")
            return None
        
        # 根据方法查找
        if method == 'text':
            matched = self.element_matcher.match_by_text(query, elements)
        elif method == 'description':
            matched = self.element_matcher.match_by_description(query, elements)
        else:  # auto
            # 先尝试文本匹配
            matched = self.element_matcher.match_by_text(query, elements)
            if not matched:
                # 再尝试描述匹配
                matched = self.element_matcher.match_by_description(query, elements)
        
        if matched:
            logger.info(f"找到 {len(matched)} 个匹配元素")
            return matched[0]  # 返回最佳匹配
        else:
            logger.warning(f"未找到匹配元素: {query}")
            return None
    
    def get_click_coordinates(
        self, 
        image_path: str, 
        query: str
    ) -> Optional[Tuple[int, int]]:
        """
        获取元素的点击坐标
        
        Args:
            image_path: 截图路径
            query: 查询条件
            
        Returns:
            点击坐标 (x, y)，如果没找到返回None
        """
        element = self.find_element(image_path, query)
        
        if element:
            return element.center
        else:
            return None
    
    def generate_adb_command(
        self, 
        image_path: str, 
        action: str,
        query: str = None
    ) -> Optional[str]:
        """
        生成ADB命令
        
        Args:
            image_path: 截图路径
            action: 操作类型 ('click', 'input', 'swipe')
            query: 元素查询条件（对于click操作）
            
        Returns:
            ADB命令字符串
        """
        if action == 'click':
            if not query:
                logger.error("点击操作需要指定查询条件")
                return None
            
            coords = self.get_click_coordinates(image_path, query)
            if coords:
                return f"adb shell input tap {coords[0]} {coords[1]}"
            else:
                return None
        
        # 其他操作类型可以扩展
        return None
    
    def visualize_elements(
        self, 
        image_path: str, 
        output_path: str = None,
        show_labels: bool = True,
        show_center: bool = False,
        min_confidence: float = 0.0
    ) -> str:
        """
        可视化识别的元素（优化版）
        
        在图像上标注识别的元素，使用更清晰的显示方式
        
        Args:
            image_path: 输入图像路径
            output_path: 输出图像路径（可选）
            show_labels: 是否显示文字标签
            show_center: 是否显示中心点
            min_confidence: 最小置信度阈值
            
        Returns:
            输出图像路径
        """
        if output_path is None:
            base, ext = os.path.splitext(image_path)
            output_path = f"{base}_annotated{ext}"
        
        # 分析元素
        elements = self.analyze_screenshot(image_path)
        
        # 过滤低置信度元素
        elements = [e for e in elements if e.confidence >= min_confidence]
        
        # 读取图像
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # 加载字体
        try:
            font_large = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
            font_small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 12)
        except:
            try:
                font_large = ImageFont.truetype("arial.ttf", 16)
                font_small = ImageFont.truetype("arial.ttf", 12)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
        
        # 元素类型颜色映射（更鲜明的颜色）
        colors = {
            ElementType.BUTTON: '#FF4444',      # 红色
            ElementType.INPUT: '#4444FF',       # 蓝色
            ElementType.TEXT: '#44FF44',        # 绿色
            ElementType.CHECKBOX: '#FF44FF',    # 紫色
            ElementType.RADIO: '#FFAA00',       # 橙色
            ElementType.SWITCH: '#00FFFF',      # 青色
            ElementType.SLIDER: '#FF8800',      # 深橙色
            ElementType.IMAGE: '#888888',       # 灰色
            ElementType.ICON: '#AAAAAA',        # 浅灰色
            ElementType.UNKNOWN: '#666666'      # 深灰色
        }
        
        # 按元素类型分组，避免重叠
        type_groups = {}
        for element in elements:
            elem_type = element.element_type
            if elem_type not in type_groups:
                type_groups[elem_type] = []
            type_groups[elem_type].append(element)
        
        # 绘制元素
        label_positions = []  # 记录已使用的标签位置，避免重叠
        
        for i, element in enumerate(elements):
            color = colors.get(element.element_type, '#FFFF00')
            
            # 绘制边界框（半透明效果）
            x1, y1, x2, y2 = element.bbox
            draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
            
            # 绘制中心点（可选）
            if show_center:
                cx, cy = element.center
                draw.ellipse((cx-3, cy-3, cx+3, cy+3), fill=color, outline='white')
            
            # 绘制编号标签（小圆圈）
            cx, cy = element.center
            radius = 12
            draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), 
                        fill=color, outline='white', width=2)
            
            # 绘制编号文字
            number_text = str(i+1)
            # 计算文字位置使其居中
            bbox = draw.textbbox((0, 0), number_text, font=font_small)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text((cx - text_width//2, cy - text_height//2), 
                     number_text, fill='white', font=font_small)
            
            # 绘制详细标签（如果启用）
            if show_labels and element.text:
                # 构建标签文本
                label_text = f"{element.element_type.value}"
                if element.text:
                    # 限制文本长度
                    text_preview = element.text[:15] + ('...' if len(element.text) > 15 else '')
                    label_text += f": {text_preview}"
                
                # 查找合适的标签位置（避免重叠）
                label_x = x1
                label_y = y1 - 22
                
                # 如果标签位置已被占用，向下移动
                for used_pos in label_positions:
                    if abs(label_x - used_pos[0]) < 100 and abs(label_y - used_pos[1]) < 25:
                        label_y += 25
                
                # 确保标签不超出图像边界
                if label_y < 0:
                    label_y = y2 + 5
                
                # 绘制标签背景
                bbox = draw.textbbox((label_x, label_y), label_text, font=font_small)
                padding = 3
                draw.rectangle(
                    [bbox[0]-padding, bbox[1]-padding, 
                     bbox[2]+padding, bbox[3]+padding],
                    fill='white', outline=color, width=1
                )
                
                # 绘制标签文字
                draw.text((label_x, label_y), label_text, fill=color, font=font_small)
                
                # 记录标签位置
                label_positions.append((label_x, label_y))
        
        # 在图像顶部添加图例
        legend_y = 10
        legend_x = 10
        legend_items = []
        
        for elem_type, color in colors.items():
            if elem_type in type_groups:
                count = len(type_groups[elem_type])
                legend_items.append((elem_type.value, color, count))
        
        # 绘制图例背景
        if legend_items:
            legend_height = len(legend_items) * 25 + 20
            draw.rectangle([5, 5, 200, legend_height], 
                          fill='white', outline='black', width=2)
            
            draw.text((legend_x, legend_y), "元素类型统计:", fill='black', font=font_small)
            legend_y += 20
            
            for type_name, color, count in legend_items:
                # 绘制颜色方块
                draw.rectangle([legend_x, legend_y, legend_x+15, legend_y+15], 
                              fill=color, outline='black')
                # 绘制文字
                draw.text((legend_x+20, legend_y), 
                         f"{type_name}: {count}个", 
                         fill='black', font=font_small)
                legend_y += 20
        
        # 保存图像
        img.save(output_path)
        logger.info(f"可视化结果已保存到: {output_path}")
        
        return output_path
    
    def _infer_element_type(self, text: str) -> ElementType:
        """
        根据文本推断元素类型
        
        Args:
            text: 文本内容
            
        Returns:
            元素类型
        """
        text_lower = text.lower()
        
        # 按钮关键词
        button_keywords = ['登录', '注册', '提交', '确认', '取消', '返回', '搜索', '发送',
                          'login', 'register', 'submit', 'confirm', 'cancel', 'back', 'search', 'send']
        
        for keyword in button_keywords:
            if keyword in text_lower:
                return ElementType.BUTTON
        
        # 输入框提示词
        input_keywords = ['请输入', '输入', '账号', '密码', '邮箱', '手机号',
                         'enter', 'input', 'username', 'password', 'email', 'phone']
        
        for keyword in input_keywords:
            if keyword in text_lower:
                return ElementType.INPUT
        
        return ElementType.TEXT
    
    def _calculate_center(self, bbox: Tuple[int, int, int, int]) -> Tuple[int, int]:
        """计算边界框中心点"""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    def _find_overlapping_text(
        self, 
        bbox: Tuple[int, int, int, int], 
        ocr_results: List[Dict]
    ) -> str:
        """
        查找与边界框重叠的文本
        
        Args:
            bbox: 边界框
            ocr_results: OCR识别结果
            
        Returns:
            重叠的文本内容
        """
        x1, y1, x2, y2 = bbox
        
        for ocr_result in ocr_results:
            ox1, oy1, ox2, oy2 = ocr_result['bbox']
            
            # 检查是否重叠
            if not (ox2 < x1 or ox1 > x2 or oy2 < y1 or oy1 > y2):
                return ocr_result['text']
        
        return ""


# 便捷函数
def locate_element(image_path: str, query: str) -> Optional[Dict]:
    """
    便捷函数：定位元素
    
    Args:
        image_path: 截图路径
        query: 查询条件
        
    Returns:
        元素信息字典
    """
    locator = AIElementLocator()
    element = locator.find_element(image_path, query)
    
    if element:
        return element.to_dict()
    else:
        return None


def get_click_command(image_path: str, query: str) -> Optional[str]:
    """
    便捷函数：获取点击命令
    
    Args:
        image_path: 截图路径
        query: 查询条件
        
    Returns:
        ADB点击命令
    """
    locator = AIElementLocator()
    return locator.generate_adb_command(image_path, 'click', query)
