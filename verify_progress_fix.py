# -*- coding: utf-8 -*-
"""进度系统重构的端到端验证。服务器：python -m http.server 8899"""
import sys, time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BASE = 'http://127.0.0.1:8899/index.html'
KEY  = 'kr_vocab_progress_v1'
BKEY = 'kr_vocab_progress_v1_backup'

fails, errs = [], []
def chk(name, cond, detail=''):
    print(('  OK   ' if cond else '  FAIL ') + name + (('  <- ' + str(detail)) if detail else ''))
    if not cond: fails.append(name)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1400, 'height': 950})
    pg.set_default_timeout(45000)
    pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
    pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' and 'ERR_CONNECTION' not in m.text else None)

    def fresh(seed=None):
        pg.goto(BASE + '?t=' + str(int(time.time() * 1000)), wait_until='domcontentloaded')
        if seed is None:
            pg.evaluate('() => localStorage.clear()')
        else:
            pg.evaluate('([k, s]) => { localStorage.clear(); localStorage.setItem(k, JSON.stringify(s)); }', [KEY, seed])
        pg.reload(wait_until='domcontentloaded')
        pg.wait_for_timeout(700)

    def st():
        return pg.evaluate('([k]) => JSON.parse(localStorage.getItem(k) || "{}")', [KEY])

    # ==================== 1. 键碰撞 ====================
    print('\n[1] 进度键跨等级碰撞（基线：1750 词 → 1618 键）')
    fresh()
    r = pg.evaluate('''() => {
      const keys = new Set(); let total = 0;
      LEVELS.forEach(l => l.units.forEach(u => u.words.forEach(w => {
        total++; keys.add(window.__app.wordKey(l.id, u.unit, w.idx));
      })));
      return {total, unique: keys.size};
    }''')
    chk(f'1750 个词产出唯一键数 == 词数', r['unique'] == r['total'], f'{r["total"]} 词 → {r["unique"]} 键')
    fresh()
    pg.evaluate('''() => {
      LEVELS.forEach(l => l.units.forEach(u => u.words.forEach(w => markLearned(l.id, u.unit, w.idx))));
    }''')
    s = st()
    chk('落盘后 learned 键数 == 1750', len(s['learned']) == 1750, len(s['learned']))
    chk('含 beginner:1_5（初级 방학）', 'beginner:1_5' in s['learned'])
    chk('含 advanced:1_5（中高级 베개）', 'advanced:1_5' in s['learned'])
    chk('无旧格式残留键', not [k for k in s['learned'] if ':' not in k])

    # ==================== 2. 「全部」模式记账 ====================
    print('\n[2] 「全部」模式下答题记到哪个单元')
    fresh()
    pg.click('.nav-link[data-nav="list"]'); pg.wait_for_timeout(400)
    pg.click('#listUnitSelector .unit-pill:has-text("全部")'); pg.wait_for_timeout(400)
    chk('currentUnit == 0（全部）', pg.evaluate('window.__app.currentUnit') == 0)
    pg.click('.nav-link[data-nav="quiz"]'); pg.wait_for_timeout(600)
    seen, bad = set(), []
    for _ in range(6):
        info = pg.evaluate('''() => {
          const qs = window.__app.quizState, w = qs.words[qs.current];
          return {word: w.word, unit: w.unit, level: w.level,
                  key: w.level + ':' + w.unit + '_' + w.idx};
        }''')
        pg.evaluate('(w) => { [...document.querySelectorAll("#optionsGrid .option-btn")].find(b => b.dataset.word === w).click(); }', info['word'])
        pg.wait_for_timeout(150)
        if info['key'] not in st()['learned']: bad.append(info)
        seen.add(info['unit'])
        pg.click('#nextBtn'); pg.wait_for_timeout(200)
    chk('成绩写进了题目自身的单元', not bad, bad[:2])
    chk('涉及多于 1 个单元（旧代码恒为 {1}）', len(seen) > 1, f'单元集合={sorted(seen)}')

    # ==================== 3. 等级持久化 + 越界兜底 ====================
    print('\n[3] 等级持久化 / 越界兜底')
    fresh()
    pg.click('.nav-link[data-nav="quiz"]'); pg.wait_for_timeout(500)
    pg.click('#quizLevelTabs .level-tab:has-text("中高级")'); pg.wait_for_timeout(500)
    pg.click('#quizUnitSelector .unit-pill:has-text("第50单元")'); pg.wait_for_timeout(500)
    chk('切到中高级第50单元', pg.evaluate('window.__app.currentLevel') == 'advanced' and pg.evaluate('window.__app.currentUnit') == 50)
    pg.reload(wait_until='domcontentloaded'); pg.wait_for_timeout(800)
    chk('刷新后等级仍是 advanced', pg.evaluate('window.__app.currentLevel') == 'advanced')
    chk('刷新后单元仍是 50', pg.evaluate('window.__app.currentUnit') == 50)
    pg.click('.nav-link[data-nav="quiz"]'); pg.wait_for_timeout(600)   # 刷新后停在首页，需先进入视图才会渲染选择器
    hl = pg.evaluate('''() => { const e=document.querySelector('#quizUnitSelector .unit-pill.active'); return e ? e.textContent.trim() : null; }''')
    chk('单元选择器有高亮且指向第50单元', hl == '第50单元', hl)
    pg.click('.nav-link[data-nav="flash"]'); pg.wait_for_timeout(600)
    pg.click('.mark-btn[title="标记掌握"]'); pg.wait_for_timeout(400)
    s = st()
    chk('掌握记录落在 advanced:50_*', any(k.startswith('advanced:50_') for k in s['mastered']))
    chk('没有污染 beginner:50_*', not any(k.startswith('beginner:50_') for k in s['mastered']))

    # 越界兜底
    fresh({'schemaVersion': 2, 'level': 'advanced', 'lastUnitByLevel': {'advanced': 999}, 'learned': {}, 'mastered': {}})
    chk('越界单元收敛到本等级第 1 单元（不是初级）',
        pg.evaluate('window.__app.currentLevel') == 'advanced' and pg.evaluate('window.__app.currentUnit') == 1,
        f'{pg.evaluate("window.__app.currentLevel")}:{pg.evaluate("window.__app.currentUnit")}')

    # ==================== 4. 旧数据迁移 ====================
    print('\n[4] v1 → v2 迁移')
    fresh({'learned': {'20_3': True}, 'mastered': {}, 'lastUnit': 50})
    s = st()
    chk('unit=20 (>11) 判给中高级', s['learned'].get('advanced:20_3') is True, list(s['learned'])[:3])
    chk('lastUnit=50 把等级恢复成 advanced', pg.evaluate('window.__app.currentLevel') == 'advanced')
    chk('迁移前原始数据已备份', pg.evaluate('([k]) => !!localStorage.getItem(k)', [BKEY]))
    fresh({'learned': {'1_5': True}, 'mastered': {}, 'lastUnit': 3})
    s = st()
    chk('unit<=11 有歧义，归初级', s['learned'].get('beginner:1_5') is True, list(s['learned'])[:3])
    chk('未误判为中高级', 'advanced:1_5' not in s['learned'])
    fresh({'learned': {'1_5': True}, 'mastered': {'2_4': True}, 'lastUnit': 1})
    s = st()
    chk('mastered ⊆ learned 不变式成立', s['learned'].get('beginner:2_4') is True)

    # ==================== 5. 统计口径 ====================
    print('\n[5] 进度页统计口径')
    seed = {'schemaVersion': 2, 'level': 'beginner', 'lastUnitByLevel': {'beginner': 1}, 'mastered': {},
            'learned': {**{f'beginner:1_{i}': True for i in range(1, 4)},
                        **{f'advanced:1_{i}': True for i in range(1, 8)}}}
    fresh(seed)
    pg.click('.nav-link[data-nav="stats"]'); pg.wait_for_timeout(600)
    v = pg.eval_on_selector('#statsContent .stat-card-value', 'e => e.textContent.trim()')
    chk('初级页只统计初级（3）', v == '3', v)
    chk('副标题标明等级', '初级共550词' in pg.inner_text('#statsContent'))
    pg.click('#statsLevelTabs .level-tab:has-text("中高级")'); pg.wait_for_timeout(500)
    v2 = pg.eval_on_selector('#statsContent .stat-card-value', 'e => e.textContent.trim()')
    chk('中高级页只统计中高级（7）', v2 == '7', v2)
    chk('副标题标明等级', '中高级共1200词' in pg.inner_text('#statsContent'))
    # 分子不会超过分母，且各行之和 == 顶部数字
    # 注意：单元行展示的是「已掌握」数，因此与「已掌握」卡片比对
    pg.click('#statsLevelTabs .level-tab:has-text("初级")'); pg.wait_for_timeout(400)
    pg.evaluate('''() => { LEVELS.find(l => l.id === 'beginner').units
        .forEach(u => u.words.forEach(w => markMastered('beginner', u.unit, w.idx))); }''')
    pg.evaluate('() => renderStats()'); pg.wait_for_timeout(500)
    cards = pg.eval_on_selector_all('#statsContent .stat-card-value', 'els => els.map(e => e.textContent.trim())')
    sub = pg.inner_text('#statsContent')
    chk('初级学满：已学习 550', cards[0] == '550', cards)
    chk('初级学满：已掌握 550', cards[1] == '550', cards)
    chk('百分比 100% 且不超 100', '100%' in sub and '101%' not in sub)
    nums = pg.eval_on_selector_all('.unit-progress-row-num', 'els => els.map(e => e.textContent.split("/")[0])')
    chk('各单元已掌握之和 == 已掌握卡片', sum(int(n) for n in nums) == 550, sum(int(n) for n in nums))

    # ==================== 6. 搜索 ====================
    print('\n[6] 单词库搜索范围')
    fresh()
    pg.click('.nav-link[data-nav="list"]'); pg.wait_for_timeout(500)
    chk('默认停在第1单元', '第1单元' in pg.inner_text('#listUnitSelector .unit-pill.active'))
    w6 = pg.evaluate('() => WORD_DATA[5].words[0].word')          # 第6单元的词
    pg.fill('#searchInput', w6); pg.wait_for_timeout(600)
    n = pg.locator('.word-item').count()
    chk(f'第1单元下能搜到第6单元的词「{w6}」', n >= 1, f'{n} 条')
    chk('显示搜索范围提示', '全部等级' in pg.inner_text('#wordList'))
    wA = pg.evaluate('() => ADVANCED_DATA[0].words[0].word')      # 中高级的词
    pg.fill('#searchInput', wA); pg.wait_for_timeout(600)
    chk(f'跨等级能搜到中高级词「{wA}」', pg.locator('.word-item').count() >= 1)
    chk('结果带等级徽标', '中高级' in pg.inner_text('.word-badge'))

    # ==================== 7. 移动端 ====================
    print('\n[7] 移动端布局')
    pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(600)
    box = pg.eval_on_selector('.brand-mark', 'e => { const r = e.getBoundingClientRect(); return {w: r.width, h: r.height}; }')
    # 单行渲染时高度约等于一个行高（~32px）；被挤成竖排三字会是 ~96px
    chk(f'品牌单行横排（宽 {box["w"]:.0f}×高 {box["h"]:.0f}）', box['w'] > box['h'] and box['h'] < 40, box)
    chk('white-space:nowrap', pg.eval_on_selector('.brand-mark', 'e => getComputedStyle(e).whiteSpace') == 'nowrap')
    chk('无横向溢出', pg.evaluate('() => document.documentElement.scrollWidth <= 390'))
    pg.screenshot(path='_shot_mobile.png')
    pg.set_viewport_size({'width': 1280, 'height': 900}); pg.wait_for_timeout(500)
    chk('桌面端 brand-sub 仍显示', pg.eval_on_selector('.brand-sub', 'e => getComputedStyle(e).display') != 'none')

    # ==================== 8. 语法选项去重 ====================
    print('\n[8] 语法选项去重')
    fresh()
    pg.click('.nav-link[data-nav="grammar"]'); pg.wait_for_timeout(600)
    pg.click('#grammarLevelTabs .level-tab:has-text("中高级语法2")'); pg.wait_for_timeout(500)
    pg.click('#grammarUnitSelector .unit-chip:has-text("第 4 单元")'); pg.wait_for_timeout(600)
    bad, checked = [], 0
    for _ in range(40):
        if pg.locator('.quiz-result').count(): break
        opts = pg.evaluate('''() => [...document.querySelectorAll("#grammarOptions .option-btn")]
            .map(e => ({opt: e.dataset.opt, ans: e.dataset.answer}))''')
        labels = [o['opt'] for o in opts]
        checked += 1
        if len(labels) != len(set(labels)): bad.append(('重复', labels))
        if not any(o['opt'] == o['ans'] for o in opts): bad.append(('答案缺失', labels))
        pg.evaluate('() => document.querySelector("#grammarOptions .option-btn").click()'); pg.wait_for_timeout(80)
        pg.click('#grammarNextBtn'); pg.wait_for_timeout(120)
    chk(f'检查了 {checked} 题，无重复选项且正确项始终存在', not bad, bad[:2])
    src_dup = pg.evaluate('''() => { let n = 0; GRAMMAR_DATA.levels.forEach(l => l.units.forEach(u => u.questions.forEach(q => {
        if(new Set(q.options).size !== q.options.length) n++; }))); return n; }''')
    print(f'  （数据源仍有 {src_dup} 处重复，由渲染层去重兜住，符合预期）')

    # ==================== 9. 端到端冒烟 ====================
    print('\n[9] 端到端冒烟')
    fresh()
    nums = pg.eval_on_selector_all('.hero-stats .stat-num', 'els => els.map(e => e.textContent.trim())')
    chk('首页四个数字为 1750/0/0/—', nums == ['1750', '0', '0', '—'], nums)
    pg.evaluate('() => selectUnitForLearn(37, "advanced")'); pg.wait_for_timeout(700)
    chk('落到中高级第37单元', pg.evaluate('window.__app.currentUnit') == 37 and pg.evaluate('window.__app.currentLevel') == 'advanced')
    for _ in range(3):
        w = pg.evaluate('''() => { const qs = window.__app.quizState; return qs.words[qs.current].word; }''')
        pg.evaluate('(x) => { [...document.querySelectorAll("#optionsGrid .option-btn")].find(b => b.dataset.word === x).click(); }', w)
        pg.wait_for_timeout(150)
        pg.click('#nextBtn'); pg.wait_for_timeout(250)
    pg.click('.nav-link[data-nav="stats"]'); pg.wait_for_timeout(600)
    v = pg.eval_on_selector('#statsContent .stat-card-value', 'e => e.textContent.trim()')
    chk('进度页显示 3', v == '3', v)
    pg.reload(wait_until='domcontentloaded'); pg.wait_for_timeout(800)
    chk('刷新后仍在第37单元', pg.evaluate('window.__app.currentUnit') == 37)
    pg.click('.nav-link[data-nav="stats"]'); pg.wait_for_timeout(600)
    pg.click('#statsLevelTabs .level-tab:has-text("初级")'); pg.wait_for_timeout(500)
    v0 = pg.eval_on_selector('#statsContent .stat-card-value', 'e => e.textContent.trim()')
    chk('切初级后显示 0（等级间不串）', v0 == '0', v0)
    # 各视图走一遍
    for nav in ['home', 'list', 'quiz', 'flash', 'write', 'idiom', 'exam', 'stats', 'grammar']:
        pg.click(f'.nav-link[data-nav="{nav}"]'); pg.wait_for_timeout(350)
    chk('9 个视图全程无 JS 报错', not errs, errs[:3])

    b.close()

print('\n' + '=' * 60)
print(f'失败 {len(fails)} 项' + ('：' + '、'.join(fails) if fails else ' —— 全部通过 ✅'))
if errs:
    print('运行时错误：')
    for e in errs[:8]: print('  ' + e)
