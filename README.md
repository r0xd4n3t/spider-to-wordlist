<a id="top"></a>

<h1 align="center">Spider to Wordlist</h1>

<p align="center">
  <kbd>
    <img src="https://raw.githubusercontent.com/r0xd4n3t/spider-to-wordlist/main/img/spider.png" alt="Spider to Wordlist banner">
  </kbd>
</p>

<p align="center">
  <img src="https://img.shields.io/github/last-commit/r0xd4n3t/spider-to-wordlist?style=flat" alt="Last commit">
  <img src="https://img.shields.io/github/stars/r0xd4n3t/spider-to-wordlist?color=brightgreen" alt="GitHub stars">
  <img src="https://img.shields.io/github/forks/r0xd4n3t/spider-to-wordlist?color=brightgreen" alt="GitHub forks">
</p>

# 📜 Introduction

**Spider to Wordlist** is a Python-based web crawler that visits pages, extracts visible text, filters it into words, removes duplicates, and saves the results into `wordlist.txt`.

It uses:

- `requests` to fetch web pages
- `BeautifulSoup` to parse HTML content
- `urllib` to work with URLs and limit crawling scope
- `re` to split and clean extracted text into words

This tool is useful for generating custom wordlists from a target website during content discovery, recon, or wordlist building workflows.

> Sample output

![](https://raw.githubusercontent.com/r0xd4n3t/spider-to-wordlist/main/img/sample.png)

## 🕹️ Usage

Make sure Python 3 is installed on your system.

1. Save the script as `spiderword.py`
2. Create a file named `url.txt`
3. Put the starting URL inside `url.txt`
4. Run the script:

```bash
python spiderword.py
```

After execution:

- the crawler reads the target URL from `url.txt`
- crawls reachable pages within scope
- extracts unique words from page content
- writes the results into `wordlist.txt`

## 📝 Prerequisites

Before using this script, you should have:

- Python 3 installed
- basic familiarity with Python modules and libraries
- understanding of how web crawling works
- required Python packages such as `requests` and `beautifulsoup4`
- a working internet connection

You may install the required packages with:

```bash
pip install requests beautifulsoup4
```

## ⚠️ Notes

- Only crawl websites you are authorized to test or analyze
- Large websites may produce very large wordlists
- Some websites may block automated requests or require headers, cookies, or rate limiting controls

<p align="center"><a href="#top">Back to Top</a></p>
