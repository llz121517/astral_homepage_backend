# tests/test_session.py
import pytest
import time
import sqlite3
from unittest.mock import patch, MagicMock
from app.core.session import verify_session


class TestVerifySession:
    """会话验证功能测试"""

    @pytest.fixture
    def mock_conn(self):
        """模拟数据库连接"""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE sessions (
                sid TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                expire_ts REAL NOT NULL
            )
        """)
        return conn

    @pytest.fixture
    def mock_cursor(self, mock_conn):
        """模拟数据库游标"""
        return mock_conn.cursor()

    def test_verify_session_with_empty_id(self):
        """测试空 session_id 返回 None"""
        result = verify_session("")
        assert result is None

        result = verify_session(None)
        assert result is None

    def test_verify_session_with_valid_session(self, mock_conn, mock_cursor):
        """测试有效的 session_id 返回用户名"""
        # 准备测试数据
        valid_sid = "test-session-123"
        username = "admin"
        future_time = time.time() + 3600  # 1小时后过期

        mock_conn.execute(
            "INSERT INTO sessions (sid, username, expire_ts) VALUES (?, ?, ?)",
            (valid_sid, username, future_time)
        )
        mock_conn.commit()

        # 模拟 get_cache_conn 返回我们的测试连接
        with patch('app.core.session.get_cache_conn', return_value=mock_conn):
            result = verify_session(valid_sid)
            assert result == username

    def test_verify_session_with_expired_session(self, mock_conn, mock_cursor):
        """测试过期的 session_id 返回 None"""
        # 准备测试数据 - 已过期的会话
        expired_sid = "expired-session-456"
        past_time = time.time() - 3600  # 1小时前过期

        mock_conn.execute(
            "INSERT INTO sessions (sid, username, expire_ts) VALUES (?, ?, ?)",
            (expired_sid, "admin", past_time)
        )
        mock_conn.commit()

        # 模拟 get_cache_conn 返回我们的测试连接
        with patch('app.core.session.get_cache_conn', return_value=mock_conn):
            result = verify_session(expired_sid)
            assert result is None

    def test_verify_session_with_nonexistent_session(self, mock_conn):
        """测试不存在的 session_id 返回 None"""
        nonexistent_sid = "nonexistent-session-789"

        # 模拟 get_cache_conn 返回我们的测试连接
        with patch('app.core.session.get_cache_conn', return_value=mock_conn):
            result = verify_session(nonexistent_sid)
            assert result is None

    def test_verify_session_sql_injection_protection(self, mock_conn):
        """测试 SQL 注入防护"""
        malicious_sid = "'; DROP TABLE sessions; --"

        # 模拟 get_cache_conn 返回我们的测试连接
        with patch('app.core.session.get_cache_conn', return_value=mock_conn):
            result = verify_session(malicious_sid)
            # 应该安全地返回 None，而不是执行恶意 SQL
            assert result is None
            # 验证表仍然存在
            cursor = mock_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
            assert cursor.fetchone() is not None
