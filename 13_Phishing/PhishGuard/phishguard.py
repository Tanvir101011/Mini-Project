import argparse
import csv
import os
from pathlib import Path
import sys
from datetime import datetime
import logging
import sqlite3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from urllib.parse import urlparse

class PhishGuard:
    """Manage a phishing database for threat analysis."""
    def __init__(self, db_path='phishguard.db', output_dir='phishguard_output'):
        self.db_path = db_path
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.conn = None
        self.cursor = None
        os.makedirs(self.output_dir, exist_ok=True)
        self.init_db()

    def init_db(self):
        """Initialize SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS phishing_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    domain TEXT,
                    ip TEXT,
                    email TEXT,
                    source TEXT,
                    status TEXT DEFAULT 'active',
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            sys.exit(1)

    def import_csv(self, csv_file):
        """Import phishing data from CSV."""
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    url = row.get('url', '')
                    domain = urlparse(url).netloc if url else ''
                    self.cursor.execute('''
                        INSERT INTO phishing_data (url, domain, ip, email, source, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        url,
                        domain,
                        row.get('ip', ''),
                        row.get('email', ''),
                        row.get('source', 'csv_import'),
                        row.get('status', 'active')
                    ))
            self.conn.commit()
            self.logger.info(f"Imported data from {csv_file}")
        except Exception as e:
            self.logger.error(f"Error importing CSV: {e}")

    def scrape_phishtank(self, limit=10):
        """Scrape phishing URLs from PhishTank."""
        url = "https://www.phishtank.com/phish_search.php?valid=y&active=All"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch PhishTank: HTTP {response.status_code}")
                return
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.find_all('tr')[1:limit + 1]  # Skip header
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 2:
                    continue
                phish_url = cols[1].text.strip()
                domain = urlparse(phish_url).netloc
                self.cursor.execute('''
                    INSERT OR IGNORE INTO phishing_data (url, domain, source, status)
                    VALUES (?, ?, ?, ?)
                ''', (phish_url, domain, 'phishtank', 'active'))
            self.conn.commit()
            self.logger.info(f"Scraped {len(rows)} URLs from PhishTank")
        except Exception as e:
            self.logger.error(f"Error scraping PhishTank: {e}")

    def query_data(self, url=None, domain=None, ip=None, date_from=None, date_to=None):
        """Query phishing data with filters."""
        query = "SELECT * FROM phishing_data WHERE 1=1"
        params = []
        if url:
            query += " AND url LIKE ?"
            params.append(f"%{url}%")
        if domain:
            query += " AND domain LIKE ?"
            params.append(f"%{domain}%")
        if ip:
            query += " AND ip LIKE ?"
            params.append(f"%{ip}%")
        if date_from:
            query += " AND added_at >= ?"
            params.append(date_from)
        if date_to:
            query += " AND added_at <= ?"
            params.append(date_to)
        try:
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in results]
        except Exception as e:
            self.logger.error(f"Error querying data: {e}")
            return []

    def update_status(self, url, status):
        """Update status of a phishing entry."""
        try:
            self.cursor.execute("UPDATE phishing_data SET status = ? WHERE url = ?", (status, url))
            self.conn.commit()
            self.logger.info(f"Updated status of {url} to {status}")
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")

    def export_results(self, results, filename='query_results.csv'):
        """Export query results to CSV."""
        output_file = os.path.join(self.output_dir, filename)
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                if results:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
            self.logger.info(f"Exported results to {output_file}")
        except Exception as e:
            self.logger.error(f"Error exporting results: {e}")

    def generate_report(self):
        """Generate a summary report."""
        summary_file = os.path.join(self.output_dir, 'summary.txt')
        try:
            self.cursor.execute("SELECT COUNT(*) FROM phishing_data")
            total_entries = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT status, COUNT(*) FROM phishing_data GROUP BY status")
            status_counts = self.cursor.fetchall()
            self.cursor.execute("SELECT domain, COUNT(*) FROM phishing_data GROUP BY domain ORDER BY COUNT(*) DESC LIMIT 5")
            top_domains = self.cursor.fetchall()

            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"PhishGuard Summary Report - {datetime.now().isoformat()}\n")
                f.write("-" * 50 + "\n")
                f.write(f"Total Entries: {total_entries}\n")
                f.write("Status Counts:\n")
                for status, count in status_counts:
                    f.write(f"  {status}: {count}\n")
                f.write("Top 5 Domains:\n")
                for domain, count in top_domains:
                    f.write(f"  {domain}: {count}\n")
                f.write("-" * 50 + "\n")
            self.logger.info(f"Summary saved to {summary_file}")
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")

    def plot_trends(self):
        """Plot phishing entries by domain over time."""
        try:
            self.cursor.execute("SELECT domain, added_at FROM phishing_data WHERE domain IS NOT NULL")
            data = self.cursor.fetchall()
            df = pd.DataFrame(data, columns=['domain', 'added_at'])
            df['added_at'] = pd.to_datetime(df['added_at'])
            df['date'] = df['added_at'].dt.date
            top_domains = df['domain'].value_counts().head(5).index
            plot_data = df[df['domain'].isin(top_domains)].groupby(['date', 'domain']).size().unstack().fillna(0)

            plt.figure(figsize=(10, 6))
            plot_data.plot(kind='line')
            plt.title('Top 5 Phishing Domains Over Time')
            plt.xlabel('Date')
            plt.ylabel('Number of Entries')
            plt.legend(title='Domain')
            plt.grid(True)
            output_plot = os.path.join(self.output_dir, 'trends.png')
            plt.savefig(output_plot)
            plt.close()
            self.logger.info(f"Trend plot saved to {output_plot}")
        except Exception as e:
            self.logger.error(f"Error plotting trends: {e}")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.logger.info("Database connection closed")

def main():
    parser = argparse.ArgumentParser(description="PhishGuard: Phishing database management tool.")
    parser.add_argument('-a', '--action', choices=['import', 'scrape', 'query', 'update', 'report', 'plot'], required=True,
                        help="Action to perform.")
    parser.add_argument('-c', '--csv', help="CSV file to import (for import action).")
    parser.add_argument('-u', '--url', help="URL to query or update.")
    parser.add_argument('-d', '--domain', help="Domain to query.")
    parser.add_argument('-i', '--ip', help="IP to query.")
    parser.add_argument('--date-from', help="Start date for query (YYYY-MM-DD).")
    parser.add_argument('--date-to', help="End date for query (YYYY-MM-DD).")
    parser.add_argument('-s', '--status', choices=['active', 'mitigated', 'suspicious'], help="Status to update (for update action).")
    parser.add_argument('-o', '--output-dir', default='phishguard_output', help="Output directory (default: phishguard_output).")
    parser.add_argument('--db', default='phishguard.db', help="Database file (default: phishguard.db).")
    parser.add_argument('--verbose', action='store_true', help="Print detailed logs.")
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialize PhishGuard
    phish = PhishGuard(args.db, args.output_dir)

    try:
        if args.action == 'import':
            if not args.csv or not Path(args.csv).is_file():
                phish.logger.error("Valid CSV file required for import.")
                sys.exit(1)
            phish.import_csv(args.csv)
        elif args.action == 'scrape':
            phish.scrape_phishtank(limit=10)
        elif args.action == 'query':
            results = phish.query_data(args.url, args.domain, args.ip, args.date_from, args.date_to)
            if results:
                phish.export_results(results)
                if args.verbose:
                    for result in results[:5]:
                        phish.logger.info(f"URL: {result['url']}, Domain: {result['domain']}, Status: {result['status']}")
                    if len(results) > 5:
                        phish.logger.info(f"... {len(results) - 5} more results ...")
            else:
                phish.logger.warning("No results found.")
        elif args.action == 'update':
            if not args.url or not args.status:
                phish.logger.error("URL and status required for update.")
                sys.exit(1)
            phish.update_status(args.url, args.status)
        elif args.action == 'report':
            phish.generate_report()
        elif args.action == 'plot':
            phish.plot_trends()

    finally:
        phish.close()

if __name__ == "__main__":
    main()