#!/bin/bash

# 启动Docker容器
docker-compose up --build -d
 
echo "ClipNote服务已启动，访问 http://localhost:8000 查看" 