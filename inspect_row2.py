# -*- coding: utf-8 -*-
"""检查第1页第6行(물리)和第7行(넘어지다)的字符"""
import pdfplumber

pdf_path = r"e:\해외에 가다\韩语单词\中高级词汇.pdf"

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    chars = page.chars
    text_chars = [c for c in chars if c['size'] < 15]

    # 第6行 top≈125.9 + 5*35.6 = 303.9
    # 第7行 top≈125.9 + 6*35.6 = 339.5
    for label, top_approx in [("第6行 물리", 303.9), ("第7行 넘어지다", 339.5)]:
        row_chars = [c for c in text_chars if abs(c['top']-top_approx) < 5]
        row_chars.sort(key=lambda c: c['x0'])
        print(f"\n{label} (top≈{top_approx}):")
        print(f"{'text':8s} {'x0':>7s} {'x1':>7s} {'top':>7s} {'size':>5s} {'font':15s}")
        for c in row_chars:
            print(f"{c['text']!r:8s} {c['x0']:7.1f} {c['x1']:7.1f} {c['top']:7.1f} {c['size']:5.1f} {c.get('fontname','?'):15s}")
