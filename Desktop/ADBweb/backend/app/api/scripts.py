"""
脚本管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from typing import Optional
from app.core.database import get_session
from app.models.script import Script
from app.schemas.common import Response, PaginatedResponse
from pydantic import BaseModel

router = APIRouter(prefix="/scripts", tags=["脚本管理"])


class ScriptCreate(BaseModel):
    """创建脚本请求模型"""
    name: str
    type: str = "visual"
    category: str = "other"
    description: Optional[str] = None
    file_path: Optional[str] = None
    file_content: Optional[str] = None
    steps_json: Optional[str] = None


class ScriptUpdate(BaseModel):
    """更新脚本请求模型"""
    name: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    file_path: Optional[str] = None
    file_content: Optional[str] = None
    steps_json: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("", response_model=Response[PaginatedResponse])
async def get_scripts(
    type: Optional[str] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_session)
):
    """获取脚本列表"""
    query = select(Script).where(Script.is_active == True)
    
    if type:
        query = query.where(Script.type == type)
    if category:
        query = query.where(Script.category == category)
    if keyword:
        query = query.where(Script.name.contains(keyword))
    
    # 优化：使用count查询计算总数
    count_query = select(func.count(Script.id)).where(Script.is_active == True)
    if type:
        count_query = count_query.where(Script.type == type)
    if category:
        count_query = count_query.where(Script.category == category)
    if keyword:
        count_query = count_query.where(Script.name.contains(keyword))
    total = db.exec(count_query).one()
    
    # 分页查询，按更新时间倒序
    offset = (page - 1) * page_size
    query = query.order_by(Script.updated_at.desc()).offset(offset).limit(page_size)
    scripts = db.exec(query).all()
    
    return Response(data={
        "items": scripts,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    })


@router.get("/{script_id}", response_model=Response[Script])
async def get_script(script_id: int, db: Session = Depends(get_session)):
    """获取脚本详情"""
    script = db.get(Script, script_id)
    if not script or not script.is_active:
        raise HTTPException(status_code=404, detail="脚本不存在")
    return Response(data=script)


@router.post("", response_model=Response[Script])
async def create_script(script_data: ScriptCreate, db: Session = Depends(get_session)):
    """创建脚本"""
    script = Script(**script_data.model_dump())
    db.add(script)
    db.commit()
    db.refresh(script)
    return Response(message="脚本创建成功", data=script)


@router.put("/{script_id}", response_model=Response[Script])
async def update_script(
    script_id: int,
    script_data: ScriptUpdate,
    db: Session = Depends(get_session)
):
    """更新脚本"""
    script = db.get(Script, script_id)
    if not script or not script.is_active:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    # 更新字段
    for key, value in script_data.model_dump(exclude_unset=True).items():
        setattr(script, key, value)
    
    db.add(script)
    db.commit()
    db.refresh(script)
    return Response(message="脚本更新成功", data=script)


@router.delete("/{script_id}", response_model=Response)
async def delete_script(script_id: int, db: Session = Depends(get_session)):
    """删除脚本（软删除）"""
    script = db.get(Script, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    script.is_active = False
    db.add(script)
    db.commit()
    return Response(message="脚本删除成功")



class ScriptValidateRequest(BaseModel):
    """脚本验证请求模型"""
    script_type: str
    content: str
    filename: Optional[str] = "script"


@router.post("/validate", response_model=Response)
async def validate_script(request: ScriptValidateRequest):
    """
    验证脚本
    
    参数:
    - script_type: 脚本类型 (python/batch/visual)
    - content: 脚本内容
    - filename: 文件名（可选）
    """
    from app.utils.script_validator import validator
    
    try:
        # 根据类型选择验证方法
        if request.script_type == "python":
            result = validator.validate_python(request.content, request.filename)
        elif request.script_type == "batch":
            result = validator.validate_batch(request.content)
        elif request.script_type == "visual":
            result = validator.validate_visual(request.content)
        else:
            raise HTTPException(status_code=400, detail="不支持的脚本类型")
        
        # 转换为字典格式
        return Response(
            message="验证完成",
            data={
                "passed": result.passed,
                "score": result.score,
                "items": [
                    {
                        "name": item.name,
                        "level": item.level,
                        "message": item.message,
                        "details": item.details
                    }
                    for item in result.items
                ],
                "suggestions": result.suggestions
            }
        )
    except Exception as e:
        return Response(
            code=500,
            message=f"验证失败: {str(e)}",
            data=None
        )
