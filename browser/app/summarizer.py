from __future__ import annotations
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from urllib.parse import urljoin


def summarize_html(html: str, base_url: str | None = None) -> Dict[str, Any]:
    """
    Produce a JSON summary of the page: title, full text content (not truncated),
    and links with text and href (resolved if possible).
    """
    soup = BeautifulSoup(html, 'lxml')

    title = (soup.title.string.strip() if soup.title and soup.title.string else '')
    # Remove non-visible elements
    for tag in soup(['script', 'style', 'noscript']):
        tag.decompose()
    # Full visible text
    text_full = ' '.join(soup.get_text(separator=' ', strip=True).split())

    links: List[Dict[str, Any]] = []
    for a in soup.find_all('a', href=True):
        href = a.get('href')
        text = ' '.join(a.get_text(separator=' ', strip=True).split())
        resolved = urljoin(base_url or '', href) if base_url else href
        links.append({'text': text, 'href': href, 'resolved': resolved})

    return {
        'title': title,
        'content': text_full,
        # Keep an excerpt for convenience; does not replace full content
        'content_excerpt': text_full[:2000],
        'links': links,
        'base_url': base_url,
    }