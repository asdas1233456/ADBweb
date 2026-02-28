# 🐳 Docker部署注意事项（中文版）

## 🎯 核心要点（必读！）

Docker部署看起来简单，但有10个关键点必须注意，否则会导致数据丢失、服务崩溃或安全问题。

---

## ⚠️ 最重要的3件事

### 1. 数据持久化（最容易忽略！）

**问题**：Docker容器删除后，容器内的所有数据都会丢失！

**场景**：
- 你运行 `docker-compose down` 删除容器
- 服务器重启
- 容器崩溃重启
- 更新镜像重新部署

**后果**：
- ❌ 数据库文件丢失（所有用户数据、设备信息、脚本记录全部消失）
- ❌ 上传的文件丢失（截图、脚本文件全部消失）
- ❌ 日志文件丢失（无法追踪问题）

**解决方案**：使用Volume挂载（已在docker-compose.yml中配置）

```yaml
volumes:
  # 数据库文件 - 必须挂载！
  - ./backend/test_platform.db:/app/backend/test_platform.db
  
  # 上传文件 - 必须挂载！
  - ./backend/uploads:/app/backend/uploads
  
  # 日志文件 - 建议挂载
  - ./logs:/app/logs
```

**验证方法**：
```bash
# 检查挂载是否生效
docker inspect adbweb | grep -A 20 Mounts

# 应该看到3个挂载点
```

**定期备份**：
```bash
# 每天自动备份（必须设置！）
0 2 * * * /www/wwwroot/ADBweb/backup.sh
```

---

### 2. 环境变量配置

**问题**：敏感信息（API密钥、数据库密码）不能写在代码里！

**错误做法**：
```python
# ❌ 不要这样做
OPENAI_API_KEY = "sk-xxxxxxxxxxxxx"  # 提交到Git后泄露
```

**正确做法**：使用 .env 文件

```bash
# 创建 .env 文件
cat > .env <<EOF
DOCKER_USERNAME=your-docker-username
TZ=Asia/Shanghai
DATABASE_URL=sqlite:///./backend/test_platform.db
OPENAI_API_KEY=your-openai-key
DEEPSEEK_API_KEY=your-deepseek-key
EOF

# 添加到 .gitignore
echo ".env" >> .gitignore
```

**注意**：
- ✅ .env 文件只在服务器上创建，不提交到Git
- ✅ 每台服务器都要单独创建
- ✅ 定期更换API密钥

---

### 3. 资源限制

**问题**：容器可能占用所有服务器资源，导致服务器卡死！

**场景**：
- AI模型推理占用大量内存
- OCR处理大图片
- 并发请求过多

**后果**：
- ❌ 服务器内存耗尽，SSH无法连接
- ❌ 其他服务被挤掉
- ❌ 服务器死机

**解决方案**：设置资源限制（已在docker-compose.yml中配置）

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # 最多使用2个CPU核心
      memory: 2G       # 最多使用2GB内存
    reservations:
      cpus: '0.5'      # 至少保留0.5个CPU核心
      memory: 512M     # 至少保留512MB内存
```

**监控资源使用**：
```bash
# 实时监控
docker stats adbweb

# 应该看到：
# CPU使用率 < 200%
# 内存使用 < 2GB
```

---

## 🔧 部署前检查清单（10项）

### ✅ 1. 服务器配置检查

```bash
# 检查内存（至少2GB）
free -h
# 输出应该显示：Mem: 2.0Gi 或更多

# 检查磁盘空间（至少10GB）
df -h
# 输出应该显示：Avail 10G 或更多

# 检查CPU
lscpu
# 输出应该显示：CPU(s): 1 或更多
```

**不满足要求怎么办**：
- 内存不足：增加swap空间或升级服务器
- 磁盘不足：清理无用文件或扩容
- CPU不足：升级服务器配置

---

### ✅ 2. Docker安装检查

```bash
# 检查Docker版本
docker --version
# 需要：Docker version 20.10.0 或更高

# 检查Docker Compose版本
docker-compose --version
# 需要：Docker Compose version 2.0.0 或更高

# 测试Docker是否正常
docker run hello-world
# 应该看到：Hello from Docker!
```

**未安装怎么办**：
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker
```

---

### ✅ 3. 端口占用检查

```bash
# 检查8000和5173端口
netstat -tuln | grep -E '8000|5173'

# 如果有输出，说明端口被占用
```

**端口被占用怎么办**：
```bash
# 查找占用进程
lsof -i :8000
lsof -i :5173

# 停止进程
kill -9 <PID>

# 或修改docker-compose.yml中的端口映射
ports:
  - "8001:8000"  # 改用8001端口
  - "5174:5173"  # 改用5174端口
```

---

### ✅ 4. 防火墙配置

```bash
# Ubuntu/Debian
sudo ufw allow 8000
sudo ufw allow 5173
sudo ufw status

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=5173/tcp
sudo firewall-cmd --reload
```

**云服务器额外步骤**：
- 阿里云：在安全组中开放8000、5173端口
- 腾讯云：在防火墙规则中开放8000、5173端口
- AWS：在Security Group中开放8000、5173端口

---

### ✅ 5. 创建必要目录

```bash
cd /www/wwwroot/ADBweb  # 或你的项目目录

# 创建目录
mkdir -p backend/uploads/screenshots
mkdir -p backend/uploads/scripts
mkdir -p logs

# 设置权限
chmod 777 backend/uploads
chmod 777 logs
```

---

### ✅ 6. 创建 .env 文件

```bash
cd /www/wwwroot/ADBweb

# 创建 .env 文件
cat > .env <<EOF
# Docker配置
DOCKER_USERNAME=your-docker-username
TZ=Asia/Shanghai

# 数据库配置
DATABASE_URL=sqlite:///./backend/test_platform.db

# AI API密钥（如果使用）
OPENAI_API_KEY=your-openai-key
DEEPSEEK_API_KEY=your-deepseek-key
EOF

# 设置权限（只有owner可读写）
chmod 600 .env
```

---

### ✅ 7. 配置Docker镜像加速（国内必须！）

```bash
# 创建配置文件
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://registry.docker-cn.com"
  ]
}
EOF

# 重启Docker
sudo systemctl daemon-reload
sudo systemctl restart docker

# 验证配置
docker info | grep -A 5 "Registry Mirrors"
```

**为什么必须配置**：
- 不配置：拉取镜像速度 < 100KB/s，可能超时失败
- 配置后：拉取镜像速度 > 5MB/s，稳定可靠

---

### ✅ 8. 准备数据库文件

```bash
cd /www/wwwroot/ADBweb/backend

# 首次部署：创建空数据库
touch test_platform.db
chmod 666 test_platform.db

# 迁移部署：复制现有数据库
# scp user@old-server:/path/to/test_platform.db ./
```

---

### ✅ 9. 验证配置文件

```bash
cd /www/wwwroot/ADBweb

# 验证docker-compose.yml语法
docker-compose config

# 应该看到完整的配置输出，没有错误
```

---

### ✅ 10. 设置自动备份

```bash
cd /www/wwwroot/ADBweb

# 创建备份脚本
cat > backup.sh <<'EOF'
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
EOF

chmod +x backup.sh

# 测试备份脚本
./backup.sh

# 设置定时任务（每天凌晨2点）
crontab -e
# 添加这一行：
# 0 2 * * * /www/wwwroot/ADBweb/backup.sh
```

---

## 🚀 部署步骤（3步完成）

### 步骤1：构建镜像

```bash
cd /www/wwwroot/ADBweb

# 构建镜像
docker-compose build

# 预计时间：5-10分钟（首次构建）
# 你会看到：
# - 下载Node.js镜像
# - 安装前端依赖
# - 构建前端
# - 下载Python镜像
# - 安装后端依赖
```

**常见问题**：
- 下载慢：检查镜像加速是否配置
- 内存不足：增加swap空间
- 网络超时：重试或使用代理

---

### 步骤2：启动服务

```bash
# 启动服务（后台运行）
docker-compose up -d

# 预计时间：30秒

# 你会看到：
# Creating network "adbweb_adbweb-network" ... done
# Creating adbweb ... done
```

---

### 步骤3：验证部署

```bash
# 1. 检查容器状态
docker ps

# 应该看到：
# CONTAINER ID   IMAGE     STATUS                    PORTS
# xxxxxxxxxxxx   adbweb    Up 30 seconds (healthy)   0.0.0.0:8000->8000/tcp, 0.0.0.0:5173->5173/tcp

# 2. 查看日志
docker-compose logs -f

# 应该看到：
# INFO:     Uvicorn running on http://0.0.0.0:8000
# 没有ERROR或EXCEPTION

# 3. 测试后端API
curl http://localhost:8000/health

# 应该返回：
# {"status":"ok"}

# 4. 测试前端（在浏览器打开）
# http://your-server-ip:5173
# 应该能看到ADBweb界面
```

---

## ❌ 5个最容易出错的地方

### 错误1：忘记创建 .env 文件

**症状**：
```
Error: Environment variable DATABASE_URL is not set
```

**解决**：
```bash
cp backend/.env.example .env
# 编辑 .env 填写实际配置
```

---

### 错误2：端口被占用

**症状**：
```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**解决**：
```bash
# 查找占用进程
lsof -i :8000

# 停止进程
kill -9 <PID>

# 或修改端口
# 编辑 docker-compose.yml
ports:
  - "8001:8000"
```

---

### 错误3：数据库文件权限问题

**症状**：
```
Error: unable to open database file
```

**解决**：
```bash
chmod 666 backend/test_platform.db
chmod 777 backend/uploads
```

---

### 错误4：内存不足

**症状**：
- 容器启动后自动退出
- `docker ps` 看不到容器

**解决**：
```bash
# 检查内存
free -h

# 增加swap空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久生效
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

### 错误5：镜像拉取失败

**症状**：
```
Error: Get https://registry-1.docker.io/v2/: net/http: TLS handshake timeout
```

**解决**：
```bash
# 配置Docker镜像加速（见上面第7步）

# 或使用代理
export HTTP_PROXY=http://proxy-server:port
export HTTPS_PROXY=http://proxy-server:port
docker-compose build
```

---

## 🔧 日常运维命令

### 查看状态

```bash
# 查看容器状态
docker ps

# 查看资源使用
docker stats adbweb

# 查看日志（实时）
docker-compose logs -f

# 查看最近100行日志
docker-compose logs --tail=100

# 只看错误日志
docker-compose logs | grep -i error
```

---

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启单个容器
docker restart adbweb

# 停止服务
docker-compose down

# 启动服务
docker-compose up -d
```

---

### 更新部署

```bash
# 1. 拉取最新代码
cd /www/wwwroot/ADBweb
git pull

# 2. 备份数据（重要！）
./backup.sh

# 3. 重新构建
docker-compose build

# 4. 重启服务
docker-compose up -d --build

# 5. 清理旧镜像
docker image prune -f
```

---

### 进入容器调试

```bash
# 进入容器
docker exec -it adbweb bash

# 查看文件
ls -la /app/backend

# 查看日志
cat /app/logs/app.log

# 测试API
curl http://localhost:8000/health

# 退出容器
exit
```

---

### 备份和恢复

```bash
# 手动备份
./backup.sh

# 查看备份文件
ls -lh /www/backup/adbweb/

# 恢复数据库
docker cp /www/backup/adbweb/db_20240228_020000.db adbweb:/app/backend/test_platform.db

# 恢复上传文件
tar -xzf /www/backup/adbweb/uploads_20240228_020000.tar.gz -C ./

# 重启服务
docker-compose restart
```

---

## 📊 监控和告警

### 设置健康检查

```bash
cat > health_check.sh <<'EOF'
#!/bin/bash
LOG_FILE="/www/logs/health_check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "[$DATE] ❌ 服务异常" >> $LOG_FILE
    
    # 发送钉钉通知（可选）
    # curl -X POST "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN" \
    #   -H 'Content-Type: application/json' \
    #   -d '{"msgtype":"text","text":{"content":"ADBweb服务异常！"}}'
    
    # 尝试重启
    cd /www/wwwroot/ADBweb
    docker-compose restart
    
    echo "[$DATE] 🔄 已尝试重启服务" >> $LOG_FILE
else
    echo "[$DATE] ✅ 服务正常" >> $LOG_FILE
fi
EOF

chmod +x health_check.sh

# 每5分钟检查一次
crontab -e
# 添加：*/5 * * * * /www/wwwroot/ADBweb/health_check.sh
```

---

### 监控资源使用

```bash
# 实时监控
docker stats adbweb

# 输出示例：
# CONTAINER ID   NAME     CPU %     MEM USAGE / LIMIT     MEM %
# xxxxxxxxxxxx   adbweb   15.23%    512MiB / 2GiB        25.00%

# 设置告警阈值
# CPU > 80% 或 内存 > 1.5GB 时告警
```

---

## 🛡️ 安全建议

### 1. 不要以root用户运行

在 Dockerfile 中添加：
```dockerfile
# 创建非root用户
RUN useradd -m -u 1000 appuser
USER appuser
```

---

### 2. 限制容器权限

在 docker-compose.yml 中添加：
```yaml
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE
```

---

### 3. 使用HTTPS

```bash
# 安装Nginx
sudo apt install nginx

# 配置反向代理
sudo nano /etc/nginx/sites-available/adbweb

# 添加配置：
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5173;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
}

# 安装SSL证书（Let's Encrypt）
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

### 4. 定期更新

```bash
# 每周检查更新
docker pull python:3.11-slim
docker pull node:18-alpine

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

---

### 5. 扫描安全漏洞

```bash
# 安装Trivy
wget https://github.com/aquasecurity/trivy/releases/download/v0.48.0/trivy_0.48.0_Linux-64bit.tar.gz
tar zxvf trivy_0.48.0_Linux-64bit.tar.gz
sudo mv trivy /usr/local/bin/

# 扫描镜像
trivy image adbweb:latest

# 查看高危漏洞
trivy image --severity HIGH,CRITICAL adbweb:latest
```

---

## ✅ 部署成功的标志

当你看到以下内容时，说明部署成功：

1. ✅ `docker ps` 显示容器状态为 "Up" 且有 "(healthy)"
2. ✅ `curl http://localhost:8000/health` 返回 `{"status":"ok"}`
3. ✅ 浏览器访问 `http://your-ip:5173` 能看到ADBweb界面
4. ✅ 日志中没有 ERROR 或 EXCEPTION
5. ✅ `ls -lh backend/test_platform.db` 显示文件大小 > 0
6. ✅ 上传功能正常工作（测试上传一个截图）
7. ✅ AI元素定位功能正常（测试识别一个按钮）

---

## 📞 遇到问题怎么办

### 1. 查看日志

```bash
# 查看所有日志
docker-compose logs

# 查看最近的错误
docker-compose logs | grep -i error

# 导出日志
docker-compose logs > debug.log
```

---

### 2. 检查配置

```bash
# 验证docker-compose.yml
docker-compose config

# 检查环境变量
docker exec adbweb env

# 检查挂载
docker inspect adbweb | grep -A 20 Mounts
```

---

### 3. 重新部署

```bash
# 完全清理
docker-compose down -v
docker system prune -a

# 重新构建
docker-compose build --no-cache

# 重新启动
docker-compose up -d
```

---

### 4. 联系支持

如果以上方法都无法解决，请提供以下信息：

1. 错误日志：`docker-compose logs > error.log`
2. 系统信息：`uname -a`
3. Docker版本：`docker --version`
4. 容器状态：`docker ps -a`
5. 资源使用：`docker stats --no-stream`

---

## 📚 相关文档

- **完整部署指南**：`DOCKER_DEPLOYMENT_GUIDE.md`（详细版，89KB）
- **快速检查清单**：`DOCKER_DEPLOYMENT_CHECKLIST.md`（快速版）
- **Dockerfile配置**：`Dockerfile`
- **Docker Compose配置**：`docker-compose.yml`
- **环境变量示例**：`backend/.env.example`

---

## 🎯 总结

Docker部署的核心是：

1. **数据持久化**：使用Volume挂载，定期备份
2. **环境变量**：使用.env文件，不提交到Git
3. **资源限制**：设置CPU和内存限制
4. **健康检查**：配置自动重启和监控
5. **安全加固**：非root用户、限制权限、HTTPS

只要做好这5点，你的Docker部署就会非常稳定可靠！

---

**祝部署顺利！🎉**

如有问题，随时查看文档或寻求帮助。
