"""
测试报告导出API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Response as FastAPIResponse
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from app.core.database import get_session
from app.schemas.common import Response
from app.services.report_export_service import ReportExportService
from pydantic import BaseModel
from typing import List
import logging
from io import BytesIO

router = APIRouter(prefix="/report-export", tags=["报告导出"])
logger = logging.getLogger(__name__)


class ExportRequest(BaseModel):
    """导出请求"""
    task_log_ids: List[int]
    format: str  # excel, pdf, json, html
    include_details: bool = True


@router.post("/export")
async def export_report(
    request: ExportRequest,
    db: Session = Depends(get_session)
):
    """
    导出测试报告
    
    Args:
        request: 导出请求
        
    Returns:
        文件流或JSON数据
    """
    try:
        service = ReportExportService(db)
        
        if request.format == "excel":
            output = service.export_to_excel(request.task_log_ids, request.include_details)
            return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=test_report_{len(request.task_log_ids)}.xlsx"
                }
            )
        
        elif request.format == "pdf":
            output = service.export_to_pdf(request.task_log_ids, request.include_details)
            return StreamingResponse(
                output,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=test_report_{len(request.task_log_ids)}.pdf"
                }
            )
        
        elif request.format == "json":
            json_data = service.export_to_json(request.task_log_ids, request.include_details)
            return FastAPIResponse(
                content=json_data,
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=test_report_{len(request.task_log_ids)}.json"
                }
            )
        
        elif request.format == "html":
            html_data = service.export_to_html(request.task_log_ids)
            return FastAPIResponse(
                content=html_data,
                media_type="text/html",
                headers={
                    "Content-Disposition": f"attachment; filename=test_report_{len(request.task_log_ids)}.html"
                }
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"不支持的导出格式: {request.format}")
    
    except ImportError as e:
        logger.error(f"导出报告失败，缺少依赖库: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"导出失败，请安装必要的依赖库: {str(e)}"
        )
    except Exception as e:
        logger.error(f"导出报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/formats", response_model=Response[list])
async def get_export_formats():
    """
    获取支持的导出格式
    
    Returns:
        支持的格式列表
    """
    formats = [
        {
            "value": "excel",
            "label": "Excel (.xlsx)",
            "description": "Excel表格格式，支持多工作表和图表",
            "icon": "📊"
        },
        {
            "value": "pdf",
            "label": "PDF (.pdf)",
            "description": "PDF文档格式，适合打印和分享",
            "icon": "📄"
        },
        {
            "value": "json",
            "label": "JSON (.json)",
            "description": "JSON数据格式，适合程序处理",
            "icon": "📋"
        },
        {
            "value": "html",
            "label": "HTML (.html)",
            "description": "HTML网页格式，可在浏览器中查看",
            "icon": "🌐"
        }
    ]
    
    return Response(data=formats)
