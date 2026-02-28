#!/bin/bash
BACKUP_DIR="/www/backup/adbweb"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份数据库
docker cp adbweb:/app/backend/test_platform.db $BACKUP_DIR/db_$DATE.db

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz backend/uploads/

# 只保留最近7天的备份
find $BACKUP_DIR -name "db_*.db" -mtime +7 -delete
find $BACKUP_DIR -name "uploads_*.tar.gz" -mtime +7 -delete

echo "✅ 备份完成: $DATE"
