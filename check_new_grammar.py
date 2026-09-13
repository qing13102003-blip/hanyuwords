import json
with open(r'e:\해외에 가다\韩语单词\grammar_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
new_grammars = ['被动态词汇形式', '使动态词汇形式', 'ㅅ的不规则变形', '는대요', '냬요', '(으)래요', '재요']
found = set()
for u in data['units']:
    for q in u['questions']:
        for g in new_grammars:
            if g in q['grammar']:
                found.add(q['grammar'])
                print('Unit', u['unit'], ':', q['grammar'])
                break
print('\nTotal new grammars found:', len(found))
