"""
AI智能元素定位API路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session
from app.core.database import get_session
from app.schemas.common import Response
from app.services.ai_element_locator import AIElementLocator, locate_element, get_click_command
from pydantic import BaseModel
from typing import List, Optional
import logging
import os
import shutil
from datetime import datetime
import uuid
from app.utils.time_utils import now_local

from app.core.config import settings
from app.utils.file_handler import FileHandler
from app.utils.path_safety import resolve_upload_path

router = APIRouter(prefix="/ai-element-locator", tags=["AI元素定位"])
logger = logging.getLogger(__name__)


class AnalyzeRequest(BaseModel):
    """分析请求"""
    image_path: str


class FindElementRequest(BaseModel):
    """查找元素请求"""
    image_path: str
    query: str
    method: str = "auto"  # text, description, auto


class GenerateCommandRequest(BaseModel):
    """生成命令请求"""
    image_path: str
    action: str  # click, input, swipe
    query: Optional[str] = None
    text: Optional[str] = None  # 用于input操作


class VisualizeRequest(BaseModel):
    """可视化请求"""
    image_path: str
    output_path: Optional[str] = None
    show_labels: bool = True  # 是否显示文字标签
    show_center: bool = False  # 是否显示中心点
    min_confidence: float = 0.0  # 最小置信度阈值



def _safe_image_path(path: str) -> str:
    """?????? uploads ??????"""
    try:
        return str(resolve_upload_path(path))
    except ValueError:
        raise HTTPException(status_code=400, detail="???????")


@router.post("/upload-screenshot")
async def upload_screenshot(file: UploadFile = File(...)):
    """
    ????
    
    Args:
        file: ????
        
    Returns:
        ????
    """
    try:
        FileHandler.ensure_upload_dir()

        size = FileHandler._get_upload_size(file)
        if size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="?????????")

        upload_dir = os.path.join(settings.UPLOAD_DIR, "screenshots", "ai_analysis")
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp = now_local().strftime("%Y%m%d_%H%M%S")
        safe_name = FileHandler._sanitize_filename(file.filename)
        file_ext = os.path.splitext(safe_name)[1].lower() or '.png'
        allowed_image_exts = {e.strip().lower() for e in settings.ALLOWED_IMAGE_EXTS.split(",") if e.strip()}
        if file_ext not in allowed_image_exts:
            raise HTTPException(status_code=400, detail="????????")

        unique = uuid.uuid4().hex[:8]
        filename = f"screenshot_{timestamp}_{unique}{file_ext}"
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"??????: {file_path}")
        
        url_path = file_path.replace("\\", "/")
        
        return Response(
            message="??????",
            data={
                "file_path": file_path,
                "url_path": url_path,
                "filename": filename,
                "size": size
            }
        )
    except HTTPException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"??????: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=Response[dict])
async def analyze_screenshot(request: AnalyzeRequest):
    """
    分析截图，识别所有UI元素
    
    Args:
        request: 分析请求
        
    Returns:
        识别的元素列表
    """
    try:
        image_path = _safe_image_path(request.image_path)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="图像文件不存在")
        
        locator = AIElementLocator()
        elements = locator.analyze_screenshot(image_path)
        
        # 转换为字典
        elements_data = [element.to_dict() for element in elements]
        
        return Response(
            message=f"识别到 {len(elements)} 个UI元素",
            data={
                "total": len(elements),
                "elements": elements_data,
                "image_path": image_path
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"分析截图失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/find-element", response_model=Response[dict])
async def find_element(request: FindElementRequest):
    """
    查找指定元素
    
    Args:
        request: 查找元素请求
        
    Returns:
        找到的元素信息
    """
    try:
        image_path = _safe_image_path(request.image_path)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="图像文件不存在")
        
        locator = AIElementLocator()
        element = locator.find_element(image_path, request.query, request.method)
        
        if element:
            return Response(
                message="找到匹配元素",
                data=element.to_dict()
            )
        else:
            return Response(
                code=404,
                message="未找到匹配元素",
                data=None
            )
    except HTTPException:
        raise
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"查找元素失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get-coordinates", response_model=Response[dict])
async def get_coordinates(request: FindElementRequest):
    """
    获取元素点击坐标
    
    Args:
        request: 查找元素请求
        
    Returns:
        点击坐标
    """
    try:
        image_path = _safe_image_path(request.image_path)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="图像文件不存在")
        
        locator = AIElementLocator()
        coords = locator.get_click_coordinates(image_path, request.query)
        
        if coords:
            return Response(
                message="获取坐标成功",
                data={
                    "x": coords[0],
                    "y": coords[1],
                    "coordinates": coords,
                    "query": request.query
                }
            )
        else:
            return Response(
                code=404,
                message="未找到匹配元素",
                data=None
            )
    except HTTPException:
        raise
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"获取坐标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-command", response_model=Response[dict])
async def generate_command(request: GenerateCommandRequest):
    """
    生成ADB命令
    
    Args:
        request: 生成命令请求
        
    Returns:
        ADB命令
    """
    try:
        image_path = _safe_image_path(request.image_path)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="图像文件不存在")
        
        locator = AIElementLocator()
        command = locator.generate_adb_command(
            image_path, 
            request.action, 
            request.query
        )
        
        if command:
            return Response(
                message="命令生成成功",
                data={
                    "command": command,
                    "action": request.action,
                    "query": request.query
                }
            )
        else:
            return Response(
                code=404,
                message="无法生成命令",
                data=None
            )
    except HTTPException:
        raise
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"生成命令失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/visualize", response_model=Response[dict])
async def visualize_elements(request: VisualizeRequest):
    """
    可视化识别的元素（优化版）
    
    在图像上标注识别的元素，使用更清晰的显示方式
    
    参数说明：
    - image_path: 图像路径
    - output_path: 输出路径（可选）
    - show_labels: 是否显示文字标签（默认True）
    - show_center: 是否显示中心点（默认False）
    - min_confidence: 最小置信度阈值（默认0.0）
    
    优化特性：
    - 使用编号圆圈标注元素位置
    - 智能避免标签重叠
    - 添加元素类型统计图例
    - 更鲜明的颜色区分
    - 可配置显示选项
    
    Args:
        request: 可视化请求
        
    Returns:
        标注后的图像路径
    """
    try:
        image_path = _safe_image_path(request.image_path)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="图像文件不存在")
        
        locator = AIElementLocator()
        output_path = _safe_image_path(request.output_path) if request.output_path else None
        output_path = locator.visualize_elements(
            image_path,
            output_path,
            show_labels=request.show_labels,
            show_center=request.show_center,
            min_confidence=request.min_confidence
        )
        
        # 将路径转换为URL友好格式
        url_output_path = output_path.replace("\\", "/")
        url_input_path = image_path.replace("\\", "/")
        
        return Response(
            message="可视化成功",
            data={
                "input_path": url_input_path,
                "output_path": url_output_path,
                "options": {
                    "show_labels": request.show_labels,
                    "show_center": request.show_center,
                    "min_confidence": request.min_confidence
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"可视化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/smart-click", response_model=Response[dict])
async def smart_click(
    image_path: str,
    query: str,
    device_id: Optional[int] = None
):
    """
    智能点击 - 一键完成：识别元素 + 生成命令 + 执行点击
    
    Args:
        image_path: 截图路径
        query: 元素查询条件
        device_id: 设备ID（可选）
        
    Returns:
        执行结果
    """
    try:
        image_path = _safe_image_path(image_path)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="图像文件不存在")
        
        # 1. 查找元素
        locator = AIElementLocator()
        element = locator.find_element(image_path, query)
        
        if not element:
            return Response(
                code=404,
                message=f"未找到匹配元素: {query}",
                data=None
            )
        
        # 2. 生成命令
        command = locator.generate_adb_command(image_path, 'click', query)
        
        if not command:
            return Response(
                code=500,
                message="无法生成点击命令",
                data=None
            )
        
        # 3. 执行命令（可选）
        execution_result = None
        if device_id:
            try:
                import subprocess
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                execution_result = {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            except HTTPException:
                raise
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise
                execution_result = {
                    "success": False,
                    "error": str(e)
                }
        
        return Response(
            message="智能点击完成",
            data={
                "element": element.to_dict(),
                "command": command,
                "execution": execution_result
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"智能点击失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capabilities", response_model=Response[dict])
async def get_capabilities(db: Session = Depends(get_session)):
    """
    获取AI元素定位器的能力信息
    
    Returns:
        能力信息
    """
    try:
        from sqlmodel import select
        from app.models import SystemConfig
        
        # 检查OCR配置
        ocr_available = False
        api_key_config = db.exec(
            select(SystemConfig).where(SystemConfig.config_key == "baidu_ocr_api_key")
        ).first()
        secret_key_config = db.exec(
            select(SystemConfig).where(SystemConfig.config_key == "baidu_ocr_secret_key")
        ).first()
        
        if api_key_config and secret_key_config:
            api_key = api_key_config.config_value
            secret_key = secret_key_config.config_value
            if api_key and secret_key:
                # 验证OCR配置
                try:
                    from app.services.ai_element_locator import OCREngine
                    ocr_engine = OCREngine(api_key, secret_key)
                    ocr_available = ocr_engine.is_available()
                except Exception as e:
                    logger.warning(f"OCR配置验证失败: {e}")
        
        capabilities = {
            "ocr_available": ocr_available,
            "ocr_provider": "百度OCR API" if ocr_available else None,
            "vision_available": True,  # OpenCV通常已安装
            "supported_actions": ["click", "input", "swipe"],
            "supported_element_types": ["button", "input", "text", "image", "icon", "checkbox", "radio", "switch"],
            "supported_query_methods": ["text", "description", "auto"]
        }
        
        return Response(
            message="能力信息获取成功",
            data=capabilities
        )
    except HTTPException:
        raise
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"获取能力信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/examples", response_model=Response[list])
async def get_examples():
    """
    获取使用示例
    
    Returns:
        示例列表
    """
    examples = [
        {
            "name": "查找登录按钮",
            "query": "登录",
            "method": "text",
            "description": "通过文本查找登录按钮"
        },
        {
            "name": "查找蓝色按钮",
            "query": "蓝色的提交按钮",
            "method": "description",
            "description": "通过自然语言描述查找按钮"
        },
        {
            "name": "查找输入框",
            "query": "请输入用户名",
            "method": "text",
            "description": "查找用户名输入框"
        },
        {
            "name": "智能点击",
            "query": "确认",
            "method": "auto",
            "description": "自动查找并点击确认按钮"
        }
    ]
    
    return Response(
        message="示例获取成功",
        data=examples
    )


# ==================== 新增API端点 ====================

class FindRelativeElementRequest(BaseModel):
    """查找相对位置元素请求"""
    image_path: str
    anchor_query: str  # 锚点元素查询
    direction: str  # left, right, top, bottom, above, below
    distance_threshold: int = 200


class FindInRegionRequest(BaseModel):
    """区域查找请求"""
    image_path: str
    region: List[int]  # [x1, y1, x2, y2]
    element_type: Optional[str] = None  # button, input, checkbox, etc.


class FilterByStateRequest(BaseModel):
    """按状态筛选请求"""
    image_path: str
    element_type: str  # checkbox, switch, radio
    state: str  # checked, unchecked, selected, normal


@router.post("/find-relative", response_model=Response[dict])
async def find_relative_element(request: FindRelativeElementRequest):
    """
    查找相对位置的元素
    
    支持的方向：
    - left/左边/左侧
    - right/右边/右侧
    - top/above/上方/上面
    - bottom/below/下方/下面
    
    示例：
    ```json
    {
        "image_path": "uploads/screenshots/xxx.png",
        "anchor_query": "登录",
        "direction": "right",
        "distance_threshold": 200
    }
    ```
    
    Returns:
        找到的元素信息
    """
    try:
        image_path = _safe_image_path(request.image_path)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="图像文件不存在")
        
        locator = AIElementLocator()
        
        # 1. 分析截图
        elements = locator.analyze_screenshot(image_path)
        
        # 2. 查找锚点元素
        anchor_element = locator.find_element(
            image_path,
            request.anchor_query,
            method="auto"
        )
        
        if not anchor_element:
            raise HTTPException(status_code=404, detail=f"未找到锚点元素: {request.anchor_query}")
        
        # 3. 查找相对位置的元素
        relative_element = locator.element_matcher.find_relative_element(
            anchor_element,
            request.direction,
            elements,
            request.distance_threshold
        )
        
        if not relative_element:
            raise HTTPException(
                status_code=404,
                detail=f"未找到{request.direction}方向的元素"
            )
        
        return Response(
            message="相对元素查找成功",
            data={
                "anchor": anchor_element.to_dict(),
                "relative": relative_element.to_dict(),
                "direction": request.direction
            }
        )
    
    except HTTPException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"相对元素查找失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/find-in-region", response_model=Response[dict])
async def find_in_region(request: FindInRegionRequest):
    """
    在指定区域内查找元素
    
    示例：
    ```json
    {
        "image_path": "uploads/screenshots/xxx.png",
        "region": [100, 100, 500, 500],
        "element_type": "button"
    }
    ```
    
    Returns:
        区域内的元素列表
    """
    try:
        image_path = _safe_image_path(request.image_path)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="图像文件不存在")
        
        if len(request.region) != 4:
            raise HTTPException(status_code=400, detail="区域坐标格式错误，应为[x1, y1, x2, y2]")
        
        locator = AIElementLocator()
        
        # 分析截图
        elements = locator.analyze_screenshot(image_path)
        
        # 在区域内查找
        region_elements = locator.element_matcher.find_in_region(
            tuple(request.region),
            elements
        )
        
        # 按类型筛选
        if request.element_type:
            region_elements = [
                e for e in region_elements
                if e.element_type.value == request.element_type
            ]
        
        return Response(
            message=f"在区域内找到 {len(region_elements)} 个元素",
            data={
                "region": request.region,
                "element_type": request.element_type,
                "count": len(region_elements),
                "elements": [e.to_dict() for e in region_elements]
            }
        )
    
    except HTTPException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"区域查找失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/filter-by-state", response_model=Response[dict])
async def filter_by_state(request: FilterByStateRequest):
    """
    按状态筛选元素
    
    支持的元素类型和状态：
    - checkbox: checked, unchecked
    - switch: checked, unchecked
    - radio: selected, normal
    
    示例：
    ```json
    {
        "image_path": "uploads/screenshots/xxx.png",
        "element_type": "checkbox",
        "state": "checked"
    }
    ```
    
    Returns:
        符合状态的元素列表
    """
    try:
        image_path = _safe_image_path(request.image_path)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="图像文件不存在")
        
        from app.services.ai_element_locator import ElementState, ElementType
        
        # 状态映射
        state_map = {
            "checked": ElementState.CHECKED,
            "unchecked": ElementState.UNCHECKED,
            "selected": ElementState.SELECTED,
            "normal": ElementState.NORMAL,
            "enabled": ElementState.ENABLED,
            "disabled": ElementState.DISABLED,
            "focused": ElementState.FOCUSED
        }
        
        if request.state not in state_map:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的状态: {request.state}"
            )
        
        target_state = state_map[request.state]
        
        locator = AIElementLocator()
        
        # 分析截图（检测所有类型）
        elements = locator.analyze_screenshot(image_path, detect_all=True)
        
        # 按类型筛选
        type_elements = [
            e for e in elements
            if e.element_type.value == request.element_type
        ]
        
        # 按状态筛选
        state_elements = locator.element_matcher.filter_by_state(
            type_elements,
            target_state
        )
        
        return Response(
            message=f"找到 {len(state_elements)} 个{request.state}状态的{request.element_type}",
            data={
                "element_type": request.element_type,
                "state": request.state,
                "count": len(state_elements),
                "elements": [e.to_dict() for e in state_elements]
            }
        )
    
    except HTTPException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"状态筛选失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/element-types", response_model=Response[list])
async def get_element_types():
    """
    获取支持的元素类型列表
    
    Returns:
        元素类型列表
    """
    from app.services.ai_element_locator import ElementType
    
    types = [
        {
            "value": elem_type.value,
            "name": elem_type.name,
            "description": _get_type_description(elem_type.value)
        }
        for elem_type in ElementType
    ]
    
    return Response(
        message="元素类型获取成功",
        data=types
    )


@router.get("/element-states", response_model=Response[list])
async def get_element_states():
    """
    获取支持的元素状态列表
    
    Returns:
        元素状态列表
    """
    from app.services.ai_element_locator import ElementState
    
    states = [
        {
            "value": state.value,
            "name": state.name,
            "description": _get_state_description(state.value)
        }
        for state in ElementState
    ]
    
    return Response(
        message="元素状态获取成功",
        data=states
    )


def _get_type_description(type_value: str) -> str:
    """获取元素类型描述"""
    descriptions = {
        "button": "按钮元素",
        "input": "输入框元素",
        "text": "文本元素",
        "image": "图像元素",
        "icon": "图标元素",
        "checkbox": "复选框元素",
        "radio": "单选按钮元素",
        "switch": "开关元素",
        "slider": "滑块元素",
        "dropdown": "下拉菜单元素",
        "tab": "标签页元素",
        "unknown": "未知类型元素"
    }
    return descriptions.get(type_value, "未知")


def _get_state_description(state_value: str) -> str:
    """获取元素状态描述"""
    descriptions = {
        "normal": "正常状态",
        "checked": "选中状态",
        "unchecked": "未选中状态",
        "enabled": "启用状态",
        "disabled": "禁用状态",
        "focused": "聚焦状态",
        "selected": "选择状态",
        "loading": "加载状态",
        "unknown": "未知状态"
    }
    return descriptions.get(state_value, "未知")
