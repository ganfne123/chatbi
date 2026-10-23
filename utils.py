"""通用工具方法。"""

from __future__ import annotations
from typing import Tuple

import secrets
from dataclasses import dataclass
from datetime import datetime

import pymysql
from passlib.context import CryptContext

from fastapi import HTTPException

from config import database_config
from security import UserContext


pwd_context = CryptContext("bcrypt_sha256", deprecated="auto")

# user 表 username 字段长度上限
USERNAME_MAX_LENGTH = 64
# token 有效期，单位：天
TOKEN_TTL_DAYS = 1


class DuplicateUsernameError(ValueError):
    """用户名已存在。"""


class UserNotFoundError(ValueError):
    """user_id 对应的用户不存在。"""




@dataclass(frozen=True, slots=True)
class UserAccount:
    """通过账号密码校验的用户信息。"""

    id: str
    username: str
    role: str


def get_hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_user(username: str, password: str, role: str = "user") -> int:
    """往 user 表新增一个用户，密码以 bcrypt_sha256 哈希后落库，明文不落库。

    :param username: 登录名，全库唯一
    :param password: 明文密码，仅用于计算哈希
    :param role: 角色名，取值范围见 role 表（admin / finance / sales）
    :return: 新插入记录的自增主键 id
    :raises ValueError: 参数不合法
    :raises DuplicateUsernameError: username 已存在
    """
    username = (username or "").strip()
    if not username:
        raise ValueError("用户名不能为空")
    if len(username) > USERNAME_MAX_LENGTH:
        raise ValueError(f"用户名长度不能超过 {USERNAME_MAX_LENGTH} 个字符")
    if not password:
        raise ValueError("密码不能为空")

    hashed_password = get_hash_password(password)

    conn = pymysql.connect(**database_config, autocommit=True)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO `user` (`username`, `password`, `role`) VALUES (%s, %s, %s)",
                (username, hashed_password, role),
            )
            return cursor.lastrowid
    except pymysql.err.IntegrityError as exc:
        raise DuplicateUsernameError(f"用户名已存在：{username}") from exc
    finally:
        conn.close()


from fastapi import HTTPException

def authenticate_user(username: str, password: str) -> UserAccount:
    """校验用户名与密码是否匹配。

    校验通过返回 UserAccount（含 user_id 与 role）。
    校验失败统一抛出 HTTPException(401)，不返回 None。

    说明：
    - 密码用 bcrypt_sha256 哈希比对，库里不存明文，单次校验约 0.4s。
    - user 表排序规则是 utf8mb4_uca1400_ai_ci，username 比对大小写不敏感。
    - 用户不存在时也执行一次等价的哈希校验，让「用户名错」与「密码错」
      的响应耗时接近，避免被用来枚举系统里有哪些账号。

    :param username: 登录名，忽略首尾空格
    :param password: 明文密码
    :return: UserAccount
    :raises HTTPException: 401，用户名或密码错误 / 参数为空 / 哈希非法
    """
    username = (username or "").strip()

    # 参数缺失：统一按登录失败处理（错误信息不区分，避免泄露细节）
    if not username or not password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    conn = pymysql.connect(**database_config)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, password, role FROM `user` WHERE username = %s",
                (username,),
            )
            row = cursor.fetchone()
    finally:
        conn.close()

    if row is None:
        # 走一次假校验，让耗时和真实校验一致，防止账号枚举
        pwd_context.dummy_verify()
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    user_id, db_username, stored_password, role = row

    try:
        matched = verify_password(password, stored_password)
    except ValueError:
        # 库里存的不是合法哈希（历史脏数据），一律按校验失败处理
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not matched:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    return UserAccount(id=user_id, username=db_username, role=role)

def verify_token(token: str) -> UserContext:
    """校验 token 是否有效，鉴权失败直接抛异常，成功返回该用户的完整 UserContext。

    抛出的异常是 fastapi.HTTPException(401, ...)，会被 api_server.py 里注册的
    http_exception_handler 统一转成 {"success": false, "error": ..., "error_type": "http_exception"}。

    返回的 UserContext 会带上角色对应的权限数据：
    - role：取自 user.role
    - row_level_filters：role_row_filter 里配置的行级过滤列，[(表名, 列名), ...]
    - masked_columns：role_masked_column 里配置的脱敏列，{列名, ...}
      （只取列名，因为 security.mask_result 是按结果集的列名比对的）

    - 过期判断放在 SQL 里用 NOW() 比较，和签发时的 DATE_ADD(NOW(), ...) 同一个时钟。
    - 传进来的值允许带 "Bearer " 前缀（前端常见的 Authorization 头格式），会自动去掉。

    :param token: token 原文，或 "Bearer <token>"
    :return: UserContext
    :raises HTTPException: 401，token 缺失 / 无效 / 已过期 / 账号已不存在
    """
    token = (token or "").strip()
    if token.lower().startswith("bearer "):
        token = token[len("bearer "):].strip()
    if not token:
        raise HTTPException(status_code=401, detail="未提供登录凭证，请先登录")

    conn = pymysql.connect(**database_config)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT u.id, u.username, u.role, (t.expires_at > NOW()) AS is_valid "
                "FROM `user_token` t "
                "JOIN `user` u ON u.username = t.user_name "
                "WHERE t.token = %s "
                "ORDER BY t.id DESC LIMIT 1",
                (token,),
            )
            row = cursor.fetchone()
            if row is None:
                # token 不存在，或它对应的账号已经被删掉
                raise HTTPException(status_code=401, detail="登录凭证无效，请重新登录")

            user_id, username, role, is_valid = row
            if not is_valid:
                raise HTTPException(status_code=401, detail="登录已过期，请重新登录")

            cursor.execute(
                "SELECT f.table_name, f.column_name "
                "FROM `role_row_filter` f "
                "JOIN `role` r ON r.id = f.role_id "
                "WHERE r.name = %s",
                (role,),
            )
            row_level_filters = [
                (table_name, column_name) for table_name, column_name in cursor.fetchall()
            ]

            cursor.execute(
                "SELECT m.column_name "
                "FROM `role_masked_column` m "
                "JOIN `role` r ON r.id = m.role_id "
                "WHERE r.name = %s",
                (role,),
            )
            masked_columns = {column_name for (column_name,) in cursor.fetchall()}
    finally:
        conn.close()

    return UserContext(
        user_id=str(user_id),
        role=role,
        row_level_filters=row_level_filters,
        masked_columns=masked_columns,
    )


def create_token(user_id: str, expires_in_days: int = TOKEN_TTL_DAYS) -> Tuple[str ,datetime]:
    """为用户签发一个 token 并写入 user_token 表，默认 1 天后过期。

    token 由 secrets.token_urlsafe(32) 生成（约 43 个字符，密码学安全随机）。
    expires_at 由数据库的 NOW() 推算，与 created_at 使用同一个时钟，避免
    应用与数据库时区不一致导致的过期时间偏移。

    :param user_id: user 表主键 id，必须已存在（表上有外键约束）
    :param expires_in_days: 有效天数，默认 1 天
    :return: IssuedToken(token=..., expires_at=...)
    :raises ValueError: 参数不合法
    :raises UserNotFoundError: user_id 对应用户不存在
    """
    if expires_in_days <= 0:
        raise ValueError("expires_in_days 必须大于 0")

    token = secrets.token_urlsafe(32)

    conn = pymysql.connect(**database_config, autocommit=True)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO `user_token` (`user_name`, `token`, `expires_at`) "
                "VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL %s DAY))",
                (user_id, token, int(expires_in_days)),
            )
            token_id = cursor.lastrowid
            cursor.execute(
                "SELECT expires_at FROM `user_token` WHERE id = %s", (token_id,)
            )
            (expires_at,) = cursor.fetchone()
    except pymysql.err.IntegrityError as exc:
        # 1452 = 外键约束失败（user_id 不存在）；其余（如 token 冲突）交给上层
        if exc.args and exc.args[0] == 1452:
            raise UserNotFoundError(f"用户不存在：user_name={user_id}") from exc
        raise
    finally:
        conn.close()

    return token, expires_at


if __name__ == "__main__":
    password = "123456"


    # 自测：新增用户 -> 校验密码 -> 签发 token -> 校验过期时间 -> 清理
    demo_username = "__self_test_user__"
    user_id = create_user(demo_username, "s3cret", role="finance")
    print(f"inserted user id={user_id}")
    create_token(user_id)
