"""
AI脚本生成API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_session
from app.models.ai_script import AIScript
from app.services.ai_script_generator import AIScriptGenerator
from app.schemas.common import Response

router = APIRouter(prefix="/ai-script", tags=["AI脚本生成"])


class ScriptGenerateRequest(BaseModel):
    """脚本生成请求"""
    prompt: str
    language: str = "adb"  # adb 或 python
    device_model: Optional[str] = None
    ai_api_key: Optional[str] = None  # AI API密钥（可选）
    ai_api_base: Optional[str] = None  # AI API基础URL（可选）


class ScriptGenerateResponse(BaseModel):
    """脚本生成响应"""
    id: int
    prompt: str
    generated_script: str
    language: str
    optimization_suggestions: List[dict]
    device_model: Optional[str]
    generation_mode: str = "rule_engine"  # 生成模式: ai 或 rule_engine
    ai_model: Optional[str] = None  # AI模型名称（如果使用AI）


@router.post("/generate", response_model=Response[ScriptGenerateResponse])
async def generate_script(
    request: ScriptGenerateRequest,
    session: Session = Depends(get_session)
):
    """
    生成测试脚本
    
    根据自然语言描述生成ADB或Python测试脚本
    """
    try:
        # 使用AI生成器生成脚本
        generator = AIScriptGenerator(
            api_key=request.ai_api_key,
            api_base=request.ai_api_base
        )
        script = generator.generate_script(request.prompt, request.language)
        
        # 优化建议
        suggestions = generator.optimize_script(script)
        
        # 确定生成模式
        generation_mode = "ai" if generator.use_ai else "rule_engine"
        ai_model = "deepseek-chat" if generator.use_ai else None
        
        # 保存到数据库
        ai_script = AIScript(
            prompt=request.prompt,
            generated_script=script,
            language=request.language,
            optimization_suggestions=str(suggestions),
            device_model=request.device_model,
            status="success"
        )
        session.add(ai_script)
        session.commit()
        session.refresh(ai_script)
        
        result = ScriptGenerateResponse(
            id=ai_script.id,
            prompt=ai_script.prompt,
            generated_script=ai_script.generated_script,
            language=ai_script.language,
            optimization_suggestions=suggestions,
            device_model=ai_script.device_model,
            generation_mode=generation_mode,
            ai_model=ai_model
        )
        
        return Response(data=result)
    except Exception as e:
        # 记录失败
        ai_script = AIScript(
            prompt=request.prompt,
            generated_script="",
            language=request.language,
            device_model=request.device_model,
            status="failed",
            error_message=str(e)
        )
        session.add(ai_script)
        session.commit()
        
        raise HTTPException(status_code=500, detail=f"脚本生成失败: {str(e)}")


class PromptOptimizeRequest(BaseModel):
    """提示词优化请求"""
    prompt: str
    language: str = "adb"
    ai_api_key: Optional[str] = None  # AI API密钥（可选）
    ai_api_base: Optional[str] = None  # AI API基础URL（可选）


class PromptOptimizeResponse(BaseModel):
    """提示词优化响应"""
    original_prompt: str
    optimized_prompt: str
    improvements: List[str]
    missing_info: List[str]


@router.post("/optimize-prompt", response_model=Response[PromptOptimizeResponse])
async def optimize_prompt(
    request: PromptOptimizeRequest
):
    """
    优化提示词
    
    分析用户输入的提示词，提供改进建议和优化后的版本
    """
    try:
        # 使用传入的AI配置创建生成器
        generator = AIScriptGenerator(
            api_key=request.ai_api_key,
            api_base=request.ai_api_base
        )
        result = generator.optimize_prompt(request.prompt, request.language)
        
        response = PromptOptimizeResponse(
            original_prompt=result["original_prompt"],
            optimized_prompt=result["optimized_prompt"],
            improvements=result["improvements"],
            missing_info=result["missing_info"]
        )
        
        return Response(data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提示词优化失败: {str(e)}")


class ScriptSaveRequest(BaseModel):
    """保存脚本请求"""
    ai_script_id: int
    name: str
    category: str = "automation"
    description: Optional[str] = None


@router.post("/save-to-scripts", response_model=Response[dict])
async def save_to_scripts(
    request: ScriptSaveRequest,
    session: Session = Depends(get_session)
):
    """
    将AI生成的脚本保存到脚本管理
    """
    try:
        # 获取AI脚本记录
        ai_script = session.get(AIScript, request.ai_script_id)
        if not ai_script:
            raise HTTPException(status_code=404, detail="AI脚本记录不存在")
        
        # 创建脚本记录
        from app.models.script import Script
        script = Script(
            name=request.name,
            type="python" if ai_script.language == "python" else "batch",
            category=request.category,
            description=request.description or ai_script.prompt,
            file_content=ai_script.generated_script,
            is_active=True
        )
        
        session.add(script)
        session.commit()
        session.refresh(script)
        
        return Response(
            message="脚本保存成功",
            data={
                "script_id": script.id,
                "name": script.name,
                "type": script.type,
                "category": script.category
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存脚本失败: {str(e)}")


@router.post("/validate-generated", response_model=Response[dict])
async def validate_generated_script(
    ai_script_id: int,
    session: Session = Depends(get_session)
):
    """
    验证AI生成的脚本
    """
    try:
        # 获取AI脚本记录
        ai_script = session.get(AIScript, ai_script_id)
        if not ai_script:
            raise HTTPException(status_code=404, detail="AI脚本记录不存在")
        
        # 使用脚本验证器
        from app.utils.script_validator import validator
        
        if ai_script.language == "python":
            result = validator.validate_python(ai_script.generated_script)
        elif ai_script.language == "adb":
            # ADB脚本按batch处理
            result = validator.validate_batch(ai_script.generated_script)
        else:
            raise HTTPException(status_code=400, detail="不支持的脚本类型")
        
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
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")


class BatchGenerateRequest(BaseModel):
    """批量生成请求"""
    prompts: List[str]
    language: str = "adb"
    generate_suite: bool = False
    ai_api_key: Optional[str] = None
    ai_api_base: Optional[str] = None


class WorkflowGenerateRequest(BaseModel):
    """工作流生成请求"""
    workflow_steps: List[str]
    language: str = "adb"
    ai_api_key: Optional[str] = None
    ai_api_base: Optional[str] = None


@router.post("/batch-generate", response_model=Response[dict])
async def batch_generate_scripts(
    request: BatchGenerateRequest,
    session: Session = Depends(get_session)
):
    """
    批量生成脚本
    
    支持同时生成多个脚本，可选择生成测试套件
    """
    try:
        from app.services.batch_generator import BatchScriptGenerator
        
        generator = BatchScriptGenerator(
            session=session,
            api_key=request.ai_api_key,
            api_base=request.ai_api_base
        )
        
        result = await generator.generate_batch_scripts(
            prompts=request.prompts,
            language=request.language,
            generate_suite=request.generate_suite
        )
        
        return Response(
            message=f"批量生成完成，成功 {result['statistics']['success']} 个，失败 {result['statistics']['failed']} 个",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量生成失败: {str(e)}")


@router.post("/workflow-generate", response_model=Response[dict])
def generate_workflow_scripts(
    request: WorkflowGenerateRequest,
    session: Session = Depends(get_session)
):
    """
    生成工作流脚本
    
    生成有步骤依赖关系的工作流脚本
    """
    try:
        from app.services.batch_generator import BatchScriptGenerator
        
        generator = BatchScriptGenerator(
            session=session,
            api_key=request.ai_api_key,
            api_base=request.ai_api_base
        )
        
        result = generator.generate_workflow_scripts(
            workflow_steps=request.workflow_steps,
            language=request.language
        )
        
        return Response(
            message=f"工作流生成完成，包含 {len(request.workflow_steps)} 个步骤",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"工作流生成失败: {str(e)}")


@router.get("/history", response_model=Response[List[ScriptGenerateResponse]])
async def get_history(
    limit: int = 10,
    session: Session = Depends(get_session)
):
    """
    获取脚本生成历史
    """
    statement = select(AIScript).order_by(AIScript.created_at.desc()).limit(limit)
    scripts = session.exec(statement).all()
    
    result = []
    for script in scripts:
        # 解析优化建议
        try:
            suggestions = eval(script.optimization_suggestions) if script.optimization_suggestions else []
        except:
            suggestions = []
        
        result.append(ScriptGenerateResponse(
            id=script.id,
            prompt=script.prompt,
            generated_script=script.generated_script,
            language=script.language,
            optimization_suggestions=suggestions,
            device_model=script.device_model
        ))
    
    return Response(data=result)


@router.delete("/{script_id}", response_model=Response[dict])
async def delete_script(
    script_id: int,
    session: Session = Depends(get_session)
):
    """删除脚本记录"""
    script = session.get(AIScript, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="脚本记录不存在")
    
    session.delete(script)
    session.commit()
    
    return Response(data={"message": "删除成功"})
