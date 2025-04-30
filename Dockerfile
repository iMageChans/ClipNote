FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=ClipNote.settings

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建静态文件和媒体文件目录
RUN mkdir -p /app/static /app/media

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--reload", "--timeout", "120", "ClipNote.wsgi:application"] 