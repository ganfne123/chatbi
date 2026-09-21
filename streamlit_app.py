"""ChatBI Streamlit 对话式前端。"""

from __future__ import annotations

import json
import os
import time
import uuid
from collections.abc import Iterable, Iterator
from datetime import datetime
from typing import Any

import requests
import streamlit as st


DEFAULT_API_BASE_URL = os.getenv("CHATBI_API_URL", "http://127.0.0.1:8000")
CHAT_HISTORY_KEY = "chatbi_chat_history"

SQL_COPY_HTML = """
<div class="sql-copy-wrap">
  <button id="copy-sql-button" type="button">复制 SQL</button>
</div>
"""

SQL_COPY_CSS = """
.sql-copy-wrap {
  display: flex;
  justify-content: flex-end;
  padding-top: 0.25rem;
}

button {
  border: 1px solid var(--st-border-color, #d6d6d6);
  border-radius: 0.5rem;
  background: var(--st-secondary-background-color, #f5f5f5);
  color: var(--st-text-color, #262730);
  cursor: pointer;
  font: inherit;
  padding: 0.35rem 0.8rem;
}

button:hover {
  border-color: var(--st-primary-color, #ff4b4b);
  color: var(--st-primary-color, #ff4b4b);
}
"""

SQL_COPY_JS = """
export default function (component) {
  const { data, parentElement } = component;
  const button = parentElement.querySelector("#copy-sql-button");
  if (!button) return;

  const sql = (data && data.sql) || "";

  function fallbackCopy() {
    const textarea = document.createElement("textarea");
    textarea.value = sql;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    parentElement.appendChild(textarea);
    textarea.focus();
    textarea.select();
    const copied = document.execCommand("copy");
    textarea.remove();
    return copied;
  }

  button.onclick = async () => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(sql);
      } else {
        fallbackCopy();
      }
      button.textContent = "已复制";
      setTimeout(() => {
        button.textContent = "复制 SQL";
      }, 1500);
    } catch (error) {
      button.textContent = "复制失败";
      setTimeout(() => {
        button.textContent = "复制 SQL";
      }, 1500);
    }
  };

  return () => {
    button.onclick = null;
  };
}
"""

sql_copy_component = st.components.v2.component(
    "chatbi_sql_copy_button",
    html=SQL_COPY_HTML,
    css=SQL_COPY_CSS,
    js=SQL_COPY_JS,
)


def parse_sse_lines(lines: Iterable[str | bytes]) -> Iterator[tuple[str, Any]]:
    """解析 SSE 文本行，依次产出事件类型和数据。"""
    event_type = "message"
    data_lines: list[str] = []

    for raw_line in lines:
        line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
        line = line.rstrip("\r")

        if not line:
            if data_lines:
                raw_data = "\n".join(data_lines)
                try:
                    data = json.loads(raw_data)
                except json.JSONDecodeError:
                    data = {"raw": raw_data}
                yield event_type, data
            event_type = "message"
            data_lines = []
            continue

        if line.startswith("event:"):
            event_type = line.removeprefix("event:").strip()
        elif line.startswith("data:"):
            data_lines.append(line.removeprefix("data:").lstrip())


def iter_stream_events(
    api_base_url: str,
    query: str,
) -> Iterator[tuple[str, Any]]:
    """调用流式接口并解析 SSE 事件。"""
    with requests.post(
        f"{api_base_url.rstrip('/')}/api/v1/query/stream",
        json={"query": query},
        headers={"Accept": "text/event-stream"},
        stream=True,
        timeout=(5, 300),
    ) as response:
        response.raise_for_status()
        yield from parse_sse_lines(response.iter_lines())


def format_duration(duration_ms: float | None) -> str:
    """格式化毫秒耗时。"""
    if duration_ms is None:
        return "未统计"
    return f"{duration_ms / 1000:.2f} s"


def has_stream_content(content: Any) -> bool:
    """过滤流式响应中的空 delta。"""
    return isinstance(content, str) and len(content) > 0


def is_empty_result(rows_text: Any, row_count: Any) -> bool:
    """判断查询是否成功但没有返回数据行。"""
    if row_count == 0:
        return True
    if not isinstance(rows_text, str):
        return False
    normalized = rows_text.strip()
    return not normalized or normalized == "查询结果为空"


def render_copy_sql_button(sql: str, card_id: str) -> None:
    """渲染复制 SQL 按钮。"""
    sql_copy_component(
        key=f"copy_sql_{card_id}",
        data={"sql": sql},
        height=42,
    )


def create_card(question: str, mode: str) -> dict[str, Any]:
    """创建一张新的查询卡片。"""
    return {
        "id": uuid.uuid4().hex,
        "question": question,
        "mode": mode,
        "created_at": datetime.now().strftime("%H:%M:%S"),
        "sql": "",
        "sql_preview": "",
        "rows_text": "",
        "row_count": None,
        "sql_generation_ms": None,
        "total_ms": None,
        "error": None,
        "error_type": None,
        "status": "running",
    }


def render_card_header(card: dict[str, Any]) -> None:
    """渲染查询卡片标题。"""
    st.caption(
        f"{card['created_at']} · "
        f"{'流式查询' if card['mode'] == 'stream' else '同步查询'}"
    )
    st.markdown(f"**{card['question']}**")


def render_sql_toolbar(card: dict[str, Any]) -> None:
    """渲染 SQL 标题和双耗时。"""
    title_col, generate_col, total_col = st.columns([3, 1.3, 1.3])
    title_col.markdown("**SQL**")

    if card.get("sql_generation_ms") is not None:
        generate_text = format_duration(card["sql_generation_ms"])
    elif card.get("status") == "running":
        generate_text = "生成中..."
    elif card.get("status") == "error":
        generate_text = "失败"
    else:
        generate_text = "未统计"

    if card.get("total_ms") is not None:
        total_text = format_duration(card["total_ms"])
    elif card.get("status") == "running":
        total_text = "计算中..."
    else:
        total_text = "未统计"

    generate_col.caption(f"SQL 生成：{generate_text}")
    total_col.caption(f"查询总耗时：{total_text}")


def render_sql_block(card: dict[str, Any]) -> None:
    """渲染完整 SQL、耗时工具栏和复制按钮。"""
    render_sql_toolbar(card)
    st.code(card.get("sql", ""), language="sql")
    render_copy_sql_button(card.get("sql", ""), card["id"])


def render_result(card: dict[str, Any], placeholder: Any | None = None) -> None:
    """渲染查询结果或友好的空结果提示。"""
    target = placeholder if placeholder is not None else st
    if is_empty_result(card.get("rows_text"), card.get("row_count")):
        target.info("没有查询到符合条件的数据，请尝试调整时间范围或筛选条件。")
        return

    target.text(str(card.get("rows_text", "")))


def render_history_card(card: dict[str, Any]) -> None:
    """渲染一张已经完成的对话卡片。"""
    with st.container(border=True):
        render_card_header(card)

        if card.get("sql"):
            render_sql_block(card)

        if card.get("status") == "error":
            st.error(
                f"{card.get('error_type', 'error')}: "
                f"{card.get('error', '未知错误')}"
            )
            return

        if card.get("status") == "success":
            render_result(card)


def render_live_stream_card(api_base_url: str, card: dict[str, Any]) -> None:
    """执行并渲染一张实时流式查询卡片。"""
    with st.container(border=True):
        render_card_header(card)
        status_placeholder = st.empty()
        toolbar_placeholder = st.empty()
        sql_placeholder = st.empty()
        copy_placeholder = st.empty()
        result_placeholder = st.empty()
        sql_parts: list[str] = []
        started_at = time.perf_counter()

        try:
            status_placeholder.info("正在生成 SQL...")
            for event_type, data in iter_stream_events(api_base_url, card["question"]):
                if event_type == "chunk":
                    content = data.get("content")
                    if not has_stream_content(content):
                        continue
                    sql_parts.append(content)
                    card["sql_preview"] = "".join(sql_parts)
                    with toolbar_placeholder.container():
                        render_sql_toolbar(card)
                    sql_placeholder.code(card["sql_preview"], language="sql")
                elif event_type == "complete_sql":
                    card["sql"] = data.get("sql", "")
                    card["sql_generation_ms"] = (
                        time.perf_counter() - started_at
                    ) * 1000
                    status_placeholder.success("SQL 生成完成，正在查询数据库...")
                    with toolbar_placeholder.container():
                        render_sql_toolbar(card)
                    sql_placeholder.code(card["sql"], language="sql")
                    with copy_placeholder.container():
                        render_copy_sql_button(card["sql"], card["id"])
                elif event_type == "result":
                    card["total_ms"] = (time.perf_counter() - started_at) * 1000
                    card["rows_text"] = data.get("rows", "")
                    card["row_count"] = data.get("row_count")
                    card["status"] = "success"
                    status_placeholder.success("查询完成")
                    with toolbar_placeholder.container():
                        render_sql_toolbar(card)
                    render_result(card, result_placeholder)
                elif event_type == "error":
                    card["total_ms"] = (time.perf_counter() - started_at) * 1000
                    card["status"] = "error"
                    card["error"] = data.get("error", "未知错误")
                    card["error_type"] = data.get("error_type", "error")
                    status_placeholder.error(
                        f"{card['error_type']}: {card['error']}"
                    )
                    return
        except requests.RequestException as exc:
            card["total_ms"] = (time.perf_counter() - started_at) * 1000
            card["status"] = "error"
            card["error"] = str(exc)
            card["error_type"] = "request_error"
            status_placeholder.error(f"请求失败：{exc}")


def render_live_sync_card(api_base_url: str, card: dict[str, Any]) -> None:
    """执行并渲染一张实时同步查询卡片。"""
    with st.container(border=True):
        render_card_header(card)
        status_placeholder = st.empty()
        started_at = time.perf_counter()
        status_placeholder.info("正在生成 SQL 并查询数据库...")

        try:
            response = requests.post(
                f"{api_base_url.rstrip('/')}/api/v1/query",
                json={"query": card["question"]},
                timeout=300,
            )
            card["total_ms"] = (time.perf_counter() - started_at) * 1000

            if not response.ok:
                card["status"] = "error"
                card["error_type"] = f"http_{response.status_code}"
                try:
                    card["error"] = response.json().get("error", response.text)
                except ValueError:
                    card["error"] = response.text
                status_placeholder.error(card["error"])
                return

            result = response.json()
            metadata = result.get("metadata", {})
            card["sql"] = result.get("sql", "")
            card["rows_text"] = result.get("formatted", "")
            card["row_count"] = 0 if card["rows_text"] == "查询结果为空" else None
            card["sql_generation_ms"] = metadata.get("sql_generation_ms")
            card["total_ms"] = metadata.get("total_ms", card["total_ms"])
            card["status"] = "success"
            status_placeholder.success("查询完成")
            render_sql_block(card)
            render_result(card)
        except requests.RequestException as exc:
            card["total_ms"] = (time.perf_counter() - started_at) * 1000
            card["status"] = "error"
            card["error"] = str(exc)
            card["error_type"] = "request_error"
            status_placeholder.error(f"请求失败：{exc}")


def render_health_check(api_base_url: str) -> None:
    """在侧边栏渲染健康检查。"""
    st.sidebar.subheader("服务健康")
    if st.sidebar.button("检查服务状态", key="health_button"):
        try:
            response = requests.get(
                f"{api_base_url.rstrip('/')}/health",
                timeout=10,
            )
            if response.ok:
                st.sidebar.success("服务响应正常")
                st.sidebar.json(response.json())
            else:
                st.sidebar.error(f"HTTP {response.status_code}")
                st.sidebar.json(response.json())
        except requests.RequestException as exc:
            st.sidebar.error(f"请求失败：{exc}")


def render_app() -> None:
    """渲染 ChatBI 单页应用。"""
    st.set_page_config(page_title="ChatBI 数据查询", page_icon="📊", layout="wide")
    st.title("ChatBI 数据查询")
    st.caption("每次查询生成一张卡片，最新结果始终显示在最上方。")

    if CHAT_HISTORY_KEY not in st.session_state:
        st.session_state[CHAT_HISTORY_KEY] = []

    api_base_url = st.sidebar.text_input(
        "API 地址",
        value=DEFAULT_API_BASE_URL,
        help="FastAPI 服务地址，例如 http://127.0.0.1:8000",
    )
    use_stream = st.sidebar.toggle("使用流式查询", value=True)
    render_health_check(api_base_url)

    if st.sidebar.button("清空对话历史", key="clear_history_button"):
        st.session_state[CHAT_HISTORY_KEY] = []
        st.rerun()

    question = st.chat_input("输入你的数据问题...")
    history: list[dict[str, Any]] = st.session_state[CHAT_HISTORY_KEY]

    if question and question.strip():
        card = create_card(question.strip(), "stream" if use_stream else "sync")
        history.insert(0, card)

        if use_stream:
            render_live_stream_card(api_base_url, card)
        else:
            render_live_sync_card(api_base_url, card)

        history = history[1:]

    if history:
        st.subheader(f"对话历史 · {len(history)}")
        for item in history:
            render_history_card(item)
    else:
        st.info("还没有查询记录，输入一个数据问题开始对话。")


def main() -> None:
    """Streamlit 入口。"""
    render_app()


if __name__ == "__main__":
    main()
