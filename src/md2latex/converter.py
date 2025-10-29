"""
Core conversion engine for md2latex.

This module handles the conversion from Markdown to LaTeX/PDF using pandoc,
with support for multiple input files, metadata handling, and template processing.
"""

import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import logging

from .config import Config
from .templates import TemplateManager


logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """Exception raised when conversion fails."""
    pass


class MarkdownConverter:
    """Main converter class for Markdown to LaTeX/PDF conversion."""
    
    def __init__(self, config: Optional[Config] = None, 
                 template_manager: Optional[TemplateManager] = None):
        """Initialize the converter.
        
        Args:
            config: Configuration object
            template_manager: Template manager instance
        """
        self.config = config or Config()
        self.template_manager = template_manager or TemplateManager()
        
    def convert_to_latex(self, input_files: List[Union[str, Path]], 
                        output_file: Union[str, Path],
                        working_dir: Optional[Path] = None) -> Path:
        """Convert Markdown files to LaTeX.
        
        Args:
            input_files: List of input Markdown files
            output_file: Output LaTeX file path
            working_dir: Working directory for conversion
            
        Returns:
            Path to the generated LaTeX file
        """
        input_paths = [Path(f).resolve() for f in input_files]  # Make absolute
        output_path = Path(output_file)
        
        # Validate input files
        for input_path in input_paths:
            if not input_path.exists():
                raise FileNotFoundError(f'Input file not found: {input_path}')
        
        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare working directory
        if working_dir is None:
            working_dir = output_path.parent
        working_dir.mkdir(parents=True, exist_ok=True)
        
        # Build pandoc command
        cmd = self._build_pandoc_command(
            input_paths, output_path, 'latex', working_dir
        )
        
        # Execute conversion
        try:
            result = subprocess.run(
                cmd, 
                cwd=working_dir,
                capture_output=True, 
                text=True, 
                check=True
            )
            
            if self.config.processing.verbose:
                logger.info(f'Pandoc output: {result.stdout}')
                
        except subprocess.CalledProcessError as e:
            error_msg = f'LaTeX conversion failed: {e.stderr}'
            logger.error(error_msg)
            raise ConversionError(error_msg) from e
        
        return output_path
    
    def convert_to_pdf(self, input_files: List[Union[str, Path]], 
                      output_file: Union[str, Path],
                      working_dir: Optional[Path] = None,
                      keep_latex: bool = False) -> Path:
        """Convert Markdown files to PDF.
        
        Args:
            input_files: List of input Markdown files
            output_file: Output PDF file path
            working_dir: Working directory for conversion
            keep_latex: Whether to keep intermediate LaTeX file
            
        Returns:
            Path to the generated PDF file
        """
        input_paths = [Path(f).resolve() for f in input_files]  # Make absolute
        output_path = Path(output_file)
        
        # Validate input files
        for input_path in input_paths:
            if not input_path.exists():
                raise FileNotFoundError(f'Input file not found: {input_path}')
        
        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare working directory
        if working_dir is None:
            working_dir = output_path.parent
        working_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy template assets if needed
        if self.config.template.name:
            try:
                self.template_manager.copy_template_assets(
                    self.config.template.name, working_dir
                )
            except Exception as e:
                logger.warning(f'Failed to copy template assets: {e}')
        
        # Build pandoc command for PDF
        cmd = self._build_pandoc_command(
            input_paths, output_path, 'pdf', working_dir
        )
        
        # Execute conversion
        try:
            result = subprocess.run(
                cmd, 
                cwd=working_dir,
                capture_output=True, 
                text=True, 
                check=True
            )
            
            if self.config.processing.verbose:
                logger.info(f'Pandoc output: {result.stdout}')
                
        except subprocess.CalledProcessError as e:
            error_msg = f'PDF conversion failed: {e.stderr}'
            logger.error(error_msg)
            raise ConversionError(error_msg) from e
        
        # Handle LaTeX file
        if keep_latex or self.config.processing.output_latex:
            latex_path = output_path.with_suffix('.tex')
            if latex_path.exists():
                logger.info(f'LaTeX file saved: {latex_path}')
        
        return output_path
    
    def _build_pandoc_command(self, input_files: List[Path], 
                            output_file: Path, output_format: str,
                            working_dir: Path) -> List[str]:
        """Build the pandoc command with all necessary options.
        
        Args:
            input_files: List of input file paths
            output_file: Output file path
            output_format: Output format ('latex' or 'pdf')
            working_dir: Working directory
            
        Returns:
            Complete pandoc command as list of strings
        """
        # Convert input files to absolute paths
        input_files = [Path(f).resolve() for f in input_files]
        
        # Convert output file to absolute path
        output_file = Path(output_file).resolve()
        
        cmd = ['pandoc']
        
        # Add input files
        cmd.extend([str(f) for f in input_files])
        
        # Add output file
        cmd.extend(['--output', str(output_file)])
        
        # Set output format
        if output_format == 'pdf':
            cmd.extend(['--pdf-engine', self.config.processing.latex_engine])
        else:
            cmd.extend(['--to', 'latex', '--standalone'])
        
        # Add metadata
        metadata = self.config.get_pandoc_metadata()
        for key, value in metadata.items():
            if isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, list):
                for item in value:
                    cmd.extend(['--metadata', f'{key}={item}'])
                continue
            cmd.extend(['--metadata', f'{key}={value}'])
        
        # Add template if specified
        if self.config.template.custom_template_path:
            template_path = Path(self.config.template.custom_template_path)
            if template_path.exists():
                cmd.extend(['--template', str(template_path)])
        elif self.config.template.name and self.config.template.name != 'default':
            try:
                template_path = self.template_manager.get_template_path(
                    self.config.template.name
                )
                cmd.extend(['--template', str(template_path)])
            except FileNotFoundError:
                logger.warning(
                    f'Template {self.config.template.name} not found, '
                    'using default'
                )
        
        # Add resource paths
        resource_paths = self.config.processing.resource_path.copy()
        resource_paths.append(str(working_dir))
        
        # Add input file directories to resource paths
        for input_file in input_files:
            parent_dir = str(input_file.parent)
            if parent_dir not in resource_paths:
                resource_paths.append(parent_dir)
        
        cmd.extend(['--resource-path', ':'.join(resource_paths)])
        
        # Add citation processing if bibliography is configured
        bibliography_path = None
        for input_file in input_files:
            bib_file = input_file.parent / 'bibliography.bib'
            if bib_file.exists():
                bibliography_path = bib_file
                break
        
        if bibliography_path:
            cmd.extend(['--bibliography', str(bibliography_path)])
            cmd.append('--citeproc')
            
            # Add CSL style if available
            csl_path = bibliography_path.parent / f'{self.config.template.bibliography_style}.csl'
            if csl_path.exists():
                cmd.extend(['--csl', str(csl_path)])
        
        # Add markdown extensions
        from_format = 'markdown+tex_math_single_backslash+tex_math_dollars+raw_tex'
        cmd.extend(['--from', from_format])
        
        # Add additional pandoc options
        cmd.extend(self.config.processing.pandoc_options)
        
        if self.config.processing.verbose:
            logger.info(f'Pandoc command: {" ".join(cmd)}')
        
        return cmd
    
    def merge_markdown_files(self, input_files: List[Union[str, Path]], 
                           output_file: Union[str, Path],
                           add_page_breaks: bool = True) -> Path:
        """Merge multiple Markdown files into a single file.
        
        Args:
            input_files: List of input Markdown files
            output_file: Output merged Markdown file
            add_page_breaks: Whether to add page breaks between files
            
        Returns:
            Path to the merged file
        """
        input_paths = [Path(f) for f in input_files]
        output_path = Path(output_file)
        
        # Validate input files
        for input_path in input_paths:
            if not input_path.exists():
                raise FileNotFoundError(f'Input file not found: {input_path}')
        
        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for i, input_path in enumerate(input_paths):
                with open(input_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    
                    # Add page break before each file except the first
                    if i > 0 and add_page_breaks:
                        outfile.write('\n\\pagebreak\n\n')
                    
                    outfile.write(content)
                    
                    # Add newline at end if not present
                    if not content.endswith('\n'):
                        outfile.write('\n')
        
        return output_path