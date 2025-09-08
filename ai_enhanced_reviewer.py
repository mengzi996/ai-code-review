#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI增强的Java代码评审工具
结合基础代码分析和AI深度分析
"""

import os
import re
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import argparse

# 导入基础评审器
from java_code_reviewer import JavaCodeReviewer, ReportGenerator, CodeIssue, ReviewResult


class AIEnhancedReviewer(JavaCodeReviewer):
    """AI增强的代码评审器"""
    
    def __init__(self, ollama_api="http://localhost:11434/api/generate", model="deepseek-coder:6.7b"):
        super().__init__()
        self.ollama_api = ollama_api
        self.model = model
    
    def call_ollama(self, prompt: str) -> str:
        """调用Ollama API进行AI分析"""
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.ollama_api, json=data, timeout=30)
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f"AI分析失败: {e}"
    
    def review_file_with_ai(self, file_path: str) -> ReviewResult:
        """使用AI增强评审单个Java文件"""
        # 先进行基础评审
        result = self.review_file(file_path)
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return result
        
        # 进行AI深度分析
        ai_issues = self._ai_code_analysis(content, file_path)
        
        # 合并AI分析结果
        result.issues.extend(ai_issues)
        
        # 重新计算评分
        result.score = self._calculate_score(result.total_lines)
        result.summary = self._generate_summary()
        
        return result
    
    def _ai_code_analysis(self, content: str, file_path: str) -> List[CodeIssue]:
        """使用AI进行深度代码分析"""
        ai_issues = []

        # 构建AI分析提示
        prompt = f"""
        你是一位资深 Java 架构师，正在评审一段生产级代码。请严格遵循以下规则：
        ## 🔍 评审重点
        1. **日志记录**
           - 是否使用 SLF4J（如 `LoggerFactory.getLogger`）
           - 异常是否记录了上下文和堆栈
           - 日志级别是否合理（error/warn/info/debug）
        2. **异常处理**
           - 是否捕获了具体异常（如 `ParseException` 而不是 `Exception`）
           - 是否向上抛出而非包装成 `RuntimeException`
           - 是否有空的 catch 块
        3. **空值检查**
           - 方法入口是否校验 `null` 参数
           - 是否抛出 `IllegalArgumentException`
        4. **代码可读性**
           - 命名是否清晰（如 `DATE_FORMATTER` 而不是 `sdfThreadLocal`）
           - 是否有必要的注释
           - 方法是否过长
        5. **线程安全**
           - `ThreadLocal<SimpleDateFormat>` 是**正确做法**，应给予正面评价
           - `synchronized` 是双重保险，可以保留
           - 禁止建议使用 `new SimpleDateFormat()` 替代 ThreadLocal**（线程不安全！）
        重要提醒：
        - 不要误报缩进问题
        - 不要建议用 new SimpleDateFormat() 替代 ThreadLocal
        - 如果使用了 ThreadLocal<SimpleDateFormat>，应正面评价
        - 异常应建议 throws ParseException 而非 Exception
        - 不要建议删除 `ThreadLocal`
        - 不要建议抛出 `RuntimeException`
        - 不要生成无效测试或错误示例

        ## 📄 输出要求

        - 仅返回 JSON
        - 不要解释
        - 严格按照以下格式：

        {{
            "issues": [
                {{
                    "line_number": 12,
                    "severity": "warning", 
                    "category": "exception",
                    "message": "抛出了通用 Exception",
                    "suggestion": "应声明 throws ParseException"
                }}
            ],
            "summary": {{
                "total_issues": 3,
                "quality_score": 75,
                "overall": "代码结构良好，建议改进异常处理和日志记录"
            }}
        }}

Java代码：
```java
{content}
```

请只返回JSON格式的结果，不要包含其他内容。
"""
        
        try:
            ai_response = self.call_ollama(prompt)
            
            # 尝试解析AI返回的JSON
            if "```json" in ai_response:
                start = ai_response.find("```json") + 7
                end = ai_response.find("```", start)
                json_str = ai_response[start:end].strip()
            elif "```" in ai_response:
                start = ai_response.find("```") + 3
                end = ai_response.find("```", start)
                json_str = ai_response[start:end].strip()
            else:
                json_str = ai_response.strip()
            
            # 解析JSON
            try:
                ai_data = json.loads(json_str)
                if "issues" in ai_data:
                    for issue_data in ai_data["issues"]:
                        ai_issues.append(CodeIssue(
                            line_number=issue_data.get("line_number", 0),
                            severity=issue_data.get("severity", "info"),
                            category=issue_data.get("category", "ai_analysis"),
                            message=issue_data.get("message", ""),
                            suggestion=issue_data.get("suggestion", "")
                        ))
            except json.JSONDecodeError:
                # 如果JSON解析失败，创建一个通用的AI分析问题
                ai_issues.append(CodeIssue(
                    line_number=0,
                    severity="info",
                    category="ai_analysis",
                    message="AI分析完成，但结果解析失败",
                    suggestion="请检查AI服务是否正常运行"
                ))
                
        except Exception as e:
            ai_issues.append(CodeIssue(
                line_number=0,
                severity="warning",
                category="ai_analysis",
                message=f"AI分析失败: {e}",
                suggestion="请检查Ollama服务是否运行"
            ))
        
        return ai_issues
    
    def generate_improvement_suggestions(self, file_path: str) -> str:
        """生成代码改进建议"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return f"无法读取文件: {e}"
        
        prompt = f"""
请为以下Java代码提供具体的改进建议，重点关注：

1. 日志记录改进：建议使用SLF4J + Logback替代System.out.println
2. 异常处理改进：完善异常处理逻辑，添加适当的日志记录
3. 空值检查改进：添加空值检查，避免空指针异常
4. 代码可读性提升：改进命名、添加注释、优化代码结构
5. 最佳实践应用：遵循Java编码规范和最佳实践

重要提醒：
- 如果代码使用了ThreadLocal<SimpleDateFormat>，这是正确的做法，不要建议删除
- 不要建议用new SimpleDateFormat()替代ThreadLocal
- 重点关注日志、异常处理、空值检查、代码可读性

请提供具体的代码示例和改进方案。

Java代码：
```java
{content}
```
"""
        
        return self.call_ollama(prompt)
    
    def generate_unit_tests(self, file_path: str) -> str:
        """生成单元测试建议"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return f"无法读取文件: {e}"
        
        prompt = f"""
请为以下Java代码生成JUnit单元测试，包括：

1. 正常情况测试
2. 边界条件测试
3. 异常情况测试
4. 参数验证测试
5. 性能测试建议

请提供完整的测试代码示例。

Java代码：
```java
{content}
```
"""
        
        return self.call_ollama(prompt)


class EnhancedReportGenerator(ReportGenerator):
    """增强的报告生成器"""
    
    @staticmethod
    def generate_comprehensive_report(results: List[ReviewResult], output_file: str, 
                                    improvement_suggestions: Dict[str, str] = None,
                                    unit_test_suggestions: Dict[str, str] = None):
        """生成综合报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Java代码综合评审报告\n\n")
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
            
            # 问题分类统计
            issue_categories = {}
            for result in results:
                for issue in result.issues:
                    category = issue.category
                    if category not in issue_categories:
                        issue_categories[category] = {"error": 0, "warning": 0, "info": 0}
                    issue_categories[category][issue.severity] += 1
            
            f.write("## 问题分类统计\n\n")
            for category, counts in issue_categories.items():
                f.write(f"### {category}\n")
                f.write(f"- 错误: {counts['error']}\n")
                f.write(f"- 警告: {counts['warning']}\n")
                f.write(f"- 建议: {counts['info']}\n\n")
            
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
                
                # AI改进建议
                if improvement_suggestions and result.file_path in improvement_suggestions:
                    f.write("#### AI改进建议\n\n")
                    f.write("```\n")
                    f.write(improvement_suggestions[result.file_path])
                    f.write("\n```\n\n")
                
                # 单元测试建议
                if unit_test_suggestions and result.file_path in unit_test_suggestions:
                    f.write("#### 单元测试建议\n\n")
                    f.write("```java\n")
                    f.write(unit_test_suggestions[result.file_path])
                    f.write("\n```\n\n")
                
                f.write("---\n\n")
            
            # 总结和建议
            f.write("## 总结和建议\n\n")
            if avg_score >= 80:
                f.write("🎉 代码质量整体良好！继续保持。\n\n")
            elif avg_score >= 60:
                f.write("📈 代码质量中等，建议关注警告和建议项。\n\n")
            else:
                f.write("⚠️ 代码质量需要改进，建议优先处理错误和警告项。\n\n")
            
            f.write("### 改进优先级\n\n")
            f.write("1. **高优先级**: 修复所有错误项\n")
            f.write("2. **中优先级**: 处理警告项\n")
            f.write("3. **低优先级**: 考虑建议项\n\n")
            
            f.write("### 后续行动\n\n")
            f.write("- [ ] 修复所有错误项\n")
            f.write("- [ ] 处理高优先级警告\n")
            f.write("- [ ] 添加单元测试\n")
            f.write("- [ ] 重构代码结构\n")
            f.write("- [ ] 优化性能瓶颈\n\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI增强的Java代码评审工具')
    parser.add_argument('path', help='要评审的Java文件或目录路径')
    parser.add_argument('--output-dir', '-o', default='./reports', help='报告输出目录')
    parser.add_argument('--format', '-f', choices=['json', 'markdown', 'both', 'comprehensive'], 
                       default='comprehensive', help='输出格式')
    parser.add_argument('--ollama-api', default='http://localhost:11434/api/generate', 
                       help='Ollama API地址')
    parser.add_argument('--model', default='deepseek-coder:6.7b', help='使用的AI模型')
    parser.add_argument('--no-ai', action='store_true', help='禁用AI分析')
    
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 查找Java文件
    if os.path.isfile(args.path) and args.path.endswith('.java'):
        java_files = [args.path]
    elif os.path.isdir(args.path):
        from java_code_reviewer import find_java_files
        java_files = find_java_files(args.path)
    else:
        print(f"错误: 路径 {args.path} 不存在或不是有效的Java文件/目录")
        return
    
    if not java_files:
        print("未找到Java文件")
        return
    
    print(f"找到 {len(java_files)} 个Java文件，开始评审...")
    
    # 执行评审
    if args.no_ai:
        reviewer = JavaCodeReviewer()
        review_method = reviewer.review_file
    else:
        reviewer = AIEnhancedReviewer(args.ollama_api, args.model)
        review_method = reviewer.review_file_with_ai
    
    results = []
    improvement_suggestions = {}
    unit_test_suggestions = {}
    
    for java_file in java_files:
        print(f"正在评审: {java_file}")
        result = review_method(java_file)
        results.append(result)
        print(f"  评分: {result.score}/100, 问题数: {len(result.issues)}")
        
        # 生成AI建议（如果启用）
        if not args.no_ai and isinstance(reviewer, AIEnhancedReviewer):
            print(f"  生成改进建议...")
            improvement_suggestions[java_file] = reviewer.generate_improvement_suggestions(java_file)
            
            print(f"  生成测试建议...")
            unit_test_suggestions[java_file] = reviewer.generate_unit_tests(java_file)
    
    # 生成报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if args.format in ['json', 'both']:
        json_file = os.path.join(args.output_dir, f'ai_java_review_{timestamp}.json')
        ReportGenerator.generate_json_report(results, json_file)
        print(f"JSON报告已生成: {json_file}")
    
    if args.format in ['markdown', 'both']:
        md_file = os.path.join(args.output_dir, f'ai_java_review_{timestamp}.md')
        ReportGenerator.generate_markdown_report(results, md_file)
        print(f"Markdown报告已生成: {md_file}")
    
    if args.format in ['comprehensive']:
        comp_file = os.path.join(args.output_dir, f'ai_java_review_comprehensive_{timestamp}.md')
        EnhancedReportGenerator.generate_comprehensive_report(
            results, comp_file, improvement_suggestions, unit_test_suggestions
        )
        print(f"综合报告已生成: {comp_file}")
    
    # 输出简要统计
    total_issues = sum(len(result.issues) for result in results)
    avg_score = sum(result.score for result in results) / len(results) if results else 0
    print(f"\n评审完成!")
    print(f"总文件数: {len(results)}")
    print(f"总问题数: {total_issues}")
    print(f"平均评分: {avg_score:.1f}/100")
    
    if not args.no_ai:
        print(f"AI分析: 已生成改进建议和测试建议")


if __name__ == "__main__":
    main()
