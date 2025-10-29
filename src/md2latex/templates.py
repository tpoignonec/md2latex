"""
Template management for md2latex.

This module handles loading, validation, and management of LaTeX templates
including default templates and custom user templates.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import importlib.resources
from jinja2 import Environment, FileSystemLoader, Template


class TemplateManager:
    """Manages LaTeX templates for document generation."""
    
    def __init__(self, custom_template_dir: Optional[Path] = None):
        """Initialize template manager.
        
        Args:
            custom_template_dir: Directory containing custom templates
        """
        self.custom_template_dir = custom_template_dir
        self._builtin_templates = {
            'simple': 'simple.tex',
            'qms': 'qms.tex',
            'academic': 'academic.tex',
            'prjdoc': 'prjdoc.tex'
        }
        
        # Get builtin templates directory
        self.builtin_dir = Path(__file__).parent / 'templates'
        
    def list_templates(self) -> Dict[str, str]:
        """List all available templates.
        
        Returns:
            Dictionary mapping template names to their types (builtin/custom)
        """
        templates = {}
        
        # Add builtin templates
        for name in self._builtin_templates:
            templates[name] = 'builtin'
        
        # Add custom templates
        if self.custom_template_dir and self.custom_template_dir.exists():
            for template_file in self.custom_template_dir.glob('*.tex'):
                name = template_file.stem
                templates[name] = 'custom'
        
        return templates
    
    def get_template_path(self, template_name: str) -> Path:
        """Get the path to a template file.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Path to the template file
            
        Raises:
            FileNotFoundError: If template is not found
        """
        # Check custom templates first
        if self.custom_template_dir:
            custom_path = self.custom_template_dir / f'{template_name}.tex'
            if custom_path.exists():
                return custom_path
        
        # Check builtin templates
        if template_name in self._builtin_templates:
            builtin_path = self.builtin_dir / self._builtin_templates[template_name]
            if builtin_path.exists():
                return builtin_path
        
        raise FileNotFoundError(f'Template "{template_name}" not found')
    
    def load_template(self, template_name: str) -> str:
        """Load template content.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template content as string
        """
        template_path = self.get_template_path(template_name)
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with given context.
        
        Args:
            template_name: Name of the template
            context: Variables to use in template rendering
            
        Returns:
            Rendered template content
        """
        template_content = self.load_template(template_name)
        template = Template(template_content)
        return template.render(**context)
    
    def copy_template_assets(self, template_name: str, output_dir: Path) -> None:
        """Copy template assets (styles, images, etc.) to output directory.
        
        Args:
            template_name: Name of the template
            output_dir: Directory to copy assets to
        """
        template_path = self.get_template_path(template_name)
        template_dir = template_path.parent
        
        # Look for assets directory next to template
        assets_dir = template_dir / f'{template_name}_assets'
        if assets_dir.exists():
            output_assets = output_dir / 'assets'
            output_assets.mkdir(exist_ok=True)
            
            for asset_file in assets_dir.rglob('*'):
                if asset_file.is_file():
                    rel_path = asset_file.relative_to(assets_dir)
                    output_file = output_assets / rel_path
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(asset_file, output_file)
    
    def validate_template(self, template_name: str) -> bool:
        """Validate that a template exists and is properly formatted.
        
        Args:
            template_name: Name of the template to validate
            
        Returns:
            True if template is valid, False otherwise
        """
        try:
            template_path = self.get_template_path(template_name)
            
            # Check if file exists and is readable
            if not template_path.exists():
                return False
            
            # Try to read the template
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic validation - check for required LaTeX structure
            required_elements = [
                '\\documentclass',
                '\\begin{document}',
                '\\end{document}'
            ]
            
            return all(element in content for element in required_elements)
            
        except Exception:
            return False
    
    def create_custom_template(self, name: str, content: str, 
                             custom_dir: Optional[Path] = None) -> Path:
        """Create a new custom template.
        
        Args:
            name: Name for the new template
            content: LaTeX template content
            custom_dir: Directory to save template (uses default if None)
            
        Returns:
            Path to the created template file
        """
        if custom_dir is None:
            custom_dir = self.custom_template_dir or Path.cwd() / 'templates'
        
        custom_dir.mkdir(parents=True, exist_ok=True)
        template_path = custom_dir / f'{name}.tex'
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return template_path
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get information about a template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Dictionary containing template information
        """
        try:
            template_path = self.get_template_path(template_name)
            templates = self.list_templates()
            
            info = {
                'name': template_name,
                'path': str(template_path),
                'type': templates.get(template_name, 'unknown'),
                'exists': template_path.exists(),
                'valid': self.validate_template(template_name)
            }
            
            if template_path.exists():
                stat = template_path.stat()
                info.update({
                    'size': stat.st_size,
                    'modified': stat.st_mtime
                })
            
            return info
            
        except FileNotFoundError:
            return {
                'name': template_name,
                'exists': False,
                'valid': False
            }


def get_default_template_manager() -> TemplateManager:
    """Get a default template manager instance."""
    return TemplateManager()