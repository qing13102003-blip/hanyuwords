import json, re, fitz

pdf_path = r'e:\해외에 가다\韩语单词\语法讲解1.pdf'
doc = fitz.open(pdf_path)
text = ''
for page in doc:
    t = page.get_text()
    t = re.sub(r'韩语老师xxxxl?|语老师xxxxl?|老师xxxxl?|韩语老师|语老师|韩\n|中\n|高\n', '', t)
    text += t + '\n'
text = re.sub(r'TOPIK II\s+全程辅导线上班', '', text)
text = re.sub(r'『中 高 级 语 法 讲 解 1 』', '', text)
text = re.sub(r'\d{4}-\d{2}-\d{2}', '', text)
text = re.sub(r'\n+', '\n', text).strip()

items = []
lines = text.split('\n')
i = 0
while i < len(lines):
    line = lines[i].strip()
    m = re.match(r'^\d+\.\s*[—–-]\s*(.+)$', line)
    if m:
        grammar = m.group(1).strip()
        explanation_lines = []
        i += 1
        while i < len(lines):
            l = lines[i].strip()
            if re.match(r'^\d+\.\s*[—–-]', l):
                break
            if l.startswith('•'):
                break
            if l and not l.startswith('韩语'):
                explanation_lines.append(l)
            i += 1
        explanation = ' '.join(explanation_lines).strip()
        explanation = re.sub(r'^[①②③④⑤]\s*', '', explanation)
        items.append({'grammar': grammar, 'explanation': explanation})
    else:
        i += 1

extra_items = [
    {'grammar': '被动态词汇形式（이/히/리/기）', 'explanation': '在动词后面添加‘이, 히, 리, 기’等构成其被动词。表示因他人的行为或动作而受到影响的意思。'},
    {'grammar': '使动态词汇形式（이/히/리/기/우/추）', 'explanation': '在动词或形容词后面添加‘이, 히, 리, 기, 우, 추’等构成其使动词。表示要求或命令他人做某事，从而使人或动物行动起来或达到某种状态。'},
    {'grammar': 'ㅅ的不规则变形', 'explanation': '当词干以‘ㅅ’作为收音结尾的词，后面遇到以元音开始的连接词时，‘ㅅ’需要脱落。'},
    {'grammar': '는대요/ㄴ�요/대요', 'explanation': '间接引语一般陈述句的缩略形式。'},
    {'grammar': '냬요', 'explanation': '间接引语一般疑问句的缩略形式。'},
    {'grammar': '(으)래요/래요', 'explanation': '间接引语命令句的缩略形式。'},
    {'grammar': '재요', 'explanation': '间接引语共动句的缩略形式。'}
]
items.extend(extra_items)

unit_size = 10
for unit_idx in [2, 3]:
    start = (unit_idx - 1) * unit_size
    end = start + unit_size
    print('\n=== Unit ' + str(unit_idx) + ' (items ' + str(start+1) + '-' + str(end) + ') ===')
    for idx in range(start, min(end, len(items))):
        it = items[idx]
        has_core = bool(it['explanation'].strip())
        print(str(idx+1) + '. ' + it['grammar'])
        print('   explanation: ' + (it['explanation'][:60] if it['explanation'] else '(empty)'))
        print('   has meaning question: ' + str(has_core))
