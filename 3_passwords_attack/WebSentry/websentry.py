#!/usr/bin/env python3

import argparse
import logging
import sys
import time
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import ssl
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('websentry.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP server to handle multiple requests."""
    pass

class WebSentryHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.websentry = kwargs.pop('websentry')
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')

    def handle_request(self, method):
        """Handle incoming HTTP requests."""
        request_data = {
            'method': method,
            'path': self.path,
            'headers': dict(self.headers),
            'body': None,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # Read POST body
        if method == 'POST':
            content_length = int(self.headers.get('Content-Length', 0))
            request_data['body'] = self.rfile.read(content_length).decode('utf-8', errors='ignore')

        # Log and store request
        logger.info(f"Intercepted {method} request: {self.path}")
        self.websentry.store_request(request_data)

        # Forward request to target
        response = self.websentry.forward_request(request_data)

        # Send response back to client
        self.send_response(response['status'])
        for header, value in response['headers'].items():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(response['body'].encode('utf-8'))

        # Analyze for vulnerabilities
        if self.websentry.analyze:
            self.websentry.analyze_request(request_data, response)

class WebSentry:
    def __init__(self, listen_host: str, listen_port: int, target_url: str, threads: int, 
                 fuzz: bool, spider: bool, analyze: bool, quiet: bool = False):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.target_url = target_url.rstrip('/')
        self.threads = threads
        self.fuzz = fuzz
        self.spider = spider
        self.analyze = analyze
        self.quiet = quiet
        self.requests = []
        self.vulnerabilities = []
        self.urls = set([target_url])
        self.output_dir = 'websentry-output'
        self.output_file = os.path.join(self.output_dir, 
            f"scan_{listen_host}_{listen_port}_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir, 
            f"scan_{listen_host}_{listen_port}_{time.strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs(self.output_dir, exist_ok=True)
        self.db_file = os.path.join(self.output_dir, 'websentry.db')
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('websentry.log')]

    def init_db(self):
        """Initialize SQLite database for storing requests."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    method TEXT,
                    path TEXT,
                    headers TEXT,
                    body TEXT,
                    timestamp TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    details TEXT,
                    request_id INTEGER,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def store_request(self, request_data: dict):
        """Store request in database."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO requests (method, path, headers, body, timestamp) VALUES (?, ?, ?, ?, ?)',
                (request_data['method'], request_data['path'], json.dumps(request_data['headers']),
                 request_data['body'], request_data['timestamp'])
            )
            conn.commit()
            request_data['id'] = cursor.lastrowid
        self.requests.append(request_data)

    def forward_request(self, request_data: dict) -> dict:
        """Forward request to target server."""
        try:
            url = f"{self.target_url}{request_data['path']}"
            headers = request_data['headers'].copy()
            headers.pop('Host', None)  # Remove Host header to avoid conflicts
            method = request_data['method'].lower()
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=request_data['body'],
                timeout=5,
                allow_redirects=False
            )
            return {
                'status': response.status_code,
                'headers': dict(response.headers),
                'body': response.text
            }
        except Exception as e:
            logger.error(f"Error forwarding request: {e}")
            return {
                'status': 500,
                'headers': {'Content-Type': 'text/plain'},
                'body': f"Error: {str(e)}"
            }

    def spider_site(self):
        """Crawl the target site to discover URLs."""
        logger.info(f"Spidering {self.target_url}")
        visited = set()
        to_visit = set([self.target_url])

        while to_visit:
            url = to_visit.pop()
            if url in visited:
                continue
            visited.add(url)
            try:
                response = requests.get(url, timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urllib.parse.urljoin(self.target_url, href)
                    if full_url.startswith(self.target_url) and full_url not in visited:
                        to_visit.add(full_url)
                        self.urls.add(full_url)
                        logger.info(f"Found URL: {full_url}")
            except Exception as e:
                logger.error(f"Error spidering {url}: {e}")

    def fuzz_request(self, request_data: dict):
        """Fuzz request parameters for vulnerabilities."""
        payloads = [
            "<script>alert('XSS')</script>",  # XSS
            "' OR '1'='1",  # SQL Injection
            "../../etc/passwd",  # Path Traversal
            "<?php phpinfo(); ?>"  # Code Injection
        ]
        results = []

        parsed = urllib.parse.urlparse(request_data['path'])
        params = urllib.parse.parse_qs(parsed.query)
        for param in params:
            for payload in payloads:
                new_params = params.copy()
                new_params[param] = payload
                new_query = urllib.parse.urlencode(new_params, doseq=True)
                new_path = parsed.path + '?' + new_query
                new_request = request_data.copy()
                new_request['path'] = new_path

                response = self.forward_request(new_request)
                result = self.analyze_response(response, payload)
                if result:
                    results.append(result)
                    logger.info(f"Potential vulnerability: {result['type']} - {result['details']}")
                    self.vulnerabilities.append(result)
        return results

    def analyze_response(self, response: dict, payload: str) -> dict:
        """Analyze response for potential vulnerabilities."""
        body = response['body'].lower()
        if payload.lower() in body:
            return {
                'type': 'Potential Vulnerability',
                'details': f"Payload {payload} reflected in response",
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        if 'sql syntax' in body or 'mysql' in body:
            return {
                'type': 'SQL Injection',
                'details': f"SQL error detected with payload {payload}",
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        if 'document.write' in body or 'alert(' in body:
            return {
                'type': 'XSS',
                'details': f"JavaScript execution detected with payload {payload}",
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        return None

    def analyze_request(self, request_data: dict, response: dict):
        """Analyze request and response for vulnerabilities."""
        if self.fuzz:
            results = self.fuzz_request(request_data)
            for result in results:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT INTO vulnerabilities (type, details, request_id, timestamp) VALUES (?, ?, ?, ?)',
                        (result['type'], result['details'], request_data['id'], result['timestamp'])
                    )
                    conn.commit()

    def run(self):
        """Run the WebSentry proxy server."""
        logger.info(f"Starting WebSentry proxy on {self.listen_host}:{self.listen_port}")
        if self.spider:
            self.spider_site()

        server = ThreadingHTTPServer((self.listen_host, self.listen_port), 
            lambda *args, **kwargs: WebSentryHandler(*args, websentry=self, **kwargs))
        
        # Optional SSL setup (self-signed for testing)
        """
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile='server.crt', keyfile='server.key')
        server.socket = context.wrap_socket(server.socket, server_side=True)
        """

        try:
            server.serve