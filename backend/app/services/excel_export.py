from pathlib import Path

import pandas as pd

from app.config import settings


def export_rows_to_excel(rows: list[dict], export_path: Path | None = None) -> Path:
    export_path = export_path or settings.export_path
    df = pd.DataFrame(rows)

    if df.empty:
        df = pd.DataFrame(
            columns=[
                "story_id",
                "story_title",
                "task_id",
                "task_title",
                "task_type",
                "priority",
                "status",
                "owner_hint",
                "dependencies",
                "gherkin",
                "acceptance_criteria",
                "business_value",
                "source_excerpt",
            ]
        )

    with pd.ExcelWriter(export_path, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Tasks", index=False)
        workbook = writer.book
        worksheet = writer.sheets["Tasks"]

        header_fmt = workbook.add_format(
            {
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "border": 1,
                "bg_color": "#D9EAF7",
            }
        )
        body_fmt = workbook.add_format(
            {"text_wrap": True, "valign": "top", "border": 1}
        )

        widths = {
            "A": 18, "B": 30, "C": 18, "D": 30, "E": 18, "F": 12,
            "G": 14, "H": 18, "I": 24, "J": 38, "K": 38, "L": 24, "M": 40,
        }
        for col, width in widths.items():
            worksheet.set_column(f"{col}:{col}", width, body_fmt)

        for idx, name in enumerate(df.columns):
            worksheet.write(0, idx, name, header_fmt)

        worksheet.freeze_panes(1, 0)
        worksheet.autofilter(0, 0, max(len(df), 1), len(df.columns) - 1)

        summary = pd.DataFrame(
            [
                {"metric": "task_count", "value": len(df)},
                {"metric": "story_count", "value": int(df["story_id"].nunique()) if not df.empty else 0},
                {"metric": "high_priority_tasks", "value": int((df["priority"] == "High").sum()) if not df.empty else 0},
            ]
        )
        summary.to_excel(writer, sheet_name="Summary", index=False)

        summary_ws = writer.sheets["Summary"]
        summary_ws.set_column("A:A", 28)
        summary_ws.set_column("B:B", 14)

    return export_path
