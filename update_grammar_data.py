import re, json

html_path = r'e:\해외에 가다\韩语单词\index.html'
grammar_path = r'e:\해외에 가다\韩语单词\grammar_data.json'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

with open(grammar_path, 'r', encoding='utf-8') as f:
    grammar_data = json.load(f)

grammar_json = json.dumps(grammar_data, ensure_ascii=False)

# 替换 const GRAMMAR_DATA = ...; 部分
pattern = re.compile(r'const GRAMMAR_DATA =\s*\{.*?\};\s*\n', re.DOTALL)
new_data = f'const GRAMMAR_DATA = {grammar_json};\n\n'

if pattern.search(html):
    html = pattern.sub(new_data, html)
    print('Updated GRAMMAR_DATA in index.html')
else:
    print('WARN: GRAMMAR_DATA not found')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
