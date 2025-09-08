#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行Java代码评审的示例脚本
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    """运行代码评审"""
    # 获取当前目录
    current_dir = Path(__file__).parent
    
    # 检查Java文件是否存在
    java_files = list(current_dir.glob("*.java"))
    if not java_files:
        print("当前目录下没有找到Java文件")
        return
    
    print(f"找到 {len(java_files)} 个Java文件:")
    for file in java_files:
        print(f"  - {file.name}")
    
    # 运行代码评审
    print("\n开始运行代码评审...")
    try:
        result = subprocess.run([
            sys.executable, 
            "java_code_reviewer.py", 
            str(current_dir),
            "--format", "both"
        ], capture_output=True, text=True, cwd=current_dir)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ 代码评审完成!")
            
            # 检查生成的报告文件
            reports_dir = current_dir / "reports"
            if reports_dir.exists():
                report_files = list(reports_dir.glob("*"))
                if report_files:
                    print(f"\n生成的报告文件:")
                    for report_file in sorted(report_files):
                        print(f"  - {report_file.name}")
        else:
            print(f"\n❌ 代码评审失败，返回码: {result.returncode}")
            
    except Exception as e:
        print(f"运行代码评审时出错: {e}")

if __name__ == "__main__":
    main()
