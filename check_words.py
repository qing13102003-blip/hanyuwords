# -*- coding: utf-8 -*-
import json

with open(r"e:\해외에 가다\韩语单词\words.json", "r", encoding="utf-8") as f:
    units = json.load(f)

print(f"总单元数: {len(units)}")
print(f"总单词数: {sum(len(u['words']) for u in units)}")

# 检查每个单元的单词
problems = []
for u in units:
    print(f"\n=== 单元 {u['unit']} ({len(u['words'])} 词) ===")
    for w in u['words']:
        word = w['word']
        cn = w['cn']
        # 检查韩文是否含有非韩文字符
        import re
        hangul = re.compile(r'[\uAC00-\uD7A3]')
        non_kr = re.sub(r'[\uAC00-\uD7A3]', '', word)
        # 检查中文是否含水印字符
        watermark = any(c in cn for c in '韩语老师lx')
        # 检查中文是否为空
        empty_cn = not cn.strip()
        # 检查中文是否过短
        short_cn = len(cn.strip()) > 0 and len(cn.strip()) < 1
        
        flag = ""
        if non_kr.strip():
            flag += f"[韩文异常:{non_kr}]"
        if watermark:
            flag += "[含水印]"
        if empty_cn:
            flag += "[中文为空]"
        
        print(f"  {w['idx']:2d}. {word:12s} - {cn:20s} {flag}")
        
        if flag:
            problems.append((u['unit'], w['idx'], word, cn, flag))

print(f"\n\n=== 问题汇总 ({len(problems)} 个) ===")
for p in problems:
    print(f"  单元{p[0]} #{p[1]}: {p[2]} - {p[3]} {p[4]}")
