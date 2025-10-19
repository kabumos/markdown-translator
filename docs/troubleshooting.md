# 故障排除指南 Troubleshooting Guide

本指南帮助您诊断和解决使用Markdown Translator时可能遇到的各种问题。

This guide helps you diagnose and resolve various issues you might encounter when using Markdown Translator.

## 🚨 常见错误和解决方案 Common Errors and Solutions

### 1. 配置相关错误 Configuration Related Errors

#### ❌ 错误：API密钥未设置
```
Configuration error: Required environment variable TRANSLATE_API_TOKEN is not set
```

**原因 Cause**: 未设置OpenRouter API密钥环境变量

**解决方案 Solution**:
```bash
# 1. 检查当前环境变量 Check current environment variables
echo $TRANSLATE_API_TOKEN
env | grep TRANSLATE

# 2. 设置环境变量 Set environment variable
export TRANSLATE_API_TOKEN="sk-or-v1-your-actual-api-key"

# 3. 验证设置 Verify setting
echo $TRANSLATE_API_TOKEN

# 4. 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）Permanent setting
echo 'export TRANSLATE_API_TOKEN="sk-or-v1-your-api-key"' >> ~/.bashrc
source ~/.bashrc
```

#### ❌ 错误：API配置无效
```
Configuration error: Invalid API configuration
```

**原因 Cause**: API配置验证失败

**解决方案 Solution**:
```bash
# 1. 检查API密钥格式 Check API key format
# OpenRouter密钥应该以 sk-or-v1- 开头
echo $TRANSLATE_API_TOKEN | grep "^sk-or-v1-"

# 2. 测试API连接 Test API connection
curl -H "Authorization: Bearer $TRANSLATE_API_TOKEN" \
     https://openrouter.ai/api/v1/models

# 3. 检查网络连接 Check network connection
ping openrouter.ai

# 4. 验证模型名称 Verify model name
export TRANSLATE_MODEL="qwen/qwen-2.5-72b-instruct"
```

#### ❌ 错误：模型不可用
```
API call failed: Model 'xxx' not found or not available
```

**原因 Cause**: 指定的模型不存在或不可用

**解决方案 Solution**:
```bash
# 1. 查看可用模型列表 List available models
curl -H "Authorization: Bearer $TRANSLATE_API_TOKEN" \
     https://openrouter.ai/api/v1/models | jq '.data[].id'

# 2. 使用推荐模型 Use recommended models
export TRANSLATE_MODEL="qwen/qwen-2.5-72b-instruct"
# 或 or
export TRANSLATE_MODEL="claude-3-5-sonnet-20241022"

# 3. 验证模型可用性 Verify model availability
python -c "
from markdown_translator.config import ConfigManager
config = ConfigManager()
print('Model:', config.get_model_name())
"
```

### 2. 文件访问错误 File Access Errors

#### ❌ 错误：文件未找到
```
FileNotFoundError: [Errno 2] No such file or directory: 'input.md'
```

**解决方案 Solution**:
```bash
# 1. 检查文件是否存在 Check if file exists
ls -la input.md

# 2. 检查文件路径 Check file path
pwd
find . -name "*.md" -type f

# 3. 使用绝对路径 Use absolute path
markdown-translator -i /full/path/to/input.md

# 4. 检查文件权限 Check file permissions
ls -la input.md
chmod 644 input.md
```

#### ❌ 错误：权限被拒绝
```
PermissionError: [Errno 13] Permission denied: 'output.md'
```

**解决方案 Solution**:
```bash
# 1. 检查输出目录权限 Check output directory permissions
ls -la output_directory/

# 2. 创建输出目录 Create output directory
mkdir -p output_directory
chmod 755 output_directory

# 3. 检查磁盘空间 Check disk space
df -h

# 4. 使用不同的输出路径 Use different output path
markdown-translator -i input.md -o ~/Documents/output.md
```

#### ❌ 错误：文件格式不支持
```
Warning: Input file 'document.txt' does not have a .md, .markdown, or .txt extension
```

**解决方案 Solution**:
```bash
# 1. 重命名文件扩展名 Rename file extension
mv document.txt document.md

# 2. 或者忽略警告继续处理 Or ignore warning and continue
markdown-translator -i document.txt -o document_zh.md

# 3. 验证文件内容是否为Markdown格式 Verify file content is Markdown
head -20 document.txt
```

### 3. 网络连接错误 Network Connection Errors

#### ❌ 错误：连接超时
```
Translation failed: Connection timeout
```

**解决方案 Solution**:
```bash
# 1. 检查网络连接 Check network connection
ping openrouter.ai
curl -I https://openrouter.ai

# 2. 检查防火墙设置 Check firewall settings
# 确保允许HTTPS连接到openrouter.ai

# 3. 使用代理（如果需要）Use proxy if needed
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# 4. 降低并发数 Reduce concurrency
markdown-translator -i file.md -n 2

# 5. 增加重试次数 Increase retry attempts
# 在代码中修改MAX_RETRIES参数
```

#### ❌ 错误：API限流
```
API call failed: Rate limit exceeded
```

**解决方案 Solution**:
```bash
# 1. 降低并发数 Reduce concurrency
markdown-translator -i file.md -n 1

# 2. 增加请求间隔 Increase request interval
# 等待几分钟后重试 Wait a few minutes and retry

# 3. 检查API配额 Check API quota
curl -H "Authorization: Bearer $TRANSLATE_API_TOKEN" \
     https://openrouter.ai/api/v1/auth/key

# 4. 使用不同的模型 Use different model
export TRANSLATE_MODEL="qwen/qwen-2.5-7b-instruct"
```

#### ❌ 错误：SSL证书验证失败
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**解决方案 Solution**:
```bash
# 1. 更新证书 Update certificates
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install ca-certificates

# macOS
brew install ca-certificates

# 2. 检查系统时间 Check system time
date
# 确保系统时间正确

# 3. 临时跳过SSL验证（不推荐用于生产环境）
# Temporarily skip SSL verification (not recommended for production)
export PYTHONHTTPSVERIFY=0
```

### 4. 内存和性能问题 Memory and Performance Issues

#### ❌ 错误：内存不足
```
MemoryError: Unable to allocate memory
```

**解决方案 Solution**:
```bash
# 1. 检查系统内存 Check system memory
free -h
top

# 2. 减小分块大小 Reduce chunk size
markdown-translator -i large_file.md -c 200

# 3. 降低并发数 Reduce concurrency
markdown-translator -i large_file.md -n 2

# 4. 使用更小的模型 Use smaller model
export TRANSLATE_MODEL="qwen/qwen-2.5-7b-instruct"

# 5. 分批处理大文件 Process large files in batches
split -l 1000 large_file.md chunk_
for chunk in chunk_*; do
    markdown-translator -i "$chunk" -o "${chunk}_zh.md"
done
```

#### ❌ 错误：处理速度过慢
```
Translation is taking too long
```

**解决方案 Solution**:
```bash
# 1. 增加并发数 Increase concurrency
markdown-translator -i file.md -n 10

# 2. 使用更快的模型 Use faster model
export TRANSLATE_MODEL="qwen/qwen-2.5-7b-instruct"

# 3. 增大分块大小 Increase chunk size
markdown-translator -i file.md -c 1000

# 4. 检查网络速度 Check network speed
speedtest-cli

# 5. 使用本地缓存 Use local caching
# 避免重复翻译相同内容
```

### 5. 翻译质量问题 Translation Quality Issues

#### ❌ 问题：翻译质量差
**症状 Symptoms**: 翻译不准确、术语不一致、格式错乱

**解决方案 Solution**:
```bash
# 1. 使用更好的模型 Use better model
export TRANSLATE_MODEL="claude-3-5-sonnet-20241022"

# 2. 减小分块大小保持上下文 Reduce chunk size for better context
markdown-translator -i file.md -c 200

# 3. 降低并发数避免上下文混乱 Reduce concurrency to avoid context confusion
markdown-translator -i file.md -n 2

# 4. 预处理文件 Preprocess file
# 确保Markdown格式正确
# 移除不必要的空行和格式问题
```

#### ❌ 问题：代码块被翻译
**症状 Symptoms**: 代码示例中的英文被错误翻译

**解决方案 Solution**:
```bash
# 1. 检查代码块格式 Check code block format
# 确保使用正确的代码块标记
```markdown
```python
# 这里的注释应该被翻译
def hello_world():
    print("Hello, World!")  # 这里不应该被翻译
```
```

# 2. 使用更小的分块 Use smaller chunks
markdown-translator -i file.md -c 150

# 3. 启用详细模式检查处理过程 Enable verbose mode
markdown-translator -i file.md --verbose
```

#### ❌ 问题：链接和图片路径被修改
**症状 Symptoms**: Markdown链接和图片路径被错误翻译

**解决方案 Solution**:
```bash
# 1. 检查链接格式 Check link format
# 确保链接格式正确
[链接文本](https://example.com)
![图片描述](images/example.png)

# 2. 使用更精确的模型 Use more precise model
export TRANSLATE_MODEL="claude-3-5-sonnet-20241022"

# 3. 减小分块大小 Reduce chunk size
markdown-translator -i file.md -c 100
```

## 🔍 诊断工具和技巧 Diagnostic Tools and Techniques

### 1. 配置诊断 Configuration Diagnosis

```bash
# 创建诊断脚本 Create diagnostic script
cat > diagnose.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
from markdown_translator.config import ConfigManager

def diagnose_config():
    print("=== Markdown Translator Configuration Diagnosis ===\n")
    
    # 检查环境变量 Check environment variables
    print("1. Environment Variables:")
    env_vars = ['TRANSLATE_API_TOKEN', 'TRANSLATE_API', 'TRANSLATE_MODEL']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'TOKEN' in var:
                print(f"   {var}: {'*' * 20}...{value[-4:]}")
            else:
                print(f"   {var}: {value}")
        else:
            print(f"   {var}: NOT SET")
    
    print("\n2. Configuration Validation:")
    try:
        config = ConfigManager()
        print(f"   ✅ Configuration loaded successfully")
        print(f"   ✅ API Base URL: {config.get_api_base_url()}")
        print(f"   ✅ Model: {config.get_model_name()}")
        
        if config.validate_api_config():
            print("   ✅ API configuration is valid")
        else:
            print("   ❌ API configuration validation failed")
            
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
    
    print("\n3. Network Connectivity:")
    import subprocess
    try:
        result = subprocess.run(['ping', '-c', '1', 'openrouter.ai'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ Network connectivity to openrouter.ai: OK")
        else:
            print("   ❌ Network connectivity to openrouter.ai: FAILED")
    except Exception as e:
        print(f"   ❌ Network test failed: {e}")

if __name__ == "__main__":
    diagnose_config()
EOF

python3 diagnose.py
```

### 2. 文件诊断 File Diagnosis

```bash
# 文件诊断脚本 File diagnosis script
cat > diagnose_file.sh << 'EOF'
#!/bin/bash

FILE="$1"

if [ -z "$FILE" ]; then
    echo "Usage: $0 <markdown_file>"
    exit 1
fi

echo "=== File Diagnosis for: $FILE ==="
echo

echo "1. File Information:"
if [ -f "$FILE" ]; then
    echo "   ✅ File exists"
    echo "   📁 Size: $(du -h "$FILE" | cut -f1)"
    echo "   📄 Lines: $(wc -l < "$FILE")"
    echo "   🔒 Permissions: $(ls -la "$FILE" | awk '{print $1}')"
else
    echo "   ❌ File does not exist"
    exit 1
fi

echo
echo "2. Content Analysis:"
echo "   📝 File type: $(file "$FILE")"

# 检查Markdown语法 Check Markdown syntax
echo "   🔍 Markdown elements found:"
grep -c "^#" "$FILE" && echo "      - Headers: $(grep -c "^#" "$FILE")" || echo "      - Headers: 0"
grep -c "^\`\`\`" "$FILE" && echo "      - Code blocks: $(($(grep -c "^\`\`\`" "$FILE") / 2))" || echo "      - Code blocks: 0"
grep -c "^\|" "$FILE" && echo "      - Tables: $(grep -c "^\|" "$FILE")" || echo "      - Tables: 0"
grep -c "!\[.*\](" "$FILE" && echo "      - Images: $(grep -c "!\[.*\](" "$FILE")" || echo "      - Images: 0"
grep -c "\[.*\](" "$FILE" && echo "      - Links: $(grep -c "\[.*\](" "$FILE")" || echo "      - Links: 0"

echo
echo "3. Potential Issues:"
# 检查潜在问题 Check potential issues
if grep -q $'\t' "$FILE"; then
    echo "   ⚠️  File contains tabs (may cause formatting issues)"
fi

if grep -q $'\r' "$FILE"; then
    echo "   ⚠️  File contains Windows line endings"
fi

if [ $(wc -l < "$FILE") -gt 10000 ]; then
    echo "   ⚠️  Large file (>10000 lines) - consider using larger chunk size"
fi

echo
echo "4. Recommended Settings:"
LINES=$(wc -l < "$FILE")
if [ $LINES -lt 500 ]; then
    echo "   📊 Chunk size: 200-300 (small file)"
    echo "   🔄 Concurrency: 2-3"
elif [ $LINES -lt 2000 ]; then
    echo "   📊 Chunk size: 400-600 (medium file)"
    echo "   🔄 Concurrency: 3-5"
else
    echo "   📊 Chunk size: 800-1200 (large file)"
    echo "   🔄 Concurrency: 5-8"
fi
EOF

chmod +x diagnose_file.sh
./diagnose_file.sh your_file.md
```

### 3. 网络诊断 Network Diagnosis

```bash
# 网络诊断脚本 Network diagnosis script
cat > diagnose_network.sh << 'EOF'
#!/bin/bash

echo "=== Network Diagnosis ==="
echo

echo "1. Basic Connectivity:"
if ping -c 1 openrouter.ai > /dev/null 2>&1; then
    echo "   ✅ Ping to openrouter.ai: OK"
else
    echo "   ❌ Ping to openrouter.ai: FAILED"
fi

echo
echo "2. DNS Resolution:"
if nslookup openrouter.ai > /dev/null 2>&1; then
    echo "   ✅ DNS resolution: OK"
    echo "   🌐 IP: $(nslookup openrouter.ai | grep -A1 "Name:" | tail -1 | awk '{print $2}')"
else
    echo "   ❌ DNS resolution: FAILED"
fi

echo
echo "3. HTTPS Connectivity:"
if curl -s -I https://openrouter.ai > /dev/null 2>&1; then
    echo "   ✅ HTTPS connection: OK"
    echo "   📡 Response: $(curl -s -I https://openrouter.ai | head -1)"
else
    echo "   ❌ HTTPS connection: FAILED"
fi

echo
echo "4. API Endpoint Test:"
if [ -n "$TRANSLATE_API_TOKEN" ]; then
    RESPONSE=$(curl -s -w "%{http_code}" -H "Authorization: Bearer $TRANSLATE_API_TOKEN" \
                    https://openrouter.ai/api/v1/models -o /dev/null)
    if [ "$RESPONSE" = "200" ]; then
        echo "   ✅ API authentication: OK"
    else
        echo "   ❌ API authentication: FAILED (HTTP $RESPONSE)"
    fi
else
    echo "   ⚠️  API token not set - cannot test authentication"
fi

echo
echo "5. Proxy Settings:"
if [ -n "$HTTP_PROXY" ] || [ -n "$HTTPS_PROXY" ]; then
    echo "   🔄 HTTP Proxy: ${HTTP_PROXY:-Not set}"
    echo "   🔄 HTTPS Proxy: ${HTTPS_PROXY:-Not set}"
else
    echo "   ℹ️  No proxy configured"
fi
EOF

chmod +x diagnose_network.sh
./diagnose_network.sh
```

## 🛠️ 高级故障排除 Advanced Troubleshooting

### 1. 调试模式 Debug Mode

```bash
# 启用Python调试模式 Enable Python debug mode
export PYTHONPATH=/path/to/markdown-translator
export PYTHONDEBUG=1

# 使用pdb调试器 Use pdb debugger
python -m pdb -c continue -m markdown_translator.cli -i file.md --verbose

# 启用详细的HTTP日志 Enable verbose HTTP logging
export HTTPX_LOG_LEVEL=DEBUG
markdown-translator -i file.md --verbose
```

### 2. 性能分析 Performance Profiling

```bash
# 使用cProfile进行性能分析 Use cProfile for performance analysis
python -m cProfile -o profile.stats -m markdown_translator.cli -i file.md

# 分析结果 Analyze results
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"

# 内存使用分析 Memory usage analysis
pip install memory-profiler
python -m memory_profiler -m markdown_translator.cli -i file.md
```

### 3. 日志分析 Log Analysis

```bash
# 启用详细日志并分析 Enable verbose logging and analyze
markdown-translator -i file.md --verbose 2>&1 | tee translation.log

# 分析错误模式 Analyze error patterns
grep -i error translation.log
grep -i warning translation.log
grep -i failed translation.log

# 分析性能指标 Analyze performance metrics
grep -i "processing time" translation.log
grep -i "api call" translation.log
grep -i "retry" translation.log
```

### 4. 环境隔离测试 Environment Isolation Testing

```bash
# 创建干净的测试环境 Create clean test environment
python -m venv test_env
source test_env/bin/activate
pip install markdown-translator

# 最小配置测试 Minimal configuration test
export TRANSLATE_API_TOKEN="your-token"
echo "# Test" > test.md
markdown-translator -i test.md --dry-run --verbose

# 逐步增加复杂性 Gradually increase complexity
markdown-translator -i test.md -c 100 -n 1 --verbose
```

## 📞 获取帮助 Getting Help

### 1. 收集诊断信息 Collect Diagnostic Information

在报告问题时，请提供以下信息：
When reporting issues, please provide the following information:

```bash
# 系统信息 System information
echo "OS: $(uname -a)"
echo "Python: $(python --version)"
echo "Pip packages: $(pip list | grep -E '(markdown-translator|openai|aiohttp|click|rich)')"

# 配置信息 Configuration information
echo "API Token: ${TRANSLATE_API_TOKEN:0:10}...${TRANSLATE_API_TOKEN: -4}"
echo "Model: $TRANSLATE_MODEL"
echo "API URL: $TRANSLATE_API"

# 错误信息 Error information
markdown-translator -i problem_file.md --verbose 2>&1 | tail -50
```

### 2. 联系支持 Contact Support

- 📖 文档：[https://markdown-translator.readthedocs.io](https://markdown-translator.readthedocs.io)
- 🐛 问题报告：[GitHub Issues](https://github.com/karminski/markdown-translator/issues)
- 💬 讨论：[GitHub Discussions](https://github.com/karminski/markdown-translator/discussions)
- 📧 邮件：support@example.com

### 3. 社区资源 Community Resources

- 📚 Wiki：[GitHub Wiki](https://github.com/karminski/markdown-translator/wiki)
- 💡 FAQ：[常见问题解答](https://github.com/karminski/markdown-translator/wiki/FAQ)
- 🎥 视频教程：[YouTube频道](https://youtube.com/example)
- 💬 聊天室：[Discord服务器](https://discord.gg/example)

---

**💡 提示**: 大多数问题都可以通过正确配置环境变量和选择合适的参数来解决。如果问题持续存在，请使用诊断脚本收集信息并联系支持团队。

**💡 Tip**: Most issues can be resolved by properly configuring environment variables and choosing appropriate parameters. If problems persist, use the diagnostic scripts to collect information and contact the support team.
