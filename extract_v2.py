# -*- coding: utf-8 -*-
import pdfplumber
import re
import json

pdf_path = r"e:\해외에 가다\韩语单词\初级核心单词(550个).pdf"
out_path = r"e:\해외에 가다\韩语单词\words.json"

HANGUL_RE = re.compile(r'[\uAC00-\uD7A3]')
CN_RE = re.compile(r'[\u4e00-\u9fff]')

def is_korean_char(c):
    return bool(HANGUL_RE.search(c))
def is_chinese_char(c):
    return bool(CN_RE.search(c))

units = []

with pdfplumber.open(pdf_path) as pdf:
    for pi, page in enumerate(pdf.pages):
        chars = page.chars
        # 关键改进：通过字体大小过滤水印
        # 水印"韩语老师"的 size ≈ 33.9，正文 size ≈ 11-14
        # 过滤掉 size > 20 的字符（水印）以及水印的 l/x 字符（size≈20-25）
        chars = [c for c in chars if c.get('size', 12) <= 18]
        
        # 找序号列的数字
        left_idx_chars = [c for c in chars if 55 <= c['x0'] <= 95 and c['text'].isdigit()]
        right_idx_chars = [c for c in chars if 295 <= c['x0'] <= 335 and c['text'].isdigit()]
        
        def group_by_row(char_list):
            rows = []
            char_list = sorted(char_list, key=lambda c: (c['top'], c['x0']))
            for c in char_list:
                placed = False
                for row in rows:
                    if c['top'] < row['bottom'] + 3 and c['bottom'] > row['top'] - 3:
                        row['chars'].append(c)
                        row['top'] = min(row['top'], c['top'])
                        row['bottom'] = max(row['bottom'], c['bottom'])
                        placed = True
                        break
                if not placed:
                    rows.append({'top': c['top'], 'bottom': c['bottom'], 'chars': [c]})
            return rows
        
        left_rows = group_by_row(left_idx_chars)
        right_rows = group_by_row(right_idx_chars)
        
        def parse_row(idx_chars, word_x_min, word_x_max, cn_x_min, cn_x_max):
            idx_chars = sorted(idx_chars, key=lambda c: c['x0'])
            idx_str = ''.join(c['text'] for c in idx_chars)
            if not idx_str.isdigit():
                return None, '', ''
            idx = int(idx_str)
            top = min(c['top'] for c in idx_chars)
            bottom = max(c['bottom'] for c in idx_chars)
            # 找同行的字符（y重叠），扩大范围以捕获跨行释义
            row_chars = [c for c in chars 
                         if c['top'] < bottom + 18 and c['bottom'] > top - 3
                         and word_x_min - 5 <= c['x0'] <= cn_x_max + 5]
            row_chars = [c for c in row_chars if c not in idx_chars]
            row_chars.sort(key=lambda c: (c['top'], c['x0']))
            
            # 韩文单词：在word x范围内
            word_chars = [(c['x0'], c['text']) for c in row_chars 
                          if is_korean_char(c['text']) and word_x_min <= c['x0'] <= word_x_max]
            # 中文释义：中文字符 + 标点，在cn x范围内
            cn_chars = [(c['top'], c['x0'], c['text']) for c in row_chars 
                        if (is_chinese_char(c['text']) or c['text'] in ';；.。、，,()（）') 
                        and cn_x_min - 10 <= c['x0'] <= cn_x_max + 10]
            # 按 top 再按 x 排序（处理跨行释义）
            cn_chars.sort(key=lambda x: (x[0], x[1]))
            word = ''.join(t for _, t in sorted(word_chars))
            cn = ''.join(t for _, _, t in cn_chars)
            return idx, word, cn
        
        left_data = {}
        for row in left_rows:
            idx, w, c = parse_row(row['chars'], 115, 180, 200, 290)
            if idx is not None and w:
                left_data[idx] = (w, c)
        
        right_data = {}
        for row in right_rows:
            idx, w, c = parse_row(row['chars'], 345, 425, 435, 540)
            if idx is not None and w:
                right_data[idx] = (w, c)
        
        unit_words = []
        for i in range(1, 26):
            if i in left_data:
                w, c = left_data[i]
                unit_words.append({"idx": i, "word": w, "cn": c or ""})
        for i in range(26, 51):
            if i in right_data:
                w, c = right_data[i]
                unit_words.append({"idx": i, "word": w, "cn": c or ""})
        
        if unit_words:
            units.append({"unit": pi+1, "words": unit_words})

total = sum(len(u['words']) for u in units)
print(f"Total units: {len(units)}, total words: {total}")

# 检查是否有缺失
for u in units:
    missing_left = [i for i in range(1,26) if i not in {w['idx'] for w in u['words'] if w['idx'] < 26}]
    missing_right = [i for i in range(26,51) if i not in {w['idx'] for w in u['words'] if w['idx'] >= 26}]
    if missing_left or missing_right:
        print(f"  Unit {u['unit']}: missing L={missing_left} R={missing_right}")

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(units, f, ensure_ascii=False, indent=2)
print(f"Saved to {out_path}")

# 验证之前有问题的单词
print("\n=== 修复验证 ===")
for u in units:
    for w in u['words']:
        if (u['unit'], w['idx']) in [(3,41),(6,15),(8,29),(9,34),(11,7),(11,12)]:
            print(f"  单元{u['unit']} #{w['idx']}: {w['word']} - '{w['cn']}'")

# 检查是否还有水印污染
print("\n=== 水印检查 ===")
wm_count = 0
for u in units:
    for w in u['words']:
        if any(c in w['cn'] for c in '韩语老师'):
            # 排除已知的正确释义
            if w['cn'] in ('老人', '话;敬语', '老', '韩服'):
                continue
            print(f"  单元{u['unit']} #{w['idx']}: {w['word']} - '{w['cn']}'")
            wm_count += 1
if wm_count == 0:
    print("  无水印污染")
