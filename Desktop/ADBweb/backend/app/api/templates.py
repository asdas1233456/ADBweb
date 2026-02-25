"""
模板市场API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime
from app.core.database import get_session
from app.models.template import Template
from app.models.script import Script
from app.schemas.common import Response, PaginatedResponse
from pydantic import BaseModel

router = APIRouter(prefix="/templates", tags=["模板市场"])


class TemplateCreate(BaseModel):
    """创建模板请求模型"""
    name: str
    description: str
    author: str = "系统"
    category: str = "other"
    type: str = "visual"
    tags: Optional[str] = None
    content: str
    preview: Optional[str] = None
    is_featured: bool = False


class TemplateUpdate(BaseModel):
    """更新模板请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    tags: Optional[str] = None
    content: Optional[str] = None
    preview: Optional[str] = None
    is_featured: Optional[bool] = None


class TemplateDownload(BaseModel):
    """下载模板请求模型"""
    script_name: str
    category: str = "other"


@router.get("", response_model=Response[PaginatedResponse])
async def get_templates(
    category: Optional[str] = None,
    type: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: Optional[str] = "downloads",
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_session)
):
    """获取模板列表"""
    query = select(Template)
    
    if category:
        query = query.where(Template.category == category)
    if type:
        query = query.where(Template.type == type)
    if keyword:
        query = query.where(Template.name.contains(keyword))
    
    # 排序
    if sort_by == "downloads":
        query = query.order_by(Template.downloads.desc())
    elif sort_by == "rating":
        query = query.order_by(Template.rating.desc())
    
    # 计算总数
    total = len(db.exec(query).all())
    
    # 分页
    offset = (page - 1) * page_size
    templates = db.exec(query.offset(offset).limit(page_size)).all()
    
    return Response(data={
        "items": templates,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    })


@router.get("/{template_id}", response_model=Response[Template])
async def get_template(template_id: int, db: Session = Depends(get_session)):
    """获取模板详情"""
    template = db.get(Template, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return Response(data=template)


@router.post("", response_model=Response[Template])
async def create_template(template_data: TemplateCreate, db: Session = Depends(get_session)):
    """创建模板"""
    template = Template(**template_data.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return Response(message="模板创建成功", data=template)


@router.put("/{template_id}", response_model=Response[Template])
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    db: Session = Depends(get_session)
):
    """更新模板"""
    template = db.get(Template, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 更新字段
    for key, value in template_data.model_dump(exclude_unset=True).items():
        setattr(template, key, value)
    
    template.updated_at = datetime.now()
    db.add(template)
    db.commit()
    db.refresh(template)
    return Response(message="模板更新成功", data=template)


@router.delete("/{template_id}", response_model=Response)
async def delete_template(template_id: int, db: Session = Depends(get_session)):
    """删除模板"""
    template = db.get(Template, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    db.delete(template)
    db.commit()
    return Response(message="模板删除成功")


@router.post("/{template_id}/download", response_model=Response)
async def download_template(
    template_id: int,
    download_data: TemplateDownload,
    db: Session = Depends(get_session)
):
    """下载模板（转为脚本）"""
    template = db.get(Template, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 处理 steps_json 数据
    steps_json = None
    if template.type == "visual" and template.content:
        try:
            import json
            parsed_content = json.loads(template.content)
            # 如果是对象且包含 steps 键，提取 steps 数组
            if isinstance(parsed_content, dict) and 'steps' in parsed_content:
                steps_json = json.dumps(parsed_content['steps'])
            elif isinstance(parsed_content, list):
                steps_json = template.content
            else:
                steps_json = "[]"
        except json.JSONDecodeError:
            steps_json = "[]"
    
    # 创建新脚本
    script = Script(
        name=download_data.script_name,
        type=template.type,
        category=download_data.category,
        description=template.description,
        file_content=template.content if template.type in ["python", "batch"] else None,
        steps_json=steps_json
    )
    db.add(script)
    
    # 增加下载次数
    template.downloads += 1
    db.add(template)
    
    db.commit()
    db.refresh(script)
    
    return Response(
        message="模板下载成功，已添加到脚本列表",
        data={"id": script.id, "script_id": script.id, "script_name": script.name}
    )
