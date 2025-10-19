# Design Document

## Overview

Markdown翻译工具是一个基于Python的命令行应用程序，采用模块化架构设计。工具通过智能分割、并发处理和内容验证机制，确保大型Markdown文件的高质量翻译。系统使用OpenRouter接口调用大语言模型，支持灵活的配置和强大的错误处理能力。

## Architecture

### 系统架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Interface │    │  Config Manager │    │  Logger System  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    Translation Engine     │
                    │  (Main Orchestrator)      │
                    └─────────────┬─────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
┌───────▼────────┐    ┌──────────▼──────────┐    ┌─────────▼────────┐
│ File Splitter  │    │  Translation Pool   │    │  Content Merger  │
│                │    │  (Async Workers)    │    │                  │
└───────┬────────┘    └──────────┬──────────┘    └─────────┬────────┘
        │                        │                         │
┌───────▼────────┐    ┌──────────▼──────────┐    ┌─────────▼────────┐
│ Markdown       │    │  OpenRouter API     │    │ Integrity        │
│ Parser         │    │  Client             │    │ Validator        │
└────────────────┘    └─────────────────────┘    └──────────────────┘
```

### 核心组件关系

- **CLI Interface**: 处理命令行参数和用户交互
- **Translation Engine**: 核心协调器，管理整个翻译流程
- **File Splitter**: 智能分割Markdown文件，保持语法完整性
- **Translation Pool**: 管理并发翻译任务
- **Content Merger**: 合并翻译结果并清理临时文件
- **Integrity Validator**: 验证翻译内容完整性

## Components and Interfaces

### 1. CLI Interface (`cli.py`)

```python
class CLIInterface:
    """命令行接口处理器"""
    
    def parse_arguments(self) -> argparse.Namespace:
        """解析命令行参数"""
        
    def validate_inputs(self, args: argparse.Namespace) -> bool:
        """验证输入参数的有效性"""
        
    def display_progress(self, current: int, total: int) -> None:
        """显示处理进度"""
```

**接口规范:**
- 支持输入文件路径 (`--input`, `-i`)
- 支持输出文件路径 (`--output`, `-o`)
- 支持分割行数配置 (`--chunk-size`, `-c`)
- 支持并发度配置 (`--concurrency`, `-n`)
- 支持详细日志模式 (`--verbose`, `-v`)

### 2. Configuration Manager (`config.py`)

```python
class ConfigManager:
    """配置管理器"""
    
    def load_environment_variables(self) -> Dict[str, str]:
        """加载环境变量配置"""
        
    def validate_api_config(self) -> bool:
        """验证API配置完整性"""
        
    def get_openai_client(self) -> OpenAI:
        """创建配置好的OpenAI客户端"""
```

**环境变量接口:**
- `TRANSLATE_API`: API基础URL (默认: "https://openrouter.ai/api/v1")
- `TRANSLATE_API_TOKEN`: API访问令牌 (必需)
- `TRANSLATE_MODEL`: 使用的模型名称 (默认: "qwen/qwen3-next-80b-a3b-instruct")

### 3. Markdown Splitter (`splitter.py`)

```python
class MarkdownSplitter:
    """智能Markdown分割器"""
    
    def __init__(self, chunk_size: int = 500):
        self.chunk_size = chunk_size
        self.syntax_patterns = self._compile_patterns()
    
    def split_file(self, file_path: str) -> List[FileChunk]:
        """分割Markdown文件为智能片段"""
        
    def _find_safe_split_point(self, lines: List[str], target_line: int) -> int:
        """找到安全的分割点，避免破坏Markdown语法"""
        
    def _is_in_code_block(self, lines: List[str], line_index: int) -> bool:
        """检查指定行是否在代码块内"""
        
    def _is_in_table(self, lines: List[str], line_index: int) -> bool:
        """检查指定行是否在表格内"""
```

**智能分割策略:**
- 检测代码块边界 (```、~~~)
- 识别表格结构
- 保持列表项完整性
- 避免在标题层级中间分割
- 保持链接引用完整性

### 4. Translation Pool (`translator.py`)

```python
class TranslationPool:
    """并发翻译处理池"""
    
    def __init__(self, concurrency: int = 5, api_client: OpenAI = None):
        self.concurrency = concurrency
        self.api_client = api_client
        self.semaphore = asyncio.Semaphore(concurrency)
    
    async def translate_chunks(self, chunks: List[FileChunk]) -> List[TranslationResult]:
        """并发翻译所有片段"""
        
    async def _translate_single_chunk(self, chunk: FileChunk) -> TranslationResult:
        """翻译单个片段"""
        
    def _create_translation_prompt(self, content: str) -> str:
        """创建翻译提示词"""
```

**翻译策略:**
- 使用信号量控制并发度
- 实现指数退避重试机制
- 添加内容完整性标识符
- 保持Markdown格式不变

### 5. Integrity Validator (`validator.py`)

```python
class IntegrityValidator:
    """内容完整性验证器"""
    
    INTEGRITY_MARKERS = {
        'start': '<<<TRANSLATION_START_MARKER>>>',
        'end': '<<<TRANSLATION_END_MARKER>>>'
    }
    
    def add_markers(self, content: str) -> str:
        """为内容添加完整性标识符"""
        
    def validate_translation(self, original: str, translated: str) -> ValidationResult:
        """验证翻译内容完整性"""
        
    def remove_markers(self, content: str) -> str:
        """移除完整性标识符"""
        
    def _check_line_count_similarity(self, original: str, translated: str) -> bool:
        """检查行数相似性"""
```

**验证机制:**
- 头尾标识符验证
- 行数差异检查 (允许±10%差异)
- Markdown语法结构验证
- 代码块完整性检查

### 6. Content Merger (`merger.py`)

```python
class ContentMerger:
    """翻译内容合并器"""
    
    def merge_translations(self, results: List[TranslationResult], output_path: str) -> MergeResult:
        """合并翻译结果为最终文件"""
        
    def cleanup_temp_files(self, temp_files: List[str]) -> None:
        """清理临时文件"""
        
    def generate_statistics(self, results: List[TranslationResult]) -> TranslationStats:
        """生成翻译统计信息"""
```

## Data Models

### 核心数据结构

```python
@dataclass
class FileChunk:
    """文件片段数据模型"""
    id: str
    content: str
    start_line: int
    end_line: int
    original_file: str
    
@dataclass
class TranslationResult:
    """翻译结果数据模型"""
    chunk_id: str
    original_content: str
    translated_content: str
    success: bool
    error_message: Optional[str] = None
    retry_count: int = 0
    processing_time: float = 0.0
    
@dataclass
class ValidationResult:
    """验证结果数据模型"""
    is_valid: bool
    issues: List[str]
    confidence_score: float
    
@dataclass
class TranslationStats:
    """翻译统计数据模型"""
    total_chunks: int
    successful_translations: int
    failed_translations: int
    total_lines: int
    total_processing_time: float
    average_chunk_time: float
```

## Error Handling

### 错误分类和处理策略

#### 1. 配置错误
- **环境变量缺失**: 显示详细错误信息，提供配置指导
- **API配置无效**: 验证连接性，提供诊断建议
- **文件路径错误**: 检查文件存在性和权限

#### 2. API调用错误
- **网络超时**: 指数退避重试 (最多3次)
- **API限流**: 动态调整请求间隔
- **认证失败**: 立即停止，提示检查API密钥
- **模型不可用**: 提供备选模型建议

#### 3. 内容处理错误
- **分割失败**: 降级到简单行数分割
- **翻译验证失败**: 自动重试，记录问题片段
- **合并错误**: 保留部分结果，报告失败片段

#### 4. 系统资源错误
- **内存不足**: 减少并发度，增加分割粒度
- **磁盘空间不足**: 清理临时文件，压缩输出
- **文件权限错误**: 提供权限修复建议

### 错误恢复机制

```python
class ErrorRecoveryManager:
    """错误恢复管理器"""
    
    def __init__(self):
        self.retry_strategies = {
            'api_timeout': ExponentialBackoffRetry(max_retries=3),
            'rate_limit': AdaptiveDelayRetry(),
            'validation_failure': ContentReprocessRetry(),
        }
    
    async def handle_error(self, error: Exception, context: Dict) -> RecoveryAction:
        """处理错误并返回恢复动作"""
        
    def create_checkpoint(self, progress: TranslationProgress) -> str:
        """创建进度检查点"""
        
    def restore_from_checkpoint(self, checkpoint_path: str) -> TranslationProgress:
        """从检查点恢复进度"""
```

## Testing Strategy

### 测试层级结构

#### 1. 单元测试
- **MarkdownSplitter**: 测试各种Markdown语法的分割正确性
- **IntegrityValidator**: 测试标识符添加/移除和验证逻辑
- **ConfigManager**: 测试环境变量加载和验证
- **TranslationPool**: 测试并发控制和错误处理

#### 2. 集成测试
- **API集成**: 使用测试API密钥验证OpenRouter连接
- **文件处理流程**: 端到端测试小文件翻译流程
- **错误恢复**: 模拟各种错误场景的恢复能力

#### 3. 性能测试
- **大文件处理**: 测试10MB+文件的处理能力
- **并发性能**: 测试不同并发度下的性能表现
- **内存使用**: 监控内存使用模式和峰值

#### 4. 兼容性测试
- **Markdown变体**: 测试GitHub、CommonMark等不同Markdown方言
- **特殊字符**: 测试Unicode、表情符号等特殊内容
- **大型表格**: 测试复杂表格结构的处理

### 测试数据集

```python
TEST_CASES = {
    'simple_markdown': 'tests/data/simple.md',
    'complex_structure': 'tests/data/complex_with_tables_and_code.md',
    'large_file': 'tests/data/large_10mb.md',
    'unicode_content': 'tests/data/unicode_mixed.md',
    'edge_cases': 'tests/data/edge_cases.md'
}
```

## Performance Considerations

### 性能优化策略

#### 1. 内存管理
- **流式处理**: 避免将整个文件加载到内存
- **分块处理**: 控制单个片段大小，防止内存溢出
- **垃圾回收**: 及时释放已处理片段的内存

#### 2. 并发优化
- **自适应并发**: 根据API响应时间动态调整并发度
- **连接池**: 复用HTTP连接，减少连接开销
- **批量处理**: 在可能的情况下批量发送请求

#### 3. 缓存策略
- **翻译缓存**: 缓存相同内容的翻译结果
- **分割缓存**: 缓存文件分割结果，支持增量处理
- **配置缓存**: 缓存API客户端配置

#### 4. 磁盘I/O优化
- **异步文件操作**: 使用异步I/O减少阻塞
- **临时文件管理**: 优化临时文件的创建和清理
- **压缩存储**: 对大型临时文件使用压缩

### 性能监控

```python
class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {
            'api_response_times': [],
            'chunk_processing_times': [],
            'memory_usage_samples': [],
            'error_rates': {}
        }
    
    def record_api_call(self, duration: float, success: bool) -> None:
        """记录API调用性能"""
        
    def record_memory_usage(self) -> None:
        """记录内存使用情况"""
        
    def generate_performance_report(self) -> Dict:
        """生成性能报告"""
```

## Security Considerations

### 安全设计原则

#### 1. API密钥安全
- **环境变量存储**: 避免硬编码API密钥
- **权限最小化**: 使用只读API密钥（如果可用）
- **密钥轮换**: 支持动态更新API密钥

#### 2. 数据保护
- **临时文件加密**: 对敏感内容的临时文件进行加密
- **内存清理**: 处理完成后清理内存中的敏感数据
- **日志脱敏**: 避免在日志中记录敏感内容

#### 3. 网络安全
- **HTTPS强制**: 所有API调用使用HTTPS
- **证书验证**: 验证API服务器证书
- **超时控制**: 设置合理的网络超时时间

#### 4. 输入验证
- **文件类型检查**: 验证输入文件确实是Markdown格式
- **大小限制**: 设置合理的文件大小上限
- **路径验证**: 防止路径遍历攻击

### 安全实现

```python
class SecurityManager:
    """安全管理器"""
    
    def validate_file_path(self, path: str) -> bool:
        """验证文件路径安全性"""
        
    def encrypt_temp_file(self, content: str) -> bytes:
        """加密临时文件内容"""
        
    def sanitize_log_content(self, content: str) -> str:
        """清理日志内容中的敏感信息"""
        
    def validate_api_response(self, response: Dict) -> bool:
        """验证API响应的安全性"""
```

## Deployment and Configuration

### 部署要求

#### 系统要求
- Python 3.8+
- 最小内存: 512MB
- 推荐内存: 2GB+
- 磁盘空间: 至少是输入文件大小的3倍

#### 依赖管理
```python
# requirements.txt
openai>=1.0.0
aiohttp>=3.8.0
asyncio-throttle>=1.0.0
click>=8.0.0
rich>=12.0.0  # 用于美观的CLI输出
pydantic>=2.0.0  # 用于数据验证
```

#### 配置文件支持
```yaml
# config.yaml (可选配置文件)
translation:
  default_chunk_size: 500
  default_concurrency: 5
  max_retries: 3
  timeout_seconds: 30

api:
  base_url: "https://openrouter.ai/api/v1"
  model: "qwen/qwen3-next-80b-a3b-instruct"
  
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### 安装和使用

```bash
# 安装
pip install markdown-translator

# 基本使用
markdown-translator -i README.md -o README_zh.md

# 高级配置
markdown-translator \
  --input large_doc.md \
  --output large_doc_zh.md \
  --chunk-size 1000 \
  --concurrency 10 \
  --verbose

# 环境变量配置
export TRANSLATE_API_TOKEN="your_openrouter_key"
export TRANSLATE_MODEL="qwen/qwen3-next-80b-a3b-instruct"
```

这个设计文档提供了完整的架构蓝图，确保工具的可靠性、性能和安全性。通过模块化设计和完善的错误处理，工具能够处理各种复杂的Markdown文件翻译需求。
