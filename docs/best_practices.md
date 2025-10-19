# 最佳实践指南 Best Practices Guide

本指南提供使用Markdown Translator的最佳实践，帮助您获得最佳的翻译质量和性能。

This guide provides best practices for using Markdown Translator to achieve optimal translation quality and performance.

## 🎯 翻译质量优化 Translation Quality Optimization

### 1. 选择合适的模型 Choose the Right Model

#### 高质量翻译 High Quality Translation
```bash
# 适用于重要文档、技术文档、正式发布内容
# For important documents, technical docs, official releases
export TRANSLATE_MODEL="claude-3-5-sonnet-20241022"
markdown-translator -i important_doc.md -c 200 -n 2 --verbose
```

#### 平衡质量和速度 Balance Quality and Speed
```bash
# 适用于日常文档、博客文章、内部文档
# For daily docs, blog posts, internal documentation
export TRANSLATE_MODEL="qwen/qwen-2.5-72b-instruct"
markdown-translator -i regular_doc.md -c 400 -n 5
```

#### 快速翻译 Fast Translation
```bash
# 适用于草稿、临时文档、大批量处理
# For drafts, temporary docs, bulk processing
export TRANSLATE_MODEL="qwen/qwen-2.5-7b-instruct"
markdown-translator -i draft_doc.md -c 800 -n 8
```

### 2. 优化分块策略 Optimize Chunking Strategy

#### 根据内容类型调整 Adjust Based on Content Type

```bash
# 技术文档（保持术语一致性）Technical docs (maintain terminology consistency)
markdown-translator -i tech_doc.md -c 150 -n 2

# API文档（保持代码完整性）API docs (maintain code integrity)
markdown-translator -i api_doc.md -c 100 -n 1

# 博客文章（平衡上下文和效率）Blog posts (balance context and efficiency)
markdown-translator -i blog_post.md -c 400 -n 5

# README文件（快速处理）README files (quick processing)
markdown-translator -i README.md -c 600 -n 6
```

#### 根据文件大小调整 Adjust Based on File Size

```bash
# 小文件 < 500行 Small files < 500 lines
markdown-translator -i small.md -c 200 -n 2

# 中等文件 500-2000行 Medium files 500-2000 lines
markdown-translator -i medium.md -c 400 -n 4

# 大文件 > 2000行 Large files > 2000 lines
markdown-translator -i large.md -c 800 -n 6
```

### 3. 预处理文档 Preprocess Documents

#### 清理格式 Clean Formatting
```bash
# 移除多余空行 Remove extra blank lines
sed '/^$/N;/^\n$/d' input.md > cleaned.md

# 统一代码块标记 Standardize code block markers
sed 's/~~~python/```python/g' input.md > standardized.md

# 修复表格格式 Fix table formatting
# 确保表格行对齐正确
```

#### 检查Markdown语法 Check Markdown Syntax
```bash
# 使用markdownlint检查语法 Use markdownlint to check syntax
npm install -g markdownlint-cli
markdownlint input.md

# 修复常见问题 Fix common issues
markdownlint --fix input.md
```

## ⚡ 性能优化 Performance Optimization

### 1. 并发配置优化 Concurrency Configuration Optimization

#### 网络环境评估 Network Environment Assessment
```bash
# 测试网络延迟 Test network latency
ping -c 10 openrouter.ai

# 测试带宽 Test bandwidth
curl -w "@curl-format.txt" -o /dev/null -s https://openrouter.ai/api/v1/models

# 创建curl格式文件 Create curl format file
cat > curl-format.txt << 'EOF'
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
EOF
```

#### 动态调整并发数 Dynamically Adjust Concurrency
```bash
# 快速网络（延迟 < 100ms）Fast network (latency < 100ms)
markdown-translator -i file.md -n 8

# 中等网络（延迟 100-300ms）Medium network (latency 100-300ms)
markdown-translator -i file.md -n 4

# 慢速网络（延迟 > 300ms）Slow network (latency > 300ms)
markdown-translator -i file.md -n 2
```

### 2. 内存管理 Memory Management

#### 监控内存使用 Monitor Memory Usage
```bash
# 实时监控内存 Real-time memory monitoring
watch -n 1 'ps aux | grep markdown-translator | grep -v grep'

# 设置内存限制 Set memory limits
ulimit -v 2097152  # 限制虚拟内存为2GB Limit virtual memory to 2GB
markdown-translator -i large_file.md -c 400 -n 3
```

#### 大文件处理策略 Large File Processing Strategy
```bash
# 方法1：减小分块大小 Method 1: Reduce chunk size
markdown-translator -i huge_file.md -c 200 -n 2

# 方法2：分割文件处理 Method 2: Split file processing
split -l 2000 huge_file.md part_
for part in part_*; do
    markdown-translator -i "$part" -o "${part}_zh.md" -c 500 -n 4
done
cat part_*_zh.md > huge_file_zh.md

# 方法3：流式处理 Method 3: Streaming processing
# 使用自定义脚本逐段处理
```

### 3. 缓存策略 Caching Strategy

#### 避免重复翻译 Avoid Duplicate Translation
```bash
# 创建翻译缓存脚本 Create translation cache script
cat > cached_translate.sh << 'EOF'
#!/bin/bash

INPUT_FILE="$1"
OUTPUT_FILE="$2"
CACHE_DIR=".translation_cache"

# 创建缓存目录 Create cache directory
mkdir -p "$CACHE_DIR"

# 计算文件哈希 Calculate file hash
HASH=$(md5sum "$INPUT_FILE" | cut -d' ' -f1)
CACHE_FILE="$CACHE_DIR/$HASH.md"

if [ -f "$CACHE_FILE" ]; then
    echo "Using cached translation for $INPUT_FILE"
    cp "$CACHE_FILE" "$OUTPUT_FILE"
else
    echo "Translating $INPUT_FILE"
    markdown-translator -i "$INPUT_FILE" -o "$OUTPUT_FILE"
    cp "$OUTPUT_FILE" "$CACHE_FILE"
fi
EOF

chmod +x cached_translate.sh
./cached_translate.sh input.md output_zh.md
```

## 🔒 安全最佳实践 Security Best Practices

### 1. API密钥管理 API Key Management

#### 安全存储 Secure Storage
```bash
# 使用专用的环境文件 Use dedicated environment file
cat > .env.local << 'EOF'
TRANSLATE_API_TOKEN=sk-or-v1-your-secret-key
TRANSLATE_MODEL=qwen/qwen-2.5-72b-instruct
EOF

# 设置严格权限 Set strict permissions
chmod 600 .env.local

# 加载环境变量 Load environment variables
set -a; source .env.local; set +a
```

#### 密钥轮换 Key Rotation
```bash
# 定期更换API密钥 Regularly rotate API keys
# 1. 在OpenRouter生成新密钥
# 2. 更新环境变量
# 3. 测试新密钥
# 4. 撤销旧密钥

# 测试新密钥 Test new key
export TRANSLATE_API_TOKEN="new-key"
markdown-translator -i test.md --dry-run
```

### 2. 文件安全 File Security

#### 输入验证 Input Validation
```bash
# 验证文件类型 Validate file type
file_type=$(file -b --mime-type "$INPUT_FILE")
if [[ "$file_type" != "text/plain" && "$file_type" != "text/markdown" ]]; then
    echo "Error: Invalid file type: $file_type"
    exit 1
fi

# 检查文件大小 Check file size
max_size=$((100 * 1024 * 1024))  # 100MB
file_size=$(stat -c%s "$INPUT_FILE")
if [ "$file_size" -gt "$max_size" ]; then
    echo "Error: File too large: $file_size bytes"
    exit 1
fi
```

#### 路径安全 Path Security
```bash
# 使用绝对路径 Use absolute paths
INPUT_FILE=$(realpath "$1")
OUTPUT_FILE=$(realpath "$2")

# 验证路径在允许的目录内 Verify paths are within allowed directories
ALLOWED_DIR=$(realpath ~/documents)
if [[ "$INPUT_FILE" != "$ALLOWED_DIR"* ]]; then
    echo "Error: Input file outside allowed directory"
    exit 1
fi
```

## 📊 监控和日志 Monitoring and Logging

### 1. 性能监控 Performance Monitoring

#### 创建监控脚本 Create Monitoring Script
```bash
cat > monitor_translation.sh << 'EOF'
#!/bin/bash

LOG_FILE="translation_monitor.log"
INPUT_FILE="$1"

echo "=== Translation Monitor Started: $(date) ===" >> "$LOG_FILE"
echo "Input file: $INPUT_FILE" >> "$LOG_FILE"
echo "File size: $(du -h "$INPUT_FILE" | cut -f1)" >> "$LOG_FILE"

# 记录开始时间 Record start time
START_TIME=$(date +%s)

# 监控系统资源 Monitor system resources
(
    while true; do
        echo "$(date): CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}'), Memory: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')" >> "$LOG_FILE"
        sleep 10
    done
) &
MONITOR_PID=$!

# 执行翻译 Execute translation
markdown-translator -i "$INPUT_FILE" --verbose 2>&1 | tee -a "$LOG_FILE"
TRANSLATION_EXIT_CODE=$?

# 停止监控 Stop monitoring
kill $MONITOR_PID 2>/dev/null

# 记录结束时间 Record end time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "=== Translation Completed: $(date) ===" >> "$LOG_FILE"
echo "Duration: ${DURATION}s" >> "$LOG_FILE"
echo "Exit code: $TRANSLATION_EXIT_CODE" >> "$LOG_FILE"
EOF

chmod +x monitor_translation.sh
./monitor_translation.sh input.md
```

### 2. 错误跟踪 Error Tracking

#### 结构化日志 Structured Logging
```bash
# 创建结构化日志脚本 Create structured logging script
cat > structured_translate.sh << 'EOF'
#!/bin/bash

INPUT_FILE="$1"
OUTPUT_FILE="$2"
LOG_FILE="translation_$(date +%Y%m%d_%H%M%S).json"

# 记录开始事件 Log start event
cat >> "$LOG_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "event": "translation_started",
  "input_file": "$INPUT_FILE",
  "output_file": "$OUTPUT_FILE",
  "file_size": $(stat -c%s "$INPUT_FILE"),
  "line_count": $(wc -l < "$INPUT_FILE")
}
EOF

# 执行翻译并捕获结果 Execute translation and capture results
if markdown-translator -i "$INPUT_FILE" -o "$OUTPUT_FILE" --verbose 2>&1; then
    STATUS="success"
    EXIT_CODE=0
else
    STATUS="failed"
    EXIT_CODE=$?
fi

# 记录完成事件 Log completion event
cat >> "$LOG_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "event": "translation_completed",
  "status": "$STATUS",
  "exit_code": $EXIT_CODE,
  "output_size": $(stat -c%s "$OUTPUT_FILE" 2>/dev/null || echo 0)
}
EOF
EOF

chmod +x structured_translate.sh
./structured_translate.sh input.md output_zh.md
```

## 🔄 批量处理最佳实践 Batch Processing Best Practices

### 1. 并行批量处理 Parallel Batch Processing

#### GNU Parallel 方案 GNU Parallel Solution
```bash
# 安装GNU parallel Install GNU parallel
# Ubuntu/Debian: sudo apt-get install parallel
# macOS: brew install parallel

# 创建并行处理函数 Create parallel processing function
translate_single() {
    local input_file="$1"
    local output_file="${input_file%.*}_zh.md"
    
    echo "Processing: $input_file"
    
    # 根据文件大小调整参数 Adjust parameters based on file size
    local file_size=$(stat -c%s "$input_file")
    local chunk_size=500
    local concurrency=3
    
    if [ "$file_size" -gt 1048576 ]; then  # > 1MB
        chunk_size=800
        concurrency=2
    fi
    
    markdown-translator -i "$input_file" -o "$output_file" \
                       -c "$chunk_size" -n "$concurrency"
}

export -f translate_single
export TRANSLATE_API_TOKEN TRANSLATE_MODEL

# 并行处理所有文件 Process all files in parallel
find docs -name "*.md" | parallel -j 4 translate_single {}
```

#### 队列管理 Queue Management
```bash
# 创建任务队列管理器 Create task queue manager
cat > queue_manager.sh << 'EOF'
#!/bin/bash

QUEUE_FILE="translation_queue.txt"
WORKERS=4
WORKER_PIDS=()

# 创建队列文件 Create queue file
find docs -name "*.md" > "$QUEUE_FILE"

# 工作进程函数 Worker process function
worker() {
    local worker_id="$1"
    local log_file="worker_${worker_id}.log"
    
    while true; do
        # 从队列获取任务 Get task from queue
        local task=$(head -n1 "$QUEUE_FILE" 2>/dev/null)
        if [ -z "$task" ]; then
            break
        fi
        
        # 从队列移除任务 Remove task from queue
        sed -i '1d' "$QUEUE_FILE"
        
        echo "Worker $worker_id processing: $task" | tee -a "$log_file"
        
        # 执行翻译 Execute translation
        if markdown-translator -i "$task" -c 400 -n 2 2>&1 | tee -a "$log_file"; then
            echo "Worker $worker_id completed: $task" | tee -a "$log_file"
        else
            echo "Worker $worker_id failed: $task" | tee -a "$log_file"
            # 重新加入队列 Re-add to queue
            echo "$task" >> "$QUEUE_FILE"
        fi
    done
}

# 启动工作进程 Start worker processes
for i in $(seq 1 $WORKERS); do
    worker "$i" &
    WORKER_PIDS+=($!)
done

# 等待所有工作进程完成 Wait for all workers to complete
for pid in "${WORKER_PIDS[@]}"; do
    wait "$pid"
done

echo "All translations completed!"
EOF

chmod +x queue_manager.sh
./queue_manager.sh
```

### 2. 增量处理 Incremental Processing

#### 基于时间戳的增量更新 Timestamp-based Incremental Updates
```bash
cat > incremental_translate.sh << 'EOF'
#!/bin/bash

SOURCE_DIR="docs"
TARGET_DIR="docs_zh"
TIMESTAMP_FILE=".last_translation"

# 获取上次翻译时间 Get last translation time
if [ -f "$TIMESTAMP_FILE" ]; then
    LAST_TRANSLATION=$(cat "$TIMESTAMP_FILE")
else
    LAST_TRANSLATION=0
fi

# 查找需要更新的文件 Find files that need updating
find "$SOURCE_DIR" -name "*.md" -newer "$TIMESTAMP_FILE" 2>/dev/null | while read file; do
    rel_path="${file#$SOURCE_DIR/}"
    target_file="$TARGET_DIR/${rel_path%.*}_zh.md"
    
    # 创建目标目录 Create target directory
    mkdir -p "$(dirname "$target_file")"
    
    echo "Updating: $file -> $target_file"
    markdown-translator -i "$file" -o "$target_file" -c 500 -n 4
done

# 更新时间戳 Update timestamp
touch "$TIMESTAMP_FILE"
EOF

chmod +x incremental_translate.sh
./incremental_translate.sh
```

## 🚀 CI/CD 集成最佳实践 CI/CD Integration Best Practices

### 1. GitHub Actions 优化 GitHub Actions Optimization

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
    timeout-minutes: 30
    
    strategy:
      matrix:
        # 并行处理不同目录 Process different directories in parallel
        directory: ['docs/api', 'docs/guides', 'docs/tutorials']
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
      with:
        fetch-depth: 2  # 获取变更历史 Get change history
        
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'
        
    - name: Install dependencies
      run: |
        pip install markdown-translator
        
    - name: Get changed files
      id: changed-files
      run: |
        # 只处理变更的文件 Only process changed files
        git diff --name-only HEAD~1 HEAD | grep '\.md$' | grep '^${{ matrix.directory }}' > changed_files.txt || true
        echo "files=$(cat changed_files.txt | tr '\n' ' ')" >> $GITHUB_OUTPUT
        
    - name: Translate changed files
      if: steps.changed-files.outputs.files != ''
      env:
        TRANSLATE_API_TOKEN: ${{ secrets.OPENROUTER_API_KEY }}
        TRANSLATE_MODEL: qwen/qwen-2.5-72b-instruct
      run: |
        # 并行翻译变更的文件 Translate changed files in parallel
        echo "${{ steps.changed-files.outputs.files }}" | xargs -n1 -P4 -I{} \
          markdown-translator -i {} -o {}_zh.md -c 400 -n 2
          
    - name: Commit translations
      if: github.event_name == 'push' && steps.changed-files.outputs.files != ''
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add ${{ matrix.directory }}/**/*_zh.md
        git commit -m "Auto-translate ${{ matrix.directory }} documentation" || exit 0
        git push
```

### 2. 质量检查集成 Quality Check Integration

```bash
# 创建翻译质量检查脚本 Create translation quality check script
cat > quality_check.sh << 'EOF'
#!/bin/bash

ORIGINAL_FILE="$1"
TRANSLATED_FILE="$2"
QUALITY_REPORT="quality_report.json"

echo "Checking translation quality for: $ORIGINAL_FILE -> $TRANSLATED_FILE"

# 基本检查 Basic checks
ORIGINAL_LINES=$(wc -l < "$ORIGINAL_FILE")
TRANSLATED_LINES=$(wc -l < "$TRANSLATED_FILE")
LINE_DIFF_PERCENT=$(echo "scale=2; abs($TRANSLATED_LINES - $ORIGINAL_LINES) / $ORIGINAL_LINES * 100" | bc -l)

# 检查代码块完整性 Check code block integrity
ORIGINAL_CODE_BLOCKS=$(grep -c '```' "$ORIGINAL_FILE")
TRANSLATED_CODE_BLOCKS=$(grep -c '```' "$TRANSLATED_FILE")

# 检查链接完整性 Check link integrity
ORIGINAL_LINKS=$(grep -o '\[.*\](.*)'  "$ORIGINAL_FILE" | wc -l)
TRANSLATED_LINKS=$(grep -o '\[.*\](.*)'  "$TRANSLATED_FILE" | wc -l)

# 生成质量报告 Generate quality report
cat > "$QUALITY_REPORT" << EOF
{
  "original_file": "$ORIGINAL_FILE",
  "translated_file": "$TRANSLATED_FILE",
  "timestamp": "$(date -Iseconds)",
  "metrics": {
    "line_count_diff_percent": $LINE_DIFF_PERCENT,
    "code_blocks_preserved": $([ $ORIGINAL_CODE_BLOCKS -eq $TRANSLATED_CODE_BLOCKS ] && echo true || echo false),
    "links_preserved": $([ $ORIGINAL_LINKS -eq $TRANSLATED_LINKS ] && echo true || echo false)
  },
  "details": {
    "original_lines": $ORIGINAL_LINES,
    "translated_lines": $TRANSLATED_LINES,
    "original_code_blocks": $ORIGINAL_CODE_BLOCKS,
    "translated_code_blocks": $TRANSLATED_CODE_BLOCKS,
    "original_links": $ORIGINAL_LINKS,
    "translated_links": $TRANSLATED_LINKS
  }
}
EOF

# 质量评分 Quality scoring
QUALITY_SCORE=100
if (( $(echo "$LINE_DIFF_PERCENT > 20" | bc -l) )); then
    QUALITY_SCORE=$((QUALITY_SCORE - 30))
fi
if [ $ORIGINAL_CODE_BLOCKS -ne $TRANSLATED_CODE_BLOCKS ]; then
    QUALITY_SCORE=$((QUALITY_SCORE - 25))
fi
if [ $ORIGINAL_LINKS -ne $TRANSLATED_LINKS ]; then
    QUALITY_SCORE=$((QUALITY_SCORE - 20))
fi

echo "Quality Score: $QUALITY_SCORE/100"

# 如果质量分数太低则失败 Fail if quality score is too low
if [ $QUALITY_SCORE -lt 70 ]; then
    echo "Quality check failed! Score: $QUALITY_SCORE"
    exit 1
fi

echo "Quality check passed! Score: $QUALITY_SCORE"
EOF

chmod +x quality_check.sh
```

## 📈 成本优化 Cost Optimization

### 1. 模型选择策略 Model Selection Strategy

```bash
# 根据内容重要性选择模型 Choose model based on content importance
classify_content() {
    local file="$1"
    local filename=$(basename "$file")
    
    # 高优先级文件 High priority files
    if [[ "$filename" =~ ^(README|CHANGELOG|LICENSE|CONTRIBUTING) ]]; then
        echo "claude-3-5-sonnet-20241022"
    # API文档 API documentation
    elif [[ "$file" =~ /api/ ]]; then
        echo "qwen/qwen-2.5-72b-instruct"
    # 内部文档 Internal documentation
    elif [[ "$file" =~ /(internal|draft)/ ]]; then
        echo "qwen/qwen-2.5-7b-instruct"
    # 默认 Default
    else
        echo "qwen/qwen-2.5-72b-instruct"
    fi
}

# 使用分类结果 Use classification result
INPUT_FILE="$1"
SELECTED_MODEL=$(classify_content "$INPUT_FILE")
export TRANSLATE_MODEL="$SELECTED_MODEL"

echo "Using model $SELECTED_MODEL for $INPUT_FILE"
markdown-translator -i "$INPUT_FILE"
```

### 2. 批量折扣优化 Bulk Discount Optimization

```bash
# 批量处理以获得更好的成本效益 Batch processing for better cost efficiency
batch_translate() {
    local files=("$@")
    local batch_size=10
    
    for ((i=0; i<${#files[@]}; i+=batch_size)); do
        local batch=("${files[@]:i:batch_size}")
        
        echo "Processing batch $((i/batch_size + 1)): ${#batch[@]} files"
        
        # 并行处理批次 Process batch in parallel
        printf '%s\n' "${batch[@]}" | xargs -n1 -P4 -I{} \
            markdown-translator -i {} -c 800 -n 2
        
        # 批次间短暂暂停 Brief pause between batches
        sleep 2
    done
}

# 收集所有需要翻译的文件 Collect all files to translate
mapfile -t files < <(find docs -name "*.md" -type f)
batch_translate "${files[@]}"
```

---

**💡 关键要点 Key Takeaways**:

1. **质量优先 Quality First**: 为重要文档选择高质量模型
2. **性能平衡 Performance Balance**: 根据网络和系统资源调整并发参数
3. **安全第一 Security First**: 妥善管理API密钥和验证输入
4. **监控重要 Monitoring Matters**: 实施全面的日志和监控
5. **成本意识 Cost Conscious**: 根据内容重要性选择合适的模型

遵循这些最佳实践将帮助您获得最佳的翻译效果和使用体验。

Following these best practices will help you achieve optimal translation results and user experience.
