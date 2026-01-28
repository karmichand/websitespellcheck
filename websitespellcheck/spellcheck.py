"""Spell checking module."""

import re
from dataclasses import dataclass

from spellchecker import SpellChecker


@dataclass
class SpellingError:
    """Represents a spelling error found in text."""

    word: str
    suggestions: list[str]
    context: str
    source: str
    tag: str

    def __str__(self) -> str:
        suggestions_str = ", ".join(self.suggestions[:3]) if self.suggestions else "none"
        return f"'{self.word}' -> suggestions: [{suggestions_str}] (in {self.source})"


class SpellingChecker:
    """Checks text for spelling errors."""

    # Words to ignore (common web/tech terms, abbreviations, etc.)
    IGNORED_WORDS = {
        "html",
        "css",
        "js",
        "javascript",
        "http",
        "https",
        "www",
        "url",
        "api",
        "json",
        "xml",
        "svg",
        "png",
        "jpg",
        "jpeg",
        "gif",
        "pdf",
        "ui",
        "ux",
        "faq",
        "faqs",
        "blog",
        "login",
        "signup",
        "signin",
        "logout",
        "username",
        "email",
        "gmail",
        "dropdown",
        "navbar",
        "sidebar",
        "checkbox",
        "tooltip",
        "popup",
        "iframe",
        "favicon",
        "homepage",
        "webpage",
        "website",
        "webinar",
        "podcast",
        "linkedin",
        "facebook",
        "twitter",
        "instagram",
        "youtube",
        "github",
        "reddit",
        "tiktok",
        "ios",
        "android",
        "macos",
        "linux",
        "ubuntu",
        "google",
        "microsoft",
        "amazon",
        "netflix",
        "spotify",
        "wifi",
        "bluetooth",
        "vpn",
        "ssl",
        "cdn",
        "seo",
        "crm",
        "saas",
        "paas",
        "iaas",
        "devops",
        "backend",
        "frontend",
        "fullstack",
        "cryptocurrency",
        "bitcoin",
        "ethereum",
        "blockchain",
        "ai",
        "ml",
        "gpt",
        "chatbot",
        "ecommerce",
        "fintech",
        "healthtech",
        "edtech",
        "proptech",
        "startup",
        "startups",
        "scalable",
        "clickable",
        "downloadable",
        "unsubscribe",
        "retweet",
        "hashtag",
        "livestream",
        "permalink",
        "metadata",
    }

    def __init__(self, language: str = "en"):
        """Initialize the spell checker.

        Args:
            language: Language code for spell checking.
        """
        self.checker = SpellChecker(language=language)
        self.checker.word_frequency.load_words(self.IGNORED_WORDS)

    def check_text(self, text: str, source: str = "", tag: str = "") -> list[SpellingError]:
        """Check text for spelling errors.

        Args:
            text: The text to check.
            source: The source of the text (e.g., 'paragraph', 'heading').
            tag: The HTML tag the text came from.

        Returns:
            A list of SpellingError objects.
        """
        errors = []

        # Extract words from text
        words = self._extract_words(text)

        # Find misspelled words
        misspelled = self.checker.unknown(words)

        for word in misspelled:
            # Skip if word looks like a code/technical term
            if self._should_ignore(word):
                continue

            suggestions = list(self.checker.candidates(word) or [])
            # Sort by likelihood
            suggestions = sorted(
                suggestions, key=lambda x: self.checker.word_frequency[x], reverse=True
            )[:5]

            # Create context (surrounding text)
            context = self._get_context(text, word)

            errors.append(
                SpellingError(
                    word=word,
                    suggestions=suggestions,
                    context=context,
                    source=source,
                    tag=tag,
                )
            )

        return errors

    def _extract_words(self, text: str) -> list[str]:
        """Extract words from text for spell checking.

        Args:
            text: The text to extract words from.

        Returns:
            A list of words.
        """
        # Split on non-word characters, keeping only alphabetic words
        words = re.findall(r"\b[a-zA-Z]+\b", text)
        # Convert to lowercase for checking
        return [word.lower() for word in words if len(word) > 1]

    def _should_ignore(self, word: str) -> bool:
        """Check if a word should be ignored.

        Args:
            word: The word to check.

        Returns:
            True if the word should be ignored.
        """
        word_lower = word.lower()

        # Skip very short words
        if len(word_lower) <= 2:
            return True

        # Skip words that look like abbreviations or codes
        if word_lower.isupper():
            return True

        # Skip words with numbers
        if any(c.isdigit() for c in word):
            return True

        # Skip camelCase or PascalCase words (likely code)
        if re.match(r"^[a-z]+[A-Z]", word):
            return True

        # Skip words ending in common suffixes that may be valid
        if word_lower.endswith(("ify", "ize", "ization")):
            return True

        return False

    def _get_context(self, text: str, word: str, context_size: int = 30) -> str:
        """Get context around a word in text.

        Args:
            text: The full text.
            word: The word to get context for.
            context_size: Number of characters on each side.

        Returns:
            The context string.
        """
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            start = max(0, match.start() - context_size)
            end = min(len(text), match.end() + context_size)
            context = text[start:end]
            if start > 0:
                context = "..." + context
            if end < len(text):
                context = context + "..."
            return context
        return text[:60] + "..." if len(text) > 60 else text

    def check_elements(self, elements: list[dict]) -> list[SpellingError]:
        """Check a list of text elements for spelling errors.

        Args:
            elements: List of dictionaries with 'text', 'source', and 'tag' keys.

        Returns:
            A list of SpellingError objects.
        """
        all_errors = []
        for element in elements:
            errors = self.check_text(
                element["text"], source=element.get("source", ""), tag=element.get("tag", "")
            )
            all_errors.extend(errors)
        return all_errors
