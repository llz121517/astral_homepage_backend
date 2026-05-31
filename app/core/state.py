# app/core/state.py
import re
from typing import Any, Dict, Optional
from app.config import DEFAULT_DESCRIPTION

# 全局存储最近设备状态
latest_device_status = {}

# 映射规则列表
MAPPING_RULES = [
    {
        "conditions": {"description": "PyCharm Community Edition"},
        "description": "PyCharm Community"
    },
    {
        "conditions": {
            "windowClass": "WorkerW",
            "processRealName": "explorer"
        },
        "description": "桌面"
    },
    {
        "conditions": {
            "windowClass": "Shell_TrayWnd",
            "processRealName": "explorer"
        },
        "description": "任务栏"
    },
    {
        "conditions": {
            "windowClass": "Chrome_WidgetWin_1",
            "description": "Microsoft Edge"
        },
        "description": "Microsoft Edge"
    },
    # 可继续添加更多规则...
]
"""
| 写法 | 含义 |
|------|------|
| `"windowTitle": "任务管理器"` | 精确等于 |
| `"windowTitle": {"contains": "Edge"}` | 标题包含 "Edge" |
| `"windowTitle": {"regex": ".*PowerShell.*"}` | 正则匹配（注意：`re.fullmatch` 要求整串匹配，可用 `.*` 包裹） |
| `"processRealName": {"in": ["cmd.exe", "powershell.exe"]}` | 值在列表中 |
"""



def _matches_condition(value: Any, condition: Any) -> bool:
    """
    判断单个字段值是否满足条件。

    支持：
      - 精确匹配：condition = "abc"
      - 字典形式：
          {"contains": "sub"} → 子串包含
          {"regex": "^Admin"} → 正则匹配（全匹配）
          {"in": ["a", "b"]} → 值在列表中
    """
    # 字段不存在/值为 None，直接不匹配
    if value is None:
        return False

    if isinstance(condition, dict):
        if "contains" in condition:
            substr = condition["contains"]
            return isinstance(value, str) and substr in value
        elif "regex" in condition:
            pattern = condition["regex"]
            return isinstance(value, str) and re.fullmatch(pattern, value) is not None
        elif "in" in condition:
            allowed_values = condition["in"]
            return value in allowed_values
        else:
            raise ValueError(f"不支持的条件类型: {condition}")
    else:
        # 精确匹配
        return value == condition


async def map_device_status(
        latest_device_status: Dict[str, Any],
        default_description: str = DEFAULT_DESCRIPTION
) -> Optional[Dict[str, Any]]:
    """
    异步映射设备状态，支持灵活匹配规则。

    Args:
        latest_device_status: 原始设备状态字典
        default_description: 无匹配时的默认描述

    Returns:
        新字典（仅返回 hostname, timestamp, status, description），若输入为空则返回 None
    """
    if not latest_device_status:
        return None

    # 提取必要字段（即使缺失也保留 key，值为 None）
    base_fields = {
        "hostname": latest_device_status.get("hostname"),
        "timestamp": latest_device_status.get("timestamp"),
        "status": latest_device_status.get("status"),
    }

    # 匹配 description
    matched_desc = None
    for rule in MAPPING_RULES:
        conditions = rule["conditions"]
        if all(
            _matches_condition(latest_device_status.get(k), v)
            for k, v in conditions.items()
        ):
            matched_desc = rule["description"]
            break

    # 构建精简结果
    result = {
        **base_fields,
        "description": matched_desc or default_description
    }
    return result