#!/bin/bash
# Java代码评审工具启动脚本

echo "🚀 Java代码自动评审工具"
echo "================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python"
    exit 1
fi

# 检查Java文件
java_files=$(find . -name "*.java" -type f | wc -l)
if [ $java_files -eq 0 ]; then
    echo "❌ 错误: 当前目录下没有找到Java文件"
    exit 1
fi

echo "✅ 找到 $java_files 个Java文件"

# 显示菜单
echo ""
echo "请选择操作:"
echo "1. 基础代码评审"
echo "2. AI增强评审 (需要Ollama服务)"
echo "3. CI/CD质量检查"
echo "4. 运行完整演示"
echo "5. 查看帮助"
echo ""

read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo "🔍 运行基础代码评审..."
        python3 java_code_reviewer.py . --format both
        ;;
    2)
        echo "🤖 运行AI增强评审..."
        # 检查Ollama服务
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo "✅ Ollama服务正在运行"
            python3 ai_enhanced_reviewer.py . --format comprehensive
        else
            echo "⚠️ Ollama服务未运行，将使用基础评审"
            python3 java_code_reviewer.py . --format both
        fi
        ;;
    3)
        echo "🔄 运行CI/CD质量检查..."
        python3 ci_integration.py . --min-score 50 --max-errors 5
        ;;
    4)
        echo "🎯 运行完整演示..."
        python3 demo_usage.py
        ;;
    5)
        echo "📖 查看帮助信息..."
        echo ""
        echo "基础评审:"
        echo "  python3 java_code_reviewer.py . --format both"
        echo ""
        echo "AI增强评审:"
        echo "  python3 ai_enhanced_reviewer.py . --format comprehensive"
        echo ""
        echo "CI/CD集成:"
        echo "  python3 ci_integration.py . --min-score 70 --max-errors 0"
        echo ""
        echo "更多帮助:"
        echo "  python3 java_code_reviewer.py --help"
        echo "  python3 ai_enhanced_reviewer.py --help"
        echo "  python3 ci_integration.py --help"
        ;;
    *)
        echo "❌ 无效选项，请重新运行脚本"
        exit 1
        ;;
esac

echo ""
echo "✅ 操作完成！"
echo "📄 查看 reports/ 目录下的报告文件"
