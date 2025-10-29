"""
High-level API for md2latex.

This module provides simple functions for converting Markdown to PDF/LaTeX
that can be easily integrated into other applications and workflows.
"""

from pathlib import Path
from typing import List, Optional, Union, Dict, Any

from .config import Config
from .converter import MarkdownConverter
from .templates import TemplateManager


def convert_markdown_to_pdf(
    input_files: Union[str, Path, List[Union[str, Path]]],
    output_file: Union[str, Path],
    config_file: Optional[Union[str, Path]] = None,
    template: str = 'simple',
    metadata: Optional[Dict[str, Any]] = None,
    working_dir: Optional[Union[str, Path]] = None,
    verbose: bool = False
) -> Path:
    """Convert Markdown files to PDF with automatic directory management.
    
    This function converts one or more Markdown files to a PDF document using
    customizable LaTeX templates. Output directories are created automatically
    as needed.
    
    Args:
        input_files: Single file or list of Markdown files to convert
        output_file: Output PDF file path (directories created automatically)
        config_file: Path to YAML configuration file (optional)
        template: Template name to use (default: 'simple')
        metadata: Document metadata (title, author, etc.)
        working_dir: Working directory for conversion (optional)
        verbose: Enable verbose output for debugging
        
    Returns:
        Path to the generated PDF file
        
    Examples:
        Basic usage with automatic output directory:
        >>> convert_markdown_to_pdf(
        ...     'document.md',
        ...     'output/document.pdf',  # Creates output/ directory
        ...     metadata={'title': 'My Document', 'author': 'John Doe'}
        ... )
        
        Multiple files with nested directory creation:
        >>> convert_markdown_to_pdf(
        ...     ['intro.md', 'main.md', 'conclusion.md'],
        ...     'reports/2024/final_report.pdf',  # Creates reports/2024/
        ...     template='academic'
        ... )
        
        With configuration file:
        >>> convert_markdown_to_pdf(
        ...     'thesis.md',
        ...     'output/thesis.pdf',
        ...     config_file='academic_config.yaml'
        ... )
    """
    # Normalize input files to list
    if isinstance(input_files, (str, Path)):
        input_files = [input_files]
    
    # Load configuration
    if config_file:
        config = Config.from_yaml(config_file)
    else:
        config = Config()
    
    # Override template if specified
    config.template.name = template
    
    # Override metadata if provided
    if metadata:
        for key, value in metadata.items():
            if hasattr(config.metadata, key):
                setattr(config.metadata, key, value)
    
    # Set verbose mode
    config.processing.verbose = verbose
    
    # Create converter and template manager
    template_manager = TemplateManager()
    converter = MarkdownConverter(config, template_manager)
    
    # Convert to PDF
    return converter.convert_to_pdf(
        input_files, output_file, 
        working_dir=Path(working_dir) if working_dir else None
    )


def convert_markdown_to_latex(
    input_files: Union[str, Path, List[Union[str, Path]]],
    output_file: Union[str, Path],
    config_file: Optional[Union[str, Path]] = None,
    template: str = 'simple',
    metadata: Optional[Dict[str, Any]] = None,
    working_dir: Optional[Union[str, Path]] = None,
    verbose: bool = False
) -> Path:
    """Convert Markdown files to LaTeX.
    
    Args:
        input_files: Single file or list of Markdown files to convert
        output_file: Output LaTeX file path
        config_file: Path to YAML configuration file (optional)
        template: Template name to use (default: 'simple')
        metadata: Document metadata (title, author, etc.)
        working_dir: Working directory for conversion
        verbose: Enable verbose output
        
    Returns:
        Path to the generated LaTeX file
        
    Example:
        >>> convert_markdown_to_latex(
        ...     ['chapter1.md', 'chapter2.md'],
        ...     'document.tex',
        ...     template='academic'
        ... )
    """
    # Normalize input files to list
    if isinstance(input_files, (str, Path)):
        input_files = [input_files]
    
    # Load configuration
    if config_file:
        config = Config.from_yaml(config_file)
    else:
        config = Config()
    
    # Override template if specified
    config.template.name = template
    
    # Override metadata if provided
    if metadata:
        for key, value in metadata.items():
            if hasattr(config.metadata, key):
                setattr(config.metadata, key, value)
    
    # Set verbose mode
    config.processing.verbose = verbose
    
    # Create converter and template manager
    template_manager = TemplateManager()
    converter = MarkdownConverter(config, template_manager)
    
    # Convert to LaTeX
    return converter.convert_to_latex(
        input_files, output_file,
        working_dir=Path(working_dir) if working_dir else None
    )


def create_config_file(
    output_path: Union[str, Path],
    template: str = 'simple',
    metadata: Optional[Dict[str, Any]] = None
) -> Path:
    """Create a configuration file with specified settings.
    
    Args:
        output_path: Path where to save the configuration file
        template: Template name to configure
        metadata: Document metadata to include
        
    Returns:
        Path to the created configuration file
        
    Example:
        >>> create_config_file(
        ...     'config.yaml',
        ...     template='academic',
        ...     metadata={'title': 'Research Paper', 'author': 'Dr. Smith'}
        ... )
    """
    config = Config()
    config.template.name = template
    
    if metadata:
        for key, value in metadata.items():
            if hasattr(config.metadata, key):
                setattr(config.metadata, key, value)
    
    output_path = Path(output_path)
    config.to_yaml(output_path)
    
    return output_path


def list_available_templates() -> Dict[str, str]:
    """List all available templates.
    
    Returns:
        Dictionary mapping template names to their types
        
    Example:
        >>> templates = list_available_templates()
        >>> print(templates)
        {'simple': 'builtin', 'academic': 'builtin', 'custom': 'custom'}
    """
    template_manager = TemplateManager()
    return template_manager.list_templates()


def validate_template(template_name: str) -> bool:
    """Validate that a template exists and is properly formatted.
    
    Args:
        template_name: Name of the template to validate
        
    Returns:
        True if template is valid, False otherwise
        
    Example:
        >>> is_valid = validate_template('simple')
        >>> print(f'Template is valid: {is_valid}')
    """
    template_manager = TemplateManager()
    return template_manager.validate_template(template_name)


def merge_markdown_files(
    input_files: List[Union[str, Path]],
    output_file: Union[str, Path],
    add_page_breaks: bool = True
) -> Path:
    """Merge multiple Markdown files into a single file.
    
    Args:
        input_files: List of Markdown files to merge
        output_file: Output merged file path
        add_page_breaks: Whether to add page breaks between files
        
    Returns:
        Path to the merged file
        
    Example:
        >>> merge_markdown_files(
        ...     ['intro.md', 'chapter1.md', 'conclusion.md'],
        ...     'complete_document.md'
        ... )
    """
    config = Config()
    converter = MarkdownConverter(config)
    
    return converter.merge_markdown_files(
        input_files, output_file, add_page_breaks
    )