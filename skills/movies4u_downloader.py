#!/usr/bin/env python3
"""
movies4u_downloader.py

A highly resilient and stealthy web scraper powered by Scrapling v0.3.
Because movies4u.direct contains numerous ad overlays and anti-bot protections,
we use Scrapling's StealthySession to bypass them and locate the actual download link.
"""
import sys
import urllib.parse
from scrapling.fetchers import StealthySession

def search_movies4u(query: str):
    # Prepare search URL
    safe_query = urllib.parse.quote_plus(query)
    search_url = f"https://movies4u.direct/?s={safe_query}"
    
    print(f"[*] Initializing Scrapling StealthySession for: {search_url}")
    
    try:
        # Initialize Scrapling's stealth browser which automatically bypasses Cloudflare
        with StealthySession(headless=True) as session:
            print("[*] Stealth session started. Fetching search page...")
            # Navigate to the search page
            page = session.fetch(search_url)
            
            # In a real scenario, we would parse the search results to find the correct movie link
            links = page.css('a')
            
            movie_results = []
            for link in links:
                href = link.attrib.get('href', '')
                try:
                    title = link.text.strip()
                except AttributeError:
                    # some elements might not have text extracted simply, handle safely
                    title = href
                    
                # Basic heuristic: if it has the query in the URL or title and isn't a nav link
                if query.lower() in href.lower() or query.lower() in title.lower():
                    if len(title) > 2 and 'http' in href:
                         # Deduplicate
                        if not any(r['url'] == href for r in movie_results):
                            movie_results.append({"title": title, "url": href})
                            
            if not movie_results:
                print(f"[-] No movies found for '{query}' on movies4u.direct.")
                return

            print(f"[+] Found {len(movie_results)} potential matches!")
            for idx, res in enumerate(movie_results[:5]):
                print(f"  {idx+1}. {res['title']} -> {res['url']}")
                
            # Select the first match
            target_url = movie_results[0]['url']
            print(f"\n[*] Navigating to movie page: {target_url} to extract download links...")
            
            # Navigate to the movie page
            movie_page = session.fetch(target_url)
            
            # Extract download buttons/links 
            download_links = movie_page.css('a')
            final_downloads = []
            for dl in download_links:
                try:
                    text = dl.text.strip().lower()
                    href = dl.attrib.get('href', '')
                    if 'download' in text or 'magnet' in href or 'torrent' in text or 'gdoto' in href or 'gofile' in href:
                        # Exclude self-referencing anchor links
                        if len(href) > 2 and not href.startswith('#'):
                            final_downloads.append(href)
                except AttributeError:
                    continue
                    
            if final_downloads:
                print(f"\n[SUCCESS] Extracted Download Links:")
                # Deduplicate links and print
                for link in set(final_downloads):
                    print(f" -> {link}")
            else:
                print("\n[-] Could not find any explicit download buttons on the movie page. Site structure may have hidden redirects.")
                try:
                    print("[*] Page Title:", movie_page.css('title')[0].text)
                except IndexError:
                    pass

    except Exception as e:
        print(f"[-] Scrapling encountered an error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 movies4u_downloader.py <movie_name>")
        sys.exit(1)
        
    query = " ".join(sys.argv[1:])
    search_movies4u(query)
