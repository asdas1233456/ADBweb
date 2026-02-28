"""
报告中心API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime
from app.core.database import get_session
from app.models.task_log import TaskLog
from app.models.script import Script
from app.models.device import Device
from app.schemas.common import Response, PaginatedResponse

router = APIRouter(prefix="/reports", tags=["报告中心"])


@router.get("", response_model=Response[PaginatedResponse])
async def get_reports(
    status: Optional[str] = None,
    device_id: Optional[int] = None,
    script_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_session)
):
    """获取报告列表"""
    query = select(TaskLog).order_by(TaskLog.start_time.desc())
    
    if status and status != 'undefined':
        query = query.where(TaskLog.status == status)
    if device_id:
        query = query.where(TaskLog.device_id == device_id)
    if script_id:
        query = query.where(TaskLog.script_id == script_id)
    if start_date and start_date != 'undefined':
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.where(TaskLog.start_time >= start_dt)
        except ValueError:
            pass  # 忽略无效的日期格式
    if end_date and end_date != 'undefined':
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.where(TaskLog.start_time <= end_dt)
        except ValueError:
            pass  # 忽略无效的日期格式
    
    # 计算总数
    total = len(db.exec(query).all())
    
    # 分页
    offset = (page - 1) * page_size
    reports = db.exec(query.offset(offset).limit(page_size)).all()
    
    # 构建响应数据（包含关联的脚本和设备名称）
    items = []
    for report in reports:
        item = report.model_dump()
        if report.script_id:
            script = db.get(Script, report.script_id)
            item["script_name"] = script.name if script else None
        if report.device_id:
            device = db.get(Device, report.device_id)
            item["device_name"] = device.model if device else None
        items.append(item)
    
    return Response(data={
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    })


@router.get("/{report_id}", response_model=Response[TaskLog])
async def get_report_detail(report_id: int, db: Session = Depends(get_session)):
    """获取报告详情"""
    report = db.get(TaskLog, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    return Response(data=report)


@router.delete("/batch-delete", response_model=Response)
async def batch_delete_reports(
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_session)
):
    """批量删除报告"""
    # 至少需要一个删除条件
    if not status and not start_date and not end_date:
        raise HTTPException(status_code=400, detail="至少需要选择一个删除条件")
    
    query = select(TaskLog)
    
    if status and status != 'undefined':
        query = query.where(TaskLog.status == status)
    if start_date and start_date != 'undefined':
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.where(TaskLog.start_time >= start_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="开始日期格式无效")
    if end_date and end_date != 'undefined':
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            # 结束日期包含当天的23:59:59
            from datetime import timedelta
            end_dt = end_dt + timedelta(days=1) - timedelta(seconds=1)
            query = query.where(TaskLog.start_time <= end_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="结束日期格式无效")
    
    # 获取要删除的报告
    reports_to_delete = db.exec(query).all()
    
    if not reports_to_delete:
        return Response(message="没有符合条件的报告需要删除", data={"deleted_count": 0})
    
    # 批量删除
    deleted_count = 0
    for report in reports_to_delete:
        db.delete(report)
        deleted_count += 1
    
    db.commit()
    
    return Response(
        message=f"成功删除 {deleted_count} 条报告",
        data={"deleted_count": deleted_count}
    )


@router.delete("/{report_id}", response_model=Response)
async def delete_report(report_id: int, db: Session = Depends(get_session)):
    """删除报告"""
    report = db.get(TaskLog, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    db.delete(report)
    db.commit()
    
    return Response(message="报告删除成功")

