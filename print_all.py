# -*- coding: utf-8 -*-
import json

with open(r"e:\해외에 가다\韩语单词\words.json", "r", encoding="utf-8") as f:
    units = json.load(f)

# 打印所有单元的所有单词
for u in units:
    print(f"\n=== 单元 {u['unit']} ({len(u['words'])}词) ===")
    for w in u['words']:
        print(f"  {w['idx']:2d}. {w['word']:12s} - {w['cn']}")
