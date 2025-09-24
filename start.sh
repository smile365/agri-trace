#!/bin/bash

# 获取 Flask 端口号
FLASK_PORT=$(grep FLASK_PORT backend/.env | cut -d '=' -f2)
echo "检测到 FLASK_PORT=${FLASK_PORT}"

# 检查端口占用
echo "检查端口 ${FLASK_PORT} 占用情况..."
PIDS=$(lsof -ti:${FLASK_PORT})

if [ -z "$PIDS" ]; then
    echo "端口 ${FLASK_PORT} 未被占用"
else
    echo "发现占用进程: $PIDS"
    # 终止所有占用进程
    kill -9 $PIDS
    echo "已终止占用进程"
    sleep 1  # 等待端口释放
fi

# 重启服务
echo "启动后端服务..."
cd backend && nohup python app.py > app.log 2>&1 &
NEW_PID=$!
echo "服务已启动 (PID: $NEW_PID)"
echo "日志输出: backend/app.log"