# -*- coding: utf-8 -*-
import pdfplumber

pdf_path = r"e:\해외에 가다\韩语单词\初级核心单词(550个).pdf"

# 检查有问题的单词
# 单元3 #41: 세우다 - 左列idx41
# 单元6 #15: 한복 - 左列idx15
# 单元8 #29: 치다 - 右列idx29 (row 4 of right col)
# 单元9 #34: 늙다 - 右列idx34 (row 9 of right col)

# 单元=页码，每页50词，左列1-25，右列26-50
# 左列idx N 的 top ≈ 120 + (N-1)*26.8
# 右列idx N 的 top ≈ 120 + (N-26)*26.8

problems = [
    (3, 41, 'right', '세우다'),   # 停(车)划;制)定(计
    (6, 15, 'left', '한복'),      # 服 (应为韩服)
    (8, 29, 'right', '치다'),     # (球);弹(乐器) (应为打(球);弹(乐器))
]

with pdfplumber.open(pdf_path) as pdf:
    for unit, idx, col, word in problems:
        page = pdf.pages[unit-1]
        if col == 'left':
            top_approx = 120 + (idx-1)*26.8
            x_range = (200, 290)
        else:
            top_approx = 120 + (idx-26)*26.8
            x_range = (445, 540)
        
        print(f"\n=== 单元{unit} #{idx} {word} (col={col}, top≈{top_approx:.0f}) ===")
        # 查找该行附近的所有字符
        for c in page.chars:
            if top_approx - 15 <= c['top'] <= top_approx + 15:
                if x_range[0] - 10 <= c['x0'] <= x_range[1] + 10:
                    print(f"  text={c['text']!r} x0={c['x0']:.1f} top={c['top']:.1f} size={c.get('size',0):.1f} fontname={c.get('fontname','?')}")

        # 也查看更宽范围
        print(f"  --- 完整行(top {top_approx-15:.0f}-{top_approx+15:.0f}) ---")
        for c in page.chars:
            if top_approx - 15 <= c['top'] <= top_approx + 15:
                if c['x0'] < 540 and c['text'] not in ('x','l'):
                    print(f"  text={c['text']!r} x0={c['x0']:.1f} top={c['top']:.1f} size={c.get('size',0):.1f}")
