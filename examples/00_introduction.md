# Introduction

This is a sample document that demonstrates the capabilities of md2latex.
The library can convert Markdown files to both LaTeX and PDF formats using
customizable templates.

## Features

md2latex supports:

- Multiple input files
- YAML configuration
- Custom LaTeX templates
- Metadata handling
- Bibliography support
- Code highlighting

## Mathematics

You can include mathematical expressions using LaTeX syntax:

$$E = mc^2$$

And inline math like $\alpha + \beta = \gamma$.

## Code Blocks

```python
def hello_world():
    print("Hello, World!")
    return True
```

## Tables

| Feature | Supported | Notes |
|---------|-----------|-------|
| Markdown | Yes | Full CommonMark support |
| LaTeX | Yes | Custom templates |
| PDF | Yes | Via pandoc and LaTeX |
| Bibliography | Yes | BibTeX format |

## Images

![Sample Image](example_image.png){ width=50% }

## Conclusion

md2latex provides a powerful and flexible way to convert Markdown
documents to professional PDF outputs using LaTeX templates.