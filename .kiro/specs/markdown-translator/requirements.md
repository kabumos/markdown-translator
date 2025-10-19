# Requirements Document

## Introduction

这是一个Python命令行工具，用于将Markdown文件翻译成中文。该工具通过智能分割、并发处理和内容验证来确保翻译质量和完整性。工具使用OpenRouter接口调用大语言模型进行翻译，支持自定义参数配置。

## Requirements

### Requirement 1

**User Story:** 作为开发者，我希望能够将大型Markdown文件按照合理的方式分割，以便进行批量翻译处理。

#### Acceptance Criteria

1. WHEN 用户指定输入文件 THEN 系统 SHALL 按照每500行（默认）将文件分割为多个片段
2. WHEN 进行文件分割时 THEN 系统 SHALL 确保不会在Markdown语法结构中间进行分割
3. WHEN 分割完成后 THEN 系统 SHALL 为每个片段生成唯一的临时文件名
4. IF 用户指定了自定义分割行数 THEN 系统 SHALL 使用用户指定的行数进行分割

### Requirement 2

**User Story:** 作为用户，我希望工具能够并发调用翻译API，以提高翻译效率。

#### Acceptance Criteria

1. WHEN 开始翻译处理时 THEN 系统 SHALL 使用默认并发度5进行处理
2. IF 用户指定了自定义并发度 THEN 系统 SHALL 使用用户指定的并发度
3. WHEN 调用翻译API时 THEN 系统 SHALL 使用OpenAI库通过OpenRouter接口
4. WHEN 发生API调用错误时 THEN 系统 SHALL 实现重试机制并记录错误日志

### Requirement 3

**User Story:** 作为用户，我希望能够通过环境变量配置API相关参数，以确保安全性和灵活性。

#### Acceptance Criteria

1. WHEN 系统启动时 THEN 系统 SHALL 从环境变量TRANSLATE_API读取API基础URL
2. WHEN 系统启动时 THEN 系统 SHALL 从环境变量TRANSLATE_API_TOKEN读取API密钥
3. WHEN 系统启动时 THEN 系统 SHALL 从环境变量TRANSLATE_MODEL读取使用的模型名称
4. IF 任何必需的环境变量未设置 THEN 系统 SHALL 显示错误信息并退出

### Requirement 4

**User Story:** 作为用户，我希望工具能够验证翻译内容的完整性，确保没有内容丢失。

#### Acceptance Criteria

1. WHEN 开始翻译每个片段时 THEN 系统 SHALL 在内容头尾添加特定标识符
2. WHEN 翻译完成后 THEN 系统 SHALL 验证标识符是否完整存在
3. WHEN 验证失败时 THEN 系统 SHALL 记录错误并重新尝试翻译该片段
4. WHEN 所有验证通过时 THEN 系统 SHALL 移除标识符并保留纯翻译内容

### Requirement 5

**User Story:** 作为用户，我希望工具能够将翻译后的片段合并为完整的文件。

#### Acceptance Criteria

1. WHEN 所有片段翻译完成后 THEN 系统 SHALL 按照原始顺序合并所有翻译片段
2. WHEN 合并完成后 THEN 系统 SHALL 生成最终的翻译文件
3. WHEN 合并过程中 THEN 系统 SHALL 清理所有临时文件
4. WHEN 合并完成后 THEN 系统 SHALL 显示翻译统计信息（总行数、片段数等）

### Requirement 6

**User Story:** 作为用户，我希望工具提供灵活的命令行参数配置。

#### Acceptance Criteria

1. WHEN 用户运行工具时 THEN 系统 SHALL 支持指定输入文件路径参数
2. WHEN 用户运行工具时 THEN 系统 SHALL 支持指定输出文件路径参数
3. WHEN 用户运行工具时 THEN 系统 SHALL 支持指定分割行数参数
4. WHEN 用户运行工具时 THEN 系统 SHALL 支持指定并发度参数
5. IF 用户未指定输出路径 THEN 系统 SHALL 使用默认命名规则生成输出文件名

### Requirement 7

**User Story:** 作为用户，我希望工具能够提供详细的日志和错误处理。

#### Acceptance Criteria

1. WHEN 工具运行时 THEN 系统 SHALL 显示处理进度信息
2. WHEN 发生错误时 THEN 系统 SHALL 记录详细的错误信息
3. WHEN 翻译完成时 THEN 系统 SHALL 显示成功统计信息
4. WHEN 调用API时 THEN 系统 SHALL 记录API调用的详细日志
