#!/usr/bin/env python3
"""Build a Word-ready HTML page from the project plan CSVs.

Edit the CSVs (in Excel, Numbers or a text editor), re-run this, then copy the
tables out of the browser and paste them into Word.

Usage:  python3 make_plan_html.py
"""

import csv
import html
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "project_plan.html"

TABLES = [
    ("4.1 Project Timeline", "project_plan.csv",
     "Approximately 275 hours in total. Phases overlap: the platform work in P4 runs "
     "alongside P3 so there is always something to progress when one side is blocked."),
    ("4.2 Goals", "project_goals.csv",
     "The basic goals together make a complete project. Stretch goals are attempted in "
     "the order listed, only once the basics are working."),
]

CSS = """
body  { font-family: Calibri, Helvetica, Arial, sans-serif; font-size: 11pt;
        color: #111; max-width: 50em; margin: 2.5em auto; line-height: 1.45; }
h1    { font-size: 17pt; margin-bottom: .2em; }
h2    { font-size: 13pt; margin: 2em 0 .4em; }
p.note{ color: #444; font-size: 10.5pt; margin: .3em 0 1em; }
p.tip { background: #f3f6fb; border-left: 3px solid #7f9fd0; padding: .7em 1em;
        font-size: 10.5pt; color: #333; }
table { border-collapse: collapse; width: 100%; margin-bottom: .5em; font-size: 10pt; }
th, td{ border: 1px solid #8c8c8c; padding: 6px 9px; text-align: left;
        vertical-align: top; }
th    { background: #e8eef7; font-weight: bold; }
tr.total td { font-weight: bold; background: #f6f6f6; }
td.num, th.num { text-align: right; white-space: nowrap; }
"""


def render(title, csv_name, note):
    rows = list(csv.reader((HERE / csv_name).open(encoding="utf-8")))
    header, body = rows[0], [r for r in rows[1:] if any(c.strip() for c in r)]

    def cell(tag, text, last_col):
        klass = ' class="num"' if last_col and text.strip().isdigit() else ""
        if last_col and tag == "th" and text.strip().lower() == "hours":
            klass = ' class="num"'
        return f"<{tag}{klass}>{html.escape(text)}</{tag}>"

    out = [f"<h2>{html.escape(title)}</h2>", f'<p class="note">{html.escape(note)}</p>',
           "<table>", "<tr>"]
    out += [cell("th", c, i == len(header) - 1) for i, c in enumerate(header)]
    out.append("</tr>")
    for row in body:
        total = row[0].strip().lower() == "total"
        out.append('<tr class="total">' if total else "<tr>")
        out += [cell("td", c, i == len(row) - 1) for i, c in enumerate(row)]
        out.append("</tr>")
    out.append("</table>")
    return "\n".join(out)


body = "\n".join(render(*t) for t in TABLES)
OUT.write_text(
    '<!DOCTYPE html>\n<html><head><meta charset="utf-8">'
    f"<title>Project Management Plan</title><style>{CSS}</style></head>\n<body>\n"
    "<h1>Project Management Plan</h1>\n"
    '<p class="tip">To use these: select a table with the mouse, copy, and paste into '
    "Word. It arrives as a real Word table. Then right-click it and apply your "
    "template&rsquo;s table style so it matches the rest of the document.</p>\n"
    f"{body}\n</body></html>\n",
    encoding="utf-8",
)
print(f"Wrote {OUT}")
