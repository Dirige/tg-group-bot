import pymysql
import time
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, config):
        self.cfg = config
        self._ensure_db()
        self._init_tables()

    def _conn(self):
        return pymysql.connect(
            host=self.cfg["host"],
            port=self.cfg.get("port", 3306),
            user=self.cfg.get("user", "root"),
            password=self.cfg.get("password", ""),
            database=self.cfg["database"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

    def _ensure_db(self):
        conn = pymysql.connect(
            host=self.cfg["host"],
            port=self.cfg.get("port", 3306),
            user=self.cfg.get("user", "root"),
            password=self.cfg.get("password", ""),
            charset="utf8mb4",
            autocommit=True,
        )
        try:
            with conn.cursor() as cur:
                cur.execute(
                    ("CREATE DATABASE IF NOT EXISTS " + chr(96) + "%s" + chr(96) + " CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    % (self.cfg["database"],)
                )
        finally:
            conn.close()

    def _init_tables(self):
        B = chr(96)
        def Q(name):
            return B + name + B
        tables = [
            ("警告记录", [("用户ID", "BIGINT NOT NULL"), ("群组ID", "BIGINT NOT NULL"), ("次数", "INT DEFAULT 0")], "PRIMARY KEY (" + Q("用户ID") + ", " + Q("群组ID") + ")"),
            ("待验证", [("用户ID", "BIGINT NOT NULL"), ("群组ID", "BIGINT NOT NULL"), ("验证码", "VARCHAR(10) NOT NULL"), ("过期时间", "DOUBLE NOT NULL"), ("失败次数", "INT DEFAULT 0"), ("刷新次数", "INT DEFAULT 0")], "PRIMARY KEY (" + Q("用户ID") + ", " + Q("群组ID") + ")"),
            ("禁言用户", [("用户ID", "BIGINT NOT NULL"), ("群组ID", "BIGINT NOT NULL"), ("解除时间", "DOUBLE NOT NULL")], "PRIMARY KEY (" + Q("用户ID") + ", " + Q("群组ID") + ")"),
            ("群组设置", [("群组ID", "BIGINT NOT NULL PRIMARY KEY"), ("入群欢迎", "TINYINT DEFAULT 1"), ("入群验证", "TINYINT DEFAULT 1"), ("反垃圾开关", "TINYINT DEFAULT 1")], None),
            ("垃圾命中", [("用户ID", "BIGINT NOT NULL"), ("群组ID", "BIGINT NOT NULL"), ("命中次数", "INT DEFAULT 0"), ("最后命中", "DOUBLE DEFAULT 0")], "PRIMARY KEY (" + Q("用户ID") + ", " + Q("群组ID") + ")"),
            ("全局黑名单", [("用户ID", "BIGINT NOT NULL PRIMARY KEY"), ("原因", "TEXT"), ("添加时间", "DOUBLE"), ("来源群组", "BIGINT DEFAULT 0")], None),
        ]
        with self._conn() as conn:
            with conn.cursor() as cur:
                for tname, cols, pk in tables:
                    col_defs = ", ".join(Q(c[0]) + " " + c[1] for c in cols)
                    if pk:
                        full = col_defs + ", " + pk
                    else:
                        full = col_defs
                    sql = "CREATE TABLE IF NOT EXISTS " + Q(tname) + " (" + full + ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
                    cur.execute(sql)
        logger.info("数据库表初始化完成")

    def add_warn(self, user_id, chat_id):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO " + chr(96) + "警告记录" + chr(96) + " (" + chr(96) + "用户ID" + chr(96) + "," + chr(96) + "群组ID" + chr(96) + "," + chr(96) + "次数" + chr(96) + ") VALUES (%s,%s,1) "
                    "ON DUPLICATE KEY UPDATE " + chr(96) + "次数" + chr(96) + "=" + chr(96) + "次数" + chr(96) + "+1",
                    (user_id, chat_id))
        return self.get_warns(user_id, chat_id)

    def get_warns(self, user_id, chat_id):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "SELECT " + B + "次数" + B + " FROM " + B + "警告记录" + B + " WHERE " + B + "用户ID" + B + "=%s AND " + B + "群组ID" + B + "=%s",
                    (user_id, chat_id))
                row = cur.fetchone()
                return row["次数"] if row else 0

    def reset_warns(self, user_id, chat_id):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "DELETE FROM " + B + "警告记录" + B + " WHERE " + B + "用户ID" + B + "=%s AND " + B + "群组ID" + B + "=%s",
                    (user_id, chat_id))

    def add_pending(self, user_id, chat_id, code, expire_at):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "INSERT INTO " + B + "待验证" + B + " (" + B + "用户ID" + B + "," + B + "群组ID" + B + "," + B + "验证码" + B + "," + B + "过期时间" + B + "," + B + "失败次数" + B + "," + B + "刷新次数" + B + ") "
                    "VALUES (%s,%s,%s,%s,0,0) "
                    "ON DUPLICATE KEY UPDATE " + B + "验证码" + B + "=VALUES(" + B + "验证码" + B + "), " + B + "过期时间" + B + "=VALUES(" + B + "过期时间" + B + "), " + B + "失败次数" + B + "=0, " + B + "刷新次数" + B + "=0",
                    (user_id, chat_id, code, expire_at))

    def get_pending(self, user_id, chat_id):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "SELECT * FROM " + B + "待验证" + B + " WHERE " + B + "用户ID" + B + "=%s AND " + B + "群组ID" + B + "=%s",
                    (user_id, chat_id))
                return cur.fetchone()

    def remove_pending(self, user_id, chat_id):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "DELETE FROM " + B + "待验证" + B + " WHERE " + B + "用户ID" + B + "=%s AND " + B + "群组ID" + B + "=%s",
                    (user_id, chat_id))

    def get_pending_count(self, chat_id):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "SELECT COUNT(*) AS cnt FROM " + B + "待验证" + B + " WHERE " + B + "群组ID" + B + "=%s",
                    (chat_id,))
                return cur.fetchone()["cnt"]

    def increment_verify_fail(self, user_id, chat_id):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "UPDATE " + B + "待验证" + B + " SET " + B + "失败次数" + B + "=" + B + "失败次数" + B + "+1 "
                    "WHERE " + B + "用户ID" + B + "=%s AND " + B + "群组ID" + B + "=%s",
                    (user_id, chat_id))
                cur.execute(
                    "SELECT " + B + "失败次数" + B + " FROM " + B + "待验证" + B + " WHERE " + B + "用户ID" + B + "=%s AND " + B + "群组ID" + B + "=%s",
                    (user_id, chat_id))
                row = cur.fetchone()
                return row["失败次数"] if row else 0

    def increment_verify_refresh(self, user_id, chat_id):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "UPDATE " + B + "待验证" + B + " SET " + B + "刷新次数" + B + "=" + B + "刷新次数" + B + "+1 "
                    "WHERE " + B + "用户ID" + B + "=%s AND " + B + "群组ID" + B + "=%s",
                    (user_id, chat_id))

    def add_mute(self, user_id, chat_id, until_ts):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "INSERT INTO " + B + "禁言用户" + B + " (" + B + "用户ID" + B + "," + B + "群组ID" + B + "," + B + "解除时间" + B + ") VALUES (%s,%s,%s) "
                    "ON DUPLICATE KEY UPDATE " + B + "解除时间" + B + "=VALUES(" + B + "解除时间" + B + ")",
                    (user_id, chat_id, until_ts))

    def remove_mute(self, user_id, chat_id):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "DELETE FROM " + B + "禁言用户" + B + " WHERE " + B + "用户ID" + B + "=%s AND " + B + "群组ID" + B + "=%s",
                    (user_id, chat_id))

    def add_to_blacklist(self, user_id, reason="", source_chat_id=0):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "INSERT INTO " + B + "全局黑名单" + B + " (" + B + "用户ID" + B + "," + B + "原因" + B + "," + B + "添加时间" + B + "," + B + "来源群组" + B + ") VALUES (%s,%s,%s,%s) "
                    "ON DUPLICATE KEY UPDATE " + B + "原因" + B + "=VALUES(" + B + "原因" + B + "), " + B + "添加时间" + B + "=VALUES(" + B + "添加时间" + B + "), " + B + "来源群组" + B + "=VALUES(" + B + "来源群组" + B + ")",
                    (user_id, reason, time.time(), source_chat_id))

    def is_blacklisted(self, user_id):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "SELECT 1 FROM " + B + "全局黑名单" + B + " WHERE " + B + "用户ID" + B + "=%s",
                    (user_id,))
                return cur.fetchone() is not None

    def get_blacklist(self):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute("SELECT * FROM " + B + "全局黑名单" + B)
                return cur.fetchall()

    def search_blacklist(self, keyword):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "SELECT * FROM " + B + "全局黑名单" + B + " WHERE " + B + "原因" + B + " LIKE %s",
                    ("%" + keyword + "%",))
                return cur.fetchall()

    def get_settings(self, chat_id):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute("SELECT * FROM " + B + "群组设置" + B + " WHERE " + B + "群组ID" + B + "=%s", (chat_id,))
                row = cur.fetchone()
                if not row:
                    return {"welcome_enabled": True, "verify_enabled": True, "antispam_enabled": True}
                return {
                    "welcome_enabled": bool(row["入群欢迎"]),
                    "verify_enabled": bool(row["入群验证"]),
                    "antispam_enabled": bool(row["反垃圾开关"]),
                }

    def update_setting(self, chat_id, key, value):
        col_map = {
            "welcome_enabled": "入群欢迎",
            "verify_enabled": "入群验证",
            "antispam_enabled": "反垃圾开关",
        }
        col = col_map.get(key)
        if not col:
            return
        B = chr(96)
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO " + B + "群组设置" + B + " (" + B + "群组ID" + B + "," + B + col + B + ") VALUES (%s, %s) "
                    "ON DUPLICATE KEY UPDATE " + B + col + B + "=VALUES(" + B + col + B + ")",
                    (chat_id, int(value)))

    def add_spam_hit(self, user_id, chat_id):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "INSERT INTO " + B + "垃圾命中" + B + " (" + B + "用户ID" + B + "," + B + "群组ID" + B + "," + B + "命中次数" + B + "," + B + "最后命中" + B + ") VALUES (%s,%s,1,%s) "
                    "ON DUPLICATE KEY UPDATE " + B + "命中次数" + B + "=" + B + "命中次数" + B + "+1, " + B + "最后命中" + B + "=VALUES(" + B + "最后命中" + B + ")",
                    (user_id, chat_id, time.time()))

    def get_spam_hits(self, user_id, chat_id):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "SELECT " + B + "命中次数" + B + "," + B + "最后命中" + B + " FROM " + B + "垃圾命中" + B + " WHERE " + B + "用户ID" + B + "=%s AND " + B + "群组ID" + B + "=%s",
                    (user_id, chat_id))
                row = cur.fetchone()
                return (row["命中次数"], row["最后命中"]) if row else (0, 0)

    def reset_spam_hits(self, user_id, chat_id):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute(
                    "DELETE FROM " + B + "垃圾命中" + B + " WHERE " + B + "用户ID" + B + "=%s AND " + B + "群组ID" + B + "=%s",
                    (user_id, chat_id))

    def get_user_info(self, user_id):
        with self._conn() as conn:
            with conn.cursor() as cur:
                B = chr(96)
                cur.execute("SELECT * FROM " + B + "全局黑名单" + B + " WHERE " + B + "用户ID" + B + "=%s", (user_id,))
                return cur.fetchone()
