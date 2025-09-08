#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Java代码评审工具使用示例
演示各种功能的使用方法
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"命令: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"返回码: {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行命令时出错: {e}")
        return False


def demo_basic_review():
    """演示基础代码评审"""
    print("\n🎯 演示1: 基础代码评审")
    
    # 基础评审
    success = run_command([
        sys.executable, "java_code_reviewer.py", ".", "--format", "both"
    ], "基础代码评审 - 生成JSON和Markdown报告")
    
    if success:
        print("✅ 基础评审完成")
        
        # 查看生成的报告
        reports_dir = Path("reports")
        if reports_dir.exists():
            report_files = list(reports_dir.glob("*.md"))
            if report_files:
                latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
                print(f"📄 最新报告: {latest_report.name}")
                
                # 显示报告前几行
                with open(latest_report, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:20]
                    print("\n报告预览:")
                    print("".join(lines))
                    if len(lines) == 20:
                        print("... (报告内容较长，已截断)")
    else:
        print("❌ 基础评审失败")


def demo_ai_enhanced_review():
    """演示AI增强评审"""
    print("\n🤖 演示2: AI增强代码评审")
    
    # 检查Ollama是否运行
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama服务正在运行")
            
            # AI增强评审
            success = run_command([
                sys.executable, "ai_enhanced_reviewer.py", ".", "--format", "comprehensive"
            ], "AI增强代码评审 - 生成综合报告")
            
            if success:
                print("✅ AI增强评审完成")
            else:
                print("❌ AI增强评审失败")
        else:
            print("⚠️ Ollama服务未运行，跳过AI增强评审")
            print("💡 提示: 启动Ollama服务后可以体验AI增强功能")
    except Exception as e:
        print(f"⚠️ 无法连接到Ollama服务: {e}")
        print("💡 提示: 请确保Ollama服务正在运行")


def demo_ci_integration():
    """演示CI/CD集成"""
    print("\n🔄 演示3: CI/CD集成")
    
    # 基础CI检查
    success = run_command([
        sys.executable, "ci_integration.py", ".", "--min-score", "50", "--max-errors", "5"
    ], "CI/CD质量门禁检查")
    
    if success:
        print("✅ CI检查通过")
    else:
        print("❌ CI检查失败")
    
    # 设置Git钩子
    print("\n🔧 设置Git钩子...")
    success = run_command([
        sys.executable, "ci_integration.py", ".", "--setup-hooks"
    ], "设置Git pre-commit钩子")
    
    if success:
        print("✅ Git钩子设置完成")
    else:
        print("❌ Git钩子设置失败")


def demo_custom_analysis():
    """演示自定义分析"""
    print("\n🔍 演示4: 自定义分析")
    
    # 分析单个文件
    java_files = list(Path(".").glob("*.java"))
    if java_files:
        test_file = java_files[0]
        print(f"分析文件: {test_file.name}")
        
        success = run_command([
            sys.executable, "java_code_reviewer.py", str(test_file), "--format", "json"
        ], f"分析单个文件: {test_file.name}")
        
        if success:
            print("✅ 单文件分析完成")
        else:
            print("❌ 单文件分析失败")
    else:
        print("⚠️ 未找到Java文件")


def show_reports():
    """显示生成的报告"""
    print("\n📊 生成的报告文件")
    print("=" * 60)
    
    reports_dir = Path("reports")
    if reports_dir.exists():
        report_files = list(reports_dir.glob("*"))
        if report_files:
            print(f"找到 {len(report_files)} 个报告文件:")
            for report_file in sorted(report_files):
                size = report_file.stat().st_size
                mtime = report_file.stat().st_mtime
                print(f"  📄 {report_file.name} ({size} bytes, {mtime})")
        else:
            print("未找到报告文件")
    else:
        print("reports目录不存在")


def show_usage_examples():
    """显示使用示例"""
    print("\n📖 使用示例")
    print("=" * 60)
    
    examples = [
        ("基础评审", "python java_code_reviewer.py . --format both"),
        ("AI增强评审", "python ai_enhanced_reviewer.py . --format comprehensive"),
        ("CI质量检查", "python ci_integration.py . --min-score 70 --max-errors 0"),
        ("设置Git钩子", "python ci_integration.py . --setup-hooks"),
        ("持续监控", "python ci_integration.py . --watch --watch-interval 30"),
        ("评审单个文件", "python java_code_reviewer.py DateUtils.java"),
        ("只生成JSON", "python java_code_reviewer.py . --format json"),
        ("禁用AI分析", "python ai_enhanced_reviewer.py . --no-ai"),
    ]
    
    for desc, cmd in examples:
        print(f"💡 {desc}:")
        print(f"   {cmd}")
        print()


def main():
    """主函数"""
    print("🚀 Java代码评审工具演示")
    print("=" * 60)
    
    # 检查当前目录
    current_dir = Path(__file__).parent
    print(f"工作目录: {current_dir}")
    
    # 检查Java文件
    java_files = list(current_dir.glob("*.java"))
    print(f"找到 {len(java_files)} 个Java文件: {[f.name for f in java_files]}")
    
    if not java_files:
        print("❌ 当前目录下没有Java文件，无法进行演示")
        return
    
    # 运行演示
    try:
        demo_basic_review()
        demo_ai_enhanced_review()
        demo_ci_integration()
        demo_custom_analysis()
        
        show_reports()
        show_usage_examples()
        
        print("\n🎉 演示完成!")
        print("\n💡 提示:")
        print("  - 查看 reports/ 目录下的报告文件")
        print("  - 运行 'python java_code_reviewer.py --help' 查看所有选项")
        print("  - 运行 'python ai_enhanced_reviewer.py --help' 查看AI功能")
        print("  - 运行 'python ci_integration.py --help' 查看CI集成功能")
        
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {e}")


if __name__ == "__main__":
    main()
