#!/usr/bin/env python3
"""Convert the proposal Markdown into Word-friendly HTML.

Word turns pasted HTML tables into native Word tables, which is the point of
this script: it is a paste bridge, not a general Markdown implementation. It
handles only the constructs used in Project_Proposal.md.

Usage:  python3 md_to_html.py [input.md] [output.html]
"""

import html
import re
import sys
from pathlib import Path

CSS = """
body   { font-family: Calibri, Helvetica, Arial, sans-serif; font-size: 11pt;
         line-height: 1.45; color: #111; max-width: 46em; margin: 2em auto; }
h1     { font-size: 20pt; margin: 0 0 .2em; }
h2     { font-size: 15pt; margin: 1.6em 0 .4em; border-bottom: 1px solid #ccc;
         padding-bottom: .15em; }
h3     { font-size: 12.5pt; margin: 1.3em 0 .35em; }
p, li  { margin: .5em 0; }
code   { font-family: Consolas, Menlo, monospace; font-size: 10pt;
         background: #f4f4f4; padding: 0 .2em; }
blockquote { margin: 1em 0; padding: .5em 1em; border-left: 3px solid #bbb;
             background: #fafafa; color: #444; }
hr     { border: 0; border-top: 1px solid #ccc; margin: 2em 0; }
img    { max-width: 100%; }
table  { border-collapse: collapse; width: 100%; margin: 1em 0;
         font-size: 10pt; }
th, td { border: 1px solid #999; padding: 5px 8px; text-align: left;
         vertical-align: top; }
th     { background: #e8eef7; font-weight: bold; }
"""

SEPARATOR = re.compile(r"^\|[\s:\-|]+\|$")


def inline(text):
    """Apply inline Markdown formatting, escaping HTML first."""
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def convert(md):
    lines = md.replace("\r\n", "\n").split("\n")
    out, i = [], 0

    def flush(buf, tag="p"):
        if buf:
            out.append(f"<{tag}>{inline(' '.join(buf).strip())}</{tag}>")
        return []

    para = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Table: a pipe row followed by a |---|---| separator
        if (
            stripped.startswith("|")
            and i + 1 < len(lines)
            and SEPARATOR.match(lines[i + 1].strip())
        ):
            para = flush(para)
            header = split_row(stripped)
            i += 2
            body = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                body.append(split_row(lines[i].strip()))
                i += 1
            out.append("<table>")
            out.append(
                "<tr>" + "".join(f"<th>{inline(c)}</th>" for c in header) + "</tr>"
            )
            for row in body:
                out.append(
                    "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>"
                )
            out.append("</table>")
            continue

        # Blank line ends a paragraph
        if not stripped:
            para = flush(para)
            i += 1
            continue

        # Horizontal rule
        if stripped == "---":
            para = flush(para)
            out.append("<hr>")
            i += 1
            continue

        # Standalone image
        img = re.fullmatch(r"!\[(.*?)\]\((.*?)\)", stripped)
        if img:
            para = flush(para)
            alt, src = html.escape(img.group(1)), html.escape(img.group(2))
            out.append(f'<p><img src="{src}" alt="{alt}"></p>')
            i += 1
            continue

        # Heading
        head = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if head:
            para = flush(para)
            level = len(head.group(1))
            out.append(f"<h{level}>{inline(head.group(2))}</h{level}>")
            i += 1
            continue

        # Blockquote (consecutive lines joined)
        if stripped.startswith(">"):
            para = flush(para)
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append(f"<blockquote>{inline(' '.join(quote))}</blockquote>")
            continue

        # Lists, with indented continuation lines folded into the item
        item = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if item:
            para = flush(para)
            tag = "ul" if item.group(2) in ("-", "*") else "ol"
            out.append(f"<{tag}>")
            while i < len(lines):
                m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
                if not m:
                    break
                text = [m.group(3)]
                i += 1
                while (
                    i < len(lines)
                    and lines[i].strip()
                    and lines[i].startswith((" ", "\t"))
                    and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[i])
                ):
                    text.append(lines[i].strip())
                    i += 1
                out.append(f"<li>{inline(' '.join(text))}</li>")
            out.append(f"</{tag}>")
            continue

        para.append(stripped)
        i += 1

    flush(para)
    body = "\n".join(out)
    return (
        '<!DOCTYPE html>\n<html><head><meta charset="utf-8">'
        f"<title>Project Proposal</title><style>{CSS}</style></head>\n"
        f"<body>\n{body}\n</body></html>\n"
    )


if __name__ == "__main__":
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "Project_Proposal.md")
    dst = Path(sys.argv[2] if len(sys.argv) > 2 else src.with_suffix(".html"))
    dst.write_text(convert(src.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"Wrote {dst}")
