#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Java代码自动评审工具
功能：检查代码风格、线程安全、日志、异常处理等
输出：结构化评审报告（JSON和Markdown格式）
"""

import os
import re
import json
import ast
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import argparse


@dataclass
class CodeIssue:
    """代码问题"""
    line_number: int
    severity: str  # "error", "warning", "info"
    category: str  # "style", "thread_safety", "logging", "exception", "performance"
    message: str
    suggestion: str


@dataclass
class ReviewResult:
    """评审结果"""
    file_path: str
    file_name: str
    total_lines: int
    issues: List[CodeIssue]
    score: float  # 0-100
    summary: str


class JavaCodeReviewer:
    """Java代码评审器"""
    
    def __init__(self):
        self.issues = []
        self.current_file = ""
        
    def review_file(self, file_path: str) -> ReviewResult:
        """评审单个Java文件"""
        self.issues = []
        self.current_file = file_path
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            return ReviewResult(
                file_path=file_path,
                file_name=os.path.basename(file_path),
                total_lines=0,
                issues=[CodeIssue(0, "error", "file", f"无法读取文件: {e}", "检查文件路径和权限")],
                score=0,
                summary="文件读取失败"
            )
        
        # 执行各种检查
        self._check_code_style(lines)
        self._check_code_style_additional(lines)
        self._check_thread_safety(lines)
        self._check_logging(lines)
        self._check_exception_handling(lines)
        self._check_performance(lines)
        self._check_best_practices(lines)
        
        # 计算评分
        score = self._calculate_score(len(lines))
        
        # 生成摘要
        summary = self._generate_summary()
        
        return ReviewResult(
            file_path=file_path,
            file_name=os.path.basename(file_path),
            total_lines=len(lines),
            issues=self.issues,
            score=score,
            summary=summary
        )
    
    def _check_code_style(self, lines: List[str]):
        """检查代码风格"""
        for i, line in enumerate(lines, 1):
            original_line = line
            line = line.strip()
            
            # 跳过空行和注释
            if not line or line.startswith('//') or line.startswith('*') or line.startswith('/*'):
                continue
            
            # 简化的缩进检查 - 只检查明显的缩进问题
            # 检查顶级声明（类、接口、枚举等）不应该有缩进
            if (line.startswith('public class') or line.startswith('class ') or 
                line.startswith('public interface') or line.startswith('interface ') or
                line.startswith('public enum') or line.startswith('enum ') or
                line.startswith('package ') or line.startswith('import ')):
                
                if original_line.startswith(' ') or original_line.startswith('\t'):
                    self.issues.append(CodeIssue(
                        i, "warning", "style",
                        "顶级声明不应有缩进",
                        "移除不必要的缩进"
                    ))
            
            # 检查方法体内容应该有缩进（简化检查）
            elif (line.startswith('{') or line.startswith('}') or 
                  line.startswith('if') or line.startswith('for') or 
                  line.startswith('while') or line.startswith('try') or
                  line.startswith('catch') or line.startswith('finally') or
                  line.startswith('return') or line.startswith('throw')):
                
                # 只检查明显缺少缩进的情况
                if (not original_line.startswith(' ') and not original_line.startswith('\t') and
                    not line.startswith('public') and not line.startswith('private') and
                    not line.startswith('protected') and not line.startswith('static')):
                    # 进一步检查是否真的需要缩进
                    if self._needs_indentation(line, i, lines):
                        self.issues.append(CodeIssue(
                            i, "warning", "style",
                            "代码块缺少适当缩进",
                            "使用4个空格进行缩进"
                        ))
    
    def _needs_indentation(self, line: str, line_num: int, lines: List[str]) -> bool:
        """检查行是否需要缩进"""
        # 检查是否在方法体、类体等需要缩进的上下文中
        for i in range(max(0, line_num - 10), line_num):
            prev_line = lines[i].strip()
            if ('{' in prev_line and 
                not prev_line.startswith('//') and 
                not prev_line.startswith('*')):
                return True
        return False
    
    def _check_code_style_additional(self, lines: List[str]):
        """检查额外的代码风格问题"""
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 检查行长度
            if len(line) > 120:
                self.issues.append(CodeIssue(
                    i, "info", "style",
                    f"行长度过长 ({len(line)} 字符)",
                    "考虑将长行拆分为多行"
                ))
            
            # 检查空行使用
            if i > 1 and lines[i-2].strip() and line and not line.startswith('//'):
                if not any(keyword in line for keyword in ['public', 'private', 'protected', 'static', 'class', 'interface']):
                    if not any(keyword in lines[i-2] for keyword in ['{', '}', ';']):
                        pass  # 这里可以添加更复杂的空行检查逻辑
            
            # 检查命名规范
            if re.match(r'^[a-z][a-zA-Z0-9]*\s*\(', line):  # 方法名
                method_name = re.match(r'^([a-z][a-zA-Z0-9]*)', line)
                if method_name and not re.match(r'^[a-z][a-zA-Z0-9]*$', method_name.group(1)):
                    self.issues.append(CodeIssue(
                        i, "warning", "style",
                        "方法名不符合驼峰命名规范",
                        "方法名应以小写字母开头，使用驼峰命名法"
                    ))
    
    def _check_thread_safety(self, lines: List[str]):
        """检查线程安全"""
        has_thread_local = False
        has_synchronized = False
        has_volatile = False
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 检查ThreadLocal使用 - 这是正确的线程安全实践
            if 'ThreadLocal' in line:
                has_thread_local = True
                if 'ThreadLocal<SimpleDateFormat>' in line:
                    self.issues.append(CodeIssue(
                        i, "info", "thread_safety",
                        "使用了ThreadLocal包装SimpleDateFormat",
                        "这是处理SimpleDateFormat线程安全的最佳实践"
                    ))
            
            # 检查synchronized使用
            if 'synchronized' in line:
                has_synchronized = True
                if 'synchronized (sdf)' in line:
                    self.issues.append(CodeIssue(
                        i, "info", "thread_safety",
                        "使用了synchronized关键字",
                        "确保了对共享资源的同步访问"
                    ))
            
            # 检查volatile使用
            if 'volatile' in line:
                has_volatile = True
            
            # 检查静态SimpleDateFormat - 只有在没有ThreadLocal保护时才报错
            if re.match(r'^\s*private\s+static\s+', line):
                if 'SimpleDateFormat' in line and 'ThreadLocal' not in line:
                    # 检查是否在类级别有ThreadLocal保护
                    class_has_threadlocal = False
                    for j in range(max(0, i-20), min(len(lines), i+20)):
                        if 'ThreadLocal<SimpleDateFormat>' in lines[j]:
                            class_has_threadlocal = True
                            break
                    
                    if not class_has_threadlocal:
                        self.issues.append(CodeIssue(
                            i, "error", "thread_safety",
                            "静态SimpleDateFormat不是线程安全的",
                            "使用ThreadLocal包装或每次创建新实例"
                        ))
    
    def _check_logging(self, lines: List[str]):
        """检查日志使用"""
        has_logger = False
        has_system_out = False
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 检查System.out.println使用
            if 'System.out.println' in line:
                has_system_out = True
                self.issues.append(CodeIssue(
                    i, "warning", "logging",
                    "使用了System.out.println进行输出",
                    "建议使用专业的日志框架如SLF4J + Logback"
                ))
            
            # 检查System.err.println使用
            if 'System.err.println' in line:
                self.issues.append(CodeIssue(
                    i, "warning", "logging",
                    "使用了System.err.println进行错误输出",
                    "建议使用日志框架的ERROR级别"
                ))
            
            # 检查日志框架
            if 'Logger' in line or 'log.' in line:
                has_logger = True
            
            # 检查异常处理中的日志
            if 'catch' in line and 'Exception' in line:
                # 检查catch块中是否有日志记录
                catch_line = i
                has_log_in_catch = False
                for j in range(i, min(i + 10, len(lines))):
                    if 'log.' in lines[j] or 'Logger' in lines[j] or 'System.out' in lines[j]:
                        has_log_in_catch = True
                        break
                
                if not has_log_in_catch:
                    self.issues.append(CodeIssue(
                        catch_line, "warning", "logging",
                        "异常处理中缺少日志记录",
                        "在catch块中记录异常信息，便于调试和监控"
                    ))
    
    def _check_exception_handling(self, lines: List[str]):
        """检查异常处理"""
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 检查空的catch块
            if 'catch' in line and 'Exception' in line:
                # 查找对应的catch块内容
                brace_count = 0
                catch_content = []
                in_catch_block = False
                
                for j in range(i, len(lines)):
                    current_line = lines[j].strip()
                    
                    # 开始计算大括号
                    if '{' in current_line:
                        brace_count += current_line.count('{')
                        in_catch_block = True
                    if '}' in current_line:
                        brace_count -= current_line.count('}')
                    
                    if in_catch_block and brace_count > 0:
                        catch_content.append(current_line)
                    
                    # 如果大括号平衡了，说明catch块结束
                    if in_catch_block and brace_count <= 0 and j > i:
                        break
                
                # 检查catch块是否为空或只有注释
                non_comment_content = [l for l in catch_content if l and not l.startswith('//') and not l.startswith('*') and not l.startswith('/*')]
                if not non_comment_content:
                    self.issues.append(CodeIssue(
                        i, "error", "exception",
                        "空的catch块",
                        "至少应该记录异常或重新抛出"
                    ))
            
            # 检查throws声明
            if 'throws' in line and 'Exception' in line:
                if 'throws Exception' in line:
                    self.issues.append(CodeIssue(
                        i, "warning", "exception",
                        "抛出了通用的Exception",
                        "应该抛出更具体的异常类型，如IOException、IllegalArgumentException等"
                    ))
            
            # 检查空值检查
            if 'null' in line and ('==' in line or '!=' in line):
                if 'null ==' in line or 'null !=' in line:
                    self.issues.append(CodeIssue(
                        i, "info", "null_safety",
                        "使用了null == 或 null != 的比较方式",
                        "建议使用Objects.equals()或Objects.isNull()/Objects.nonNull()"
                    ))
            
            # 检查可能的空指针异常风险
            if ('.' in line and not line.startswith('//') and 
                not any(keyword in line for keyword in ['import', 'package', 'class', 'interface'])):
                # 检查链式调用但没有空值检查
                if line.count('.') > 2 and 'null' not in line and 'if' not in line:
                    self.issues.append(CodeIssue(
                        i, "warning", "null_safety",
                        "链式调用可能存在空指针异常风险",
                        "建议添加空值检查或使用Optional"
                    ))
    
    def _check_performance(self, lines: List[str]):
        """检查性能问题"""
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 检查String拼接
            if '+' in line and 'String' in line:
                if line.count('+') > 3:
                    self.issues.append(CodeIssue(
                        i, "warning", "performance",
                        "多次字符串拼接可能影响性能",
                        "考虑使用StringBuilder"
                    ))
            
            # 检查循环中的字符串操作
            if 'for' in line and ('String' in line or '+' in line):
                self.issues.append(CodeIssue(
                    i, "info", "performance",
                    "循环中可能存在字符串操作",
                    "检查是否需要使用StringBuilder"
                ))
    
    def _check_best_practices(self, lines: List[str]):
        """检查最佳实践"""
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 检查魔法数字
            if re.search(r'\b\d{2,}\b', line) and not re.search(r'(0x|0b)', line):
                self.issues.append(CodeIssue(
                    i, "info", "style",
                    "可能存在魔法数字",
                    "考虑定义为常量"
                ))
            
            # 检查TODO/FIXME
            if 'TODO' in line or 'FIXME' in line:
                self.issues.append(CodeIssue(
                    i, "info", "style",
                    "发现TODO或FIXME标记",
                    "及时处理待办事项"
                ))
    
    def _calculate_score(self, total_lines: int) -> float:
        """计算代码质量评分"""
        if not self.issues:
            return 100.0
        
        # 根据问题严重程度扣分
        error_count = sum(1 for issue in self.issues if issue.severity == "error")
        warning_count = sum(1 for issue in self.issues if issue.severity == "warning")
        info_count = sum(1 for issue in self.issues if issue.severity == "info")
        
        # 计算扣分
        error_penalty = error_count * 10
        warning_penalty = warning_count * 5
        info_penalty = info_count * 1
        
        total_penalty = error_penalty + warning_penalty + info_penalty
        
        # 根据代码行数调整扣分比例
        penalty_ratio = min(total_penalty / max(total_lines, 1), 1.0)
        
        score = max(0, 100 - (penalty_ratio * 100))
        return round(score, 1)
    
    def _generate_summary(self) -> str:
        """生成评审摘要"""
        if not self.issues:
            return "代码质量优秀，未发现明显问题。"
        
        error_count = sum(1 for issue in self.issues if issue.severity == "error")
        warning_count = sum(1 for issue in self.issues if issue.severity == "warning")
        info_count = sum(1 for issue in self.issues if issue.severity == "info")
        
        summary_parts = []
        if error_count > 0:
            summary_parts.append(f"{error_count}个错误")
        if warning_count > 0:
            summary_parts.append(f"{warning_count}个警告")
        if info_count > 0:
            summary_parts.append(f"{info_count}个建议")
        
        return f"发现{', '.join(summary_parts)}，需要关注和改进。"


class ReportGenerator:
    """报告生成器"""
    
    @staticmethod
    def generate_json_report(results: List[ReviewResult], output_file: str):
        """生成JSON格式报告"""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(results),
            "files": [asdict(result) for result in results],
            "summary": {
                "total_issues": sum(len(result.issues) for result in results),
                "average_score": sum(result.score for result in results) / len(results) if results else 0,
                "files_with_errors": sum(1 for result in results if any(issue.severity == "error" for issue in result.issues))
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def generate_markdown_report(results: List[ReviewResult], output_file: str):
        """生成Markdown格式报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Java代码评审报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 总体统计
            total_issues = sum(len(result.issues) for result in results)
            avg_score = sum(result.score for result in results) / len(results) if results else 0
            files_with_errors = sum(1 for result in results if any(issue.severity == "error" for issue in result.issues))
            
            f.write("## 总体统计\n\n")
            f.write(f"- **评审文件数**: {len(results)}\n")
            f.write(f"- **总问题数**: {total_issues}\n")
            f.write(f"- **平均评分**: {avg_score:.1f}/100\n")
            f.write(f"- **有错误的文件数**: {files_with_errors}\n\n")
            
            # 详细报告
            f.write("## 详细报告\n\n")
            for result in results:
                f.write(f"### {result.file_name}\n\n")
                f.write(f"**文件路径**: `{result.file_path}`\n\n")
                f.write(f"**代码行数**: {result.total_lines}\n\n")
                f.write(f"**质量评分**: {result.score}/100\n\n")
                f.write(f"**问题摘要**: {result.summary}\n\n")
                
                if result.issues:
                    f.write("#### 问题详情\n\n")
                    for issue in result.issues:
                        severity_emoji = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(issue.severity, "📝")
                        f.write(f"- **第{issue.line_number}行** {severity_emoji} **{issue.severity.upper()}** ({issue.category})\n")
                        f.write(f"  - **问题**: {issue.message}\n")
                        f.write(f"  - **建议**: {issue.suggestion}\n\n")
                else:
                    f.write("✅ 未发现问题\n\n")
                
                f.write("---\n\n")


def find_java_files(directory: str) -> List[str]:
    """查找目录下的所有Java文件"""
    java_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.java'):
                java_files.append(os.path.join(root, file))
    return java_files


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Java代码自动评审工具')
    parser.add_argument('path', help='要评审的Java文件或目录路径')
    parser.add_argument('--output-dir', '-o', default='./reports', help='报告输出目录')
    parser.add_argument('--format', '-f', choices=['json', 'markdown', 'both'], default='both', help='输出格式')
    
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 查找Java文件
    if os.path.isfile(args.path) and args.path.endswith('.java'):
        java_files = [args.path]
    elif os.path.isdir(args.path):
        java_files = find_java_files(args.path)
    else:
        print(f"错误: 路径 {args.path} 不存在或不是有效的Java文件/目录")
        return
    
    if not java_files:
        print("未找到Java文件")
        return
    
    print(f"找到 {len(java_files)} 个Java文件，开始评审...")
    
    # 执行评审
    reviewer = JavaCodeReviewer()
    results = []
    
    for java_file in java_files:
        print(f"正在评审: {java_file}")
        result = reviewer.review_file(java_file)
        results.append(result)
        print(f"  评分: {result.score}/100, 问题数: {len(result.issues)}")
    
    # 生成报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if args.format in ['json', 'both']:
        json_file = os.path.join(args.output_dir, f'java_review_{timestamp}.json')
        ReportGenerator.generate_json_report(results, json_file)
        print(f"JSON报告已生成: {json_file}")
    
    if args.format in ['markdown', 'both']:
        md_file = os.path.join(args.output_dir, f'java_review_{timestamp}.md')
        ReportGenerator.generate_markdown_report(results, md_file)
        print(f"Markdown报告已生成: {md_file}")
    
    # 输出简要统计
    total_issues = sum(len(result.issues) for result in results)
    avg_score = sum(result.score for result in results) / len(results) if results else 0
    print(f"\n评审完成!")
    print(f"总文件数: {len(results)}")
    print(f"总问题数: {total_issues}")
    print(f"平均评分: {avg_score:.1f}/100")


if __name__ == "__main__":
    main()
