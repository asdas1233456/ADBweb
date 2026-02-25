"""
定时任务调度服务
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session, select
from app.models import ScheduledTask
from app.core.database import engine
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SchedulerService:
    """定时任务调度器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler(daemon=True)
        self.scheduler.start()
        logger.info("定时任务调度器已启动")
    
    def add_task(self, task: ScheduledTask):
        """添加定时任务"""
        try:
            job_id = f"scheduled_task_{task.id}"
            
            # 解析执行时间
            hour, minute = task.schedule_time.split(":")[:2]
            
            # 根据频率创建触发器
            if task.frequency == "daily":
                trigger = CronTrigger(hour=int(hour), minute=int(minute))
            elif task.frequency == "weekly":
                # schedule_day 应该是 Monday, Tuesday 等
                day_of_week = task.schedule_day.lower() if task.schedule_day else "mon"
                trigger = CronTrigger(day_of_week=day_of_week, hour=int(hour), minute=int(minute))
            elif task.frequency == "monthly":
                # schedule_day 应该是 1-31
                day = int(task.schedule_day) if task.schedule_day else 1
                trigger = CronTrigger(day=day, hour=int(hour), minute=int(minute))
            else:
                logger.error(f"不支持的频率类型: {task.frequency}")
                return
            
            # 添加任务到调度器
            self.scheduler.add_job(
                func=self._execute_task,
                trigger=trigger,
                id=job_id,
                args=[task.id],
                replace_existing=True
            )
            
            logger.info(f"定时任务已添加: {task.name} (ID: {task.id})")
            
        except Exception as e:
            logger.error(f"添加定时任务失败: {e}")
    
    def remove_task(self, task_id: int):
        """移除定时任务"""
        try:
            job_id = f"scheduled_task_{task_id}"
            self.scheduler.remove_job(job_id)
            logger.info(f"定时任务已移除: ID {task_id}")
        except Exception as e:
            logger.error(f"移除定时任务失败: {e}")
    
    def pause_task(self, task_id: int):
        """暂停定时任务"""
        try:
            job_id = f"scheduled_task_{task_id}"
            self.scheduler.pause_job(job_id)
            logger.info(f"定时任务已暂停: ID {task_id}")
        except Exception as e:
            logger.error(f"暂停定时任务失败: {e}")
    
    def resume_task(self, task_id: int):
        """恢复定时任务"""
        try:
            job_id = f"scheduled_task_{task_id}"
            self.scheduler.resume_job(job_id)
            logger.info(f"定时任务已恢复: ID {task_id}")
        except Exception as e:
            logger.error(f"恢复定时任务失败: {e}")
    
    def _execute_task(self, task_id: int):
        """执行定时任务"""
        logger.info(f"开始执行定时任务: ID {task_id}")
        
        with Session(engine) as db:
            task = db.get(ScheduledTask, task_id)
            if not task or not task.is_enabled:
                logger.warning(f"定时任务不存在或已禁用: ID {task_id}")
                return
            
            # 更新任务统计
            task.last_run_at = datetime.now()
            task.run_count += 1
            
            # 计算下次运行时间
            task.next_run_at = self._calculate_next_run(task)
            
            db.add(task)
            db.commit()
            
            # TODO: 调用脚本执行服务
            logger.info(f"定时任务执行完成: {task.name}")
    
    def _calculate_next_run(self, task: ScheduledTask) -> datetime:
        """计算下次运行时间"""
        now = datetime.now()
        hour, minute = map(int, task.schedule_time.split(":")[:2])
        
        if task.frequency == "daily":
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        elif task.frequency == "weekly":
            # 简化处理，加7天
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            next_run += timedelta(days=7)
        elif task.frequency == "monthly":
            # 简化处理，加30天
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            next_run += timedelta(days=30)
        else:
            next_run = now + timedelta(days=1)
        
        return next_run
    
    def load_tasks_from_db(self):
        """从数据库加载所有启用的定时任务"""
        try:
            with Session(engine) as db:
                tasks = db.exec(
                    select(ScheduledTask).where(ScheduledTask.is_enabled == True)
                ).all()
                
                for task in tasks:
                    self.add_task(task)
                
                logger.info(f"已加载 {len(tasks)} 个定时任务")
        except Exception as e:
            logger.error(f"加载定时任务失败: {e}")
    
    def shutdown(self):
        """关闭调度器"""
        self.scheduler.shutdown()
        logger.info("定时任务调度器已关闭")


# 全局调度器实例
scheduler_service = SchedulerService()
