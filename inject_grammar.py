import re, json

html_path = r'e:\해외에 가다\韩语单词\index.html'
grammar_path = r'e:\해외에 가다\韩语单词\grammar_data.json'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

with open(grammar_path, 'r', encoding='utf-8') as f:
    grammar_data = json.load(f)

grammar_json = json.dumps(grammar_data, ensure_ascii=False)

# 1. 导航栏添加"语法"按钮
old_nav = '''<button class="nav-link" data-nav="stats" onclick="go('stats')">进度</button>
    </div>'''
new_nav = '''<button class="nav-link" data-nav="stats" onclick="go('stats')">进度</button>
      <button class="nav-link" data-nav="grammar" onclick="go('grammar')">语法</button>
    </div>'''
if old_nav in html:
    html = html.replace(old_nav, new_nav)
    print('Added grammar nav button')
else:
    print('WARN: nav pattern not found')

# 2. 在 STATS VIEW 后添加 GRAMMAR VIEW
old_stats_end = '''  </section>
</div>

<div class="toast" id="toast"></div>'''
new_views = '''  </section>

  <!-- GRAMMAR VIEW -->
  <section class="view" id="view-grammar">
    <div class="page-head">
      <div>
        <button class="back-btn" onclick="go('home')">← 返回首页</button>
        <h1 class="page-title" style="margin-top:12px">语法选择 <span class="kr" style="color:var(--coral)">문법</span></h1>
      </div>
    </div>
    <div class="level-tabs" id="grammarLevelTabs"></div>
    <div class="unit-selector" id="grammarUnitSelector"></div>
    <div id="grammarContent"></div>
  </section>
</div>

<div class="toast" id="toast"></div>'''
if old_stats_end in html:
    html = html.replace(old_stats_end, new_views)
    print('Added grammar view HTML')
else:
    print('WARN: stats end pattern not found')

# 3. 注入 GRAMMAR_DATA 常量
old_levels = '''const LEVELS = ['''
new_levels = f'''// ===== GRAMMAR DATA =====
const GRAMMAR_DATA = {grammar_json};

const LEVELS = ['''
if old_levels in html:
    html = html.replace(old_levels, new_levels, 1)
    print('Injected GRAMMAR_DATA constant')
else:
    print('WARN: LEVELS pattern not found')

# 4. 更新 go() 函数以支持 grammar 视图
# 找到 switch(currentView) 或类似的 render 调用
# 我们在 renderGrammar 函数中处理，但 go() 需要清空/渲染
# 先找到 renderStats 调用位置，在其后添加 renderGrammar
old_render_dispatch = '''else if(currentView === 'stats') renderStats();'''
new_render_dispatch = '''else if(currentView === 'stats') renderStats();
  else if(currentView === 'grammar') renderGrammar();'''
if old_render_dispatch in html:
    html = html.replace(old_render_dispatch, new_render_dispatch)
    print('Updated view dispatch for grammar')
else:
    print('WARN: render dispatch pattern not found')

# 5. 在脚本末尾添加语法模式 JS 函数
grammar_js = r'''

// ===== GRAMMAR QUIZ =====
let grammarState = null;
let currentGrammarUnit = 1;

function getGrammarUnits(){
  return GRAMMAR_DATA.units || [];
}

function renderGrammar(){
  renderLevelTabs('grammarLevelTabs');
  const us = document.getElementById('grammarUnitSelector');
  const units = getGrammarUnits();
  if(units.length === 0){
    us.innerHTML = '<div style="color:var(--ink-soft)">暂无语法单元</div>';
    document.getElementById('grammarContent').innerHTML = '';
    return;
  }
  us.innerHTML = units.map(u => {
    const active = u.unit === currentGrammarUnit ? 'active' : '';
    return `<button class="unit-chip ${active}" onclick="selectGrammarUnit(${u.unit})">第 ${u.unit} 单元</button>`;
  }).join('');
  renderGrammarQuestions();
}

function selectGrammarUnit(unit){
  currentGrammarUnit = unit;
  grammarState = null;
  renderGrammar();
}

function renderGrammarQuestions(){
  const container = document.getElementById('grammarContent');
  const unit = getGrammarUnits().find(u => u.unit === currentGrammarUnit);
  if(!unit || !unit.questions || unit.questions.length === 0){
    container.innerHTML = '<div style="text-align:center;padding:48px;color:var(--ink-soft)">该单元暂无题目</div>';
    return;
  }

  if(!grammarState || grammarState.unit !== unit.unit){
    grammarState = {
      unit: unit.unit,
      questions: shuffle([...unit.questions]),
      current: 0,
      correct: 0,
      answered: false
    };
  }

  const total = grammarState.questions.length;
  const q = grammarState.questions[grammarState.current];

  container.innerHTML = `
    <div class="quiz-container">
      <div class="quiz-progress">${grammarState.current + 1} / ${total}</div>
      <div class="quiz-card">
        <div class="quiz-word" style="font-size:22px;line-height:1.6">${q.question}</div>
      </div>
      <div class="options-grid" id="grammarOptions">
        ${q.options.map((opt, i) => `
          <button class="option-btn" data-idx="${i}" data-answer="${escapeHtml(q.answer)}" data-opt="${escapeHtml(opt)}" onclick="answerGrammar(this)">
            ${opt}
          </button>
        `).join('')}
      </div>
      <div class="quiz-feedback" id="grammarFeedback"></div>
      <div class="quiz-actions">
        <button class="btn btn-ghost" onclick="go('home')">退出</button>
        <button class="btn btn-primary" id="grammarNextBtn" disabled onclick="nextGrammar()">下一题 → <span style="font-size:11px;opacity:.7">(Enter)</span></button>
      </div>
    </div>
  `;
}

function escapeHtml(text){
  if(text === null || text === undefined) return '';
  return String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

function answerGrammar(btn){
  if(!grammarState || grammarState.answered) return;
  const picked = btn.dataset.opt;
  const correct = btn.dataset.answer;
  const opts = document.querySelectorAll('#grammarOptions .option-btn');
  opts.forEach(o => o.classList.add('disabled'));
  const fb = document.getElementById('grammarFeedback');
  const isCorrect = picked === correct;

  opts.forEach(o => {
    if(o.dataset.opt === correct) o.classList.add('correct');
    else if(o.dataset.opt === picked && !isCorrect) o.classList.add('wrong');
  });

  if(isCorrect){
    grammarState.correct++;
    fb.className = 'quiz-feedback show correct';
    fb.innerHTML = '✅ 回答正确！';
  }else{
    fb.className = 'quiz-feedback show wrong';
    fb.innerHTML = `❌ 答错了。正确答案是：${correct}`;
  }
  grammarState.answered = true;
  document.getElementById('grammarNextBtn').disabled = false;
}

function nextGrammar(){
  if(!grammarState) return;
  grammarState.answered = false;
  grammarState.current++;
  if(grammarState.current >= grammarState.questions.length){
    showGrammarResult();
  }else{
    renderGrammarQuestions();
  }
}

function showGrammarResult(){
  const container = document.getElementById('grammarContent');
  const total = grammarState.questions.length;
  const correct = grammarState.correct;
  const pct = Math.round(correct / total * 100);
  container.innerHTML = `
    <div class="quiz-result">
      <div class="quiz-result-score">${correct}/${total}</div>
      <div class="quiz-result-title">本单元完成！</div>
      <div class="quiz-result-desc">正确率 ${pct}%</div>
      <div class="quiz-actions" style="justify-content:center;margin-top:24px">
        <button class="btn btn-ghost" onclick="go('home')">返回首页</button>
        <button class="btn btn-primary" onclick="restartGrammarUnit()">再来一遍</button>
      </div>
    </div>
  `;
}

function restartGrammarUnit(){
  grammarState = null;
  renderGrammar();
}

// 全局键盘监听增加语法模式
const _originalKeydown = document.onkeydown;
document.addEventListener('keydown', e => {
  if(currentView === 'grammar' && grammarState && grammarState.answered && e.key === 'Enter'){
    e.preventDefault();
    nextGrammar();
  }
});
'''

# 在 </script> 之前插入
old_script_end = '</script>'
# 找到最后一个 </script>
last_idx = html.rfind(old_script_end)
if last_idx != -1:
    html = html[:last_idx] + grammar_js + '\n' + html[last_idx:]
    print('Added grammar JS functions')
else:
    print('WARN: </script> not found')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Done injecting grammar mode into index.html')
