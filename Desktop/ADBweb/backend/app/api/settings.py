"""
系统设置API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import SystemConfig
from app.schemas.common import Response
from app.utils.adb_scanner import scan_adb_paths, scan_python_paths
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime

router = APIRouter(prefix="/settings", tags=["系统设置"])


class ConfigUpdate(BaseModel):
    """配置更新"""
    config_value: str


@router.get("", response_model=Response[Dict[str, str]])
async def get_settings(db: Session = Depends(get_session)):
    """获取所有系统配置"""
    configs = db.exec(select(SystemConfig)).all()
    
    # 转换为字典格式
    settings_dict = {
        config.config_key: config.config_value
        for config in configs
    }
    
    return Response(data=settings_dict)


@router.put("", response_model=Response)
async def update_settings(
    settings_data: Dict[str, str],
    db: Session = Depends(get_session)
):
    """批量更新系统配置"""
    for key, value in settings_data.items():
        config = db.exec(
            select(SystemConfig).where(SystemConfig.config_key == key)
        ).first()
        
        if config:
            config.config_value = value
            config.updated_at = datetime.now()
            db.add(config)
    
    db.commit()
    return Response(message="配置已保存")


@router.get("/{config_key}", response_model=Response[SystemConfig])
async def get_config(config_key: str, db: Session = Depends(get_session)):
    """获取单个配置项"""
    config = db.exec(
        select(SystemConfig).where(SystemConfig.config_key == config_key)
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置项不存在")
    
    return Response(data=config)


@router.put("/{config_key}", response_model=Response)
async def update_config(
    config_key: str,
    config_data: ConfigUpdate,
    db: Session = Depends(get_session)
):
    """更新单个配置项"""
    config = db.exec(
        select(SystemConfig).where(SystemConfig.config_key == config_key)
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置项不存在")
    
    config.config_value = config_data.config_value
    config.updated_at = datetime.now()
    db.add(config)
    db.commit()
    
    return Response(message="配置已更新")


@router.get("/scan/adb-paths", response_model=Response[List[Dict[str, str]]])
async def scan_adb():
    """扫描系统中的ADB路径"""
    try:
        paths = scan_adb_paths()
        return Response(
            message=f"找到 {len(paths)} 个ADB路径" if paths else "未找到ADB路径",
            data=paths
        )
    except Exception as e:
        return Response(
            code=500,
            message=f"扫描失败: {str(e)}",
            data=[]
        )


@router.get("/scan/python-paths", response_model=Response[List[Dict[str, str]]])
async def scan_python():
    """扫描系统中的Python路径"""
    try:
        paths = scan_python_paths()
        return Response(
            message=f"找到 {len(paths)} 个Python路径" if paths else "未找到Python路径",
            data=paths
        )
    except Exception as e:
        return Response(
            code=500,
            message=f"扫描失败: {str(e)}",
            data=[]
        )
