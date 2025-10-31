"""
Command-line interface for md2latex.

This module provides a CLI for converting Markdown files to PDF/LaTeX
with various options for configuration, templates, and output control.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional

from . import __version__
from .api import (
    convert_markdown_to_pdf,
    convert_markdown_to_latex,
    create_config_file,
    list_available_templates,
    validate_template,
    merge_markdown_files
)
from .config import create_sample_config


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s'
    )


def cmd_convert(args: argparse.Namespace) -> int:
    """Handle the convert command."""
    try:
        # Load config file (required)
        if not args.config:
            print('Error: Config file is required', file=sys.stderr)
            return 1

        from md2latex.config import Config
        config = Config.from_yaml(args.config)
        
        # Get input files from config
        if not config.contents.files:
            print('Error: No input files specified in config file',
                  file=sys.stderr)
            return 1

        # Resolve file paths relative to config file directory
        config_dir = Path(args.config).parent
        input_files = [str(config_dir / f) for f in config.contents.files]

        # Generate output path if not provided
        if not args.output:
            # Use config file name as base for output
            config_path = Path(args.config)
            output_extension = 'pdf' if args.format == 'pdf' else 'tex'
            output_filename = config_path.stem + '.' + output_extension
            args.output = output_filename
        
        # Ensure parent directory exists for specified output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if args.format == 'pdf':
            result_path = convert_markdown_to_pdf(
                input_files=input_files,
                output_file=args.output,
                config_file=args.config,
                template=None,
                metadata=None,
                working_dir=None,
                verbose=args.verbose
            )
        else:  # latex
            result_path = convert_markdown_to_latex(
                input_files=input_files,
                output_file=args.output,
                config_file=args.config,
                template=None,
                metadata=None,
                working_dir=None,
                verbose=args.verbose
            )
        
        print(f'Successfully generated: {result_path}')
        return 0
        
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1


def cmd_list_templates(args: argparse.Namespace) -> int:
    """Handle the list-templates command."""
    try:
        templates = list_available_templates()
        
        if not templates:
            print('No templates available.')
            return 0
        
        print('Available templates:')
        for name, template_type in sorted(templates.items()):
            status = '✓' if validate_template(name) else '✗'
            print(f'  {status} {name} ({template_type})')
        
        return 0
        
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1


def cmd_validate_template(args: argparse.Namespace) -> int:
    """Handle the validate-template command."""
    try:
        is_valid = validate_template(args.template)
        
        if is_valid:
            print(f'Template "{args.template}" is valid.')
            return 0
        else:
            print(f'Template "{args.template}" is invalid or not found.')
            return 1
            
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1


def cmd_create_config(args: argparse.Namespace) -> int:
    """Handle the create-config command."""
    try:
        config_path = create_config_file(
            output_path=args.output,
            template=args.template,
            metadata={
                'title': args.title,
                'author': args.author,
                'company': args.company,
            } if any([args.title, args.author, args.company]) else None
        )
        
        print(f'Configuration file created: {config_path}')
        return 0
        
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1


def cmd_merge(args: argparse.Namespace) -> int:
    """Handle the merge command."""
    try:
        result_path = merge_markdown_files(
            input_files=args.input,
            output_file=args.output,
            add_page_breaks=not args.no_page_breaks
        )
        
        print(f'Merged file created: {result_path}')
        return 0
        
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog='md2latex',
        description='Convert Markdown files to PDF using LaTeX templates'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'md2latex {__version__}'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Convert command
    convert_parser = subparsers.add_parser(
        'convert',
        help='Convert Markdown files to PDF or LaTeX'
    )
    
    convert_parser.add_argument(
        'config',
        help='Configuration YAML file'
    )
    
    convert_parser.add_argument(
        '--output', '-o',
        help='Output file path (default: [config_name].pdf or .tex)'
    )
    
    convert_parser.add_argument(
        '--format', '-f',
        choices=['pdf', 'latex'],
        default='pdf',
        help='Output format (default: pdf)'
    )
    
    # List templates command
    list_parser = subparsers.add_parser(
        'list-templates',
        help='List available templates'
    )
    
    # Validate template command
    validate_parser = subparsers.add_parser(
        'validate-template',
        help='Validate a template'
    )
    
    validate_parser.add_argument(
        'template',
        help='Template name to validate'
    )
    
    # Create config command
    config_parser = subparsers.add_parser(
        'create-config',
        help='Create a sample configuration file'
    )
    
    config_parser.add_argument(
        '--output', '-o',
        default='md2latex.yaml',
        help='Output configuration file path (default: md2latex.yaml)'
    )
    
    config_parser.add_argument(
        '--template', '-t',
        default='simple',
        help='Template name (default: simple)'
    )
    
    config_parser.add_argument(
        '--title',
        help='Document title'
    )
    
    config_parser.add_argument(
        '--author',
        help='Document author'
    )
    
    config_parser.add_argument(
        '--company',
        help='Company name'
    )
    
    # Merge command
    merge_parser = subparsers.add_parser(
        'merge',
        help='Merge multiple Markdown files into one'
    )
    
    merge_parser.add_argument(
        'input',
        nargs='+',
        help='Input Markdown files to merge'
    )
    
    merge_parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output merged file path'
    )
    
    merge_parser.add_argument(
        '--no-page-breaks',
        action='store_true',
        help='Do not add page breaks between files'
    )
    
    return parser


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Command handlers
    handlers = {
        'convert': cmd_convert,
        'list-templates': cmd_list_templates,
        'validate-template': cmd_validate_template,
        'create-config': cmd_create_config,
        'merge': cmd_merge,
    }
    
    handler = handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f'Unknown command: {args.command}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())