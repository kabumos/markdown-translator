# 配置示例和最佳实践 Configuration Examples & Best Practices

本文档提供了Markdown Translator的详细配置示例和最佳实践指南。

This document provides detailed configuration examples and best practices for Markdown Translator.

## 📋 环境配置示例 Environment Configuration Examples

### 1. 基础配置 Basic Configuration

#### Linux/macOS 配置
```bash
# ~/.bashrc 或 ~/.zshrc
export TRANSLATE_API_TOKEN="sk-or-v1-your-openrouter-key"
export TRANSLATE_MODEL="qwen/qwen-2.5-72b-instruct"
export TRANSLATE_API="https://openrouter.ai/api/v1"

# 重新加载配置 Reload configuration
source ~/.bashrc
```

#### Windows 配置
```cmd
# 临时设置 Temporary setting
set TRANSLATE_API_TOKEN=sk-or-v1-your-openrouter-key
set TRANSLATE_MODEL=qwen/qwen-2.5-72b-instruct

# 永久设置 Permanent setting
setx TRANSLATE_API_TOKEN "sk-or-v1-your-openrouter-key"
setx TRANSLATE_MODEL "qwen/qwen-2.5-72b-instruct"
```

#### PowerShell 配置
```powershell
# 临时设置 Temporary setting
$env:TRANSLATE_API_TOKEN = "sk-or-v1-your-openrouter-key"
$env:TRANSLATE_MODEL = "qwen/qwen-2.5-72b-instruct"

# 添加到PowerShell配置文件 Add to PowerShell profile
Add-Content $PROFILE '$env:TRANSLATE_API_TOKEN = "sk-or-v1-your-openrouter-key"'
```

### 2. 项目级配置 Project-level Configuration

#### .env 文件配置
```bash
# .env - 项目根目录
# OpenRouter API Configuration
TRANSLATE_API_TOKEN=sk-or-v1-your-api-key-here
TRANSLATE_MODEL=qwen/qwen-2.5-72b-instruct
TRANSLATE_API=https://openrouter.ai/api/v1

# Optional: Performance tuning
DEFAULT_CHUNK_SIZE=500
DEFAULT_CONCURRENCY=5
MAX_RETRIES=3
TIMEOUT_SECONDS=30

# Optional: Logging
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

#### direnv 配置（推荐）
```bash
# .envrc - 自动环境管理
export TRANSLATE_API_TOKEN="sk-or-v1-your-api-key"
export TRANSLATE_MODEL="qwen/qwen-2.5-72b-instruct"

# 进入目录时自动加载 Auto-load when entering directory
# 需要安装 direnv: https://direnv.net/
```

## 🎯 不同场景的最佳配置 Best Configurations for Different Scenarios

### 1. 文档类型优化 Document Type Optimization

#### 技术文档 Technical Documentation
```bash
# 使用高质量模型，较小分块保持技术术语一致性
export TRANSLATE_MODEL="claude-3-5-sonnet-20241022"
markdown-translator -i technical_doc.md -c 200 -n 3 --verbose
```

#### 博客文章 Blog Posts
```bash
# 平衡质量和速度
export TRANSLATE_MODEL="qwen/qwen-2.5-72b-instruct"
markdown-translator -i blog_post.md -c 400 -n 5
```

#### API文档 API Documentation
```bash
# 保持代码示例完整性，使用较小分块
export TRANSLATE_MODEL="qwen/qwen-2.5-72b-instruct"
markdown-translator -i api_docs.md -c 150 -n 2 --verbose
```

#### README文件 README Files
```bash
# 快速翻译，适中质量
export TRANSLATE_MODEL="qwen/qwen-2.5-7b-instruct"
markdown-translator -i README.md -c 300 -n 8
```

### 2. 文件大小优化 File Size Optimization

#### 小文件 (< 1MB)
```bash
# 配置示例 Configuration example
CHUNK_SIZE=300
CONCURRENCY=3
MODEL="qwen/qwen-2.5-72b-instruct"

markdown-translator -i small_doc.md -c $CHUNK_SIZE -n $CONCURRENCY
```

#### 中等文件 (1-10MB)
```bash
# 配置示例 Configuration example
CHUNK_SIZE=500
CONCURRENCY=5
MODEL="qwen/qwen-2.5-72b-instruct"

markdown-translator -i medium_doc.md -c $CHUNK_SIZE -n $CONCURRENCY --verbose
```

#### 大文件 (> 10MB)
```bash
# 配置示例 Configuration example
CHUNK_SIZE=1000
CONCURRENCY=8
MODEL="qwen/qwen-2.5-7b-instruct"  # 使用更快的模型

markdown-translator -i large_doc.md -c $CHUNK_SIZE -n $CONCURRENCY --verbose
```

### 3. 网络环境优化 Network Environment Optimization

#### 慢速网络 Slow Network
```bash
# 减少并发，增加超时时间
export TRANSLATE_MODEL="qwen/qwen-2.5-7b-instruct"
markdown-translator -i doc.md -c 300 -n 2 --verbose
```

#### 不稳定网络 Unstable Network
```bash
# 使用更小的分块和更低的并发
markdown-translator -i doc.md -c 200 -n 1 --verbose
```

#### 企业网络（有代理）Corporate Network with Proxy
```bash
# 设置代理 Set proxy
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1

markdown-translator -i doc.md -c 400 -n 3
```

## 🔧 高级配置 Advanced Configuration

### 1. 自定义配置文件 Custom Configuration File

创建 `translator_config.yaml`：
```yaml
# translator_config.yaml
api:
  base_url: "https://openrouter.ai/api/v1"
  token: "${TRANSLATE_API_TOKEN}"  # 从环境变量读取
  model: "qwen/qwen-2.5-72b-instruct"
  timeout: 30
  max_retries: 3

translation:
  default_chunk_size: 500
  default_concurrency: 5
  min_chunk_size: 50
  max_chunk_size: 2000
  max_concurrency: 20

validation:
  enable_integrity_check: true
  line_count_tolerance: 0.1  # 10% tolerance
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

### 2. 批量处理配置 Batch Processing Configuration

#### 批量翻译脚本 Batch Translation Script
```bash
#!/bin/bash
# batch_translate.sh

# 配置 Configuration
API_TOKEN="your-api-key"
MODEL="qwen/qwen-2.5-72b-instruct"
CHUNK_SIZE=500
CONCURRENCY=5
INPUT_DIR="docs"
OUTPUT_DIR="docs_zh"

# 设置环境 Setup environment
export TRANSLATE_API_TOKEN="$API_TOKEN"
export TRANSLATE_MODEL="$MODEL"

# 创建输出目录 Create output directory
mkdir -p "$OUTPUT_DIR"

# 翻译所有Markdown文件 Translate all Markdown files
find "$INPUT_DIR" -name "*.md" -type f | while read -r file; do
    # 计算相对路径 Calculate relative path
    rel_path="${file#$INPUT_DIR/}"
    output_file="$OUTPUT_DIR/${rel_path%.*}_zh.md"
    
    # 创建输出目录结构 Create output directory structure
    mkdir -p "$(dirname "$output_file")"
    
    echo "Translating: $file -> $output_file"
    
    # 执行翻译 Execute translation
    if markdown-translator -i "$file" -o "$output_file" -c "$CHUNK_SIZE" -n "$CONCURRENCY"; then
        echo "✅ Success: $file"
    else
        echo "❌ Failed: $file"
    fi
done

echo "Batch translation completed!"
```

#### 并行批量处理 Parallel Batch Processing
```bash
#!/bin/bash
# parallel_batch_translate.sh

# 使用GNU parallel进行并行处理
export TRANSLATE_API_TOKEN="your-api-key"
export TRANSLATE_MODEL="qwen/qwen-2.5-72b-instruct"

# 并行翻译函数 Parallel translation function
translate_file() {
    local input_file="$1"
    local output_file="${input_file%.*}_zh.md"
    
    echo "Processing: $input_file"
    markdown-translator -i "$input_file" -o "$output_file" -c 400 -n 2
}

export -f translate_file

# 并行执行 Execute in parallel
find docs -name "*.md" | parallel -j 4 translate_file {}
```

### 3. Docker 配置 Docker Configuration

#### 基础 Dockerfile
```dockerfile
FROM python:3.11-slim

# 设置工作目录 Set working directory
WORKDIR /app

# 安装系统依赖 Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件 Copy dependency files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码 Copy application code
COPY . .
RUN pip install -e .

# 创建非root用户 Create non-root user
RUN useradd -m -u 1000 translator
USER translator

# 设置入口点 Set entrypoint
ENTRYPOINT ["markdown-translator"]
```

#### Docker Compose 配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  translator:
    build: .
    environment:
      - TRANSLATE_API_TOKEN=${TRANSLATE_API_TOKEN}
      - TRANSLATE_MODEL=${TRANSLATE_MODEL:-qwen/qwen-2.5-72b-instruct}
    volumes:
      - ./docs:/app/docs
      - ./output:/app/output
    command: ["-i", "/app/docs/README.md", "-o", "/app/output/README_zh.md"]

  batch-translator:
    build: .
    environment:
      - TRANSLATE_API_TOKEN=${TRANSLATE_API_TOKEN}
      - TRANSLATE_MODEL=${TRANSLATE_MODEL:-qwen/qwen-2.5-72b-instruct}
    volumes:
      - ./docs:/app/docs
      - ./output:/app/output
      - ./scripts:/app/scripts
    command: ["/app/scripts/batch_translate.sh"]
```

### 4. CI/CD 集成配置 CI/CD Integration Configuration

#### GitHub Actions
```yaml
# .github/workflows/translate-docs.yml
name: Translate Documentation

on:
  push:
    paths: ['docs/**/*.md']
  pull_request:
    paths: ['docs/**/*.md']

jobs:
  translate:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
        
    - name: Install dependencies
      run: |
        pip install markdown-translator
        
    - name: Translate documentation
      env:
        TRANSLATE_API_TOKEN: ${{ secrets.OPENROUTER_API_KEY }}
        TRANSLATE_MODEL: qwen/qwen-2.5-72b-instruct
      run: |
        # 翻译变更的文件 Translate changed files
        git diff --name-only HEAD~1 HEAD | grep '\.md$' | while read file; do
          if [ -f "$file" ]; then
            echo "Translating $file"
            markdown-translator -i "$file" -o "${file%.*}_zh.md" -c 400 -n 3
          fi
        done
        
    - name: Commit translations
      if: github.event_name == 'push'
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add docs/**/*_zh.md
        if git diff --staged --quiet; then
          echo "No changes to commit"
        else
          git commit -m "Auto-translate documentation [skip ci]"
          git push
        fi
```

#### GitLab CI
```yaml
# .gitlab-ci.yml
stages:
  - translate

translate-docs:
  stage: translate
  image: python:3.11-slim
  
  before_script:
    - pip install markdown-translator
    
  script:
    - |
      # 翻译所有Markdown文件 Translate all Markdown files
      find docs -name "*.md" -type f | while read file; do
        echo "Translating $file"
        markdown-translator -i "$file" -o "${file%.*}_zh.md" -c 500 -n 5
      done
      
  after_script:
    - |
      # 提交翻译结果 Commit translation results
      git config --global user.email "gitlab-ci@example.com"
      git config --global user.name "GitLab CI"
      git add docs/**/*_zh.md
      git commit -m "Auto-translate documentation" || true
      git push origin $CI_COMMIT_REF_NAME || true
      
  variables:
    TRANSLATE_API_TOKEN: $OPENROUTER_API_KEY
    TRANSLATE_MODEL: "qwen/qwen-2.5-72b-instruct"
    
  only:
    changes:
      - docs/**/*.md
```

## 🎛️ 性能调优配置 Performance Tuning Configuration

### 1. 内存优化 Memory Optimization

```bash
# 低内存环境配置 Low memory environment
export TRANSLATE_MODEL="qwen/qwen-2.5-7b-instruct"  # 使用较小模型
markdown-translator -i large_file.md -c 200 -n 2 --verbose

# 监控内存使用 Monitor memory usage
# 在另一个终端运行 Run in another terminal
watch -n 1 'ps aux | grep markdown-translator'
```

### 2. 网络优化 Network Optimization

```bash
# 网络优化配置 Network optimization configuration
export TRANSLATE_MODEL="qwen/qwen-2.5-72b-instruct"

# 慢速网络 Slow network
markdown-translator -i file.md -c 300 -n 2

# 快速网络 Fast network
markdown-translator -i file.md -c 800 -n 10

# 不稳定网络 Unstable network
markdown-translator -i file.md -c 150 -n 1 --verbose
```

### 3. 成本优化 Cost Optimization

```bash
# 使用成本较低的模型 Use cost-effective models
export TRANSLATE_MODEL="qwen/qwen-2.5-7b-instruct"

# 增大分块大小减少API调用 Increase chunk size to reduce API calls
markdown-translator -i file.md -c 1000 -n 8

# 批量处理以获得更好的成本效益 Batch processing for better cost efficiency
find docs -name "*.md" -exec markdown-translator -i {} -c 800 -n 6 \;
```

## 📊 监控和日志配置 Monitoring and Logging Configuration

### 1. 详细日志配置 Detailed Logging Configuration

```bash
# 启用详细日志 Enable verbose logging
markdown-translator -i file.md --verbose > translation.log 2>&1

# 自定义日志格式 Custom log format
export LOG_FORMAT="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
markdown-translator -i file.md --verbose
```

### 2. 性能监控 Performance Monitoring

```bash
# 使用time命令监控性能 Monitor performance with time command
time markdown-translator -i large_file.md -c 500 -n 5 --verbose

# 监控系统资源 Monitor system resources
# 在翻译过程中运行 Run during translation
htop
# 或 or
top -p $(pgrep -f markdown-translator)
```

### 3. 错误追踪 Error Tracking

```bash
# 捕获所有输出用于调试 Capture all output for debugging
markdown-translator -i file.md --verbose 2>&1 | tee debug.log

# 只捕获错误 Capture only errors
markdown-translator -i file.md 2> errors.log
```

这些配置示例涵盖了各种使用场景和环境，帮助用户根据自己的需求选择最适合的配置。
