"""
Configuration management for md2latex.

This module handles loading and validation of YAML configuration files
that specify LaTeX template selection, document metadata, and rendering parameters.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field


@dataclass
class TemplateConfig:
    """Configuration for LaTeX template selection and parameters."""

    name: str = 'report'
    font_size: str = '11pt'
    line_spacing: float = 1.25
    number_sections: bool = True
    table_of_contents: bool = True
    bibliography_style: str = 'ieee'


@dataclass
class DocumentMetadata:
    """Document metadata configuration."""
    title: str = "Untitled Document"
    subtitle: Optional[str] = None
    author: Union[str, List[str]] = "Unknown Author"
    date: str = "\\today"
    abstract: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    subject: Optional[str] = None
    company: Optional[str] = None
    project_name: Optional[str] = None
    document_type: Optional[str] = None
    revision: str = "1.0"
    language: str = "english"
    document_class: Optional[str] = None  # Custom document class (e.g., "iris-report")


@dataclass
class DocumentConfig:
    """Document configuration."""

    template: str = 'report'  # Template name
    source: str = 'markdown'  # Source type (e.g., 'markdown')
    files: List[str] = field(default_factory=list)  # List of input files
    bibliography: Optional[str] = None  # Bibliography file path


@dataclass
class ProcessingOptions:
    """Processing and rendering options."""
    pandoc_options: List[str] = field(default_factory=list)
    latex_engine: str = "pdflatex"
    output_latex: bool = False
    output_pdf: bool = True
    clean_intermediate: bool = True
    verbose: bool = False
    resource_path: List[str] = field(default_factory=list)


@dataclass
class Config:
    """Main configuration class for md2latex."""

    template: TemplateConfig = field(default_factory=TemplateConfig)
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    processing: ProcessingOptions = field(default_factory=ProcessingOptions)
    document: DocumentConfig = field(default_factory=DocumentConfig)
    
    @classmethod
    def from_yaml(cls, config_path: Union[str, Path]) -> 'Config':
        """Load configuration from a YAML file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in configuration file: {e}")
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create configuration from a dictionary."""
        # Extract and validate template configuration
        template_data = data.get('template', {})
        template_config = TemplateConfig(**{
            k: v for k, v in template_data.items() 
            if k in TemplateConfig.__dataclass_fields__
        })
        
        # Extract and validate metadata
        metadata_data = data.get('metadata', {})
        metadata = DocumentMetadata(**{
            k: v for k, v in metadata_data.items() 
            if k in DocumentMetadata.__dataclass_fields__
        })
        
        # Extract and validate processing options
        processing_data = data.get('processing', {})
        processing = ProcessingOptions(**{
            k: v for k, v in processing_data.items()
            if k in ProcessingOptions.__dataclass_fields__
        })

        # Extract and validate document configuration
        document_data = data.get('document', {})
        document = DocumentConfig(**{
            k: v for k, v in document_data.items()
            if k in DocumentConfig.__dataclass_fields__
        })

        return cls(
            template=template_config,
            metadata=metadata,
            processing=processing,
            document=document
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = {
            'template': {
                k: v for k, v in self.template.__dict__.items()
                if not k.startswith('_')
            },
            'metadata': {
                k: v for k, v in self.metadata.__dict__.items()
                if not k.startswith('_')
            },
            'processing': {
                k: v for k, v in self.processing.__dict__.items()
                if not k.startswith('_')
            }
        }

        # Add document if files are specified
        if self.document.files:
            document_dict = {
                k: v for k, v in self.document.__dict__.items()
                if not k.startswith('_')
            }
            result['document'] = document_dict

        return result
    
    def to_yaml(self, output_path: Union[str, Path]) -> None:
        """Save configuration to a YAML file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)
    
    def get_pandoc_metadata(self) -> Dict[str, Any]:
        """Get metadata formatted for pandoc frontmatter."""
        pandoc_meta = {}
        
        # Document metadata
        if self.metadata.title:
            pandoc_meta['title'] = self.metadata.title
        if self.metadata.subtitle:
            pandoc_meta['subtitle'] = self.metadata.subtitle
        if self.metadata.author:
            pandoc_meta['author'] = self.metadata.author
        if self.metadata.date:
            pandoc_meta['date'] = self.metadata.date
        if self.metadata.abstract:
            pandoc_meta['abstract'] = self.metadata.abstract
        
        # Template-specific metadata
        if self.metadata.company:
            pandoc_meta['company'] = self.metadata.company
        if self.metadata.document_type:
            pandoc_meta['document_type'] = self.metadata.document_type
        if self.metadata.revision:
            pandoc_meta['revision'] = self.metadata.revision

        # Template options
        # Only set document_class if explicitly specified in metadata
        if self.metadata.document_class:
            pandoc_meta['documentclass'] = self.metadata.document_class
            pandoc_meta['document_class'] = self.metadata.document_class
        
        pandoc_meta['fontsize'] = self.template.font_size
        pandoc_meta['linestretch'] = self.template.line_spacing
        pandoc_meta['numbersections'] = self.template.number_sections
        pandoc_meta['toc'] = self.template.table_of_contents
        
        return pandoc_meta


def create_default_config() -> Config:
    """Create a default configuration."""
    return Config()


def create_sample_config(output_path: Union[str, Path]) -> None:
    """Create a sample configuration file."""
    config = create_default_config()
    
    # Set some example values
    config.metadata.title = "Sample Document"
    config.metadata.author = ["John Doe", "Jane Smith"]
    config.metadata.company = "Example Corp"
    config.metadata.abstract = "This is a sample document generated with md2latex."
    config.template.name = "simple"
    config.template.font_size = "12pt"
    
    config.to_yaml(output_path)