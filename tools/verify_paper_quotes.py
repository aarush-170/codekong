"""Check that every quoted "Current" passage in paper/EDITS_PENDING.md appears
verbatim in the paper .docx, so each pending edit can be applied mechanically.

    python tools/verify_paper_quotes.py            # check EDITS_PENDING.md
    python tools/verify_paper_quotes.py --dump     # print the paper's text

Text is taken from word/document.xml, one line per paragraph (runs joined).
The draft uses curly apostrophes and em dashes; quotes must match exactly.
Exit code 1 if any quote is missing.
"""
from __future__ import annotations

import html
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCX = ROOT / "paper" / "CodeKong_RAG_Mutation_Testing.docx"
EDITS = ROOT / "paper" / "EDITS_PENDING.md"


def paper_text() -> str:
    xml = zipfile.ZipFile(DOCX).read("word/document.xml").decode("utf-8")
    paras = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S):
        t = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))
        if t.strip():
            paras.append(html.unescape(t))
    return "\n".join(paras)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    text = paper_text()
    if "--dump" in sys.argv:
        print(text)
        return 0
    edits = EDITS.read_text(encoding="utf-8")
    blocks = re.findall(r"\*\*[^\n]*Current[^\n]*\*\*\n\n((?:>.*\n?)+)", edits)
    missing = 0
    for block in blocks:
        for line in block.splitlines():
            quote = line.lstrip(">").strip()
            if not quote:
                continue
            ok = quote in text
            missing += not ok
            print(("OK   " if ok else "MISS ") + quote[:90])
    print(f"\n{len(blocks)} quoted blocks, {missing} line(s) not found verbatim")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
