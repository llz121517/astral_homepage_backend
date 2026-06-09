# app/api/v1/site/info.py
import json
from fastapi import APIRouter
from app.core.db.db_op import get_site_config
from app.core.db.db_op import update_site_config
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any

class SiteConfigUpdate(BaseModel):
    site_title: Optional[str] = None
    keywords: Optional[str] = None
    description: Optional[str] = None
    header: Optional[str] = None
    footer: Optional[str] = None
    beian: Optional[str] = None
    ico: Optional[str] = None
    avatar_url: Optional[str] = None
    avatar_kuang: Optional[str] = None
    maxwidth: Optional[int] = None
    title1: Optional[str] = None
    title2: Optional[str] = None
    tags: Optional[List[str]] = None                # 存为 JSON 字符串
    timeline: Optional[List[Dict[str, Any]]] = None # 存为 JSON 字符串
    descriptions: Optional[List[Dict[str, Any]]] = None  # 存为 JSON 字符串
    side_info: Optional[List[Dict[str, Any]]] = None     # 存为 JSON 字符串
    switch_indexavatar: Optional[int] = None
    switch_leftcard: Optional[int] = None
    switch_skill: Optional[int] = None
    switch_tcs: Optional[int] = None
    active_theme_id: Optional[int] = None

    @field_validator(
        'site_title', 'keywords', 'description', 'header', 'footer',
        'beian', 'ico', 'avatar_url', 'avatar_kuang', 'title1', 'title2',
        mode='before'
    )
    def null_to_empty_string(cls, v):
        return "" if v is None else v

    @field_validator('tags', mode='before')
    def null_to_empty_list(cls, v):
        return [] if v is None else v

    @field_validator('timeline', 'descriptions', 'side_info', mode='before')
    def null_to_empty_dict_list(cls, v):
        return [] if v is None else v

router = APIRouter(prefix="/api/v1/site", tags=["site", "api_v1"])


@router.get("/info")
async def get_site_info():
    """
    返回站点基础信息
    """
    data = get_site_config()
    # 将 JSON 字符串字段解析回 Python 对象
    json_fields = {'tags', 'timeline', 'descriptions', 'side_info'}
    for field in json_fields:
        if field in data and isinstance(data[field], str):
            data[field] = json.loads(data[field])
    return {"code": 1, "msg": "success", "data": data}


@router.put("/info")
async def update_site_info(update_data: SiteConfigUpdate):
    """
    更新站点基础信息
    """
    if update_data.tags:
        update_data.tags = [tag.strip() for tag in update_data.tags]
    if update_data.timeline:
        for item in update_data.timeline:
            item["title"] = item["title"].strip()
            item["content"] = item["content"].strip()
    if update_data.descriptions:
        for item in update_data.descriptions:
            item["title"] = item["title"].strip()
            item["content"] = item["content"].strip()
    if update_data.side_info:
        for item in update_data.side_info:
            item["title"] = item["title"].strip()
            item["content"] = item["content"].strip()

    updated = update_site_config(update_data.model_dump(exclude_unset=True))

    if not updated:
        return {"code": 0, "msg": "No changes or update failed"}
    return {"code": 1, "msg": "success"}
