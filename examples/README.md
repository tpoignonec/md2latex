# Examples

This directory contains sample files and commands demonstrating all features from the main README.md.

## Files to assemble

- `00_introduction.md` - Basic document with math, tables, and formatting
- `01_chapter1.md` - First chapter for multi-file documents
- `02_chapter2.md` - Second chapter for multi-file documents

## Basic Commands

### Simple document conversion

```bash
md2latex convert \
    00_introduction.md 01_chapter1.md 02_chapter2.md \
    --config basic_config.yaml \
    --output outputs/simple.pdf
```

### Use templates

For instance to generate a QMS-like document:
```bash
md2latex convert \
    00_introduction.md 01_chapter1.md 02_chapter2.md \
    --config basic_config.yaml \
    --output outputs/qms.pdf \
    --template qms
```

### Define styles in config


```bash
md2latex convert \
    00_introduction.md 01_chapter1.md 02_chapter2.md \
    --config basic_config.yaml \
    --output outputs/qms.pdf \
    --template qms
```

