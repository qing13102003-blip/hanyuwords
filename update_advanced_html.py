# -*- coding: utf-8 -*-
"""把中高级词汇数据嵌入index.html，并更新等级名称"""
import json
import re

# 读取中高级词汇数据
with open(r"e:\해외에 가다\韩语单词\words_advanced.json", "r", encoding="utf-8") as f:
    advanced_data = json.load(f)

# 读取index.html
with open(r"e:\해외에 가다\韩语单词\index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. 更新LEVELS定义：把高级改为中高级，并填入数据
advanced_json = json.dumps(advanced_data, ensure_ascii=False)

# 找到并替换LEVELS数组
old_levels = """const LEVELS = [
  {id:'beginner', name:'初级', kr:'초급', desc:'550个初级核心词汇', units:WORD_DATA},
  {id:'advanced', name:'高级', kr:'고급', desc:'高级词汇', units:[]}
];"""

new_levels = f"""const ADVANCED_DATA = {advanced_json};

const LEVELS = [
  {{id:'beginner', name:'初级', kr:'초급', desc:'550个初级核心词汇', units:WORD_DATA}},
  {{id:'advanced', name:'中高级', kr:'중고급', desc:'1200个中高级词汇', units:ADVANCED_DATA}}
];"""

if old_levels in html:
    html = html.replace(old_levels, new_levels)
    print("✓ LEVELS已更新")
else:
    print("✗ 未找到LEVELS定义，尝试正则匹配")
    pattern = r"const LEVELS = \[.*?\];"
    match = re.search(pattern, html, re.DOTALL)
    if match:
        html = html[:match.start()] + new_levels + html[match.end():]
        print("✓ LEVELS已更新（正则匹配）")
    else:
        print("✗ 匹配失败")

# 保存
with open(r"e:\해외에 가다\韩语单词\index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✓ index.html已保存")

# 验证
total_beginner = sum(len(u['words']) for u in json.loads(re.search(r'const WORD_DATA = (\[.*?\]);', html, re.DOTALL).group(1)))
print(f"初级词汇: {total_beginner}词")
print(f"中高级词汇: {sum(len(u['words']) for u in advanced_data)}词")
