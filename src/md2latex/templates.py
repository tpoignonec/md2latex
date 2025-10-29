"""
Template management for md2latex.

This module handles loading and management of modular LaTeX template components
including metadata files, titlepage templates, and appendix templates.
"""

import yaml
import shutil
from pathlib import Path
from typing import Dict, Optional, Any


class TemplateManager:
    """Manages modular LaTeX templates for document generation."""
    
    def __init__(self, custom_template_dir: Optional[Path] = None):
        """Initialize template manager.
        
        Args:
            custom_template_dir: Directory containing custom templates
        """
        self.custom_template_dir = custom_template_dir
        self._builtin_templates = {
            'simple': 'simple',
            'qms': 'qms'
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
            for template_dir in self.custom_template_dir.iterdir():
                if template_dir.is_dir() and (template_dir / 'metadata.yaml').exists():
                    templates[template_dir.name] = 'custom'
        
        return templates
    
    def get_template_dir(self, template_name: str) -> Path:
        """Get the directory containing a template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Path to the template directory
            
        Raises:
            FileNotFoundError: If template is not found
        """
        # Check custom templates first
        if self.custom_template_dir:
            custom_path = self.custom_template_dir / template_name
            if custom_path.exists() and custom_path.is_dir():
                return custom_path
        
        # Check builtin templates
        if template_name in self._builtin_templates:
            builtin_path = self.builtin_dir / self._builtin_templates[template_name]
            if builtin_path.exists():
                return builtin_path
        
        raise FileNotFoundError(f'Template "{template_name}" not found')
    
    def load_template_metadata(self, template_name: str) -> Dict[str, Any]:
        """Load template metadata from metadata.yaml file.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template metadata as dictionary
        """
        template_dir = self.get_template_dir(template_name)
        metadata_file = template_dir / 'metadata.yaml'
        
        if not metadata_file.exists():
            return {}
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def get_template_component(self, template_name: str, component: str) -> Optional[Path]:
        """Get path to a template component (titlepage.tex, appendix.tex, etc.).
        
        Args:
            template_name: Name of the template
            component: Component name (e.g., 'titlepage', 'appendix')
            
        Returns:
            Path to component file if it exists, None otherwise
        """
        template_dir = self.get_template_dir(template_name)
        component_file = template_dir / f'{component}.tex'
        
        return component_file if component_file.exists() else None
    
    def validate_template(self, template_name: str) -> bool:
        """Validate that a template exists and has required components.
        
        Args:
            template_name: Name of the template to validate
            
        Returns:
            True if template is valid, False otherwise
        """
        try:
            template_dir = self.get_template_dir(template_name)
            
            # Check if directory exists
            if not template_dir.exists():
                return False
            
            # Check if metadata.yaml exists
            metadata_file = template_dir / 'metadata.yaml'
            if not metadata_file.exists():
                return False
            
            # Try to load metadata
            try:
                self.load_template_metadata(template_name)
            except Exception:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get information about a template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Dictionary containing template information
        """
        try:
            template_dir = self.get_template_dir(template_name)
            templates = self.list_templates()
            
            info = {
                'name': template_name,
                'path': str(template_dir),
                'type': templates.get(template_name, 'unknown'),
                'exists': template_dir.exists(),
                'valid': self.validate_template(template_name)
            }
            
            if template_dir.exists():
                # Check for available components
                components = []
                for component in ['titlepage', 'appendix']:
                    if self.get_template_component(template_name, component):
                        components.append(component)
                info['components'] = components
                
                # Get metadata
                info['metadata'] = self.load_template_metadata(template_name)
            
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