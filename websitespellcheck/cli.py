"""Command-line interface for the website spell checker."""

import argparse
import json
import sys

from .checker import WebsiteChecker


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Check websites for spelling and grammar errors.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com
  %(prog)s https://example.com --spelling-only
  %(prog)s https://example.com --grammar-only
  %(prog)s https://example.com --json
        """,
    )

    parser.add_argument("url", help="The URL of the website to check")
    parser.add_argument(
        "--spelling-only",
        action="store_true",
        help="Only check for spelling errors",
    )
    parser.add_argument(
        "--grammar-only",
        action="store_true",
        help="Only check for grammar errors",
    )
    parser.add_argument(
        "--language",
        "-l",
        default="en",
        help="Language code (default: en)",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        dest="output_json",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output",
    )

    args = parser.parse_args()

    # Determine what to check
    check_spelling = not args.grammar_only
    check_grammar = not args.spelling_only

    if args.verbose:
        print(f"Checking: {args.url}")
        print(f"Spelling: {'yes' if check_spelling else 'no'}")
        print(f"Grammar: {'yes' if check_grammar else 'no'}")
        print(f"Language: {args.language}")
        print()

    # Run the check
    with WebsiteChecker(
        check_spelling=check_spelling,
        check_grammar=check_grammar,
        language=args.language,
    ) as checker:
        result = checker.check(args.url)

    # Output results
    if args.output_json:
        output = {
            "url": result.url,
            "text_elements_count": result.text_elements_count,
            "spelling_errors": [
                {
                    "word": e.word,
                    "suggestions": e.suggestions,
                    "context": e.context,
                    "source": e.source,
                    "tag": e.tag,
                }
                for e in result.spelling_errors
            ],
            "grammar_errors": [
                {
                    "message": e.message,
                    "suggestions": e.suggestions,
                    "context": e.context,
                    "rule_id": e.rule_id,
                    "category": e.category,
                    "source": e.source,
                    "tag": e.tag,
                }
                for e in result.grammar_errors
            ],
            "total_errors": result.total_errors,
            "error_message": result.error_message,
        }
        print(json.dumps(output, indent=2))
    else:
        print(result.summary())

    # Exit with error code if errors found
    sys.exit(1 if result.has_errors else 0)


if __name__ == "__main__":
    main()
