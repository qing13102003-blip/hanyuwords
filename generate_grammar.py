import re, json, fitz, random

# ============================================================
# 配置：每个 PDF 对应一个语法册（level）
# ============================================================
PDF_CONFIG = [
    {
        'pdf': r'e:\해외에 가다\韩语单词\语法讲解1.pdf',
        'id': 'advanced_grammar_1',
        'name': '中高级语法1',
        'kr': '중고급 문법 1',
        'extra_items': [
            {
                'grammar': '被动态词汇形式（이/히/리/기）',
                'explanation': '在动词后面添加‘이, 히, 리, 기’等构成其被动词。表示因他人的行为或动作而受到影响的意思。例如：보다→보이다, 쌓다→쌓이다, 놓다→놓이다, 바꾸다→바뀌다, 잡다→잡히다, 읽다→읽히다, 먹다→먹히다, 열다→열리다, 듣다→들리다等。'
            },
            {
                'grammar': '使动态词汇形式（이/히/리/기/우/추）',
                'explanation': '在动词或形容词后面添加‘이, 히, 리, 기, 우, 추’等构成其使动词。表示要求或命令他人做某事，从而使人或动物行动起来或达到某种状态。例如：보다→보이다, 높다→높이다, 죽다→죽이다, 앉다→앉히다, 살다→살리다, 알다→알리다, 울다→울리다, 자다→재우다, 서다→세우다, 낮다→낮추다等。'
            },
            {
                'grammar': 'ㅅ的不规则变形',
                'explanation': '当词干以‘ㅅ’作为收音结尾的词，后面遇到以元音开始的连接词时，‘ㅅ’需要脱落。这类词有: 긋다(划)、낫다(痊愈;比…好)、붓다(倒;肿)、잇다(连接)、젓다(摇;摆)、짓다(建造)等。'
            },
            {
                'grammar': '는대요/ㄴ대요/대요',
                'explanation': '间接引语一般陈述句的缩略形式。由는다/ㄴ다/다고해요缩略而来，用于转述从他人那里听来的陈述内容。'
            },
            {
                'grammar': '냬요',
                'explanation': '间接引语一般疑问句的缩略形式。由냐고해요缩略而来，用于转述从他人那里听来的疑问内容。'
            },
            {
                'grammar': '(으)래요/래요',
                'explanation': '间接引语命令句的缩略形式。由(으)라고해요缩略而来，用于转述从他人那里听来的命令或要求内容。'
            },
            {
                'grammar': '재요',
                'explanation': '间接引语共动句的缩略形式。由자고해요缩略而来，用于转述从他人那里听来的共同行动提议。'
            }
        ]
    },
    {
        'pdf': r'e:\해외에 가다\韩语单词\语法讲解2.pdf',
        'id': 'advanced_grammar_2',
        'name': '中高级语法2',
        'kr': '중고급 문법 2',
        'extra_items': []
    },
    {
        'pdf': r'e:\해외에 가다\韩语单词\语法讲解3.pdf',
        'id': 'advanced_grammar_3',
        'name': '中高级语法3',
        'kr': '중고급 문법 3',
        'extra_items': []
    }
]

UNIT_SIZE = 10  # 每单元语法点数

# ============================================================
# PDF 提取
# ============================================================
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        t = page.get_text()
        # 去除页眉页脚
        t = re.sub(r'韩语老师xxxxl?|语老师xxxxl?|老师xxxxl?|韩语老师|语老师|韩\n|中\n|高\n', '', t)
        t = re.sub(r'TOPIK II\s+全程辅导线上班', '', t)
        t = re.sub(r'『中 高 级 语 法 讲 解 \d+』', '', t)
        t = re.sub(r'\d{4}-\d{2}-\d{2}', '', t)
        text += t + '\n'
    text = re.sub(r'\n+', '\n', text).strip()
    return text

def parse_items(text):
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
                # 例句开始标志：• 或 - 后跟非空白内容
                if l.startswith('•'):
                    break
                if re.match(r'^-\s*\S', l):
                    break
                if l and not l.startswith('韩语'):
                    explanation_lines.append(l)
                i += 1
            explanation = ' '.join(explanation_lines).strip()
            explanation = re.sub(r'^[①②③④⑤]\s*', '', explanation)
            items.append({'grammar': grammar, 'explanation': explanation})
        else:
            i += 1
    return items

# ============================================================
# explanation 为空时的兜底说明
# ============================================================
def fallback_explanation(grammar):
    m = re.search(r'[（(]([^)）]+)[)）]', grammar)
    if m:
        note = m.group(1).strip()
        if any(k in note for k in ['间接引语', '陈述', '疑问', '命令', '共动']):
            return f"用于{note}的间接引语形式"
        if any(k in note for k in ['被动', '使动', '不规则']):
            return f"表示{note}"
        return f"表示{note}"
    g = grammar.strip()
    if '이라고' in g and '라고하다' in g:
        return "间接引语中用于名词或名词化谓语后的引用形式，有收音用‘이라고’，无收音用‘라고’"
    if '달라고' in g or '주라고' in g:
        return "间接引语中请求或要求给予某物的表达，说话人为接受人时用‘달라고’，第三者为接受人时用‘주라고’"
    if '다고하다' in g or '다고해요' in g:
        return "间接引语形式，用于转述他人的陈述内容"
    if '냐고하다' in g or '냐고해요' in g:
        return "间接引语形式，用于转述他人的疑问内容"
    if '라고하다' in g or '라고해요' in g:
        return "间接引语形式，用于转述他人的命令或要求内容"
    if '자고하다' in g or '자고해요' in g:
        return "间接引语形式，用于转述他人的共同行动提议"
    return ''

# ============================================================
# 语法形式空格规范化
# ============================================================
GRAMMAR_SPACING_FIXES = [
    ('냐고하다하다', '냐고하다'),
    ('/ -', '/-'),
    ('아/어/여있다', '아/어/여 있다'),
    ('아/어/여버리다', '아/어/여 버리다'),
    ('아/어/여가다', '아/어/여 가다'),
    ('아/어/여오다', '아/어/여 오다'),
    ('아/어/여내다', '아/어/여 내다'),
    ('아/어/여놓다', '아/어/여 놓다'),
    ('아/어/여두다', '아/어/여 두다'),
    ('아/어/여봤자', '아/어/여 봤자'),
    ('게하다', '게 하다'),
    ('도록하다', '도록 하다'),
    ('(으)로인해', '(으)로 인해'),
    ('기위해서', '기 위해서'),
    ('-을/를위해서', '-을/를 위해서'),
    ('아/어/여가지고', '아/어/여 가지고'),
    ('을지도/ㄹ지도모르다', '을지도/ㄹ지도 모르다'),
    ('는줄알다', '는 줄 알다'),
    ('는줄모르다', '는 줄 모르다'),
    ('은/ㄴ줄알다', '은/ㄴ 줄 알다'),
    ('은/ㄴ줄모르다', '은/ㄴ 줄 모르다'),
    ('을/ㄹ줄알다', '을/ㄹ 줄 알다'),
    ('을/ㄹ줄모르다', '을/ㄹ 줄 모르다'),
    ('에도불구하고', '에도 불구하고'),
    ('을/ㄹ뿐만아니라', '을/ㄹ 뿐만 아니라'),
    ('(이)나마찬가지이다', '(이)나 마찬가지이다'),
]

def normalize_grammar_spacing(g):
    for old, new in GRAMMAR_SPACING_FIXES:
        g = g.replace(old, new)
    return g

# ============================================================
# 例句空格修正（兜底：针对所有 PDF 中已知的无空格例句）
# ============================================================
EXAMPLE_SPACING_FIXES = {
    '그렇지않아도': '그렇지 않아도',
    '피곤한데같이커피한잔할까요': '피곤한데 같이 커피 한잔 할까요',
    '저도막지금커피를마시려던참이었어요': '저도 막 지금 커피를 마시려던 참이었어요',
    '이건중요하니까써놓으세요': '이건 중요하니까 써 놓으세요',
    '안그래도쓰려던참이었어요': '안 그래도 쓰려던 참이었어요',
    '시가되자마자모두들퇴근했다': '6시가 되자마자 모두들 퇴근했다',
    '66시가되자마자모두들퇴근했다': '6시가 되자마자 모두들 퇴근했다',
    '66시가 되자마자모두들퇴근했다': '6시가 되자마자 모두들 퇴근했다',
    '66시가 되자마자 모두들 퇴근했다': '6시가 되자마자 모두들 퇴근했다',
    '경치가그림처럼아름다워요': '경치가 그림처럼 아름다워요',
    '저는아버지처럼살고싶어요': '저는 아버지처럼 살고 싶어요',
    '사람마다얼굴이다르듯이생각도다르다': '사람마다 얼굴이 다르듯이 생각도 다르다',
    '지금까지그래왔듯이앞으로도최선을다하자': '지금까지 그래왔듯이 앞으로도 최선을 다하자',
    '그는귀찮은듯이대충대답을했다': '그는 귀찮은 듯이 대충 대답을 했다',
    '그는아무것도안들리는듯이가만히있었다': '그는 아무것도 안 들리는 듯이 가만히 있었다',
    '두사람이싸운듯이눈도안마주쳐요': '두 사람이 싸운 듯이 눈도 안 마주쳐요',
    '비가올듯이날이흐리다': '비가 올 듯이 날이 흐리다',
    '방도어두울때창문조차작아요': '방도 어두울 때 창문조차 작아요',
    '휴가는커녕주말조차쉬지못하고있어요': '휴가는 커녕 주말조차 쉬지 못하고 있어요',
    '내생일을부모님마저잊어버리고계셨다': '내 생일을 부모님마저 잊어버리고 계셨다',
    '사업실패로빚을져서집마저팔아버렸다': '사업 실패로 빚을 져서 집마저 팔아버렸다',
    '보시다시피여기아묵도없습니다': '보시다시피 여기 아묵도 없습니다',
    '아파서쓰러지다시피침대에누웠다': '아파서 쓰러지다시피 침대에 누웠다',
    '시험공부하느라밤을새우다시피했어요': '시험 공부하느라 밤을 새우다시피 했어요',
    '매일친구집에가서같이살다시피한다': '매일 친구 집에 가서 같이 살다시피 한다',
    'ㄹ뿐만아니라': 'ㄹ 뿐만 아니라',
    '나마찬가지다': '나 마찬가지다',
}

def fix_example_spacing(text):
    for old, new in EXAMPLE_SPACING_FIXES.items():
        text = text.replace(old, new)
    return text

# ============================================================
# 从 explanation 提取核心中文含义（作为题目答案和选项）
# ============================================================
def extract_core_meaning(explanation):
    explanation = explanation.strip()
    if not explanation:
        return ''
    # 优先找“表示/用于/是”引导的完整语义说明
    for keyword in ['表示', '用于', '是']:
        idx = explanation.find(keyword)
        if idx != -1:
            end = explanation.find('。', idx)
            if end == -1:
                end = explanation.find('；', idx)
            if end == -1:
                comma = explanation.find('，', idx + 10)
                if comma != -1:
                    end = comma
            if end == -1:
                end = len(explanation)
            return explanation[idx:end].strip()
    return explanation[:40].strip() + ('...' if len(explanation) > 40 else '')

# ============================================================
# 生成选择题（题目=韩文语法，选项=中文含义）
# ============================================================
def make_options(correct, pool):
    others = [x['core'] for x in pool if x['core'] and x['core'] != correct]
    random.shuffle(others)
    wrongs = [o for o in others if o][:3]
    opts = wrongs + [correct]
    random.shuffle(opts)
    return opts

def build_questions(items):
    questions = []
    for it in items:
        grammar = it['grammar']
        core = it['core']
        if not core:
            # 无法提取中文含义时，跳过该语法点（避免无正确答案）
            continue
        questions.append({
            'type': 'meaning',
            'question': f'— {grammar}',
            'options': make_options(core, items),
            'answer': core,
            'grammar': grammar,
            'explanation': it['explanation']
        })
    return questions

# ============================================================
# 主流程
# ============================================================
random.seed(42)
levels = []

for cfg in PDF_CONFIG:
    print(f'\nProcessing {cfg["name"]} ({cfg["pdf"]})...')
    text = extract_text_from_pdf(cfg['pdf'])
    items = parse_items(text)

    # 合并额外语法点
    for extra in cfg.get('extra_items', []):
        items.append({'grammar': extra['grammar'], 'explanation': extra['explanation']})

    # 填充 explanation
    for it in items:
        if not it['explanation'].strip():
            it['explanation'] = fallback_explanation(it['grammar'])

    # 规范化空格
    for it in items:
        it['grammar'] = normalize_grammar_spacing(it['grammar'])
        it['explanation'] = fix_example_spacing(it['explanation'])

    # 计算核心含义
    for it in items:
        it['core'] = extract_core_meaning(it['explanation'])

    # 划分单元
    units = []
    for u in range(0, len(items), UNIT_SIZE):
        unit_items = items[u:u+UNIT_SIZE]
        questions = build_questions(unit_items)
        random.shuffle(questions)
        units.append({
            'unit': u // UNIT_SIZE + 1,
            'questions': questions
        })

    levels.append({
        'id': cfg['id'],
        'name': cfg['name'],
        'kr': cfg['kr'],
        'source': cfg['pdf'].split('\\')[-1],
        'units': units
    })

    total_items = sum(len(u['questions']) for u in units)
    print(f'  Grammar items: {len(items)}')
    print(f'  Valid questions: {total_items}')
    print(f'  Units: {len(units)}')
    for u in units:
        print(f"    Unit {u['unit']}: {len(u['questions'])} questions")

grammar_data = {'levels': levels}

out_path = r'e:\해외에 가다\韩语单词\grammar_data.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(grammar_data, f, ensure_ascii=False, indent=2)

print(f'\nSaved {out_path}')
print(f'Total levels: {len(levels)}')
