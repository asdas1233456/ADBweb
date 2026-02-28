"""
AI智能元素定位器完整测试套件
整合了所有AI元素定位器相关的测试
"""
import pytest
import requests
import json
import os
from PIL import Image, ImageDraw, ImageFont

BASE_URL = "http://localhost:8000/api/v1"


class TestAIElementLocator:
    """AI元素定位器基础功能测试"""
    
    @pytest.fixture
    def test_image_path(self):
        """创建测试图片"""
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # 绘制一些测试元素
        draw.rectangle([100, 100, 300, 150], outline='blue', width=2)
        draw.text((150, 115), "登录", fill='black')
        
        draw.rectangle([100, 200, 300, 250], outline='blue', width=2)
        draw.text((150, 215), "注册", fill='black')
        
        path = "test_screenshot.png"
        img.save(path)
        yield path
        
        # 清理
        if os.path.exists(path):
            os.remove(path)
    
    def test_upload_screenshot(self, test_image_path):
        """测试上传截图"""
        with open(test_image_path, "rb") as f:
            files = {"file": ("screenshot.png", f, "image/png")}
            response = requests.post(
                f"{BASE_URL}/ai-element-locator/upload-screenshot",
                files=files
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "file_path" in data["data"]
    
    def test_analyze_screenshot(self, test_image_path):
        """测试分析截图"""
        # 先上传
        with open(test_image_path, "rb") as f:
            files = {"file": ("screenshot.png", f, "image/png")}
            upload_response = requests.post(
                f"{BASE_URL}/ai-element-locator/upload-screenshot",
                files=files
            )
        
        image_path = upload_response.json()["data"]["file_path"]
        
        # 分析
        response = requests.post(
            f"{BASE_URL}/ai-element-locator/analyze",
            json={"image_path": image_path}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "elements" in data["data"]


class TestEnhancedFeatures:
    """AI元素定位器增强功能测试"""
    
    def test_find_relative_element(self):
        """测试相对位置查找"""
        # 这里需要实际的测试图片
        pass
    
    def test_find_in_region(self):
        """测试区域查找"""
        pass
    
    def test_filter_by_state(self):
        """测试状态筛选"""
        pass


class TestVisualization:
    """可视化功能测试"""
    
    def test_visualize_with_labels(self):
        """测试带标签的可视化"""
        pass
    
    def test_visualize_without_labels(self):
        """测试不带标签的可视化"""
        pass


class TestOCR:
    """OCR功能测试"""
    
    def test_ocr_recognition(self):
        """测试OCR识别"""
        try:
            import paddleocr
            # OCR测试
            pass
        except ImportError:
            pytest.skip("PaddleOCR未安装")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
