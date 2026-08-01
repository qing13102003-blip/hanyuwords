# -*- coding: utf-8 -*-
"""从中高级词汇.pdf提取所有词汇，保留全部6列内容（照搬）"""
import pdfplumber
import json
import re

pdf_path = r"e:\해외에 가다\韩语单词\中高级词汇.pdf"

def is_korean_char(t):
    return '\uAC00' <= t <= '\uD7A3'

def is_chinese_char(t):
    return '\u4e00' <= t <= '\u9fff'

def extract_words():
    all_units = []
    unit_num = 1
    unit_words = []
    words_per_unit = 50  # 每50个词一个单元

    with pdfplumber.open(pdf_path) as pdf:
        global_idx = 0  # 全局词序号

        for page in pdf.pages:
            chars = page.chars
            # 过滤水印 (size > 15)
            text_chars = [c for c in chars if c['size'] < 15]

            # 找出所有行（按top分组）
            # 序号字符: size≈11, x0在55-75之间
            idx_chars = [c for c in text_chars if abs(c['size']-11.0) < 0.5 and 55 < c['x0'] < 75]

            # 按top合并序号字符（同top的多个数字字符合并为一个序号）
            if not idx_chars:
                continue
            idx_chars.sort(key=lambda c: c['top'])

            # 按top分组（top相差<3视为同一行）
            rows = []
            current_row = [idx_chars[0]]
            for c in idx_chars[1:]:
                if abs(c['top'] - current_row[-1]['top']) < 3:
                    current_row.append(c)
                else:
                    rows.append(current_row)
                    current_row = [c]
            rows.append(current_row)

            for row_idx_chars in rows:
                top = row_idx_chars[0]['top']
                # 合并序号文本
                row_idx_chars.sort(key=lambda c: c['x0'])
                idx_text = ''.join(c['text'] for c in row_idx_chars).strip()

                # 验证是纯数字
                if not idx_text.isdigit():
                    continue

                # 获取该行所有字符（top范围 ±5）
                row_chars = [c for c in text_chars if abs(c['top'] - top) < 5 and c not in row_idx_chars]
                row_chars.sort(key=lambda c: c['x0'])

                if not row_chars:
                    continue

                # 分类提取各列
                word_parts = []      # 单词（韩文，size≈13）
                source_parts = []    # 对应来源（F2，括号汉字或/）
                pos_parts = []        # 词性（F2，[xxx]）
                cn_parts = []         # 释义（F3中文）
                example_parts = []    # 应用（F2韩文+F3中文混合）

                # 状态机
                phase = 'word'  # word -> source -> pos -> cn -> example
                pos_closed = False

                for c in row_chars:
                    text = c['text']
                    font = c.get('fontname', '')
                    x0 = c['x0']
                    size = c['size']

                    # 单词：size≈13 或 在word阶段且x0<200
                    if phase == 'word':
                        if x0 < 200:
                            word_parts.append(text)
                        elif text == '(' or text == '/' or (is_chinese_char(text) and font == 'CIDFont+F2' and x0 < 285):
                            # 进入来源阶段
                            phase = 'source'
                            source_parts.append(text)
                        elif text == '[':
                            # 直接进入词性阶段
                            phase = 'pos'
                            pos_parts.append(text)
                        elif font == 'CIDFont+F3':
                            # 直接是释义（无来源无词性）
                            phase = 'cn'
                            cn_parts.append(text)
                        else:
                            word_parts.append(text)

                    elif phase == 'source':
                        if text == '[':
                            phase = 'pos'
                            pos_parts.append(text)
                        elif font == 'CIDFont+F3' and not (text == '(' or text == ')' or text == '[' or text == ']'):
                            # 进入释义阶段
                            phase = 'cn'
                            cn_parts.append(text)
                        else:
                            source_parts.append(text)

                    elif phase == 'pos':
                        pos_parts.append(text)
                        if text == ']':
                            pos_closed = True
                            phase = 'cn'

                    elif phase == 'cn':
                        if is_korean_char(text):
                            # 韩文字符出现在释义后，进入应用阶段（应用列韩文用F5字体）
                            phase = 'example'
                            example_parts.append(text)
                        elif font == 'CIDFont+F3' or text in '；;，,、':
                            cn_parts.append(text)
                        else:
                            cn_parts.append(text)

                    elif phase == 'example':
                        example_parts.append(text)

                # 清理各字段
                word = ''.join(word_parts).strip()
                source = ''.join(source_parts).strip()
                pos = ''.join(pos_parts).strip()
                cn = ''.join(cn_parts).strip()
                example = ''.join(example_parts).strip()

                if not word:
                    continue

                global_idx += 1

                # 添加到单元
                unit_words.append({
                    'idx': len(unit_words) + 1,
                    'word': word,
                    'source': source,
                    'pos': pos,
                    'cn': cn,
                    'example': example
                })

                # 每50个词一个单元
                if len(unit_words) >= words_per_unit:
                    all_units.append({'unit': unit_num, 'words': unit_words})
                    unit_num += 1
                    unit_words = []

    # 添加剩余的词
    if unit_words:
        all_units.append({'unit': unit_num, 'words': unit_words})

    return all_units


if __name__ == '__main__':
    units = extract_words()
    total = sum(len(u['words']) for u in units)
    print(f"提取完成：{len(units)}个单元，共{total}个词")

    # 显示每个单元的词数
    for u in units:
        print(f"  单元{u['unit']}: {len(u['words'])}词")

    # 显示前10个词
    print("\n前10个词（单元1）：")
    for w in units[0]['words'][:10]:
        print(f"  {w['idx']}. {w['word']} | {w['source']} | {w['pos']} | {w['cn']} | {w['example']}")

    # 显示最后5个词
    print(f"\n最后5个词（单元{units[-1]['unit']}）：")
    for w in units[-1]['words'][-5:]:
        print(f"  {w['idx']}. {w['word']} | {w['source']} | {w['pos']} | {w['cn']} | {w['example']}")

    # 保存到JSON
    out_path = r"e:\해외에 가다\韩语单词\words_advanced.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(units, f, ensure_ascii=False, indent=2)
    print(f"\n已保存到: {out_path}")
