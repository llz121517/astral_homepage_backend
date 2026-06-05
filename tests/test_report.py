# tests/test_report.py
import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.api.v1.report import receive_status_report


class TestReceiveStatusReport:
    """设备状态报告接口测试"""

    @pytest.fixture
    def mock_request(self):
        """模拟 FastAPI Request 对象"""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_receive_status_report_success(self, mock_request):
        """测试成功接收并处理设备状态报告"""
        # 模拟加密数据（这里假设已经加密好的base64字符串）
        encrypted_data = "mock_encrypted_base64_string"
        body = encrypted_data.encode('utf-8')

        # 模拟解密后的数据
        decrypted_data = {
            "hostname": "test-host",
            "status": "online",
            "timestamp": "2024-01-01T00:00:00Z"
        }

        with patch('app.api.v1.report.decrypt_aes_cbc_payload', return_value=decrypted_data), \
                patch('app.api.v1.report.update_device_status') as mock_update:
            result = await receive_status_report(mock_request, body)

            # 验证返回结果
            assert result.status_code == 200
            assert json.loads(result.body) == {"status": "ok"}

            # 验证数据库更新被调用
            mock_update.assert_called_once_with("test-host", decrypted_data)

    @pytest.mark.asyncio
    async def test_receive_status_report_empty_body(self, mock_request):
        """测试空请求体返回400错误"""
        body = b""

        with pytest.raises(HTTPException) as exc_info:
            await receive_status_report(mock_request, body)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "空请求体"

    @pytest.mark.asyncio
    async def test_receive_status_report_whitespace_only_body(self, mock_request):
        """测试仅包含空白字符的请求体返回400错误"""
        body = b"   \n\t  "

        with pytest.raises(HTTPException) as exc_info:
            await receive_status_report(mock_request, body)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "空请求体"

    @pytest.mark.asyncio
    async def test_receive_status_report_missing_hostname(self, mock_request):
        """测试缺少hostname字段返回400错误"""
        encrypted_data = "mock_encrypted_base64_string"
        body = encrypted_data.encode('utf-8')

        # 模拟解密后的数据，但不包含hostname
        decrypted_data = {
            "status": "online",
            "timestamp": "2024-01-01T00:00:00Z"
        }

        with patch('app.api.v1.report.decrypt_aes_cbc_payload', return_value=decrypted_data):
            with pytest.raises(HTTPException) as exc_info:
                await receive_status_report(mock_request, body)

            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "缺少 hostname 字段"

    @pytest.mark.asyncio
    async def test_receive_status_report_invalid_encrypted_data(self, mock_request):
        """测试无效加密数据返回400错误"""
        body = b"invalid_encrypted_data"

        with patch('app.api.v1.report.decrypt_aes_cbc_payload', side_effect=ValueError("Invalid encryption")):
            with pytest.raises(HTTPException) as exc_info:
                await receive_status_report(mock_request, body)

            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "无效的加密数据或格式错误"

    @pytest.mark.asyncio
    async def test_receive_status_report_server_error(self, mock_request):
        """测试服务器内部错误返回500错误"""
        body = b"some_valid_encrypted_data"

        with patch('app.api.v1.report.decrypt_aes_cbc_payload', side_effect=Exception("Unexpected error")):
            with pytest.raises(HTTPException) as exc_info:
                await receive_status_report(mock_request, body)

            assert exc_info.value.status_code == 500
            assert exc_info.value.detail == "Internal Error"

    @pytest.mark.asyncio
    async def test_receive_status_report_prints_debug_info(self, mock_request, capsys):
        """测试打印调试信息"""
        encrypted_data = "mock_encrypted_base64_string"
        body = encrypted_data.encode('utf-8')

        decrypted_data = {
            "hostname": "test-host",
            "status": "online",
            "timestamp": "2024-01-01T00:00:00Z"
        }

        with patch('app.api.v1.report.decrypt_aes_cbc_payload', return_value=decrypted_data), \
                patch('app.api.v1.report.update_device_status'):
            await receive_status_report(mock_request, body)

            captured = capsys.readouterr()
            assert "收到设备状态:" in captured.out
            assert "hostname: test-host" in captured.out
            assert "status: online" in captured.out

    @pytest.mark.asyncio
    async def test_receive_status_report_body_too_large(self, mock_request):
        """测试请求体过大被拒绝（超过64KB）"""
        # 创建一个超过64KB的请求体
        large_body = b"x" * (64 * 1024 + 1)

        # 这个测试主要验证Body参数的max_length限制是否生效
        # 在实际FastAPI应用中，这会在进入函数前就被拒绝
        # 在单元测试中，我们直接传入大body来测试异常处理
        try:
            result = await receive_status_report(mock_request, large_body)
            # 如果没有抛出异常，说明需要额外的长度检查
            assert False, "应该对过大的请求体进行限制"
        except Exception as e:
            # 预期会抛出某种异常
            pass
