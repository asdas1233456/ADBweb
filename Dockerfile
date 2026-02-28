# 多阶段构建 - 前端构建阶段（改用国内镜像源）
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# 配置 npm 国内源（淘宝镜像，解决 npm install 超时）
RUN npm config set registry https://registry.npmmirror.com --global

# 复制前端依赖文件
COPY package*.json ./

# 安装前端依赖（用国内源，不会超时）
RUN npm install

# 复制前端源码
COPY . .

RUN chmod -R 755 node_modules/.bin

RUN rm -f src/services/api_missing.ts src/services/api_temp.ts src/services/api_fixed.ts && \
    npm run build

# 构建前端
RUN npm run build

# 后端运行阶段（改用阿里云国内镜像）
FROM python:3.11-slim


# 设置工作目录
WORKDIR /app

# 配置 apt 国内源（解决 apt-get update 超时）
# 配置 apt 国内源（解决 apt-get update 超时）
RUN if [ -f /etc/apt/sources.list ]; then \
        sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
        sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list; \
    elif [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
        sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources; \
    fi


# 安装系统依赖（用国内源，不会超时）
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*


# 复制后端依赖文件
COPY backend/requirements.txt ./backend/

# 安装Python依赖（用清华源，强化国内源）
RUN pip install --no-cache-dir -r backend/requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制后端代码
COPY backend/ ./backend/

# 复制前端构建产物
COPY --from=frontend-builder /app/dist ./dist

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
