#!/bin/bash

# lol-server 部署脚本

echo "🚀 开始部署到 Railway: lol-server"

# 检查是否已登录
if ! railway whoami > /dev/null 2>&1; then
    echo "📝 请先登录 Railway"
    railway login
fi

# 检查项目是否存在
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库"
    git init
    git add .
    git commit -m "Initial commit for lol-server"
fi

# 链接到 Railway 项目
echo "🔗 链接到项目 lol-server"
railway link lol-server

# 部署
echo "☁️  部署到 Railway..."
railway up

echo "✅ 部署完成！"
