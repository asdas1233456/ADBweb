#!/bin/bash

echo "========================================"
echo "ADBweb 全面测试套件"
echo "========================================"
echo

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

echo "Python 版本: $(python3 --version)"

# 检查依赖
echo "检查测试依赖..."
if ! python3 -c "import pytest" &> /dev/null; then
    echo "安装测试依赖..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 依赖安装失败"
        exit 1
    fi
fi

# 创建报告目录
mkdir -p reports
mkdir -p allure-results

echo
echo "开始运行测试..."
echo "========================================"

# 运行测试
python3 -m pytest test_comprehensive.py --alluredir=allure-results -v --html=reports/report.html --self-contained-html

# 检查测试结果
if [ $? -ne 0 ]; then
    echo
    echo "❌ 测试执行失败"
    echo "请查看上方错误信息"
else
    echo
    echo "✅ 测试执行完成"
fi

echo
echo "========================================"
echo "报告生成"
echo "========================================"

# 检查 Allure 是否安装
if ! command -v allure &> /dev/null; then
    echo "⚠️  Allure 未安装，跳过 Allure 报告生成"
    echo "💡 安装 Allure: https://docs.qameta.io/allure/#_installing_a_commandline"
    echo "📊 HTML 报告已生成: reports/report.html"
else
    echo "生成 Allure 报告..."
    allure generate allure-results -o allure-report --clean
    if [ $? -ne 0 ]; then
        echo "❌ Allure 报告生成失败"
    else
        echo "✅ Allure 报告生成成功"
        echo "📊 报告位置: allure-report/index.html"
        
        # 询问是否打开报告
        read -p "是否打开 Allure 报告? (y/n): " choice
        if [[ $choice == [Yy]* ]]; then
            allure open allure-report
        fi
    fi
fi

echo
echo "========================================"
echo "测试完成"
echo "========================================"
echo "📁 HTML 报告: reports/report.html"
echo "📁 Allure 报告: allure-report/index.html"
echo "📁 测试结果: allure-results/"
echo

# 在 macOS 上可以用 open，在 Linux 上可以用 xdg-open
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "💡 使用 'open reports/report.html' 查看 HTML 报告"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "💡 使用 'xdg-open reports/report.html' 查看 HTML 报告"
fi