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
        
        # Create and add metadata file
        metadata_file = self._create_metadata_file(working_dir)
        if metadata_file:
            cmd.extend(['--metadata-file', str(metadata_file)])
        
        # Add template includes explicitly for both PDF and LaTeX output
        # (pandoc doesn't reliably process includes from metadata files)
        if self.config.template.name and self.config.template.name != 'default':
            try:
                # Add titlepage if available
                titlepage_path = self.template_manager.get_template_component(
                    self.config.template.name, 'titlepage'
                )
                if titlepage_path and titlepage_path.exists():
                    cmd.extend(['--include-before-body', str(titlepage_path)])
                
                # Add appendix if available
                appendix_path = self.template_manager.get_template_component(
                    self.config.template.name, 'appendix'
                )
                if appendix_path and appendix_path.exists():
                    cmd.extend(['--include-after-body', str(appendix_path)])
                    
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
    
    def _create_metadata_file(self, working_dir: Path) -> Optional[Path]:
        """Create a pandoc metadata file combining template defaults and user config.
        
        Args:
            working_dir: Working directory for the metadata file
            
        Returns:
            Path to the created metadata file, or None if no template
        """
        if not self.config.template.name or self.config.template.name == 'default':
            return None
        
        try:
            # Load template metadata
            template_metadata = self.template_manager.load_template_metadata(
                self.config.template.name
            )
            
            # Merge with user configuration
            combined_metadata = template_metadata.copy()
            user_metadata = self.config.get_pandoc_metadata()
            
            # User metadata overrides template defaults
            combined_metadata.update(user_metadata)
            
            # Remove include directives since we handle them explicitly via
            # command line
            combined_metadata.pop('include-before-body', None)
            combined_metadata.pop('include-after-body', None)
            
            # Write metadata file
            metadata_file = working_dir / 'metadata.yaml'
            with open(metadata_file, 'w', encoding='utf-8') as f:
                import yaml
                yaml.dump(combined_metadata, f, default_flow_style=False,
                          indent=2)
            
            return metadata_file
            
        except Exception as e:
            logger.warning(f'Failed to create metadata file: {e}')
            return None
    
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
