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
        assert 'academic' in templates
        assert 'prjdoc' in templates
        
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
            
            template_content = '''
\\documentclass{article}
\\begin{document}
Test template
\\end{document}
'''
            
            template_path = manager.create_custom_template(
                'test_template', 
                template_content,
                custom_dir
            )
            
            assert template_path.exists()
            assert manager.validate_template('test_template') is True
            
            templates = manager.list_templates()
            assert 'test_template' in templates
            assert templates['test_template'] == 'custom'

    def test_load_template_content(self):
        """Test loading template content."""
        manager = TemplateManager()
        content = manager.load_template('simple')
        
        # Should contain basic LaTeX structure
        assert '\\documentclass' in content
        assert '\\begin{document}' in content
        assert '\\end{document}' in content

    def test_get_nonexistent_template_path(self):
        """Test error handling for nonexistent template."""
        manager = TemplateManager()
        
        with pytest.raises(FileNotFoundError):
            manager.get_template_path('nonexistent_template')

    def test_custom_template_priority(self):
        """Test that custom templates override builtin ones."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir)
            manager = TemplateManager(custom_dir)
            
            # Create a custom template with same name as builtin
            custom_content = '''
\\documentclass{article}
\\begin{document}
Custom simple template
\\end{document}
'''
            
            custom_path = custom_dir / 'simple.tex'
            with open(custom_path, 'w') as f:
                f.write(custom_content)
            
            # Should load the custom version
            content = manager.load_template('simple')
            assert 'Custom simple template' in content
            
            # Should still be listed as custom
            templates = manager.list_templates()
            assert templates['simple'] == 'custom'