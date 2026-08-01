# -*- coding: utf-8 -*-
"""精确检查第1页第2行 수입 的字符位置"""
import pdfplumber

pdf_path = r"e:\해외에 가다\韩语单词\中高级词汇.pdf"

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    chars = page.chars

    # 过滤水印
    text_chars = [c for c in chars if c['size'] < 15]

    # 第2行 top≈161.5
    row_chars = [c for c in text_chars if abs(c['top']-161.5) < 5]
    row_chars.sort(key=lambda c: c['x0'])

    print("第1页第2行 (수입) 所有字符:")
    print(f"{'text':8s} {'x0':>7s} {'x1':>7s} {'top':>7s} {'size':>5s} {'font':15s}")
    for c in row_chars:
        print(f"{c['text']!r:8s} {c['x0']:7.1f} {c['x1']:7.1f} {c['top']:7.1f} {c['size']:5.1f} {c.get('fontname','?'):15s}")

    # 同时看第1行(부족)对比
    print("\n第1页第1行 (부족) 所有字符:")
    row1_chars = [c for c in text_chars if abs(c['top']-125.9) < 5]
    row1_chars.sort(key=lambda c: c['x0'])
    for c in row1_chars:
        print(f"{c['text']!r:8s} {c['x0']:7.1f} {c['x1']:7.1f} {c['top']:7.1f} {c['size']:5.1f} {c.get('fontname','?'):15s}")

    # 第3行(열정)
    print("\n第1页第3行 (열정) 所有字符:")
    row3_chars = [c for c in text_chars if abs(c['top']-197.2) < 5]
    row3_chars.sort(key=lambda c: c['x0'])
    for c in row3_chars:
        print(f"{c['text']!r:8s} {c['x0']:7.1f} {c['x1']:7.1f} {c['top']:7.1f} {c['size']:5.1f} {c.get('fontname','?'):15s}")
