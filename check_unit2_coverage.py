import json
from collections import Counter

with open(r'e:\해외에 가다\韩语单词\grammar_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('Unit 2 question count:', len(data['units'][1]['questions']))
counts = Counter(q['grammar'] for q in data['units'][1]['questions'])
for g, c in counts.most_common():
    print(f'{c} x {g}')
