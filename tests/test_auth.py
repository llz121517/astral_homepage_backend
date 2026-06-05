# tests/test_auth.py
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import Request
from fastapi.responses import RedirectResponse
from app.core.auth import admin_jump


class TestAdminJump:
    """管理员页面跳转依赖测试"""

    @pytest.fixture
    def mock_request(self):
        """模拟 FastAPI Request 对象"""
        request = MagicMock(spec=Request)
        return request

    @pytest.mark.asyncio
    async def test_admin_jump_with_valid_session(self, mock_request):
        """测试有效会话时不重定向（返回 None）"""
        # 设置有效的 session_id cookie
        mock_request.cookies = {"session_id": "valid-session-123"}

        # 模拟 verify_session 返回用户名（表示会话有效）
        with patch('app.core.auth.verify_session', return_value="admin"):
            result = await admin_jump(mock_request)
            # 有效会话应该返回 None，允许继续访问
            assert result is None

    @pytest.mark.asyncio
    async def test_admin_jump_without_session(self, mock_request):
        """测试无 session_id 时重定向到登录页"""
        # 没有 session_id cookie
        mock_request.cookies = {}

        result = await admin_jump(mock_request)

        # 应该重定向到登录页
        assert isinstance(result, RedirectResponse)
        assert result.headers["location"] == "/login"
        assert result.status_code == 302

    @pytest.mark.asyncio
    async def test_admin_jump_with_empty_session_id(self, mock_request):
        """测试空 session_id 时重定向到登录页"""
        # session_id 为空字符串
        mock_request.cookies = {"session_id": ""}

        result = await admin_jump(mock_request)

        # 应该重定向到登录页
        assert isinstance(result, RedirectResponse)
        assert result.headers["location"] == "/login"
        assert result.status_code == 302

    @pytest.mark.asyncio
    async def test_admin_jump_with_invalid_session(self, mock_request):
        """测试无效 session_id 时重定向到登录页"""
        # 设置无效的 session_id
        mock_request.cookies = {"session_id": "invalid-session-456"}

        # 模拟 verify_session 返回 None（表示会话无效）
        with patch('app.core.auth.verify_session', return_value=None):
            result = await admin_jump(mock_request)

            # 应该重定向到登录页
            assert isinstance(result, RedirectResponse)
            assert result.headers["location"] == "/login"
            assert result.status_code == 302

    @pytest.mark.asyncio
    async def test_admin_jump_with_expired_session(self, mock_request):
        """测试过期 session_id 时重定向到登录页"""
        # 设置过期的 session_id
        mock_request.cookies = {"session_id": "expired-session-789"}

        # 模拟 verify_session 返回 None（表示会话已过期）
        with patch('app.core.auth.verify_session', return_value=None):
            result = await admin_jump(mock_request)

            # 应该重定向到登录页
            assert isinstance(result, RedirectResponse)
            assert result.headers["location"] == "/login"
            assert result.status_code == 302

    @pytest.mark.asyncio
    async def test_admin_jump_verify_session_called_correctly(self, mock_request):
        """测试 verify_session 被正确调用"""
        session_id = "test-session-verify"
        mock_request.cookies = {"session_id": session_id}

        with patch('app.core.auth.verify_session', return_value="admin") as mock_verify:
            await admin_jump(mock_request)

            # 验证 verify_session 被调用且参数正确
            mock_verify.assert_called_once_with(session_id)
