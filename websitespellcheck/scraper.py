"""Web scraping module to fetch and extract text from websites."""

import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class WebScraper:
    """Fetches and extracts text content from websites."""

    EXCLUDED_TAGS = {
        "script",
        "style",
        "meta",
        "link",
        "noscript",
        "header",
        "footer",
        "nav",
        "aside",
        "iframe",
        "svg",
        "canvas",
        "code",
        "pre",
    }

    def __init__(self, timeout: int = 30):
        """Initialize the scraper.

        Args:
            timeout: Request timeout in seconds.
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (compatible; WebsiteSpellCheck/1.0)",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

    def fetch_page(self, url: str) -> str:
        """Fetch HTML content from a URL.

        Args:
            url: The URL to fetch.

        Returns:
            The HTML content as a string.

        Raises:
            requests.RequestException: If the request fails.
        """
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def extract_text(self, html: str) -> list[dict]:
        """Extract text content from HTML.

        Args:
            html: The HTML content to parse.

        Returns:
            A list of dictionaries containing text and metadata.
        """
        soup = BeautifulSoup(html, "lxml")

        # Remove excluded tags
        for tag in soup.find_all(self.EXCLUDED_TAGS):
            tag.decompose()

        text_elements = []

        # Extract title
        title = soup.find("title")
        if title and title.string:
            text_elements.append(
                {"text": title.string.strip(), "source": "title", "tag": "title"}
            )

        # Extract meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            text_elements.append(
                {
                    "text": meta_desc["content"].strip(),
                    "source": "meta description",
                    "tag": "meta",
                }
            )

        # Extract headings
        for level in range(1, 7):
            for heading in soup.find_all(f"h{level}"):
                text = self._get_element_text(heading)
                if text:
                    text_elements.append(
                        {"text": text, "source": f"heading h{level}", "tag": f"h{level}"}
                    )

        # Extract paragraphs
        for para in soup.find_all("p"):
            text = self._get_element_text(para)
            if text:
                text_elements.append({"text": text, "source": "paragraph", "tag": "p"})

        # Extract list items
        for li in soup.find_all("li"):
            text = self._get_element_text(li)
            if text:
                text_elements.append(
                    {"text": text, "source": "list item", "tag": "li"}
                )

        # Extract links text
        for link in soup.find_all("a"):
            text = self._get_element_text(link)
            if text and len(text) > 3:  # Skip very short link text
                text_elements.append({"text": text, "source": "link", "tag": "a"})

        # Extract button text
        for button in soup.find_all("button"):
            text = self._get_element_text(button)
            if text:
                text_elements.append(
                    {"text": text, "source": "button", "tag": "button"}
                )

        # Extract span and div text (only direct text, not nested)
        for tag_name in ["span", "div"]:
            for elem in soup.find_all(tag_name):
                # Only get direct text content
                direct_text = "".join(
                    child.string for child in elem.children if isinstance(child, str)
                ).strip()
                if direct_text and len(direct_text) > 5:
                    text_elements.append(
                        {"text": direct_text, "source": tag_name, "tag": tag_name}
                    )

        return text_elements

    def _get_element_text(self, element) -> str:
        """Get cleaned text from an element.

        Args:
            element: A BeautifulSoup element.

        Returns:
            Cleaned text string.
        """
        text = element.get_text(separator=" ", strip=True)
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def scrape(self, url: str) -> list[dict]:
        """Scrape a URL and extract text content.

        Args:
            url: The URL to scrape.

        Returns:
            A list of text elements with metadata.
        """
        html = self.fetch_page(url)
        return self.extract_text(html)
