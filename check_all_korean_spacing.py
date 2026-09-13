import json, re

with open(r'e:\해외에 가다\韩语单词\grammar_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def extract_korean(text):
    return re.findall(r'[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f][\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\s]*[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]', text)

for field_name in ['grammar', 'question', 'answer', 'explanation']:
    samples = []
    for level in data['levels']:
        for unit in level['units']:
            for q in unit['questions']:
                val = q.get(field_name, '')
                kr_parts = extract_korean(val)
                for part in kr_parts:
                    if len(part) > 5 and ' ' not in part:
                        samples.append((unit['unit'], q['grammar'], part))
    print(f'[{field_name}] {len(samples)} segments without spaces')
    for unit, grammar, part in samples[:10]:
        print(f'  Unit {unit} | {grammar} | {part}')
