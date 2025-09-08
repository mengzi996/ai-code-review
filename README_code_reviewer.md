# Java代码自动评审工具

这是一个Python脚本，用于自动读取Java文件并进行代码评审，检查代码风格、线程安全、日志、异常处理等方面，并输出结构化的评审报告。

## 功能特性

### 代码检查项目
- **代码风格**: 缩进、行长度、命名规范、空行使用
- **线程安全**: ThreadLocal使用、synchronized关键字、静态变量安全性
- **日志记录**: System.out.println使用、日志框架使用、异常日志记录
- **异常处理**: 空catch块、异常类型、异常处理完整性
- **性能优化**: 字符串拼接、循环中的字符串操作
- **最佳实践**: 魔法数字、TODO标记、代码规范

### 输出格式
- **JSON格式**: 结构化数据，便于程序处理
- **Markdown格式**: 人类可读的报告，包含详细说明

## 使用方法

### 1. 基本使用

```bash
# 评审单个Java文件
python java_code_reviewer.py DateUtils.java

# 评审整个目录
python java_code_reviewer.py /path/to/java/project

# 评审当前目录
python java_code_reviewer.py .
```

### 2. 高级选项

```bash
# 指定输出目录
python java_code_reviewer.py . --output-dir ./my_reports

# 只生成JSON报告
python java_code_reviewer.py . --format json

# 只生成Markdown报告
python java_code_reviewer.py . --format markdown

# 生成两种格式的报告
python java_code_reviewer.py . --format both
```

### 3. 快速运行

使用提供的快速运行脚本：

```bash
python run_review.py
```

## 输出示例

### 控制台输出
```
找到 3 个Java文件，开始评审...
正在评审: /path/to/DateUtils.java
  评分: 85.0/100, 问题数: 2
正在评审: /path/to/FileUtils.java
  评分: 70.0/100, 问题数: 4
正在评审: /path/to/StringUtils.java
  评分: 95.0/100, 问题数: 1

评审完成!
总文件数: 3
总问题数: 7
平均评分: 83.3/100
```

### JSON报告结构
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "total_files": 3,
  "files": [
    {
      "file_path": "/path/to/DateUtils.java",
      "file_name": "DateUtils.java",
      "total_lines": 27,
      "score": 85.0,
      "summary": "发现2个建议，需要关注和改进。",
      "issues": [
        {
          "line_number": 12,
          "severity": "warning",
          "category": "logging",
          "message": "使用了System.out.println进行输出",
          "suggestion": "建议使用专业的日志框架如SLF4J + Logback"
        }
      ]
    }
  ],
  "summary": {
    "total_issues": 7,
    "average_score": 83.3,
    "files_with_errors": 0
  }
}
```

### Markdown报告
生成详细的Markdown报告，包含：
- 总体统计信息
- 每个文件的详细分析
- 问题分类和严重程度
- 具体的改进建议

## 评分机制

代码质量评分基于以下规则：
- **错误 (error)**: 每个扣10分
- **警告 (warning)**: 每个扣5分  
- **建议 (info)**: 每个扣1分
- 最终分数 = max(0, 100 - 扣分比例 × 100)

## 集成到CI/CD

可以将此工具集成到持续集成流程中：

```bash
# 在CI脚本中运行
python java_code_reviewer.py src/main/java --format json --output-dir reports

# 检查是否有严重问题
if grep -q '"severity": "error"' reports/*.json; then
    echo "发现严重代码问题，构建失败"
    exit 1
fi
```

## 扩展功能

### 添加自定义检查规则
可以在`JavaCodeReviewer`类中添加新的检查方法：

```python
def _check_custom_rule(self, lines: List[str]):
    """自定义检查规则"""
    for i, line in enumerate(lines, 1):
        # 添加你的检查逻辑
        pass
```

### 集成AI代码分析
可以结合现有的`generate_utils.py`，让AI进一步分析代码：

```python
def analyze_with_ai(self, code_content: str):
    """使用AI进行深度代码分析"""
    # 调用Ollama API进行更深入的分析
    pass
```

## 依赖要求

- Python 3.6+
- 标准库模块（无需额外安装）

## 文件结构

```
.
├── java_code_reviewer.py    # 主评审工具
├── run_review.py           # 快速运行脚本
├── generate_utils.py       # 原有的代码生成工具
├── DateUtils.java          # 示例Java文件
├── FileUtils.java          # 示例Java文件
├── StringUtils.java        # 示例Java文件
└── reports/                # 生成的报告目录
    ├── java_review_20240115_103000.json
    └── java_review_20240115_103000.md
```

## 注意事项

1. 工具会递归扫描指定目录下的所有`.java`文件
2. 报告文件会以时间戳命名，避免覆盖
3. 建议在代码提交前运行此工具进行检查
4. 可以根据团队规范调整检查规则和评分标准
