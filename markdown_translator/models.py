"""
Core data models for the Markdown translator.

This module defines the data structures used throughout the translation process,
including file chunks, translation results, validation results, and statistics.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class TranslationStatus(Enum):
    """Translation status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class FileChunk:
    """
    Represents a chunk of a Markdown file for translation.
    
    Attributes:
        id: Unique identifier for the chunk
        content: The actual content of the chunk
        start_line: Starting line number in the original file
        end_line: Ending line number in the original file
        original_file: Path to the original file
        sequence_number: Sequential number for ordering (0-based)
        temp_file: Path to temporary file (if created)
    """
    id: str
    content: str
    start_line: int
    end_line: int
    original_file: str
    sequence_number: int = 0
    temp_file: Optional[str] = None


@dataclass
class TranslationResult:
    """
    Represents the result of translating a file chunk.
    
    Attributes:
        chunk_id: ID of the chunk that was translated
        original_content: Original content before translation
        translated_content: Translated content
        success: Whether the translation was successful
        sequence_number: Sequential number for ordering (0-based)
        error_message: Error message if translation failed
        retry_count: Number of retry attempts made
        processing_time: Time taken to process this chunk (in seconds)
        status: Current status of the translation
    """
    chunk_id: str
    original_content: str
    translated_content: str
    success: bool
    sequence_number: int = 0
    error_message: Optional[str] = None
    retry_count: int = 0
    processing_time: float = 0.0
    status: TranslationStatus = TranslationStatus.PENDING


@dataclass
class ValidationResult:
    """
    Represents the result of validating translated content.
    
    Attributes:
        is_valid: Whether the validation passed
        issues: List of validation issues found
        confidence_score: Confidence score of the validation (0.0 to 1.0)
        line_count_diff: Difference in line count between original and translated
        has_markers: Whether integrity markers were found and valid
    """
    is_valid: bool
    issues: List[str]
    confidence_score: float
    line_count_diff: int = 0
    has_markers: bool = False


@dataclass
class TranslationStats:
    """
    Statistics about the translation process.
    
    Attributes:
        total_chunks: Total number of chunks processed
        successful_translations: Number of successful translations
        failed_translations: Number of failed translations
        total_lines: Total number of lines processed
        total_processing_time: Total time taken for all processing
        average_chunk_time: Average time per chunk
        total_retries: Total number of retry attempts
        api_calls_made: Total number of API calls made
    """
    total_chunks: int
    successful_translations: int
    failed_translations: int
    total_lines: int
    total_processing_time: float
    average_chunk_time: float
    total_retries: int = 0
    api_calls_made: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate as a percentage."""
        if self.total_chunks == 0:
            return 0.0
        return (self.successful_translations / self.total_chunks) * 100.0


@dataclass
class TranslationProgress:
    """
    Represents the current progress of a translation job.
    
    Attributes:
        completed_chunks: Number of chunks completed
        total_chunks: Total number of chunks
        current_chunk_id: ID of currently processing chunk
        start_time: When the translation started
        estimated_completion: Estimated completion time
        errors: List of errors encountered
    """
    completed_chunks: int
    total_chunks: int
    current_chunk_id: Optional[str] = None
    start_time: Optional[float] = None
    estimated_completion: Optional[float] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_chunks == 0:
            return 0.0
        return (self.completed_chunks / self.total_chunks) * 100.0


@dataclass
class MergeResult:
    """
    Result of merging translated chunks back into a complete file.
    
    Attributes:
        success: Whether the merge was successful
        output_file: Path to the output file
        chunks_merged: Number of chunks successfully merged
        total_chunks: Total number of chunks that should have been merged
        errors: List of errors encountered during merge
        final_line_count: Number of lines in the final merged file
    """
    success: bool
    output_file: str
    chunks_merged: int
    total_chunks: int
    errors: List[str]
    final_line_count: int = 0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
