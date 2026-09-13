import re, json

with open(r'e:\해외에 가다\韩语单词\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'const GRAMMAR_DATA = (\{.*?\});\s*\n', html, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    for u in data['units']:
        print('Unit', u['unit'], ':', len(u['questions']), 'questions')
else:
    print('GRAMMAR_DATA not found')
