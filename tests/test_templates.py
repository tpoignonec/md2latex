"""Tests for md2latex template management."""

import pytest
import tempfile
from pathlib import Path

from md2latex.templates import TemplateManager


class TestTemplateManager:
    """Test TemplateManager class."""

    def test_list_builtin_templates(self):
        """Test listing builtin templates."""
        manager = TemplateManager()
        templates = manager.list_templates()
        
        # Should have the default builtin templates
        assert 'simple' in templates
        assert 'qms' in templates
        
        # All should be builtin
        assert templates['simple'] == 'builtin'
        assert templates['qms'] == 'builtin'

    def test_validate_builtin_templates(self):
        """Test validation of builtin templates."""
        manager = TemplateManager()
        
        # These should validate successfully
        assert manager.validate_template('simple') is True

    def test_get_template_info(self):
        """Test getting template information."""
        manager = TemplateManager()
        info = manager.get_template_info('simple')
        
        assert info['name'] == 'simple'
        assert info['type'] == 'builtin'
        assert info['exists'] is True
        assert info['valid'] is True

    def test_nonexistent_template_info(self):
        """Test getting info for nonexistent template."""
        manager = TemplateManager()
        info = manager.get_template_info('nonexistent')
        
        assert info['name'] == 'nonexistent'
        assert info['exists'] is False
        assert info['valid'] is False

    def test_create_custom_template(self):
        """Test creating a custom template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir)
            manager = TemplateManager(custom_dir)
            
            # Create custom template directory and metadata
            template_dir = custom_dir / 'test_template'
            template_dir.mkdir()
            
            metadata_content = '''
documentclass: article
fontsize: 12pt
'''
            
            with open(template_dir / 'metadata.yaml', 'w') as f:
                f.write(metadata_content)
            
            assert manager.validate_template('test_template') is True
            
            templates = manager.list_templates()
            assert 'test_template' in templates
            assert templates['test_template'] == 'custom'

    def test_load_template_metadata(self):
        """Test loading template metadata."""
        manager = TemplateManager()
        metadata = manager.load_template_metadata('simple')
        
        # Should contain basic configuration
        assert 'documentclass' in metadata
        assert metadata['documentclass'] == 'article'

    def test_get_template_component(self):
        """Test getting template components."""
        manager = TemplateManager()
        
        # Should have titlepage component
        titlepage = manager.get_template_component('simple', 'titlepage')
        assert titlepage is not None
        assert titlepage.exists()

    def test_get_nonexistent_template_dir(self):
        """Test error handling for nonexistent template."""
        manager = TemplateManager()
        
        with pytest.raises(FileNotFoundError):
            manager.get_template_dir('nonexistent_template')

    def test_custom_template_priority(self):
        """Test that custom templates override builtin ones."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir)
            manager = TemplateManager(custom_dir)
            
            # Create a custom template with same name as builtin
            simple_dir = custom_dir / 'simple'
            simple_dir.mkdir()
            
            custom_metadata = '''
documentclass: article
fontsize: 14pt
custom: true
'''
            
            with open(simple_dir / 'metadata.yaml', 'w') as f:
                f.write(custom_metadata)
            
            # Should load the custom version
            metadata = manager.load_template_metadata('simple')
            assert metadata.get('custom') is True
            assert metadata.get('fontsize') == '14pt'
            
            # Should still be listed as custom
            templates = manager.list_templates()
            assert templates['simple'] == 'custom'