# 快速开始指南 Quick Start Guide

欢迎使用Markdown Translator！本指南将帮助您在5分钟内开始使用这个工具。

Welcome to Markdown Translator! This guide will help you get started with the tool in 5 minutes.

## 🚀 5分钟快速开始 5-Minute Quick Start

### 步骤1：安装 Step 1: Installation

```bash
# 使用pip安装 Install using pip
pip install markdown-translator

# 验证安装 Verify installation
markdown-translator --version
```

### 步骤2：获取API密钥 Step 2: Get API Key

1. 访问 [OpenRouter](https://openrouter.ai) 并注册账户
2. 在控制台中创建API密钥
3. 复制您的API密钥（格式：`sk-or-v1-...`）

### 步骤3：配置环境 Step 3: Configure Environment

```bash
# 设置API密钥 Set API key
export TRANSLATE_API_TOKEN="sk-or-v1-your-api-key-here"

# 可选：设置模型 Optional: Set model
export TRANSLATE_MODEL="qwen/qwen-2.5-72b-instruct"
```

### 步骤4：翻译您的第一个文件 Step 4: Translate Your First File

```bash
# 创建测试文件 Create test file
echo "# Hello World
This is a test document.
- Item 1
- Item 2" > test.md

# 翻译文件 Translate file
markdown-translator -i test.md -o test_zh.md

# 查看结果 View result
cat test_zh.md
```

🎉 **恭喜！您已经成功翻译了第一个Markdown文件！**

🎉 **Congratulations! You've successfully translated your first Markdown file!**

## 📚 常用命令 Common Commands

### 基本翻译 Basic Translation
```bash
# 最简单的用法 Simplest usage
markdown-translator -i README.md

# 指定输出文件 Specify output file
markdown-translator -i README.md -o README_chinese.md

# 详细输出 Verbose output
markdown-translator -i README.md --verbose
```

### 高级选项 Advanced Options
```bash
# 自定义分块大小 Custom chunk size
markdown-translator -i large_doc.md --chunk-size 1000

# 调整并发数 Adjust concurrency
markdown-translator -i doc.md --concurrency 8

# 组合选项 Combined options
markdown-translator -i doc.md -o doc_zh.md -c 500 -n 5 --verbose
```

### 批量处理 Batch Processing
```bash
# 翻译目录中的所有Markdown文件 Translate all Markdown files in directory
for file in docs/*.md; do
    markdown-translator -i "$file"
done

# 使用find命令 Using find command
find docs -name "*.md" -exec markdown-translator -i {} \;
```

## ⚙️ 配置选项 Configuration Options

### 环境变量 Environment Variables
| 变量 Variable | 必需 Required | 默认值 Default | 说明 Description |
|---------------|---------------|----------------|------------------|
| `TRANSLATE_API_TOKEN` | ✅ | - | OpenRouter API密钥 |
| `TRANSLATE_MODEL` | ❌ | `qwen/qwen-2.5-72b-instruct` | 翻译模型 |
| `TRANSLATE_API` | ❌ | `https://openrouter.ai/api/v1` | API基础URL |

### 命令行参数 Command Line Arguments
| 参数 Argument | 短参数 Short | 默认值 Default | 说明 Description |
|---------------|--------------|----------------|------------------|
| `--input` | `-i` | - | 输入文件路径 |
| `--output` | `-o` | `{input}_zh.md` | 输出文件路径 |
| `--chunk-size` | `-c` | 500 | 分块大小（行数）|
| `--concurrency` | `-n` | 5 | 并发数 |
| `--verbose` | `-v` | false | 详细输出 |

## 🎯 使用场景示例 Usage Scenarios

### 场景1：翻译技术文档 Scenario 1: Technical Documentation
```bash
# 使用较小的分块保持技术术语一致性
# Use smaller chunks to maintain technical term consistency
export TRANSLATE_MODEL="claude-3-5-sonnet-20241022"
markdown-translator -i technical_guide.md -c 200 -n 2 --verbose
```

### 场景2：翻译博客文章 Scenario 2: Blog Posts
```bash
# 平衡速度和质量 Balance speed and quality
markdown-translator -i blog_post.md -c 400 -n 5
```

### 场景3：翻译API文档 Scenario 3: API Documentation
```bash
# 保持代码示例完整性 Preserve code example integrity
markdown-translator -i api_reference.md -c 150 -n 2 --verbose
```

### 场景4：批量翻译 Scenario 4: Batch Translation
```bash
# 快速批量处理 Quick batch processing
export TRANSLATE_MODEL="qwen/qwen-2.5-7b-instruct"
find docs -name "*.md" | xargs -I {} markdown-translator -i {} -c 600 -n 8
```

## 🔧 常见配置 Common Configurations

### 配置文件方式 Configuration File Approach
```bash
# 创建配置文件 Create configuration file
cat > .env << 'EOF'
TRANSLATE_API_TOKEN=sk-or-v1-your-api-key
TRANSLATE_MODEL=qwen/qwen-2.5-72b-instruct
TRANSLATE_API=https://openrouter.ai/api/v1
EOF

# 加载配置 Load configuration
source .env

# 使用配置 Use configuration
markdown-translator -i document.md
```

### 项目级配置 Project-level Configuration
```bash
# 为不同项目创建不同的配置脚本
# Create different configuration scripts for different projects

# 项目A：高质量翻译 Project A: High quality translation
cat > translate_project_a.sh << 'EOF'
#!/bin/bash
export TRANSLATE_MODEL="claude-3-5-sonnet-20241022"
markdown-translator -i "$1" -c 200 -n 2 --verbose
EOF

# 项目B：快速翻译 Project B: Fast translation
cat > translate_project_b.sh << 'EOF'
#!/bin/bash
export TRANSLATE_MODEL="qwen/qwen-2.5-7b-instruct"
markdown-translator -i "$1" -c 800 -n 8
EOF

chmod +x translate_project_*.sh
```

## 🚨 常见问题快速解决 Quick Problem Resolution

### 问题1：API密钥错误 Problem 1: API Key Error
```bash
# 错误信息 Error message
# Configuration error: Required environment variable TRANSLATE_API_TOKEN is not set

# 解决方案 Solution
export TRANSLATE_API_TOKEN="sk-or-v1-your-actual-key"
echo $TRANSLATE_API_TOKEN  # 验证设置 Verify setting
```

### 问题2：网络连接问题 Problem 2: Network Connection Issues
```bash
# 测试连接 Test connection
ping openrouter.ai
curl -I https://openrouter.ai

# 如果有代理 If using proxy
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port
```

### 问题3：翻译速度慢 Problem 3: Slow Translation
```bash
# 增加并发数 Increase concurrency
markdown-translator -i file.md -n 10

# 使用更快的模型 Use faster model
export TRANSLATE_MODEL="qwen/qwen-2.5-7b-instruct"
```

### 问题4：内存不足 Problem 4: Out of Memory
```bash
# 减小分块大小 Reduce chunk size
markdown-translator -i large_file.md -c 200

# 降低并发数 Reduce concurrency
markdown-translator -i large_file.md -n 2
```

## 📖 下一步 Next Steps

### 深入学习 Deep Dive
- 📚 阅读完整文档：[README.md](../README.md)
- 🔧 查看配置示例：[配置示例](../examples/config_examples.md)
- 🛠️ 学习故障排除：[故障排除指南](troubleshooting.md)
- 💡 掌握最佳实践：[最佳实践指南](best_practices.md)

### 高级功能 Advanced Features
```bash
# 干运行模式 Dry run mode
markdown-translator -i file.md --dry-run

# 从检查点恢复 Resume from checkpoint
markdown-translator --resume checkpoint.json

# 自定义输出格式 Custom output format
markdown-translator -i file.md -o custom_name.md
```

### 集成到工作流 Integrate into Workflow
```bash
# Git钩子集成 Git hook integration
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# 自动翻译变更的Markdown文件
git diff --cached --name-only | grep '\.md$' | while read file; do
    if [ -f "$file" ]; then
        markdown-translator -i "$file"
        git add "${file%.*}_zh.md"
    fi
done
EOF
chmod +x .git/hooks/pre-commit
```

## 🆘 获取帮助 Getting Help

### 文档资源 Documentation Resources
- 📖 完整文档：[GitHub Repository](https://github.com/karminski/markdown-translator)
- 🐛 问题报告：[GitHub Issues](https://github.com/karminski/markdown-translator/issues)
- 💬 社区讨论：[GitHub Discussions](https://github.com/karminski/markdown-translator/discussions)

### 社区支持 Community Support
- 💬 Discord：[加入我们的Discord服务器](https://discord.gg/example)
- 📧 邮件：support@example.com
- 🐦 Twitter：[@markdown_translator](https://twitter.com/example)

### 贡献代码 Contributing
```bash
# 克隆仓库 Clone repository
git clone https://github.com/karminski/markdown-translator.git
cd markdown-translator

# 安装开发依赖 Install development dependencies
pip install -e ".[dev]"

# 运行测试 Run tests
pytest

# 提交改进 Submit improvements
# 查看 CONTRIBUTING.md 了解详细信息
```

---

**🎉 现在您已经掌握了Markdown Translator的基本用法！开始翻译您的文档吧！**

**🎉 Now you've mastered the basics of Markdown Translator! Start translating your documents!**

**💡 提示**: 如果遇到任何问题，请查看[故障排除指南](troubleshooting.md)或在GitHub上提交issue。

**💡 Tip**: If you encounter any issues, check the [troubleshooting guide](troubleshooting.md) or submit an issue on GitHub.
