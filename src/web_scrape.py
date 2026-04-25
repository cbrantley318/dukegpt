# Scraping helpers

import requests
import trafilatura
import time
from urllib.parse import urljoin, urlparse
from collections import deque
from pathlib import Path
import os, json

# Most content in this file generated with AI, using Claude Sonnet 4.6


HEADERS = {'User-Agent': 'Mozilla/5.0 (Duke CS372 Research Project)'}


def scrape_url(url: str) -> str | None:
    """Fetch a URL and extract clean text using trafilatura."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        text = trafilatura.extract(
            response.text,
            include_tables=True,
            include_links=False,
            no_fallback=False
        )
        return text
    except Exception as e:
        print(f'    Failed {url}: {e}')
        return None


def scrape_urls(url_list: list[str], label: str) -> list[dict]:
    """Scrape a list of URLs and return list of {text, source} dicts."""
    docs = []
    for url in url_list:
        print(f'  Scraping: {url}')
        text = scrape_url(url)
        if text and len(text.strip()) > 200:
            docs.append({'text': text.strip(), 'source': url, 'type': label})
            print(f'     {len(text)} chars')
        time.sleep(0.5)  # be polite
    return docs


def _extract_links(html: str, base_url: str, allowed_domain: str) -> list[str]:
    """
    Extract same-domain links from raw HTML using trafilatura's link extraction.
    Falls back to a lightweight regex scan if trafilatura yields nothing.
    """
    from trafilatura.utils import load_html
    # from trafilatura.external import extract_links  # trafilatura ≥ 1.6

    links = set()
    base_parsed = urlparse(base_url)

    try:
        tree = load_html(html)
        if tree is not None:
            for a in tree.iter('a'):
                href = a.get('href', '')
                if href:
                    abs_url = urljoin(base_url, href.split('#')[0])  # drop fragments
                    parsed = urlparse(abs_url)
                    # print(parsed)
                    if parsed.scheme in ('http', 'https') and (parsed.netloc == allowed_domain or parsed.netloc.endswith("." + allowed_domain)):
                        links.add(abs_url)
    except Exception:
        # Fallback: crude regex
        print("PERFORMING fallback")
        import re
        for href in re.findall(r'href=["\']([^"\']+)["\']', html):
            abs_url = urljoin(base_url, href.split('#')[0])
            parsed = urlparse(abs_url)
            print("LINK")
            if parsed.scheme in ('http', 'https') and (parsed.netloc == allowed_domain or parsed.netloc.endswith(allowed_domain)):
                links.add(abs_url)

    return list(links)


def crawl_site(
    seed_url: str,
    label: str,
    *,
    max_pages: int = 50,
    max_depth: int = 3,
    delay: float = 0.5,
    url_filter: callable = None,
) -> list[dict]:
    """
    BFS crawl starting from seed_url, staying within the same domain.

    Args:
        seed_url:    The starting URL.
        label:       'type' tag applied to every returned doc.
        max_pages:   Hard cap on total pages fetched (default 50).
        max_depth:   Maximum link depth from the seed (default 3).
        delay:       Polite pause between requests in seconds (default 0.5).
        url_filter:  Optional callable(url: str) -> bool; return False to skip a URL.

    Returns:
        List of {text, source, type, depth} dicts (only pages with >200 chars of text).
    """
    allowed_domain = urlparse(seed_url).netloc
    allowed_domain = "duke.edu"
    print("Crawling allowed from " + allowed_domain)
    visited: set[str] = set()
    queue: deque[tuple[str, int]] = deque([(seed_url, 0)])  # (url, depth)
    docs: list[dict] = []

    print(f'  Crawling {seed_url}  [max_pages={max_pages}, max_depth={max_depth}]')

    while queue and len(visited) < max_pages:
        url, depth = queue.popleft()

        if url in visited:
            continue
        if depth > max_depth:
            continue
        if url_filter and not url_filter(url):
            print(f'    Skipped (filter): {url}')
            continue

        visited.add(url)
        print(f'  [depth={depth}] Fetching: {url}')

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            raw_html = response.text
        except Exception as e:
            print(f'    Failed {url}: {e}')
            time.sleep(delay)
            continue

        # Extract clean text
        text = trafilatura.extract(
            raw_html,
            include_tables=True,
            include_links=False,
            no_fallback=False,
        )
        if text and len(text.strip()) > 200:
            docs.append({
                'text': text.strip(),
                'source': url,
                'type': label,
                'depth': depth,
            })
            print(f'     {len(text)} chars')

        # Discover child links (only if we can go deeper)
        if depth < max_depth:
            child_links = _extract_links(raw_html, url, allowed_domain)
            new_links = [l for l in child_links if l not in visited]
            print(f'    Found {len(new_links)} new links')
            for link in new_links:
                queue.append((link, depth + 1))

        time.sleep(delay)

    print(f'  Crawl complete: {len(docs)} docs from {len(visited)} pages visited')
    return docs



def unpack_raw_docs(docs: list, out_dir: Path):
    """Save each {text, source, type} doc as a .txt grouped by type."""
    manifest = []
    for i, doc in enumerate(docs):
        doc_type = doc.get("type", "unknown").replace(" ", "_")
        type_dir = out_dir / doc_type
        type_dir.mkdir(parents=True, exist_ok=True)
        fp = type_dir / f"doc_{i:04d}.txt"
        fp.write_text(doc.get("text", ""), encoding="utf-8")
        manifest.append({"index": i, "file": str(fp), "source": doc.get("source", ""), "type": doc_type})
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"  raw_docs: {len(docs)} docs → {out_dir}/")


# scrapes the listed URL's and saves them as txt's
if __name__ == '__main__':
    # Source 1: Duke public web pages
    # Focused on info students actually ask about — crawled from top-level domains

    SAVE_DIR = Path.cwd()


    DUKE_SEEDS = [
        ('https://registrar.duke.edu/',              'registrar',    30, 3),
        ('https://students.duke.edu/',               'students',     30, 3),
        ('https://financialaid.duke.edu/',           'financial_aid',30, 3),
        ('https://housing.duke.edu/',                'housing',      30, 3),
        ('https://studentaffairs.duke.edu/',         'student_affairs', 40, 3),
        ('https://library.duke.edu/',                'library',      20, 3),
        ('https://dining.duke.edu/',                 'dining',      20, 3),
        ('https://duke.edu/',                        'duke',      30, 4),
    ]

    # DUKE_SEEDS = [      #dummy test case
    #     ('https://dining.duke.edu/',                 'dining',      5, 3),
    # ]

    print('Crawling Duke web domains...')
    web_docs = []

    for seed_url, label, max_pages, max_depth in DUKE_SEEDS:
        print(f'\n--- {label} ---')
        docs = crawl_site(
            seed_url,
            label=label,
            max_pages=max_pages,
            max_depth=max_depth,
            delay=0.5,
        )
        web_docs.extend(docs)

    print(f'\nCollected {len(web_docs)} web pages total')
    out_dir = Path(SAVE_DIR) / 'new_web_scrapes'
    unpack_raw_docs(web_docs, out_dir)

