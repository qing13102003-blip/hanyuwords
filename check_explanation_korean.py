import json, re

with open(r'e:\해외에 가다\韩语单词\grammar_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def extract_korean(text):
    # 提取连续的韩文片段（可能包含空格）
    return re.findall(r'[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f][\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\s]*[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]', text)

samples = []
for level in data['levels']:
    for unit in level['units']:
        for q in unit['questions']:
            e = q.get('explanation', '')
            kr_parts = extract_korean(e)
            for part in kr_parts:
                if len(part) > 5 and ' ' not in part:
                    samples.append((unit['unit'], q['grammar'], part))

print(f'Found {len(samples)} Korean segments without spaces in explanations:')
for unit, grammar, part in samples[:30]:
    print(f'Unit {unit} | {grammar} | {part}')
