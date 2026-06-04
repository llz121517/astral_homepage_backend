# app/core/db_op.py
from .db import get_site_conn, get_session_conn
from .crypto import sha256_digest


def get_admin_account() -> dict:
    """读取 site_config 账号密码"""
    conn = get_site_conn()
    row = conn.execute("SELECT user, pwd FROM site_config WHERE id = 1").fetchone()
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
        update_parts.append("pwd = ?")
        params.append(sha256_digest(new_pwd))

    conn = get_site_conn()
    conn.execute(
        f"UPDATE site_config SET {','.join(update_parts)} WHERE id = 1",
        params
    )
    conn.commit()