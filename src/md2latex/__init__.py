"""
md2latex - A Python library for generating PDF documents from Markdown files using LaTeX templates.

This library provides a simple and extensible way to convert Markdown files to PDF
documents using customizable LaTeX templates. It supports multiple input files,
metadata handling, and containerized execution for reproducibility.

Main features:
- Support for multiple Markdown files as input
- YAML-based configuration system
- Customizable LaTeX templates
- Metadata handling (title, author, date, etc.)
- Command-line interface and Python API
- Containerized execution with Docker

Author: Thibault Poignonec
License: Apache 2.0
"""

__version__ = "0.1.0"
__author__ = "Thibault Poignonec"
__email__ = "Thibault.poignonec@gmail.com"
__license__ = "Apache 2.0"

from .converter import MarkdownConverter
from .config import Config
from .templates import TemplateManager
from .api import convert_markdown_to_pdf, convert_markdown_to_latex

__all__ = [
    "MarkdownConverter",
    "Config", 
    "TemplateManager",
    "convert_markdown_to_pdf",
    "convert_markdown_to_latex",
]