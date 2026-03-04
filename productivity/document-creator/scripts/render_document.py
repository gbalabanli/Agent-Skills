#!/usr/bin/env python3
"""Render structured document JSON into a template-driven PDF output.

Current supported canonical template:
- official-paper
"""

from __future__ import annotations

import argparse
import html
import io
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
TEMPLATE_ROOT = SKILL_ROOT / "templates"


@dataclass
class SectionDef:
    section_id: str
    title: str


WORD_PATTERN = re.compile(r"[A-Za-z0-9']+")


def normalize_text(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
    return re.sub(r"\s+", " ", normalized)


def resolve_template(raw_name: str) -> str:
    norm = normalize_text(raw_name)
    if not norm:
        raise ValueError("Template value is empty.")

    direct = {
        "official paper": "official-paper",
        "official": "official-paper",
        "paper format": "official-paper",
        "academic paper": "official-paper",
        "official paper format": "official-paper",
        "wikipedia official paper style": "official-paper",
    }
    if norm in direct:
        return direct[norm]

    if "official" in norm and "paper" in norm:
        return "official-paper"
    if "academic" in norm and "paper" in norm:
        return "official-paper"

    raise ValueError(
        "Unsupported template name. Available templates: official paper"
    )


def load_json_file(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise ValueError(f"Input JSON not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON input: {exc}") from exc


def load_template_spec(template_id: str) -> dict[str, Any]:
    spec_path = TEMPLATE_ROOT / template_id / "spec.json"
    try:
        return json.loads(spec_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Template spec not found: {spec_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid template spec JSON: {exc}") from exc


def normalize_references(raw: Any) -> list[dict[str, str]]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValueError("Field 'references' must be a list.")

    result = []
    for idx, item in enumerate(raw, start=1):
        if isinstance(item, str):
            text = item.strip()
            if text:
                result.append({"title": text, "url": "", "note": ""})
            continue
        if not isinstance(item, dict):
            raise ValueError(f"Reference #{idx} must be an object or string.")
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        note = str(item.get("note", "")).strip()
        if not title and not url:
            continue
        result.append({"title": title or "Untitled source", "url": url, "note": note})
    return result


def normalize_block(block: Any) -> dict[str, Any]:
    if isinstance(block, str):
        return {"type": "paragraph", "text": block}
    if not isinstance(block, dict):
        return {
            "type": "math",
            "caption": "Unstructured block",
            "schema": {"value": block},
        }

    block_type = str(block.get("type", "paragraph")).strip().lower()
    if block_type == "paragraph":
        text = str(block.get("text", "")).strip()
        return {"type": "paragraph", "text": text}
    if block_type == "table":
        columns = block.get("columns", [])
        rows = block.get("rows", [])
        if not isinstance(columns, list):
            columns = []
        if not isinstance(rows, list):
            rows = []
        normalized_rows = []
        for row in rows:
            if isinstance(row, list):
                normalized_rows.append([str(cell) for cell in row])
            else:
                normalized_rows.append([str(row)])
        return {
            "type": "table",
            "caption": str(block.get("caption", "Untitled table")).strip(),
            "columns": [str(cell) for cell in columns],
            "rows": normalized_rows,
        }
    if block_type == "math":
        schema = block.get("schema", {})
        return {
            "type": "math",
            "caption": str(block.get("caption", "Mathematical schema")).strip(),
            "schema": schema,
        }
    if block_type == "code":
        schema = block.get("schema", {})
        if not isinstance(schema, dict):
            schema = {}
        language = str(block.get("language", schema.get("language", ""))).strip()
        code_text = str(block.get("code", schema.get("code", schema.get("snippet", "")))).strip()
        if language:
            schema["language"] = language
        if code_text:
            schema["code"] = code_text
        return {
            "type": "code",
            "caption": str(block.get("caption", "Code schema")).strip(),
            "schema": schema,
        }

    return {
        "type": "math",
        "caption": f"Unknown block type: {block_type}",
        "schema": block,
    }


def normalize_sections(raw: Any, section_defs: list[SectionDef]) -> dict[str, list[dict[str, Any]]]:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("Field 'sections' must be an object.")

    normalized: dict[str, list[dict[str, Any]]] = {}
    for definition in section_defs:
        section_blocks = raw.get(definition.section_id, [])
        if isinstance(section_blocks, str):
            section_blocks = [section_blocks]
        if not isinstance(section_blocks, list):
            section_blocks = [section_blocks]

        blocks = [normalize_block(item) for item in section_blocks]
        if not blocks:
            blocks = [
                {
                    "type": "paragraph",
                    "text": "Content not provided. Add section content in source JSON.",
                }
            ]
        normalized[definition.section_id] = blocks
    return normalized


def normalize_index_descriptions(
    raw: Any,
    section_defs: list[SectionDef],
    defaults: dict[str, str],
) -> dict[str, str]:
    raw_map = raw if isinstance(raw, dict) else {}
    result: dict[str, str] = {}
    for definition in section_defs:
        value = str(raw_map.get(definition.section_id, "")).strip()
        if not value:
            value = str(defaults.get(definition.section_id, "")).strip()
        if not value:
            value = f"Overview of {definition.title.lower()}."
        result[definition.section_id] = value
    return result


def estimate_body_word_count(sections: dict[str, list[dict[str, Any]]]) -> int:
    total = 0
    for blocks in sections.values():
        for block in blocks:
            if block.get("type") == "paragraph":
                text = str(block.get("text", ""))
                total += len(WORD_PATTERN.findall(text))
    return total


def load_reportlab():
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            BaseDocTemplate,
            Frame,
            PageBreak,
            PageTemplate,
            Paragraph,
            Preformatted,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'reportlab'. Install with: pip install reportlab"
        ) from exc

    return {
        "colors": colors,
        "A4": A4,
        "ParagraphStyle": ParagraphStyle,
        "getSampleStyleSheet": getSampleStyleSheet,
        "mm": mm,
        "BaseDocTemplate": BaseDocTemplate,
        "Frame": Frame,
        "PageBreak": PageBreak,
        "PageTemplate": PageTemplate,
        "Paragraph": Paragraph,
        "Preformatted": Preformatted,
        "Spacer": Spacer,
        "Table": Table,
        "TableStyle": TableStyle,
    }


def build_styles(rl: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    stylesheet = rl["getSampleStyleSheet"]()
    paragraph_style = stylesheet["BodyText"]
    typography = spec["typography"]

    line_height = typography["body_size_pt"] * typography.get("line_spacing", 1.35)
    paragraph_style.fontName = typography["font_family"]
    paragraph_style.fontSize = typography["body_size_pt"]
    paragraph_style.leading = line_height
    paragraph_style.spaceAfter = 8

    title_style = rl["ParagraphStyle"](
        "TitlePage",
        parent=paragraph_style,
        fontName=typography["title_font"],
        fontSize=typography["title_size_pt"],
        leading=typography["title_size_pt"] * 1.2,
        alignment=1,
        spaceAfter=16,
    )
    subtitle_style = rl["ParagraphStyle"](
        "Subtitle",
        parent=paragraph_style,
        fontName=typography["font_family"],
        fontSize=typography["subtitle_size_pt"],
        leading=typography["subtitle_size_pt"] * 1.3,
        alignment=1,
        spaceAfter=12,
    )
    heading_style = rl["ParagraphStyle"](
        "SectionHeading",
        parent=paragraph_style,
        fontName=typography["heading_font"],
        fontSize=typography["heading_size_pt"],
        leading=typography["heading_size_pt"] * 1.3,
        spaceBefore=8,
        spaceAfter=10,
    )
    caption_style = rl["ParagraphStyle"](
        "Caption",
        parent=paragraph_style,
        fontName=typography["font_family"],
        fontSize=typography["caption_size_pt"],
        leading=typography["caption_size_pt"] * 1.35,
        spaceAfter=6,
        italic=True,
    )
    reference_style = rl["ParagraphStyle"](
        "ReferenceEntry",
        parent=paragraph_style,
        spaceAfter=6,
    )
    reference_note_style = rl["ParagraphStyle"](
        "ReferenceNote",
        parent=paragraph_style,
        fontSize=10,
        leading=13,
        leftIndent=16,
        italic=True,
        textColor=rl["colors"].Color(0.25, 0.25, 0.25),
        spaceAfter=8,
    )
    mono_style = rl["ParagraphStyle"](
        "Monospace",
        parent=paragraph_style,
        fontName=typography["monospace_font"],
        fontSize=10,
        leading=13,
    )

    return {
        "body": paragraph_style,
        "title": title_style,
        "subtitle": subtitle_style,
        "heading": heading_style,
        "caption": caption_style,
        "reference": reference_style,
        "reference_note": reference_note_style,
        "mono": mono_style,
    }


def make_doc_class(rl: dict[str, Any]):
    class OfficialPaperDoc(rl["BaseDocTemplate"]):
        def __init__(self, filename: Any, page_spec: dict[str, Any], **kwargs: Any):
            margins = page_spec["margin_mm"]
            mm = rl["mm"]
            super().__init__(
                filename,
                pagesize=rl["A4"],
                topMargin=margins["top"] * mm,
                rightMargin=margins["right"] * mm,
                bottomMargin=margins["bottom"] * mm,
                leftMargin=margins["left"] * mm,
                **kwargs,
            )
            frame = rl["Frame"](
                self.leftMargin,
                self.bottomMargin,
                self.width,
                self.height,
                id="normal",
            )
            self._section_pages: dict[str, int] = {}
            self.addPageTemplates(
                [
                    rl["PageTemplate"](
                        id="default",
                        frames=[frame],
                        onPage=self._draw_footer,
                    )
                ]
            )

        def _draw_footer(self, canvas: Any, doc: Any) -> None:
            canvas.saveState()
            canvas.setFont("Times-Roman", 9)
            canvas.drawCentredString(rl["A4"][0] / 2, 11 * rl["mm"], str(canvas.getPageNumber()))
            canvas.restoreState()

        def afterFlowable(self, flowable: Any) -> None:
            section_id = getattr(flowable, "_section_id", None)
            if section_id and section_id not in self._section_pages:
                self._section_pages[section_id] = self.page

        @property
        def section_pages(self) -> dict[str, int]:
            return dict(self._section_pages)

    return OfficialPaperDoc


def build_story(
    rl: dict[str, Any],
    styles: dict[str, Any],
    spec: dict[str, Any],
    payload: dict[str, Any],
    section_defs: list[SectionDef],
    sections: dict[str, list[dict[str, Any]]],
    references: list[dict[str, str]],
    index_descriptions: dict[str, str],
    section_pages: dict[str, int] | None,
) -> list[Any]:
    story: list[Any] = []
    Paragraph = rl["Paragraph"]
    Spacer = rl["Spacer"]
    PageBreak = rl["PageBreak"]
    Table = rl["Table"]
    TableStyle = rl["TableStyle"]
    Preformatted = rl["Preformatted"]
    colors = rl["colors"]
    table_header_rgb = spec["tables"]["header_background_rgb"]
    table_grid_rgb = spec["tables"]["grid_line_rgb"]
    table_header_color = colors.Color(
        table_header_rgb[0] / 255.0,
        table_header_rgb[1] / 255.0,
        table_header_rgb[2] / 255.0,
    )
    table_grid_color = colors.Color(
        table_grid_rgb[0] / 255.0,
        table_grid_rgb[1] / 255.0,
        table_grid_rgb[2] / 255.0,
    )

    # Title page (page 1)
    story.append(Spacer(1, 130))
    story.append(Paragraph(html.escape(payload["title"]), styles["title"]))
    subtitle = str(payload.get("subtitle", "")).strip()
    if subtitle:
        story.append(Paragraph(html.escape(subtitle), styles["subtitle"]))
    authors = payload.get("authors", [])
    if authors:
        story.append(Paragraph(html.escape(", ".join(authors)), styles["subtitle"]))
    if payload.get("date"):
        story.append(Paragraph(html.escape(payload["date"]), styles["subtitle"]))
    story.append(PageBreak())

    # Index page (page 2)
    story.append(Paragraph("Index", styles["heading"]))
    story.append(
        Paragraph(
            "Main sections listed with purpose and starting page.",
            styles["body"],
        )
    )
    toc_rows: list[list[Any]] = [["Section", "Page", "What This Section Covers"]]
    for section in section_defs:
        page_value = "?"
        if section_pages:
            page_value = str(section_pages.get(section.section_id, "?"))
        summary = index_descriptions.get(section.section_id, "")
        toc_rows.append(
            [
                section.title,
                page_value,
                Paragraph(html.escape(summary), styles["body"]),
            ]
        )
    toc_table = Table(toc_rows, colWidths=[130, 50, 250])
    toc_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BACKGROUND", (0, 0), (-1, 0), table_header_color),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, table_grid_color),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(toc_table)
    story.append(PageBreak())

    table_number = 0
    schema_number = 0
    code_schema_number = 0
    table_label = spec["tables"]["caption_prefix"]
    schema_label = spec["math_schema"]["caption_prefix"]
    code_schema_label = spec.get("code_schema", {}).get("caption_prefix", "Code Schema")

    def _title_case_key(raw_key: str) -> str:
        return raw_key.replace("_", " ").strip().title()

    def _format_simple_value(value: Any) -> str:
        if value is None:
            return "-"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)

    def _append_key_value_table(
        rows: list[list[str]],
        key_header: str,
        value_header: str,
    ) -> None:
        if not rows:
            return
        table_rows: list[list[Any]] = [[key_header, value_header]]
        for key, value in rows:
            table_rows.append(
                [
                    Paragraph(html.escape(key), styles["body"]),
                    Paragraph(html.escape(value), styles["body"]),
                ]
            )
        kv_table = Table(table_rows, colWidths=[150, 300])
        kv_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BACKGROUND", (0, 0), (-1, 0), table_header_color),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("GRID", (0, 0), (-1, -1), 0.5, table_grid_color),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(kv_table)
        story.append(Spacer(1, 8))

    # Main sections in fixed order.
    for idx, definition in enumerate(section_defs):
        if idx > 0:
            story.append(PageBreak())
        heading = Paragraph(definition.title, styles["heading"])
        setattr(heading, "_section_id", definition.section_id)
        story.append(heading)

        blocks = sections[definition.section_id]
        for block in blocks:
            block_type = block["type"]
            if block_type == "paragraph":
                text = html.escape(str(block.get("text", "")).strip())
                if text:
                    story.append(Paragraph(text, styles["body"]))
                continue

            if block_type == "table":
                table_number += 1
                caption = block.get("caption", "Untitled table")
                story.append(
                    Paragraph(
                        html.escape(f"{table_label} {table_number}. {caption}"),
                        styles["caption"],
                    )
                )
                columns = block.get("columns", [])
                rows = block.get("rows", [])
                table_data: list[list[str]] = []
                if columns:
                    table_data.append([str(col) for col in columns])
                for row in rows:
                    table_data.append([str(cell) for cell in row])
                if not table_data:
                    table_data = [["(empty table)"]]
                col_count = max(len(row) for row in table_data)
                normalized_rows = []
                for row in table_data:
                    padded = row + [""] * (col_count - len(row))
                    normalized_rows.append(padded)
                table = Table(normalized_rows, repeatRows=1 if columns else 0)
                table.setStyle(
                    TableStyle(
                        [
                            ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
                            ("FONTSIZE", (0, 0), (-1, -1), 10),
                            ("GRID", (0, 0), (-1, -1), 0.5, table_grid_color),
                            ("LEFTPADDING", (0, 0), (-1, -1), 4),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                            ("TOPPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ]
                    )
                )
                if columns:
                    table.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), table_header_color),
                                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                            ]
                        )
                    )
                story.append(table)
                story.append(Spacer(1, 8))
                continue

            if block_type == "code":
                code_schema_number += 1
                caption_prefix = f"{code_schema_label} {code_schema_number}"
            else:
                schema_number += 1
                caption_prefix = f"{schema_label} {schema_number}"

            caption = block.get("caption", "Structured schema")
            story.append(
                Paragraph(
                    html.escape(f"{caption_prefix}. {caption}"),
                    styles["caption"],
                )
            )

            raw_schema = block.get("schema", {})
            schema_obj = raw_schema if isinstance(raw_schema, dict) else {"value": raw_schema}

            equation = str(schema_obj.get("equation", "")).strip()
            if equation:
                story.append(
                    Paragraph(
                        html.escape(f"Equation: {equation}"),
                        styles["body"],
                    )
                )

            description = str(schema_obj.get("description", "")).strip()
            if description:
                story.append(
                    Paragraph(
                        html.escape(f"Description: {description}"),
                        styles["body"],
                    )
                )

            variables = schema_obj.get("variables", {})
            if isinstance(variables, dict) and variables:
                variable_rows = []
                for key, value in variables.items():
                    variable_rows.append([str(key), _format_simple_value(value)])
                _append_key_value_table(variable_rows, "Variable", "Meaning")

            bands = schema_obj.get("bands", {})
            if isinstance(bands, dict) and bands:
                band_rows = []
                for key, value in bands.items():
                    band_rows.append([str(key), _format_simple_value(value)])
                _append_key_value_table(band_rows, "Band", "Range / Meaning")

            thresholds = schema_obj.get("thresholds", {})
            if isinstance(thresholds, dict) and thresholds:
                threshold_rows = []
                for key, value in thresholds.items():
                    threshold_rows.append([str(key), _format_simple_value(value)])
                _append_key_value_table(threshold_rows, "Threshold", "Value")

            if block_type == "code":
                language = str(schema_obj.get("language", "")).strip()
                if language:
                    story.append(
                        Paragraph(
                            html.escape(f"Language: {language}"),
                            styles["body"],
                        )
                    )
                purpose = str(schema_obj.get("purpose", "")).strip()
                if purpose:
                    story.append(
                        Paragraph(
                            html.escape(f"Purpose: {purpose}"),
                            styles["body"],
                        )
                    )
                code_snippet = str(
                    schema_obj.get("code", schema_obj.get("snippet", ""))
                ).rstrip()
                if code_snippet:
                    story.append(Preformatted(code_snippet, styles["mono"]))
                    story.append(Spacer(1, 8))

            recognized_keys = {
                "equation",
                "description",
                "variables",
                "bands",
                "thresholds",
                "language",
                "purpose",
                "code",
                "snippet",
            }
            extra_rows = []
            for key, value in schema_obj.items():
                if key in recognized_keys:
                    continue
                extra_rows.append([_title_case_key(str(key)), _format_simple_value(value)])
            _append_key_value_table(extra_rows, "Field", "Value")

            if (
                not equation
                and not description
                and not (isinstance(variables, dict) and variables)
                and not (isinstance(bands, dict) and bands)
                and not (isinstance(thresholds, dict) and thresholds)
                and not extra_rows
                and block_type != "code"
            ):
                story.append(Paragraph("No schema details provided.", styles["body"]))
                story.append(Spacer(1, 8))

    # References at end.
    story.append(PageBreak())
    story.append(Paragraph(spec["structure"]["references_title"], styles["heading"]))
    if references:
        for idx, item in enumerate(references, start=1):
            title = item["title"] or "Untitled source"
            url = item["url"]
            if url:
                text = f"[{idx}] {title}. {url}"
            else:
                text = f"[{idx}] {title}."
            story.append(Paragraph(html.escape(text), styles["reference"]))
            note = str(item.get("note", "")).strip()
            if not note:
                note = str(spec.get("references", {}).get("default_note", "")).strip()
            if note:
                story.append(
                    Paragraph(
                        html.escape(f"Relevance: {note}"),
                        styles["reference_note"],
                    )
                )
    else:
        story.append(Paragraph("No references provided.", styles["body"]))

    return story


def render_official_paper(payload: dict[str, Any], output_path: Path, spec: dict[str, Any]) -> dict[str, int]:
    rl = load_reportlab()
    section_defs = [
        SectionDef(item["id"], item["title"])
        for item in spec["structure"]["main_sections"]
    ]
    sections = normalize_sections(payload.get("sections"), section_defs)
    index_defaults = spec.get("index", {}).get("default_section_summaries", {})
    index_descriptions = normalize_index_descriptions(
        payload.get("index_descriptions"),
        section_defs,
        index_defaults if isinstance(index_defaults, dict) else {},
    )
    references = normalize_references(payload.get("references"))
    body_word_count = estimate_body_word_count(sections)
    min_word_count = int(spec.get("quality", {}).get("min_word_count", 0))
    if min_word_count and body_word_count < min_word_count:
        print(
            f"[WARN] Body word count is {body_word_count}, below template minimum {min_word_count}.",
            file=sys.stderr,
        )

    styles = build_styles(rl, spec)
    OfficialPaperDoc = make_doc_class(rl)

    # First pass to determine section start pages for index table.
    draft_buffer = io.BytesIO()
    first_doc = OfficialPaperDoc(draft_buffer, spec["page"])
    first_story = build_story(
        rl=rl,
        styles=styles,
        spec=spec,
        payload=payload,
        section_defs=section_defs,
        sections=sections,
        references=references,
        index_descriptions=index_descriptions,
        section_pages=None,
    )
    first_doc.build(first_story)
    section_pages = first_doc.section_pages

    output_path.parent.mkdir(parents=True, exist_ok=True)
    second_doc = OfficialPaperDoc(str(output_path), spec["page"])
    second_story = build_story(
        rl=rl,
        styles=styles,
        spec=spec,
        payload=payload,
        section_defs=section_defs,
        sections=sections,
        references=references,
        index_descriptions=index_descriptions,
        section_pages=section_pages,
    )
    second_doc.build(second_story)
    return {"body_word_count": body_word_count}


def prepare_payload(raw_payload: dict[str, Any], template_override: str | None) -> tuple[dict[str, Any], str]:
    payload = dict(raw_payload)

    raw_template = template_override or str(payload.get("template", "")).strip()
    if not raw_template:
        raise ValueError("Template is required. Provide --template or input field 'template'.")
    canonical_template = resolve_template(raw_template)

    title = str(payload.get("title", "")).strip()
    if not title:
        raise ValueError("Field 'title' is required.")
    payload["title"] = title

    subtitle = str(payload.get("subtitle", "")).strip()
    if subtitle:
        payload["subtitle"] = subtitle

    authors = payload.get("authors", [])
    if authors is None:
        authors = []
    if not isinstance(authors, list):
        raise ValueError("Field 'authors' must be an array of strings.")
    payload["authors"] = [str(name).strip() for name in authors if str(name).strip()]

    if payload.get("date") is not None:
        payload["date"] = str(payload.get("date")).strip()

    return payload, canonical_template


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a structured document JSON into PDF.")
    parser.add_argument("--input", required=True, help="Path to input JSON payload.")
    parser.add_argument("--output", required=True, help="Path to output PDF.")
    parser.add_argument(
        "--template",
        help="Optional free-text template override. Example: 'official paper'.",
    )
    args = parser.parse_args()

    try:
        raw_payload = load_json_file(Path(args.input))
        payload, template_id = prepare_payload(raw_payload, args.template)
        spec = load_template_spec(template_id)

        output_path = Path(args.output).resolve()
        render_stats: dict[str, int] | None = None
        if template_id == "official-paper":
            render_stats = render_official_paper(payload, output_path, spec)
        else:
            raise ValueError(f"Template '{template_id}' is not implemented.")

        print(f"[OK] Generated document: {output_path}")
        print(f"[OK] Template: {template_id}")
        if render_stats:
            print(f"[OK] Estimated body words: {render_stats.get('body_word_count', 0)}")
        return 0
    except (ValueError, RuntimeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
