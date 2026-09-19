// ===== EXAM (真题生词库：多届标签 + 选词义/拼写) =====
let examState = null;
let examWriteState = null;
let currentExamLevelId = null;
let currentExamUnit = 1;
let examMode = 'quiz';

function getExamLevels(){ return EXAM_DATA.levels || []; }
function getCurrentExamLevel(){
  const lv = getExamLevels();
  return lv.find(l => l.id === currentExamLevelId) || lv[0];
}
function getExamUnits(){
  const lv = getCurrentExamLevel();
  return lv ? (lv.units || []) : [];
}
function getExamUnitWords(unitNum){
  const u = getExamUnits().find(x => x.unit === unitNum);
  return u ? u.words : [];
}

function renderExam(){
  renderExamLevelTabs();
  renderExamModeTabs();
  const us = document.getElementById('examUnitSelector');
  const units = getExamUnits();
  if(units.length === 0){
    us.innerHTML = '<div style="color:var(--ink-soft)">暂无真题单元</div>';
    document.getElementById('examContent').innerHTML = '';
    return;
  }
  if(!units.some(u => u.unit === currentExamUnit)) currentExamUnit = units[0].unit;
  us.innerHTML = units.map(u =>
    `<button class="unit-pill ${currentExamUnit === u.unit ? 'active' : ''}" onclick="selectExamUnit(${u.unit})">第${u.unit}单元</button>`
  ).join('');
  if(examMode === 'quiz') renderExamQuiz();
  else renderExamWrite();
}

function renderExamLevelTabs(){
  const c = document.getElementById('examLevelTabs');
  if(!c) return;
  const levels = getExamLevels();
  if(!currentExamLevelId && levels.length) currentExamLevelId = levels[0].id;
  c.innerHTML = levels.map(l => {
    const active = l.id === currentExamLevelId ? 'active' : '';
    const wordCount = l.units.reduce((s,u)=>s+u.words.length,0);
    return `<button class="level-tab ${active}" onclick="setExamLevel('${l.id}')">
      <span class="level-tab-name">${l.name}</span>
      <span class="level-tab-kr">${l.kr}</span>
      <span class="level-tab-count">${wordCount}词</span>
    </button>`;
  }).join('');
}

function setExamLevel(id){
  if(id === currentExamLevelId) return;
  currentExamLevelId = id;
  const units = getExamUnits();
  currentExamUnit = units.length ? units[0].unit : 1;
  examState = null;
  examWriteState = null;
  renderExam();
}

function renderExamModeTabs(){
  const c = document.getElementById('examModeTabs');
  const tabs = [
    {id:'quiz', name:'选词义', kr:'의미 선택'},
    {id:'write', name:'拼写', kr:'철자'}
  ];
  c.innerHTML = tabs.map(m =>
    `<button class="level-tab ${examMode === m.id ? 'active' : ''}" onclick="setExamMode('${m.id}')">
      <span class="level-tab-name">${m.name}</span>
      <span class="level-tab-kr">${m.kr}</span>
    </button>`
  ).join('');
}

function setExamMode(m){
  if(examMode === m) return;
  examMode = m;
  examState = null;
  examWriteState = null;
  renderExam();
}

function selectExamUnit(u){
  currentExamUnit = u;
  examState = null;
  examWriteState = null;
  renderExam();
}

// ----- 真题 · 选词义 -----
function renderExamQuiz(){
  const words = getExamUnitWords(currentExamUnit);
  const container = document.getElementById('examContent');
  if(words.length === 0){
    container.innerHTML = '<div style="text-align:center;padding:48px;color:var(--ink-soft)">该单元暂无单词</div>';
    return;
  }
  if(!examState || examState.unit !== currentExamUnit){
    examState = {
      unit: currentExamUnit,
      questions: shuffle([...words]),
      current: 0,
      correct: 0,
      answered: false,
      mistakeMap: {}
    };
  }
  renderExamQuestion();
}

function renderExamQuestion(){
  const container = document.getElementById('examContent');
  const words = getExamUnitWords(currentExamUnit);
  const q = examState.questions[examState.current];
  const wrongPool = shuffle(words.filter(x => x.word !== q.word && x.cn !== q.cn));
  const wrongs = [];
  for(const x of wrongPool){
    if(!wrongs.some(y => y.cn === x.cn)) wrongs.push(x);
    if(wrongs.length === 3) break;
  }
  const options = shuffle([q.cn, ...wrongs.map(x => x.cn)]);
  const total = examState.questions.length;

  container.innerHTML = `
    <div class="quiz-container">
      <div class="quiz-progress">${examState.current + 1} / ${total}</div>
      <div class="quiz-card">
        <div class="quiz-word">${q.word}</div>
        <div class="quiz-hint">自动播放发音 · 也可点击 🔊 重听</div>
        <div style="margin-top:18px">
          <button class="btn btn-ghost" onclick="speakWord('${q.word.replace(/'/g, "\\'")}')">🔊 听发音</button>
        </div>
      </div>
      <div class="options-grid" id="examOptions">
        ${options.map(opt => `
          <button class="option-btn" data-answer="${escapeHtml(q.cn)}" data-opt="${escapeHtml(opt)}" onclick="answerExam(this)">
            ${opt}
          </button>
        `).join('')}
      </div>
      <div class="quiz-feedback" id="examFeedback"></div>
      <div class="quiz-actions">
        <button class="btn btn-ghost" onclick="go('home')">退出</button>
        <button class="btn btn-primary" id="examNextBtn" disabled onclick="nextExam()">下一题 → <span style="font-size:11px;opacity:.7">(Enter)</span></button>
      </div>
    </div>
  `;
  setTimeout(() => speakWord(q.word), 350);
}

function answerExam(btn){
  if(!examState || examState.answered) return;
  const picked = btn.dataset.opt;
  const correct = btn.dataset.answer;
  const opts = document.querySelectorAll('#examOptions .option-btn');
  opts.forEach(o => o.classList.add('disabled'));
  const fb = document.getElementById('examFeedback');
  const isCorrect = picked === correct;

  opts.forEach(o => {
    if(o.dataset.opt === correct) o.classList.add('correct');
    else if(o.dataset.opt === picked && !isCorrect) o.classList.add('wrong');
  });

  if(isCorrect){
    examState.correct++;
    fb.className = 'quiz-feedback show correct';
    fb.innerHTML = '✅ 回答正确！';
  }else{
    fb.className = 'quiz-feedback show wrong';
    fb.innerHTML = `❌ 答错了。正确释义：${correct}`;
    const key = examState.questions[examState.current].word;
    examState.mistakeMap[key] = (examState.mistakeMap[key] || 0) + 1;
    insertRetry(examState.questions, examState.current, examState.questions[examState.current]);
  }
  examState.answered = true;
  document.getElementById('examNextBtn').disabled = false;
}

function nextExam(){
  if(!examState) return;
  examState.answered = false;
  examState.current++;
  if(examState.current >= examState.questions.length){
    showExamResult();
  }else{
    renderExamQuestion();
  }
}

function showExamResult(){
  const container = document.getElementById('examContent');
  const total = examState.questions.length;
  const correct = examState.correct;
  const pct = Math.round(correct / total * 100);
  const mistakes = Object.values(examState.mistakeMap).reduce((a,b)=>a+b,0);
  container.innerHTML = `
    <div class="quiz-result">
      <div class="quiz-result-score">${correct}/${total}</div>
      <div class="quiz-result-title">本单元完成！</div>
      <div class="quiz-result-desc">正确率 ${pct}% · 错题 ${mistakes} 道（已安排重复练习）</div>
      <div class="quiz-actions" style="justify-content:center;margin-top:24px">
        <button class="btn btn-ghost" onclick="go('home')">返回首页</button>
        <button class="btn btn-primary" onclick="restartExamUnit()">再来一遍</button>
      </div>
    </div>
  `;
}

function restartExamUnit(){
  examState = null;
  renderExamQuiz();
}

// ----- 真题 · 拼写（看中文默写韩文）-----
function renderExamWrite(){
  const words = getExamUnitWords(currentExamUnit);
  const container = document.getElementById('examContent');
  if(words.length === 0){
    container.innerHTML = '<div style="text-align:center;padding:48px;color:var(--ink-soft)">该单元暂无单词</div>';
    return;
  }
  if(!examWriteState || examWriteState.unit !== currentExamUnit){
    examWriteState = {
      unit: currentExamUnit,
      words: shuffle([...words]),
      current: 0,
      correct: 0,
      answered: false
    };
  }
  renderExamWriteQuestion();
}

function renderExamWriteQuestion(){
  const c = document.getElementById('examContent');
  if(!examWriteState){ renderExamWrite(); return; }
  if(examWriteState.current >= examWriteState.words.length){
    showExamWriteResult();
    return;
  }
  const w = examWriteState.words[examWriteState.current];
  const total = examWriteState.words.length;
  const cur = examWriteState.current + 1;

  c.innerHTML = `
    <div class="spell-stage" style="max-width:640px;margin:0 auto">
      <div class="quiz-progress" style="max-width:640px;margin:0 auto 24px">
        <div class="progress-count">${cur} / ${total}</div>
        <div class="progress-count">正确 ${examWriteState.correct}</div>
      </div>
      <div class="spell-card">
        <div class="spell-hint">请根据中文释义拼写对应的韩文单词</div>
        <div class="spell-cn">${w.cn}</div>
      </div>
      <div class="spell-input-row">
        <input type="text" class="spell-input" id="exWriteInput"
          placeholder="在此输入韩文..."
          autocomplete="off" autocapitalize="off" spellcheck="false"
          onkeydown="if(event.key==='Enter'){event.preventDefault(); examWriteState.answered ? nextExamWrite() : checkExWrite();}">
        <button class="btn btn-primary" onclick="checkExWrite()">提交</button>
      </div>
      <div style="text-align:center;margin-bottom:16px">
        <button class="btn btn-ghost" onclick="revealExAnswer()">👁 看答案</button>
        <button class="btn btn-ghost" onclick="speakWord('${w.word.replace(/'/g, "\\'")}')">🔊 听发音</button>
      </div>
      <div class="spell-reveal" id="exWriteReveal">
        <div class="spell-reveal-label">正确答案</div>
        <div class="spell-reveal-word">${w.word}</div>
      </div>
      <div class="quiz-feedback" id="exWriteFeedback"></div>
      <div style="text-align:center;margin-top:24px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
        <button class="btn btn-ghost" onclick="go('home')">退出</button>
        <button class="btn btn-primary" id="exWriteNextBtn" style="display:none" onclick="nextExamWrite()">下一个 → <span style="font-size:11px;opacity:.7">(Enter)</span></button>
      </div>
    </div>
  `;
  setTimeout(() => document.getElementById('exWriteInput')?.focus(), 100);
}

function checkExWrite(){
  if(!examWriteState || examWriteState.answered) return;
  const input = document.getElementById('exWriteInput');
  if(!input) return;
  const val = input.value.trim();
  if(!val){ toast('请先输入韩语单词'); return; }
  const w = examWriteState.words[examWriteState.current];
  const fb = document.getElementById('exWriteFeedback');
  const isCorrect = val === w.word || val.replace(/\s/g,'') === w.word;
  examWriteState.answered = true;

  if(isCorrect){
    input.classList.add('correct');
    examWriteState.correct++;
    fb.className = 'quiz-feedback show correct';
    fb.innerHTML = '✅ 写对了！';
    toast('✅ 正确！');
  }else{
    input.classList.add('wrong');
    document.getElementById('exWriteReveal').classList.add('show');
    fb.className = 'quiz-feedback show wrong';
    fb.innerHTML = '❌ 还差一点，看看正确答案吧';
    toast('❌ 再想想');
    insertRetry(examWriteState.words, examWriteState.current, w);
  }
  document.getElementById('exWriteNextBtn').style.display = 'inline-block';
  input.focus();
}

function revealExAnswer(){
  const reveal = document.getElementById('exWriteReveal');
  if(reveal) reveal.classList.add('show');
  if(examWriteState && !examWriteState.answered){
    examWriteState.answered = true;
    const btn = document.getElementById('exWriteNextBtn');
    if(btn) btn.style.display = 'inline-block';
  }
  document.getElementById('exWriteInput')?.focus();
}

function nextExamWrite(){
  examWriteState.current++;
  examWriteState.answered = false;
  renderExamWriteQuestion();
}

function showExamWriteResult(){
  const container = document.getElementById('examContent');
  const total = examWriteState.words.length;
  const correct = examWriteState.correct;
  const pct = total ? Math.round(correct / total * 100) : 0;
  container.innerHTML = `
    <div class="quiz-result">
      <div class="quiz-result-score">${correct}/${total}</div>
      <div class="quiz-result-title">本单元完成！</div>
      <div class="quiz-result-desc">正确率 ${pct}%</div>
      <div class="quiz-actions" style="justify-content:center;margin-top:24px">
        <button class="btn btn-ghost" onclick="go('home')">返回首页</button>
        <button class="btn btn-primary" onclick="restartExamWriteUnit()">再来一遍</button>
      </div>
    </div>
  `;
}

function restartExamWriteUnit(){
  examWriteState = null;
  renderExamWrite();
}

// 全局键盘监听：真题选词义 Enter 下一题
document.addEventListener('keydown', e => {
  if(currentView === 'exam' && examMode === 'quiz' && examState && examState.answered && e.key === 'Enter'){
    e.preventDefault();
    nextExam();
  }
});
