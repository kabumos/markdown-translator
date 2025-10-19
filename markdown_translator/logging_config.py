"""
Logging configuration for the Markdown translator.

This module provides centralized logging configuration with support for
different log levels, file output, and Rich formatting.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from rich.console import Console
from rich.logging import RichHandler

from .progress import TranslationLogger


class LoggingConfig:
    """
    Centralized logging configuration manager.
    
    Handles setup of loggers with appropriate handlers, formatters,
    and output destinations based on configuration.
    """
    
    # 日志级别映射
    LOG_LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    def __init__(self):
        """Initialize the logging configuration manager."""
        self._loggers: Dict[str, TranslationLogger] = {}
        self._console = Console()
    
    def setup_logging(
        self,
        level: str = 'INFO',
        log_file: Optional[str] = None,
        verbose: bool = False,
        quiet: bool = False
    ) -> TranslationLogger:
        """
        Setup main application logging.
        
        Args:
            level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
            log_file: Optional path to log file
            verbose: Enable verbose (DEBUG) logging
            quiet: Enable quiet mode (ERROR only)
            
        Returns:
            Configured TranslationLogger instance
        """
        # 确定日志级别
        if quiet:
            log_level = logging.ERROR
        elif verbose:
            log_level = logging.DEBUG
        else:
            log_level = self.LOG_LEVELS.get(level.upper(), logging.INFO)
        
        # 生成默认日志文件名（如果未指定）
        if log_file is None and not quiet:
            log_file = self._generate_default_log_file()
        
        # 创建主日志器
        logger = TranslationLogger(
            name="markdown_translator",
            level=log_level,
            log_file=log_file,
            console=self._console
        )
        
        self._loggers["main"] = logger
        
        # 配置第三方库的日志级别
        self._configure_third_party_loggers(log_level)
        
        return logger
    
    def get_logger(self, name: str = "main") -> Optional[TranslationLogger]:
        """
        Get a configured logger by name.
        
        Args:
            name: Logger name
            
        Returns:
            TranslationLogger instance or None if not found
        """
        return self._loggers.get(name)
    
    def create_component_logger(
        self,
        component_name: str,
        level: Optional[int] = None,
        log_file: Optional[str] = None
    ) -> TranslationLogger:
        """
        Create a logger for a specific component.
        
        Args:
            component_name: Name of the component
            level: Optional logging level (inherits from main if not specified)
            log_file: Optional separate log file for this component
            
        Returns:
            Configured TranslationLogger instance
        """
        # 使用主日志器的级别作为默认值
        if level is None and "main" in self._loggers:
            level = self._loggers["main"].logger.level
        elif level is None:
            level = logging.INFO
        
        logger_name = f"markdown_translator.{component_name}"
        
        logger = TranslationLogger(
            name=logger_name,
            level=level,
            log_file=log_file,
            console=self._console
        )
        
        self._loggers[component_name] = logger
        return logger
    
    def _generate_default_log_file(self) -> str:
        """
        Generate a default log file path with timestamp.
        
        Returns:
            Path to the default log file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = Path.home() / ".markdown_translator" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        return str(log_dir / f"translation_{timestamp}.log")
    
    def _configure_third_party_loggers(self, level: int) -> None:
        """
        Configure logging levels for third-party libraries.
        
        Args:
            level: Base logging level to use
        """
        # 设置第三方库的日志级别，避免过多的调试信息
        third_party_loggers = [
            'openai',
            'aiohttp',
            'asyncio',
            'urllib3',
            'httpx'
        ]
        
        # 对于第三方库，使用更高的日志级别
        third_party_level = max(level, logging.WARNING)
        
        for logger_name in third_party_loggers:
            logging.getLogger(logger_name).setLevel(third_party_level)
    
    def shutdown_logging(self) -> None:
        """
        Shutdown all loggers and clean up resources.
        """
        for logger in self._loggers.values():
            for handler in logger.logger.handlers[:]:
                handler.close()
                logger.logger.removeHandler(handler)
        
        self._loggers.clear()


# 全局日志配置实例
_logging_config = LoggingConfig()


def setup_logging(
    level: str = 'INFO',
    log_file: Optional[str] = None,
    verbose: bool = False,
    quiet: bool = False
) -> TranslationLogger:
    """
    Setup application logging (convenience function).
    
    Args:
        level: Logging level
        log_file: Optional log file path
        verbose: Enable verbose logging
        quiet: Enable quiet mode
        
    Returns:
        Configured TranslationLogger instance
    """
    return _logging_config.setup_logging(level, log_file, verbose, quiet)


def get_logger(name: str = "main") -> Optional[TranslationLogger]:
    """
    Get a configured logger (convenience function).
    
    Args:
        name: Logger name
        
    Returns:
        TranslationLogger instance or None
    """
    return _logging_config.get_logger(name)


def create_component_logger(
    component_name: str,
    level: Optional[int] = None,
    log_file: Optional[str] = None
) -> TranslationLogger:
    """
    Create a component logger (convenience function).
    
    Args:
        component_name: Component name
        level: Optional logging level
        log_file: Optional log file
        
    Returns:
        Configured TranslationLogger instance
    """
    return _logging_config.create_component_logger(component_name, level, log_file)


def shutdown_logging() -> None:
    """Shutdown logging (convenience function)."""
    _logging_config.shutdown_logging()
