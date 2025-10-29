"""Tests for md2latex configuration module."""

import pytest
import tempfile
import yaml
from pathlib import Path

from md2latex.config import Config, TemplateConfig, DocumentMetadata, ProcessingOptions


class TestTemplateConfig:
    """Test TemplateConfig class."""

    def test_default_values(self):
        """Test default template configuration values."""
        config = TemplateConfig()
        assert config.name == 'simple'
        assert config.style == 'article'
        assert config.margin == '3cm'
        assert config.font_size == '11pt'
        assert config.line_spacing == 1.25
        assert config.number_sections is True
        assert config.table_of_contents is True
        assert config.bibliography_style == 'ieee'


class TestDocumentMetadata:
    """Test DocumentMetadata class."""

    def test_default_values(self):
        """Test default document metadata values."""
        metadata = DocumentMetadata()
        assert metadata.title == 'Untitled Document'
        assert metadata.author == 'Unknown Author'
        assert metadata.date == '\\today'
        assert metadata.revision == '1.0'
        assert metadata.language == 'english'


class TestProcessingOptions:
    """Test ProcessingOptions class."""

    def test_default_values(self):
        """Test default processing options."""
        options = ProcessingOptions()
        assert options.latex_engine == 'pdflatex'
        assert options.output_latex is False
        assert options.output_pdf is True
        assert options.clean_intermediate is True
        assert options.verbose is False


class TestConfig:
    """Test Config class."""

    def test_default_config(self):
        """Test default configuration creation."""
        config = Config()
        assert isinstance(config.template, TemplateConfig)
        assert isinstance(config.metadata, DocumentMetadata)
        assert isinstance(config.processing, ProcessingOptions)

    def test_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            'template': {
                'name': 'qms',
                'font_size': '12pt'
            },
            'metadata': {
                'title': 'Test Document',
                'author': 'Test Author'
            },
            'processing': {
                'verbose': True
            }
        }
        
        config = Config.from_dict(data)
        assert config.template.name == 'qms'
        assert config.template.font_size == '12pt'
        assert config.metadata.title == 'Test Document'
        assert config.metadata.author == 'Test Author'
        assert config.processing.verbose is True

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = Config()
        config.template.name = 'test'
        config.metadata.title = 'Test Title'
        
        data = config.to_dict()
        assert data['template']['name'] == 'test'
        assert data['metadata']['title'] == 'Test Title'

    def test_yaml_roundtrip(self):
        """Test saving and loading config from YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'test_config.yaml'
            
            # Create and save config
            config = Config()
            config.template.name = 'qms'
            config.metadata.title = 'YAML Test'
            config.to_yaml(config_path)
            
            # Load config back
            loaded_config = Config.from_yaml(config_path)
            assert loaded_config.template.name == 'qms'
            assert loaded_config.metadata.title == 'YAML Test'

    def test_yaml_file_not_found(self):
        """Test error handling for missing YAML file."""
        with pytest.raises(FileNotFoundError):
            Config.from_yaml('nonexistent.yaml')

    def test_invalid_yaml(self):
        """Test error handling for invalid YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content: [')
            f.flush()
            
            with pytest.raises(ValueError):
                Config.from_yaml(f.name)

    def test_get_pandoc_metadata(self):
        """Test pandoc metadata generation."""
        config = Config()
        config.metadata.title = 'Test Document'
        config.metadata.author = ['Author 1', 'Author 2']
        config.metadata.company = 'Test Company'
        
        metadata = config.get_pandoc_metadata()
        assert metadata['title'] == 'Test Document'
        assert metadata['author'] == ['Author 1', 'Author 2']
        assert metadata['PDcompany'] == 'Test Company'
        assert metadata['documentclass'] == 'article'
        assert metadata['fontsize'] == '11pt'