from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Iterable

class SecurityError(Exception):
    """权限校验或 SQL 安全检查失败。"""



@dataclass(slots=True)
class UserContext:
    """当前请求的最小权限上下文。"""

    user_id: str
    role: str = "admin"
    region: str | None = None
    allowed_regions: list[str] = field(default_factory=list)

    row_level_filters: list[tuple[str, str]] = field(default_factory=list)
    masked_columns: set[str] = field(default_factory=set)

    @classmethod
    def demo_admin(cls) -> "UserContext":
        return cls(user_id="demo_admin", role="admin")



_DANGEROUS_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|REPLACE)\b",
    flags=re.IGNORECASE,
)
_CLAUSE_BOUNDARY = re.compile(
    r"\b(GROUP\s+BY|ORDER\s+BY|LIMIT|HAVING)\b",
    flags=re.IGNORECASE,
)
class QuerySecurityManager:



    def secure_sql(self,sql: str , user_contest: UserContext) ->str :
        normalized_sql = self._normalize_sql(sql)
        self._ensure_select_only(normalized_sql)

        if user_contest.role == "sales":
            for table_name , field_name in user_contest.row_level_filters:
                if user_contest.region is None:
                    raise SecurityError("sales必须要有region字段")
                predicate=self._filter_field(sql , table_name, field_name , user_contest.region)
                if predicate:
                    normalized_sql = self._append_predicate(normalized_sql, predicate)

        return normalized_sql

    def mask_result(
        self,
        columns: list[str],
        rows: Iterable[tuple | list],
        user: UserContext | None = None,
    ) -> tuple[list[str], list[tuple]]:
        user_context = user or UserContext.demo_admin()
        if not user_context.masked_columns:
            return columns, [tuple(row) for row in rows]

        sensitive_indexes = {
            index
            for index, column in enumerate(columns)
            if column.lower() in user_context.masked_columns
        }
        if not sensitive_indexes:
            return columns, [tuple(row) for row in rows]

        masked_rows: list[tuple] = []
        for row in rows:
            values = list(row)
            for index in sensitive_indexes:
                values[index] = "***"
            masked_rows.append(tuple(values))

        return columns, masked_rows






    @staticmethod
    def _normalize_sql(sql: str) ->str:
        normalized = sql.strip()
        normalized = re.sub(r"^```sql\s*|```$", "", normalized, flags=re.IGNORECASE)
        normalized = normalized.strip()
        return normalized[:-1].strip() if normalized.endswith(";") else normalized

    @staticmethod
    def _ensure_select_only(sql: str):
        if not sql:
            raise SecurityError("SQL 不能为空。")
        if sql.count(";") > 0:
            raise SecurityError("检测到多语句执行风险。")
        if _DANGEROUS_KEYWORDS.search(sql):
            raise SecurityError("只允许执行查询语句。")
        if not re.match(r"^\s*(SELECT|WITH)\b", sql, flags=re.IGNORECASE):
            raise SecurityError("只允许执行查询语句。")

    def _filter_field(self,sql: str , table_name: str , field_name: str , region: str) ->str |None:

        if not self._contains_table(sql, table_name):
            return None

        qualifier = self._find_table_qualifier(sql, table_name)
        return f"{qualifier}.{field_name} = '{self._escape_sql_literal(region)}'"



    @staticmethod
    def _contains_table(sql: str, table_name: str) -> bool:
        return re.search(
            rf"\b(?:FROM|JOIN)\s+{re.escape(table_name)}\b",
            sql,
            flags=re.IGNORECASE,
        ) is not None

    @staticmethod
    def _find_table_qualifier(sql: str, table_name: str) -> str:
        pattern = re.compile(
            rf"\b(?:FROM|JOIN)\s+{re.escape(table_name)}(?:\s+(?:AS\s+)?([a-zA-Z_][\w]*))?",
            flags=re.IGNORECASE,
        )
        match = pattern.search(sql)
        alias = match.group(1) if match else None
        return alias or table_name

    def _append_predicate(self, sql: str, predicate: str) -> str:
        boundary = _CLAUSE_BOUNDARY.search(sql)
        insert_at = boundary.start() if boundary else len(sql)
        prefix = sql[:insert_at].rstrip()
        suffix = sql[insert_at:].lstrip()
        joiner = " AND " if re.search(r"\bWHERE\b", prefix, flags=re.IGNORECASE) else " WHERE "
        updated = f"{prefix}{joiner}{predicate}"
        if suffix:
            updated = f"{updated} {suffix}"
        return updated


    @staticmethod
    def _escape_sql_literal(value: str) -> str:
        return value.replace("'", "''")
