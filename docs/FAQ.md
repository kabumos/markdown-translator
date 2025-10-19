# 常见问题解答 Frequently Asked Questions (FAQ)

本文档回答了使用Markdown Translator时最常遇到的问题。

This document answers the most frequently encountered questions when using Markdown Translator.

## 🔧 安装和配置 Installation & Configuration

### Q1: 如何安装Markdown Translator？
**How do I install Markdown Translator?**

```bash
# 方法1：使用pip安装 Method 1: Install using pip
pip install markdown-translator

# 方法2：从源码安装 Method 2: Install from source
git clone https://github.com/karminski/markdown-translator.git
cd markdown-translator
pip install -e .

# 验证安装 Verify installation
markdown-translator --version
```

### Q2: 支持哪些Python版本？
**Which Python versions are supported?**

Markdown Translator支持Python 3.8及以上版本。推荐使用Python 3.11以获得最佳性能。

Markdown Translator supports Python 3.8 and above. Python 3.11 is recommended for optimal performance.

```bash
# 检查Python版本 Check Python version
python --version

# 如果版本过低，请升级 If version is too old, please upgrade
# Ubuntu/Debian
sudo apt update && sudo apt install python3.11

# macOS
brew install python@3.11

# Windows
# 从 python.org 下载并安装最新版本
```

### Q3: 如何获取OpenRouter API密钥？
**How do I get an OpenRouter API key?**

1. 访问 [OpenRouter官网](https://openrouter.ai)
2. 注册账户或登录现有账户
3. 进入控制台 (Console)
4. 点击 "Keys" 或"API Keys"
5. 创建新的API密钥
6. 复制密钥（格式：`sk-or-v1-...`）

**注意**: 请妥善保管您的API密钥，不要在代码中硬编码或公开分享。

**Note**: Please keep your API key secure, don't hardcode it in your code or share it publicly.

### Q4: 环境变量设置后不生效怎么办？
**What if environment variables don't take effect after setting?**

```bash
# 1. 检查当前环境变量 Check current environment variables
echo $TRANSLATE_API_TOKEN
env | grep TRANSLATE

# 2. 重新加载shell配置 Reload shell configuration
source ~/.bashrc  # 或 ~/.zshrc

# 3. 在当前会话中设置 Set in current session
export TRANSLATE_API_TOKEN="your-key"

# 4. 验证设置 Verify setting
markdown-translator -i test.md --dry-run --verbose
```

### Q5: 可以使用配置文件而不是环境变量吗？
**Can I use a configuration file instead of environment variables?**

虽然工具主要使用环境变量，但您可以创建脚本来管理配置：

While the tool primarily uses environment variables, you can create scripts to manage configuration:

```bash
# 创建配置脚本 Create configuration script
cat > setup_env.sh << 'EOF'
#!/bin/bash
export TRANSLATE_API_TOKEN="sk-or-v1-your-key"
export TRANSLATE_MODEL="qwen/qwen-2.5-72b-instruct"
export TRANSLATE_API="https://openrouter.ai/api/v1"
echo "Environment configured for Markdown Translator"
EOF

# 使用配置 Use configuration
source setup_env.sh
markdown-translator -i document.md
```

## 🚀 使用和功能 Usage & Features

### Q6: 支持哪些文件格式？
**Which file formats are supported?**

主要支持Markdown格式文件：
Primarily supports Markdown format files:

- `.md` - 标准Markdown文件
- `.markdown` - Markdown文件
- `.txt` - 纯文本文件（会按Markdown处理）

```bash
# 支持的文件示例 Supported file examples
markdown-translator -i README.md
markdown-translator -i document.markdown  
markdown-translator -i notes.txt
```

### Q7: 如何处理大文件？
**How to handle large files?**

对于大文件，建议调整以下参数：
For large files, adjust these parameters:

```bash
# 大文件处理策略 Large file processing strategy
# 1. 增大分块大小 Increase chunk size
markdown-translator -i large_file.md --chunk-size 1000

# 2. 适当降低并发数 Moderately reduce concurrency
markdown-translator -i large_file.md --concurrency 4

# 3. 启用详细模式监控进度 Enable verbose mode to monitor progress
markdown-translator -i large_file.md --verbose

# 4. 如果内存不足，可以预先分割文件 If memory is insufficient, pre-split the file
split -l 2000 huge_file.md part_
for part in part_*; do
    markdown-translator -i "$part"
done
```

### Q8: 翻译质量如何控制？
**How to control translation quality?**

影响翻译质量的主要因素：
Main factors affecting translation quality:

```bash
# 1. 选择高质量模型 Choose high-quality model
export TRANSLATE_MODEL="claude-3-5-sonnet-20241022"

# 2. 使用较小分块保持上下文 Use smaller chunks to maintain context
markdown-translator -i doc.md --chunk-size 200

# 3. 降低并发数避免上下文混乱 Reduce concurrency to avoid context confusion
markdown-translator -i doc.md --concurrency 2

# 4. 预处理文档格式 Preprocess document formatting
# 确保Markdown语法正确，移除多余空行等
```

### Q9: 支持哪些翻译模型？
**Which translation models are supported?**

推荐的模型按质量排序：
Recommended models ranked by quality:

| 模型 Model | 质量 Quality | 速度 Speed | 成本 Cost | 适用场景 Use Case |
|------------|--------------|------------|-----------|-------------------|
| `claude-3-5-sonnet-20241022` | 最高 Highest | 慢 Slow | 高 High | 重要文档 Important docs |
| `qwen/qwen-2.5-72b-instruct` | 高 High | 中等 Medium | 中等 Medium | 日常文档 Daily docs |
| `qwen/qwen-2.5-7b-instruct` | 中等 Medium | 快 Fast | 低 Low | 草稿文档 Draft docs |

```bash
# 设置模型 Set model
export TRANSLATE_MODEL="claude-3-5-sonnet-20241022"
```

### Q10: 如何批量翻译多个文件？
**How to batch translate multiple files?**

```bash
# 方法1：简单循环 Method 1: Simple loop
for file in docs/*.md; do
    markdown-translator -i "$file"
done

# 方法2：使用find命令 Method 2: Using find command
find docs -name "*.md" -exec markdown-translator -i {} \;

# 方法3：并行处理 Method 3: Parallel processing
find docs -name "*.md" | xargs -n1 -P4 -I{} markdown-translator -i {}

# 方法4：GNU parallel Method 4: GNU parallel
find docs -name "*.md" | parallel markdown-translator -i {}
```

## ⚡ 性能和优化 Performance & Optimization

### Q11: 如何提高翻译速度？
**How to improve translation speed?**

```bash
# 1. 增加并发数 Increase concurrency
markdown-translator -i file.md --concurrency 10

# 2. 使用更快的模型 Use faster model
export TRANSLATE_MODEL="qwen/qwen-2.5-7b-instruct"

# 3. 增大分块大小 Increase chunk size
markdown-translator -i file.md --chunk-size 800

# 4. 检查网络连接 Check network connection
ping openrouter.ai
```

### Q12: 内存使用过多怎么办？
**What to do about excessive memory usage?**

```bash
# 1. 减小分块大小 Reduce chunk size
markdown-translator -i file.md --chunk-size 200

# 2. 降低并发数 Reduce concurrency
markdown-translator -i file.md --concurrency 2

# 3. 监控内存使用 Monitor memory usage
top -p $(pgrep -f markdown-translator)

# 4. 设置内存限制 Set memory limits
ulimit -v 2097152  # 限制为2GB Limit to 2GB
```

### Q13: API调用频率限制怎么处理？
**How to handle API rate limiting?**

```bash
# 1. 降低并发数 Reduce concurrency
markdown-translator -i file.md --concurrency 1

# 2. 检查API配额 Check API quota
curl -H "Authorization: Bearer $TRANSLATE_API_TOKEN" \
     https://openrouter.ai/api/v1/auth/key

# 3. 等待一段时间后重试 Wait and retry
sleep 60
markdown-translator -i file.md

# 4. 使用不同的模型 Use different model
export TRANSLATE_MODEL="qwen/qwen-2.5-7b-instruct"
```

## 🔒 安全和隐私 Security & Privacy

### Q14: API密钥安全如何保证？
**How to ensure API key security?**

```bash
# 1. 使用环境变量而不是硬编码 Use environment variables, not hardcoding
export TRANSLATE_API_TOKEN="your-key"

# 2. 设置文件权限 Set file permissions
chmod 600 .env

# 3. 不要提交到版本控制 Don't commit to version control
echo ".env" >> .gitignore

# 4. 定期轮换密钥 Regularly rotate keys
# 在OpenRouter控制台生成新密钥并更新
```

### Q15: 翻译的文档会被存储吗？
**Are translated documents stored?**

Markdown Translator本身不存储您的文档内容。但是：
Markdown Translator itself doesn't store your document content. However:

- 文档内容会发送到OpenRouter API进行翻译
- 请查看OpenRouter的隐私政策了解数据处理方式
- 建议不要翻译包含敏感信息的文档
- 可以在翻译前移除敏感内容

### Q16: 如何处理敏感文档？
**How to handle sensitive documents?**

```bash
# 1. 预处理移除敏感信息 Preprocess to remove sensitive info
sed 's/password123/[PASSWORD]/g' sensitive_doc.md > cleaned_doc.md

# 2. 使用本地替换敏感内容 Use local replacement for sensitive content
# 翻译前替换，翻译后恢复

# 3. 分段处理 Process in segments
# 只翻译非敏感部分

# 4. 考虑使用本地翻译模型 Consider using local translation models
# 虽然本工具不支持，但可以考虑其他方案
```

## 🐛 错误处理 Error Handling

### Q17: 常见错误信息及解决方法？
**Common error messages and solutions?**

#### 配置错误 Configuration Errors
```bash
# 错误 Error: "Required environment variable TRANSLATE_API_TOKEN is not set"
# 解决 Solution:
export TRANSLATE_API_TOKEN="sk-or-v1-your-key"

# 错误 Error: "Invalid API configuration"
# 解决 Solution:
# 检查API密钥格式和网络连接
curl -H "Authorization: Bearer $TRANSLATE_API_TOKEN" https://openrouter.ai/api/v1/models
```

#### 文件错误 File Errors
```bash
# 错误 Error: "No such file or directory"
# 解决 Solution:
ls -la input_file.md  # 检查文件是否存在
pwd  # 确认当前目录

# 错误 Error: "Permission denied"
# 解决 Solution:
chmod 644 input_file.md  # 修改文件权限
```

#### 网络错误 Network Errors
```bash
# 错误 Error: "Connection timeout"
# 解决 Solution:
ping openrouter.ai  # 测试网络连接
export HTTP_PROXY=http://proxy:port  # 如果需要代理
```

### Q18: 如何调试翻译问题？
**How to debug translation issues?**

```bash
# 1. 启用详细模式 Enable verbose mode
markdown-translator -i file.md --verbose

# 2. 使用干运行模式检查配置 Use dry-run mode to check configuration
markdown-translator -i file.md --dry-run --verbose

# 3. 测试小文件 Test with small file
echo "# Test" > test.md
markdown-translator -i test.md --verbose

# 4. 检查API连接 Check API connection
python -c "
from markdown_translator.config import ConfigManager
config = ConfigManager()
print('Valid:', config.validate_api_config())
"
```

### Q19: 翻译中断后如何恢复？
**How to resume after translation interruption?**

目前版本支持基本的中断处理：
Current version supports basic interruption handling:

```bash
# 1. 使用Ctrl+C优雅中断 Use Ctrl+C for graceful interruption
# 工具会尝试保存进度

# 2. 检查部分翻译结果 Check partial translation results
ls -la *_zh.md

# 3. 从中断点继续 Continue from interruption point
# 手动处理剩余部分或重新运行

# 4. 未来版本将支持检查点恢复 Future versions will support checkpoint resume
# markdown-translator --resume checkpoint.json
```

## 🔄 集成和自动化 Integration & Automation

### Q20: 如何集成到CI/CD流程？
**How to integrate into CI/CD pipeline?**

#### GitHub Actions示例 GitHub Actions Example
```yaml
# .github/workflows/translate.yml
name: Translate Docs
on:
  push:
    paths: ['docs/**/*.md']

jobs:
  translate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
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
        find docs -name "*.md" | xargs -I {} markdown-translator -i {}
```

### Q21: 如何创建自动化脚本？
**How to create automation scripts?**

```bash
# 创建自动翻译脚本 Create auto-translation script
cat > auto_translate.sh << 'EOF'
#!/bin/bash

# 配置 Configuration
export TRANSLATE_API_TOKEN="your-key"
export TRANSLATE_MODEL="qwen/qwen-2.5-72b-instruct"

# 监控目录变化 Monitor directory changes
inotifywait -m -r -e modify,create --format '%w%f' docs/ | while read file; do
    if [[ "$file" == *.md ]]; then
        echo "Translating updated file: $file"
        markdown-translator -i "$file" -c 400 -n 3
    fi
done
EOF

chmod +x auto_translate.sh
```

### Q22: 支持Docker部署吗？
**Is Docker deployment supported?**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖 Install dependencies
RUN pip install markdown-translator

# 设置入口点 Set entrypoint
ENTRYPOINT ["markdown-translator"]

# 使用示例 Usage example
# docker build -t markdown-translator .
# docker run -v $(pwd):/data -e TRANSLATE_API_TOKEN="your-key" \
#   markdown-translator -i /data/README.md -o /data/README_zh.md
```

## 📊 监控和日志 Monitoring & Logging

### Q23: 如何查看详细的处理日志？
**How to view detailed processing logs?**

```bash
# 1. 启用详细模式 Enable verbose mode
markdown-translator -i file.md --verbose

# 2. 重定向日志到文件 Redirect logs to file
markdown-translator -i file.md --verbose > translation.log 2>&1

# 3. 实时查看日志 View logs in real-time
markdown-translator -i file.md --verbose | tee translation.log

# 4. 分析日志内容 Analyze log content
grep -i error translation.log
grep -i "processing time" translation.log
```

### Q24: 如何监控翻译进度？
**How to monitor translation progress?**

```bash
# 1. 使用详细模式查看进度 Use verbose mode to see progress
markdown-translator -i large_file.md --verbose

# 2. 在另一个终端监控进程 Monitor process in another terminal
watch -n 1 'ps aux | grep markdown-translator'

# 3. 监控输出文件大小变化 Monitor output file size changes
watch -n 5 'ls -lh *_zh.md'

# 4. 使用系统监控工具 Use system monitoring tools
htop  # 查看CPU和内存使用
```

## 💰 成本和计费 Cost & Billing

### Q25: 翻译成本如何计算？
**How is translation cost calculated?**

成本主要取决于：
Cost mainly depends on:

1. **使用的模型** - 不同模型价格不同
2. **文档长度** - 按token数量计费
3. **API调用次数** - 分块数量影响调用次数

```bash
# 成本优化建议 Cost optimization suggestions
# 1. 选择合适的模型 Choose appropriate model
export TRANSLATE_MODEL="qwen/qwen-2.5-7b-instruct"  # 更便宜 Cheaper

# 2. 增大分块大小减少API调用 Increase chunk size to reduce API calls
markdown-translator -i file.md --chunk-size 1000

# 3. 批量处理获得更好的成本效益 Batch processing for better cost efficiency
```

### Q26: 如何估算翻译成本？
**How to estimate translation cost?**

```bash
# 1. 计算文档大小 Calculate document size
wc -w document.md  # 单词数 Word count
wc -c document.md  # 字符数 Character count

# 2. 估算token数量 Estimate token count
# 大约 1 token ≈ 4 字符（英文）
# Approximately 1 token ≈ 4 characters (English)

# 3. 查看OpenRouter定价 Check OpenRouter pricing
# 访问 https://openrouter.ai/models 查看具体价格

# 4. 使用较小文件测试 Test with smaller files
echo "# Test document" > test.md
markdown-translator -i test.md --verbose
# 查看API调用日志估算成本
```

## 🤝 社区和支持 Community & Support

### Q27: 如何报告bug或请求功能？
**How to report bugs or request features?**

1. **GitHub Issues**: [提交问题](https://github.com/karminski/markdown-translator/issues)
2. **GitHub Discussions**: [参与讨论](https://github.com/karminski/markdown-translator/discussions)
3. **邮件支持**: support@example.com
4. **社区聊天**: [Discord服务器](https://discord.gg/example)

### Q28: 如何贡献代码？
**How to contribute code?**

```bash
# 1. Fork并克隆仓库 Fork and clone repository
git clone https://github.com/your-username/markdown-translator.git
cd markdown-translator

# 2. 创建开发环境 Create development environment
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# 3. 运行测试 Run tests
pytest

# 4. 提交更改 Submit changes
git checkout -b feature/your-feature
git commit -m "Add your feature"
git push origin feature/your-feature
# 然后创建Pull Request
```

### Q29: 有中文社区支持吗？
**Is there Chinese community support?**

是的！我们提供中文支持：
Yes! We provide Chinese support:

- 📖 中文文档：完整的中文使用指南
- 💬 中文讨论：GitHub Discussions中文区
- 📧 中文邮件支持：support-zh@example.com
- 🐦 微博：[@markdown_translator_cn](https://weibo.com/example)

### Q30: 未来会有哪些新功能？
**What new features are planned for the future?**

计划中的功能：
Planned features:

- ✅ 检查点和恢复功能 Checkpoint and resume functionality
- ✅ 更多翻译模型支持 More translation model support
- ✅ 配置文件支持 Configuration file support
- ✅ 翻译缓存机制 Translation caching mechanism
- ✅ 批量处理优化 Batch processing optimization
- ✅ Web界面 Web interface
- ✅ 插件系统 Plugin system

---

## 📞 仍有问题？Still Have Questions?

如果您的问题没有在这里找到答案，请：
If your question isn't answered here, please:

1. 📖 查看完整文档：[README.md](../README.md)
2. 🔍 搜索已有问题：[GitHub Issues](https://github.com/karminski/markdown-translator/issues)
3. 💬 参与社区讨论：[GitHub Discussions](https://github.com/karminski/markdown-translator/discussions)
4. 📧 联系支持团队：support@example.com

我们会持续更新这个FAQ，添加更多常见问题和解答。

We continuously update this FAQ, adding more common questions and answers.

**💡 提示**: 在提问时，请提供尽可能详细的信息，包括错误信息、系统环境、使用的命令等，这样我们能更快地帮助您解决问题。

**💡 Tip**: When asking questions, please provide as much detail as possible, including error messages, system environment, commands used, etc., so we can help you solve the problem faster.
