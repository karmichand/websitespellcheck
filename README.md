# Website Spell Check

A tool to check websites for spelling and grammar errors. Available as a command-line tool, web interface, or Docker container.

## Features

- Fetches and parses web pages to extract text content
- Checks for spelling errors using pyspellchecker
- Checks for grammar errors using LanguageTool
- Web interface for easy browser-based checking
- Outputs results in human-readable or JSON format
- Supports multiple languages
- Docker support for easy deployment

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

### Docker Installation

```bash
# Using Docker Compose (recommended)
docker compose up -d

# Or build and run manually
docker build -t websitespellcheck .
docker run -p 5001:5000 websitespellcheck
```

## Usage

### Web Interface

Start the web server:
```bash
# Local
websitespellcheck-web

# Or with Docker
docker compose up -d
```

Then open http://localhost:5000 in your browser (or http://localhost:5001 when using Docker).

**Note:** Port 5000 is used by AirPlay Receiver on macOS. Docker is configured to use port 5001 by default to avoid this conflict.

### Command Line

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

### Python API

```python
from websitespellcheck import WebsiteChecker

with WebsiteChecker() as checker:
    result = checker.check("https://example.com")
    print(result.summary())
```

## Configuration

The web server can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST`   | 0.0.0.0 | Host to bind to |
| `PORT`   | 5000    | Port to listen on |
| `DEBUG`  | false   | Enable debug mode |

## Requirements

- Python 3.10+
- Java Runtime (for LanguageTool grammar checking)
