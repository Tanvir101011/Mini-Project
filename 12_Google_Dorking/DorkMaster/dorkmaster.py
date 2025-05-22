import argparse
import csv
import os
from pathlib import Path
import sys
from datetime import datetime
import logging
import requests
from bs4 import BeautifulSoup
import random
import time

class DorkMaster:
    """Handle Google Dork query automation."""
    def __init__(self, output_dir='dorkmaster_output', proxy=None):
        self.output_dir = output_dir
        self.proxy = proxy
        self.logger = logging.getLogger(__name__)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.dork_categories = {
            'files': 'filetype:pdf site:*.edu confidential',
            'login': 'inurl:(login | admin | dashboard) site:*.gov',
            'cameras': 'inurl:(webcam | camera | viewer) "live view"',
            'ftp': 'intitle:"index of" inurl:ftp',
            'sql': 'filetype:sql intext:"insert into" site:*.org',
            'exposed': 'inurl:(phpinfo | .git | config) site:*.com'
        }

    def build_query(self, category=None, custom_query=None):
        """Build a Google Dork query."""
        if custom_query:
            return custom_query
        if category in self.dork_categories:
            return self.dork_categories[category]
        self.logger.error(f"Invalid category: {category}. Available: {list(self.dork_categories.keys())}")
        return None

    def search_google(self, query):
        """Execute Google search and scrape results."""
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
        try:
            response = requests.get(url, headers=self.headers, proxies=proxies, timeout=10)
            if response.status_code == 429:
                self.logger.warning("Rate limit detected. Consider using a proxy or waiting.")
                return []
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch results: HTTP {response.status_code}")
                return []
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            for g in soup.find_all('div', class_='g')[:10]:  # Limit to first 10 results
                title = g.find('h3')
                link = g.find('a', href=True)
                snippet = g.find('div', class_='VwiC3b')
                if link and title:
                    results.append({
                        'url': link['href'],
                        'title': title.text,
                        'snippet': snippet.text if snippet else ''
                    })
            return results
        except Exception as e:
            self.logger.error(f"Error searching Google: {e}")
            return []

    def save_results(self, results, query):
        """Save search results to CSV."""
        os.makedirs(self.output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(self.output_dir, f"results_{timestamp}.csv")
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['url', 'title', 'snippet', 'query', 'timestamp']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for result in results:
                    writer.writerow({
                        'url': result['url'],
                        'title': result['title'],
                        'snippet': result['snippet'],
                        'query': query,
                        'timestamp': datetime.now().isoformat()
                    })
            self.logger.info(f"Results saved to {output_file}")
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")

    def generate_summary(self, results, query):
        """Generate a summary report."""
        summary_file = os.path.join(self.output_dir, 'summary.txt')
        try:
            with open(summary_file, 'a', encoding='utf-8') as f:
                f.write(f"DorkMaster Summary Report - {datetime.now().isoformat()}\n")
                f.write("-" * 50 + "\n")
                f.write(f"Query: {query}\n")
                f.write(f"Results Found: {len(results)}\n")
                for result in results[:5]:  # Limit to first 5 for brevity
                    f.write(f"URL: {result['url']}\nTitle: {result['title']}\nSnippet: {result['snippet'][:100]}...\n")
                if len(results) > 5:
                    f.write(f"... {len(results) - 5} more results ...\n")
                f.write("-" * 50 + "\n\n")
            self.logger.info(f"Summary appended to {summary_file}")
        except Exception as e:
            self.logger.error(f"Error saving summary: {e}")

def main():
    parser = argparse.ArgumentParser(description="DorkMaster: Automate Google Dork searches.")
    parser.add_argument('-c', '--category', choices=['files', 'login', 'cameras', 'ftp', 'sql', 'exposed'],
                        help="Predefined dork category.")
    parser.add_argument('-q', '--query', help="Custom dork query (e.g., 'inurl:login site:*.edu').")
    parser.add_argument('-o', '--output-dir', default='dorkmaster_output', help="Output directory (default: dorkmaster_output).")
    parser.add_argument('-p', '--proxy', help="Proxy URL (e.g., http://proxy:port).")
    parser.add_argument('--verbose', action='store_true', help="Print detailed results.")
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Validate input
    if not args.category and not args.query:
        logger.error("Either --category or --query must be provided.")
        sys.exit(1)

    dork = DorkMaster(args.output_dir, args.proxy)
    query = dork.build_query(args.category, args.query)
    if not query:
        sys.exit(1)

    # Execute search
    logger.info(f"Executing query: {query}")
    results = dork.search_google(query)
    if not results:
        logger.warning("No results found.")
        return

    # Save and summarize results
    dork.save_results(results, query)
    dork.generate_summary(results, query)

    # Print verbose output
    if args.verbose:
        for result in results[:10]:  # Limit to first 10 for brevity
            logger.info(f"URL: {result['url']}\nTitle: {result['title']}\nSnippet: {result['snippet'][:100]}...")
        if len(results) > 10:
            logger.info(f"... {len(results) - 10} more results ...")

    logger.info(f"Search complete. Results in {args.output_dir}")
    time.sleep(random.uniform(1, 3))  # Random delay to avoid rate-limiting

if __name__ == "__main__":
    main()