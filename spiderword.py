import re
import random
import time
import os
from urllib.parse import urlparse, urljoin
import urllib3
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(category=InsecureRequestWarning)

visited_urls = set()
urls_to_crawl = set()
last_cleanup_time = time.time()

def crawl(starting_url, base_url):
    global last_cleanup_time

    # Initialize a PoolManager object
    http = urllib3.PoolManager()

    # Add the starting URL to the set of URLs to crawl
    urls_to_crawl.add(starting_url)

    def write_wordlist(words):
        # Write the unique words to a set
        unique_words.update(words)

    unique_words = set()

    while urls_to_crawl:
        # Get the next URL from the set of URLs to crawl
        url = urls_to_crawl.pop()

        # Check if we have already visited this URL
        if url in visited_urls:
            continue
        visited_urls.add(url)

        # Check if it's been 1 minute since the last cleanup
        if time.time() - last_cleanup_time >= 60:
            # Add a delay of 5 seconds before cleanup
            time.sleep(5)
            # Clean up the wordlist set by removing non-alphanumeric characters
            unique_words_cleaned = set()
            for word in unique_words:
                word_cleaned = re.sub(r'\W+', '', word)
                if word_cleaned:
                    unique_words_cleaned.add(word_cleaned)
            # Replace the contents of the file with the unique words
            with open('wordlist.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(sorted(unique_words_cleaned)) + '\n')
            unique_words = unique_words_cleaned

            # Update the last cleanup time
            last_cleanup_time = time.time()

        # Set a random user agent for each request
        headers = {
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
                'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.16 Safari/537.36',
                'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
                'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 Edge/16.16299'
            ])
        }

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

# Read the starting URL from a file called url.txt
with open('url.txt') as f:
    starting_url = f.readline().strip()

parsed_starting_url = urlparse(starting_url)
base_url = parsed_starting_url.scheme + '://' + parsed_starting_url.netloc

crawl(starting_url, base_url)
