# tests/test_state.py
import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from app.core.state import _matches_condition, map_device_status


class TestMatchesCondition:
    """条件匹配功能测试"""

    def test_exact_match_success(self):
        """测试精确匹配成功"""
        assert _matches_condition("admin", "admin") is True
        assert _matches_condition(123, 123) is True

    def test_exact_match_failure(self):
        """测试精确匹配失败"""
        assert _matches_condition("admin", "user") is False
        assert _matches_condition(123, 456) is False

    def test_none_value_returns_false(self):
        """测试 None 值返回 False"""
        assert _matches_condition(None, "admin") is False
        assert _matches_condition(None, {"contains": "test"}) is False

    def test_contains_condition_success(self):
        """测试子串包含条件成功"""
        assert _matches_condition("Administrator", {"contains": "Admin"}) is True
        assert _matches_condition("hello world", {"contains": "world"}) is True

    def test_contains_condition_failure(self):
        """测试子串包含条件失败"""
        assert _matches_condition("User", {"contains": "Admin"}) is False
        assert _matches_condition(123, {"contains": "test"}) is False  # 非字符串类型

    def test_regex_condition_success(self):
        """测试正则匹配条件成功"""
        assert _matches_condition("Admin123", {"regex": "^Admin\\d+$"}) is True
        assert _matches_condition("test@example.com", {"regex": "^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$"}) is True

    def test_regex_condition_failure(self):
        """测试正则匹配条件失败"""
        assert _matches_condition("User123", {"regex": "^Admin\\d+$"}) is False
        assert _matches_condition(123, {"regex": "^\\d+$"}) is False  # 非字符串类型

    def test_in_condition_success(self):
        """测试列表包含条件成功"""
        assert _matches_condition("online", {"in": ["online", "active"]}) is True
        assert _matches_condition(1, {"in": [1, 2, 3]}) is True

    def test_in_condition_failure(self):
        """测试列表包含条件失败"""
        assert _matches_condition("offline", {"in": ["online", "active"]}) is False
        assert _matches_condition(4, {"in": [1, 2, 3]}) is False

    def test_unsupported_condition_raises_error(self):
        """测试不支持的条件类型抛出异常"""
        with pytest.raises(ValueError, match="不支持的条件类型"):
            _matches_condition("value", {"unknown": "condition"})


class TestMapDeviceStatus:
    """设备状态映射功能测试"""

    @pytest.fixture
    def mock_rules(self):
        """模拟匹配规则"""
        return [
            {
                "conditions": {"status": "online"},
                "description": "设备在线"
            },
            {
                "conditions": {"status": "offline"},
                "description": "设备离线"
            },
            {
                "conditions": {"hostname": {"contains": "server"}},
                "description": "服务器设备"
            }
        ]

    @pytest.fixture
    def mock_default_description(self):
        """模拟默认描述"""
        return "未知状态"

    def test_empty_input_returns_none(self):
        """测试空输入返回 None"""
        assert map_device_status({}) is None
        assert map_device_status(None) is None

    def test_basic_fields_extraction(self, mock_rules, mock_default_description):
        """测试基础字段提取"""
        device_status = {
            "hostname": "test-host",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "unknown",
            "extra_field": "should_be_ignored"
        }

        with patch('app.core.state.MAPPING_RULES', mock_rules), \
                patch('app.core.state.DEFAULT_DESCRIPTION', mock_default_description):
            result = map_device_status(device_status)

            assert result["hostname"] == "test-host"
            assert result["timestamp"] == "2024-01-01T00:00:00Z"
            assert result["status"] == "unknown"
            assert "extra_field" not in result  # 额外字段应被过滤

    def test_matching_online_status(self, mock_rules, mock_default_description):
        """测试匹配在线状态"""
        device_status = {
            "hostname": "host1",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "online"
        }

        with patch('app.core.state.MAPPING_RULES', mock_rules), \
                patch('app.core.state.DEFAULT_DESCRIPTION', mock_default_description):
            result = map_device_status(device_status)
            assert result["description"] == "设备在线"

    def test_matching_offline_status(self, mock_rules, mock_default_description):
        """测试匹配离线状态"""
        device_status = {
            "hostname": "host2",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "offline"
        }

        with patch('app.core.state.MAPPING_RULES', mock_rules), \
                patch('app.core.state.DEFAULT_DESCRIPTION', mock_default_description):
            result = map_device_status(device_status)
            assert result["description"] == "设备离线"

    def test_matching_hostname_contains(self, mock_rules, mock_default_description):
        """测试主机名包含匹配"""
        device_status = {
            "hostname": "web-server-01",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "maintenance"
        }

        with patch('app.core.state.MAPPING_RULES', mock_rules), \
                patch('app.core.state.DEFAULT_DESCRIPTION', mock_default_description):
            result = map_device_status(device_status)
            assert result["description"] == "服务器设备"

    def test_no_match_uses_default_description(self, mock_rules, mock_default_description):
        """测试无匹配时使用默认描述"""
        device_status = {
            "hostname": "desktop-pc",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "unknown"
        }

        with patch('app.core.state.MAPPING_RULES', mock_rules), \
                patch('app.core.state.DEFAULT_DESCRIPTION', mock_default_description):
            result = map_device_status(device_status, default_description=mock_default_description)
            assert result["description"] == mock_default_description

    def test_missing_fields_handled_gracefully(self, mock_rules, mock_default_description):
        """测试缺失字段被优雅处理"""
        device_status = {
            "hostname": "partial-host"
            # 缺少 timestamp 和 status
        }

        with patch('app.core.state.MAPPING_RULES', mock_rules), \
                patch('app.core.state.DEFAULT_DESCRIPTION', mock_default_description):
            result = map_device_status(device_status, default_description=mock_default_description)

            assert result["hostname"] == "partial-host"
            assert result["timestamp"] is None
            assert result["status"] is None
            assert result["description"] == mock_default_description

    def test_first_match_wins(self, mock_rules, mock_default_description):
        """测试第一个匹配的规则生效"""
        # 添加一个会先匹配的通用规则
        extended_rules = [
            {
                "conditions": {"hostname": {"contains": ""}},  # 总是匹配
                "description": "通用描述"
            },
            *mock_rules
        ]

        device_status = {
            "hostname": "server-01",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "online"
        }

        with patch('app.core.state.MAPPING_RULES', extended_rules), \
                patch('app.core.state.DEFAULT_DESCRIPTION', mock_default_description):
            result = map_device_status(device_status)
            # 应该使用第一个匹配的规则
            assert result["description"] == "通用描述"

    def test_result_structure(self, mock_rules, mock_default_description):
        """测试结果字典结构正确"""
        device_status = {
            "hostname": "test",
            "timestamp": "2024-01-01",
            "status": "online"
        }

        with patch('app.core.state.MAPPING_RULES', mock_rules), \
                patch('app.core.state.DEFAULT_DESCRIPTION', mock_default_description):
            result = map_device_status(device_status)

            # 验证只包含指定的四个字段
            expected_keys = {"hostname", "timestamp", "status", "description"}
            assert set(result.keys()) == expected_keys
