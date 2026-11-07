"""Compact WCAG 2.2 lookup and heuristic HTML audit helpers.

The catalog stores official success-criterion numbers, handles, titles, and
levels from the W3C WCAG 2.2 JSON. It does not copy techniques or full
criterion HTML. Heuristic audits are not a conformance claim.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Sequence

CATALOG_PATH = Path(__file__).resolve().parent / "data" / "wcag22_success_criteria.json"
LEVEL_RANK = {"A": 1, "AA": 2, "AAA": 3}

_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


@dataclass(frozen=True)
class SuccessCriterion:
    num: str
    id: str
    handle: str
    title: str
    level: str | None
    principle_id: str
    principle: str
    guideline_num: str
    guideline: str
    versions: tuple[str, ...]


@dataclass(frozen=True)
class AuditFinding:
    criterion: str
    level: str
    severity: str
    summary: str
    evidence: str


def load_catalog(path: Path | None = None) -> list[SuccessCriterion]:
    catalog_path = path or CATALOG_PATH
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    rows = []
    for item in payload["criteria"]:
        rows.append(
            SuccessCriterion(
                num=item["num"],
                id=item["id"],
                handle=item["handle"],
                title=item["title"],
                level=item.get("level"),
                principle_id=item["principle_id"],
                principle=item["principle"],
                guideline_num=item["guideline_num"],
                guideline=item["guideline"],
                versions=tuple(item.get("versions") or ()),
            )
        )
    return rows


def lookup(query: str, catalog: Sequence[SuccessCriterion] | None = None) -> SuccessCriterion | None:
    needle = query.strip().lower()
    rows = catalog if catalog is not None else load_catalog()
    for row in rows:
        if row.num.lower() == needle or row.id.lower() == needle or row.handle.lower() == needle:
            return row
    return None


def checklist(
    *,
    max_level: str = "AA",
    principle: str | None = None,
    catalog: Sequence[SuccessCriterion] | None = None,
) -> list[SuccessCriterion]:
    cap = LEVEL_RANK[max_level.upper()]
    rows = catalog if catalog is not None else load_catalog()
    selected = []
    for row in rows:
        if row.level is None or LEVEL_RANK.get(row.level, 99) > cap:
            continue
        if principle and row.principle.lower() != principle.lower() and row.principle_id.lower() != principle.lower():
            continue
        selected.append(row)
    return selected


def _attr_map(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    return {key.lower(): (value or "") for key, value in attrs}


class _HtmlAuditor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.findings: list[AuditFinding] = []
        self._stack: list[tuple[str, dict[str, str]]] = []
        self._seen_html = False
        self._html_lang = False
        self._seen_title_tag = False
        self._title_text: list[str] = []
        self._in_title = False
        self._label_depth = 0
        self._label_for: str | None = None
        self._label_text: list[str] = []
        self._control_ids: set[str] = set()
        self._labeled_ids: set[str] = set()
        self._unnamed_controls: list[tuple[str, str]] = []
        self._link_depth = 0
        self._link_text: list[str] = []
        self._link_has_named_img = False
        self._button_depth = 0
        self._button_text: list[str] = []
        self._button_named_attr = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        amap = _attr_map(attrs)
        if tag not in _VOID:
            self._stack.append((tag, amap))

        if tag == "html":
            self._seen_html = True
            if amap.get("lang", "").strip() or amap.get("xml:lang", "").strip():
                self._html_lang = True

        if tag == "title":
            self._seen_title_tag = True
            self._in_title = True

        if tag == "img":
            if "alt" not in amap:
                self.findings.append(
                    AuditFinding(
                        "1.1.1",
                        "A",
                        "fail",
                        "Image is missing an alt attribute",
                        amap.get("src", "<img>"),
                    )
                )
            elif amap["alt"].strip() and self._link_depth:
                self._link_has_named_img = True

        if tag in {"audio", "video"}:
            if "autoplay" in amap and "controls" not in amap:
                self.findings.append(
                    AuditFinding(
                        "1.4.2",
                        "A",
                        "fail",
                        "Time-based media autoplays without controls",
                        tag,
                    )
                )

        if "tabindex" in amap:
            raw = amap["tabindex"].strip()
            if raw.lstrip("-").isdigit() and int(raw) > 0:
                self.findings.append(
                    AuditFinding(
                        "2.4.3",
                        "A",
                        "warn",
                        "Positive tabindex can break focus order",
                        f"{tag} tabindex={raw}",
                    )
                )

        if tag == "a":
            self._link_depth += 1
            self._link_text = []
            self._link_has_named_img = False
            if amap.get("aria-label", "").strip() or amap.get("aria-labelledby", "").strip() or amap.get("title", "").strip():
                self._link_has_named_img = True

        if tag == "iframe" and not (
            amap.get("title", "").strip()
            or amap.get("aria-label", "").strip()
            or amap.get("aria-labelledby", "").strip()
        ):
            self.findings.append(
                AuditFinding(
                    "4.1.2",
                    "A",
                    "fail",
                    "iframe has no accessible name",
                    amap.get("src", "<iframe>"),
                )
            )

        if tag == "label":
            self._label_depth += 1
            self._label_for = amap.get("for") or None
            self._label_text = []

        if tag in {"input", "select", "textarea"}:
            input_type = amap.get("type", "text").lower() if tag == "input" else tag
            if tag != "input" or input_type not in {"hidden", "submit", "button", "reset", "image"}:
                control_id = amap.get("id", "").strip()
                if control_id:
                    self._control_ids.add(control_id)
                named = bool(
                    amap.get("aria-label", "").strip()
                    or amap.get("aria-labelledby", "").strip()
                    or amap.get("title", "").strip()
                    or self._label_depth
                    or (tag == "input" and input_type in {"checkbox", "radio"} and self._label_depth)
                )
                if not named:
                    self._unnamed_controls.append((control_id, f"{tag} type={input_type}"))

        if tag == "button":
            self._button_depth += 1
            self._button_text = []
            self._button_named_attr = bool(
                amap.get("aria-label", "").strip()
                or amap.get("aria-labelledby", "").strip()
                or amap.get("title", "").strip()
            )

        if tag == "input" and amap.get("type", "text").lower() in {"submit", "button", "reset"}:
            if not (
                amap.get("value", "").strip()
                or amap.get("aria-label", "").strip()
                or amap.get("aria-labelledby", "").strip()
                or amap.get("title", "").strip()
            ):
                self.findings.append(
                    AuditFinding(
                        "4.1.2",
                        "A",
                        "fail",
                        "Button-style input has no accessible name",
                        f"input type={amap.get('type')}",
                    )
                )

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "a" and self._link_depth:
            self._link_depth -= 1
            text = "".join(self._link_text).strip()
            if not text and not self._link_has_named_img:
                self.findings.append(
                    AuditFinding(
                        "2.4.4",
                        "A",
                        "fail",
                        "Link has no accessible name",
                        "<a>",
                    )
                )
        if tag == "button" and self._button_depth:
            self._button_depth -= 1
            text = "".join(self._button_text).strip()
            if not text and not self._button_named_attr:
                self.findings.append(
                    AuditFinding(
                        "4.1.2",
                        "A",
                        "fail",
                        "Button has no accessible name",
                        "<button>",
                    )
                )
        if tag == "label" and self._label_depth:
            self._label_depth -= 1
            if self._label_for and "".join(self._label_text).strip():
                self._labeled_ids.add(self._label_for)
            self._label_for = None
        if self._stack and self._stack[-1][0] == tag:
            self._stack.pop()
        elif tag not in _VOID:
            for index in range(len(self._stack) - 1, -1, -1):
                if self._stack[index][0] == tag:
                    del self._stack[index:]
                    break

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_text.append(data)
        if self._link_depth:
            self._link_text.append(data)
        if self._button_depth:
            self._button_text.append(data)
        if self._label_depth:
            self._label_text.append(data)

    def finish(self) -> list[AuditFinding]:
        if self._seen_html and not self._html_lang:
            self.findings.append(
                AuditFinding("3.1.1", "A", "fail", "html element is missing a lang attribute", "<html>")
            )
        if not self._seen_title_tag or not "".join(self._title_text).strip():
            self.findings.append(
                AuditFinding("2.4.2", "A", "fail", "Document is missing a non-empty title", "<title>")
            )
        for control_id, evidence in self._unnamed_controls:
            if control_id and control_id in self._labeled_ids:
                continue
            self.findings.append(
                AuditFinding("3.3.2", "A", "fail", "Form control has no label or accessible name", evidence)
            )
        return self.findings


def audit_html(markup: str) -> list[AuditFinding]:
    parser = _HtmlAuditor()
    parser.feed(markup)
    parser.close()
    return parser.finish()


def audit_path(path: Path) -> list[AuditFinding]:
    return audit_html(path.read_text(encoding="utf-8"))


def _print_criterion(row: SuccessCriterion) -> None:
    level = row.level or "removed"
    print(f"{row.num} [{level}] {row.handle}")
    print(f"  {row.principle} / {row.guideline}")
    print(f"  {row.title}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Look up WCAG 2.2 criteria or heuristically audit HTML.")
    sub = parser.add_subparsers(dest="command", required=True)

    look = sub.add_parser("lookup", help="Find one criterion by number, id, or handle")
    look.add_argument("query")

    check = sub.add_parser("checklist", help="Print Level A/AA (or AAA) checklist")
    check.add_argument("--max-level", default="AA", choices=["A", "AA", "AAA"])
    check.add_argument("--principle", default=None)

    aud = sub.add_parser("audit", help="Heuristic HTML audit against a subset of A/AA checks")
    aud.add_argument("html_path")

    args = parser.parse_args(argv)
    catalog = load_catalog()

    if args.command == "lookup":
        row = lookup(args.query, catalog)
        if row is None:
            print(f"No criterion matched {args.query!r}", file=sys.stderr)
            return 1
        _print_criterion(row)
        return 0

    if args.command == "checklist":
        for row in checklist(max_level=args.max_level, principle=args.principle, catalog=catalog):
            print(f"{row.num}\t{row.level}\t{row.principle}\t{row.handle}")
        return 0

    findings = audit_path(Path(args.html_path))
    if not findings:
        print("No heuristic failures on the implemented checks.")
        return 0
    for finding in findings:
        print(f"{finding.severity}\t{finding.criterion}\t{finding.summary}\t{finding.evidence}")
    return 1 if any(item.severity == "fail" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
