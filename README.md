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

