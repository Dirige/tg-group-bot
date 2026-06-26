import sqlite3
import time
from pathlib import Path

class Database:
    def __init__(self, db_path):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
    
    def _init_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS warnings (
                user_id INTEGER,
                chat_id INTEGER,
                count INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, chat_id)
            );
            CREATE TABLE IF NOT EXISTS pending_verify (
                user_id INTEGER,
                chat_id INTEGER,
                code TEXT,
                expire_at REAL,
                fail_count INTEGER DEFAULT 0,
                refresh_count INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, chat_id)
            );
            CREATE TABLE IF NOT EXISTS muted_users (
                user_id INTEGER,
                chat_id INTEGER,
                expire_at REAL,
                PRIMARY KEY (user_id, chat_id)
            );
            CREATE TABLE IF NOT EXISTS group_settings (
                chat_id INTEGER PRIMARY KEY,
                welcome_enabled INTEGER DEFAULT 1,
                verify_enabled INTEGER DEFAULT 1,
                antispam_enabled INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS spam_hits (
                user_id INTEGER,
                chat_id INTEGER,
                hit_count INTEGER DEFAULT 0,
                last_hit_time REAL DEFAULT 0,
                PRIMARY KEY (user_id, chat_id)
            );
            CREATE TABLE IF NOT EXISTS global_blacklist (
                user_id INTEGER PRIMARY KEY,
                reason TEXT DEFAULT '',
                added_at REAL,
                source_chat_id INTEGER DEFAULT 0
            );
        """)
        self.conn.commit()
    
    def add_warn(self, user_id, chat_id):
        self.conn.execute(
            'INSERT INTO warnings (user_id, chat_id, count) VALUES (?, ?, 1) '
            'ON CONFLICT(user_id, chat_id) DO UPDATE SET count = count + 1',
            (user_id, chat_id)
        )
        self.conn.commit()
        return self.get_warns(user_id, chat_id)
    
    def get_warns(self, user_id, chat_id):
        row = self.conn.execute(
            'SELECT count FROM warnings WHERE user_id=? AND chat_id=?',
            (user_id, chat_id)
        ).fetchone()
        return row['count'] if row else 0
    
    def reset_warns(self, user_id, chat_id):
        self.conn.execute(
            'DELETE FROM warnings WHERE user_id=? AND chat_id=?',
            (user_id, chat_id)
        )
        self.conn.commit()
    
    def add_pending(self, user_id, chat_id, code, expire_at):
        self.conn.execute(
            'INSERT OR REPLACE INTO pending_verify VALUES (?, ?, ?, ?)',
            (user_id, chat_id, code, expire_at)
        )
        self.conn.commit()
    
    def get_pending(self, user_id, chat_id):
        row = self.conn.execute(
            'SELECT * FROM pending_verify WHERE user_id=? AND chat_id=?',
            (user_id, chat_id)
        ).fetchone()
        return dict(row) if row else None
    
    def remove_pending(self, user_id, chat_id):
        self.conn.execute(
            'DELETE FROM pending_verify WHERE user_id=? AND chat_id=?',
            (user_id, chat_id)
        )
        self.conn.commit()
    
    def increment_verify_fail(self, user_id, chat_id):
        self.conn.execute(
            'UPDATE pending_verify SET fail_count = fail_count + 1 WHERE user_id=? AND chat_id=?',
            (user_id, chat_id)
        )
        self.conn.commit()
        row = self.conn.execute(
            'SELECT fail_count FROM pending_verify WHERE user_id=? AND chat_id=?',
            (user_id, chat_id)
        ).fetchone()
        return row['fail_count'] if row else 0
    
    def increment_verify_refresh(self, user_id, chat_id):
        self.conn.execute(
            'UPDATE pending_verify SET refresh_count = refresh_count + 1 WHERE user_id=? AND chat_id=?',
            (user_id, chat_id)
        )
        self.conn.commit()
        row = self.conn.execute(
            'SELECT refresh_count FROM pending_verify WHERE user_id=? AND chat_id=?',
            (user_id, chat_id)
        ).fetchone()
        return row['refresh_count'] if row else 0
    
    def add_mute(self, user_id, chat_id, expire_at):
        self.conn.execute(
            'INSERT OR REPLACE INTO muted_users VALUES (?, ?, ?)',
            (user_id, chat_id, expire_at)
        )
        self.conn.commit()
    
    def get_mute(self, user_id, chat_id):
        row = self.conn.execute(
            'SELECT * FROM muted_users WHERE user_id=? AND chat_id=?',
            (user_id, chat_id)
        ).fetchone()
        return dict(row) if row else None
    
    def remove_mute(self, user_id, chat_id):
        self.conn.execute(
            'DELETE FROM muted_users WHERE user_id=? AND chat_id=?',
            (user_id, chat_id)
        )
        self.conn.commit()
    
    def get_expired_mutes(self):
        now = time.time()
        rows = self.conn.execute(
            'SELECT * FROM muted_users WHERE expire_at > 0 AND expire_at < ?',
            (now,)
        ).fetchall()
        return [dict(r) for r in rows]
    
    def get_settings(self, chat_id):
        row = self.conn.execute(
            'SELECT * FROM group_settings WHERE chat_id=?',
            (chat_id,)
        ).fetchone()
        if not row:
            self.conn.execute(
                'INSERT INTO group_settings (chat_id) VALUES (?)',
                (chat_id,)
            )
            self.conn.commit()
            return self.get_settings(chat_id)
        return dict(row)
    
    def update_setting(self, chat_id, key, value):
        allowed = {'welcome_enabled', 'verify_enabled', 'antispam_enabled'}
        if key not in allowed:
            return
        self.conn.execute(
            f'UPDATE group_settings SET [{key}]=? WHERE chat_id=?',
            (value, chat_id)
        )
        self.conn.commit()

    def add_to_blacklist(self, user_id, reason='', source_chat_id=0):
        self.conn.execute(
            'INSERT OR REPLACE INTO global_blacklist (user_id, reason, added_at, source_chat_id) VALUES (?, ?, ?, ?)',
            (user_id, reason, time.time(), source_chat_id)
        )
        self.conn.commit()

    def remove_from_blacklist(self, user_id):
        self.conn.execute(
            'DELETE FROM global_blacklist WHERE user_id=?',
            (user_id,)
        )
        self.conn.commit()

    def is_blacklisted(self, user_id):
        row = self.conn.execute(
            'SELECT * FROM global_blacklist WHERE user_id=?',
            (user_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_blacklist(self, limit=50):
        rows = self.conn.execute(
            'SELECT * FROM global_blacklist ORDER BY added_at DESC LIMIT ?',
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def search_blacklist(self, keyword):
        rows = self.conn.execute(
            'SELECT * FROM global_blacklist WHERE CAST(user_id AS TEXT) LIKE ? OR reason LIKE ?',
            (f'%{keyword}%', f'%{keyword}%')
        ).fetchall()
        return [dict(r) for r in rows]

    def get_all_users(self):
        rows = self.conn.execute(
            'SELECT DISTINCT user_id FROM warnings UNION SELECT DISTINCT user_id FROM pending_verify UNION SELECT DISTINCT user_id FROM muted_users UNION SELECT DISTINCT user_id FROM global_blacklist'
        ).fetchall()
        return [r['user_id'] for r in rows]

    def get_user_info(self, user_id):
        result = {}
        warns = self.conn.execute('SELECT * FROM warnings WHERE user_id=?', (user_id,)).fetchall()
        result['warnings'] = [dict(r) for r in warns]
        pending = self.conn.execute('SELECT * FROM pending_verify WHERE user_id=?', (user_id,)).fetchall()
        result['pending_verify'] = [dict(r) for r in pending]
        muted = self.conn.execute('SELECT * FROM muted_users WHERE user_id=?', (user_id,)).fetchall()
        result['muted'] = [dict(r) for r in muted]
        blacklisted = self.conn.execute('SELECT * FROM global_blacklist WHERE user_id=?', (user_id,)).fetchone()
        result['blacklisted'] = dict(blacklisted) if blacklisted else None
        return result


    def add_spam_hit(self, user_id, chat_id):
        self.conn.execute(
            "INSERT INTO spam_hits (user_id, chat_id, hit_count, last_hit_time) VALUES (?, ?, 1, ?) "
            "ON CONFLICT(user_id, chat_id) DO UPDATE SET hit_count = hit_count + 1, last_hit_time = ?",
            (user_id, chat_id, time.time(), time.time())
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT hit_count FROM spam_hits WHERE user_id=? AND chat_id=?",
            (user_id, chat_id)
        ).fetchone()
        return row["hit_count"] if row else 0

    def reset_spam_hits(self, user_id, chat_id):
        self.conn.execute(
            "DELETE FROM spam_hits WHERE user_id=? AND chat_id=?",
            (user_id, chat_id)
        )
        self.conn.commit()

    def get_spam_hits(self, user_id, chat_id):
        row = self.conn.execute(
            "SELECT hit_count FROM spam_hits WHERE user_id=? AND chat_id=?",
            (user_id, chat_id)
        ).fetchone()
        return row["hit_count"] if row else 0
