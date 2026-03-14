"""
WebSocket 连接管理器
"""
from typing import Dict, List
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime
from app.utils.time_utils import now_local


class ConnectionManager:
    def __init__(self):
        # 存储所有活跃连接: {client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # 存储任务订阅: {task_id: [client_id1, client_id2]}
        self.task_subscribers: Dict[int, List[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """接受新连接"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"✅ 客户端 {client_id} 已连接, 当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, client_id: str):
        """断开连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        # 清理订阅
        for task_id in list(self.task_subscribers.keys()):
            if client_id in self.task_subscribers[task_id]:
                self.task_subscribers[task_id].remove(client_id)
                if not self.task_subscribers[task_id]:
                    del self.task_subscribers[task_id]
        
        print(f"❌ 客户端 {client_id} 已断开, 当前连接数: {len(self.active_connections)}")
    
    def subscribe_task(self, task_id: int, client_id: str):
        """订阅任务更新"""
        if task_id not in self.task_subscribers:
            self.task_subscribers[task_id] = []
        if client_id not in self.task_subscribers[task_id]:
            self.task_subscribers[task_id].append(client_id)
            print(f"📡 客户端 {client_id} 订阅任务 {task_id}")
    
    async def send_task_update(self, task_id: int, data: dict):
        """向订阅该任务的所有客户端发送更新"""
        if task_id not in self.task_subscribers:
            return
        
        message = json.dumps({
            "type": "task_update",
            "task_id": task_id,
            "data": data,
            "timestamp": now_local().isoformat()
        })
        
        # 发送给所有订阅者
        disconnected_clients = []
        for client_id in self.task_subscribers[task_id]:
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_text(message)
                except Exception as e:
                    print(f"⚠️ 发送失败: {client_id}, 错误: {e}")
                    disconnected_clients.append(client_id)
        
        # 清理断开的连接
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def broadcast(self, message: str):
        """广播消息给所有连接"""
        disconnected_clients = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception:
                disconnected_clients.append(client_id)
        
        for client_id in disconnected_clients:
            self.disconnect(client_id)


# 全局连接管理器实例
manager = ConnectionManager()
