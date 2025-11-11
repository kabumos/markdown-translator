# Markdown Translator

![cover](./assets/images/markdown-translator.png)

一个基于Python的命令行工具，使用OpenRouter API将Markdown文件翻译成中文。该工具通过智能分割、并发处理和内容验证来确保翻译质量和完整性。

A Python command-line tool for translating Markdown files to Chinese using OpenRouter API with intelligent splitting, concurrent processing, and content validation.

## ✨ 特性 Features

- **🧠 智能分割 Intelligent Splitting**: 保持Markdown语法完整性的智能文件分割
- **⚡ 并发处理 Concurrent Processing**: 多线程并发翻译，提高处理效率
- **🔍 内容验证 Content Validation**: 确保翻译完整性和内容一致性
- **🛡️ 错误恢复 Error Recovery**: 强大的错误处理和重试机制
- **📊 进度跟踪 Progress Tracking**: 实时进度显示和美观的控制台输出
- **🔒 安全保护 Security**: 输入验证和路径安全检查
- **📈 性能监控 Performance Monitoring**: 内存使用监控和性能优化
- **⚙️ 配置灵活 Configuration Flexibility**: 支持环境变量和YAML配置文件

## 📦 安装 Installation

### 使用 pip 安装 Install via pip

(懒得上传pip了, 请手动构建)

```bash
pip install markdown-translator
```

### 从源码安装 Install from source

```bash
git clone https://github.com/karminski/markdown-translator.git
cd markdown-translator
pip install -e .
```

### 开发环境安装 Development installation

```bash
git clone https://github.com/karminski/markdown-translator.git
cd markdown-translator
pip install -e ".[dev]"
```

## 🚀 快速开始 Quick Start

### 1. 环境配置 Environment Setup

首先，您需要获取OpenRouter API密钥并设置环境变量：

First, get your OpenRouter API key and set up environment variables:

```bash
# 设置API密钥 Set API key
export TRANSLATE_API_TOKEN="your_openrouter_api_key"

# 可选：设置使用的模型 Optional: Set model
export TRANSLATE_MODEL="qwen/qwen-2.5-72b-instruct"

# 可选：设置API基础URL Optional: Set API base URL
export TRANSLATE_API="https://openrouter.ai/api/v1"
```

### 2. 基本使用 Basic Usage

```bash
# 翻译Markdown文件 Translate a Markdown file
markdown-translator -i README.md -o README_zh.md

# 使用短命令 Use short command
mt -i docs.md -o docs_zh.md

# 自动生成输出文件名 Auto-generate output filename
markdown-translator -i README.md
# 输出文件将是 README_zh.md Output file will be README_zh.md
```

### 3. 高级用法 Advanced Usage

```bash
# 自定义分割大小和并发数 Custom chunk size and concurrency
markdown-translator -i large_doc.md -o large_doc_zh.md --chunk-size 1000 --concurrency 10

# 详细输出模式 Verbose output
markdown-translator -i doc.md -o doc_zh.md --verbose

# 干运行模式（查看配置但不执行翻译）Dry run mode
markdown-translator -i doc.md --dry-run

# 从检查点恢复翻译 Resume from checkpoint
markdown-translator --resume checkpoint.json
```

## ⚙️ 配置详解 Configuration Guide

### 环境变量 Environment Variables

| 变量名 Variable | 必需 Required | 默认值 Default | 说明 Description |
|----------------|---------------|----------------|------------------|
| `TRANSLATE_API_TOKEN` | ✅ | - | OpenRouter API密钥 |
| `TRANSLATE_API` | ❌ | `https://openrouter.ai/api/v1` | API基础URL |
| `TRANSLATE_MODEL` | ❌ | `qwen/qwen-2.5-72b-instruct` | 使用的翻译模型 |
| `CONFIG_FILE` | ❌ | - | YAML配置文件路径 |

### 命令行参数 Command Line Options

| 参数 Option | 短参数 Short | 类型 Type | 默认值 Default | 说明 Description |
|-------------|--------------|-----------|----------------|------------------|
| `--input` | `-i` | string | - | 输入Markdown文件路径（必需）|
| `--output` | `-o` | string | `{input}_zh.md` | 输出文件路径 |
| `--chunk-size` | `-c` | integer | 500 | 每个分块的行数 |
| `--concurrency` | `-n` | integer | 5 | 并发翻译数量 |
| `--verbose` | `-v` | flag | false | 启用详细日志 |
| `--dry-run` | - | flag | false | 干运行模式 |
| `--resume` | - | string | - | 从检查点恢复 |
| `--config-file` | - | string | - | YAML配置文件路径 |
| `--timeout` | - | integer | 120 | API超时时间（秒） |
| `--max-retries` | - | integer | 5 | API调用最大重试次数 |
| `--retry-delay` | - | integer | 5 | 重试初始延迟（秒） |
| `--max-delay` | - | integer | 300 | 重试最大延迟（秒） |
| `--checkpoint-interval` | - | integer | 10 | 每N个分块保存一次检查点 |

## 📋 配置示例和最佳实践 Configuration Examples & Best Practices

创建 `.env` 文件：Create a `.env` file:

```bash
# OpenRouter API配置 OpenRouter API Configuration
TRANSLATE_API_TOKEN=sk-or-v1-your-api-key-here
TRANSLATE_MODEL=qwen/qwen-2.5-72b-instruct
TRANSLATE_API=https://openrouter.ai/api/v1

# 可选：日志级别 Optional: Log level
LOG_LEVEL=INFO
```

### 2. YAML配置文件 YAML Configuration File

创建 `translator_config.yaml` 文件以使用更丰富的配置选项：

```yaml
api:
  base_url: "https://openrouter.ai/api/v1"
  token: "${TRANSLATE_API_TOKEN}"  # 将使用环境变量 Use environment variable
  model: "qwen/qwen-2.5-72b-instruct"
  timeout: 120
  max_retries: 5
  retry_delay: 5
  max_delay: 300

translation:
  default_chunk_size: 500
  default_concurrency: 5
  min_chunk_size: 50
  max_chunk_size: 2000
  max_concurrency: 20
  checkpoint_interval: 10

validation:
  enable_integrity_check: true
  line_count_tolerance: 0.1
  enable_syntax_validation: true

performance:
  enable_monitoring: true
  memory_limit_mb: 1024
  temp_file_cleanup: true

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "translator.log"
```

当未指定 `--config-file` 时，工具会自动在以下位置查找配置文件：
1. `./translator_config.yaml` (当前目录)
2. `./config.yaml` (当前目录) 
3. `~/.markdown-translator/config.yaml` (用户主目录)
4. `/etc/markdown-translator/config.yaml` (系统范围)

环境变量的优先级高于配置文件设置。

然后加载环境变量：Then load environment variables:

```bash
# Linux/macOS
source .env

# Windows
set /p TRANSLATE_API_TOKEN=<.env
```

### 2. 不同场景的最佳配置 Best Configurations for Different Scenarios

#### 小文件翻译 Small Files (< 1MB)
```bash
markdown-translator -i small_doc.md -c 300 -n 3
```

#### 大文件翻译 Large Files (> 10MB)
```bash
markdown-translator -i large_doc.md -c 1000 -n 8 --verbose
```

#### 高质量翻译 High Quality Translation
```bash
export TRANSLATE_MODEL="claude-3-5-sonnet-20241022"
markdown-translator -i important_doc.md -c 200 -n 2
```

#### 快速翻译 Fast Translation
```bash
export TRANSLATE_MODEL="qwen/qwen-2.5-7b-instruct"
markdown-translator -i draft_doc.md -c 800 -n 15
```

### 3. 批量处理脚本 Batch Processing Script

创建批量翻译脚本：Create a batch translation script:

```bash
#!/bin/bash
# batch_translate.sh

# 设置通用配置 Set common configuration
export TRANSLATE_API_TOKEN="your-api-key"
export TRANSLATE_MODEL="qwen/qwen-2.5-72b-instruct"

# 翻译目录中的所有Markdown文件 Translate all Markdown files in directory
for file in docs/*.md; do
    if [ -f "$file" ]; then
        echo "Translating $file..."
        markdown-translator -i "$file" -c 500 -n 5
        echo "Completed $file"
    fi
done

echo "All files translated!"
```

### 4. Docker配置 Docker Configuration

创建 `Dockerfile`：Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖 Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制应用代码 Copy application code
COPY . .
RUN pip install -e .

# 设置入口点 Set entrypoint
ENTRYPOINT ["markdown-translator"]
```

使用Docker运行：Run with Docker:

```bash
# 构建镜像 Build image
docker build -t markdown-translator .

# 运行翻译 Run translation
docker run -v $(pwd):/data \
  -e TRANSLATE_API_TOKEN="your-api-key" \
  markdown-translator -i /data/README.md -o /data/README_zh.md
```

## 🔧 故障排除指南 Troubleshooting Guide

### 常见问题 Common Issues

#### 1. API密钥错误 API Key Issues

**问题 Problem**: `Configuration error: Required environment variable TRANSLATE_API_TOKEN is not set`

**解决方案 Solution**:
```bash
# 检查环境变量是否设置 Check if environment variable is set
echo $TRANSLATE_API_TOKEN

# 设置环境变量 Set environment variable
export TRANSLATE_API_TOKEN="your-actual-api-key"

# 验证API密钥有效性 Verify API key validity
curl -H "Authorization: Bearer $TRANSLATE_API_TOKEN" \
     https://openrouter.ai/api/v1/models
```

#### 2. 网络连接问题 Network Connection Issues

**问题 Problem**: `Translation failed: Connection timeout` 或 `API call failed`

**解决方案 Solution**:
```bash
# 检查网络连接 Check network connection
ping openrouter.ai

# 使用代理（如果需要）Use proxy if needed
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port

# 降低并发数 Reduce concurrency
markdown-translator -i file.md -n 2
```

#### 3. 内存不足 Memory Issues

**问题 Problem**: `MemoryError` 或系统变慢 System slowdown

**解决方案 Solution**:
```bash
# 减小分块大小 Reduce chunk size
markdown-translator -i large_file.md -c 200

# 降低并发数 Reduce concurrency
markdown-translator -i large_file.md -n 2

# 监控内存使用 Monitor memory usage
markdown-translator -i file.md --verbose
```

#### 4. 文件权限问题 File Permission Issues

**问题 Problem**: `Permission denied` 或 `File not found`

**解决方案 Solution**:
```bash
# 检查文件权限 Check file permissions
ls -la input_file.md

# 修改权限 Change permissions
chmod 644 input_file.md

# 检查输出目录权限 Check output directory permissions
ls -la output_directory/
mkdir -p output_directory
```

#### 5. 翻译质量问题 Translation Quality Issues

**问题 Problem**: 翻译质量不佳或格式错乱 Poor translation quality or formatting issues

**解决方案 Solution**:
```bash
# 使用更好的模型 Use better model
export TRANSLATE_MODEL="claude-3-5-sonnet-20241022"

# 减小分块大小以保持上下文 Reduce chunk size for better context
markdown-translator -i file.md -c 200

# 启用详细模式查看处理过程 Enable verbose mode
markdown-translator -i file.md --verbose
```

### 错误代码参考 Error Code Reference

| 错误代码 Error Code | 含义 Meaning | 解决方案 Solution |
|-------------------|--------------|------------------|
| 1 | 配置错误 Configuration error | 检查环境变量设置 |
| 2 | 文件访问错误 File access error | 检查文件权限和路径 |
| 3 | API调用失败 API call failed | 检查网络和API密钥 |
| 4 | 内存不足 Out of memory | 减少并发数和分块大小 |
| 130 | 用户中断 User interrupted | 正常，可使用--resume恢复 |

### 调试技巧 Debugging Tips

#### 1. 启用详细日志 Enable Verbose Logging

```bash
# 查看详细处理过程 View detailed processing
markdown-translator -i file.md --verbose

# 查看配置信息 View configuration
markdown-translator -i file.md --dry-run --verbose
```

#### 2. 检查API连接 Test API Connection

```bash
# 测试API连接 Test API connection
python -c "
from markdown_translator.config import ConfigManager
config = ConfigManager()
print('API Config Valid:', config.validate_api_config())
print('Model:', config.get_model_name())
"
```

#### 3. 分步调试 Step-by-step Debugging

```bash
# 1. 测试小文件 Test with small file
echo '# Test\nHello world' > test.md
markdown-translator -i test.md --verbose

# 2. 测试分割功能 Test splitting functionality
markdown-translator -i large_file.md --dry-run --verbose

# 3. 测试单个分块 Test single chunk
markdown-translator -i file.md -c 50 -n 1 --verbose
```

### 性能优化建议 Performance Optimization Tips

#### 1. 选择合适的参数 Choose Appropriate Parameters

```bash
# 文件大小 < 1MB File size < 1MB
markdown-translator -i small.md -c 300 -n 3

# 文件大小 1-10MB File size 1-10MB  
markdown-translator -i medium.md -c 500 -n 5

# 文件大小 > 10MB File size > 10MB
markdown-translator -i large.md -c 1000 -n 8
```

#### 2. 监控系统资源 Monitor System Resources

```bash
# 监控内存使用 Monitor memory usage
top -p $(pgrep -f markdown-translator)

# 监控网络连接 Monitor network connections
netstat -an | grep openrouter.ai
```

#### 3. 使用检查点功能 Use Checkpoint Feature

```bash
# 长时间翻译建议启用检查点 Enable checkpoints for long translations
markdown-translator -i very_large_file.md --verbose
# 如果中断，使用 --resume checkpoint.json 恢复
```

## 📚 高级用法 Advanced Usage

### 1. 自定义翻译提示词 Custom Translation Prompts

虽然工具内置了优化的翻译提示词，但您可以通过修改源码来自定义：

```python
# 在 translator.py 中修改 _create_translation_prompt 方法
def _create_translation_prompt(self, content: str) -> str:
    return f"""
请将以下Markdown内容翻译成中文，保持格式不变：
Please translate the following Markdown content to Chinese while preserving formatting:

{content}

要求 Requirements:
1. 保持所有Markdown语法标记不变
2. 保持代码块内容不变
3. 保持链接URL不变
4. 确保翻译自然流畅
"""
```

### 2. 集成到CI/CD流程 Integration with CI/CD

GitHub Actions示例：

```yaml
name: Translate Documentation
on:
  push:
    paths: ['docs/**/*.md']

jobs:
  translate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install translator
      run: pip install markdown-translator
    - name: Translate docs
      env:
        TRANSLATE_API_TOKEN: ${{ secrets.OPENROUTER_API_KEY }}
      run: |
        for file in docs/**/*.md; do
          markdown-translator -i "$file" -o "${file%.*}_zh.md"
        done
    - name: Commit translations
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add docs/**/*_zh.md
        git commit -m "Auto-translate documentation" || exit 0
        git push
```

### 3. 与其他工具集成 Integration with Other Tools

#### 与MkDocs集成 Integration with MkDocs

```bash
# 翻译MkDocs文档 Translate MkDocs documentation
find docs -name "*.md" -exec markdown-translator -i {} \;

# 创建多语言配置 Create multilingual configuration
# mkdocs.yml
site_name: My Project
nav:
  - Home: index.md
  - 中文首页: index_zh.md
```

#### 与Sphinx集成 Integration with Sphinx

```python
# conf.py
extensions = ['sphinx.ext.autodoc']

# 添加翻译后处理脚本 Add post-translation script
import subprocess
import os

def translate_docs():
    for root, dirs, files in os.walk('source'):
        for file in files:
            if file.endswith('.md'):
                input_path = os.path.join(root, file)
                subprocess.run(['markdown-translator', '-i', input_path])
```

## 🤝 贡献指南 Contributing

我们欢迎各种形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### 开发环境设置 Development Setup

```bash
# 克隆仓库 Clone repository
git clone https://github.com/karminski/markdown-translator.git
cd markdown-translator

# 创建虚拟环境 Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 安装开发依赖 Install development dependencies
pip install -e ".[dev]"

# 安装pre-commit钩子 Install pre-commit hooks
pre-commit install

# 运行测试 Run tests
pytest

# 代码格式化 Format code
black markdown_translator tests
isort markdown_translator tests

# 类型检查 Type checking
mypy markdown_translator
```

## 📄 许可证 License

MIT License - 详见 [LICENSE](LICENSE) 文件。

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 支持 Support

- 📖 文档：[https://markdown-translator.readthedocs.io](https://markdown-translator.readthedocs.io)
- 🐛 问题报告：[GitHub Issues](https://github.com/karminski/markdown-translator/issues)
- 💬 讨论：[GitHub Discussions](https://github.com/karminski/markdown-translator/discussions)
- 📧 邮件：contact@example.com

## 🙏 致谢 Acknowledgments

- [OpenRouter](https://openrouter.ai) - 提供AI模型API服务
- [Rich](https://github.com/Textualize/rich) - 美观的终端输出
- [Click](https://click.palletsprojects.com/) - 命令行界面框架
- [OpenAI Python SDK](https://github.com/openai/openai-python) - API客户端库

---

**⭐ 如果这个项目对您有帮助，请给我们一个星标！**

**⭐ If this project helps you, please give us a star!**
