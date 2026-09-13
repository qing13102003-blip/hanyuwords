import json, random

IDIOMS = [
    {"word": "입맛에 맞다", "meaning": "对口味、合胃口"},
    {"word": "가슴을 울리다", "meaning": "扣人心弦；震动"},
    {"word": "발목을 잡다", "meaning": "抓住脚踝；喻指抓把柄、拉后腿"},
    {"word": "손을 맞잡다", "meaning": "携手，联手"},
    {"word": "등 떠밀다", "meaning": "用力推背；喻指赶鸭子上架"},
    {"word": "눈을 맞추다", "meaning": "对视"},
    {"word": "발 벗고 나서다", "meaning": "全力以赴"},
    {"word": "손에 땀을 쥐다", "meaning": "手里捏着一把汗"},
    {"word": "그림의 떡", "meaning": "画里的年糕；喻指可望而不可即、画饼充饥"},
    {"word": "새 발의 피", "meaning": "鸟脚的血；喻指微不足道"},
    {"word": "우물 안 개구리", "meaning": "井底之蛙，喻指见识短浅"},
    {"word": "티끌 모아 태산", "meaning": "积尘堆成泰山，喻指积少成多"},
    {"word": "앞뒤를 재다", "meaning": "瞻前顾后、左思右想"},
    {"word": "진땀을 흘리다", "meaning": "满头大汗"},
    {"word": "귀를 기울이다", "meaning": "倾听"},
    {"word": "입을 막다", "meaning": "堵嘴，封口"},
    {"word": "눈감아 주다", "meaning": "睁一只眼闭一只眼；视而不见"},
    {"word": "귓등으로 듣다", "meaning": "用耳背来听；喻指当耳旁风"},
    {"word": "손을 떼다", "meaning": "抽手、停手"},
    {"word": "이를 가다", "meaning": "咬牙切齿"},
    {"word": "담을 쌓다", "meaning": "筑起围墙；喻指漠不关心"},
    {"word": "열을 올리다", "meaning": "发怒；热衷"},
    {"word": "꿩 먹고 알 먹다", "meaning": "又吃野鸡又吃蛋；一箭双雕"},
    {"word": "병 주고 약 주다", "meaning": "打一个巴掌给一个甜枣"},
    {"word": "하나를 듣고 열을 알다", "meaning": "闻一知十；举一反三"},
    {"word": "남의 떡이 더 커 보이다", "meaning": "别人的饼看着更大；这山望着那山高"},
    {"word": "콧대가 높다", "meaning": "鼻梁高；喻指傲慢"},
    {"word": "귀에 못이 박히다", "meaning": "耳朵里听出茧子"},
    {"word": "허리띠를 졸라매다", "meaning": "勒紧裤腰带"},
    {"word": "발을 빼다", "meaning": "抽身，脱身，退出，摆脱"},
    {"word": "발걸음을 맞추다", "meaning": "对齐脚步"},
    {"word": "앞뒤를 가리다", "meaning": "瞻前顾后、权衡利弊"},
    {"word": "물 샐 틈 없다", "meaning": "滴水不漏；水泄不通"},
    {"word": "귀가 아프다", "meaning": "耳朵疼；耳朵里听出茧子"},
    {"word": "날개 돋치다", "meaning": "长了翅膀；喻指畅销、卖得好"},
    {"word": "손이 발이 되다", "meaning": "腿作为了脚（苦苦哀求）"},
    {"word": "못을 박다", "meaning": "钉钉子；喻指伤人心"},
    {"word": "머리를 맞대다", "meaning": "碰头、面对面"},
    {"word": "고개를 숙이다", "meaning": "低头致敬、低头认输"},
    {"word": "한눈에 보이다", "meaning": "一览无余，尽收眼底"},
    {"word": "입이 벌어지다", "meaning": "（由于惊愕）张大嘴"},
    {"word": "제 눈에 안경", "meaning": "情人眼里出西施"},
    {"word": "엎질러진 물", "meaning": "覆水难收"},
    {"word": "싼 게 비지떡", "meaning": "便宜没好货"},
    {"word": "입 밖에 내다", "meaning": "脱口而出"},
    {"word": "눈 감아 주다", "meaning": "视而不见；装作没看见"},
    {"word": "한 술 더 뜨다", "meaning": "再吃一口；[喻]变本加厉"},
    {"word": "귓등으로 듣다", "meaning": "听而不闻，当耳旁风"},
    {"word": "하나를 보면 열을 알다", "meaning": "闻一知十"},
    {"word": "천 리 길도 한 걸음부터", "meaning": "千里之行，始于足下"},
    {"word": "소 잃고 외양간 고치다", "meaning": "亡羊补牢"},
    {"word": "윗물이 맑아야 아랫물이 맑다", "meaning": "上梁不正下梁歪"},
]

# 去重（按 word）
seen = {}
for item in IDIOMS:
    seen[item['word']] = item['meaning']
IDIOMS = [{'word': k, 'meaning': v} for k, v in seen.items()]

# 每单元 10 条
UNIT_SIZE = 10
units = []
for i in range(0, len(IDIOMS), UNIT_SIZE):
    chunk = IDIOMS[i:i+UNIT_SIZE]
    questions = []
    for item in chunk:
        others = [x['meaning'] for x in IDIOMS if x['meaning'] != item['meaning']]
        random.shuffle(others)
        options = others[:3] + [item['meaning']]
        random.shuffle(options)
        questions.append({
            'word': item['word'],
            'meaning': item['meaning'],
            'options': options,
            'answer': item['meaning']
        })
    units.append({'unit': i//UNIT_SIZE + 1, 'questions': questions})

data = {'units': units}

with open(r'e:\해외에 가다\韩语单词\idiom_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Total idioms: {len(IDIOMS)}')
print(f'Units: {len(units)}')
for u in units:
    print(f'  Unit {u["unit"]}: {len(u["questions"])} questions')
