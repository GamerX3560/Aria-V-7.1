#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  ARIA Multimodal Deep Research Agent v4                      ║
║  Personal data hooking • Multimodal OCR ingestion            ║
║  uvloop-accelerated • CJK-safe rich PDF dossiers             ║
║  Crawls GitHub, Reddit, Arch Wiki, Awesome Lists, HN, etc.  ║
╚══════════════════════════════════════════════════════════════╝

Usage:
    python3 deep_research_v4.py "build me a resume" --type personal --level 3
    python3 deep_research_v4.py "LLM agentic architectures" --type tech --level 2
    python3 deep_research_v4.py --categories-file categories.json --level 3
    python3 deep_research_v4.py --full
"""
import asyncio
import json
import sys
import os
import re
import time
import logging
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse, quote_plus

import httpx
from bs4 import BeautifulSoup
from openai import AsyncOpenAI
import markdown
from weasyprint import HTML, CSS
import trafilatura
try:
    from scrapling import DynamicFetcher
    has_scrapling = True
except ImportError:
    has_scrapling = False

_scrapling_fetcher = None
import uvloop
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
try:
    from ddgs import DDGS  # New package name (v9+)
except ImportError:
    from duckduckgo_search import DDGS  # Fallback for older installs

# uvloop is activated at the entry point via uvloop.run() to avoid deprecation warnings

# ─── Config ───────────────────────────────────────────
NVIDIA_API_KEY = "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"
BASE_URL = "https://integrate.api.nvidia.com/v1"
MODEL = "qwen/qwen2.5-coder-32b-instruct"
RESEARCH_DIR = Path.home() / "aria" / "research"
RESEARCH_DIR.mkdir(exist_ok=True)

# How many URLs to crawl PER CATEGORY (adjust for depth vs speed)
DEFAULT_MAX_URLS_PER_CATEGORY = 300

SYSTEM_SPECS = """
Target System (HARD REQUIREMENTS — tools MUST work on this):
- OS: Arch Linux (Hyprland/Wayland) — NOT Ubuntu, NOT Fedora
- CPU: AMD Ryzen 5 3400G (4 cores / 8 threads, Zen+ architecture)
- GPU: AMD RX 6600 8GB VRAM (RDNA2) — ROCm compatible, NO NVIDIA/CUDA
- RAM: 16GB DDR4
- Shell: zsh | Terminal: kitty (supports Kitty graphics protocol)
- Python: 3.14 | Node.js available
- Package Managers: pacman (official), yay (AUR helper)
- Display Server: Wayland via Hyprland compositor
- Audio: PipeWire
- Phone: Rooted Android device connected via ADB
- Browser: Brave
"""

log = logging.getLogger("DeepResearch")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

aclient = AsyncOpenAI(api_key=NVIDIA_API_KEY, base_url=BASE_URL)

# GitHub token for authenticated API (30 req/min vs 10 unauthenticated)
_GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

GITHUB_HEADERS = {**HEADERS}
if _GITHUB_TOKEN and (_GITHUB_TOKEN.startswith("ghp_") or _GITHUB_TOKEN.startswith("gho_") or _GITHUB_TOKEN.startswith("github_pat_")):
    GITHUB_HEADERS["Authorization"] = f"Bearer {_GITHUB_TOKEN}"
    log.info("GitHub: authenticated (30 req/min)")

# Track all visited URLs globally to avoid redundant fetches
_visited_urls = set()
_url_counter = 0


# ═══════════════════════════════════════════════════════
# SEARCH ENGINE SCRAPERS
# ═══════════════════════════════════════════════════════

async def search_duckduckgo(query: str, max_pages: int = 5) -> list[str]:
    """Search DuckDuckGo via the duckduckgo-search library (no captcha issues)."""
    urls = []
    # Truncate overly long queries
    words = query.split()
    if len(words) > 10:
        query = " ".join(words[:10])
    
    max_results = max_pages * 15  # ~15 results per "page"
    
    try:
        def _do_search():
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    href = r.get("href", "")
                    if href and href.startswith("http") and href not in _visited_urls:
                        results.append(href)
            return results
        
        urls = await asyncio.to_thread(_do_search)
        log.info(f"    DDG library: {len(urls)} results for '{query[:60]}'")
    except Exception as e:
        log.warning(f"DDG search failed: {e}")
        # Fallback: try HTML scraping as backup
        try:
            async with httpx.AsyncClient(timeout=20, headers=HEADERS, follow_redirects=True) as client:
                for page in range(min(max_pages, 3)):
                    params = {"q": query}
                    if page > 0:
                        params["s"] = str(page * 30)
                    resp = await client.get("https://html.duckduckgo.com/html/", params=params)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "html.parser")
                        for link in soup.select("a.result__a"):
                            href = link.get("href", "")
                            if href.startswith("http") and href not in _visited_urls:
                                urls.append(href)
                    await asyncio.sleep(2)
        except Exception as e2:
            log.warning(f"DDG HTML fallback also failed: {e2}")
    
    # Small delay between DDG calls to avoid rate-limiting
    await asyncio.sleep(1.5)
    return urls


async def search_github_api(query: str, max_pages: int = 4, min_year: int = 2023) -> list[dict]:
    """Search GitHub REST API with pagination and date filtering.
    Uses best-match sorting (default) to find relevant niche repos, not just most popular.
    """
    repos = []
    # Truncate long queries — GitHub search breaks with 10+ words
    words = query.split()
    if len(words) > 8:
        query = " ".join(words[:8])
    
    async with httpx.AsyncClient(timeout=15, headers=GITHUB_HEADERS) as client:
        for page in range(1, max_pages + 1):
            try:
                # Use default sort (best-match) — NOT sort=updated which returns mega-popular generic repos
                # Also add stars filter to avoid mega-repos that pollute results
                full_query = f"{query} pushed:>{min_year}-01-01 stars:<100000"
                url = f"https://api.github.com/search/repositories?q={quote_plus(full_query)}&per_page=30&page={page}"
                resp = await client.get(url)
                if resp.status_code != 200:
                    if resp.status_code == 403:
                        log.warning("GitHub rate limit hit, waiting 60s...")
                        await asyncio.sleep(60)
                        continue
                    break
                data = resp.json()
                for repo in data.get("items", []):
                    repos.append({
                        "name": repo["full_name"],
                        "url": repo["html_url"],
                        "stars": repo["stargazers_count"],
                        "forks": repo.get("forks_count", 0),
                        "description": repo.get("description", "") or "",
                        "language": repo.get("language", "Unknown"),
                        "updated": repo.get("updated_at", ""),
                        "topics": repo.get("topics", []),
                        "license": (repo.get("license") or {}).get("spdx_id", "Unknown"),
                        "open_issues": repo.get("open_issues_count", 0),
                    })
                await asyncio.sleep(2)
            except Exception as e:
                log.warning(f"GitHub API page {page} failed: {e}")
                break
    return repos


async def search_github_topics(topic: str) -> list[dict]:
    """Search GitHub by topic tag."""
    repos = []
    try:
        async with httpx.AsyncClient(timeout=15, headers={**HEADERS, "Accept": "application/vnd.github.mercy-preview+json"}) as client:
            url = f"https://api.github.com/search/repositories?q=topic:{quote_plus(topic)}&sort=stars&order=desc&per_page=30"
            resp = await client.get(url)
            if resp.status_code == 200:
                for repo in resp.json().get("items", []):
                    repos.append({
                        "name": repo["full_name"],
                        "url": repo["html_url"],
                        "stars": repo["stargazers_count"],
                        "description": repo.get("description", "") or "",
                        "language": repo.get("language", "Unknown"),
                        "updated": repo.get("updated_at", ""),
                    })
    except Exception as e:
        log.warning(f"GitHub topic search failed: {e}")
    return repos


# ═══════════════════════════════════════════════════════
# PERSONAL DATA HOOKS & MULTIMODAL INGESTION
# ═══════════════════════════════════════════════════════

async def ingest_personal_data() -> str:
    """Scan ~/.personal_data/ for local files (PDFs, Images, TXT) to augment research context."""
    personal_dir = Path.home() / ".personal_data"
    if not personal_dir.exists():
        return ""
    
    log.info(f"  [Personal Hook] Scanning {personal_dir} for personal data...")
    compiled_personal_text = []
    
    for file_path in personal_dir.glob("**/*"):
        if not file_path.is_file():
            continue
            
        ext = file_path.suffix.lower()
        if ext in ['.txt', '.md', '.json', '.csv']:
            try:
                text = await asyncio.to_thread(file_path.read_text, encoding='utf-8')
                compiled_personal_text.append(f"--- Document: {file_path.name} ---\n{text[:5000]}")
                log.info(f"    Loaded text: {file_path.name}")
            except Exception as e:
                log.warning(f"    Failed text {file_path.name}: {e}")
                
        elif ext == '.pdf':
            try:
                def read_pdf(p):
                    with fitz.open(p) as doc:
                        return "\n".join(page.get_text() for page in doc)
                text = await asyncio.to_thread(read_pdf, str(file_path))
                compiled_personal_text.append(f"--- PDF Document: {file_path.name} ---\n{text[:5000]}")
                log.info(f"    Loaded PDF: {file_path.name}")
            except Exception as e:
                log.warning(f"    Failed PDF {file_path.name}: {e}")
                
        elif ext in ['.png', '.jpg', '.jpeg', '.webp']:
            try:
                def read_image(p):
                    return pytesseract.image_to_string(Image.open(p))
                text = await asyncio.to_thread(read_image, str(file_path))
                compiled_personal_text.append(f"--- Image/OCR: {file_path.name} ---\n{text[:3000]}")
                log.info(f"    Loaded Image OCR: {file_path.name}")
            except Exception as e:
                log.warning(f"    Failed Image {file_path.name}: {e}")
                
    if compiled_personal_text:
        log.info(f"  [Personal Hook] Ingested {len(compiled_personal_text)} personal documents.")
        return "\n\n".join(compiled_personal_text)
    return ""


# ═══════════════════════════════════════════════════════
# WEB SCRAPERS
async def scrape_page(url: str, headless: bool = True, extract_links: bool = False) -> tuple[str, list[str]]:
    """Extract text and links from a URL. Uses StealthyFetcher to bypass anti-bot, then Trafilatura."""
    global _url_counter
    
    if url in _visited_urls:
        return "", []
    _visited_urls.add(url)
    _url_counter += 1
    
    if _url_counter % 50 == 0:
        log.info(f"  ... crawled {_url_counter} URLs so far")
    
    links = []
    html_content = ""
    
    try:
        global _scrapling_fetcher
        if has_scrapling:
            if _scrapling_fetcher is None:
                _scrapling_fetcher = DynamicFetcher(headless=True)
            response = await _scrapling_fetcher.async_fetch(url)
            if response and response.body:
                html_content = response.body.decode("utf-8", errors="ignore")
        else:
            async with httpx.AsyncClient(timeout=12, headers=HEADERS, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", ""):
                    html_content = resp.text
                    
        if not html_content:
            return "", []

        text = await asyncio.to_thread(trafilatura.extract, html_content, include_links=True)
        if text and len(text) > 200:
            cleaned = re.sub(r'\n+', '\n', text).strip()
            return cleaned[:10000], links[:50]

        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        
        if extract_links:
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http"):
                    links.append(href)
                elif href.startswith("/"):
                    base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                    links.append(urljoin(base, href))
        
        return text[:10000], links[:50]
    except Exception as e:
        return "", []

async def fetch_github_readme(repo_fullname: str) -> str:
    """Fetch README.md from a GitHub repo."""
    for branch in ["main", "master"]:
        url = f"https://raw.githubusercontent.com/{repo_fullname}/{branch}/README.md"
        try:
            async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    _visited_urls.add(url)
                    return resp.text[:8000]
        except Exception as e:
            pass
    return ""


async def scrape_arch_wiki(topic: str) -> str:
    """Search and scrape the Arch Wiki for a topic."""
    search_url = f"https://wiki.archlinux.org/index.php?search={quote_plus(topic)}&title=Special%3ASearch"
    text, links = await scrape_page(search_url, extract_links=True)
    
    # Follow the first 3 wiki result links
    wiki_texts = [text[:3000]]
    relevant_links = [l for l in links if "wiki.archlinux.org" in l and "Special:" not in l][:3]
    for link in relevant_links:
        page_text, _ = await scrape_page(link)
        if page_text:
            wiki_texts.append(page_text[:3000])
        await asyncio.sleep(0.5)
    
    return "\
\
---\
\
".join(wiki_texts)


async def scrape_reddit_search(query: str) -> list[dict]:
    """Search Reddit (old.reddit.com) and extract post content."""
    posts = []
    encoded = quote_plus(query)
    urls_to_try = [
        f"https://old.reddit.com/search/?q={encoded}&sort=relevance&t=year",
        f"https://old.reddit.com/r/linux/search/?q={encoded}&restrict_sr=on&sort=top&t=year",
        f"https://old.reddit.com/r/archlinux/search/?q={encoded}&restrict_sr=on&sort=top&t=year",
        f"https://old.reddit.com/r/hyprland/search/?q={encoded}&restrict_sr=on&sort=top&t=all",
        f"https://old.reddit.com/r/commandline/search/?q={encoded}&restrict_sr=on&sort=top&t=year",
    ]
    
    for url in urls_to_try:
        text, links = await scrape_page(url, extract_links=True)
        if text:
            posts.append({"url": url, "content": text[:4000]})
        
        # Follow first 5 thread links
        thread_links = [l for l in links if "/comments/" in l][:5]
        for tl in thread_links:
            thread_text, _ = await scrape_page(tl)
            if thread_text and len(thread_text) > 200:
                posts.append({"url": tl, "content": thread_text[:4000]})
            await asyncio.sleep(0.5)
        
        await asyncio.sleep(1)
    
    return posts


async def discover_awesome_lists(category: str) -> list[dict]:
    """Find and parse GitHub 'awesome' lists relevant to the category."""
    awesome_repos = []
    
    queries = [
        f"awesome {category}",
        f"awesome linux {category}",
        f"awesome wayland",
    ]
    
    for q in queries:
        repos = await search_github_api(q, max_pages=1)
        for repo in repos:
            name = repo["name"].lower()
            desc = repo["description"].lower()
            if "awesome" in name or "awesome" in desc or "curated" in desc:
                awesome_repos.append(repo)
        await asyncio.sleep(2)
    
    # Parse each awesome list README for tool links
    discovered_tools = []
    for repo in awesome_repos[:5]:
        readme = await fetch_github_readme(repo["name"])
        if readme:
            # Extract GitHub links from the README
            gh_links = re.findall(r'https?://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+', readme)
            for link in gh_links[:30]:
                discovered_tools.append({
                    "url": link,
                    "source": f"awesome-list:{repo['name']}",
                })
        await asyncio.sleep(1)
    
    return discovered_tools


# ═══════════════════════════════════════════════════════
# LLM ANALYSIS
# ═══════════════════════════════════════════════════════

async def llm_analyze(prompt: str, max_tokens: int = 4096) -> str:
    """Send a prompt to the Nvidia LLM."""
    try:
        completion = await aclient.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=max_tokens,
        )
        if completion.choices and completion.choices[0].message.content:
            return completion.choices[0].message.content.strip()
    except Exception as e:
        log.error(f"LLM analysis failed: {e}")
    return ""


async def llm_extract_tools_from_text(text: str, category: str) -> list[str]:
    """Use the LLM to extract tool names from raw web text."""
    prompt = f"""From the following web page text about "{category}", extract ALL mentioned software tools, libraries, or projects. 
Return ONLY a JSON array of tool names, nothing else. Example: ["tool1", "tool2", "tool3"]
If no tools are found, return [].

TEXT:
{text[:4000]}"""
    
    response = await llm_analyze(prompt, max_tokens=500)
    try:
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return []


# ═══════════════════════════════════════════════════════
# MAIN RESEARCH PIPELINE
# ═══════════════════════════════════════════════════════


async def condense_query(raw_prompt: str) -> dict:
    """Use LLM to break a long user prompt into focused, short search queries.
    
    The key insight: search engines need SPECIFIC tool/library names, not generic topic phrases.
    Generic queries like 'AI desktop automation' return mega-popular unrelated repos.
    Specific queries like 'browser-use python playwright' find actual niche tools.
    """
    if len(raw_prompt.split()) <= 6:
        # Short enough already — use as-is
        core = raw_prompt
        return {
            "core": core,
            "github_queries": [f"{core} python", f"{core} tool", f"best {core} linux"],
            "ddg_queries": [f"best {core} tools linux 2024", f"{core} open source", f"site:github.com {core}"],
            "reddit_query": core,
        }
    
    prompt = f"""You are a search query expert. Convert this research topic into SPECIFIC, TARGETED search queries.

CRITICAL RULES:
1. Include SPECIFIC tool/library names you know about (e.g., "pyautogui", "browser-use", "ydotool")
2. GitHub queries should find NICHE, specialized repos — NOT mega-popular generic ones
3. DuckDuckGo queries should use "best X for Y" or "X vs Y" patterns to find comparison articles
4. Each query must be MAX 6 words
5. Include at least one query with "github" or "awesome-list" prefix

Return JSON with:
- "core": Main topic in 2-4 words (used for Reddit/Wiki/HN searches)  
- "github_queries": 6 SPECIFIC GitHub search queries targeting actual tools/libraries in this space
- "ddg_queries": 5 varied DuckDuckGo queries (comparisons, tutorials, alternatives, reviews)
- "reddit_query": 1 Reddit search query (3-5 words)

Topic: "{raw_prompt}"

Return ONLY valid JSON, no markdown."""

    response = await llm_analyze(prompt, max_tokens=600)
    try:
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            if "core" in parsed:
                log.info(f"  [Query Condenser] Core topic: {parsed['core']}")
                log.info(f"  [Query Condenser] GitHub queries: {parsed.get('github_queries', [])}")
                log.info(f"  [Query Condenser] DDG queries: {parsed.get('ddg_queries', [])}")
                return parsed
    except Exception as e:
        log.warning(f"  Query condenser failed: {e}, using fallback")
    
    # Fallback: take first 4 words
    words = raw_prompt.split()[:4]
    core = " ".join(words)
    return {
        "core": core,
        "github_queries": [f"{core} python", f"{core} tool", f"best {core}", f"{core} library", f"{core} framework", f"awesome {core}"],
        "ddg_queries": [f"best {core} tools 2024", f"{core} python library", f"site:github.com {core}", f"{core} comparison review", f"{core} alternative open source"],
        "reddit_query": core,
    }

async def research_category(category: str, description: str, max_urls: int = DEFAULT_MAX_URLS_PER_CATEGORY, pages: int = 3, topic_type: str = "general", min_year: int = 2023) -> dict:
    """Ultra-deep research for a single capability category."""
    global _url_counter
    _url_counter = 0
    _visited_urls.clear()
    
    log.info(f"\\n{'═'*60}")
    log.info(f"RESEARCHING: {category}")
    log.info(f"Target: crawl up to {max_urls} URLs")
    log.info(f"{'═'*60}")
    
    start = time.time()
    
    findings = {
        "category": category,
        "description": description,
        "timestamp": datetime.now().isoformat(),
        "github_repos": [],
        "awesome_list_tools": [],
        "web_sources": [],
        "reddit_discussions": [],
        "arch_wiki": "",
        "all_tool_names": set(),
        "total_urls_crawled": 0,
        "llm_deep_analysis": "",
        "llm_comparison_matrix": "",
        "llm_final_recommendations": "",
    }
    
    reddit_posts = []

    # ─── Stage 0: Personal Context Hooking ───────────────
    personal_context = await ingest_personal_data()
    findings["personal_context_found"] = bool(personal_context)

    # ─── Stage 1: GitHub Deep Dive ───────────────────────
    log.info("  Stage 1/6: GitHub Deep Dive...")
    
    # Condense long queries via LLM for focused search
    condensed = await condense_query(category)
    search_core = condensed["core"]
    
    if topic_type in ["tech", "software", "security"]:
        github_queries = condensed.get("github_queries", [
            f"{search_core} python linux",
            f"{search_core} CLI tool",
            f"best {search_core} terminal",
            f"{search_core} local offline",
        ])
    elif topic_type in ["science", "business", "personal"]:
        github_queries = [f"{search_core} templates code", f"{search_core} data pipeline"]
    else:
        github_queries = [search_core]
    
    all_repos = []
    for q in github_queries:
        repos = await search_github_api(q, max_pages=2)
        all_repos.extend(repos)
        await asyncio.sleep(2)
    
    # Also search by topic tags — use combined terms, not generic single words
    # Single tags like 'ai' or 'automation' return mega-popular unrelated repos
    core_words = search_core.lower().split()
    if len(core_words) >= 2:
        # Use pairs/triples of words as topics, not single words
        topic_tags = [
            "-".join(core_words[:2]),  # e.g. "desktop-automation"
            "-".join(core_words[:3]) if len(core_words) >= 3 else "-".join(core_words),  # e.g. "ai-desktop-automation"
        ]
    else:
        topic_tags = [core_words[0]] if core_words else []
    
    core_lower = search_core.lower()
    for tag in topic_tags[:2]:
        repos = await search_github_topics(tag)
        # Filter: only keep repos whose description mentions at least one core keyword
        for r in repos:
            desc = (r.get("description", "") or "").lower()
            name = (r.get("name", "") or "").lower()
            # Check if at least one core word appears in description or name
            if any(w in desc or w in name for w in core_words if len(w) > 2):
                all_repos.append(r)
        await asyncio.sleep(2)
    
    # Deduplicate
    seen_repos = set()
    unique_repos = []
    for r in all_repos:
        if r["name"] not in seen_repos:
            seen_repos.add(r["name"])
            unique_repos.append(r)
    
    unique_repos.sort(key=lambda x: x["stars"], reverse=True)
    log.info(f"  Found {len(unique_repos)} unique GitHub repos")
    
    # Fetch READMEs for all repos (up to 25)
    for repo in unique_repos[:25]:
        readme = await fetch_github_readme(repo["name"])
        repo["readme_excerpt"] = readme[:4000]
        findings["all_tool_names"].add(repo["name"].split("/")[-1])
        await asyncio.sleep(0.3)
    
    findings["github_repos"] = unique_repos[:25]

    # ─── Stage 2: Awesome Lists Discovery ───────────────
    if topic_type in ["tech", "software", "security"]:
        log.info("  Stage 2/6: Awesome Lists Discovery...")
        awesome_tools = await discover_awesome_lists(search_core)
        findings["awesome_list_tools"] = awesome_tools
        log.info(f"  Found {len(awesome_tools)} tools from awesome lists")
        
        for tool in awesome_tools[:20]:
            repo_match = re.match(r'https?://github\.com/([^/]+/[^/]+)', tool["url"])
            if repo_match:
                repo_name = repo_match.group(1)
                if repo_name not in seen_repos:
                    readme = await fetch_github_readme(repo_name)
                    if readme:
                        unique_repos.append({
                            "name": repo_name, "url": tool["url"],
                            "stars": 0, "description": "", "language": "?",
                            "readme_excerpt": readme[:3000], "source": tool["source"],
                        })
                        seen_repos.add(repo_name)
                        findings["all_tool_names"].add(repo_name.split("/")[-1])
                await asyncio.sleep(0.3)
    else:
        log.info("  Stage 2/6: Awesome Lists Discovery (Skipped for non-tech topcs)...")

    # ─── Stage 3: DuckDuckGo Deep Crawl ──────────────────
    log.info("  Stage 3/6: DuckDuckGo Multi-Page Crawl...")
    
    if topic_type == "tech":
        ddg_queries = condensed.get("ddg_queries", [
            f"best {search_core} tools linux {min_year}",
            f"{search_core} python library",
            f"site:github.com {search_core} {min_year}",
        ])
    elif topic_type == "science":
        ddg_queries = [
            f"{search_core} research papers {min_year}",
            f"{search_core} open source algorithm",
            f"site:arxiv.org {search_core}",
        ]
    else:
        ddg_queries = [
            f"{search_core} {min_year} evaluation review",
            f"top {search_core} solutions",
        ]
    
    all_web_urls = []
    for q in ddg_queries:
        urls = await search_duckduckgo(q, max_pages=4)
        all_web_urls.extend(urls)
        await asyncio.sleep(1)
    
    # Deduplicate
    unique_web_urls = list(dict.fromkeys(all_web_urls))
    log.info(f"  Found {len(unique_web_urls)} unique web URLs")
    
    # Scrape web pages with recursive link following
    web_contents = []
    urls_to_scrape = unique_web_urls[:min(len(unique_web_urls), max_urls // 2)]
    
    for url in urls_to_scrape:
        if _url_counter >= max_urls:
            break
        text, links = await scrape_page(url, extract_links=True)
        if text and len(text) > 300:
            web_contents.append({"url": url, "content": text[:5000]})
            
            # Follow interesting links from the page (1-level deep crawl)
            relevant_links = [l for l in links if any(kw in l.lower() for kw in 
                [category.split()[0].lower(), "github.com", "arch", "linux", "tool", "review"]
            )][:5]
            for sub_link in relevant_links:
                if _url_counter >= max_urls:
                    break
                sub_text, _ = await scrape_page(sub_link)
                if sub_text and len(sub_text) > 300:
                    web_contents.append({"url": sub_link, "content": sub_text[:3000]})
                await asyncio.sleep(0.3)
        await asyncio.sleep(0.5)
    
    # NOTE: web_sources is set AFTER Stage 4.5 so HN/blog content is included
    log.info(f"  Scraped {len(web_contents)} web pages")

    # ─── Stage 4: Reddit Deep Dive ───────────────────────
    if topic_type in ["tech", "business", "security"]:
        log.info("  Stage 4/6: Reddit Community Discussions...")
        reddit_posts = await scrape_reddit_search(condensed.get("reddit_query", search_core))
        findings["reddit_discussions"] = reddit_posts
        log.info(f"  Found {len(reddit_posts)} Reddit discussions")
    else:
        log.info("  Stage 4/6: Reddit Community Discussions (Skipped)...")

    # ─── Stage 4.5: Hacker News & Dev Blogs ──────────────
    if topic_type in ["tech", "software", "security"]:
        log.info("  Stage 4.5/6: Hacker News & Dev Blogs...")
        hn_urls = await search_duckduckgo(f"site:news.ycombinator.com {search_core}", max_pages=1)
        hn_urls += await search_duckduckgo(f"site:dev.to {search_core}", max_pages=1)
        for url in hn_urls[:15]:
            if _url_counter >= max_urls:
                break
            text, _ = await scrape_page(url)
            if text and len(text) > 300:
                web_contents.append({"url": url, "content": text[:4000]})
            await asyncio.sleep(0.5)
        log.info(f"  Scraped {len(hn_urls)} HN/blog URLs")
    else:
        log.info("  Stage 4.5/6: Hacker News & Dev Blogs (Skipped)...")

    # Set web_sources AFTER all web+HN scraping is done
    findings["web_sources"] = [{"url": w["url"], "excerpt": w["content"][:3000]} for w in web_contents]

    # ─── Stage 5: Arch Wiki ──────────────────────────────
    log.info("  Stage 5/6: Arch Wiki Scraping...")
    
    wiki_text = await scrape_arch_wiki(search_core)
    findings["arch_wiki"] = wiki_text[:5000]
    if wiki_text:
        log.info(f"  Arch Wiki content: {len(wiki_text)} chars")

    # ─── Stage 6: LLM Triple-Pass Analysis ───────────────
    log.info("  Stage 6/6: LLM Deep Analysis (3 passes)...")
    
    # Extract tool names from all web content using LLM
    for wc in web_contents[:10]:
        tools = await llm_extract_tools_from_text(wc["content"], category)
        for t in tools:
            findings["all_tool_names"].add(t.lower())
        await asyncio.sleep(0.5)
    
    all_tools = list(findings["all_tool_names"])
    log.info(f"  Total unique tools discovered: {len(all_tools)}")
    
    # Pass 1: Comprehensive overview
    repo_block = "\\n".join([
        f"- **{r['name']}** (★{r['stars']}, {r['language']}, License: {r.get('license','?')}): {r['description']}\\n  README excerpt: {r.get('readme_excerpt','')[:300]}"
        for r in unique_repos[:15]
    ])
    
    reddit_block = "\\n".join([f"- {p['url']}: {p['content'][:300]}" for p in reddit_posts[:5]])
    wiki_block = findings["arch_wiki"][:2000]
    
    personal_block = f"\n\nUSER'S PERSONAL DATA CONTEXT (CRITICAL):\n{personal_context[:8000]}\n" if personal_context else ""
    
    pass1_prompt = f"""You are a world-class AI researcher and architect operating an advanced execution framework on "{category}".
{SYSTEM_SPECS}
{personal_block}
GITHUB REPOSITORIES FOUND ({len(unique_repos)} total):
{repo_block}

REDDIT COMMUNITY DISCUSSIONS:
{reddit_block}

ARCH WIKI:
{wiki_block}

ALL TOOL NAMES DISCOVERED: {', '.join(all_tools[:50])}

TASK (Pass 1 — Comprehensive Overview):
1. Review the User's Personal Data Context first (if provided). Frame all research insights around building the exact outcome the user wants based on their personal data profile!
2. List EVERY tool/library/project/insight discovered for this category (name + 1-line description + URL if known).
3. Synthesize the raw data into a cohesive overview mapping out the research landscape (templates, techniques, pipelines).
4. For technical tools, assess: Does it work on AMD GPU (no CUDA)? Does it run on Wayland? Is it actively maintained?

Be exhaustive. Embed personal data seamlessly into the architectural overview."""

    pass1 = await llm_analyze(pass1_prompt, max_tokens=4096)
    findings["llm_deep_analysis"] = pass1
    
    # Pass 2: Head-to-head comparison matrix
    pass2_prompt = f"""Based on this research overview for "{category}":

{pass1[:3000]}

{SYSTEM_SPECS}

TASK (Pass 2 — Comparison Matrix):
Create a detailed comparison table with these columns:
| Tool | Stars | Language | Arch/AUR | Wayland | AMD GPU | RAM Usage | CLI/API | Active | Overall Score (1-10) |

Then for every tool scoring 7+, write a 3-sentence deep analysis covering:
- Exact installation method on Arch Linux
- Key strengths that make it stand out
- Known limitations or gotchas

Include ALL alternatives, even minor ones. The user wants to see EVERY option before choosing."""

    pass2 = await llm_analyze(pass2_prompt, max_tokens=4096)
    findings["llm_comparison_matrix"] = pass2
    
    # Pass 3: Final ranked recommendations
    pass3_prompt = f"""Based on these detailed comparisons for "{category}":

Comparison Matrix:
{pass2[:3000]}

Full Research:
{pass1[:2000]}

{SYSTEM_SPECS}

TASK (Pass 3 — Final Recommendations):
Rank the TOP 5 tools from best to worst. For each:
1. **Name** and GitHub URL
2. **Why it's ranked here** (2-3 sentences)
3. **Exact install command** for Arch Linux
4. **How ARIA should integrate it** (CLI wrapper or Python API approach)
5. **Alternatives to this pick** (what else could replace it)

Also list:
- Any tools that are "rising stars" (new but promising)
- Any tools the user should absolutely AVOID and why
- Your #1 overall pick with HIGH CONFIDENCE justification"""
    pass3 = await llm_analyze(pass3_prompt, max_tokens=4096)
    findings["llm_final_recommendations"] = pass3
    
    # Convert set to list for JSON serialization
    findings["all_tool_names"] = all_tools
    findings["total_urls_crawled"] = _url_counter
    
    elapsed = time.time() - start
    log.info(f"  ✓ Category complete: {_url_counter} URLs crawled in {elapsed:.0f}s")
    log.info(f"  ✓ {len(all_tools)} unique tools discovered")
    
    return findings


async def run_full_research(categories: list[dict], max_urls: int = DEFAULT_MAX_URLS_PER_CATEGORY, pages: int = 3, resume_dir: str | None = None):
    """Run ultra-deep research across all capability categories."""
    if resume_dir:
        output_dir = Path(resume_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        log.info(f"Resuming research session directly in: {output_dir}")
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = RESEARCH_DIR / f"session_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
    
    all_findings = []
    grand_start = time.time()
    grand_urls = 0
    
    for i, cat in enumerate(categories):
        cat_slug = cat["name"].replace(" ", "_").lower()
        if output_dir.joinpath(f"{cat_slug}.json").exists():
            log.info(f"\\n{'═'*60}")
            log.info(f"Category {i+1}/{len(categories)}: {cat['name']} [SKIPPED - ALREADY COMPLETE]")
            log.info(f"{'═'*60}")
            with open(output_dir / f"{cat_slug}.json") as f:
                findings = json.load(f)
            all_findings.append(findings)
            grand_urls += findings.get("total_urls_crawled", 0)
            continue
            
        log.info(f"\\n{'═'*60}")
        log.info(f"Category {i+1}/{len(categories)}: {cat['name']}")
        log.info(f"{'═'*60}")
        
        findings = await research_category(
            cat["name"], 
            cat.get("description", ""), 
            max_urls=max_urls,
            pages=pages,
            topic_type=cat.get("type", "general"),
            min_year=cat.get("min_year", 2023)
        )
        all_findings.append(findings)
        grand_urls += findings["total_urls_crawled"]
        
        # Save individual JSON
        cat_slug = cat["name"].replace(" ", "_").lower()
        with open(output_dir / f"{cat_slug}.json", "w") as f:
            json.dump(findings, f, indent=2, default=str)
        
        # Save detailed markdown report (V4: clean human-readable output)
        md_path = output_dir / f"{cat_slug}.md"
        with open(md_path, "w") as f:
            # ── Cover Page ──
            f.write(f"# Deep Research Report: {cat['name']}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(f"**Engine:** ARIA Multimodal Deep Research v4\n\n")
            f.write(f"**URLs Crawled:** {findings['total_urls_crawled']} | ")
            f.write(f"**Tools Discovered:** {len(findings['all_tool_names'])}\n\n")
            f.write("---\n\n")
            
            # ── GitHub Repos (clean, no raw HTML) ──
            f.write(f"## GitHub Repositories ({len(findings['github_repos'])})\n\n")
            for r in findings["github_repos"]:
                f.write(f"### [{r['name']}]({r['url']}) — ★{r['stars']}\n\n")
                f.write(f"- **Language:** {r['language']} | **License:** {r.get('license','?')}\n")
                f.write(f"- **Description:** {r['description']}\n")
                if r.get("readme_excerpt"):
                    clean_readme = re.sub(r'<[^>]+>', '', r['readme_excerpt'][:300]).strip()
                    clean_readme = re.sub(r'\n{3,}', '\n\n', clean_readme)
                    clean_readme = clean_readme.replace('![', '[').strip()
                    if clean_readme:
                        f.write(f"- **README Excerpt:** {clean_readme[:200]}...\n")
                f.write("\n")
            
            # ── Awesome Lists (deduplicated) ──
            if findings["awesome_list_tools"]:
                seen_awesome = set()
                deduped = []
                for t in findings["awesome_list_tools"]:
                    if t["url"] not in seen_awesome:
                        seen_awesome.add(t["url"])
                        deduped.append(t)
                f.write(f"## Awesome List Discoveries ({len(deduped)})\n\n")
                for t in deduped[:15]:
                    f.write(f"- [{t['url']}]({t['url']}) (from {t['source']})\n")
                f.write("\n")
            
            # ── Reddit ──
            if findings["reddit_discussions"]:
                f.write(f"## Reddit Discussions ({len(findings['reddit_discussions'])})\n\n")
                for p in findings["reddit_discussions"][:10]:
                    f.write(f"- [{p['url']}]({p['url']})\n")
                f.write("\n")
            
            # ── Arch Wiki (skip bot-check pages) ──
            wiki_text = findings.get("arch_wiki", "")
            if wiki_text and "Making sure you" not in wiki_text and len(wiki_text) > 200:
                f.write(f"## Arch Wiki\n\n{wiki_text[:2000]}\n\n")
            
            # ── Tool Names Summary ──
            f.write(f"## All Tools Discovered ({len(findings['all_tool_names'])})\n\n")
            f.write(", ".join(sorted(findings["all_tool_names"])) + "\n\n")
            
            # ── LLM Analysis Sections ──
            f.write("---\n\n")
            f.write("## 🧠 LLM Analysis — Pass 1: Comprehensive Overview\n\n")
            f.write(findings.get("llm_deep_analysis", findings.get("llm_comprehensive_overview", "")) + "\n\n")
            
            f.write("---\n\n## 📊 LLM Analysis — Pass 2: Comparison Matrix\n\n")
            f.write(findings.get("llm_comparison_matrix", "") + "\n\n")
            
            f.write("---\n\n## 🏆 LLM Analysis — Pass 3: Final Recommendations\n\n")
            f.write(findings.get("llm_final_recommendations", "") + "\n")
        
        log.info(f"  Report saved: {md_path}")
        
        # ─── Generate PDF Report ────────────────────────
        try:
            with open(md_path, "r") as md_file:
                md_content = md_file.read()
            html_content = markdown.markdown(md_content, extensions=["tables", "fenced_code"])
            
            # Add premium CSS with CJK font support for the PDF output
            css = CSS(string='''
                @page {
                    size: A4;
                    margin: 2cm;
                    @bottom-center {
                        content: "ARIA Deep Research v4 — Page " counter(page) " of " counter(pages);
                        font-size: 8pt;
                        color: #95a5a6;
                    }
                }
                body {
                    font-family: "Noto Sans", "Noto Sans CJK SC", "Noto Sans CJK JP", "Noto Sans CJK KR",
                                 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    color: #2c3e50;
                    line-height: 1.7;
                    font-size: 10.5pt;
                }
                h1 {
                    color: #1a1a2e;
                    border-bottom: 3px solid #6c5ce7;
                    padding-bottom: 12px;
                    font-size: 22pt;
                    font-weight: 700;
                    letter-spacing: -0.5px;
                }
                h2 {
                    color: #6c5ce7;
                    margin-top: 28px;
                    border-bottom: 1px solid #dfe6e9;
                    padding-bottom: 8px;
                    font-size: 16pt;
                    font-weight: 600;
                }
                h3 {
                    color: #2d3436;
                    font-size: 13pt;
                    font-weight: 600;
                    margin-top: 18px;
                }
                a {
                    color: #6c5ce7;
                    text-decoration: none;
                    border-bottom: 1px dotted #6c5ce7;
                }
                pre {
                    background: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    padding: 12px 16px;
                    overflow-x: auto;
                    font-size: 9pt;
                    line-height: 1.5;
                }
                code {
                    background: #f1f3f5;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: "JetBrains Mono", "Fira Code", "Source Code Pro", monospace;
                    font-size: 9.5pt;
                    color: #e74c3c;
                }
                pre code { background: none; color: inherit; padding: 0; }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 16px 0;
                    font-size: 9.5pt;
                }
                th {
                    background: #6c5ce7;
                    color: white;
                    padding: 10px 12px;
                    text-align: left;
                    font-weight: 600;
                }
                td {
                    padding: 8px 12px;
                    border-bottom: 1px solid #e9ecef;
                }
                tr:nth-child(even) td { background: #f8f9fa; }
                ul, ol { padding-left: 22px; }
                li { margin-bottom: 6px; }
                strong { color: #2d3436; }
                blockquote {
                    border-left: 4px solid #6c5ce7;
                    margin: 16px 0;
                    padding: 8px 16px;
                    background: #f8f9fa;
                    color: #636e72;
                    font-style: italic;
                }
                hr {
                    border: none;
                    border-top: 2px solid #dfe6e9;
                    margin: 24px 0;
                }
                img {
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                    margin: 12px 0;
                }
            ''')
            
            pdf_path = output_dir / f"{cat_slug}_report.pdf"
            HTML(string=html_content).write_pdf(target=str(pdf_path), stylesheets=[css])
            log.info(f"  PDF dossier compiled: {pdf_path}")
        except Exception as e:
            log.warning(f"  PDF generation failed: {e}")
        
        if i < len(categories) - 1:
            log.info("  Cooling down 5s before next category...")
            await asyncio.sleep(5)
    
    # Master index
    elapsed = time.time() - grand_start
    master = {
        "session": timestamp,
        "total_categories": len(categories),
        "total_urls_crawled": grand_urls,
        "total_time_seconds": elapsed,
        "categories": [c["name"] for c in categories],
        "output_dir": str(output_dir),
    }
    with open(output_dir / "MASTER_INDEX.json", "w") as f:
        json.dump(master, f, indent=2)
    
    log.info(f"\\n{'═'*60}")
    log.info(f"GRAND TOTAL: {grand_urls} URLs crawled in {elapsed/60:.1f} minutes")
    log.info(f"Results: {output_dir}")
    log.info(f"{'═'*60}")
    
    return all_findings, output_dir


# ─── Default Research Categories ─────────────────────
DEFAULT_CATEGORIES = [
    # ─── AGENTIC AI & LLM FRAMEWORKS ─────────────────
    {"name": "AI agent framework python", "description": "Agentic AI frameworks like LangChain, CrewAI, AutoGen, AgentGPT, OpenClaw, OpenHands, Aider"},
    {"name": "MCP model context protocol server", "description": "MCP servers for LLM tool use: filesystem, browser, database, email, GitHub MCP tools"},
    {"name": "LLM memory RAG system", "description": "Persistent memory, RAG, vector databases, long-term context for AI agents: Mem0, ChromaDB, Qdrant"},
    {"name": "AI agent orchestration multi-agent", "description": "Multi-agent orchestration: CrewAI, AutoGen, LangGraph, Swarm, agent-to-agent communication"},
    {"name": "self improving AI agent", "description": "Self-correcting and self-improving AI agents, reflection loops, skill learning agents"},
    {"name": "AI coding agent terminal", "description": "AI coding assistants: Aider, OpenCode, Continue, Tabby, Cline, Cursor alternatives for terminal"},
    {"name": "AI browser automation agent", "description": "AI-powered browser agents: browser-use, Skyvern, LaVague, Agent-E, web automation with LLM"},
    {"name": "local LLM inference engine", "description": "Local LLM runners: Ollama, llama.cpp, vLLM, text-generation-webui, LMStudio, LocalAI for AMD GPU"},
    # ─── VOICE & VISION AGENTS ───────────────────────
    {"name": "AI voice agent assistant", "description": "Voice-controlled AI assistants, real-time voice chat, Pipecat, LiveKit, voice-to-action"},
    {"name": "speech to text STT whisper", "description": "Real-time voice transcription: Whisper, Faster-Whisper, Vosk, DeepSpeech for AMD GPU"},
    {"name": "text to speech TTS neural", "description": "Natural TTS engines: Coqui, Piper, XTTS, Bark, F5-TTS, Kokoro for local use"},
    {"name": "computer vision OCR screenshot", "description": "OCR tools: Tesseract, PaddleOCR, EasyOCR, screen capture text extraction for Wayland"},
    {"name": "AI image generation local AMD", "description": "Local image gen on AMD: Stable Diffusion, Flux, ComfyUI, A1111, SDXL with ROCm"},
    {"name": "AI voice cloning local", "description": "Voice cloning and real-time voice changer: RVC, OpenVoice, XTTS, So-VITS for AMD"},
    # ─── SYSTEM & AUTOMATION ─────────────────────────
    {"name": "linux automation workflow", "description": "System automation: n8n, Huginn, Node-RED, Activepieces, self-hosted workflow engines"},
    {"name": "android ADB automation scrcpy", "description": "Phone-to-PC tools: scrcpy, ADB automation, app control, rooted device management"},
    {"name": "screen recording wayland", "description": "Screen capture and recording on Wayland: OBS, wf-recorder, gpu-screen-recorder"},
    {"name": "clipboard manager wayland", "description": "Clipboard history for Wayland: cliphist, clipvault, wl-clipboard"},
    {"name": "smart notification linux", "description": "Desktop notifications, alerts, reminders: dunst, mako, swaync for Hyprland"},
    # ─── PRODUCTIVITY & DATA ─────────────────────────
    {"name": "file format converter universal", "description": "Universal file converter: pandoc, ffmpeg, ImageMagick, PDF/DOCX/video/audio conversion"},
    {"name": "PDF manipulation python", "description": "PDF tools: pypdf, OCRmyPDF, pdfplumber, camelot, pdf2image, form filling"},
    {"name": "web scraping automation AI", "description": "AI-powered web scrapers: Crawl4AI, FireCrawl, ScrapeGraphAI, Scrapy, data extraction"},
    {"name": "terminal file manager TUI", "description": "TUI file managers: yazi, lf, ranger, broot, nnn, superfile"},
    {"name": "system monitoring terminal TUI", "description": "System monitors: btop, nvtop, bottom, zenith, glances for AMD GPU"},
    # ─── COMMUNICATION & SOCIAL ──────────────────────
    {"name": "social media bot automation API", "description": "Social media bots: Instagram, Twitter/X, YouTube, Telegram bots, scheduling, analytics"},
    {"name": "gmail API email automation", "description": "Email automation: Gmail API, IMAP tools, email templating, auto-reply bots"},
    # ─── SECURITY & DEV TOOLS ────────────────────────
    {"name": "network security scanner linux", "description": "Security tools: nmap, rustscan, nuclei, subfinder, OSINT tools for Linux"},
    {"name": "password manager CLI", "description": "Credential management: pass, Bitwarden CLI, KeePassXC CLI, gopass"},
    {"name": "data backup sync encrypted", "description": "Backup tools: restic, borg, rclone, syncthing, encrypted archive management"},
    # ─── RESEARCH & KNOWLEDGE ────────────────────────
    {"name": "AI deep research agent", "description": "Deep research agents: STORM, GPT-Researcher, Tavily, Perplexity-like agents for local use"},
    {"name": "knowledge graph personal wiki", "description": "Personal knowledge bases: Obsidian, Logseq, SiYuan, Foam, second brain tools"},
    {"name": "AI research paper arxiv", "description": "arXiv tools: paper summarizers, citation managers, Semantic Scholar, Zotero integrations"},
    # ─── AI MEDIA & CREATIVE ────────────────────────
    {"name": "media transcoding AMD GPU", "description": "GPU-accelerated transcoding: ffmpeg VAAPI, HandBrake, av1an for AMD"},
    {"name": "image editor CLI python", "description": "CLI image editing: ImageMagick, Pillow, AI upscaling, background removal, batch processing"},
    {"name": "AI music generation local", "description": "Local AI music: AudioCraft, MusicGen, Stable Audio, Udio alternatives"},
]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ARIA Multimodal Deep Research Agent v4")
    parser.add_argument("topic", nargs="*", help="Single topic to research")
    parser.add_argument("--level", type=int, choices=[1, 2, 3, 4], default=2, help="Research depth level (1-4)")
    parser.add_argument("--type", type=str, choices=["tech", "software", "science", "security", "business", "personal", "general"], default="general", help="Topic routing category")
    parser.add_argument("--categories-file", type=str, help="JSON file containing categories to research")
    parser.add_argument("--full", action="store_true", help="Run full default research sweep")
    parser.add_argument("--min-year", type=int, default=2023, help="Minimum year for data freshness")
    parser.add_argument("--max-urls", type=int, default=DEFAULT_MAX_URLS_PER_CATEGORY, help="Max urls to scrape per category")
    parser.add_argument("--resume", type=str, help="Directory of a previous session to resume (skips completed categories)")
    
    args = parser.parse_args()
    
    # Configure level limits
    depth_map = {
        1: {"max_urls": 50, "pages": 1},
        2: {"max_urls": 300, "pages": 3},
        3: {"max_urls": 1000, "pages": 5},
        4: {"max_urls": 5000, "pages": 10}
    }
    level_cfg = depth_map[args.level]
    args.max_urls = args.max_urls if args.max_urls != DEFAULT_MAX_URLS_PER_CATEGORY else level_cfg["max_urls"]

    if args.categories_file:
        with open(args.categories_file) as f:
            categories = json.load(f)
    elif args.full:
        categories = DEFAULT_CATEGORIES
    elif args.topic:
        topic = " ".join(args.topic)
        categories = [{"name": topic, "description": topic, "type": args.type, "level": args.level, "min_year": args.min_year}]
    else:
        parser.print_help()
        print(f"\\nDefault: {len(DEFAULT_CATEGORIES)} categories, ~{DEFAULT_MAX_URLS_PER_CATEGORY} URLs each")
        sys.exit(0)
    
    print(f"🔬 ARIA Multimodal Deep Research v4: {len(categories)} topics | Type: {args.type} | Level: {args.level} | Min Year: {args.min_year}")
    print(f"   Estimated total: ~{len(categories) * args.max_urls} URLs")
    print(f"   Personal data dir: ~/.personal_data/")
    
    uvloop.run(run_full_research(categories, max_urls=args.max_urls, pages=level_cfg["pages"], resume_dir=args.resume))
