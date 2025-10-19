"""
Content merger for combining translated Markdown chunks.

This module provides functionality to merge translated chunks back into complete files,
clean up temporary files, and generate translation statistics.
"""

import os
import logging
from typing import List, Optional
from pathlib import Path

from .interfaces import IMerger
from .models import TranslationResult, MergeResult, TranslationStats


class ContentMerger(IMerger):
    """
    Merges translated chunks back into complete Markdown files.
    
    This class handles the final stage of the translation process by:
    - Combining translated chunks in the correct order
    - Writing the merged content to the output file
    - Cleaning up temporary files
    - Generating comprehensive statistics
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the ContentMerger.
        
        Args:
            logger: Optional logger instance for logging operations
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def merge_translations(self, results: List[TranslationResult], output_path: str) -> MergeResult:
        """
        Merge translation results into a final output file.
        
        Args:
            results: List of TranslationResult objects to merge
            output_path: Path where the merged file should be written
            
        Returns:
            MergeResult indicating success/failure and statistics
        """
        self.logger.info(f"开始合并 {len(results)} 个翻译片段到 {output_path}")
        
        errors = []
        chunks_merged = 0
        
        try:
            # 验证输入
            if not results:
                error_msg = "没有翻译结果可以合并"
                self.logger.error(error_msg)
                return MergeResult(
                    success=False,
                    output_file=output_path,
                    chunks_merged=0,
                    total_chunks=0,
                    errors=[error_msg]
                )
            
            # 按chunk_id排序以确保正确的顺序
            # 假设chunk_id格式为 "chunk_001", "chunk_002" 等
            sorted_results = self._sort_results_by_chunk_id(results)
            
            # 验证所有翻译都成功了
            failed_chunks = [r for r in sorted_results if not r.success]
            if failed_chunks:
                error_msg = f"发现 {len(failed_chunks)} 个失败的翻译片段"
                self.logger.warning(error_msg)
                errors.append(error_msg)
                for failed in failed_chunks:
                    errors.append(f"片段 {failed.chunk_id}: {failed.error_message}")
            
            # 创建输出目录（如果不存在）
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 合并内容
            merged_content = []
            line_count = 0
            
            for result in sorted_results:
                if result.success and result.translated_content:
                    # 移除可能存在的完整性标记
                    clean_content = self._clean_translated_content(result.translated_content)
                    merged_content.append(clean_content)
                    line_count += len(clean_content.splitlines())
                    chunks_merged += 1
                    self.logger.debug(f"合并片段 {result.chunk_id}")
                else:
                    # 对于失败的片段，使用原始内容作为后备
                    if result.original_content:
                        self.logger.warning(f"片段 {result.chunk_id} 翻译失败，使用原始内容")
                        merged_content.append(result.original_content)
                        line_count += len(result.original_content.splitlines())
                        chunks_merged += 1
                    else:
                        error_msg = f"片段 {result.chunk_id} 没有可用的内容"
                        self.logger.error(error_msg)
                        errors.append(error_msg)
            
            # 写入合并后的文件
            final_content = '\n'.join(merged_content)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            self.logger.info(f"成功合并 {chunks_merged} 个片段到 {output_path}")
            self.logger.info(f"最终文件包含 {line_count} 行")
            
            return MergeResult(
                success=len(errors) == 0,
                output_file=output_path,
                chunks_merged=chunks_merged,
                total_chunks=len(results),
                errors=errors,
                final_line_count=line_count
            )
            
        except Exception as e:
            error_msg = f"合并过程中发生错误: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return MergeResult(
                success=False,
                output_file=output_path,
                chunks_merged=chunks_merged,
                total_chunks=len(results),
                errors=[error_msg]
            )
    
    def cleanup_temp_files(self, temp_files: List[str]) -> None:
        """
        Clean up temporary files created during processing.
        
        Args:
            temp_files: List of temporary file paths to clean up
        """
        if not temp_files:
            self.logger.debug("没有临时文件需要清理")
            return
        
        self.logger.info(f"开始清理 {len(temp_files)} 个临时文件")
        
        cleaned_count = 0
        failed_count = 0
        
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    cleaned_count += 1
                    self.logger.debug(f"已删除临时文件: {temp_file}")
                else:
                    self.logger.debug(f"临时文件不存在: {temp_file}")
            except Exception as e:
                failed_count += 1
                self.logger.warning(f"删除临时文件失败 {temp_file}: {str(e)}")
        
        self.logger.info(f"临时文件清理完成: 成功 {cleaned_count}, 失败 {failed_count}")
    
    def generate_statistics(self, results: List[TranslationResult]) -> TranslationStats:
        """
        Generate statistics from translation results.
        
        Args:
            results: List of TranslationResult objects
            
        Returns:
            TranslationStats object with computed statistics
        """
        if not results:
            return TranslationStats(
                total_chunks=0,
                successful_translations=0,
                failed_translations=0,
                total_lines=0,
                total_processing_time=0.0,
                average_chunk_time=0.0,
                total_retries=0,
                api_calls_made=0
            )
        
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_processing_time = sum(r.processing_time for r in results)
        total_retries = sum(r.retry_count for r in results)
        
        # 计算总行数（基于原始内容）
        total_lines = 0
        for result in results:
            if result.original_content:
                total_lines += len(result.original_content.splitlines())
        
        # API调用次数 = 成功的翻译 + 重试次数
        api_calls_made = successful + total_retries
        
        # 平均处理时间
        average_chunk_time = total_processing_time / len(results) if results else 0.0
        
        stats = TranslationStats(
            total_chunks=len(results),
            successful_translations=successful,
            failed_translations=failed,
            total_lines=total_lines,
            total_processing_time=total_processing_time,
            average_chunk_time=average_chunk_time,
            total_retries=total_retries,
            api_calls_made=api_calls_made
        )
        
        self.logger.info(f"翻译统计: {successful}/{len(results)} 成功 "
                        f"({stats.success_rate:.1f}%), "
                        f"总耗时 {total_processing_time:.2f}秒")
        
        return stats
    
    def _sort_results_by_chunk_id(self, results: List[TranslationResult]) -> List[TranslationResult]:
        """
        Sort translation results by sequence number to maintain correct order.
        
        Args:
            results: List of TranslationResult objects
            
        Returns:
            Sorted list of TranslationResult objects
        """
        try:
            # 首先尝试使用sequence_number排序（最可靠）
            if all(hasattr(r, 'sequence_number') for r in results):
                return sorted(results, key=lambda r: r.sequence_number)
            
            # 后备方案：从chunk_id提取序号
            def extract_chunk_number(chunk_id: str) -> int:
                """Extract numeric part from chunk ID for sorting."""
                try:
                    # 假设chunk_id格式为 "chunk_001_xxxxx"
                    if '_' in chunk_id:
                        parts = chunk_id.split('_')
                        if len(parts) >= 2 and parts[1].isdigit():
                            return int(parts[1])
                        # 尝试最后一个数字部分
                        for part in reversed(parts):
                            if part.isdigit():
                                return int(part)
                    
                    # 如果没有下划线，尝试提取末尾的数字
                    import re
                    match = re.search(r'(\d+)', chunk_id)
                    if match:
                        return int(match.group(1))
                    else:
                        return 0
                except (ValueError, IndexError):
                    self.logger.warning(f"无法解析chunk ID: {chunk_id}")
                    return 0
            
            return sorted(results, key=lambda r: extract_chunk_number(r.chunk_id))
            
        except Exception as e:
            self.logger.warning(f"排序chunk时出错: {str(e)}, 使用原始顺序")
            return results
    
    def _clean_translated_content(self, content: str) -> str:
        """
        Clean translated content by removing integrity markers and normalizing.
        
        Args:
            content: Translated content that may contain markers
            
        Returns:
            Cleaned content without markers
        """
        # 移除常见的完整性标记
        markers_to_remove = [
            '<<<TRANSLATION_START_MARKER>>>',
            '<<<TRANSLATION_END_MARKER>>>',
            '<!-- TRANSLATION_START -->',
            '<!-- TRANSLATION_END -->'
        ]
        
        cleaned = content
        for marker in markers_to_remove:
            cleaned = cleaned.replace(marker, '')
        
        # 规范化换行符和空白
        lines = cleaned.splitlines()
        # 移除开头和结尾的空行
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        return '\n'.join(lines)
