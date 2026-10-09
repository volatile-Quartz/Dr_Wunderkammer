#!/bin/bash

# 确保脚本以UTF-8编码运行
export LANG=C.UTF-8

echo "欢迎使用GitBlog - 基于GitHub Issues的博客系统"
echo "======================================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null
then
    echo "错误: Python 3 未安装，请先安装Python 3.7+"
    exit 1
fi

# 检查pip是否安装
if ! command -v pip3 &> /dev/null
then
    echo "错误: pip 未安装，请先安装pip"
    exit 1
fi

# 安装依赖
echo "正在安装项目依赖..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]
then
    echo "错误: 依赖安装失败，请检查网络连接或requirements.txt文件"
    exit 1
fi

echo "依赖安装成功！"

# 提示用户输入GitHub Token和仓库名称
echo "\n请输入您的GitHub Personal Access Token (获取地址: https://github.com/settings/tokens)"
echo "注意: Token需要有repo权限"
read -s GITHUB_TOKEN

echo "\n请输入您的GitHub仓库名称 (格式: owner/repo)"
read REPO_NAME

# 验证输入
echo "\n正在验证输入信息..."
if [ -z "$GITHUB_TOKEN" ] || [ -z "$REPO_NAME" ]
then
    echo "错误: GitHub Token和仓库名称都不能为空"
    exit 1
fi

# 运行博客生成器
echo "\n正在运行博客生成器..."
python3 main.py "$GITHUB_TOKEN" "$REPO_NAME"

if [ $? -eq 0 ]
then
echo "\n🎉 博客生成成功！请查看README.md文件"
echo "\n下一步建议："
echo "1. 将项目推送到GitHub仓库"
echo "2. 配置GitHub Actions自动更新"
echo "3. 创建第一个Issue作为博客文章"
else
echo "\n错误: 博客生成失败，请查看错误信息"
fi

# 为Windows用户提供提示
echo "\n注意：如果您在Windows系统上使用此脚本，请考虑使用PowerShell或命令提示符直接运行以下命令："
echo "python main.py YOUR_GITHUB_TOKEN YOUR_REPO_NAME"