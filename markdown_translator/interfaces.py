"""
Core interfaces and abstract base classes for the Markdown translator.

This module defines the contracts that different components must implement,
ensuring consistent behavior across the translation pipeline.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .models import (
    FileChunk, 
    TranslationResult, 
    ValidationResult, 
    TranslationStats,
    MergeResult
)


class ISplitter(ABC):
    """Interface for Markdown file splitters."""
    
    @abstractmethod
    def split_file(self, file_path: str) -> List[FileChunk]:
        """
        Split a Markdown file into chunks for translation.
        
        Args:
            file_path: Path to the Markdown file to split
            
        Returns:
            List of FileChunk objects representing the split content
        """
        pass
    
    @abstractmethod
    def get_chunk_size(self) -> int:
        """Get the configured chunk size."""
        pass
    
    @abstractmethod
    def set_chunk_size(self, size: int) -> None:
        """Set the chunk size for splitting."""
        pass


class ITranslator(ABC):
    """Interface for translation services."""
    
    @abstractmethod
    async def translate_chunks(self, chunks: List[FileChunk]) -> List[TranslationResult]:
        """
        Translate a list of file chunks.
        
        Args:
            chunks: List of FileChunk objects to translate
            
        Returns:
            List of TranslationResult objects with translation results
        """
        pass
    
    @abstractmethod
    async def translate_single_chunk(self, chunk: FileChunk) -> TranslationResult:
        """
        Translate a single file chunk.
        
        Args:
            chunk: FileChunk object to translate
            
        Returns:
            TranslationResult object with the translation result
        """
        pass
    
    @abstractmethod
    def get_concurrency(self) -> int:
        """Get the current concurrency level."""
        pass
    
    @abstractmethod
    def set_concurrency(self, concurrency: int) -> None:
        """Set the concurrency level for translation."""
        pass


class IValidator(ABC):
    """Interface for translation content validators."""
    
    @abstractmethod
    def add_markers(self, content: str) -> str:
        """
        Add integrity markers to content before translation.
        
        Args:
            content: Original content to add markers to
            
        Returns:
            Content with integrity markers added
        """
        pass
    
    @abstractmethod
    def validate_translation(self, original: str, translated: str) -> ValidationResult:
        """
        Validate that translated content maintains integrity.
        
        Args:
            original: Original content with markers
            translated: Translated content that should have markers
            
        Returns:
            ValidationResult indicating whether validation passed
        """
        pass
    
    @abstractmethod
    def remove_markers(self, content: str) -> str:
        """
        Remove integrity markers from translated content.
        
        Args:
            content: Translated content with markers
            
        Returns:
            Clean translated content without markers
        """
        pass


class IMerger(ABC):
    """Interface for merging translated chunks."""
    
    @abstractmethod
    def merge_translations(self, results: List[TranslationResult], output_path: str) -> MergeResult:
        """
        Merge translation results into a final output file.
        
        Args:
            results: List of TranslationResult objects to merge
            output_path: Path where the merged file should be written
            
        Returns:
            MergeResult indicating success/failure and statistics
        """
        pass
    
    @abstractmethod
    def cleanup_temp_files(self, temp_files: List[str]) -> None:
        """
        Clean up temporary files created during processing.
        
        Args:
            temp_files: List of temporary file paths to clean up
        """
        pass
    
    @abstractmethod
    def generate_statistics(self, results: List[TranslationResult]) -> TranslationStats:
        """
        Generate statistics from translation results.
        
        Args:
            results: List of TranslationResult objects
            
        Returns:
            TranslationStats object with computed statistics
        """
        pass


class IConfigManager(ABC):
    """Interface for configuration management."""
    
    @abstractmethod
    def load_environment_variables(self) -> Dict[str, str]:
        """
        Load configuration from environment variables.
        
        Returns:
            Dictionary of configuration values
        """
        pass
    
    @abstractmethod
    def validate_api_config(self) -> bool:
        """
        Validate that API configuration is complete and valid.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_api_client(self) -> Any:
        """
        Get a configured API client for translation services.
        
        Returns:
            Configured API client object
        """
        pass
    
    @abstractmethod
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: Configuration key to retrieve
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        pass


class ILogger(ABC):
    """Interface for logging services."""
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Log an info message."""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message."""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """Log an error message."""
        pass
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message."""
        pass


class IProgressReporter(ABC):
    """Interface for progress reporting."""
    
    @abstractmethod
    def start_progress(self, total_items: int, description: str = "") -> None:
        """
        Start progress tracking.
        
        Args:
            total_items: Total number of items to process
            description: Description of the operation
        """
        pass
    
    @abstractmethod
    def update_progress(self, completed: int, message: str = "") -> None:
        """
        Update progress.
        
        Args:
            completed: Number of completed items
            message: Optional status message
        """
        pass
    
    @abstractmethod
    def finish_progress(self, success: bool = True, message: str = "") -> None:
        """
        Finish progress tracking.
        
        Args:
            success: Whether the operation completed successfully
            message: Final status message
        """
        pass
