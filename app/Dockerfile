# 使用 Node.js 18 的基础镜像
FROM node:18

# 设置工作目录
WORKDIR /app

# 将 package.json 和 pnpm-lock.yaml（如果有）复制到工作目录
COPY package.json pnpm-lock.yaml* ./

# 全局安装 pnpm 和 vite
RUN npm install -g pnpm vite

# 安装项目依赖
RUN pnpm install

# 将项目文件复制到工作目录
COPY . .

# 构建项目
RUN pnpm run build

# 使用 Nginx 镜像来运行构建结果
FROM nginx:alpine

# 将构建结果复制到 Nginx 中
COPY --from=0 /app/dist /usr/share/nginx/html

# 暴露 80 端口
EXPOSE 80

# 运行 Nginx
CMD ["nginx", "-g", "daemon off;"]
