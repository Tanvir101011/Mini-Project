#!/usr/bin/env python3

import argparse
import logging
import sys
import os
import pyodbc
import pandas as pd
import sqlite3
import json
import time
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mdb_query.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MDBQuery:
    def __init__(self, mdb_file: str, output_dir: str = 'mdb_query-output', quiet: bool = False):
        self.mdb_file = os.path.abspath(mdb_file)
        self.output_dir = os.path.abspath(output_dir)
        self.log_dir = os.path.join(self.output_dir, 'logs')
        self.json_file = os.path.join(self.log_dir,
            f"mdb_query_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.log_dir, 'mdb_query.db')
        os.makedirs(self.log_dir, exist_ok=True)
        self.actions = []
        self.conn = None
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('mdb_query.log')]

    def init_db(self):
        """Initialize SQLite database for storing action logs."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mdb_file TEXT,
                    action TEXT,
                    status TEXT,
                    output_path TEXT,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def store_action(self, action: str, status: str, output_path: str = ''):
        """Store action details in database."""
        timestamp = time.strftime('%Y-%m-d %H:%M:%S')
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO actions (mdb_file, action, status, output_path, timestamp) '
                'VALUES (?, ?, ?, ?, ?)',
                (self.mdb_file, action, status, output_path, timestamp)
            )
            conn.commit()
        self.actions.append({
            'mdb_file': self.mdb_file,
            'action': action,
            'status': status,
            'output_path': output_path,
            'timestamp': timestamp
        })

    def connect(self):
        """Connect to MDB file using MDB Tools ODBC driver."""
        try:
            if not os.path.exists(self.mdb_file):
                raise FileNotFoundError(f"MDB file not found: {self.mdb_file}")
            conn_str = f"DRIVER={{MDBTools}};DBQ={self.mdb_file};"
            self.conn = pyodbc.connect(conn_str)
            logger.info(f"Connected to MDB file: {self.mdb_file}")
            self.store_action("Connect", f"Connected to {self.mdb_file}")
        except pyodbc.Error as e:
            logger.error(f"Connection failed: {e}")
            self.store_action("Connect", f"Connection failed: {e}")
            sys.exit(1)

    def list_tables(self):
        """List all tables in the MDB file."""
        try:
            if not self.conn:
                self.connect()
            cursor = self.conn.cursor()
            tables = [table.table_name for table in cursor.tables(tableType='TABLE')]
            if tables:
                logger.info(f"Tables found: {', '.join(tables)}")
                self.store_action("List Tables", f"Tables: {', '.join(tables)}")
                return tables
            else:
                logger.warning("No tables found in MDB file")
                self.store_action("List Tables", "No tables found")
                return []
        except pyodbc.Error as e:
            logger.error(f"Error listing tables: {e}")
            self.store_action("List Tables", f"Error: {e}")
            return []

    def execute_query(self, query: str, output_file: Optional[str] = None, format: str = 'csv'):
        """Execute SQL query and optionally save results."""
        try:
            if not self.conn:
                self.connect()
            cursor = self.conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description] if cursor.description else []
            results = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in results] if results else []

            if data:
                logger.info(f"Query returned {len(data)} rows")
                if output_file:
                    output_path = os.path.join(self.output_dir, output_file)
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    if format == 'csv':
                        df = pd.DataFrame(data)
                        df.to_csv(output_path, index=False)
                        logger.info(f"Results saved to {output_path}")
                        self.store_action("Execute Query", f"Query results saved to {output_path}", output_path)
                    elif format == 'sqlite':
                        with sqlite3.connect(output_path) as conn:
                            df = pd.DataFrame(data)
                            table_name = os.path.splitext(os.path.basename(output_path))[0]
                            df.to_sql(table_name, conn, if_exists='replace', index=False)
                        logger.info(f"Results saved to SQLite: {output_path}")
                        self.store_action("Execute Query", f"Query results saved to {output_path}", output_path)
                else:
                    logger.info(f"Query results: {json.dumps(data[:5], indent=2)}")
                    self.store_action("Execute Query", f"Query returned {len(data)} rows")
            else:
                logger.warning("Query returned no results")
                self.store_action("Execute Query", "No results")
            cursor.close()
        except pyodbc.Error as e:
            logger.error(f"Query failed: {e}")
            self.store_action("Execute Query", f"Query failed: {e}")

    def save_results(self):
        """Save action logs to JSON file."""
        with open(self.json_file, 'w') as f:
            json.dump({
                'mdb_file': self.mdb_file,
                'output_dir': self.output_dir,
                'actions': self.actions,
                'timestamp': time.strftime('%Y-%m-d %H:%M:%S')
            }, f, indent=4)
        logger.info(f"Results saved to {self.json_file}")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
            self.store_action("Close", "Connection closed")

def main():
    parser = argparse.ArgumentParser(
        description="MDBQuery: Tool for querying Microsoft Access (MDB) databases.",
        epilog="Example: ./mdb_query.py -f database.mdb -a list"
    )
    parser.add_argument('-f', '--file', required=True, help="Path to MDB file")
    parser.add_argument('-a', '--action', choices=['list', 'query'], required=True,
                        help="Action to perform (list tables, execute query)")
    parser.add_argument('-q', '--query', help="SQL query to execute (for query action)")
    parser.add_argument('-o', '--output', help="Output file for query results")
    parser.add_argument('--format', choices=['csv', 'sqlite'], default='csv',
                        help="Output format (csv, sqlite; default: csv)")
    parser.add_argument('--output-dir', default='mdb_query-output',
                        help="Output directory (default: mdb_query-output)")
    parser.add_argument('--quiet', action='store_true',
                        help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
          MDBQuery v1.0
      MDB Database Tool
    ==============================
    WARNING: Use only on MDB files you own or have explicit permission to access.
    Unauthorized use may violate laws or terms of service.
    ==============================
    """)

    try:
        mdb = MDBQuery(
            mdb_file=args.file,
            output_dir=args.output_dir,
            quiet=args.quiet
        )

        if args.action == 'list':
            mdb.list_tables()
        elif args.action == 'query':
            if not args.query:
                logger.error("Query action requires --query argument")
                sys.exit(1)
            mdb.execute_query(args.query, args.output, args.format)

        mdb.save_results()
        mdb.close()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()