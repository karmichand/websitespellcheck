"""Flask web application for website spell and grammar checking."""

import os
from flask import Flask, render_template, request, jsonify

from .checker import WebsiteChecker


app = Flask(__name__)


@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def check_website():
    """Check a website for spelling and grammar errors."""
    data = request.get_json() if request.is_json else request.form
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Add https:// if no protocol specified
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    check_spelling = data.get("check_spelling", True)
    check_grammar = data.get("check_grammar", True)

    # Handle string values from form
    if isinstance(check_spelling, str):
        check_spelling = check_spelling.lower() in ("true", "1", "on")
    if isinstance(check_grammar, str):
        check_grammar = check_grammar.lower() in ("true", "1", "on")

    try:
        with WebsiteChecker(
            check_spelling=check_spelling,
            check_grammar=check_grammar,
        ) as checker:
            result = checker.check(url)

        if result.error_message:
            return jsonify({"error": result.error_message}), 400

        return jsonify({
            "url": result.url,
            "text_elements_count": result.text_elements_count,
            "total_errors": result.total_errors,
            "extracted_text": result.extracted_text,
            "spelling_errors": [
                {
                    "word": e.word,
                    "suggestions": e.suggestions[:5],
                    "context": e.context,
                }
                for e in result.spelling_errors
            ],
            "grammar_errors": [
                {
                    "message": e.message,
                    "suggestions": e.suggestions[:5],
                    "context": e.context,
                }
                for e in result.grammar_errors
            ],
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


def main():
    """Run the web application."""
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
