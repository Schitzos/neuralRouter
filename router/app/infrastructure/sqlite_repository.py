"""
SQLite repository implementation
"""
import sqlite3
import os
from datetime import datetime
from typing import Dict, Any
from ..domain.interfaces.tracer import IRepository


class SQLiteRepository(IRepository):
    """SQLite-based repository for local data persistence"""
    
    def __init__(self, db_path: str = "schitzo.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT UNIQUE,
                    model TEXT,
                    tier TEXT,
                    cost REAL,
                    latency REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    value TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def log_request(self, request_id: str, model: str, tier: str, cost: float, latency: float) -> None:
        """Log a request"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO requests 
                    (request_id, model, tier, cost, latency) 
                    VALUES (?, ?, ?, ?, ?)
                """, (request_id, model, tier, cost, latency))
        except Exception as e:
            print(f"Failed to log request: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Total requests
                total_requests = conn.execute(
                    "SELECT COUNT(*) as count FROM requests"
                ).fetchone()["count"]
                
                # Requests today
                requests_today = conn.execute("""
                    SELECT COUNT(*) as count FROM requests 
                    WHERE DATE(timestamp) = DATE('now')
                """).fetchone()["count"]
                
                # Cost today
                cost_today = conn.execute("""
                    SELECT COALESCE(SUM(cost), 0) as total FROM requests 
                    WHERE DATE(timestamp) = DATE('now')
                """).fetchone()["total"]
                
                # Tier distribution
                tier_stats = conn.execute("""
                    SELECT tier, COUNT(*) as count FROM requests 
                    GROUP BY tier
                """).fetchall()
                
                tier_distribution = {}
                for row in tier_stats:
                    tier_distribution[row["tier"]] = row["count"]
                
                return {
                    "total_requests": total_requests,
                    "requests_today": requests_today,
                    "cost_today_usd": cost_today,
                    "tier_distribution": tier_distribution
                }
                
        except Exception as e:
            print(f"Failed to get stats: {e}")
            return {
                "total_requests": 0,
                "requests_today": 0,
                "cost_today_usd": 0.0,
                "tier_distribution": {}
            }