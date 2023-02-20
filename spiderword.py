import re
from urllib.parse import urlparse
import urllib3
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urljoin

urllib3.disable_warnings(category=InsecureRequestWarning)

visited_urls = set()
urls_to_crawl = set()

def crawl(starting_url, base_url):
    # Initialize a PoolManager object
    http = urllib3.PoolManager()

    # Add the starting URL to the set of URLs to crawl
    urls_to_crawl.add(starting_url)

    while urls_to_crawl:
        # Get the next URL from the set of URLs to crawl
        url = urls_to_crawl.pop()

        # Check if we have already visited this URL
        if url in visited_urls:
            continue
        visited_urls.add(url)

        # Make a request to the URL using the PoolManager object and get the HTML content
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        response = http.request('GET', url)
        html = response.data

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Find all the text in the HTML content
        text = soup.get_text()

        # Split the text into words
        words = re.findall(r'\b[a-zA-Z0-9]+\b', text)

        # Remove any duplicate words
        unique_words = set(words)

        # Write the unique words to a file called wordlist.txt
        with open('wordlist.txt', 'a', encoding='utf-8') as f:
            f.write('\n'.join(sorted(unique_words)) + '\n')

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
        print(f"Crawled page: {url} [{num_unique_words} word(s) found]")

# Read the starting URL from a file called url.txt
with open('url.txt') as f:
    starting_url = f.readline().strip()

parsed_starting_url = urlparse(starting_url)
base_url = parsed_starting_url.scheme + '://' + parsed_starting_url.netloc

crawl(starting_url, base_url)
