"""
Command line interface for the Markdown translator.

This module provides the CLI entry point and argument parsing for the tool.
"""

import os
import sys
import asyncio
import signal
import json
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from .config import ConfigManager
from .engine import create_translation_engine
from .logging_config import setup_logging
from .security import SecurityManager, InputValidator
from . import __version__


console = Console()


def validate_input_file(ctx, param, value):
    """Validate that the input file exists and is readable."""
    if value is None:
        return None
    
    # Use security manager for comprehensive validation
    security_manager = SecurityManager()
    validation_result = security_manager.validate_file_path(value)
    
    if not validation_result.is_valid:
        if validation_result.risk_level == 'critical':
            raise click.BadParameter(f"Security validation failed: {', '.join(validation_result.issues)}")
        elif validation_result.risk_level == 'high':
            raise click.BadParameter(f"Input file validation failed: {', '.join(validation_result.issues)}")
        else:
            # Medium/low risk - show warnings but allow
            for issue in validation_result.issues:
                console.print(f"[yellow]Warning: {issue}[/yellow]")
    
    input_path = Path(value)
    if not input_path.suffix.lower() in ['.md', '.markdown', '.txt']:
        console.print(f"[yellow]Warning: Input file '{value}' does not have a .md, .markdown, or .txt extension.[/yellow]")
    
    return str(input_path.resolve())


def validate_output_file(ctx, param, value):
    """Validate that the output file path is writable."""
    if value is None:
        return None
    
    # Use security manager for comprehensive validation
    security_manager = SecurityManager()
    validation_result = security_manager.validate_output_path(value)
    
    if not validation_result.is_valid:
        if validation_result.risk_level in ['critical', 'high']:
            raise click.BadParameter(f"Output path validation failed: {', '.join(validation_result.issues)}")
        else:
            # Medium/low risk - show warnings but allow
            for issue in validation_result.issues:
                console.print(f"[yellow]Warning: {issue}[/yellow]")
    
    # Check if output file already exists and warn user
    output_path = Path(value)
    if output_path.exists():
        console.print(f"[yellow]Warning: Output file '{value}' already exists and will be overwritten.[/yellow]")
    
    return str(output_path.resolve())


def validate_chunk_size(ctx, param, value):
    """Validate chunk size parameter."""
    if value is None:
        return None  # Let optimizer decide
    
    # Use input validator for security validation
    input_validator = InputValidator()
    validation_result = input_validator.validate_chunk_size(value)
    
    if not validation_result.is_valid:
        raise click.BadParameter(f"Chunk size validation failed: {', '.join(validation_result.issues)}")
    
    if value < 50:
        console.print(f"[yellow]Warning: Very small chunk size ({value}) may result in poor translation quality.[/yellow]")
    
    if value > 5000:
        console.print(f"[yellow]Warning: Large chunk size ({value}) may cause API timeouts or memory issues.[/yellow]")
    
    return value


def validate_concurrency(ctx, param, value):
    """Validate concurrency parameter."""
    if value is None:
        return None  # Let optimizer decide
    
    # Use input validator for security validation
    input_validator = InputValidator()
    validation_result = input_validator.validate_concurrency(value)
    
    if not validation_result.is_valid:
        raise click.BadParameter(f"Concurrency validation failed: {', '.join(validation_result.issues)}")
    
    if value < 1:
        console.print("[yellow]Warning: Concurrency level less than 1 will be set to 1.[/yellow]")
        return 1
    
    if value > 50:
        console.print(f"[yellow]Warning: High concurrency level ({value}) may cause rate limiting.[/yellow]")
    
    return value


@click.command()
@click.option('-i', '--input', 'input_file', required=True, callback=validate_input_file,
              help='Input Markdown file to translate')
@click.option('-o', '--output', 'output_file', required=True, callback=validate_output_file,
              help='Output file for translated content')
@click.option('-c', '--chunk-size', type=int, callback=validate_chunk_size,
              help='Chunk size for splitting (default: auto)')
@click.option('-n', '--concurrency', type=int, callback=validate_concurrency,
              help='Number of concurrent translation tasks (default: auto)')
@click.option('--config-file', type=click.Path(exists=False), 
              help='Path to YAML configuration file')
@click.option('--timeout', type=int, default=120,
              help='API timeout in seconds (default: 120)')
@click.option('--max-retries', type=int, default=5,
              help='Maximum number of retries for API calls (default: 5)')
@click.option('--retry-delay', type=int, default=5,
              help='Initial delay between retries in seconds (default: 5)')
@click.option('--max-delay', type=int, default=300,
              help='Maximum delay between retries in seconds (default: 300)')
@click.option('--checkpoint-interval', type=int, default=10,
              help='Save checkpoint every N chunks (default: 10)')
@click.option('--resume', is_flag=True,
              help='Resume from checkpoint if it exists')
@click.option('--verbose', is_flag=True,
              help='Enable verbose logging')
@click.option('--version', is_flag=True,
              help='Show version and exit')
def main(input_file: str, output_file: Optional[str], chunk_size: Optional[int], concurrency: Optional[int],
         config_file: Optional[str], timeout: int, max_retries: int, retry_delay: int,
         max_delay: int, checkpoint_interval: int, resume: bool, verbose: bool, version: bool):
    """
    Translate Markdown files to Chinese using AI.
    
    This tool splits large Markdown files into chunks, translates them concurrently
    using OpenRouter API, and merges the results while preserving formatting.
    
    Example usage:
    
        markdown-translator -i README.md -o README_zh.md
        
        markdown-translator -i docs.md --chunk-size 1000 --concurrency 10
        
        markdown-translator --config-file config.yaml --resume
    """
    
    # Handle version flag
    if version:
        console.print(f"Markdown Translator v{__version__}")
        return
    
    # Setup signal handlers for graceful shutdown
    shutdown_event = asyncio.Event()
    
    def signal_handler(signum, frame):
        console.print(f"\n[yellow]Received signal {signum}, initiating graceful shutdown...[/yellow]")
        shutdown_event.set()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Display banner
    console.print(Panel.fit(
        "[bold blue]Markdown Translator[/bold blue]\n"
        "AI-powered Markdown translation tool",
        border_style="blue"
    ))
    
    # Generate default output path if not provided
    if output_file is None:
        output_file = generate_default_output_path(input_file)
        console.print(f"[dim]Using default output path: {output_file}[/dim]")
    
    # Initialize configuration manager with optional config file
    try:
        config_manager = ConfigManager(config_file=config_file)
        
        # Validate API configuration
        if not config_manager.validate_api_config():
            console.print("[red]Error: Invalid API configuration. Please check your API token and settings.[/red]")
            console.print("\nRequired environment variables:")
            console.print("  TRANSLATE_API_TOKEN - Your OpenRouter API token")
            console.print("\nOptional environment variables:")
            console.print("  TRANSLATE_API - API base URL (default: https://openrouter.ai/api/v1)")
            console.print("  TRANSLATE_MODEL - Model to use (default: qwen/qwen-2.5-72b-instruct)")
            sys.exit(1)
            
        # Display configuration summary
        if verbose:
            console.print("\n[bold]Configuration:[/bold]")
            console.print(f"  Input file: {input_file}")
            console.print(f"  Output file: {output_file}")
            console.print(f"  Config file: {config_file if config_file else 'None (using defaults)'}")
            console.print(f"  Chunk size: {chunk_size if chunk_size is not None else 'auto (optimizer will decide)'}")
            console.print(f"  Concurrency: {concurrency if concurrency is not None else 'auto (optimizer will decide)'}")
            console.print(f"  Model: {config_manager.get_model_name()}")
            console.print(f"  API URL: {config_manager.get_api_base_url()}")
            console.print(f"  Timeout: {timeout}s")
            console.print(f"  Max retries: {max_retries}")
            console.print(f"  Retry delay: {retry_delay}s")
            console.print(f"  Max delay: {max_delay}s")
            console.print(f"  Checkpoint interval: {checkpoint_interval} chunks")
            console.print(f"  Resume: {resume}")
            console.print(f"  Verbose: {verbose}")
        
        # Handle resume mode
        if resume:
            # Look for checkpoint file based on output file
            checkpoint_path = Path(output_file).with_suffix('.chkpt.json')
            if checkpoint_path.exists():
                console.print(f"[blue]Resuming translation from checkpoint: {checkpoint_path}[/blue]")
                return asyncio.run(resume_translation(str(checkpoint_path), verbose))
            else:
                console.print(f"[yellow]Checkpoint file not found: {checkpoint_path}. Starting new translation.[/yellow]")
        
        # Run the translation
        return asyncio.run(run_translation(
            input_file=input_file,
            output_file=output_file,
            chunk_size=chunk_size,
            concurrency=concurrency,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            max_delay=max_delay,
            checkpoint_interval=checkpoint_interval,
            verbose=verbose,
            shutdown_event=shutdown_event,
            config_manager=config_manager
        ))


async def run_translation(input_file: str, output_file: str, chunk_size: int, 
                         concurrency: int, timeout: int, max_retries: int, 
                         retry_delay: int, max_delay: int, checkpoint_interval: int,
                         verbose: bool, shutdown_event: asyncio.Event, config_manager: ConfigManager):
    """
    Run the main translation process.
    
    Args:
        input_file: Path to input file
        output_file: Path to output file
        chunk_size: Chunk size for splitting
        concurrency: Concurrency level
        timeout: API timeout in seconds
        max_retries: Maximum number of retries for API calls
        retry_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        checkpoint_interval: Save checkpoint every N chunks
        verbose: Enable verbose logging
        shutdown_event: Event for graceful shutdown
        config_manager: Configuration manager instance
    """
    try:
        # Setup logging
        logger = setup_logging(verbose=verbose)
        
        # Create translation engine with default values for None parameters
        console.print("[blue]Initializing translation engine...[/blue]")
        engine = create_translation_engine(
            chunk_size=chunk_size if chunk_size is not None else 500,
            concurrency=concurrency if concurrency is not None else 5,
            verbose=verbose
        )
        
        # Progress callback
        def progress_callback(progress):
            if not shutdown_event.is_set():
                console.print(f"[dim]Progress: {progress.completion_percentage:.1f}% "
                            f"({progress.completed_chunks}/{progress.total_chunks})[/dim]")
        
        # Start translation
        console.print(f"[green]Starting translation of {Path(input_file).name}...[/green]")
        
        # Create task for translation
        translation_task = asyncio.create_task(
            engine.translate_file(
                input_path=input_file,
                output_path=output_file,
                chunk_size=chunk_size,
                concurrency=concurrency,
                progress_callback=progress_callback
            )
        )
        
        # Wait for either completion or shutdown signal
        done, pending = await asyncio.wait(
            [translation_task, asyncio.create_task(shutdown_event.wait())],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        if shutdown_event.is_set():
            # Graceful shutdown requested
            console.print("[yellow]Shutdown requested, cancelling translation...[/yellow]")
            translation_task.cancel()
            
            try:
                await translation_task
            except asyncio.CancelledError:
                console.print("[yellow]Translation cancelled successfully.[/yellow]")
            
            # Create checkpoint if possible
            progress = engine.get_translation_progress()
            if progress and progress.completed_chunks > 0:
                try:
                    checkpoint_path = engine.create_checkpoint(progress)
                    console.print(f"[blue]Checkpoint saved: {checkpoint_path}[/blue]")
                    console.print(f"[blue]Resume with: --resume {checkpoint_path}[/blue]")
                except Exception as e:
                    console.print(f"[yellow]Could not save checkpoint: {e}[/yellow]")
            
            sys.exit(130)
        
        # Translation completed
        stats = translation_task.result()
        
        # Display results
        console.print(f"\n[bold green]Translation completed successfully![/bold green]")
        console.print(f"[green]Output file: {output_file}[/green]")
        console.print(f"\n[bold]Statistics:[/bold]")
        console.print(f"  Total chunks: {stats.total_chunks}")
        console.print(f"  Successful: {stats.successful_translations}")
        console.print(f"  Failed: {stats.failed_translations}")
        console.print(f"  Success rate: {stats.success_rate:.1f}%")
        console.print(f"  Total time: {stats.total_processing_time:.2f}s")
        console.print(f"  Average per chunk: {stats.average_chunk_time:.2f}s")
        console.print(f"  Total lines: {stats.total_lines}")
        console.print(f"  API calls: {stats.api_calls_made}")
        console.print(f"  Retries: {stats.total_retries}")
        
        if stats.failed_translations > 0:
            console.print(f"\n[yellow]Warning: {stats.failed_translations} chunks failed to translate.[/yellow]")
            console.print("[yellow]Check the output file for any untranslated sections.[/yellow]")
            return 1
        
        return 0
        
    except Exception as e:
        console.print(f"\n[red]Translation failed: {e}[/red]")
        if verbose:
            import traceback
            console.print(f"[red]{traceback.format_exc()}[/red]")
        return 1


async def resume_translation(checkpoint_path: str, verbose: bool):
    """
    Resume translation from a checkpoint.
    
    Args:
        checkpoint_path: Path to checkpoint file
        verbose: Enable verbose logging
    """
    try:
        # Setup logging
        log_level = "DEBUG" if verbose else "INFO"
        logger = setup_logging(log_level)
        
        # Create translation engine
        console.print("[blue]Initializing translation engine...[/blue]")
        engine = create_translation_engine(verbose=verbose)
        
        # Resume translation
        console.print(f"[blue]Resuming translation from {checkpoint_path}...[/blue]")
        stats = await engine.resume_translation(checkpoint_path)
        
        # Display results
        console.print(f"\n[bold green]Translation resumed and completed successfully![/bold green]")
        console.print(f"[green]Output file: {stats.output_path}[/green]")
        console.print(f"\n[bold]Statistics:[/bold]")
        console.print(f"  Total chunks: {stats.total_chunks}")
        console.print(f"  Successful: {stats.successful_translations}")
        console.print(f"  Failed: {stats.failed_translations}")
        console.print(f"  Success rate: {stats.success_rate:.1f}%")
        console.print(f"  Total time: {stats.total_processing_time:.2f}s")
        console.print(f"  Average per chunk: {stats.average_chunk_time:.2f}s")
        console.print(f"  Total lines: {stats.total_lines}")
        console.print(f"  API calls: {stats.api_calls_made}")
        console.print(f"  Retries: {stats.total_retries}")
        
        if stats.failed_translations > 0:
            console.print(f"\n[yellow]Warning: {stats.failed_translations} chunks failed to translate.[/yellow]")
            console.print("[yellow]Check the output file for any untranslated sections.[/yellow]")
            return 1
        
        return 0
        
    except FileNotFoundError:
        console.print(f"[red]Checkpoint file not found: {checkpoint_path}[/red]")
        return 1
    except json.JSONDecodeError:
        console.print(f"[red]Invalid checkpoint file format: {checkpoint_path}[/red]")
        return 1
    except NotImplementedError:
        console.print("[yellow]Resume functionality is not yet implemented.[/yellow]")
        return 1
    except AttributeError as e:
        if "resume_translation" in str(e):
            console.print("[yellow]Resume functionality is not yet implemented.[/yellow]")
            return 1
        raise
    except Exception as e:
        console.print(f"\n[red]Resume failed: {e}[/red]")
        if verbose:
            import traceback
            console.print(f"[red]{traceback.format_exc()}[/red]")
        return 1


def cli_entry_point():
    """Entry point for the CLI when installed as a package."""
    try:
        result = main()
        if isinstance(result, int):
            sys.exit(result)
    except KeyboardInterrupt:
        console.print("\n[yellow]Translation interrupted by user.[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        if '--verbose' in sys.argv or '-v' in sys.argv:
            import traceback
            console.print(f"[red]{traceback.format_exc()}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    cli_entry_point()
