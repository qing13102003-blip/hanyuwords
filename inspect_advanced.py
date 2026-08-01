# -*- coding: utf-8 -*-
"""检查中高级词汇.pdf的结构"""
import pdfplumber

pdf_path = r"e:\해외에 가다\韩语单词\中高级词汇.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"总页数: {len(pdf.pages)}")
    print("="*70)

    # 检查前2页的结构
    for pi, page in enumerate(pdf.pages[:2]):
        print(f"\n--- 第{pi+1}页 ---")
        print(f"页面尺寸: width={page.width}, height={page.height}")

        chars = page.chars
        print(f"字符总数: {len(chars)}")

        # 字符大小分布
        sizes = {}
        for c in chars:
            sz = round(c['size'], 1)
            sizes[sz] = sizes.get(sz, 0) + 1
        print(f"字符大小分布: {sorted(sizes.items())}")

        # 显示前30个字符的详细信息
        print("\n前30个字符:")
        for c in chars[:30]:
            print(f"  text={c['text']!r:8s} x0={c['x0']:.1f} top={c['top']:.1f} size={c['size']:.1f} fontname={c.get('fontname','?')}")

        # 提取页面文本
        text = page.extract_text()
        if text:
            print(f"\n页面文本（前500字符）:")
            print(text[:500])
        print("="*70)
