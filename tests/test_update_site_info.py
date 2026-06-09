# tests/test_update_site_info.py
import pytest
from unittest.mock import patch
from app.api.v1.site.info import SiteConfigUpdate, update_site_info


class TestSiteConfigUpdateValidator:
    """SiteConfigUpdate 模型验证器测试"""

    # ---------- null_to_empty_string ----------

    def test_null_string_field_converted_to_empty(self):
        """字符串字段传 None 应被转为空字符串"""
        data = SiteConfigUpdate(site_title=None, header=None)
        assert data.site_title == ""
        assert data.header == ""

    def test_non_null_string_field_unchanged(self):
        """字符串字段传正常值应保持不变"""
        data = SiteConfigUpdate(site_title="标题", header="hello")
        assert data.site_title == "标题"
        assert data.header == "hello"

    @pytest.mark.parametrize("field", [
        "site_title", "keywords", "description", "header", "footer",
        "beian", "ico", "avatar_url", "avatar_kuang", "title1", "title2",
    ])
    def test_all_string_fields_null_to_empty(self, field):
        """所有受验证器保护的字符串字段传 None 都应转为空字符串"""
        data = SiteConfigUpdate(**{field: None})
        assert getattr(data, field) == ""

    # ---------- null_to_empty_list / null_to_empty_dict_list ----------

    def test_null_tags_converted_to_empty_list(self):
        """tags 传 None 应被转为空列表"""
        data = SiteConfigUpdate(tags=None)
        assert data.tags == []

    @pytest.mark.parametrize("field", ["timeline", "descriptions", "side_info"])
    def test_null_json_dict_list_converted_to_empty_list(self, field):
        """timeline / descriptions / side_info 传 None 应被转为空列表"""
        data = SiteConfigUpdate(**{field: None})
        assert getattr(data, field) == []

    def test_non_null_json_fields_unchanged(self):
        """JSON 字段传正常值应保持不变"""
        tags = ["a", "b"]
        timeline = [{"title": "t", "content": "c"}]
        data = SiteConfigUpdate(tags=tags, timeline=timeline)
        assert data.tags == tags
        assert data.timeline == timeline

    # ---------- 不受验证器影响的字段 ----------

    def test_int_fields_not_affected_by_validator(self):
        """整数字段不受验证器影响"""
        data = SiteConfigUpdate(maxwidth=None, switch_indexavatar=None)
        assert data.maxwidth is None
        assert data.switch_indexavatar is None


class TestUpdateSiteInfo:
    """update_site_info 数据清洗与返回值测试"""

    # ---------- 数据清洗：tags ----------

    @pytest.mark.asyncio
    async def test_tags_stripped(self):
        """tags 列表中的每个元素应去除首尾空格"""
        data = SiteConfigUpdate(tags=["  python  ", " fastapi ", "test"])

        with patch("app.api.v1.site.info.update_site_config", return_value=True) as mock_update:
            await update_site_info(data)

            result = mock_update.call_args[0][0]
            assert result["tags"] == ["python", "fastapi", "test"]

    # ---------- 数据清洗：timeline / descriptions / side_info ----------

    @pytest.mark.asyncio
    async def test_timeline_fields_stripped(self):
        """timeline 中每个 item 的 title 和 content 应去除首尾空格"""
        data = SiteConfigUpdate(timeline=[
            {"title": " 标题1 ", "content": " 内容1 "},
            {"title": "标题2", "content": "内容2  "},
        ])

        with patch("app.api.v1.site.info.update_site_config", return_value=True) as mock_update:
            await update_site_info(data)

            result = mock_update.call_args[0][0]
            assert result["timeline"] == [
                {"title": "标题1", "content": "内容1"},
                {"title": "标题2", "content": "内容2"},
            ]

    @pytest.mark.asyncio
    async def test_descriptions_fields_stripped(self):
        """descriptions 中每个 item 的 title 和 content 应去除首尾空格"""
        data = SiteConfigUpdate(descriptions=[
            {"title": " 关于我 ", "content": " 一段介绍 "},
        ])

        with patch("app.api.v1.site.info.update_site_config", return_value=True) as mock_update:
            await update_site_info(data)

            result = mock_update.call_args[0][0]
            assert result["descriptions"] == [
                {"title": "关于我", "content": "一段介绍"},
            ]

    @pytest.mark.asyncio
    async def test_side_info_fields_stripped(self):
        """side_info 中每个 item 的 title 和 content 应去除首尾空格"""
        data = SiteConfigUpdate(side_info=[
            {"title": " 侧边栏 ", "content": " 内容 "},
        ])

        with patch("app.api.v1.site.info.update_site_config", return_value=True) as mock_update:
            await update_site_info(data)

            result = mock_update.call_args[0][0]
            assert result["side_info"] == [
                {"title": "侧边栏", "content": "内容"},
            ]

    # ---------- 数据透传 ----------

    @pytest.mark.asyncio
    async def test_plain_text_fields_not_modified(self):
        """纯文本字段不做 strip 处理，原样传递"""
        data = SiteConfigUpdate(site_title=" 保留空格 ", header="hello")

        with patch("app.api.v1.site.info.update_site_config", return_value=True) as mock_update:
            await update_site_info(data)

            result = mock_update.call_args[0][0]
            assert result["site_title"] == " 保留空格 "
            assert result["header"] == "hello"

    @pytest.mark.asyncio
    async def test_exclude_unset_fields(self):
        """未设置的字段不应出现在传给 update_site_config 的字典中"""
        data = SiteConfigUpdate(site_title="新标题")

        with patch("app.api.v1.site.info.update_site_config", return_value=True) as mock_update:
            await update_site_info(data)

            result = mock_update.call_args[0][0]
            assert result == {"site_title": "新标题"}
            assert "tags" not in result
            assert "timeline" not in result

    @pytest.mark.asyncio
    async def test_empty_json_fields_skip_strip(self):
        """JSON 字段为空列表时不触发 strip 逻辑"""
        data = SiteConfigUpdate(site_title="标题")

        with patch("app.api.v1.site.info.update_site_config", return_value=True) as mock_update:
            await update_site_info(data)

            result = mock_update.call_args[0][0]
            # 空列表虽然经过验证器，但 if 判断为 False，不会进入 strip 分支
            # exclude_unset 确保未显式设置的 JSON 字段不出现在结果中
            assert "tags" not in result
            assert "timeline" not in result
            assert "descriptions" not in result
            assert "side_info" not in result

    @pytest.mark.asyncio
    async def test_all_json_fields_stripped_together(self):
        """多个 JSON 字段同时传入时应全部正确清洗"""
        data = SiteConfigUpdate(
            tags=[" a ", "b"],
            timeline=[{"title": " t1 ", "content": " c1 "}],
            descriptions=[{"title": " d1 ", "content": " dc1 "}],
            side_info=[{"title": " s1 ", "content": " sc1 "}],
        )

        with patch("app.api.v1.site.info.update_site_config", return_value=True) as mock_update:
            await update_site_info(data)

            result = mock_update.call_args[0][0]
            assert result["tags"] == ["a", "b"]
            assert result["timeline"][0]["title"] == "t1"
            assert result["descriptions"][0]["content"] == "dc1"
            assert result["side_info"][0]["title"] == "s1"

    # ---------- 返回值 ----------

    @pytest.mark.asyncio
    async def test_returns_success_when_updated(self):
        """update_site_config 返回 True 时应返回成功"""
        data = SiteConfigUpdate(site_title="新标题")

        with patch("app.api.v1.site.info.update_site_config", return_value=True):
            response = await update_site_info(data)

            assert response["code"] == 1
            assert response["msg"] == "success"

    @pytest.mark.asyncio
    async def test_returns_failure_when_not_updated(self):
        """update_site_config 返回 False 时应返回失败"""
        data = SiteConfigUpdate(site_title="新标题")

        with patch("app.api.v1.site.info.update_site_config", return_value=False):
            response = await update_site_info(data)

            assert response["code"] == 0

    @pytest.mark.asyncio
    async def test_update_site_config_always_called(self):
        """即使不传任何 JSON 字段，也应调用 update_site_config"""
        data = SiteConfigUpdate(footer="页脚内容")

        with patch("app.api.v1.site.info.update_site_config", return_value=True) as mock_update:
            await update_site_info(data)

            mock_update.assert_called_once()


import json
import pytest
from unittest.mock import patch
from app.api.v1.site.info import SiteConfigUpdate, update_site_info, get_site_info


class TestGetSiteInfo:
    """get_site_info 返回值与 JSON 反序列化测试"""

    @pytest.mark.asyncio
    async def test_return_structure(self):
        """返回值应包含正确的 code 和 msg"""
        with patch("app.api.v1.site.info.get_site_config", return_value={"site_title": "测试"}):
            response = await get_site_info()

            assert response["code"] == 1
            assert response["msg"] == "success"
            assert "data" in response

    @pytest.mark.asyncio
    async def test_json_string_fields_parsed(self):
        """JSON 字符串字段应被解析回 Python 对象"""
        mock_data = {
            "tags": '["python", "fastapi"]',
            "timeline": '[{"title": "t1", "content": "c1"}]',
            "descriptions": '[{"title": "d1", "content": "dc1"}]',
            "side_info": '[]',
        }

        with patch("app.api.v1.site.info.get_site_config", return_value=mock_data):
            response = await get_site_info()

            data = response["data"]
            assert data["tags"] == ["python", "fastapi"]
            assert data["timeline"] == [{"title": "t1", "content": "c1"}]
            assert data["descriptions"] == [{"title": "d1", "content": "dc1"}]
            assert data["side_info"] == []

    @pytest.mark.asyncio
    async def test_non_string_json_fields_not_parsed(self):
        """已经是列表/字典的 JSON 字段不应再被解析"""
        mock_data = {
            "tags": ["already", "a", "list"],
            "timeline": [{"title": "t", "content": "c"}],
        }

        with patch("app.api.v1.site.info.get_site_config", return_value=mock_data):
            response = await get_site_info()

            data = response["data"]
            assert data["tags"] == ["already", "a", "list"]
            assert data["timeline"] == [{"title": "t", "content": "c"}]

    @pytest.mark.asyncio
    async def test_missing_json_fields_no_error(self):
        """返回数据中缺少 JSON 字段时不应报错"""
        mock_data = {"site_title": "测试", "header": "hello"}

        with patch("app.api.v1.site.info.get_site_config", return_value=mock_data):
            response = await get_site_info()

            assert response["code"] == 1
            assert response["data"]["site_title"] == "测试"
            assert "tags" not in response["data"]

    @pytest.mark.asyncio
    async def test_plain_text_fields_unchanged(self):
        """纯文本字段应原样返回"""
        mock_data = {
            "site_title": "标题",
            "header": " 保留空格 ",
            "maxwidth": 1100,
        }

        with patch("app.api.v1.site.info.get_site_config", return_value=mock_data):
            response = await get_site_info()

            data = response["data"]
            assert data["site_title"] == "标题"
            assert data["header"] == " 保留空格 "
            assert data["maxwidth"] == 1100

    @pytest.mark.asyncio
    async def test_null_string_json_field_not_parsed(self):
        """JSON 字段值为 None 时不应被解析"""
        mock_data = {"tags": None, "site_title": "测试"}

        with patch("app.api.v1.site.info.get_site_config", return_value=mock_data):
            response = await get_site_info()

            assert response["data"]["tags"] is None

