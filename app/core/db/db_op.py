# app/core/db_op.py
"""
封装数据库操作
"""
import json
from app.core.db.db import get_site_conn, get_cache_conn
from app.core.crypto import sha256_digest


def get_account() -> dict:
    """
    读取 site_config 中的账号与密码摘要

    :return: 包含 user 和 pwd_hash 字段的字典
    :raises RuntimeError: 当 site_config 表未初始化时抛出异常
    """
    conn = get_site_conn()
    row = conn.execute("SELECT user, pwd_hash FROM users WHERE id = 1").fetchone()
    if row is None:
        raise RuntimeError("Site config not initialized!")
    return dict(row)


def modify_credential(
    new_username: str | None = None,
    new_pwd: str | None = None
) -> None:
    """
    修改管理员凭据，new_pwd 字段以 SHA256 摘要形式入库，自动刷新 updated_at

    :param new_username: 需要更新的用户名(可选)
    :param new_pwd: 需要更新的密码(可选)
    :raises ValueError: 当 new_username 字段为纯空格时抛出
    """
    if new_username is None and new_pwd is None:
        return

    update_parts = ["updated_at = CURRENT_TIMESTAMP"]
    params = []

    if new_username is not None:
        if not new_username.strip():
            raise ValueError("Username cannot be empty or whitespace")
        update_parts.append("user = ?")
        params.append(new_username)

    if new_pwd is not None:
        update_parts.append("pwd_hash = ?")
        params.append(sha256_digest(new_pwd))

    conn = get_site_conn()
    conn.execute(
        f"UPDATE users SET {','.join(update_parts)} WHERE id = 1",
        params
    )
    conn.commit()


def update_device_status(device_id: str, status: dict) -> None:
    """
    更新 device_status 表中的设备状态

    使用 INSERT OR REPLACE 实现 Upsert 操作，如果设备已存在则更新状态，否则插入新记录。

    :param device_id: 设备唯一标识符
    :param status: 设备状态对象字典（将被序列化为 JSON 字符串存储）
    :return: 无返回值
    """
    conn = get_cache_conn()

    # 将状态对象序列化为 JSON 字符串
    status_json = json.dumps(status)

    conn.execute("INSERT OR REPLACE INTO device_status (device_id, status) VALUES (?, ?)",
                 (device_id, status_json)
    )
    conn.commit()


def get_device_status() -> dict:
    """
    读取 device_status 中的设备状态字典

    :return: 包含 device_id 和 status 字段的字典
    :raises RuntimeError: 当 device_status 表未初始化时抛出异常
    """
    conn = get_cache_conn()
    row = conn.execute("SELECT device_id, status FROM device_status LIMIT 1").fetchone()
    if row is None:
        raise RuntimeError("Site config not initialized!")
    return {
        "device_id": row[0],
        "status": json.loads(row[1])
    }


def get_site_config() -> dict:
    """
    读取 site_config 表中的配置项

    :return: 包含所有 site_config 字段值的字典
    :raises RuntimeError: 当 site_config 表未初始化时抛出异常
    """
    conn = get_site_conn()
    row = conn.execute("SELECT * FROM site_config LIMIT 1").fetchone()
    if row is None:
        raise RuntimeError("Site config not initialized!")
    return dict(row)


def get_theme_by_id(tid: int) -> dict | list | None:
    """
    根据id查询themes主题，返回字典/列表/None

    :param tid: 需要查寻的主题 id
    :return: 当 tid 为 0 时返回包含所有主题的列表 否则返回查询的主题 当数据库无数据时返回 None
    """
    conn = get_site_conn()
    if tid == 0:
        rows = conn.execute("SELECT * FROM themes ORDER BY weight ASC").fetchall()
        if not rows:
            return None
        return [dict(row) for row in rows]
    else:
        row = conn.execute("""
                SELECT id,name,raw_css,weight FROM themes WHERE id = ?
            """, (tid,)).fetchone()
        if row is None:
            return None
        return dict(row)