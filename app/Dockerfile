# 阶段1: 通用基础阶段，安装依赖
FROM node:18 AS base

# 设置工作目录
WORKDIR /usr/src/app

# 全局安装 pnpm
RUN npm install -g pnpm

# 复制 package.json 和 pnpm-lock.yaml
COPY package.json pnpm-lock.yaml* ./

# 安装依赖
RUN pnpm install

# 复制源代码
COPY . .

# 阶段2: 开发阶段
FROM base AS dev

# 暴露开发端口
EXPOSE 5173

# 设置开发模式
CMD ["pnpm", "run", "dev"]

FROM base as build
# 构建应用
RUN pnpm run build

# 阶段3: 生产阶段
FROM nginx:alpine AS prod

# 从构建阶段复制构建产物到当前镜像
COPY --from=build /usr/src/app/dist /usr/share/nginx/html

# 暴露生产端口
EXPOSE 80

# 使用 Nginx 运行
CMD ["nginx", "-g", "daemon off;"]
