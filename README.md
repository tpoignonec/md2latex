# md2latex

A Python library for generating PDF documents from Markdown files using customizable LaTeX templates.

## Overview

md2latex provides a simple and extensible way to convert Markdown files to professional PDF documents using LaTeX templates. It supports multiple input files, metadata handling, and containerized execution for reproducibility.

## Installation

### Using pip (recommended)

```bash
pip install md2latex
```

### From source

```bash
git clone https://github.com/tpoignonec/md2latex.git
cd md2latex
pip install -e .
```

### Using Docker

The library includes a Docker container with all dependencies pre-installed:

```bash
# Build the container
docker build -t md2latex .

# Run with your files mounted
docker run -v $(pwd):/workspace md2latex convert input.md --output output.pdf
```

## Quick Start

### Simple document conversion

```bash
cd examples
md2latex convert \
    00_introduction.md \
    01_chapter1.md \
    02_chapter2.md \
    --output outputs/simple.pdf
```

### QMS-like document

```bash
cd examples
md2latex convert \
    00_introduction.md \
    01_chapter1.md \
    02_chapter2.md \
    --output outputs/simple.pdf \
    --template qms
```

### LaTeX output with custom document class

```bash
cd examples
md2latex convert \
    ../markdown-latex-template/content/01-main.md \
    --config config.yaml \
    --output document.tex \
    --format latex
```

This will create a `_build/` directory containing:
- `document.tex` - The generated LaTeX file
- `iris-report.cls` - The custom document class
- `metadata.yaml` - The document metadata
- Any other file required (images, bibliography file, etc.)

You can then compile the LaTeX file manually:

```bash
cd _build
pdflatex document.tex
```

## Working Directory Management

md2latex automatically manages working directories based on the output format:

- **PDF format**: Uses a temporary directory (`/tmp/md2latex_*`) that is cleaned up after generation
- **LaTeX format**: Uses `_build/` directory next to the config file, containing all files needed to compile the LaTeX document

This ensures that all necessary files (`.tex`, `.cls`, `metadata.yaml`) are in the same directory for easy compilation.

````

