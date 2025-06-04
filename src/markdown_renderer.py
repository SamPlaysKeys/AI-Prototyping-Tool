"""
Markdown Renderer Module

This module provides comprehensive markdown rendering functionality for both CLI and web interfaces.
It supports output to files, stdout, HTML conversion, and configurable styling.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import markdown
    from markdown.extensions import codehilite, toc, tables, fenced_code

    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


class OutputFormat(Enum):
    """Supported output formats."""

    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    PLAIN_TEXT = "text"


class OutputTarget(Enum):
    """Output targets for rendering."""

    STDOUT = "stdout"
    FILE = "file"
    STRING = "string"


@dataclass
class RenderConfig:
    """Configuration for markdown rendering."""

    output_format: OutputFormat = OutputFormat.MARKDOWN
    output_target: OutputTarget = OutputTarget.FILE
    output_path: Optional[str] = None
    filename: Optional[str] = None
    css_theme: str = "default"
    custom_css: Optional[str] = None
    include_toc: bool = True
    highlight_code: bool = True
    add_metadata: bool = True
    download_enabled: bool = True
    title: Optional[str] = None
    author: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class MarkdownRenderer:
    """Main markdown renderer class with CLI and web support."""

    def __init__(self, config: Optional[RenderConfig] = None):
        """
        Initialize the markdown renderer.

        Args:
            config: Rendering configuration
        """
        self.config = config or RenderConfig()
        self.css_themes = self._load_css_themes()

    def _load_css_themes(self) -> Dict[str, str]:
        """Load predefined CSS themes."""
        return {
            "default": self._get_default_css(),
            "github": self._get_github_css(),
            "minimal": self._get_minimal_css(),
            "dark": self._get_dark_css(),
            "professional": self._get_professional_css(),
        }

    def render_markdown(
        self, content: str, config: Optional[RenderConfig] = None
    ) -> str:
        """
        Render markdown content according to configuration.

        Args:
            content: Raw markdown content to render
            config: Optional configuration override

        Returns:
            Rendered content as string
        """
        render_config = config or self.config

        # Add metadata if requested
        if render_config.add_metadata:
            content = self._add_metadata(content, render_config)

        # Process based on output format
        if render_config.output_format == OutputFormat.MARKDOWN:
            return self._render_markdown_output(content, render_config)
        elif render_config.output_format == OutputFormat.HTML:
            return self._render_html_output(content, render_config)
        elif render_config.output_format == OutputFormat.JSON:
            return self._render_json_output(content, render_config)
        elif render_config.output_format == OutputFormat.PLAIN_TEXT:
            return self._render_plain_text_output(content, render_config)
        else:
            raise ValueError(
                f"Unsupported output format: {render_config.output_format}"
            )

    def render_to_file(
        self, content: str, config: Optional[RenderConfig] = None
    ) -> str:
        """
        Render markdown content and save to file.

        Args:
            content: Raw markdown content
            config: Optional configuration override

        Returns:
            Path to saved file
        """
        render_config = config or self.config
        render_config.output_target = OutputTarget.FILE

        rendered_content = self.render_markdown(content, render_config)

        # Determine output path and filename
        output_path = self._get_output_path(render_config)
        filename = self._get_filename(render_config)

        file_path = Path(output_path) / filename

        # Ensure output directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(rendered_content)

        return str(file_path)

    def render_to_stdout(
        self, content: str, config: Optional[RenderConfig] = None
    ) -> None:
        """
        Render markdown content to stdout.

        Args:
            content: Raw markdown content
            config: Optional configuration override
        """
        render_config = config or self.config
        render_config.output_target = OutputTarget.STDOUT

        rendered_content = self.render_markdown(content, render_config)
        print(rendered_content)

    def render_for_web(
        self, content: str, config: Optional[RenderConfig] = None
    ) -> Dict[str, Any]:
        """
        Render markdown content for web display with download options.

        Args:
            content: Raw markdown content
            config: Optional configuration override

        Returns:
            Dictionary with rendered content and download options
        """
        render_config = config or self.config

        # Generate HTML version
        html_config = RenderConfig(
            output_format=OutputFormat.HTML,
            output_target=OutputTarget.STRING,
            css_theme=render_config.css_theme,
            custom_css=render_config.custom_css,
            include_toc=render_config.include_toc,
            highlight_code=render_config.highlight_code,
            add_metadata=render_config.add_metadata,
            title=render_config.title,
            author=render_config.author,
        )

        html_content = self.render_markdown(content, html_config)

        # Generate markdown version
        md_config = RenderConfig(
            output_format=OutputFormat.MARKDOWN,
            output_target=OutputTarget.STRING,
            add_metadata=render_config.add_metadata,
            title=render_config.title,
            author=render_config.author,
        )

        md_content = self.render_markdown(content, md_config)

        result = {
            "html_content": html_content,
            "markdown_content": md_content,
            "css_theme": render_config.css_theme,
            "download_options": {
                "markdown_enabled": render_config.download_enabled,
                "html_enabled": render_config.download_enabled,
                "markdown_filename": self._get_download_filename("md", render_config),
                "html_filename": self._get_download_filename("html", render_config),
            },
        }

        return result

    def _render_markdown_output(self, content: str, config: RenderConfig) -> str:
        """Render as markdown with potential enhancements."""
        # For markdown output, we mainly just clean up and format
        lines = content.split("\n")
        cleaned_lines = []

        for line in lines:
            # Clean up any extra whitespace
            cleaned_line = line.rstrip()
            cleaned_lines.append(cleaned_line)

        return "\n".join(cleaned_lines)

    def _render_html_output(self, content: str, config: RenderConfig) -> str:
        """Render markdown as HTML."""
        if not MARKDOWN_AVAILABLE:
            # Fallback to basic HTML conversion if markdown library not available
            return self._basic_markdown_to_html(content, config)

        # Configure markdown extensions
        extensions = ["markdown.extensions.extra"]

        if config.highlight_code:
            extensions.append("markdown.extensions.codehilite")

        if config.include_toc:
            extensions.append("markdown.extensions.toc")

        extensions.extend(
            [
                "markdown.extensions.tables",
                "markdown.extensions.fenced_code",
                "markdown.extensions.def_list",
            ]
        )

        # Convert markdown to HTML
        md = markdown.Markdown(extensions=extensions)
        html_body = md.convert(content)

        # Get CSS
        css = self._get_css(config)

        # Create complete HTML document
        title = config.title or "Generated Document"

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css}
    </style>
</head>
<body>
    <div class="container">
{html_body}
    </div>
</body>
</html>
"""

        return html_template

    def _render_json_output(self, content: str, config: RenderConfig) -> str:
        """Render as JSON."""
        data = {
            "content": content,
            "format": "markdown",
            "config": config.to_dict(),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "title": config.title,
                "author": config.author,
            },
        }

        return json.dumps(data, indent=2)

    def _render_plain_text_output(self, content: str, config: RenderConfig) -> str:
        """Render as plain text (strip markdown formatting)."""
        # Basic markdown to text conversion
        lines = content.split("\n")
        text_lines = []

        for line in lines:
            # Remove markdown formatting
            line = line.strip()

            # Remove headers
            if line.startswith("#"):
                line = line.lstrip("#").strip()

            # Remove bold/italic
            line = line.replace("**", "").replace("*", "")
            line = line.replace("__", "").replace("_", "")

            # Remove code blocks
            if line.startswith("```"):
                continue

            # Remove inline code
            while "`" in line:
                start = line.find("`")
                end = line.find("`", start + 1)
                if start != -1 and end != -1:
                    line = line[:start] + line[start + 1 : end] + line[end + 1 :]
                else:
                    break

            text_lines.append(line)

        return "\n".join(text_lines)

    def _basic_markdown_to_html(self, content: str, config: RenderConfig) -> str:
        """Basic markdown to HTML conversion without external library."""
        lines = content.split("\n")
        html_lines = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith("```"):
                if in_code_block:
                    html_lines.append("</pre>")
                    in_code_block = False
                else:
                    html_lines.append("<pre><code>")
                    in_code_block = True
                continue

            if in_code_block:
                html_lines.append(line)
                continue

            # Headers
            if line.startswith("# "):
                html_lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith("## "):
                html_lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith("### "):
                html_lines.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith("#### "):
                html_lines.append(f"<h4>{line[5:]}</h4>")
            elif line.strip() == "":
                html_lines.append("<br>")
            else:
                # Basic formatting
                formatted_line = line
                formatted_line = formatted_line.replace("**", "<strong>").replace(
                    "**", "</strong>"
                )
                formatted_line = formatted_line.replace("*", "<em>").replace(
                    "*", "</em>"
                )
                html_lines.append(f"<p>{formatted_line}</p>")

        if in_code_block:
            html_lines.append("</code></pre>")

        html_body = "\n".join(html_lines)
        css = self._get_css(config)
        title = config.title or "Generated Document"

        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>{css}</style>
</head>
<body>
    <div class="container">
        {html_body}
    </div>
</body>
</html>
"""

    def _add_metadata(self, content: str, config: RenderConfig) -> str:
        """Add metadata header to content."""
        metadata_lines = []

        if config.title:
            metadata_lines.append(f"# {config.title}")
            metadata_lines.append("")

        # Add document info
        metadata_lines.extend(
            [
                "---",
                f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ]
        )

        if config.author:
            metadata_lines.append(f"**Author:** {config.author}")

        metadata_lines.extend([f"**Format:** {config.output_format.value}", "---", ""])

        return "\n".join(metadata_lines) + "\n" + content

    def _get_css(self, config: RenderConfig) -> str:
        """Get CSS for HTML output."""
        if config.custom_css:
            return config.custom_css

        theme_css = self.css_themes.get(config.css_theme, self.css_themes["default"])
        return theme_css

    def _get_output_path(self, config: RenderConfig) -> str:
        """Get output directory path."""
        if config.output_path:
            return config.output_path
        return "./output"

    def _get_filename(self, config: RenderConfig) -> str:
        """Get output filename."""
        if config.filename:
            return config.filename

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = self._get_file_extension(config.output_format)

        if config.title:
            # Clean title for filename
            clean_title = "".join(
                c for c in config.title if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            clean_title = clean_title.replace(" ", "_").lower()
            return f"{clean_title}_{timestamp}.{extension}"

        return f"generated_content_{timestamp}.{extension}"

    def _get_download_filename(self, extension: str, config: RenderConfig) -> str:
        """Get filename for downloads."""
        if config.title:
            clean_title = "".join(
                c for c in config.title if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            clean_title = clean_title.replace(" ", "_").lower()
            return f"{clean_title}.{extension}"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"generated_content_{timestamp}.{extension}"

    def _get_file_extension(self, output_format: OutputFormat) -> str:
        """Get file extension for output format."""
        extensions = {
            OutputFormat.MARKDOWN: "md",
            OutputFormat.HTML: "html",
            OutputFormat.JSON: "json",
            OutputFormat.PLAIN_TEXT: "txt",
        }
        return extensions[output_format]

    def _get_default_css(self) -> str:
        """Default CSS theme."""
        return """
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 2em;
            margin-bottom: 1em;
        }
        h1 { border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }
        code {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 3px;
            padding: 2px 4px;
            font-size: 87.5%;
        }
        pre {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
        }
        pre code {
            background: none;
            border: none;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #3498db;
            margin: 0;
            padding-left: 20px;
            color: #666;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        """

    def _get_github_css(self) -> str:
        """GitHub-style CSS theme."""
        return """
        .container {
            max-width: 980px;
            margin: 0 auto;
            padding: 45px;
            font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif;
            font-size: 16px;
            line-height: 1.5;
            color: #24292e;
        }
        h1, h2, h3, h4, h5, h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }
        h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 10px; }
        h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 8px; }
        h3 { font-size: 1.25em; }
        code {
            padding: 2px 4px;
            margin: 0;
            font-size: 85%;
            background-color: rgba(27,31,35,0.05);
            border-radius: 3px;
        }
        pre {
            padding: 16px;
            overflow: auto;
            font-size: 85%;
            line-height: 1.45;
            background-color: #f6f8fa;
            border-radius: 3px;
        }
        blockquote {
            padding: 0 1em;
            color: #6a737d;
            border-left: 4px solid #dfe2e5;
            margin: 0;
        }
        table {
            border-spacing: 0;
            border-collapse: collapse;
            margin-top: 0;
            margin-bottom: 16px;
        }
        th, td {
            padding: 6px 13px;
            border: 1px solid #dfe2e5;
        }
        th {
            font-weight: 600;
            background-color: #f6f8fa;
        }
        """

    def _get_minimal_css(self) -> str:
        """Minimal CSS theme."""
        return """
        .container {
            max-width: 680px;
            margin: 0 auto;
            padding: 40px 20px;
            font-family: Georgia, serif;
            font-size: 18px;
            line-height: 1.8;
            color: #333;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            margin-top: 2em;
            margin-bottom: 0.5em;
        }
        code, pre {
            font-family: 'SF Mono', Monaco, monospace;
            background-color: #f5f5f5;
        }
        code {
            padding: 2px 4px;
            border-radius: 2px;
        }
        pre {
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
        }
        """

    def _get_dark_css(self) -> str:
        """Dark theme CSS."""
        return """
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #e1e1e1;
            background-color: #1a1a1a;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff;
            margin-top: 2em;
            margin-bottom: 1em;
        }
        h1 { border-bottom: 2px solid #4a9eff; padding-bottom: 10px; }
        h2 { border-bottom: 1px solid #666; padding-bottom: 5px; }
        code {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 3px;
            padding: 2px 4px;
            color: #f8f8f2;
        }
        pre {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
        }
        pre code {
            background: none;
            border: none;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #4a9eff;
            margin: 0;
            padding-left: 20px;
            color: #aaa;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #444;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #2d2d2d;
            font-weight: bold;
        }
        a {
            color: #4a9eff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        """

    def _get_professional_css(self) -> str:
        """Professional CSS theme."""
        return """
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px;
            font-family: 'Times New Roman', serif;
            font-size: 16px;
            line-height: 1.7;
            color: #2c3e50;
            background-color: #ffffff;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Arial', sans-serif;
            color: #1a252f;
            margin-top: 2.5em;
            margin-bottom: 1em;
            font-weight: 600;
        }
        h1 {
            font-size: 2.2em;
            border-bottom: 3px solid #34495e;
            padding-bottom: 15px;
            text-align: center;
        }
        h2 {
            font-size: 1.6em;
            border-bottom: 2px solid #7f8c8d;
            padding-bottom: 8px;
        }
        h3 {
            font-size: 1.3em;
            color: #34495e;
        }
        code {
            background-color: #ecf0f1;
            border: 1px solid #bdc3c7;
            border-radius: 2px;
            padding: 3px 6px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        pre {
            background-color: #ecf0f1;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            padding: 20px;
            overflow-x: auto;
            margin: 20px 0;
        }
        pre code {
            background: none;
            border: none;
            padding: 0;
        }
        blockquote {
            border-left: 5px solid #3498db;
            margin: 20px 0;
            padding-left: 25px;
            font-style: italic;
            color: #5d6d7e;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 25px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        th, td {
            border: 1px solid #d5d8dc;
            padding: 15px;
            text-align: left;
        }
        th {
            background-color: #34495e;
            color: white;
            font-weight: bold;
            font-family: 'Arial', sans-serif;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        a {
            color: #2980b9;
            text-decoration: none;
            border-bottom: 1px dotted #2980b9;
        }
        a:hover {
            color: #1abc9c;
            border-bottom: 1px solid #1abc9c;
        }
        """


# Convenience functions for easy usage


def render_to_file(
    content: str,
    output_path: str = "./output",
    filename: Optional[str] = None,
    output_format: OutputFormat = OutputFormat.MARKDOWN,
    css_theme: str = "default",
    title: Optional[str] = None,
) -> str:
    """
    Convenience function to render content to file.

    Args:
        content: Markdown content to render
        output_path: Directory to save file
        filename: Optional filename
        output_format: Output format
        css_theme: CSS theme for HTML output
        title: Document title

    Returns:
        Path to saved file
    """
    config = RenderConfig(
        output_format=output_format,
        output_target=OutputTarget.FILE,
        output_path=output_path,
        filename=filename,
        css_theme=css_theme,
        title=title,
    )

    renderer = MarkdownRenderer(config)
    return renderer.render_to_file(content)


def render_to_stdout(
    content: str,
    output_format: OutputFormat = OutputFormat.MARKDOWN,
    title: Optional[str] = None,
) -> None:
    """
    Convenience function to render content to stdout.

    Args:
        content: Markdown content to render
        output_format: Output format
        title: Document title
    """
    config = RenderConfig(
        output_format=output_format, output_target=OutputTarget.STDOUT, title=title
    )

    renderer = MarkdownRenderer(config)
    renderer.render_to_stdout(content)


def render_for_web(
    content: str,
    css_theme: str = "default",
    title: Optional[str] = None,
    author: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to render content for web display.

    Args:
        content: Markdown content to render
        css_theme: CSS theme
        title: Document title
        author: Document author

    Returns:
        Dictionary with rendered content and options
    """
    config = RenderConfig(
        css_theme=css_theme, title=title, author=author, download_enabled=True
    )

    renderer = MarkdownRenderer(config)
    return renderer.render_for_web(content)
