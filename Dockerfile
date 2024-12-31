# ------------------------------------------------
# 阶段1：前端基础镜像（安装 pnpm + 依赖）
# ------------------------------------------------
  FROM node:20 AS frontend-base
  WORKDIR /frontend

  # 全局安装 pnpm
  RUN npm install -g pnpm

  # 只复制与依赖安装相关的文件
  COPY app/package.json app/pnpm-lock.yaml* ./

  # 安装前端依赖
  RUN pnpm install

  # 复制前端全部源代码（忽略 .dockerignore 中的内容）
  COPY app/ ./

  # ------------------------------------------------
  # 阶段2：前端构建阶段
  # ------------------------------------------------
  FROM frontend-base AS frontend-builder
  RUN pnpm run build

  # ------------------------------------------------
  # 阶段3：后端构建阶段
  # ------------------------------------------------
  FROM ultralytics/ultralytics:8.3.55-cpu AS backend-builder
  WORKDIR /backend

  # 复制后端依赖文件并安装
  COPY api/requirements.txt ./
  RUN pip install -r requirements.txt

  # 复制后端源代码
  COPY api/ ./

  # ------------------------------------------------
  # 阶段4：最终生产镜像
  # ------------------------------------------------
  FROM ultralytics/ultralytics:8.3.55-cpu

  # 安装 Nginx
  RUN apt-get update && apt-get install -y --no-install-recommends nginx

  # 移除默认配置，避免冲突
  RUN rm /etc/nginx/sites-enabled/default

  # 切换工作目录至 /app/backend
  WORKDIR /app/backend

  # 复制前端构建产物到 Nginx 默认静态资源目录
  COPY --from=frontend-builder /frontend/dist /usr/share/nginx/html

  # 复制后端代码到容器
  COPY --from=backend-builder /backend /app/backend

  # 安装后端依赖
  RUN pip install -r requirements.txt

  # 复制自定义的 Nginx 配置
  COPY ./nginx.conf /etc/nginx/conf.d/default.conf

  # 暴露端口
  EXPOSE 80

  # 启动脚本：使用 uvicorn 启动后端 & 同时运行 Nginx
  CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & nginx -g 'daemon off;'"]
