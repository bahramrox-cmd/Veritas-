---
id: e41c9b77-0d5a-4f6e-8a12-9f3b21c0d8aa
title: WCAG 2.2
desc: Map W3C WCAG 2.2 onto Veritas protocol work
updated: 1762462020000
created: 1762462020000
---

# WCAG 2.2

## Provenance

- **Documented source:** W3C Web Content Accessibility Guidelines (WCAG) 2.2, from the uploaded JSON catalog of principles, guidelines, and success criteria.
- **Spec:** https://www.w3.org/TR/WCAG22/
- **Compact machine catalog in this repo:** `data/wcag22_success_criteria.json` (numbers, handles, titles, levels, versions). Techniques HTML from the dump was not copied.
- **Working notes** below are interpretation. They are not W3C text and not an existing Veritas product requirement until you adopt them.

WCAG 2.2 Level AA is 31 Level A plus 24 Level AA success criteria (55). Criterion 4.1.1 Parsing is obsolete and removed in 2.2; it remains in the catalog with `level: null` and is excluded from A/AA checklists.

## Documented principles (W3C handles)

1. Perceivable
2. Operable
3. Understandable
4. Robust

## Working notes: map onto Veritas

These pairings are proposed design, not documented Veritas protocol source.

| WCAG principle | Veritas concern | Proposed reading |
| --- | --- | --- |
| Perceivable | Truth has to reach a person | A finding that cannot be seen, heard, or otherwise perceived is not available. Text alternatives, structure, contrast, and media alternatives are how the claim stays presentable. |
| Operable | The person stays in control | Keyboard access, time, navigation, and input size/gestures keep the user able to act without being trapped or rushed. |
| Understandable | Humility and plain language | Page language, predictable UI, and error identification/suggestion reduce false certainty and hidden process. |
| Robust | The record survives tools | Name, role, value, and status messages keep content usable by assistive technology and by later agents reading the same UI. |

## Working notes: conformance target

- **Supported for a future Veritas web UI:** WCAG 2.2 Level AA (the usual legal/public target).
- **Not claimed for this repository today:** there is no web application in `Veritas-`. The Docker image only prints `veritas docker-build-cloud-demo`. WCAG applies to web content, not to that container by itself.
- **AAA:** 31 additional criteria. Useful as stretch goals; not the default bar.

## Lookup and audit helpers

```text
python veritas_wcag.py lookup 1.4.3
python veritas_wcag.py checklist --max-level AA
python veritas_wcag.py audit path\to\page.html
```

`audit` is a small HTML heuristic (alt, lang, title, labels, names, autoplay, positive tabindex). It is not a WCAG conformance audit.
