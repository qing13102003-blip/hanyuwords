import re, fitz

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

# 1. 标准编号语法
pattern1 = re.compile(r'^\d+\.\s*[—–-]\s*(.+)$', re.MULTILINE)
std_items = pattern1.findall(text)
print('Standard numbered items:', len(std_items))
for i, item in enumerate(std_items, 1):
    print(f'{i:2d}. {item}')

# 2. 查找可能的未编号语法标题
print('\n\nPotential unnumbered grammar titles:')
lines = text.split('\n')
for i, line in enumerate(lines):
    # 被动态/使动态/特殊变形后的第一个非空行且不是说明/例子
    if line.strip() in ['被动态', '使动态', '特殊变形']:
        # 找下一个编号后面的内容
        j = i + 1
        while j < len(lines) and not re.match(r'^\d+\.\s*[—–-]', lines[j].strip()):
            l = lines[j].strip()
            if l and not l.startswith('①') and not l.startswith('②') and not l.startswith('③') and not l.startswith('•') and not l.startswith('将') and not l.endswith('→'):
                # 可能是标题
                if len(l) < 30 and ('形式' in l or '变形' in l or '不规则' in l):
                    print(f'  After {line}: {l}')
            j += 1
