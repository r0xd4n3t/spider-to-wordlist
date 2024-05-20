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
MAX_RETRIES = 3

def write_wordlist(words):
    """Write the unique words to a file called wordlist.txt."""
    with open(WORDLIST_FILE, 'a', encoding='utf-8') as f:
        for word in words:
            if word.strip() and word.strip() not in visited_urls:  # Check if word is not empty and not already visited
                f.write(f"{word}\n")
                visited_urls.add(word.strip())  # Add the word to the visited set

def cleanup_wordlist(force_cleanup=False):
    global last_cleanup_time

    print("[*] Initiating wordlist cleanup...")

    if time.time() - last_cleanup_time >= CLEANUP_INTERVAL or force_cleanup:
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
    else:
        print("[*] Cleanup not needed at this time.")

def set_random_user_agent():
    """Generate a random user agent using fake_useragent."""
    user_agent = UserAgent()
    return user_agent.random

def fetch_url(http, url, headers):
    """Fetch the URL with retries and handle SSL errors."""
    for attempt in range(MAX_RETRIES):
        try:
            response = http.request('GET', url, headers=headers)
            return response
        except urllib3.exceptions.SSLError as e:
            print(f"[!] SSL error: {url} - {e}")
        except urllib3.exceptions.MaxRetryError as e:
            print(f"[!] Max retries exceeded: {url} - {e}")
        except Exception as e:
            print(f"[!] Error fetching {url}: {e}")
        time.sleep(1)
    return None

def crawl(starting_url, base_url):
    global last_cleanup_time

    http = urllib3.PoolManager(cert_reqs='CERT_NONE')  # Skip SSL verification
    urls_to_crawl.add(starting_url)

    try:
        while urls_to_crawl:
            url = urls_to_crawl.pop()
            if url in visited_urls:
                continue
            visited_urls.add(url)

            cleanup_wordlist()

            headers = {'User-Agent': set_random_user_agent()}
            response = fetch_url(http, url, headers)

            if not response:
                continue

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
        cleanup_wordlist(force_cleanup=True)
        exit()

if __name__ == "__main__":
    with open('url.txt') as f:
        starting_url = f.readline().strip()

    parsed_starting_url = urlparse(starting_url)
    base_url = f"{parsed_starting_url.scheme}://{parsed_starting_url.netloc}"

    crawl(starting_url, base_url)
