"""
Command line interface for the Markdown translator.

This module provides the CLI entry point and argument parsing for the tool.
"""

import os
import sys
import asyncio
import signal
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from .config import ConfigManager
from .engine import create_translation_engine
from .logging_config import setup_logging
from .security import SecurityManager, InputValidator


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
    
    if value > 20:
        console.print(f"[yellow]Warning: High concurrency ({value}) may cause API rate limiting.[/yellow]")
    
    return value


def generate_default_output_path(input_path: str) -> str:
    """Generate a default output path based on the input path."""
    input_path_obj = Path(input_path)
    stem = input_path_obj.stem
    suffix = input_path_obj.suffix
    parent = input_path_obj.parent
    
    # Add _zh suffix before the file extension
    default_output = parent / f"{stem}_zh{suffix}"
    return str(default_output)


@click.command()
@click.option(
    '--input', '-i',
    type=str,
    required=True,
    callback=validate_input_file,
    help='Path to the input Markdown file to translate.'
)
@click.option(
    '--output', '-o',
    type=str,
    callback=validate_output_file,
    help='Path to the output translated file. If not specified, will use input filename with _zh suffix.'
)
@click.option(
    '--chunk-size', '-c',
    type=int,
    default=None,
    callback=validate_chunk_size,
    help='Number of lines per chunk for translation. If not specified, optimizer will suggest optimal size.'
)
@click.option(
    '--concurrency', '-n',
    type=int,
    default=None,
    callback=validate_concurrency,
    help='Number of concurrent translation requests. If not specified, optimizer will suggest optimal concurrency.'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    default=False,
    help='Enable verbose logging output.'
)
@click.option(
    '--dry-run',
    is_flag=True,
    default=False,
    help='Show what would be done without actually translating.'
)
@click.option(
    '--resume',
    type=str,
    help='Resume translation from checkpoint file.'
)
@click.version_option(version='1.0.0', prog_name='markdown-translator')
def main(input: str, output: Optional[str], chunk_size: int, concurrency: int, 
         verbose: bool, dry_run: bool, resume: Optional[str]):
    """
    Translate Markdown files to Chinese using AI translation services.
    
    This tool splits large Markdown files into chunks, translates them concurrently
    using OpenRouter API, and merges the results while preserving formatting.
    
    Example usage:
    
        markdown-translator -i README.md -o README_zh.md
        
        markdown-translator -i docs.md --chunk-size 1000 --concurrency 10
        
        markdown-translator --resume checkpoint.json
    """
    
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
    
    # Handle resume mode
    if resume:
        console.print(f"[blue]Resuming translation from checkpoint: {resume}[/blue]")
        return asyncio.run(resume_translation(resume, verbose))
    
    # Generate default output path if not provided
    if output is None:
        output = generate_default_output_path(input)
        console.print(f"[dim]Using default output path: {output}[/dim]")
    
    # Validate configuration
    try:
        config_manager = ConfigManager()
        if not config_manager.validate_api_config():
            console.print("[red]Error: Invalid API configuration. Please check your environment variables.[/red]")
            console.print("\nRequired environment variables:")
            console.print("  TRANSLATE_API_TOKEN - Your OpenRouter API token")
            console.print("\nOptional environment variables:")
            console.print("  TRANSLATE_API - API base URL (default: https://openrouter.ai/api/v1)")
            console.print("  TRANSLATE_MODEL - Model to use (default: qwen/qwen-2.5-72b-instruct)")
            sys.exit(1)
    except ValueError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        sys.exit(1)
    
    # Display configuration summary
    if verbose or dry_run:
        console.print("\n[bold]Configuration:[/bold]")
        console.print(f"  Input file: {input}")
        console.print(f"  Output file: {output}")
        console.print(f"  Chunk size: {chunk_size if chunk_size is not None else 'auto (optimizer will decide)'}")
        console.print(f"  Concurrency: {concurrency if concurrency is not None else 'auto (optimizer will decide)'}")
        console.print(f"  Model: {config_manager.get_model_name()}")
        console.print(f"  API URL: {config_manager.get_api_base_url()}")
        console.print(f"  Verbose: {verbose}")
    
    if dry_run:
        console.print("\n[yellow]Dry run mode - no actual translation will be performed.[/yellow]")
        return
    
    # Run the translation
    return asyncio.run(run_translation(
        input_file=input,
        output_file=output,
        chunk_size=chunk_size,
        concurrency=concurrency,
        verbose=verbose,
        shutdown_event=shutdown_event
    ))


async def run_translation(input_file: str, output_file: str, chunk_size: int, 
                         concurrency: int, verbose: bool, shutdown_event: asyncio.Event):
    """
    Run the main translation process.
    
    Args:
        input_file: Path to input file
        output_file: Path to output file
        chunk_size: Chunk size for splitting
        concurrency: Concurrency level
        verbose: Enable verbose logging
        shutdown_event: Event for graceful shutdown
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
        logger = setup_logging(verbose=verbose)
        
        # Create translation engine
        console.print("[blue]Initializing translation engine...[/blue]")
        engine = create_translation_engine(verbose=verbose)
        
        # Resume translation
        console.print(f"[blue]Resuming translation from {checkpoint_path}...[/blue]")
        stats = await engine.resume_translation(checkpoint_path)
        
        # Display results (same as above)
        console.print(f"\n[bold green]Translation resumed and completed![/bold green]")
        # ... (same result display logic)
        
        return 0
        
    except NotImplementedError:
        console.print("[yellow]Resume functionality is not yet implemented.[/yellow]")
        return 1
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
