import re
import random
import time
import os
from urllib.parse import urlparse, urljoin
import urllib3
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from fake_useragent import UserAgent

# Disable insecure request warnings
urllib3.disable_warnings(category=InsecureRequestWarning)

# Initialize global sets for visited URLs and URLs to crawl
visited_urls = set()
urls_to_crawl = set()
last_cleanup_time = time.time()

# Constants
WORDLIST_FILE = 'wordlist.txt'
CLEANUP_INTERVAL = 60
CLEANUP_DELAY = 5

def write_wordlist(words):
    """Write the unique words to a file called wordlist.txt."""
    with open(WORDLIST_FILE, 'a', encoding='utf-8') as f:
        for word in words:
            f.write(f"{word}\n")

def cleanup_wordlist():
    """Clean up the wordlist file by removing duplicate words and updating the last cleanup time."""
    global last_cleanup_time

    if time.time() - last_cleanup_time >= CLEANUP_INTERVAL:
        time.sleep(CLEANUP_DELAY)
        wordlist_size_before = os.path.getsize(WORDLIST_FILE)
        print(f"[+] Wordlist: file size before cleanup: {wordlist_size_before / 1024:.2f} KB")

        with open(WORDLIST_FILE, 'r', encoding='utf-8') as f:
            unique_words = set(line.strip() for line in f if line.strip() and re.match(r"^[a-zA-Z0-9_.,!?@#$%^&*()-=+ ]*$", line))

        sorted_unique_words = sorted(unique_words)
        with open(WORDLIST_FILE, 'w', encoding='utf-8') as f:
            for word in sorted_unique_words:
                f.write(f"{word}\n")

        wordlist_size_after = os.path.getsize(WORDLIST_FILE)
        print(f"[-] Wordlist: file size after cleanup: {wordlist_size_after / 1024:.2f} KB")
        last_cleanup_time = time.time()

def set_random_user_agent():
    """Generate a random user agent using fake_useragent."""
    user_agent = UserAgent()
    return user_agent.random

def crawl(starting_url, base_url):
    """Crawl web pages starting from the given URL and collect words."""
    global last_cleanup_time

    http = urllib3.PoolManager()
    urls_to_crawl.add(starting_url)

    try:
        while urls_to_crawl:
            url = urls_to_crawl.pop()
            if url in visited_urls:
                continue
            visited_urls.add(url)

            cleanup_wordlist()

            headers = {'User-Agent': set_random_user_agent()}
            response = http.request('GET', url, headers=headers)
            html = response.data

            try:
                soup = BeautifulSoup(html, 'html.parser')
            except Exception as e:
                print(f"[!] Parser error: {url} - {e}")
                continue

            text = soup.get_text()
            words = re.findall(r"[a-zA-Z0-9]+", text)
            words = [word.encode('ascii', 'ignore').decode('utf-8') for word in words]
            unique_words = set(words)
            write_wordlist(unique_words)

            num_unique_words = len(unique_words)

            for link in soup.find_all('a', href=True):
                next_url = urljoin(base_url, link['href'])
                parsed_url = urlparse(next_url)
                if parsed_url.scheme in ['http', 'https'] and parsed_url.netloc.endswith(urlparse(base_url).netloc):
                    urls_to_crawl.add(next_url)

            print(f"[+] Crawled page: {url} [{num_unique_words} word(s) found]")

    except KeyboardInterrupt:
        print("\n[-] Crawling process interrupted. Cleaning up and exiting gracefully.")
        cleanup_wordlist()
        exit()

if __name__ == "__main__":
    with open('url.txt') as f:
        starting_url = f.readline().strip()

    parsed_starting_url = urlparse(starting_url)
    base_url = f"{parsed_starting_url.scheme}://{parsed_starting_url.netloc}"

    crawl(starting_url, base_url)
