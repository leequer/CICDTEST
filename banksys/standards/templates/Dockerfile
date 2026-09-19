FROM python:3.11-slim

WORKDIR /app

# 使用国内镜像加速（可选，国内服务器推荐）
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir uv

# 复制依赖文件
COPY pyproject.toml ./

# 复制源代码
COPY src/ ./src/

# 安装依赖
RUN uv sync

# 暴露端口
EXPOSE 6100

# 启动命令
CMD ["uv", "run", "python", "-m", "src.backend.app"]
