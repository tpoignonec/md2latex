# Examples

This directory contains sample files and commands demonstrating the md2latex tool.

## Files to assemble

- `00_introduction.md` - Basic document with math, tables, and formatting
- `01_chapter1.md` - First chapter for multi-file documents
- `02_chapter2.md` - Second chapter for multi-file documents

## Configuration File

The `document.yaml` file is the main input to md2latex. It defines the input files and document metadata:

```yaml
contents:
  type: markdown
  files:
    - 00_introduction.md
    - 01_chapter1.md
    - 02_chapter2.md

metadata:
  title: "My Title"
  author: "The Author"
  company: "The Company"
  document_class: "iris-report"
```

## Basic Usage

### Generate LaTeX output

```bash
md2latex convert document.yaml --format latex
```

This generates `_build/document.tex` along with all required files (`iris-report.cls`, `metadata.yaml`).

### Generate LaTeX with custom output name

```bash
md2latex convert document.yaml --format latex --output my_document.tex
```

This generates `_build/my_document.tex`.

### Generate PDF output

```bash
md2latex convert document.yaml --format pdf
```

This generates `document.pdf` in a temporary directory.

### Generate PDF with custom output name

```bash
md2latex convert document.yaml --format pdf --output my_document.pdf
```
