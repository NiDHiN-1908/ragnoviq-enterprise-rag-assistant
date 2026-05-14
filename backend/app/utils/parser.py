"""
Utility functions for content parsing and processing.
"""

import logging
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class ContentParser:
    """Parses and cleans HTML content."""

    @staticmethod
    def parse_html(html: str) -> str:
        """
        Parse HTML and extract clean text.
        Removes boilerplate and unnecessary elements.
        """
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "noscript"]):
                script.decompose()

            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.startswith("<!--")):
                comment.extract()

            # Get text
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            return text

        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
            return ""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Additional text cleaning.
        Removes extra whitespace, special characters, etc.
        """
        try:
            # Remove multiple whitespaces
            text = re.sub(r"\s+", " ", text)

            # Remove extra newlines
            text = re.sub(r"\n+", "\n", text)

            # Strip leading/trailing whitespace
            text = text.strip()

            return text

        except Exception as e:
            logger.error(f"Error cleaning text: {str(e)}")
            return text

    @staticmethod
    def extract_metadata(html: str) -> dict:
        """Extract metadata from HTML."""
        try:
            soup = BeautifulSoup(html, "html.parser")
            metadata = {}

            # Title
            if soup.title:
                metadata["title"] = soup.title.string

            # Meta description
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                metadata["description"] = meta_desc.get("content")

            # Keywords
            meta_keywords = soup.find("meta", attrs={"name": "keywords"})
            if meta_keywords:
                metadata["keywords"] = meta_keywords.get("content")

            return metadata

        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {}
