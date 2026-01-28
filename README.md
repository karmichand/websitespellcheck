# Website Spell Check

A command-line tool to check websites for spelling and grammar errors.

## Features

- Fetches and parses web pages to extract text content
- Checks for spelling errors using pyspellchecker
- Checks for grammar errors using LanguageTool
- Outputs results in human-readable or JSON format
- Supports multiple languages

## Installation

### macOS (Homebrew)

Install dependencies using Homebrew:
```bash
brew install python@3.12 openjdk
```

Add Java to your path (add to your shell profile for persistence):
```bash
export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"
```

Then install the package:
```bash
pip install -r requirements.txt
pip install -e .
```

### Linux/Other

```bash
pip install -r requirements.txt
pip install -e .
```

## Usage

Basic usage:
```bash
websitespellcheck https://example.com
```

Check spelling only:
```bash
websitespellcheck https://example.com --spelling-only
```

Check grammar only:
```bash
websitespellcheck https://example.com --grammar-only
```

Output as JSON:
```bash
websitespellcheck https://example.com --json
```

Verbose output:
```bash
websitespellcheck https://example.com -v
```

## Python API

```python
from websitespellcheck import WebsiteChecker

with WebsiteChecker() as checker:
    result = checker.check("https://example.com")
    print(result.summary())
```

## Requirements

- Python 3.10+
- Java Runtime (for LanguageTool grammar checking)
