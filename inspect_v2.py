# -*- coding: utf-8 -*-
import pdfplumber

pdf_path = r"e:\해외에 가다\韩语单词\初级核心单词(550个).pdf"

# 检查单元3 #41 세우다 和 单元11 #12 말씀 的原始字符
with pdfplumber.open(pdf_path) as pdf:
    # 单元3 #41 (right col, idx=41, top≈522)
    page = pdf.pages[2]
    print("=== 单元3 #41 세우다 (top 510-540) ===")
    for c in page.chars:
        if 510 <= c['top'] <= 540 and c['x0'] > 430 and c['x0'] < 540:
            if c.get('size', 12) <= 18:
                print(f"  text={c['text']!r} x0={c['x0']:.1f} top={c['top']:.1f} size={c.get('size',0):.1f}")

    # 单元11 #12 말씀 (left col, idx=12, top≈415)
    page = pdf.pages[10]
    print("\n=== 单元11 #12 말씀 (top 405-430) ===")
    for c in page.chars:
        if 405 <= c['top'] <= 430 and c['x0'] > 195 and c['x0'] < 290:
            if c.get('size', 12) <= 18:
                print(f"  text={c['text']!r} x0={c['x0']:.1f} top={c['top']:.1f} size={c.get('size',0):.1f}")
