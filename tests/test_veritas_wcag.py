from pathlib import Path

from veritas_wcag import audit_html, checklist, lookup


PASSING_HTML = """<!doctype html>
<html lang="en">
<head><title>Sample</title></head>
<body>
  <img src="a.png" alt="Chart of monthly errors">
  <a href="/about">About</a>
  <label for="email">Email</label>
  <input id="email" type="email">
  <button>Save</button>
</body>
</html>
"""

FAILING_HTML = """<!doctype html>
<html>
<head></head>
<body>
  <img src="a.png">
  <a href="/about"></a>
  <input type="text">
  <button></button>
  <iframe src="https://example.com"></iframe>
  <audio autoplay></audio>
  <div tabindex="3">Skip</div>
</body>
</html>
"""


def test_lookup_by_number_and_id():
    by_num = lookup("1.4.3")
    by_id = lookup("contrast-minimum")
    assert by_num is not None
    assert by_id is not None
    assert by_num.num == "1.4.3"
    assert by_num.level == "AA"
    assert by_num.handle == "Contrast (Minimum)"
    assert by_id.num == by_num.num


def test_aa_checklist_count_and_excludes_removed_parsing():
    rows = checklist(max_level="AA")
    assert len(rows) == 55
    assert all(row.level in {"A", "AA"} for row in rows)
    assert lookup("4.1.1") is not None
    assert lookup("4.1.1").level is None
    assert "4.1.1" not in {row.num for row in rows}


def test_principle_filter():
    robust = checklist(max_level="AA", principle="robust")
    assert [row.num for row in robust] == ["4.1.2", "4.1.3"]


def test_audit_passing_html_has_no_findings():
    assert audit_html(PASSING_HTML) == []


def test_audit_failing_html_maps_known_criteria():
    findings = audit_html(FAILING_HTML)
    codes = {item.criterion for item in findings}
    assert {"1.1.1", "1.4.2", "2.4.2", "2.4.3", "2.4.4", "3.1.1", "3.3.2", "4.1.2"} <= codes


def test_catalog_file_exists():
    path = Path(__file__).resolve().parents[1] / "data" / "wcag22_success_criteria.json"
    assert path.is_file()
