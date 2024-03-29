import re
import random
import time
import os
from urllib.parse import urlparse, urljoin
import urllib3
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from fake_useragent import UserAgent

urllib3.disable_warnings(category=InsecureRequestWarning)

visited_urls = set()
urls_to_crawl = set()
last_cleanup_time = time.time()

def write_wordlist(words):
    # Write the unique words to a file called wordlist.txt
    with open('wordlist.txt', 'a', encoding='utf-8') as f:
        for word in words:
            f.write(f"{word}\n")

def cleanup_wordlist():
    global last_cleanup_time

    if time.time() - last_cleanup_time >= 60:
        # Add a delay of 5 seconds before cleanup
        time.sleep(5)
        # Print the size of the wordlist file before cleaning it up
        wordlist_size_before = os.path.getsize('wordlist.txt')
        print(f"[+] Wordlist: file size before cleanup: {wordlist_size_before / 1024:.2f} KB")

        # Clean up the wordlist file by removing duplicate words
        print(f"[*] Wordlist: Running..Clean up!")
        with open('wordlist.txt', 'r', encoding='utf-8') as f:
            unique_words = set(line.strip() for line in f if line.strip() and re.search("^[a-zA-Z0-9_.,!?@#$%^&*()-=+ ]*$", line))
        sorted_unique_words = sorted(unique_words)
        with open('unique_wordlist.txt', 'w', encoding='utf-8') as f:
            for word in sorted_unique_words:
                f.write(f"{word}\n")
        os.replace('unique_wordlist.txt', 'wordlist.txt')
        wordlist_size_after = os.path.getsize('wordlist.txt')
        print(f"[-] Wordlist: file size after cleanup: {wordlist_size_after / 1024:.2f} KB")

        # Update the last cleanup time
        last_cleanup_time = time.time()

def set_random_user_agent():
    # Use fake_useragent to generate a random user agent
    user_agent = UserAgent()
    return user_agent.random

def crawl(starting_url, base_url):
    global last_cleanup_time

    # Initialize a PoolManager object
    http = urllib3.PoolManager()

    # Add the starting URL to the set of URLs to crawl
    urls_to_crawl.add(starting_url)

    try:
        while urls_to_crawl:
            # Get the next URL from the set of URLs to crawl
            url = urls_to_crawl.pop()

            # Check if we have already visited this URL
            if url in visited_urls:
                continue
            visited_urls.add(url)

            cleanup_wordlist()

            # Set a random user agent for each request
            headers = {'User-Agent': set_random_user_agent()}

            # Make a request to the URL using the PoolManager object and get the HTML content
            http = urllib3.PoolManager(cert_reqs='CERT_NONE')
            response = http.request('GET', url, headers=headers)
            html = response.data

            try:
                # Parse the HTML content using BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
            except AssertionError:
                # Handle parser errors and skip this URL
                print(f"[!] Parser error: {url}")
                continue

            # Find all the text in the HTML content
            text = soup.get_text()

            # Split the text into words
            words = re.findall(r"[a-zA-Z0-9]+", text)

            # Remove any non-ASCII characters from the words
            words = [word.encode('ascii', 'ignore').decode('utf-8') for word in words]

            # Remove any duplicate words
            unique_words = set(words)

            # Write the unique words to a file called wordlist.txt
            write_wordlist(unique_words)

            # Count the number of unique words found
            num_unique_words = len(unique_words)

            # Find all the links on the page and add them to the set of URLs to crawl
            for link in soup.find_all('a'):
                next_url = link.get('href')
                if next_url:
                    absolute_url = urljoin(base_url, next_url)
                    parsed_url = urlparse(absolute_url)
                    if parsed_url.scheme == 'http' or parsed_url.scheme == 'https':
                        if parsed_url.netloc == urlparse(base_url).netloc or parsed_url.netloc.endswith('.' + urlparse(base_url).netloc):
                            urls_to_crawl.add(absolute_url)

            # Print a progress message to indicate which page was crawled and the number of unique words found
            print(f"[+] Crawled page: {url} [{num_unique_words} word(s) found]")

    except KeyboardInterrupt:
        print("\n[-] Crawling process interrupted. Cleaning up and exiting gracefully.")
        cleanup_wordlist()
        # Add any additional cleanup tasks if needed
        exit()

# Read the starting URL from a file called url.txt
with open('url.txt') as f:
    starting_url = f.readline().strip()

parsed_starting_url = urlparse(starting_url)
base_url = parsed_starting_url.scheme + '://' + parsed_starting_url.netloc

crawl(starting_url, base_url)
