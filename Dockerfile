# ----- 构建前端 -----
  FROM node:20 AS frontend-builder
  WORKDIR /frontend

  # 只复制必要文件
  COPY app/package*.json ./
  RUN npm install

  # 复制前端代码（忽略 .dockerignore 中的内容）
  COPY app/ ./
  RUN npm run build

  # ----- 构建后端 -----
  FROM ultralytics/ultralytics:8.3.55-cpu AS backend-builder
  WORKDIR /backend

  # 复制后端依赖和代码
  COPY api/requirements.txt ./
  RUN pip install -r requirements.txt

  COPY api/ ./

  # ----- 创建生产镜像并安装 Nginx -----
  FROM ultralytics/ultralytics:8.3.55-cpu

  # 安装 Nginx
  RUN apt-get update && apt-get install -y --no-install-recommends nginx

  # 将工作目录指定为 /app/backend
  WORKDIR /app/backend

  # 复制前端构建产物到 Nginx 的默认服务目录
  COPY --from=frontend-builder /frontend/dist /usr/share/nginx/html

  # 复制后端代码到容器内 /app/backend
  COPY --from=backend-builder /backend /app/backend

  # 安装后端依赖
  RUN pip install -r requirements.txt

  # 复制 Nginx 配置文件
  COPY ./nginx.conf /etc/nginx/conf.d/default.conf

  # 暴露端口
  EXPOSE 80

  # 启动脚本，确保后端与 Nginx 同时运行
  CMD ["sh", "-c", "python main.py & nginx -g 'daemon off;'"]
