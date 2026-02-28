"""
脚本模板API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_session
from app.models.script_template import ScriptTemplate
from app.services.template_service import TemplateService
from app.schemas.common import Response

router = APIRouter(prefix="/script-templates", tags=["脚本模板"])


class TemplateCreateRequest(BaseModel):
    """创建模板请求"""
    name: str
    category: str
    description: Optional[str] = None
    language: str = "adb"
    template_content: str
    variables: Optional[dict] = None
    tags: Optional[List[str]] = None


class TemplateUseRequest(BaseModel):
    """使用模板请求"""
    template_id: int
    variables: Optional[dict] = None


class TemplateResponse(BaseModel):
    """模板响应"""
    id: int
    name: str
    category: str
    description: Optional[str]
    language: str
    template_content: str
    variables: Optional[dict]
    tags: Optional[List[str]]
    usage_count: int
    is_builtin: bool
    created_by: str
    created_at: str


@router.get("", response_model=Response[List[TemplateResponse]])
async def get_templates(
    category: Optional[str] = None,
    language: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 20,
    session: Session = Depends(get_session)
):
    """获取模板列表"""
    service = TemplateService(session)
    templates = service.get_templates(category, language, keyword, limit)
    
    result = []
    for template in templates:
        # 解析变量和标签
        import json
        variables = None
        if template.variables:
            try:
                variables = json.loads(template.variables)
            except:
                pass
        
        tags = None
        if template.tags:
            tags = template.tags.split(",")
        
        result.append(TemplateResponse(
            id=template.id,
            name=template.name,
            category=template.category,
            description=template.description,
            language=template.language,
            template_content=template.template_content,
            variables=variables,
            tags=tags,
            usage_count=template.usage_count,
            is_builtin=template.is_builtin,
            created_by=template.created_by,
            created_at=template.created_at.isoformat()
        ))
    
    return Response(data=result)


@router.get("/categories", response_model=Response[List[dict]])
async def get_categories(session: Session = Depends(get_session)):
    """获取模板分类"""
    service = TemplateService(session)
    categories = service.get_categories()
    return Response(data=categories)


@router.get("/{template_id}", response_model=Response[TemplateResponse])
async def get_template(template_id: int, session: Session = Depends(get_session)):
    """获取单个模板"""
    service = TemplateService(session)
    template = service.get_template(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 解析变量和标签
    import json
    variables = None
    if template.variables:
        try:
            variables = json.loads(template.variables)
        except:
            pass
    
    tags = None
    if template.tags:
        tags = template.tags.split(",")
    
    result = TemplateResponse(
        id=template.id,
        name=template.name,
        category=template.category,
        description=template.description,
        language=template.language,
        template_content=template.template_content,
        variables=variables,
        tags=tags,
        usage_count=template.usage_count,
        is_builtin=template.is_builtin,
        created_by=template.created_by,
        created_at=template.created_at.isoformat()
    )
    
    return Response(data=result)


@router.post("/use", response_model=Response[dict])
async def use_template(
    request: TemplateUseRequest,
    session: Session = Depends(get_session)
):
    """使用模板生成脚本"""
    try:
        service = TemplateService(session)
        content = service.use_template(request.template_id, request.variables)
        
        return Response(
            message="模板使用成功",
            data={"content": content}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"使用模板失败: {str(e)}")


@router.post("", response_model=Response[TemplateResponse])
async def create_template(
    request: TemplateCreateRequest,
    session: Session = Depends(get_session)
):
    """创建模板"""
    try:
        service = TemplateService(session)
        
        # 如果没有提供变量，尝试从内容中提取
        variables = request.variables
        if not variables:
            variables = service.extract_variables(request.template_content)
        
        template = service.create_template(
            name=request.name,
            category=request.category,
            template_content=request.template_content,
            language=request.language,
            description=request.description,
            variables=variables,
            tags=request.tags,
            created_by="user"
        )
        
        # 解析变量和标签
        import json
        parsed_variables = None
        if template.variables:
            try:
                parsed_variables = json.loads(template.variables)
            except:
                pass
        
        parsed_tags = None
        if template.tags:
            parsed_tags = template.tags.split(",")
        
        result = TemplateResponse(
            id=template.id,
            name=template.name,
            category=template.category,
            description=template.description,
            language=template.language,
            template_content=template.template_content,
            variables=parsed_variables,
            tags=parsed_tags,
            usage_count=template.usage_count,
            is_builtin=template.is_builtin,
            created_by=template.created_by,
            created_at=template.created_at.isoformat()
        )
        
        return Response(message="模板创建成功", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建模板失败: {str(e)}")


@router.delete("/{template_id}", response_model=Response[dict])
async def delete_template(template_id: int, session: Session = Depends(get_session)):
    """删除模板"""
    template = session.get(ScriptTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    if template.is_builtin:
        raise HTTPException(status_code=400, detail="不能删除内置模板")
    
    template.is_active = False
    session.add(template)
    session.commit()
    
    return Response(message="模板删除成功", data={"id": template_id})