import json, re

with open(r'e:\해외에 가다\韩语单词\grammar_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 常见助词：应该前面有空格
particles = ['은', '는', '이', '가', '을', '를', '의', '에', '에게', '께', '에서', '으로', '로', '부터', '까지', '하고', '와', '과', '처럼', '보다', '아니라고', '이라고', '라고']
# 常见连接词尾：应该前面无空格（连写）
suffixes = ['아', '어', '여', '고', '지만', '으면', '면', '으니', '니', '아서', '어서', '여서', '는데', '은데', 'ㄴ', '는', '던', '을', 'ㄹ', '기', '게', '도록', '나', '이나', '든', '든지', '려면', '려다', '자마자', '대로', '줄', '밖에', '며', '고요']
# 依存名词：前面应该有空格
dependent_nouns = ['것', '수', '때', '곳', '분', '사람', '이유', '방법', '정도']

def find_korean(text):
    """找出文本中韩文片段"""
    return re.findall(r'[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f][\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\s/\-()]*[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]', text)

def check_spacing(text, context):
    issues = []
    # 检查助词前是否有空格（简单规则：助词前面如果是韩文字母，则应该有空格）
    for p in particles:
        # 找 "한글+助词" 无空格的情况
        pattern = re.compile(r'([\uac00-\ud7af])' + re.escape(p) + r'(?![\uac00-\ud7af])')
        for m in pattern.finditer(text):
            # 排除一些常见的非助词情况
            issues.append(f"助词'{p}'前可能缺少空格: ...{text[max(0,m.start()-3):m.end()+3]}...")
    # 检查连接词尾前是否有空格（简单规则：连接词尾前如果有空格，可能是错误的）
    # 这个规则太严格，暂不检查
    return issues

print('=== 检查所有语法条目中的韩文空格问题 ===\n')

all_issues = []
for level in data.get('levels', []):
    for unit in level.get('units', []):
        for q in unit.get('questions', []):
            # 检查 grammar 字段
            for field in ['grammar', 'question', 'answer', 'explanation']:
                val = q.get(field, '')
                if not val:
                    continue
                issues = check_spacing(val, f"Unit {unit['unit']} Q: {q.get('grammar','')[:20]}")
                for issue in issues:
                    all_issues.append(f"[{field}] {issue}")

if all_issues:
    print(f'发现 {len(all_issues)} 处可能的空格问题：\n')
    for issue in all_issues[:100]:
        print(issue)
    if len(all_issues) > 100:
        print(f'... 还有 {len(all_issues)-100} 处未显示')
else:
    print('未发现明显的空格问题。')
