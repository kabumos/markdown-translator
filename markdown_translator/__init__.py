"""
Markdown Translator - A tool for translating Markdown files to Chinese using OpenRouter API.

This package provides intelligent splitting, concurrent processing, and content validation
to ensure high-quality translation of large Markdown files.
"""

__version__ = "0.1.0"
__author__ = "Markdown Translator Team"
__email__ = "contact@example.com"

from .models import FileChunk, TranslationResult, ValidationResult, TranslationStats, MergeResult
from .config import ConfigManager
from .merger import ContentMerger
from .progress import RichProgressReporter, TranslationLogger, UserFriendlyErrorReporter
from .logging_config import setup_logging, get_logger, create_component_logger
from .performance import PerformanceMonitor, PerformanceOptimizer
from .security import SecurityManager, InputValidator

# TODO: Import these as they are implemented in future tasks
# from .splitter import MarkdownSplitter
# from .translator import TranslationPool
# from .validator import IntegrityValidator

__all__ = [
    "FileChunk",
    "TranslationResult", 
    "ValidationResult",
    "TranslationStats",
    "MergeResult",
    "ConfigManager",
    "ContentMerger",
    "RichProgressReporter",
    "TranslationLogger",
    "UserFriendlyErrorReporter",
    "setup_logging",
    "get_logger",
    "create_component_logger",
    "PerformanceMonitor",
    "PerformanceOptimizer",
    "SecurityManager",
    "InputValidator",
    # TODO: Add these as they are implemented
    # "MarkdownSplitter",
    # "TranslationPool",
    # "IntegrityValidator",
]
