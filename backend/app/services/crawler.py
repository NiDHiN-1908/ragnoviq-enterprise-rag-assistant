"""
Web scraping and crawling service.
Handles website crawling with depth control and dynamic content.
"""

import logging
from typing import List, Set, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class WebCrawler:
    """Handles website crawling and content extraction."""

    def __init__(self):
        self.session = self._create_session()
        self.visited_urls: Set[str] = set()
        self.max_depth = settings.max_crawl_depth
        self.max_pages = settings.max_pages_per_domain
        self.timeout = settings.request_timeout

    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy and modern browser headers."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        return session

    def _is_valid_url(self, url: str, base_domain: str) -> bool:
        """Check if URL is valid and belongs to same domain."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ["http", "https"]:
                return False
            url_domain = parsed.netloc.lower()
            return url_domain == base_domain or url_domain.endswith(f".{base_domain}")
        except Exception:
            return False

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and trailing slashes."""
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{parsed.query}".rstrip("?").rstrip("/")
        return normalized

    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all internal links from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        base_domain = urlparse(base_url).netloc.lower()
        links = []

        for link in soup.find_all("a", href=True):
            url = link["href"].strip()
            if not url or url.startswith("#") or url.startswith("javascript:"):
                continue

            absolute_url = urljoin(base_url, url)
            if self._is_valid_url(absolute_url, base_domain):
                normalized = self._normalize_url(absolute_url)
                if normalized not in self.visited_urls:
                    links.append(normalized)

        return links

    def crawl(self, start_url: str) -> List[dict]:
        """
        Crawl website recursively.
        
        Returns:
            List of crawled pages with URL and content
        """
        if not start_url.startswith("http://") and not start_url.startswith("https://"):
            start_url = "https://" + start_url

        self.visited_urls.clear()
        pages = []
        to_crawl = [start_url]
        base_domain = urlparse(start_url).netloc.lower()

        while to_crawl and len(pages) < self.max_pages:
            url = to_crawl.pop(0)

            if url in self.visited_urls:
                continue

            try:
                logger.info(f"Crawling: {url}")
                try:
                    response = self.session.get(
                        url, timeout=self.timeout, allow_redirects=True
                    )
                except requests.exceptions.SSLError:
                    logger.warning(f"SSL verification failed for {url}. Retrying with verify=False")
                    response = self.session.get(
                        url, timeout=self.timeout, allow_redirects=True, verify=False
                    )

                response.raise_for_status()
                self.visited_urls.add(url)

                # Parse content
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Extract title
                title = None
                if soup.title and soup.title.string:
                    title = soup.title.string.strip()
                if not title:
                    title = base_domain.replace("www.", "").capitalize()

                # Extract main content
                content = self._extract_text(soup)

                if content.strip():
                    pages.append({
                        "url": url,
                        "title": title,
                        "content": response.text,
                        "content_text": content,
                    })

                # Extract and queue new links
                links = self._extract_links(response.text, url)
                for l in links[:15]:
                    if l not in to_crawl:
                        to_crawl.append(l)

            except requests.RequestException as e:
                logger.warning(f"Failed to crawl {url}: {str(e)}")
                self.visited_urls.add(url)
            except Exception as e:
                logger.error(f"Error crawling {url}: {str(e)}")
                self.visited_urls.add(url)

        logger.info(f"Crawl complete. Visited {len(self.visited_urls)} pages, collected {len(pages)} pages.")
        return pages

    @staticmethod
    def _extract_text(soup: BeautifulSoup) -> str:
        """
        Extract clean text from soup.
        Remove scripts, styles, and navigation elements.
        """
        # Remove script and style elements
        for element in soup(["script", "style", "noscript", "svg", "iframe"]):
            element.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)

        return text
