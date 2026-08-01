# -*- coding: utf-8 -*-
import json
import re

with open(r"e:\해외에 가다\韩语单词\words.json", "r", encoding="utf-8") as f:
    units = json.load(f)

# 检查所有可能有问题的单词
# 1. 中文释义含"韩/语/老/师"（可能是水印残留）
# 2. 中文释义看起来不完整
# 3. 中文释义有多余字符
print("=== 可疑单词 ===")
for u in units:
    for w in u['words']:
        cn = w['cn']
        word = w['word']
        issues = []
        # 检查含水印字符
        for c in '韩语老师':
            if c in cn:
                issues.append(f"含水印字'{c}'")
        # 检查释义可能不完整（以分号开头或结尾，或只有一个字）
        if cn.startswith(';') or cn.endswith(';'):
            issues.append("分号位置异常")
        if len(cn) == 1 and cn in '韩语老师':
            issues.append("单字且为水印字")
        # 检查释义是否有重复片段
        # 检查以括号开头（可能缺少前面的字）
        if cn.startswith('('):
            issues.append("以括号开头(可能缺字)")
        if cn.startswith(';'):
            issues.append("以分号开头")
        if issues:
            print(f"  单元{u['unit']} #{w['idx']}: {word} - '{cn}' -> {issues}")

# 另外检查一些已知的可疑释义
print("\n=== 需要人工核对的单词（释义可能有误）===")
suspicious = []
for u in units:
    for w in u['words']:
        cn = w['cn']
        # 释义超过8个字的
        if len(cn) > 8:
            suspicious.append((u['unit'], w['idx'], w['word'], cn, "释义过长"))
        # 释义只有一个字的
        elif len(cn) == 1:
            suspicious.append((u['unit'], w['idx'], w['word'], cn, "释义单字"))
        # 释义含"韩/语/老/师"但不在已知修复列表中
        elif any(c in cn for c in '韩语老师'):
            suspicious.append((u['unit'], w['idx'], w['word'], cn, "含水印字"))

for s in suspicious:
    print(f"  单元{s[0]} #{s[1]}: {s[2]} - '{s[3]}' ({s[4]})")
