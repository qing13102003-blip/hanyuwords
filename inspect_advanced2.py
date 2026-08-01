# -*- coding: utf-8 -*-
"""详细检查中高级词汇.pdf - 看每页结构和词数"""
import pdfplumber
import re

pdf_path = r"e:\해외에 가다\韩语单词\中高级词汇.pdf"

def is_korean_char(t):
    return '\uAC00' <= t <= '\uD7A3'

def is_chinese_char(t):
    return '\u4e00' <= t <= '\u9fff'

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    print(f"总页数: {total_pages}")

    # 检查第1页、第50页、最后一页的结构
    for pi in [0, 49, total_pages-1]:
        page = pdf.pages[pi]
        chars = page.chars

        # 过滤水印 (size > 15)
        text_chars = [c for c in chars if c['size'] < 15]

        # 找出所有序号字符 (size=11, x0在60-70之间)
        idx_chars = [c for c in text_chars if abs(c['size']-11.0)<0.1 and 55 < c['x0'] < 75]
        idx_chars.sort(key=lambda c: c['top'])

        # 提取每行的序号
        row_tops = []
        for c in idx_chars:
            # 检查是否是数字
            if c['text'].isdigit():
                row_tops.append((c['text'], c['top']))

        print(f"\n=== 第{pi+1}页 ===")
        print(f"文本字符数: {len(text_chars)}")
        print(f"序号字符数: {len(idx_chars)}")
        print(f"行数(按序号): {len(row_tops)}")
        if row_tops:
            print(f"首行top: {row_tops[0][1]}, 末行top: {row_tops[-1][1]}")
            print(f"首行序号: {row_tops[0][0]}, 末行序号: {row_tops[-1][0]}")

        # 显示前5行的详细数据
        print("\n前5行详情:")
        for i, (idx_text, top) in enumerate(row_tops[:5]):
            # 同一行的字符 (top范围 ±5)
            row_chars = [c for c in text_chars if abs(c['top']-top) < 5]
            row_chars.sort(key=lambda c: c['x0'])

            # 按x位置分组
            idx_part = ''.join(c['text'] for c in row_chars if c['x0'] < 120)
            word_part = ''.join(c['text'] for c in row_chars if 120 <= c['x0'] < 215)
            source_part = ''.join(c['text'] for c in row_chars if 215 <= c['x0'] < 283)
            pos_part = ''.join(c['text'] for c in row_chars if 283 <= c['x0'] < 390)
            cn_part = ''.join(c['text'] for c in row_chars if 390 <= c['x0'] < 585)
            app_part = ''.join(c['text'] for c in row_chars if c['x0'] >= 585)

            print(f"  行{i+1} [top={top:.1f}]:")
            print(f"    序号: {idx_part}")
            print(f"    单词: {word_part}")
            print(f"    来源: {source_part}")
            print(f"    词性: {pos_part}")
            print(f"    释义: {cn_part}")
            print(f"    应用: {app_part}")
