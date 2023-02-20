import re
import queue
from urllib.parse import urlparse
import urllib3
from bs4 import BeautifulSoup
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

visited_urls = set()

def crawl(starting_url, base_url):
    # Initialize a session object
    session = requests.Session()

    # Initialize a queue with the starting URL
    q = queue.Queue()
    q.put(starting_url)

    while not q.empty():
        # Get the next URL from the queue
        url = q.get()

        # Check if we have already visited this URL
        if url in visited_urls:
            continue
        visited_urls.add(url)

        # Make a request to the URL using the session object and get the HTML content
        response = session.get(url, verify=False)
        html = response.content

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

        # Find all the links on the page and add them to the queue
        for link in soup.find_all('a'):
            next_url = link.get('href')
            if next_url and next_url.startswith('http'):
                parsed_url = urlparse(next_url)
                parsed_base_url = urlparse(base_url)
                if parsed_url.netloc == parsed_base_url.netloc or parsed_url.netloc.endswith('.' + parsed_base_url.netloc):
                    q.put(next_url)

        # Print a progress message to indicate which page was crawled and the number of unique words found
        print(f"Crawled page: {url} [{num_unique_words} word(s) found]")

# Read the starting URL from a file called url.txt
with open('url.txt') as f:
    starting_url = f.readline().strip()

parsed_starting_url = urlparse(starting_url)
base_url = parsed_starting_url.scheme + '://' + parsed_starting_url.netloc

crawl(starting_url, base_url)
