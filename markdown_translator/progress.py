"""
Progress reporting and logging system for the Markdown translator.

This module provides Rich-based progress display, detailed logging,
and user-friendly error reporting functionality.
"""

import logging
import sys
from typing import Optional, Any, Dict
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.progress import (
    Progress, 
    TaskID, 
    BarColumn, 
    TextColumn, 
    TimeRemainingColumn,
    TimeElapsedColumn,
    SpinnerColumn
)
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live

from .interfaces import IProgressReporter, ILogger
from .models import TranslationStats, TranslationProgress


class RichProgressReporter(IProgressReporter):
    """
    Rich-based progress reporter with beautiful console output.
    
    Provides real-time progress tracking with estimated completion times,
    current status, and visual progress bars.
    """
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the progress reporter.
        
        Args:
            console: Optional Rich console instance
        """
        self.console = console or Console()
        self.progress: Optional[Progress] = None
        self.task_id: Optional[TaskID] = None
        self.live: Optional[Live] = None
        self._start_time: Optional[datetime] = None
        
    def start_progress(self, total_items: int, description: str = "处理中") -> None:
        """
        Start progress tracking with Rich progress bar.
        
        Args:
            total_items: Total number of items to process
            description: Description of the operation
        """
        self._start_time = datetime.now()
        
        # 创建自定义进度条
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            expand=True
        )
        
        self.task_id = self.progress.add_task(description, total=total_items)
        self.progress.start()
        
    def update_progress(self, completed: int, message: str = "") -> None:
        """
        Update progress with current completion count.
        
        Args:
            completed: Number of completed items
            message: Optional status message
        """
        if self.progress and self.task_id is not None:
            # 更新描述以包含状态消息
            description = f"处理中"
            if message:
                description += f" - {message}"
            
            self.progress.update(
                self.task_id, 
                completed=completed,
                description=description
            )
    
    def finish_progress(self, success: bool = True, message: str = "") -> None:
        """
        Finish progress tracking and show final status.
        
        Args:
            success: Whether the operation completed successfully
            message: Final status message
        """
        if self.progress:
            if success:
                final_message = f"✅ 完成"
                if message:
                    final_message += f" - {message}"
            else:
                final_message = f"❌ 失败"
                if message:
                    final_message += f" - {message}"
            
            if self.task_id is not None:
                self.progress.update(self.task_id, description=final_message)
            
            self.progress.stop()
            
            # 显示完成时间
            if self._start_time:
                elapsed = datetime.now() - self._start_time
                self.console.print(f"总耗时: {elapsed.total_seconds():.2f} 秒")
    
    def display_statistics(self, stats: TranslationStats) -> None:
        """
        Display translation statistics in a formatted table.
        
        Args:
            stats: TranslationStats object with computed statistics
        """
        # 创建统计表格
        table = Table(title="翻译统计", show_header=True, header_style="bold magenta")
        table.add_column("指标", style="cyan", no_wrap=True)
        table.add_column("数值", style="green")
        
        # 添加统计数据
        table.add_row("总片段数", str(stats.total_chunks))
        table.add_row("成功翻译", str(stats.successful_translations))
        table.add_row("失败翻译", str(stats.failed_translations))
        table.add_row("成功率", f"{stats.success_rate:.1f}%")
        table.add_row("总行数", str(stats.total_lines))
        table.add_row("总耗时", f"{stats.total_processing_time:.2f} 秒")
        table.add_row("平均每片段", f"{stats.average_chunk_time:.2f} 秒")
        table.add_row("重试次数", str(stats.total_retries))
        table.add_row("API调用", str(stats.api_calls_made))
        
        self.console.print(table)
    
    def display_error_summary(self, errors: list) -> None:
        """
        Display error summary in a user-friendly format.
        
        Args:
            errors: List of error messages
        """
        if not errors:
            return
            
        error_panel = Panel(
            "\n".join(f"• {error}" for error in errors),
            title="❌ 错误摘要",
            title_align="left",
            border_style="red"
        )
        self.console.print(error_panel)


class TranslationLogger(ILogger):
    """
    Enhanced logger with Rich formatting and file output.
    
    Provides structured logging with different levels, file output,
    and beautiful console formatting using Rich.
    """
    
    def __init__(
        self, 
        name: str = "markdown_translator",
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        console: Optional[Console] = None
    ):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
            level: Logging level
            log_file: Optional file path for log output
            console: Optional Rich console instance
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.console = console or Console()
        
        # 清除现有的处理器
        self.logger.handlers.clear()
        
        # 添加Rich控制台处理器
        console_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=False,
            markup=True
        )
        console_handler.setLevel(level)
        
        # 设置控制台格式
        console_format = logging.Formatter(
            fmt="%(message)s",
            datefmt="[%X]"
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # 添加文件处理器（如果指定了日志文件）
        if log_file:
            self._setup_file_handler(log_file, level)
    
    def _setup_file_handler(self, log_file: str, level: int) -> None:
        """
        Setup file handler for logging to file.
        
        Args:
            log_file: Path to log file
            level: Logging level
        """
        try:
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            
            # 设置文件格式（更详细）
            file_format = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            self.console.print(f"[yellow]警告: 无法设置文件日志 {log_file}: {e}[/yellow]")
    
    def info(self, message: str, **kwargs) -> None:
        """Log an info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message."""
        self.logger.warning(f"[yellow]{message}[/yellow]", **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log an error message."""
        self.logger.error(f"[red]{message}[/red]", **kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message."""
        self.logger.debug(f"[dim]{message}[/dim]", **kwargs)
    
    def success(self, message: str, **kwargs) -> None:
        """Log a success message."""
        self.logger.info(f"[green]✅ {message}[/green]", **kwargs)
    
    def set_level(self, level: int) -> None:
        """
        Set the logging level.
        
        Args:
            level: New logging level
        """
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)


class UserFriendlyErrorReporter:
    """
    User-friendly error reporting with suggestions and solutions.
    
    Provides helpful error messages with context and suggested solutions
    for common issues.
    """
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the error reporter.
        
        Args:
            console: Optional Rich console instance
        """
        self.console = console or Console()
        
        # 错误类型到用户友好消息的映射
        self.error_messages = {
            'api_key_missing': {
                'title': '🔑 API密钥缺失',
                'message': 'OpenRouter API密钥未设置',
                'solution': '请设置环境变量 TRANSLATE_API_TOKEN'
            },
            'api_connection_failed': {
                'title': '🌐 API连接失败',
                'message': '无法连接到OpenRouter API',
                'solution': '请检查网络连接和API密钥是否正确'
            },
            'file_not_found': {
                'title': '📁 文件未找到',
                'message': '指定的输入文件不存在',
                'solution': '请检查文件路径是否正确'
            },
            'permission_denied': {
                'title': '🚫 权限不足',
                'message': '没有权限访问指定文件或目录',
                'solution': '请检查文件权限或使用管理员权限运行'
            },
            'disk_space_full': {
                'title': '💾 磁盘空间不足',
                'message': '磁盘空间不足，无法写入文件',
                'solution': '请清理磁盘空间或选择其他输出位置'
            },
            'rate_limit_exceeded': {
                'title': '⏱️ API限流',
                'message': 'API调用频率超过限制',
                'solution': '请降低并发度或稍后重试'
            }
        }
    
    def report_error(
        self, 
        error_type: str, 
        details: str = "", 
        exception: Optional[Exception] = None
    ) -> None:
        """
        Report an error with user-friendly formatting.
        
        Args:
            error_type: Type of error (key in error_messages)
            details: Additional error details
            exception: Optional exception object
        """
        error_info = self.error_messages.get(error_type, {
            'title': '❌ 未知错误',
            'message': '发生了未知错误',
            'solution': '请查看详细日志或联系支持'
        })
        
        # 构建错误消息
        content = f"[bold red]{error_info['message']}[/bold red]"
        
        if details:
            content += f"\n\n详细信息: {details}"
        
        if exception:
            content += f"\n\n技术详情: {str(exception)}"
        
        content += f"\n\n[bold green]建议解决方案:[/bold green]\n{error_info['solution']}"
        
        # 显示错误面板
        error_panel = Panel(
            content,
            title=error_info['title'],
            title_align="left",
            border_style="red",
            padding=(1, 2)
        )
        
        self.console.print(error_panel)
    
    def report_validation_errors(self, validation_errors: list) -> None:
        """
        Report validation errors in a structured format.
        
        Args:
            validation_errors: List of validation error messages
        """
        if not validation_errors:
            return
        
        content = "发现以下验证问题:\n\n"
        for i, error in enumerate(validation_errors, 1):
            content += f"{i}. {error}\n"
        
        content += "\n[bold yellow]这些问题可能影响翻译质量，建议检查输入文件。[/bold yellow]"
        
        panel = Panel(
            content,
            title="⚠️ 验证警告",
            title_align="left",
            border_style="yellow",
            padding=(1, 2)
        )
        
        self.console.print(panel)
