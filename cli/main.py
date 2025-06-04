#!/usr/bin/env python3
"""
AI Prototyping Tool - Command Line Interface

A powerful CLI for rapid AI application prototyping with LM Studio integration.
"""

import sys
import os
import json
import webbrowser
from pathlib import Path
from typing import List, Optional, Dict, Any

import click
from click import Context

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestrator import (
    OrchestrationEngine,
    OrchestrationConfig,
    CompletionMode,
    quick_generate,
)
from prompt_schema import DeliverableType
from lmstudio_client import LMStudioClient, LMStudioError
from markdown_renderer import (
    MarkdownRenderer,
    RenderConfig,
    OutputFormat,
    OutputTarget,
    render_to_file,
    render_to_stdout,
)


# Exit codes
EXIT_SUCCESS = 0
EXIT_GENERAL_ERROR = 1
EXIT_CONFIG_ERROR = 2
EXIT_CONNECTION_ERROR = 3
EXIT_VALIDATION_ERROR = 4
EXIT_FILE_ERROR = 5
EXIT_MODEL_ERROR = 6


# Global configuration
pass_config = click.make_pass_decorator(dict, ensure=True)


class CLIError(Exception):
    """Custom exception for CLI errors."""

    def __init__(self, message: str, exit_code: int = EXIT_GENERAL_ERROR):
        super().__init__(message)
        self.exit_code = exit_code


def setup_logging(verbose: int) -> None:
    """Setup logging based on verbosity level."""
    import logging

    if verbose == 0:
        level = logging.WARNING
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def validate_file_exists(file_path: str) -> Path:
    """Validate that a file exists and return Path object."""
    path = Path(file_path)
    if not path.exists():
        raise CLIError(f"File not found: {file_path}", EXIT_FILE_ERROR)
    if not path.is_file():
        raise CLIError(f"Path is not a file: {file_path}", EXIT_FILE_ERROR)
    return path


def validate_output_dir(output_path: str) -> Path:
    """Validate output directory and create if necessary."""
    path = Path(output_path)

    if path.exists() and not path.is_dir():
        raise CLIError(
            f"Output path exists but is not a directory: {output_path}", EXIT_FILE_ERROR
        )

    # Create directory if it doesn't exist
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise CLIError(f"Failed to create output directory: {e}", EXIT_FILE_ERROR)

    return path


def parse_deliverable_types(deliverable_types: List[str]) -> List[DeliverableType]:
    """Parse and validate deliverable type strings."""
    parsed_types = []
    available_types = {dt.value: dt for dt in DeliverableType}

    for type_str in deliverable_types:
        if type_str not in available_types:
            available = ", ".join(available_types.keys())
            raise CLIError(
                f"Unknown deliverable type: {type_str}\n"
                f"Available types: {available}",
                EXIT_VALIDATION_ERROR,
            )
        parsed_types.append(available_types[type_str])

    return parsed_types


def test_lm_studio_connection(base_url: str, api_key: Optional[str] = None) -> bool:
    """Test connection to LM Studio."""
    try:
        client = LMStudioClient(base_url=base_url, api_key=api_key)
        health = client.health_check()
        return health.get("status") == "healthy"
    except Exception:
        return False


def get_available_models(base_url: str, api_key: Optional[str] = None) -> List[str]:
    """Get list of available models from LM Studio."""
    try:
        client = LMStudioClient(base_url=base_url, api_key=api_key)
        models = client.list_models()
        return [model.id for model in models]
    except Exception:
        return []


def format_output(content: str, format_type: str, show_html: bool = False) -> str:
    """Format output content based on specified format."""
    if format_type.lower() == "json":
        # If content is already JSON, pretty print it
        try:
            data = json.loads(content)
            return json.dumps(data, indent=2)
        except json.JSONDecodeError:
            # If not JSON, wrap it
            return json.dumps({"content": content}, indent=2)

    if show_html and format_type.lower() == "markdown":
        # Convert markdown to HTML preview
        try:
            import markdown

            html = markdown.markdown(content)
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AI Prototyping Tool - Generated Content</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
    </style>
</head>
<body>
{html}
</body>
</html>"""
        except ImportError:
            click.echo(
                "Warning: markdown package not installed, showing raw markdown",
                err=True,
            )

    return content


def save_output(content: str, output_path: Path, filename: str = None) -> Path:
    """Save content to output file."""
    if filename is None:
        filename = "generated_content.md"

    output_file = output_path / filename

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        return output_file
    except OSError as e:
        raise CLIError(f"Failed to write output file: {e}", EXIT_FILE_ERROR)


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version information")
@click.option(
    "-v", "--verbose", count=True, help="Increase verbosity (use multiple times)"
)
@click.option("--config-file", type=click.Path(), help="Path to configuration file")
@click.pass_context
def cli(ctx: Context, version: bool, verbose: int, config_file: Optional[str]):
    """AI Prototyping Tool - Generate professional documentation with AI.

    This tool uses LM Studio to generate various types of business and technical
    documentation from simple text prompts.
    """
    setup_logging(verbose)

    if version:
        click.echo("AI Prototyping Tool v0.1.0")
        ctx.exit()

    # Load configuration
    config = {}
    if config_file:
        try:
            with open(config_file) as f:
                config = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise CLIError(f"Failed to load config file: {e}", EXIT_CONFIG_ERROR)

    ctx.ensure_object(dict)
    ctx.obj.update(config)
    ctx.obj["verbose"] = verbose

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.option("--prompt", "-p", help="Text prompt for generation")
@click.option(
    "--prompt-file",
    "-f",
    type=click.Path(exists=True),
    help="File containing the prompt text",
)
@click.option(
    "--deliverable-types",
    "-t",
    multiple=True,
    default=["problem_statement"],
    help="Types of deliverables to generate (can be used multiple times)",
)
@click.option("--model", "-m", help="LM Studio model to use")
@click.option(
    "--lm-studio-url", default="http://localhost:1234/v1", help="LM Studio base URL"
)
@click.option("--api-key", help="API key for LM Studio (if required)")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="./output",
    help="Output directory for generated files",
)
@click.option(
    "--output-format",
    type=click.Choice(["markdown", "json"]),
    default="markdown",
    help="Output format",
)
@click.option(
    "--show-html", is_flag=True, help="Generate HTML preview of markdown content"
)
@click.option("--raw", is_flag=True, help="Output raw content without formatting")
@click.option(
    "--merge/--no-merge",
    default=True,
    help="Merge multiple deliverables into single document",
)
@click.option(
    "--max-tokens", type=int, default=2048, help="Maximum tokens for generation"
)
@click.option(
    "--temperature",
    type=float,
    default=0.7,
    help="Temperature for generation (0.0-1.0)",
)
@click.option("--top-p", type=float, default=0.9, help="Top-p for generation (0.0-1.0)")
@click.option(
    "--completion-mode",
    type=click.Choice(["sequential", "batch", "streaming"]),
    default="sequential",
    help="Completion mode",
)
@click.option(
    "--save-config", type=click.Path(), help="Save current configuration to file"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be generated without actually generating",
)
@pass_config
def generate(
    config,
    prompt,
    prompt_file,
    deliverable_types,
    model,
    lm_studio_url,
    api_key,
    output,
    output_format,
    show_html,
    raw,
    merge,
    max_tokens,
    temperature,
    top_p,
    completion_mode,
    save_config,
    dry_run,
):
    """Generate AI documentation from prompts.

    Examples:

      # Generate from text prompt
      ai-proto generate -p "Create a customer management system"

      # Generate from file
      ai-proto generate -f requirements.txt

      # Generate specific deliverable types
      ai-proto generate -p "E-commerce platform" -t personas -t use_cases

      # Use specific model and output settings
      ai-proto generate -p "Mobile app" -m "llama-7b" -o ./docs --show-html
    """
    try:
        # Validate inputs
        if not prompt and not prompt_file:
            raise CLIError(
                "Either --prompt or --prompt-file must be provided",
                EXIT_VALIDATION_ERROR,
            )

        if prompt and prompt_file:
            raise CLIError(
                "Cannot specify both --prompt and --prompt-file", EXIT_VALIDATION_ERROR
            )

        # Read prompt from file if specified
        if prompt_file:
            prompt_path = validate_file_exists(prompt_file)
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    prompt = f.read().strip()
            except OSError as e:
                raise CLIError(f"Failed to read prompt file: {e}", EXIT_FILE_ERROR)

        if not prompt.strip():
            raise CLIError("Prompt cannot be empty", EXIT_VALIDATION_ERROR)

        # Parse deliverable types
        parsed_deliverable_types = parse_deliverable_types(deliverable_types)

        # Validate output directory
        output_path = validate_output_dir(output)

        # Test LM Studio connection
        if not dry_run:
            click.echo(f"Testing connection to LM Studio at {lm_studio_url}...")
            if not test_lm_studio_connection(lm_studio_url, api_key):
                raise CLIError(
                    f"Cannot connect to LM Studio at {lm_studio_url}. "
                    "Please ensure LM Studio is running and accessible.",
                    EXIT_CONNECTION_ERROR,
                )
            click.echo("✓ Connected to LM Studio")

        # Get available models and validate selection
        if not dry_run:
            available_models = get_available_models(lm_studio_url, api_key)
            if not available_models:
                raise CLIError(
                    "No models available in LM Studio. Please load a model first.",
                    EXIT_MODEL_ERROR,
                )

            if model and model not in available_models:
                available_str = ", ".join(available_models)
                raise CLIError(
                    f"Model '{model}' not found. Available models: {available_str}",
                    EXIT_MODEL_ERROR,
                )

            if not model:
                model = available_models[0]
                click.echo(f"Using model: {model}")

        # Create orchestration config
        orchestration_config = OrchestrationConfig(
            lm_studio_base_url=lm_studio_url,
            lm_studio_api_key=api_key,
            model_name=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            completion_mode=CompletionMode(completion_mode),
            merge_into_single_document=merge,
            output_format=output_format,
            enable_logging=config.get("verbose", 0) > 0,
        )

        # Save configuration if requested
        if save_config:
            config_data = {
                "lm_studio_url": lm_studio_url,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "completion_mode": completion_mode,
                "output_format": output_format,
                "merge": merge,
            }
            try:
                with open(save_config, "w") as f:
                    json.dump(config_data, f, indent=2)
                click.echo(f"Configuration saved to {save_config}")
            except OSError as e:
                click.echo(f"Warning: Failed to save config: {e}", err=True)

        # Show dry run information
        if dry_run:
            click.echo("\n=== DRY RUN - No generation will occur ===")
            click.echo(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            click.echo(
                f"Deliverable types: {[dt.value for dt in parsed_deliverable_types]}"
            )
            click.echo(f"Model: {model or 'first available'}")
            click.echo(f"Output directory: {output_path}")
            click.echo(f"Output format: {output_format}")
            click.echo(f"Merge documents: {merge}")
            return

        # Generate content
        click.echo(f"\nGenerating {len(parsed_deliverable_types)} deliverable(s)...")

        with click.progressbar(
            length=len(parsed_deliverable_types), label="Generating content"
        ) as bar:

            def progress_callback():
                bar.update(1)

            # Use the orchestration engine
            result = quick_generate(
                user_input=prompt,
                deliverable_types=parsed_deliverable_types,
                model_name=model,
                lm_studio_base_url=lm_studio_url,
                lm_studio_api_key=api_key,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                completion_mode=CompletionMode(completion_mode),
                merge_into_single_document=merge,
            )

            # Update progress bar to completion
            bar.update(len(parsed_deliverable_types) - bar.pos)

        # Check for errors
        if result.error_count > 0:
            click.echo(
                f"\nWarning: {result.error_count} deliverable(s) failed to generate:",
                err=True,
            )
            for dr in result.deliverable_results:
                if not dr.success:
                    click.echo(
                        f"  - {dr.deliverable_type.value}: {dr.error_message}", err=True
                    )

        if result.success_count == 0:
            raise CLIError("All deliverables failed to generate", EXIT_GENERAL_ERROR)

        # Process and save output
        if merge and result.merged_document:
            content = result.merged_document
            filename = f"merged_deliverables.{output_format}"
        else:
            # Save individual deliverables
            for dr in result.deliverable_results:
                if dr.success:
                    individual_content = format_output(
                        dr.content, output_format, show_html
                    )
                    individual_filename = f"{dr.deliverable_type.value}.{output_format}"
                    save_output(individual_content, output_path, individual_filename)

            # Use first successful deliverable for main output
            successful_results = [dr for dr in result.deliverable_results if dr.success]
            content = successful_results[0].content if successful_results else ""
            filename = f"generated_content.{output_format}"

        # Format output
        if not raw:
            content = format_output(content, output_format, show_html)

        # Save main output
        if content:
            output_file = save_output(content, output_path, filename)
            click.echo(f"\n✓ Generated content saved to: {output_file}")

            # Open HTML preview if requested
            if show_html and output_format == "markdown":
                html_file = output_path / f"{output_file.stem}.html"
                html_content = format_output(content, "markdown", True)
                save_output(html_content, output_path, html_file.name)
                click.echo(f"✓ HTML preview saved to: {html_file}")

                if click.confirm("Open HTML preview in browser?"):
                    webbrowser.open(f"file://{html_file.absolute()}")

        # Show summary
        click.echo(f"\n=== Generation Summary ===")
        click.echo(
            f"Successful: {result.success_count}/{len(parsed_deliverable_types)}"
        )
        click.echo(f"Total tokens used: {result.total_tokens_used}")
        click.echo(f"Total time: {result.total_execution_time:.2f}s")

        if result.error_count > 0:
            sys.exit(EXIT_GENERAL_ERROR)

    except CLIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user", err=True)
        sys.exit(EXIT_GENERAL_ERROR)
    except Exception as e:
        if config.get("verbose", 0) > 0:
            import traceback

            traceback.print_exc()
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(EXIT_GENERAL_ERROR)


@cli.command()
@click.option(
    "--lm-studio-url", default="http://localhost:1234/v1", help="LM Studio base URL"
)
@click.option("--api-key", help="API key for LM Studio (if required)")
def models(lm_studio_url, api_key):
    """List available models in LM Studio."""
    try:
        click.echo(f"Connecting to LM Studio at {lm_studio_url}...")

        if not test_lm_studio_connection(lm_studio_url, api_key):
            raise CLIError(
                f"Cannot connect to LM Studio at {lm_studio_url}", EXIT_CONNECTION_ERROR
            )

        available_models = get_available_models(lm_studio_url, api_key)

        if not available_models:
            click.echo("No models are currently loaded in LM Studio.")
            click.echo("Please load a model in LM Studio before proceeding.")
            return

        click.echo(f"\nAvailable models ({len(available_models)}):")
        for i, model in enumerate(available_models, 1):
            click.echo(f"  {i}. {model}")

    except CLIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(e.exit_code)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(EXIT_GENERAL_ERROR)


@cli.command()
def deliverables():
    """List available deliverable types."""
    click.echo("Available deliverable types:\n")

    for dt in DeliverableType:
        # Convert enum value to human readable
        display_name = dt.value.replace("_", " ").title()
        click.echo(f"  {dt.value:<35} - {display_name}")

    click.echo("\nUsage example:")
    click.echo("  ai-proto generate -p 'My project' -t problem_statement -t personas")


@cli.command()
@click.option(
    "--lm-studio-url", default="http://localhost:1234/v1", help="LM Studio base URL"
)
@click.option("--api-key", help="API key for LM Studio (if required)")
def health(lm_studio_url, api_key):
    """Check LM Studio connection and health."""
    try:
        click.echo(f"Testing connection to LM Studio at {lm_studio_url}...")

        client = LMStudioClient(base_url=lm_studio_url, api_key=api_key)

        # Test connection
        health_status = client.health_check()

        if health_status.get("status") == "healthy":
            click.echo("✓ LM Studio is healthy and accessible")
        else:
            click.echo(f"⚠ LM Studio status: {health_status}")

        # Get models
        models = client.list_models()
        click.echo(f"✓ Found {len(models)} available model(s)")

        # Show additional info if available
        if hasattr(client, "get_server_info"):
            try:
                info = client.get_server_info()
                if info:
                    click.echo(f"Server version: {info.get('version', 'unknown')}")
            except:
                pass

    except LMStudioError as e:
        click.echo(f"LM Studio error: {e}", err=True)
        sys.exit(EXIT_CONNECTION_ERROR)
    except Exception as e:
        click.echo(f"Connection failed: {e}", err=True)
        sys.exit(EXIT_CONNECTION_ERROR)


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user", err=True)
        sys.exit(EXIT_GENERAL_ERROR)


if __name__ == "__main__":
    main()
