# Java代码自动评审工具

一个功能完整的Java代码自动评审系统，实现"提交代码 → 自动评审"的初步自动化流程。

## 🚀 快速开始

### 1. 一键启动
```bash
./start_review.sh
```

### 2. 基础使用
```bash
# 评审当前目录的所有Java文件
python3 java_code_reviewer.py . --format both

# 使用AI增强评审
python3 ai_enhanced_reviewer.py . --format comprehensive

# CI/CD质量检查
python3 ci_integration.py . --min-score 70 --max-errors 0
```

## 📁 项目结构

```
.
├── java_code_reviewer.py          # 基础代码评审工具
├── ai_enhanced_reviewer.py        # AI增强评审工具  
├── ci_integration.py              # CI/CD集成工具
├── demo_usage.py                  # 使用演示脚本
├── start_review.sh                # 一键启动脚本
├── requirements.txt               # 依赖包列表
├── README_code_reviewer.md        # 详细使用说明
├── 项目总结.md                    # 项目总结文档
└── reports/                       # 生成的报告目录
```

## ✨ 核心功能

### 🔍 基础代码评审
- **代码风格**: 缩进、行长度、命名规范
- **线程安全**: ThreadLocal、synchronized检查
- **日志记录**: 专业日志框架使用检查
- **异常处理**: 空catch块、异常类型检查
- **性能优化**: 字符串拼接、循环优化
- **最佳实践**: 魔法数字、TODO标记检查

### 🤖 AI增强分析
- **智能分析**: 使用Ollama进行深度代码分析
- **改进建议**: 生成具体的代码重构建议
- **测试生成**: 自动生成单元测试代码
- **综合报告**: 结合基础分析和AI分析

### 🔄 CI/CD集成
- **质量门禁**: 可配置的评分和问题阈值
- **Git钩子**: 自动设置pre-commit检查
- **持续监控**: 实时监控代码变化
- **CI报告**: 生成适合CI/CD的质量报告

## 📊 评审示例

### 基础评审结果
```
找到 3 个Java文件，开始评审...
正在评审: ./StringUtils.java
  评分: 36.4/100, 问题数: 5
正在评审: ./FileUtils.java  
  评分: 0/100, 问题数: 10
正在评审: ./DateUtils.java
  评分: 0/100, 问题数: 14

评审完成!
总文件数: 3
总问题数: 29
平均评分: 12.1/100
```

### 发现的主要问题
- ❌ **错误**: 空的catch块、线程安全问题
- ⚠️ **警告**: 使用System.out.println、异常处理不当
- ℹ️ **建议**: 性能优化、代码风格改进

## 🛠️ 安装和使用

### 环境要求
- Python 3.6+
- requests库 (用于AI功能)

### 安装依赖
```bash
pip install -r requirements.txt
```

### 基础使用
```bash
# 1. 基础评审
python3 java_code_reviewer.py . --format both

# 2. AI增强评审 (需要Ollama服务)
python3 ai_enhanced_reviewer.py . --format comprehensive

# 3. CI质量检查
python3 ci_integration.py . --min-score 70 --max-errors 0

# 4. 运行演示
python3 demo_usage.py
```

### AI功能 (可选)
如果需要AI增强功能，请先启动Ollama服务：
```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 启动服务
ollama serve

# 拉取模型
ollama pull deepseek-coder:6.7b
```

## 📈 输出格式

### JSON报告
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "total_files": 3,
  "files": [...],
  "summary": {
    "total_issues": 29,
    "average_score": 12.1,
    "files_with_errors": 1
  }
}
```

### Markdown报告
- 总体统计信息
- 每个文件的详细分析
- 问题分类和严重程度
- 具体的改进建议

## 🔧 配置选项

### 质量门禁配置
```bash
python3 ci_integration.py . \
  --min-score 80 \      # 最低评分
  --max-errors 0 \      # 最大错误数
  --max-warnings 10     # 最大警告数
```

### AI模型配置
```bash
python3 ai_enhanced_reviewer.py . \
  --ollama-api http://localhost:11434/api/generate \
  --model deepseek-coder:6.7b
```

## 🎯 实际效果

### 评审能力
- ✅ 能够发现真实的代码问题
- ✅ 提供具体的改进建议
- ✅ 支持多种输出格式
- ✅ 集成AI进行深度分析

### 自动化程度
- ✅ 支持批量文件评审
- ✅ 集成Git钩子
- ✅ 支持CI/CD流程
- ✅ 持续监控代码变化

## 🚀 未来规划

### 短期改进
- [ ] 优化检查规则，减少误报
- [ ] 增强AI分析质量
- [ ] 提高大文件处理速度
- [ ] 开发Web界面

### 长期规划
- [ ] 支持多语言 (Python, JavaScript等)
- [ ] 机器学习优化
- [ ] 团队协作功能
- [ ] 云端SaaS服务

## 📝 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

**🎉 感谢使用Java代码自动评审工具！让代码质量检查变得简单高效。**
