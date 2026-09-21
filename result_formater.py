from typing import List


class ResultFormatter:
    """将数据库结果格式化为文本表格。"""

    def format(self, columns: List[str], results: List[tuple]) -> str:
        """按列宽格式化查询结果。"""
        if not results:
            return "查询结果为空"
        if not columns:
            return "查询结果无列信息"

        col_widths: list[int] = []
        for index, column in enumerate(columns):
            max_data_width = 0
            for row in results:
                if index < len(row):
                    max_data_width = max(
                        max_data_width,
                        len(str(row[index])),
                    )
            col_widths.append(max(len(str(column)), max_data_width) + 2)

        header = "|".join(
            str(column).ljust(col_widths[index])
            for index, column in enumerate(columns)
        )
        separator = "+".join("-" * width for width in col_widths)

        rows = []
        for row in results:
            cells = []
            for index in range(len(columns)):
                value = row[index] if index < len(row) else ""
                cells.append(str(value).ljust(col_widths[index]))
            rows.append("|".join(cells))

        return (
            f"{separator}\n{header}\n{separator}\n"
            + "\n".join(rows)
            + f"\n{separator}"
        )

    def format_error(self, error_msg: str) -> str:
        """格式化错误信息。"""
        return f"执行出错：{error_msg}"
