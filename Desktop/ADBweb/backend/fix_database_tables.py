#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复数据库表缺失问题
"""

import sqlite3
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

def fix_database_tables():
    """修复数据库表"""
    db_path = "test_platform.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("开始修复数据库表...")
        
        # 1. 创建设备健康度记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                health_score INTEGER NOT NULL,
                battery_level INTEGER,
                temperature REAL,
                cpu_usage REAL,
                memory_usage REAL,
                storage_usage REAL,
                network_status TEXT,
                last_active_time DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES device (id)
            )
        """)
        print("✓ 创建 device_health_records 表")
        
        # 2. 创建设备使用统计表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_usage_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER UNIQUE NOT NULL,
                total_executions INTEGER DEFAULT 0,
                success_executions INTEGER DEFAULT 0,
                failed_executions INTEGER DEFAULT 0,
                total_duration INTEGER DEFAULT 0,
                avg_duration REAL,
                success_rate REAL,
                last_execution_time DATETIME,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES device (id)
            )
        """)
        print("✓ 创建 device_usage_stats 表")
        
        # 3. 检查并修复脚本表的steps_json字段
        cursor.execute("PRAGMA table_info(script)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'steps_json' not in columns:
            cursor.execute("ALTER TABLE script ADD COLUMN steps_json TEXT")
            print("✓ 添加 script.steps_json 字段")
        
        # 4. 修复脚本表中的空名称
        cursor.execute("UPDATE script SET name = 'Unnamed Script ' || id WHERE name IS NULL OR name = ''")
        affected = cursor.rowcount
        if affected > 0:
            print(f"✓ 修复了 {affected} 个空脚本名称")
        
        # 5. 修复脚本表中的无效steps_json
        cursor.execute("SELECT id, steps_json FROM script WHERE type = 'visual'")
        scripts = cursor.fetchall()
        
        fixed_count = 0
        for script_id, steps_json in scripts:
            if not steps_json:
                # 设置默认的steps_json
                default_steps = '[{"id": "s1", "type": "click", "name": "点击操作", "config": {"x": 100, "y": 200}}]'
                cursor.execute("UPDATE script SET steps_json = ? WHERE id = ?", (default_steps, script_id))
                fixed_count += 1
            else:
                try:
                    import json
                    json.loads(steps_json)
                except json.JSONDecodeError:
                    # 修复无效的JSON
                    default_steps = '[{"id": "s1", "type": "click", "name": "点击操作", "config": {"x": 100, "y": 200}}]'
                    cursor.execute("UPDATE script SET steps_json = ? WHERE id = ?", (default_steps, script_id))
                    fixed_count += 1
        
        if fixed_count > 0:
            print(f"✓ 修复了 {fixed_count} 个无效的steps_json")
        
        # 6. 创建脚本模板表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS script_template (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                language TEXT DEFAULT 'adb',
                template_content TEXT NOT NULL,
                variables TEXT,
                tags TEXT,
                usage_count INTEGER DEFAULT 0,
                is_builtin BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_by TEXT DEFAULT 'system',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ 创建 script_template 表")
        
        # 7. 检查并创建测试用例表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                test_data TEXT,
                expected_result TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ 创建 test_cases 表")
        
        # 8. 添加一些测试数据
        cursor.execute("SELECT COUNT(*) FROM device_health_records")
        if cursor.fetchone()[0] == 0:
            # 为现有设备添加健康度记录
            cursor.execute("SELECT id FROM device LIMIT 3")
            devices = cursor.fetchall()
            
            for device_id, in devices:
                cursor.execute("""
                    INSERT INTO device_health_records 
                    (device_id, health_score, battery_level, cpu_usage, memory_usage)
                    VALUES (?, ?, ?, ?, ?)
                """, (device_id, 85, 75, 45.5, 60.2))
            
            print(f"✓ 为 {len(devices)} 个设备添加了健康度记录")
        
        # 9. 添加一些脚本模板
        cursor.execute("SELECT COUNT(*) FROM script_template")
        if cursor.fetchone()[0] == 0:
            templates = [
                ("应用登录测试", "测试", "测试应用登录功能", "adb", 
                 "adb shell input tap {{login_x}} {{login_y}}\nadb shell input text {{username}}\nadb shell input tap {{password_x}} {{password_y}}\nadb shell input text {{password}}",
                 '{"login_x": {"type": "number", "default": "100"}, "login_y": {"type": "number", "default": "200"}, "username": {"type": "text", "default": "testuser"}, "password_x": {"type": "number", "default": "100"}, "password_y": {"type": "number", "default": "300"}, "password": {"type": "text", "default": "testpass"}}',
                 "登录,测试,自动化"),
                ("搜索功能测试", "测试", "测试应用搜索功能", "adb",
                 "adb shell input tap {{search_x}} {{search_y}}\nadb shell input text {{search_keyword}}\nadb shell input keyevent 66",
                 '{"search_x": {"type": "number", "default": "200"}, "search_y": {"type": "number", "default": "100"}, "search_keyword": {"type": "text", "default": "测试关键词"}}',
                 "搜索,测试,自动化")
            ]
            
            for template in templates:
                cursor.execute("""
                    INSERT INTO script_template 
                    (name, category, description, language, template_content, variables, tags, is_builtin)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """, template)
            
            print(f"✓ 添加了 {len(templates)} 个内置模板")
        
        conn.commit()
        print("✅ 数据库修复完成！")
        
        # 显示表统计
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        print(f"\n📊 数据库包含 {len(tables)} 个表:")
        for table, in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} 条记录")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    success = fix_database_tables()
    sys.exit(0 if success else 1)