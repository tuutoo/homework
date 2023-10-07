# 使用 Node.js 18 的基础镜像
FROM node:18

# 设置工作目录
WORKDIR /usr/src/app

# 全局安装 pnpm
RUN npm install -g pnpm

# 将 package.json 和 pnpm-lock.yaml（如果有）复制到工作目录
COPY package.json pnpm-lock.yaml* ./
COPY . .

# 安装项目依赖
RUN pnpm install

# 暴露端口（与 docker-compose 文件一致）
EXPOSE 5173
CMD ["pnpm", "run", "dev"]