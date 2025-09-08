#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI/CD集成脚本
用于在持续集成流程中自动运行代码评审
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any
import argparse


class CIIntegration:
    """CI/CD集成类"""
    
    def __init__(self, min_score: float = 70.0, max_errors: int = 0, max_warnings: int = 10):
        self.min_score = min_score
        self.max_errors = max_errors
        self.max_warnings = max_warnings
        self.failed = False
        self.results = {}
    
    def run_code_review(self, path: str, use_ai: bool = False) -> Dict[str, Any]:
        """运行代码评审"""
        print(f"🔍 开始代码评审: {path}")
        
        # 选择评审工具
        if use_ai:
            cmd = [sys.executable, "ai_enhanced_reviewer.py", path, "--format", "json"]
        else:
            cmd = [sys.executable, "java_code_reviewer.py", path, "--format", "json"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode != 0:
                print(f"❌ 代码评审失败: {result.stderr}")
                self.failed = True
                return {}
            
            # 查找生成的JSON报告
            reports_dir = Path(__file__).parent / "reports"
            json_files = list(reports_dir.glob("*.json"))
            
            if not json_files:
                print("❌ 未找到生成的报告文件")
                self.failed = True
                return {}
            
            # 读取最新的报告
            latest_report = max(json_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_report, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            print(f"✅ 代码评审完成，报告: {latest_report.name}")
            return report_data
            
        except Exception as e:
            print(f"❌ 运行代码评审时出错: {e}")
            self.failed = True
            return {}
    
    def check_quality_gates(self, report_data: Dict[str, Any]) -> bool:
        """检查质量门禁"""
        if not report_data:
            return False
        
        summary = report_data.get("summary", {})
        files = report_data.get("files", [])
        
        # 检查总体评分
        avg_score = summary.get("average_score", 0)
        if avg_score < self.min_score:
            print(f"❌ 平均评分 {avg_score:.1f} 低于最低要求 {self.min_score}")
            self.failed = True
        
        # 检查错误数量
        total_errors = 0
        total_warnings = 0
        
        for file_data in files:
            issues = file_data.get("issues", [])
            for issue in issues:
                if issue.get("severity") == "error":
                    total_errors += 1
                elif issue.get("severity") == "warning":
                    total_warnings += 1
        
        if total_errors > self.max_errors:
            print(f"❌ 错误数量 {total_errors} 超过限制 {self.max_errors}")
            self.failed = True
        
        if total_warnings > self.max_warnings:
            print(f"⚠️ 警告数量 {total_warnings} 超过建议限制 {self.max_warnings}")
            # 警告不一定会导致失败，但会提醒
        
        # 输出统计信息
        print(f"\n📊 质量门禁检查结果:")
        print(f"  平均评分: {avg_score:.1f}/100 (要求: ≥{self.min_score})")
        print(f"  错误数量: {total_errors} (限制: ≤{self.max_errors})")
        print(f"  警告数量: {total_warnings} (建议: ≤{self.max_warnings})")
        print(f"  评审文件数: {len(files)}")
        
        return not self.failed
    
    def generate_ci_report(self, report_data: Dict[str, Any], output_file: str):
        """生成CI报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# CI/CD 代码质量报告\n\n")
            f.write(f"**构建时间**: {os.popen('date').read().strip()}\n\n")
            
            if self.failed:
                f.write("## ❌ 质量门禁检查失败\n\n")
            else:
                f.write("## ✅ 质量门禁检查通过\n\n")
            
            if report_data:
                summary = report_data.get("summary", {})
                f.write("## 统计信息\n\n")
                f.write(f"- 评审文件数: {summary.get('total_files', 0)}\n")
                f.write(f"- 总问题数: {summary.get('total_issues', 0)}\n")
                f.write(f"- 平均评分: {summary.get('average_score', 0):.1f}/100\n")
                f.write(f"- 有错误的文件数: {summary.get('files_with_errors', 0)}\n\n")
                
                # 问题详情
                files = report_data.get("files", [])
                f.write("## 文件详情\n\n")
                for file_data in files:
                    file_name = file_data.get("file_name", "")
                    score = file_data.get("score", 0)
                    issues = file_data.get("issues", [])
                    
                    f.write(f"### {file_name}\n\n")
                    f.write(f"**评分**: {score}/100\n\n")
                    
                    if issues:
                        f.write("**问题列表**:\n\n")
                        for issue in issues:
                            severity = issue.get("severity", "")
                            message = issue.get("message", "")
                            line = issue.get("line_number", 0)
                            
                            emoji = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(severity, "📝")
                            f.write(f"- {emoji} 第{line}行: {message}\n")
                    else:
                        f.write("✅ 无问题\n")
                    
                    f.write("\n")
    
    def run_git_hooks(self, path: str):
        """运行Git钩子"""
        print("🔧 设置Git钩子...")
        
        # 创建pre-commit钩子
        hook_content = f"""#!/bin/bash
# 自动生成的代码评审钩子

echo "🔍 运行代码评审..."
python3 {Path(__file__).parent}/ci_integration.py {path} --min-score 70 --max-errors 0

if [ $? -ne 0 ]; then
    echo "❌ 代码评审失败，提交被阻止"
    exit 1
fi

echo "✅ 代码评审通过，允许提交"
"""
        
        git_dir = Path(path) / ".git"
        if git_dir.exists():
            hooks_dir = git_dir / "hooks"
            hooks_dir.mkdir(exist_ok=True)
            
            pre_commit_hook = hooks_dir / "pre-commit"
            with open(pre_commit_hook, 'w') as f:
                f.write(hook_content)
            
            # 设置执行权限
            os.chmod(pre_commit_hook, 0o755)
            print(f"✅ Git pre-commit钩子已设置: {pre_commit_hook}")
        else:
            print("⚠️ 未找到Git仓库，跳过钩子设置")
    
    def run_continuous_review(self, path: str, watch_interval: int = 30):
        """持续监控代码变化"""
        print(f"👀 开始持续监控: {path} (间隔: {watch_interval}秒)")
        
        import time
        last_modified = {}
        
        while True:
            try:
                # 检查文件变化
                java_files = list(Path(path).rglob("*.java"))
                current_modified = {f: f.stat().st_mtime for f in java_files}
                
                # 找出变化的文件
                changed_files = []
                for file_path, mtime in current_modified.items():
                    if file_path not in last_modified or last_modified[file_path] != mtime:
                        changed_files.append(file_path)
                
                if changed_files:
                    print(f"📝 检测到文件变化: {[f.name for f in changed_files]}")
                    
                    # 运行评审
                    report_data = self.run_code_review(path)
                    if report_data:
                        self.check_quality_gates(report_data)
                        
                        # 生成报告
                        timestamp = os.popen('date +%Y%m%d_%H%M%S').read().strip()
                        ci_report = Path(path) / f"ci_report_{timestamp}.md"
                        self.generate_ci_report(report_data, str(ci_report))
                        print(f"📄 CI报告已生成: {ci_report}")
                
                last_modified = current_modified
                time.sleep(watch_interval)
                
            except KeyboardInterrupt:
                print("\n👋 停止持续监控")
                break
            except Exception as e:
                print(f"❌ 监控过程中出错: {e}")
                time.sleep(watch_interval)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='CI/CD代码质量集成工具')
    parser.add_argument('path', help='要监控的Java项目路径')
    parser.add_argument('--min-score', type=float, default=70.0, help='最低质量评分')
    parser.add_argument('--max-errors', type=int, default=0, help='最大错误数量')
    parser.add_argument('--max-warnings', type=int, default=10, help='最大警告数量')
    parser.add_argument('--use-ai', action='store_true', help='使用AI增强评审')
    parser.add_argument('--setup-hooks', action='store_true', help='设置Git钩子')
    parser.add_argument('--watch', action='store_true', help='持续监控模式')
    parser.add_argument('--watch-interval', type=int, default=30, help='监控间隔(秒)')
    
    args = parser.parse_args()
    
    # 创建CI集成实例
    ci = CIIntegration(args.min_score, args.max_errors, args.max_warnings)
    
    # 设置Git钩子
    if args.setup_hooks:
        ci.run_git_hooks(args.path)
    
    # 持续监控模式
    if args.watch:
        ci.run_continuous_review(args.path, args.watch_interval)
        return
    
    # 单次评审
    print("🚀 开始CI/CD代码质量检查...")
    
    # 运行代码评审
    report_data = ci.run_code_review(args.path, args.use_ai)
    
    if not report_data:
        print("❌ 代码评审失败")
        sys.exit(1)
    
    # 检查质量门禁
    if ci.check_quality_gates(report_data):
        print("✅ 质量门禁检查通过")
        
        # 生成CI报告
        timestamp = os.popen('date +%Y%m%d_%H%M%S').read().strip()
        ci_report = Path(args.path) / f"ci_report_{timestamp}.md"
        ci.generate_ci_report(report_data, str(ci_report))
        print(f"📄 CI报告已生成: {ci_report}")
        
        sys.exit(0)
    else:
        print("❌ 质量门禁检查失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
