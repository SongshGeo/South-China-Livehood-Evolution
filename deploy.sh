#!/bin/bash
# 部署脚本

echo "🚀 开始部署到 Vercel..."

# 进入 Docusaurus 目录
cd docs-docusaurus

# 安装依赖
echo "📦 安装依赖..."
npm ci

# 构建项目
echo "🔨 构建项目..."
npm run build

# 部署到 Vercel
echo "🚀 部署到 Vercel..."
npx vercel --prod --yes

echo "✅ 部署完成！"
