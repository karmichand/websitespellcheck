"""Grammar checking module."""

from dataclasses import dataclass

import language_tool_python


@dataclass
class GrammarError:
    """Represents a grammar error found in text."""

    message: str
    context: str
    suggestions: list[str]
    rule_id: str
    category: str
    source: str
    tag: str

    def __str__(self) -> str:
        suggestions_str = ", ".join(self.suggestions[:3]) if self.suggestions else "none"
        return f"{self.message} -> suggestions: [{suggestions_str}] (in {self.source})"


class GrammarChecker:
    """Checks text for grammar errors using LanguageTool."""

    # Rule IDs to ignore (overly pedantic or false positives)
    IGNORED_RULES = {
        "WHITESPACE_RULE",
        "COMMA_PARENTHESIS_WHITESPACE",
        "UPPERCASE_SENTENCE_START",  # Often wrong for web content
        "EN_QUOTES",  # Quote style preference
        "DASH_RULE",  # Dash style preference
        "MORFOLOGIK_RULE_EN_US",  # Let spell checker handle this
        "MORFOLOGIK_RULE_EN_GB",
        "WORD_CONTAINS_UNDERSCORE",  # Common in web content
        "EN_UNPAIRED_BRACKETS",
        "EN_UNPAIRED_QUOTES",
    }

    def __init__(self, language: str = "en-US"):
        """Initialize the grammar checker.

        Args:
            language: Language code for grammar checking.
        """
        self.tool = language_tool_python.LanguageTool(language)

    def check_text(self, text: str, source: str = "", tag: str = "") -> list[GrammarError]:
        """Check text for grammar errors.

        Args:
            text: The text to check.
            source: The source of the text (e.g., 'paragraph', 'heading').
            tag: The HTML tag the text came from.

        Returns:
            A list of GrammarError objects.
        """
        errors = []

        # Skip very short text
        if len(text.strip()) < 5:
            return errors

        matches = self.tool.check(text)

        for match in matches:
            # Skip ignored rules
            if match.rule_id in self.IGNORED_RULES:
                continue

            # Skip spelling errors (let spell checker handle those)
            if match.category == "TYPOS":
                continue

            errors.append(
                GrammarError(
                    message=match.message,
                    context=match.context,
                    suggestions=match.replacements[:5] if match.replacements else [],
                    rule_id=match.rule_id,
                    category=match.category,
                    source=source,
                    tag=tag,
                )
            )

        return errors

    def check_elements(self, elements: list[dict]) -> list[GrammarError]:
        """Check a list of text elements for grammar errors.

        Args:
            elements: List of dictionaries with 'text', 'source', and 'tag' keys.

        Returns:
            A list of GrammarError objects.
        """
        all_errors = []
        for element in elements:
            errors = self.check_text(
                element["text"], source=element.get("source", ""), tag=element.get("tag", "")
            )
            all_errors.extend(errors)
        return all_errors

    def close(self):
        """Close the LanguageTool instance."""
        self.tool.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
