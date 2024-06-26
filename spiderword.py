import re
import time
import os
from urllib.parse import urlparse, urljoin
import urllib3
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from fake_useragent import UserAgent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Disable insecure request warnings
urllib3.disable_warnings(category=InsecureRequestWarning)

class WebCrawler:
    def __init__(self, starting_urls, wordlist_file='wordlist.txt', cleanup_interval=60, cleanup_delay=5, max_retries=3):
        self.visited_urls = set()
        self.urls_to_crawl = set()
        self.wordlist_file = wordlist_file
        self.cleanup_interval = cleanup_interval
        self.cleanup_delay = cleanup_delay
        self.max_retries = max_retries
        self.last_cleanup_time = time.time()
        self.allowed_domains = []
        self.http = urllib3.PoolManager(cert_reqs='CERT_NONE')  # Skip SSL verification

        # Initialize allowed domains and URLs to crawl
        for url in starting_urls:
            self.allowed_domains.append(urlparse(url).netloc)
            self.urls_to_crawl.add(url)

    def write_wordlist(self, words):
        """Write the unique words to a file."""
        with open(self.wordlist_file, 'a', encoding='utf-8') as f:
            for word in words:
                if word.strip() and word.strip() not in self.visited_urls:
                    f.write(f"{word}\n")
                    self.visited_urls.add(word.strip())

    def cleanup_wordlist(self, force_cleanup=False):
        """Remove duplicates and non-alphanumeric characters from the wordlist."""
        if time.time() - self.last_cleanup_time >= self.cleanup_interval or force_cleanup:
            time.sleep(self.cleanup_delay)
            wordlist_size_before = os.path.getsize(self.wordlist_file)
            logging.info(f"Wordlist: file size before cleanup: {wordlist_size_before / 1024:.2f} KB")

            with open(self.wordlist_file, 'r', encoding='utf-8') as f:
                unique_words = set(line.strip() for line in f if line.strip() and re.match(r"^[a-zA-Z0-9_.,!?@#$%^&*()-=+ ]*$", line))

            sorted_unique_words = sorted(unique_words)
            with open(self.wordlist_file, 'w', encoding='utf-8') as f:
                for word in sorted_unique_words:
                    f.write(f"{word}\n")

            wordlist_size_after = os.path.getsize(self.wordlist_file)
            logging.info(f"Wordlist: file size after cleanup: {wordlist_size_after / 1024:.2f} KB")
            self.last_cleanup_time = time.time()
        else:
            logging.info("Cleanup not needed at this time.")

    def set_random_user_agent(self):
        """Generate a random user agent."""
        user_agent = UserAgent()
        return user_agent.random

    def fetch_url(self, url):
        """Fetch the URL with retries and handle SSL errors."""
        headers = {'User-Agent': self.set_random_user_agent()}
        for attempt in range(self.max_retries):
            try:
                response = self.http.request('GET', url, headers=headers)
                return response
            except urllib3.exceptions.SSLError as e:
                logging.warning(f"SSL error: {url} - {e}")
            except urllib3.exceptions.MaxRetryError as e:
                logging.warning(f"Max retries exceeded: {url} - {e}")
            except Exception as e:
                logging.warning(f"Error fetching {url}: {e}")
            time.sleep(1)
        return None

    def is_valid_domain(self, url):
        """Check if the URL is within the allowed domain and subdomains."""
        parsed_url = urlparse(url)
        return any(parsed_url.netloc == domain or parsed_url.netloc.endswith('.' + domain) for domain in self.allowed_domains)

    def is_valid_url(self, url):
        """Check if the URL is valid and not a JavaScript or mailto link."""
        parsed_url = urlparse(url)
        return parsed_url.scheme in ['http', 'https'] and bool(parsed_url.netloc)

    def crawl_domain(self, base_url):
        """Crawl all pages within the specified domain."""
        domain = urlparse(base_url).netloc
        self.urls_to_crawl.add(base_url)

        while self.urls_to_crawl:
            url = self.urls_to_crawl.pop()
            if url in self.visited_urls:
                continue
            self.visited_urls.add(url)

            self.cleanup_wordlist()

            response = self.fetch_url(url)
            if not response:
                continue

            html = response.data

            try:
                soup = BeautifulSoup(html, 'html.parser')
            except Exception as e:
                logging.warning(f"Parser error: {url} - {e}")
                continue

            text = soup.get_text()
            words = re.findall(r"[a-zA-Z0-9]+", text)
            words = [word.encode('ascii', 'ignore').decode('utf-8') for word in words]
            unique_words = set(words)
            self.write_wordlist(unique_words)

            for link in soup.find_all('a', href=True):
                href = link['href']
                next_url = urljoin(url, href)
                if self.is_valid_domain(next_url) and self.is_valid_url(next_url) and next_url not in self.visited_urls:
                    self.urls_to_crawl.add(next_url)

            logging.info(f"Crawled page: {url} [{len(unique_words)} word(s) found]")

    def crawl(self):
        """Crawl the web starting from the initial URLs."""
        try:
            for base_url in self.allowed_domains:
                logging.info(f"Starting crawl for domain: {base_url}")
                self.crawl_domain(f"https://{base_url}")
        except KeyboardInterrupt:
            logging.info("Crawling process interrupted. Cleaning up and exiting gracefully.")
        finally:
            self.cleanup_wordlist(force_cleanup=True)

if __name__ == "__main__":
    with open('url.txt') as f:
        starting_urls = [f"https://{line.strip()}" for line in f.readlines()]

    crawler = WebCrawler(starting_urls)
    crawler.crawl()
