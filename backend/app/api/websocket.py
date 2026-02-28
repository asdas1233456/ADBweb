"""
WebSocket API 路由
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager
import json

router = APIRouter()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket 连接端点"""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理订阅请求
            if message.get("type") == "subscribe":
                task_id = message.get("task_id")
                if task_id:
                    manager.subscribe_task(task_id, client_id)
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "task_id": task_id,
                        "message": f"已订阅任务 {task_id}"
                    }))
            
            # 处理取消订阅
            elif message.get("type") == "unsubscribe":
                task_id = message.get("task_id")
                if task_id and task_id in manager.task_subscribers:
                    if client_id in manager.task_subscribers[task_id]:
                        manager.task_subscribers[task_id].remove(client_id)
                        await websocket.send_text(json.dumps({
                            "type": "unsubscribed",
                            "task_id": task_id
                        }))
            
            # 处理心跳
            elif message.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": message.get("timestamp")
                }))
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"❌ WebSocket 错误: {e}")
        manager.disconnect(client_id)
