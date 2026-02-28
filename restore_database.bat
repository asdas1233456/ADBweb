@echo off
REM 数据库恢复脚本
echo 可用的备份文件：
echo.

dir /b backups\*.db

echo.
set /p BACKUP_FILE="请输入要恢复的备份文件名（不含路径）: "

if exist "backups\%BACKUP_FILE%" (
    echo 正在恢复数据库...
    copy "backups\%BACKUP_FILE%" "backend\test_platform.db" /Y
    echo 恢复完成！请重启后端服务。
) else (
    echo 错误：备份文件不存在！
)

pause
