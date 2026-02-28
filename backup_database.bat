@echo off
REM 数据库备份脚本
echo 正在备份数据库...

set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

if not exist "backups" mkdir backups

copy "backend\test_platform.db" "backups\test_platform_%TIMESTAMP%.db"

echo 备份完成: backups\test_platform_%TIMESTAMP%.db
pause
