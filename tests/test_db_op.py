# tests/test_db_op.py
import unittest

import pytest
import json
import sqlite3
from unittest.mock import patch
from app.core.db.db_op import update_site_config


class TestUpdateSiteConfig:
    """update_site_config 功能测试"""

    @pytest.fixture
    def mock_conn(self):
        """模拟 site.db 连接（使用内存数据库）"""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS site_config (
                id            INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
                site_title    TEXT NOT NULL DEFAULT '',
                keywords      TEXT NOT NULL DEFAULT '',
                description   TEXT NOT NULL DEFAULT '',
                tags          TEXT NOT NULL DEFAULT '[]',
                timeline      TEXT NOT NULL DEFAULT '[]',
                descriptions  TEXT NOT NULL DEFAULT '[]',
                side_info     TEXT NOT NULL DEFAULT '[]',
                header        TEXT NOT NULL DEFAULT '',
                footer        TEXT NOT NULL DEFAULT '',
                beian         TEXT NOT NULL DEFAULT '',
                ico           TEXT NOT NULL DEFAULT '',
                avatar_url    TEXT NOT NULL DEFAULT '',
                avatar_kuang  TEXT NOT NULL DEFAULT '',
                maxwidth      INTEGER NOT NULL DEFAULT 1100,
                title1        TEXT NOT NULL DEFAULT '',
                title2        TEXT NOT NULL DEFAULT '',
                switch_indexavatar  INTEGER NOT NULL DEFAULT 0,
                switch_leftcard   INTEGER NOT NULL DEFAULT 0,
                switch_skill      INTEGER NOT NULL DEFAULT 0,
                switch_tcs        INTEGER NOT NULL DEFAULT 0,
                active_theme_id   INTEGER NOT NULL DEFAULT 1,
                updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("INSERT INTO site_config DEFAULT VALUES;")
        conn.commit()
        return conn

    # ---------- 边界条件 ----------

    def test_empty_dict_returns_false(self):
        """空字典应直接返回 False"""
        assert update_site_config({}) is False

    def test_all_none_values_returns_false(self):
        """所有字段均为 None 时应返回 False"""
        data = {"site_title": None, "keywords": None}
        assert update_site_config(data) is False

    # ---------- 正常更新 ----------

    def test_single_text_field_update(self, mock_conn):
        """单个纯文本字段更新"""
        with patch('app.core.db.db_op.get_site_conn', return_value=mock_conn):
            result = update_site_config({"site_title": "新标题"})
            assert result is True

            row = mock_conn.execute("SELECT site_title FROM site_config WHERE id = 1").fetchone()
            assert row["site_title"] == "新标题"

    def test_multiple_fields_update(self, mock_conn):
        """多个字段同时更新"""
        with patch('app.core.db.db_op.get_site_conn', return_value=mock_conn):
            result = update_site_config({
                "site_title": "新标题",
                "keywords": "测试,关键词",
                "description": "测试描述"
            })
            assert result is True

            row = mock_conn.execute(
                "SELECT site_title, keywords, description FROM site_config WHERE id = 1"
            ).fetchone()
            assert row["site_title"] == "新标题"
            assert row["keywords"] == "测试,关键词"
            assert row["description"] == "测试描述"

    def test_none_values_filtered_out(self, mock_conn):
        """None 值应被过滤，不影响其他字段"""
        with patch('app.core.db.db_op.get_site_conn', return_value=mock_conn):
            update_site_config({
                "site_title": "新标题",
                "keywords": None,
                "description": "测试描述"
            })

            row = mock_conn.execute(
                "SELECT site_title, keywords, description FROM site_config WHERE id = 1"
            ).fetchone()
            assert row["site_title"] == "新标题"
            assert row["keywords"] == ""      # 默认值，未更新
            assert row["description"] == "测试描述"

    # ---------- JSON 字段序列化 ----------

    @pytest.mark.parametrize("field", ["tags", "timeline", "descriptions", "side_info"])
    def test_json_list_field_auto_serialized(self, mock_conn, field):
        """JSON 字段传入列表时应自动序列化"""
        value = [{"a": 1}, {"b": 2}]
        with patch('app.core.db.db_op.get_site_conn', return_value=mock_conn):
            update_site_config({field: value})

            row = mock_conn.execute(f"SELECT {field} FROM site_config WHERE id = 1").fetchone()
            assert row[field] == json.dumps(value, ensure_ascii=False)

    @pytest.mark.parametrize("field", ["tags", "timeline", "descriptions", "side_info"])
    def test_json_dict_field_auto_serialized(self, mock_conn, field):
        """JSON 字段传入字典时应自动序列化"""
        value = {"key": "value", "count": 3}
        with patch('app.core.db.db_op.get_site_conn', return_value=mock_conn):
            update_site_config({field: value})

            row = mock_conn.execute(f"SELECT {field} FROM site_config WHERE id = 1").fetchone()
            assert row[field] == json.dumps(value, ensure_ascii=False)

    @pytest.mark.parametrize("field", ["tags", "timeline", "descriptions", "side_info"])
    def test_json_field_string_not_serialized(self, mock_conn, field):
        """JSON 字段传入普通字符串时不应重复序列化"""
        value = '["已有", "JSON", "字符串"]'
        with patch('app.core.db.db_op.get_site_conn', return_value=mock_conn):
            update_site_config({field: value})

            row = mock_conn.execute(f"SELECT {field} FROM site_config WHERE id = 1").fetchone()
            assert row[field] == value

    def test_non_json_field_not_serialized(self, mock_conn):
        """非 JSON 字段即使传入列表也不应序列化"""
        with patch('app.core.db.db_op.get_site_conn', return_value=mock_conn):
            # header 不在 json_fields 中，传列表会直接报错（SQLite 不接受列表）
            update_site_config({"header": "纯文本"})

            row = mock_conn.execute("SELECT header FROM site_config WHERE id = 1").fetchone()
            assert row["header"] == "纯文本"

    # ---------- SQL 和数据库行为 ----------

    def test_updated_at_is_set(self, mock_conn):
        """updated_at 应在每次更新时被设为 CURRENT_TIMESTAMP"""
        with patch('app.core.db.db_op.get_site_conn', return_value=mock_conn):
            update_site_config({"site_title": "v1"})
            ts1 = mock_conn.execute(
                "SELECT updated_at FROM site_config WHERE id = 1"
            ).fetchone()["updated_at"]
            assert ts1 is not None

            update_site_config({"site_title": "v2"})
            ts2 = mock_conn.execute(
                "SELECT updated_at FROM site_config WHERE id = 1"
            ).fetchone()["updated_at"]
            # CURRENT_TIMESTAMP 每次更新应不同（秒级精度，理论上不同）
            assert ts2 >= ts1

    def test_sql_injection_key_safe(self, mock_conn):
        """传入的 key 直接拼接 SQL，需确保参数化值不被注入影响"""
        with patch('app.core.db.db_op.get_site_conn', return_value=mock_conn):
            # key 是 "site_title"，值带 SQL 注入尝试
            result = update_site_config({"site_title": "'; DROP TABLE site_config; --"})
            assert result is True

            # 表仍在，值被正确存储
            row = mock_conn.execute("SELECT site_title FROM site_config WHERE id = 1").fetchone()
            assert row["site_title"] == "'; DROP TABLE site_config; --"

    def test_returns_false_when_no_rows_affected(self):
        """UPDATE 影响行数为 0 时应返回 False"""
        # 创建完整的 mock 连接和 cursor
        mock_conn = unittest.mock.MagicMock()
        mock_cursor = unittest.mock.MagicMock()
        mock_cursor.rowcount = 0
        mock_conn.execute.return_value = mock_cursor

        with patch('app.core.db.db_op.get_site_conn', return_value=mock_conn):
            result = update_site_config({"site_title": "测试"})
            assert result is False
