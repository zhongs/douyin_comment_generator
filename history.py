import sqlite3
import json
from datetime import datetime

class HistoryManager:
    def __init__(self, db_path='history.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_url TEXT NOT NULL,
                    video_title TEXT,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def add_record(self, video_url, video_title, comment):
        """添加一条历史记录"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'INSERT INTO history (video_url, video_title, comment) VALUES (?, ?, ?)',
                (video_url, video_title, comment)
            )
            conn.commit()

    def get_records(self, limit=50):
        """获取历史记录"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                'SELECT * FROM history ORDER BY created_at DESC LIMIT ?',
                (limit,)
            )
            records = cursor.fetchall()
            return [{
                'id': record['id'],
                'video_url': record['video_url'],
                'video_title': record['video_title'],
                'comment': record['comment'],
                'created_at': record['created_at']
            } for record in records]
