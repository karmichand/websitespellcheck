"""Main website checker module that combines all checks."""

from dataclasses import dataclass, field

from .grammar import GrammarChecker, GrammarError
from .scraper import WebScraper
from .spellcheck import SpellingChecker, SpellingError


@dataclass
class CheckResult:
    """Results from checking a website."""

    url: str
    spelling_errors: list[SpellingError] = field(default_factory=list)
    grammar_errors: list[GrammarError] = field(default_factory=list)
    text_elements_count: int = 0
    error_message: str | None = None

    @property
    def total_errors(self) -> int:
        """Get total number of errors found."""
        return len(self.spelling_errors) + len(self.grammar_errors)

    @property
    def has_errors(self) -> bool:
        """Check if any errors were found."""
        return self.total_errors > 0

    def summary(self) -> str:
        """Generate a summary of the check results."""
        if self.error_message:
            return f"Error checking {self.url}: {self.error_message}"

        lines = [
            f"Website Check Results for: {self.url}",
            "=" * 60,
            f"Text elements analyzed: {self.text_elements_count}",
            f"Spelling errors found: {len(self.spelling_errors)}",
            f"Grammar errors found: {len(self.grammar_errors)}",
            "=" * 60,
        ]

        if self.spelling_errors:
            lines.append("\nSPELLING ERRORS:")
            lines.append("-" * 40)
            for error in self.spelling_errors:
                lines.append(f"  - {error}")
                lines.append(f"    Context: \"{error.context}\"")

        if self.grammar_errors:
            lines.append("\nGRAMMAR ERRORS:")
            lines.append("-" * 40)
            for error in self.grammar_errors:
                lines.append(f"  - {error}")
                lines.append(f"    Context: \"{error.context}\"")

        if not self.has_errors:
            lines.append("\nNo spelling or grammar errors found!")

        return "\n".join(lines)


class WebsiteChecker:
    """Main class to check websites for spelling and grammar errors."""

    def __init__(
        self,
        check_spelling: bool = True,
        check_grammar: bool = True,
        language: str = "en",
    ):
        """Initialize the website checker.

        Args:
            check_spelling: Whether to check spelling.
            check_grammar: Whether to check grammar.
            language: Language code for checking.
        """
        self.scraper = WebScraper()
        self.spelling_checker = SpellingChecker(language=language) if check_spelling else None
        self.grammar_checker = (
            GrammarChecker(language=f"{language}-US" if language == "en" else language)
            if check_grammar
            else None
        )

    def check(self, url: str) -> CheckResult:
        """Check a website for spelling and grammar errors.

        Args:
            url: The URL to check.

        Returns:
            A CheckResult object with the findings.
        """
        result = CheckResult(url=url)

        try:
            # Scrape the website
            text_elements = self.scraper.scrape(url)
            result.text_elements_count = len(text_elements)

            # Check spelling
            if self.spelling_checker:
                result.spelling_errors = self.spelling_checker.check_elements(text_elements)

            # Check grammar
            if self.grammar_checker:
                result.grammar_errors = self.grammar_checker.check_elements(text_elements)

        except Exception as e:
            result.error_message = str(e)

        return result

    def close(self):
        """Clean up resources."""
        if self.grammar_checker:
            self.grammar_checker.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
