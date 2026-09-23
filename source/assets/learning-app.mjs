import {freshProfile, validateContent, applyEvidence, applyDiagnostic, importWorkbenchSignals, importWorkbenchSelfReports, recommend, demoProfile, skillsFromJD} from './learning-core.mjs';
const root = document.querySelector('#learning-app');
if (root) {
  const data = await fetch('assets/learning.json').then(r => r.json());
  validateContent(data);
  const STORE = 'learning_profile_v1';
  const esc = x => String(x ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const load = () => { try { return JSON.parse(localStorage.getItem(STORE)) || freshProfile(); } catch { return freshProfile(); } };
  let profile = load(), current = null, lab = null, labMode = 'browser-demo', localSessions = new Map();
  const LAB_REF = 'learning_lab_session_v1';
  const save = p => { profile = p; localStorage.setItem(STORE, JSON.stringify(p)); };
  if (profile.onboarding === 'new' && !localStorage.getItem('learning_ignore_legacy')) { try { const prior = JSON.parse(localStorage.getItem('wb_profile')); if (prior) { profile.role = 'fde'; profile.background = prior.background || 'novice'; } const diag = JSON.parse(localStorage.getItem('wb_diag_kb-assistant')); if (diag) profile = importWorkbenchSignals(profile, diag); const stages=JSON.parse(localStorage.getItem('wb_stages_kb-assistant')); if (stages) profile=importWorkbenchSelfReports(profile,stages); } catch {} }
  const unit = id => data.units.find(u => u.id === id);
  const skillName = id => data.skills.find(s => s.id === id)?.name || id;
  const unitUnlocked = (u,extra=[]) => u.prerequisites.every(pid => extra.includes(pid) || profile.completed.includes(pid) || unit(pid)?.skills.every(s => (profile.mastery[s]?.score || 0) >= 65)) && u.skills.every(id => (data.skills.find(s=>s.id===id)?.prerequisites || []).every(pre => (profile.mastery[pre]?.score || 0) >= 10 || extra.some(pid => unit(pid)?.skills.includes(pre))));
  const formatName = {micro_lesson:'微课',deep_dive:'深入学习',worked_example:'示例',interactive_quiz:'互动题',flash_review:'闪卡复习',guided_lab:'引导实训',challenge_lab:'挑战实训',capstone:'综合项目',real_world_fde_case:'FDE 案例',jd_skill_drill:'岗位技能练习'};
  const roleName = {fde:'FDE', 'applied-ai':'Applied AI', solutions:'Solutions Engineer', 'ai-engineer':'AI Engineer'};
  const resources = u => u.resources?.length ? `<details class="learn-resources"><summary>需要时再看深入资料</summary><p>${u.resources.map(r=>`<a href="${esc(r.url)}">${esc(r.title)}</a>`).join(' · ')}</p></details>` : '';
  function shell(body) { root.innerHTML = `<div class="learn-shell">${body}</div>`; }
  function bind(id, fn) { document.getElementById(id)?.addEventListener('click', fn); }
  function render() {
    const hash = location.hash.replace(/^#/, '');
    if (profile.onboarding === 'new' && !hash.startsWith('demo=')) return onboarding();
    if (hash === 'diagnose') return diagnostic();
    if (hash.startsWith('unit=')) return renderUnit(hash.slice(5).split('&')[0],hash.includes('&review=1'));
    if (hash === 'settings') return settings();
    return today();
  }
  function onboarding() {
    shell(`<section class="learn-focus"><span class="learn-kicker">只需 1 个选择</span><h1>你的下一步，从这里开始</h1><p>选择目标后，用约 5 分钟的短诊断生成学习地图。也可以先按新手默认路线开始。</p><label>我想走向 <select id="learn-role"><option value="fde">FDE</option><option value="applied-ai">Applied AI</option><option value="solutions">Solutions Engineer</option><option value="ai-engineer">AI Engineer</option></select></label><div class="learn-actions"><button class="learn-primary" id="start-diagnosis">开始短诊断 →</button><button class="learn-text" id="skip-diagnosis">先开始学习</button></div><p class="learn-muted">无需账号；进度仅保存在当前浏览器，可随时重置。</p></section><p class="learn-foot">已有资料仍可在 <a href="library.html">知识库</a> 搜索。</p>`);
    document.getElementById('learn-role').value = profile.role;
    bind('start-diagnosis', () => { save({...profile,role:document.getElementById('learn-role').value,onboarding:'diagnosing'}); location.hash = 'diagnose'; render(); });
    bind('skip-diagnosis', () => { save({...profile,role:document.getElementById('learn-role').value,onboarding:'ready'}); location.hash = ''; render(); });
  }
  function diagnostic() {
    const ids = ['discover-brief','llm-basics','rag-example','eval-basics'];
    const questions = ids.map(unit);
    const step = Number(sessionStorage.getItem('learn_diag_step') || 0);
    if (step >= questions.length) { sessionStorage.removeItem('learn_diag_step'); location.hash=''; return today(); }
    const u = questions[step], q = u.diagnostic_question;
    shell(`<section class="learn-focus"><span class="learn-kicker">短诊断 ${step+1}/${questions.length} · 约 5 分钟</span><h1>${esc(q.prompt)}</h1><p>选你认为最合适的做法。答错也只用于调整推荐。</p><div class="learn-options">${q.options.map((o,i) => `<button class="learn-option" data-answer="${i}">${esc(o)}</button>`).join('')}</div><button class="learn-text" id="diag-skip">跳过，按新手路径开始</button></section>`);
    root.querySelectorAll('[data-answer]').forEach(b => b.onclick = () => { const answers = JSON.parse(sessionStorage.getItem('learn_diag_answers') || '{}'); answers[u.id] = Number(b.dataset.answer) === q.answer; sessionStorage.setItem('learn_diag_answers',JSON.stringify(answers)); sessionStorage.setItem('learn_diag_step',String(step+1)); if (step+1 === questions.length) { save(applyDiagnostic(profile,answers,data)); sessionStorage.removeItem('learn_diag_answers'); sessionStorage.removeItem('learn_diag_step'); location.hash=''; } render(); });
    bind('diag-skip', () => { save({...profile,onboarding:'ready'}); sessionStorage.removeItem('learn_diag_step'); sessionStorage.removeItem('learn_diag_answers'); location.hash=''; render(); });
  }
  function today() {
    const rec = recommend(profile,data), u = rec.unit;
    const weak = profile.weakSkills.map(skillName).join('、');
    const completed = profile.completed.length;
    const unlock = u?.next_candidates.map(unit).find(v => v && unitUnlocked(v,[u.id]));
    shell(`<section class="learn-focus"><span class="learn-kicker">今天最值得做什么 · ${esc(roleName[profile.role])}</span><h1>${u ? esc(u.title) : '当前目标已完成'}</h1><p class="learn-reason">${esc(rec.reason)}</p>${u ? `<div class="learn-facts"><span>${esc(formatName[u.format])}</span><span>约 ${u.estimated_time} 分钟</span><span>${u.skills.map(skillName).map(esc).join(' / ')}</span></div><p class="learn-unlock">完成后：${unlock ? `解锁 ${esc(unlock.title)}` : '更新下一步并安排复习'}</p><a class="learn-primary" href="learn.html#unit=${u.id}${rec.action==='review'?'&review=1':''}">${rec.action === 'review' ? '开始短复习' : '继续学习'} →</a>` : `<a class="learn-primary" href="learn.html#settings">调整目标 →</a>`}</section><div class="learn-quiet-grid"><div><b>薄弱技能</b><p>${weak ? esc(weak) + ' · 已纳入后续推荐' : '暂无明显薄弱项'}</p></div><div><b>连续学习</b><p>${profile.streak.days || 0} 天 · 完成 ${completed} 个单元</p></div></div><p class="learn-foot"><a href="learn.html#settings">调整目标与学习时间</a>　·　<a href="library.html">探索全部资料</a>　·　<a href="workbench.html">原有交付工作台</a></p>`);
  }
  function renderUnit(id,isReview=false) {
    const u = unit(id); if (!u) { location.hash=''; return today(); } current = u;
    const unlocked = unitUnlocked(u);
    if (!unlocked && !isReview) { shell(`<section class="learn-focus"><span class="learn-kicker">逐步解锁</span><h1>先完成前面的学习</h1><p>完成基础内容后，这项练习会自动进入今日计划。</p><a class="learn-primary" href="learn.html">回到今天的计划 →</a></section>`); return; }
    if (u.lab_template) return renderLab(u);
    const q = u.question;
    shell(`<div class="learn-back"><a href="learn.html">← 今天的计划</a></div><section class="learn-focus"><span class="learn-kicker">${esc(formatName[u.format])} · 约 ${u.estimated_time} 分钟</span><h1>${esc(u.title)}</h1><p class="learn-body">${esc(u.body)}</p><div class="learn-question"><b>用一道题检验理解</b><p>${esc(q.prompt)}</p><div class="learn-options">${q.options.map((o,i) => `<button class="learn-option" data-answer="${i}">${esc(o)}</button>`).join('')}</div></div><div id="unit-result" aria-live="polite"></div>${resources(u)}</section>`);
    root.querySelectorAll('[data-answer]').forEach(b => b.onclick = () => { const ok = Number(b.dataset.answer) === q.answer; save(applyEvidence(profile,u,{kind:isReview?'review':'quiz',passed:ok,errorType:ok ? null : 'conceptual_choice'})); root.querySelectorAll('[data-answer]').forEach(x => x.disabled = true); document.getElementById('unit-result').innerHTML = `<p class="learn-result ${ok ? 'ok' : 'needs-work'}">${ok ? '答对了。已记录练习证据；复习会自动安排。' : '这道题还需补强。'}</p><p>${ok ? '' : esc(u.body)}</p><button class="learn-primary" id="unit-next">${ok ? '回到今天的计划' : '再试一次'} →</button>`; bind('unit-next', () => { if (ok) location.href='learn.html'; else renderUnit(id,isReview); }); });
  }
  async function request(path, method='GET', body=null) { const r = await fetch(path,{method,headers:{'Content-Type':'application/json'},body:body ? JSON.stringify(body) : undefined}); const j = await r.json(); if (!r.ok) throw Error(j.error || String(r.status)); return j; }
  function localProvider() {
    const persist = s => { localSessions.set(s.id,s); sessionStorage.setItem('learning_local_lab_'+s.id,JSON.stringify(s)); return s; };
    const get = id => { const s=localSessions.get(id) || JSON.parse(sessionStorage.getItem('learning_local_lab_'+id) || 'null'); if (!s || s.expiresAt < Date.now()) throw Error('session_timed_out'); return s; };
    return {
      async create(templateId) { const id=crypto.randomUUID(); return persist({id,templateId,status:'ready',workspace:{answer:null},attempts:0,hintsUsed:0,expiresAt:Date.now()+30*60*1000,quota:{maxAttempts:8,timeoutSeconds:1800},runtime:'browser-demo'}); },
      async get(id) { return get(id); },
      async workspace(id,answer) { const s=get(id); s.workspace.answer=answer; s.status='running'; return persist(s); },
      async evaluate(id) { const s=get(id), t=data.labTemplates[s.templateId]; if (s.attempts>=8) throw Error('attempt_quota_reached'); const ok=s.workspace.answer===t.answer; s.attempts++; s.status=ok?'completed':'ready'; persist(s); return {passed:ok,score:ok?100:0,tests:[{name:'场景决策',passed:ok,hidden:false},{name:'隐藏边界用例',passed:ok,hidden:true}],errorType:ok?null:'conceptual_choice',feedback:ok?'这次决策符合场景要求。':'检查权限、证据或独立验收的边界。',attempts:s.attempts,hintsUsed:s.hintsUsed,status:s.status}; },
      async hint(id) { const s=get(id), h=data.labTemplates[s.templateId].hints, ix=Math.min(s.hintsUsed,h.length-1); s.hintsUsed++; persist(s); return {level:ix+1,text:h[ix],hintsUsed:s.hintsUsed}; },
      async reset(id) { const s=get(id); s.workspace.answer=null;s.attempts=0;s.hintsUsed=0;s.status='ready';return persist(s); },
      async restart(id) { const s=get(id);s.status='ready';s.expiresAt=Date.now()+1800000;return persist(s); }
    };
  }
  let provider = localProvider();
  try { const health = await request('/api/labs/health'); if (health.provider === 'reference-mock-server') { labMode='server-mock'; provider={create:id=>request('/api/labs/sessions','POST',{templateId:id}),get:id=>request(`/api/labs/sessions/${id}`),workspace:(id,answer)=>request(`/api/labs/sessions/${id}/workspace`,'POST',{answer}),evaluate:id=>request(`/api/labs/sessions/${id}/evaluate`,'POST',{}),hint:id=>request(`/api/labs/sessions/${id}/hint`,'POST',{}),reset:id=>request(`/api/labs/sessions/${id}/reset`,'POST',{}),restart:id=>request(`/api/labs/sessions/${id}/restart`,'POST',{})}; } } catch {}
  function renderLab(u) {
    const t=data.labTemplates[u.lab_template];
    if (!lab) { const ref=JSON.parse(sessionStorage.getItem(LAB_REF) || 'null'); if (ref?.templateId===u.lab_template && ref.mode===labMode) { provider.get(ref.id).then(s=>{lab=s;renderLab(u);}).catch(()=>{sessionStorage.removeItem(LAB_REF);renderLab(u);}); return; } }
    shell(`<div class="learn-back"><a href="learn.html">← 今天的计划</a></div><section class="learn-focus"><span class="learn-kicker">浏览器实训 · Level ${t.level} · 约 ${u.estimated_time} 分钟</span><h1>${esc(u.title)}</h1><p>${esc(t.prompt)}</p>${t.config ? `<pre class="learn-config">${esc(t.config)}</pre>` : ''}<p class="learn-muted">${labMode === 'server-mock' ? '参考服务端模拟评测' : '浏览器演示模拟评测'}：这是结构化场景练习，不执行任意代码，也不代表生产级沙箱或能力认证。</p><div id="lab-runtime">${lab?.templateId===u.lab_template ? `运行状态：${esc(lab.status)} · 已尝试 ${lab.attempts}/8` : '点击开始即可创建工作区，无需安装或配置。'}</div><div id="lab-workspace"></div><div id="lab-result" aria-live="polite"></div>${resources(u)}</section>`);
    if (lab?.templateId===u.lab_template) labWorkspace(u,t); else { document.getElementById('lab-workspace').innerHTML='<button class="learn-primary" id="lab-start">开始实训 →</button>'; bind('lab-start',async()=>{ try {lab=await provider.create(u.lab_template);sessionStorage.setItem(LAB_REF,JSON.stringify({id:lab.id,templateId:u.lab_template,mode:labMode}));labWorkspace(u,t);}catch(e){showLabError(e);} }); }
  }
  function showLabError(e) { document.getElementById('lab-result').textContent=`实训暂不可用：${e.message}`; }
  function labWorkspace(u,t) {
    document.getElementById('lab-runtime').textContent=`运行状态：${lab.status} · 已尝试 ${lab.attempts}/8 · 自动保存选项 · 30 分钟超时`;
    document.getElementById('lab-workspace').innerHTML=`<div class="learn-options">${t.choices.map((x,i)=>`<label class="learn-choice"><input type="radio" name="lab-answer" value="${i}" ${lab.workspace.answer===i?'checked':''}> ${esc(x)}</label>`).join('')}</div><div class="learn-actions"><button class="learn-primary" id="lab-evaluate">运行评测</button><button class="learn-text" id="lab-hint">帮助我解卡</button><button class="learn-text" id="lab-reset">重置</button><button class="learn-text" id="lab-restart">重启</button></div><p class="learn-muted">提示按概念 → 定位 → 半成品 → 完整解释逐级展开。</p>`;
    root.querySelectorAll('[name="lab-answer"]').forEach(r => r.onchange=async()=>{try{lab=await provider.workspace(lab.id,Number(r.value));document.getElementById('lab-runtime').textContent=`运行状态：${lab.status} · 已尝试 ${lab.attempts}/8 · 已自动保存`;}catch(e){showLabError(e);} });
    bind('lab-evaluate',async()=>{ try { if (lab.workspace.answer===null) { document.getElementById('lab-result').textContent='先选择一个方案。'; return; } const result=await provider.evaluate(lab.id); lab.attempts=result.attempts;lab.status=result.status; save(applyEvidence(profile,u,{kind:'lab',passed:result.passed,tests:result.tests,errorType:result.errorType,hintsUsed:result.hintsUsed})); document.getElementById('lab-result').innerHTML=`<p class="learn-result ${result.passed?'ok':'needs-work'}">${esc(result.feedback)}</p><ul>${result.tests.map(x=>`<li>${esc(x.name)}${x.hidden?'（隐藏测试）':''}：${x.passed?'通过':'待改进'}</li>`).join('')}</ul>${result.passed?'<a class="learn-primary" href="learn.html">返回今天的计划 →</a>':'<p>可能卡在概念边界。可逐级获取提示，也可回到推荐的补充学习。</p>'}`; document.getElementById('lab-runtime').textContent=`运行状态：${lab.status} · 已尝试 ${lab.attempts}/8`; }catch(e){showLabError(e);} });
    bind('lab-hint',async()=>{try{const h=await provider.hint(lab.id);lab.hintsUsed=h.hintsUsed; document.getElementById('lab-result').innerHTML=`<p class="learn-result">第 ${h.level} 级提示：${esc(h.text)}</p>`;}catch(e){showLabError(e);} });
    bind('lab-reset',async()=>{try{lab=await provider.reset(lab.id);labWorkspace(u,t);document.getElementById('lab-result').textContent='工作区已重置。';}catch(e){showLabError(e);} });
    bind('lab-restart',async()=>{try{lab=await provider.restart(lab.id);labWorkspace(u,t);document.getElementById('lab-result').textContent='会话已重启。';}catch(e){showLabError(e);} });
  }
  function settings() {
    shell(`<section class="learn-focus"><span class="learn-kicker">学习设置</span><h1>目标可以随时改变</h1><label>目标角色 <select id="settings-role">${Object.entries(roleName).map(([id,n])=>`<option value="${id}">${esc(n)}</option>`).join('')}</select></label><label>每天可投入 <select id="settings-time"><option value="10">10 分钟</option><option value="15">15 分钟</option><option value="30">30 分钟</option><option value="60">60 分钟</option></select></label><details><summary>按需设置目标行业、地区或岗位描述</summary><label>目标行业 <select id="settings-industry"><option value="general">通用</option><option value="finance">金融</option><option value="retail">零售</option><option value="healthcare">医疗</option><option value="saas">软件服务</option></select></label><label>目标地区 <select id="settings-region"><option value="china">中国</option><option value="global">其他地区</option></select></label><label>目标公司（可选）<input id="settings-company" maxlength="80" placeholder="仅作目标标签"></label><label>岗位描述（可选）<textarea id="settings-jd" rows="4" placeholder="粘贴公开岗位要求；只提取技能标签，不保存原文"></textarea></label><p class="learn-muted">当前市场权重来自 2026-09-17 中国岗位历史样本；其他地区不使用该权重。公司名称仅作标签，路径按岗位描述中的技能重排。</p></details><div class="learn-actions"><button class="learn-primary" id="settings-save">保存并重排路径</button><button class="learn-text" id="settings-redo">重新诊断</button></div><hr><p>这些数据仅在当前浏览器保存。演示画像会覆盖当前本地画像，请先导出备份。</p><button class="learn-text" id="profile-export">导出学习画像 JSON</button><button class="learn-text" id="profile-reset">清空学习画像</button><h2>演示画像</h2><p class="learn-muted">以下为明确标注的演示数据，不代表真实用户。</p>${data.demoPersonas.map(x=>`<button class="learn-option demo-persona" data-persona="${x.id}">${esc(x.label)}</button>`).join('')}</section>`);
    document.getElementById('settings-role').value=profile.role; document.getElementById('settings-time').value=String(profile.minutesPerDay);document.getElementById('settings-industry').value=profile.industry;document.getElementById('settings-region').value=profile.region;document.getElementById('settings-company').value=profile.company || '';
    bind('settings-save',()=>{const jd=document.getElementById('settings-jd').value;save({...profile,role:document.getElementById('settings-role').value,minutesPerDay:Number(document.getElementById('settings-time').value),industry:document.getElementById('settings-industry').value,region:document.getElementById('settings-region').value,company:document.getElementById('settings-company').value.trim(),targetSkills:jd ? skillsFromJD(jd) : profile.targetSkills});location.href='learn.html';});
    bind('settings-redo',()=>{save({...profile,onboarding:'diagnosing'});sessionStorage.removeItem('learn_diag_step');location.hash='diagnose';render();});
    bind('profile-reset',()=>{if(confirm('清空当前浏览器中的自适应学习画像？')){localStorage.setItem('learning_ignore_legacy','1');save(freshProfile());location.href='learn.html';}});
    bind('profile-export',()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(profile,null,2)],{type:'application/json'}));a.download='fde-learning-profile.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);});
    root.querySelectorAll('[data-persona]').forEach(b=>b.onclick=()=>{if(confirm('载入演示画像会覆盖当前自适应学习记录，继续？')){save(demoProfile(data.demoPersonas.find(x=>x.id===b.dataset.persona)));location.href='learn.html';}});
  }
  window.addEventListener('hashchange',render);
  render();
}
