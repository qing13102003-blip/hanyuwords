# -*- coding: utf-8 -*-
import json

with open(r"e:\해외에 가다\韩语单词\words.json", "r", encoding="utf-8") as f:
    words = json.load(f)

# 读取原始HTML模板（需要从备份恢复，因为之前的index.html已被注入数据）
# 由于index.html已被注入，我们需要读取它并替换数据部分
with open(r"e:\해외에 가다\韩语单词\index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 找到并替换 WORD_DATA 的赋值
import re
# 匹配 const WORD_DATA = [...]; 的模式
pattern = r'const WORD_DATA = \[.*?\];'
words_json = json.dumps(words, ensure_ascii=False)
replacement = f'const WORD_DATA = {words_json};'
html_new = re.sub(pattern, replacement, html, count=1, flags=re.DOTALL)

if html_new == html:
    print("WARNING: No replacement made!")
else:
    with open(r"e:\해외에 가다\韩语单词\index.html", "w", encoding="utf-8") as f:
        f.write(html_new)
    print(f"Updated HTML with {sum(len(u['words']) for u in words)} words")
    print(f"HTML size: {len(html_new)} chars")
