/* FDE 实训平台 · 多项目引擎 —— 静态优先实现
 * 数据：window.WB_DATA.projects[]（构建时注入）· 状态：localStorage
 * 路由：#home 实训库 / #p/{pid} 今日 / #p/{pid}/diag / #p/{pid}/skills / #p/{pid}/data / #p/{pid}/task-{sid}
 * 状态按项目隔离（wb_diag_{pid} / wb_stages_{pid}）；旧版单项目数据自动迁移到 P1。
 * 原则（蓝图 §3/§6）：
 *  - 阅读状态与能力状态分离；无证据的能力一律"未评估"
 *  - 任务状态机：未开始→进行中→待评审→需修改/通过
 *  - 评审须逐项留证据；变式追问防投机；"在帮助下完成"如实记录
 *  - 代码任务本机运行后上传报告，明确标注"未经平台独立执行"
 */
(function () {
  'use strict';
  var D = window.WB_DATA;
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };
  var LS = {
    get: function (k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set: function (k, v) { localStorage.setItem(k, JSON.stringify(v)); },
    del: function (k) { localStorage.removeItem(k); }
  };

  var K_PROFILE = 'wb_profile', K_LAST = 'wb_last';
  var LEGACY = { diag: 'wb_diag', stages: 'wb_stages' };           // 旧单项目 key → 迁移到 P1
  function proj(pid) { for (var i = 0; i < D.projects.length; i++) if (D.projects[i].id === pid) return D.projects[i]; return null; }
  function diagKey(pid) { return 'wb_diag_' + pid; }
  function stagesKey(pid) { return 'wb_stages_' + pid; }
  (function migrate() {                                             // 一次性迁移：旧 key → P1
    var p1 = D.projects[0];
    if (LS.get(LEGACY.diag, null) && !LS.get(diagKey(p1.id), null)) LS.set(diagKey(p1.id), LS.get(LEGACY.diag, null));
    if (LS.get(LEGACY.stages, null) && !LS.get(stagesKey(p1.id), null)) LS.set(stagesKey(p1.id), LS.get(LEGACY.stages, null));
  })();

  // Keep storage status values stable; only soften the words shown to learners.
  var ST_LABEL = { not_started: '未开始', in_progress: '进行中', submitted: '待自评', revise: '需补充', passed: '自评完成' };
  var ST_CLS = { not_started: 'st0', in_progress: 'st1', submitted: 'st2', revise: 'st3', passed: 'st4' };
  var DIM_ST = { unknown: '未评估', practicing: '有诊断线索', review: '待补充自评', passed: '已有自评记录' };
  var DIM_CLS = { unknown: 'ds0', practicing: 'ds1', review: 'ds2', passed: 'ds3' };
  function storedStatusLabel(label) {
    return ({ '待评审': '待自评', '需修改': '需补充', '通过': '自评完成' })[label] || label;
  }

  function profile() {
    var p = LS.get(K_PROFILE, null);
    if (p && !p.v) {                                                  // v1 → v2：自由文本目标存入 goalText
      p = { v: 2, goal: 'job', goalText: p.goal || '', background: 'other', hours: p.hours || '3-5h', pilot: '', createdAt: p.createdAt || Date.now() };
      LS.set(K_PROFILE, p);
    }
    return p;
  }
  function routingFor(p) {                                            // 第一条 when 全匹配的规则生效
    var R = D.routing || { default: { order: D.projects.map(function (x) { return x.id; }), note: '' }, rules: [] };
    for (var i = 0; i < (R.rules || []).length; i++) {
      var w = R.rules[i].when || {}, ok = true;
      for (var k in w) if (w.hasOwnProperty(k) && p[k] !== w[k]) { ok = false; break; }
      if (ok) return { note: R.rules[i].note, order: R.rules[i].order || R.default.order };
    }
    return R.default;
  }
  function dismissed(pid) {
    return LS.get('wb_overrides', []).some(function (o) { return o && o.pid === pid && o.type === 'dismiss_routing'; });
  }
  function isAdaptive(p) { return p.quiz.every(function (q) { return !!q.level; }); }
  function median(arr) {
    if (!arr.length) return 0;
    var s = arr.slice().sort(function (a, b) { return a - b; });
    var m = Math.floor(s.length / 2);
    return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
  }
  function diag(pid) { return LS.get(diagKey(pid), null); }
  function stages(pid) { return LS.get(stagesKey(pid), {}); }
  function stage(pid, sid) { return stages(pid)[sid] || null; }
  function saveStage(pid, sid, obj) { var all = stages(pid); all[sid] = obj; LS.set(stagesKey(pid), all); }
  function fmt(ts) { var d = new Date(ts); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0') + ' ' + String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0'); }

  // ---------------- 状态派生（按项目） ----------------
  function nextStage(p) {
    for (var i = 0; i < p.stages.length; i++) {
      var st = stage(p.id, p.stages[i].id);
      if (!st || st.status !== 'passed') return p.stages[i];
    }
    return null;
  }
  function doneCount(p) {
    var n = 0; p.stages.forEach(function (s) { var st = stage(p.id, s.id); if (st && st.status === 'passed') n++; }); return n;
  }
  function allDone(p) { return doneCount(p) === p.stages.length; }
  function totalPassed() {
    var n = 0; D.projects.forEach(function (p) { n += doneCount(p); }); return n;
  }
  var DIM_STAGE = {};                                               // 每项目独立构建
  function dimStage(p, dim) {
    if (!DIM_STAGE[p.id]) { var m = {}; p.stages.forEach(function (s) { m[s.dim] = s.id; }); DIM_STAGE[p.id] = m; }
    return DIM_STAGE[p.id][dim];
  }
  function dimState(p, dim) {
    var sid = dimStage(p, dim); var st = stage(p.id, sid);
    var q = diag(p.id); var quizHint = null;
    if (q && q.result) { var r = q.result[dim]; if (r && r.ok === r.n && r.n > 0) quizHint = 'practicing'; }
    if (st) {
      if (st.status === 'passed') return { s: 'passed', from: '阶段「' + stageTitle(p, sid) + '」已保存自评记录，自填依据 ' + latestVersion(p, sid).evidN + ' 项' };
      if (st.status === 'submitted' || st.status === 'revise') return { s: 'review', from: '阶段「' + stageTitle(p, sid) + '」' + ST_LABEL[st.status] + '，补充后可保存自评' };
      if (st.status === 'in_progress') return { s: 'practicing', from: '阶段「' + stageTitle(p, sid) + '」进行中' };
    }
    if (quizHint) return { s: quizHint, from: '诊断题全部答对（仅知识题线索，不代表实作能力）' };
    return { s: 'unknown', from: '无证据。完成诊断与对应阶段后更新' };
  }
  function stageTitle(p, sid) { for (var i = 0; i < p.stages.length; i++) if (p.stages[i].id === sid) return p.stages[i].title; return sid; }
  function latestVersion(p, sid) { var st = stage(p.id, sid); return st && st.versions.length ? st.versions[st.versions.length - 1] : null; }

  // ---------------- 路由 ----------------
  var view = $('#wb-view');
  var TABS = [
    ['home', '实训库'], ['today', '今日'], ['diag', '诊断'], ['skills', '学习记录'], ['data', '数据']
  ];
  function syncTabs(cur) {
    var pid = LS.get(K_LAST, null) || D.projects[0].id;
    document.querySelectorAll('.wb-tab').forEach(function (a, i) {
      var key = TABS[i] ? TABS[i][0] : null;
      if (!key) return;
      a.setAttribute('href', key === 'home' ? '#home' : (key === 'today' ? '#p/' + pid : '#p/' + pid + '/' + key));
      a.classList.toggle('on', key === cur);
    });
  }
  function route() {
    var h = location.hash.replace('#', '');
    var m;
    if (h === '' || h === 'home') { syncTabs('home'); renderHome(); }
    else if ((m = h.match(/^p\/([\w-]+)$/))) { var p = proj(m[1]); if (!p) { renderHome(); return; } LS.set(K_LAST, p.id); syncTabs('today'); renderToday(p); }
    else if ((m = h.match(/^p\/([\w-]+)\/diag$/))) { var p1 = proj(m[1]); if (!p1) { renderHome(); return; } LS.set(K_LAST, p1.id); syncTabs('diag'); renderDiag(p1); }
    else if ((m = h.match(/^p\/([\w-]+)\/skills$/))) { var p2 = proj(m[1]); if (!p2) { renderHome(); return; } LS.set(K_LAST, p2.id); syncTabs('skills'); renderSkills(p2); }
    else if ((m = h.match(/^p\/([\w-]+)\/data$/))) { var p3 = proj(m[1]); if (!p3) { renderHome(); return; } syncTabs('data'); renderData(p3); }
    else if ((m = h.match(/^p\/([\w-]+)\/task-([\w-]+)$/))) { var p4 = proj(m[1]); if (!p4) { renderHome(); return; } LS.set(K_LAST, p4.id); syncTabs('today'); renderTask(p4, m[2]); }
    else if (h === 'today' || h === 'diag' || h === 'skills' || h === 'data') {            // 旧链接兼容
      location.hash = h === 'today' ? '#p/' + (LS.get(K_LAST, null) || D.projects[0].id) : '#p/' + (LS.get(K_LAST, null) || D.projects[0].id) + '/' + h;
    }
    else { syncTabs('home'); renderHome(); }
  }
  window.addEventListener('hashchange', route);

  function head(title, sub) {
    return '<div class="wb-head"><h2>' + esc(title) + '</h2>' + (sub ? '<p class="wb-sub">' + esc(sub) + '</p>' : '') + '</div>';
  }

  // ---------------- 实训库首页 ----------------
  var homeEdit = false;                                               // 「修改目标」：有画像也强制显示表单
  function renderHome() {
    var p = profile();
    var html = head('实训库', '建议先完成入门主项目。其余项目用于完成主项目后的场景迁移练习。平台只做文本格式提示，阶段状态是个人自评记录。');
    if (!p || homeEdit) {
      html += '<div class="wb-card focus"><h3>' + (p ? '修改你的目标' : '开始前：确认你的目标') + '</h3>' +
        '<label class="wb-label">学习目的</label>' +
        '<select id="wb-goal" class="wb-input">' + D.goals.map(function (g) { return '<option value="' + g.id + '">' + esc(g.name) + '</option>'; }).join('') + '</select>' +
        '<label class="wb-label">你的背景</label>' +
        '<select id="wb-bg" class="wb-input">' + D.backgrounds.map(function (b) { return '<option value="' + b.id + '">' + esc(b.name) + '</option>'; }).join('') + '</select>' +
        '<label class="wb-label">每周可投入时间</label>' +
        '<select id="wb-hours" class="wb-input"><option value="3-5h">3-5 小时</option><option value="5-10h">5-10 小时</option><option value="10h+">10 小时以上</option></select>' +
        '<label class="wb-label">试点编号</label>' +
        '<input id="wb-pilot" class="wb-input" placeholder="试点学员填写，如 P03；其他访客留空">' +
        '<button id="wb-go" class="wb-btn pri">确认目标，进入实训库</button></div>';
      view.innerHTML = html;
      if (p) {                                                        // 预填现值（旧文本目标在 goalText，不回显）
        $('#wb-goal').value = p.goal;
        $('#wb-bg').value = p.background || 'other';
        $('#wb-hours').value = p.hours || '3-5h';
        $('#wb-pilot').value = p.pilot || '';
      }
      $('#wb-go').onclick = function () {
        var prev = profile();
        LS.set(K_PROFILE, { v: 2, goal: $('#wb-goal').value, background: $('#wb-bg').value, hours: $('#wb-hours').value, pilot: $('#wb-pilot').value.trim(), createdAt: prev && prev.createdAt || Date.now() });
        homeEdit = false;
        renderHome();
      };
      return;
    }
    var route = routingFor(p);
    var ordered = route.order.map(function (pid) { return proj(pid); }).filter(Boolean);
    if (!ordered.length) ordered = D.projects.slice();
    var mainProject = ordered[0];
    html += '<div class="wb-card"><p class="wb-note">路径建议基于你填写的目的与背景，可随时在下方修改</p>' +
      '<p>' + esc(route.note) + '</p>' +
      '<button id="wb-edit-goal" class="wb-btn sm">修改目标</button></div>';
    var done = doneCount(mainProject), ns = nextStage(mainProject);
    html += '<div class="wb-card focus wb-main-project"><div class="wb-card-tag">入门主项目 · 推荐从这里开始</div>' +
      '<h3>' + esc(mainProject.title) + '</h3><p>' + esc(mainProject.one_liner) + '</p>' +
      '<div class="wb-progress"><div class="wb-progress-bar"><i style="width:' + (done / mainProject.stages.length * 100) + '%"></i></div><span>主项目自评进度 ' + done + ' / ' + mainProject.stages.length + ' 阶段</span></div>' +
      '<a class="wb-btn pri" href="#p/' + mainProject.id + '">' + (done ? '继续主项目：' + esc(ns ? ns.title : '复习') + ' →' : '开始主项目 →') + '</a></div>';
    html += '<details class="wb-migration"><summary>完成主项目后，再选一个场景迁移练习（' + ordered.slice(1).length + ' 个项目）</summary><p class="wb-note">这些项目复用相近的交付阶段，重点是比较不同业务约束如何改变方案。无需把五个项目都做完。</p><div class="wb-grid2">';
    ordered.slice(1).forEach(function (pr) {
      var done = doneCount(pr), ns = nextStage(pr);
      html += '<div class="wb-card"><div class="wb-card-tag">场景迁移 · ' + esc(pr.tag) + '</div>' +
        '<h3>' + esc(pr.title) + '</h3><p>' + esc(pr.one_liner) + '</p>' +
        '<div class="wb-progress" style="margin:8px 0 4px"><div class="wb-progress-bar"><i style="width:' + (done / pr.stages.length * 100) + '%"></i></div><span>' + done + ' / ' + pr.stages.length + ' 阶段</span></div>' +
        (allDone(pr) ? '<a class="wb-btn pri" href="#p/' + pr.id + '">复习与导出 →</a>' :
          '<a class="wb-btn" href="#p/' + pr.id + '">' + (done > 0 ? '继续：' + esc(ns.title) + ' →' : '开始迁移练习 →') + '</a>');
      html += '</div>';
    });
    html += '</div></details>';
    html += '<p class="wb-note">进度、自填依据与提交文本只保存在你自己的浏览器（localStorage）。跨项目自评记录汇总见 <a href="profile.html">能力档案 →</a>；数据备份见各项目的「数据」页。</p>';
    view.innerHTML = html;
    $('#wb-edit-goal').onclick = function () { homeEdit = true; renderHome(); };
  }

  // ---------------- 项目内：今日 ----------------
  function renderToday(p) {
    var dg = diag(p.id);
    var ns = nextStage(p);
    var html = '<div class="crumb"><a href="#home">实训库</a><span>/</span><span>' + esc(p.title) + '</span></div>';
    html += head('今日任务', p.one_liner);
    html += '<div class="wb-progress"><div class="wb-progress-bar"><i style="width:' + (doneCount(p) / p.stages.length * 100) + '%"></i></div>' +
      '<span>' + doneCount(p) + ' / ' + p.stages.length + ' 阶段自评完成</span></div>';
    if (ns) {
      var st = stage(p.id, ns.id);
      var last = st && st.versions.length ? st.versions[st.versions.length - 1] : null;
      html += '<div class="wb-card focus">' +
        '<div class="wb-card-tag">' + esc(ST_LABEL[st ? st.status : 'not_started']) + '</div>' +
        '<h3>' + esc(ns.title) + '<span class="wb-est">预计 ' + esc(ns.est) + '</span></h3>' +
        '<p>' + esc(ns.goal) + '</p>' +
        '<div class="wb-next"><b>下一项交付物：</b>' + esc(ns.deliver.join('、')) + '</div>' +
        (last && last.feedback ? '<div class="wb-feedback"><b>最近一次反馈（' + fmt(last.ts) + '）：</b>' + last.feedback + '</div>' : '') +
        '<a class="wb-btn pri" href="#p/' + p.id + '/task-' + ns.id + '">' + (st && st.status !== 'not_started' ? '继续任务 →' : '开始任务 →') + '</a></div>';
    } else {
      html += '<div class="wb-card focus"><h3>🎉 本项目 ' + p.stages.length + ' 个阶段已完成自评</h3><p>你已保存本项目的自评记录。请按阶段提示整理并自行核对作品；平台没有运行代码或独立验证交付物。可到「数据」页备份记录，或到 <a href="profile.html">能力档案</a> 查看汇总。</p></div>';
    }
    if (dg && dg.done && dg.levels) {                                 // 路径建议卡（仅 v2 自适应诊断）
      if (dg.lowConf) {
        html += '<p class="wb-note">诊断结果被标记为低可信，路径建议未启用；可重做诊断。</p>';
      } else if (!dismissed(p.id)) {
        html += '<div class="wb-card wb-routing"><h3>路径建议（基于诊断线索）</h3>' +
          p.stages.map(function (s) {
            var lv = dg.levels[s.dim];
            var tip = lv === 2 ? '可快速过：直接看自检清单后尝试自评' : lv === 1 ? '建议正常做' : '建议先读参考资料再动手';
            return '<div class="wb-route-row"><b>' + esc(s.title) + '</b><span>' + tip + '</span></div>';
          }).join('') +
          '<p class="wb-note">建议仅来自知识题线索，随时可以按自己的节奏来。</p>' +
          '<button id="wb-dismiss-routing" class="wb-btn sm">我自己安排，不再显示</button></div>';
      }
    }
    html += '<div class="wb-grid2">' +
      '<div class="wb-card"><h3>基础诊断</h3><p>' + (dg && dg.done ? '已完成（' + fmt(dg.ts) + '）。诊断结果只是线索，能力状态以阶段证据为准。' : isAdaptive(p) ? '自适应诊断：6 个维度逐级出题（约 12-18 题）+ 1 个自评线索。约 10 分钟。' : p.quiz.length + ' 道知识题（6 维度 × 2 题）+ 1 个自评线索。约 10 分钟。') + '</p><a class="wb-btn" href="#p/' + p.id + '/diag">' + (dg && dg.done ? '查看/重做诊断' : '开始诊断') + '</a></div>' +
      '<div class="wb-card"><h3>学习自评记录</h3><p>查看诊断线索、阶段自评记录和建议补做的任务。</p><a class="wb-btn" href="#p/' + p.id + '/skills">查看学习记录</a></div></div>';
    html += '<p class="wb-note">状态保存在本浏览器（localStorage），可到「数据」页导出备份。关键词格式检查只查提交文本是否含指定词；清单与迁移回答由你自行勾选和填写，均为自评记录，不代表第三方评审或平台验证。</p>';
    view.innerHTML = html;
    var dr = $('#wb-dismiss-routing');
    if (dr) dr.onclick = function () {
      var ov = LS.get('wb_overrides', []);
      ov.push({ ts: Date.now(), pid: p.id, type: 'dismiss_routing' });
      LS.set('wb_overrides', ov);
      renderToday(p);
    };
  }

  // ---------------- 诊断 ----------------
  var diagDraft = {};
  function selfRateHtml() {
    var html = '<div class="wb-card"><h3>自评线索（不计入能力状态）</h3><p class="wb-note">以下仅用于校准辅导深度；无证据的自评不会提升能力状态。</p>';
    D.dims.forEach(function (d) {
      html += '<label class="wb-self"><input type="checkbox" data-dim="' + d.id + '"> ' + esc(D.selfRate[d.id]) + '</label>';
    });
    return html + '</div>';
  }
  function renderDiag(p) {
    var dg = diag(p.id);
    var adaptive = isAdaptive(p);
    var html = '<div class="crumb"><a href="#p/' + p.id + '">' + esc(p.title) + '</a><span>/</span><span>基础诊断</span></div>';
    html += head('基础诊断 · ' + esc(p.title), adaptive ?
      '自适应诊断：6 个维度逐级出题，按作答情况动态深入。结果只作学习线索，不测实作能力；答错不会给你打低分。' :
      p.quiz.length + ' 道知识题 × 6 个维度。结果只作学习线索，不测实作能力；答错不会给你打低分。');
    if (dg && dg.done && !diagDraft._editing) {
      html += '<div class="wb-card"><h3>上次诊断结果（' + fmt(dg.ts) + '）</h3>';
      html += '<div class="wb-dimgrid">' + D.dims.map(function (d) {
        var st = dimState(p, d.id);
        var cell = '<div class="wb-dim"><b>' + esc(d.name) + '</b>';
        if (dg.levels) {
          var lv = dg.levels[d.id];
          cell += '<span>层级线索：' + (lv === 2 ? '应用层' : lv === 1 ? '概念层' : '未接触') + '</span>';
        } else {
          var r = dg.result[d.id] || { ok: 0, n: 2 };
          cell += '<span>题目 ' + r.ok + '/' + r.n + '</span>';
        }
        if (dg.probe && dg.probe[d.id] !== undefined) cell += '<span class="wb-note">权衡探针：' + (dg.probe[d.id] ? '答对' : '未答对') + '（不计入层级）</span>';
        return cell + '<span class="' + DIM_CLS[st.s] + '">' + DIM_ST[st.s] + '</span></div>';
      }).join('') + '</div>';
      if (dg.misHits) {
        html += '<div class="wb-mis"><h4>误区提示</h4>';
        var anyMis = false;
        D.dims.forEach(function (d) {
          (dg.misHits[d.id] || []).forEach(function (mid) {
            var m = D.misconceptions[mid];
            if (!m) return;
            anyMis = true;
            html += '<div class="wb-mis-item"><b>' + esc(m.name) + '</b><span class="wb-q-dim">' + esc(d.name) + '</span><p>' + esc(m.def) + '</p>' +
              '<p class="wb-note">建议资料：' + m.resources.map(function (r) { return '<a href="' + esc(r.u) + '.html">' + esc(r.t) + '</a>'; }).join('、') + '</p></div>';
          });
        });
        if (!anyMis) html += '<p class="wb-note">本次作答没有命中已命名的典型误区。</p>';
        html += '</div>';
      }
      if (dg.lowConf) html += '<div class="wb-feedback big"><b>低可信标记：</b>本次作答速度异常快，结果标记为低可信线索，不用于路径建议。</div>';
      html += '<p class="wb-note">维度与阶段对应：' + D.dims.map(function (d) { return esc(d.name) + '→' + esc(stageTitle(p, dimStage(p, d.id))); }).join(' · ') + '</p>';
      html += '<p class="wb-note">这是知识题线索，不是能力测评。能力状态以各阶段自评证据为准。</p>';
      html += '<button id="wb-redo" class="wb-btn">重做诊断</button> <a class="wb-btn pri" href="#p/' + p.id + '">回到今日任务</a></div>';
      view.innerHTML = html;
      $('#wb-redo').onclick = function () { diagDraft._editing = true; renderDiag(p); };
      return;
    }
    if (adaptive) { startAdpt(p); return; }
    html += '<div class="wb-quiz">';
    p.quiz.forEach(function (q, i) {
      html += '<div class="wb-q" data-qid="' + q.id + '"><div class="wb-q-t">' + (i + 1) + '. ' + esc(q.q) + '<span class="wb-q-dim">' + esc(D.dimMap[q.dim]) + '</span></div>';
      q.opts.forEach(function (o, j) {
        html += '<label class="wb-opt"><input type="radio" name="' + q.id + '" value="' + j + '"> ' + esc(o) + '</label>';
      });
      html += '</div>';
    });
    html += '</div>';
    html += selfRateHtml();
    html += '<button id="wb-submit-diag" class="wb-btn pri">提交诊断</button>';
    view.innerHTML = html;
    $('#wb-submit-diag').onclick = function () {
      var answers = {}, missing = 0;
      p.quiz.forEach(function (q) {
        var sel = document.querySelector('input[name="' + q.id + '"]:checked');
        if (sel) answers[q.id] = parseInt(sel.value, 10); else missing++;
      });
      if (missing) { alert('还有 ' + missing + ' 道题未作答'); return; }
      var self = {};
      document.querySelectorAll('.wb-self input:checked').forEach(function (el) { self[el.getAttribute('data-dim')] = true; });
      var result = {};
      D.dims.forEach(function (d) { result[d.id] = { ok: 0, n: 0 }; });
      p.quiz.forEach(function (q) {
        result[q.dim].n++;
        if (answers[q.id] === q.ans) result[q.dim].ok++;
      });
      LS.set(diagKey(p.id), { answers: answers, self: self, result: result, done: true, ts: Date.now() });
      diagDraft._editing = false;
      renderDiag(p);
    };
  }

  // ---------------- 自适应诊断引擎（仅全量带 level 的题库；draft 不持久化，离开即重来） ----------------
  var adpt = null;
  function adptPlan(p) {                                              // 每维度：L1×2 / L2×2 / L3 探针×1（按数组顺序）
    var plan = {};
    p.quiz.forEach(function (q) {
      if (!plan[q.dim]) plan[q.dim] = { l1: [], l2: [], probe: null };
      if (q.level === 1) plan[q.dim].l1.push(q);
      else if (q.level === 2) plan[q.dim].l2.push(q);
      else if (q.probe) plan[q.dim].probe = q;
    });
    return plan;
  }
  function startAdpt(p) {
    adpt = { plan: adptPlan(p), di: -1, qnum: 0, records: [], answers: {}, timing: {}, levels: {}, probe: {}, done: false };
    adptNextDim(p);
  }
  function adptNextDim(p) {
    adpt.di++;
    if (adpt.di >= D.dims.length) { adpt.done = true; renderAdptSelf(p); return; }
    var g = adpt.plan[D.dims[adpt.di].id];
    adpt.step = 'l2a';                                                // 定级阶梯：L2 起步
    adpt.q = g.l2[0];
    renderAdptQ(p);
  }
  function adptAdvance(p, correct) {
    var dim = D.dims[adpt.di].id, g = adpt.plan[dim];
    if (adpt.step === 'l2a') {
      if (correct) { adpt.step = 'l2b'; adpt.q = g.l2[1]; }
      else { adpt.step = 'l1a'; adpt.q = g.l1[0]; }
    } else if (adpt.step === 'l2b') {
      if (correct) {
        adpt.levels[dim] = 2;
        if (g.probe) { adpt.step = 'probe'; adpt.q = g.probe; } else return adptNextDim(p);
      } else { adpt.levels[dim] = 1; return adptNextDim(p); }
    } else if (adpt.step === 'l1a') {
      if (correct) { adpt.step = 'l1b'; adpt.q = g.l1[1]; }
      else { adpt.levels[dim] = 0; return adptNextDim(p); }
    } else if (adpt.step === 'l1b') {
      adpt.levels[dim] = correct ? 1 : 0;
      return adptNextDim(p);
    } else if (adpt.step === 'probe') {                               // 探针单独记录，不影响定级
      adpt.probe[dim] = correct;
      return adptNextDim(p);
    }
    renderAdptQ(p);
  }
  function adptIsLast() {                                             // 末题（最后一个维度的收尾题）换按钮文案
    if (adpt.di !== D.dims.length - 1) return false;
    var g = adpt.plan[D.dims[adpt.di].id];
    return adpt.step === 'l1b' || (adpt.step === 'probe') || (adpt.step === 'l2b' && !g.probe);
  }
  function renderAdptQ(p) {
    var q = adpt.q;
    adpt.qnum++;
    adpt.presentedAt = Date.now();
    adpt.changes = 0;
    var html = '<div class="crumb"><a href="#p/' + p.id + '">' + esc(p.title) + '</a><span>/</span><span>基础诊断</span></div>';
    html += head('基础诊断 · ' + esc(p.title), '一题一屏，作答前不显示对错；答错不会给你打低分。');
    html += '<div class="wb-quiz"><div class="wb-q" data-qid="' + q.id + '"><div class="wb-q-t"><span class="wb-q-dim">' + esc(D.dimMap[q.dim]) + ' · 第 ' + adpt.qnum + ' 题</span>' + esc(q.q) + '</div>';
    q.opts.forEach(function (o, j) {
      html += '<label class="wb-opt"><input type="radio" name="' + q.id + '" value="' + j + '"> ' + esc(o) + '</label>';
    });
    html += '</div></div>';
    html += '<button id="wb-next-q" class="wb-btn pri">' + (adptIsLast() ? '查看诊断结果' : '下一题') + '</button>';
    view.innerHTML = html;
    $('.wb-q').addEventListener('change', function () { adpt.changes++; });
    $('#wb-next-q').onclick = function () {
      var sel = document.querySelector('input[name="' + q.id + '"]:checked');
      if (!sel) { alert('请先选择一个选项'); return; }
      var choice = parseInt(sel.value, 10);
      var rec = { qid: q.id, choice: choice, correct: choice === q.ans, ms: Date.now() - adpt.presentedAt, changes: adpt.changes };
      adpt.records.push(rec);
      adpt.answers[q.id] = choice;
      adpt.timing[q.id] = { ms: rec.ms, changes: rec.changes };
      adptAdvance(p, rec.correct);
    };
  }
  function renderAdptSelf(p) {
    var html = '<div class="crumb"><a href="#p/' + p.id + '">' + esc(p.title) + '</a><span>/</span><span>基础诊断</span></div>';
    html += head('基础诊断 · ' + esc(p.title), '知识题已完成，最后补充自评线索。');
    html += selfRateHtml();
    html += '<button id="wb-submit-diag" class="wb-btn pri">提交诊断</button>';
    view.innerHTML = html;
    $('#wb-submit-diag').onclick = function () { finalizeAdpt(p); };
  }
  function finalizeAdpt(p) {
    var self = {};
    document.querySelectorAll('.wb-self input:checked').forEach(function (el) { self[el.getAttribute('data-dim')] = true; });
    var qmap = {};
    p.quiz.forEach(function (q) { qmap[q.id] = q; });
    var result = {};
    D.dims.forEach(function (d) { result[d.id] = { ok: 0, n: 0 }; });
    var misHits = {};
    adpt.records.forEach(function (r) {
      var q = qmap[r.qid];
      if (!q.probe) {                                                 // 探针题不计入 ok/n
        result[q.dim].n++;
        if (r.correct) result[q.dim].ok++;
      }
      if (!r.correct) {
        var mid = q.mis && q.mis[r.choice];
        if (mid) {
          if (!misHits[q.dim]) misHits[q.dim] = [];
          if (misHits[q.dim].indexOf(mid) === -1) misHits[q.dim].push(mid);
        }
      }
    });
    var lowConf = adpt.records.every(function (r) { return r.correct; }) &&
      median(adpt.records.map(function (r) { return r.ms; })) < 2500;
    LS.set(diagKey(p.id), {
      v: 2, answers: adpt.answers, timing: adpt.timing, self: self, result: result,
      levels: adpt.levels, probe: adpt.probe, misHits: misHits, lowConf: lowConf, done: true, ts: Date.now()
    });
    adpt = null;
    diagDraft._editing = false;
    renderDiag(p);
  }

  // ---------------- 任务详情 ----------------
  function renderTask(p, sid) {
    var s = null;
    for (var i = 0; i < p.stages.length; i++) if (p.stages[i].id === sid) s = p.stages[i];
    if (!s) { view.innerHTML = head('任务不存在'); return; }
    var st = stage(p.id, sid) || { status: 'not_started', versions: [] };
    var html = '<div class="crumb"><a href="#home">实训库</a><span>/</span><a href="#p/' + p.id + '">' + esc(p.title) + '</a><span>/</span><span>' + esc(s.title) + '</span></div>';
    html += '<div class="wb-status ' + ST_CLS[st.status] + '">状态：' + ST_LABEL[st.status] + '</div>';

    html += '<section class="wb-sec"><h3>① 任务目标与自检参考</h3><p>' + esc(s.goal) + '</p>';
      html += '<div class="wb-cols"><div><b>建议交付物</b><ul>' + s.deliver.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>' +
      '<div><b>自检参考</b><ul>' + s.checks.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div></div>';
    html += '<details class="wb-details"><summary>自评清单（' + s.rubric.length + ' 项；由你自行判断并留记录）</summary><ul class="wb-rubric-list">' +
      s.rubric.map(function (r) { return '<li>' + esc(r.k) + '<p class="wb-hint">提示：' + esc(r.hint) + '</p></li>'; }).join('') + '</ul></details></section>';

    html += '<section class="wb-sec"><h3>② 资料与辅导<span class="wb-srcnote">（先读 1 篇，另外 2 篇按需查）</span></h3>';
    html += s.resources.map(function (r, ix) {
      return '<div class="wb-res' + (ix === 0 ? ' wb-res-first' : '') + '"><span class="wb-res-order">' + (ix === 0 ? '先读 1 篇' : '按需查') + '</span><a href="' + esc(r.u) + '.html" target="_blank" rel="noopener"><b>' + esc(r.t) + '</b></a>' +
        '<span class="wb-res-src">出处：' + esc(r.src) + '</span><p>' + esc(r.why) + '</p></div>';
    }).join('') + '</section>';

    html += '<section class="wb-sec"><h3>③ 提交与自评反馈</h3>';
    var v = latestVersion(p, sid);
    if (v) {
      html += '<div class="wb-versions"><b>版本历史</b><ul>' + st.versions.map(function (ver, i) {
        return '<li>v' + (i + 1) + ' · ' + fmt(ver.ts) + ' · ' + esc(storedStatusLabel(ver.statusLabel)) + (ver.helped ? ' · <span class="wb-helped">自报在帮助下完成</span>' : '') + '</li>';
      }).join('') + '</ul></div>';
      if (v.feedback) html += '<div class="wb-feedback big"><b>最新反馈：</b>' + v.feedback + '</div>';
    }
    if (st.status === 'passed') {
      html += '<div class="wb-passed">✅ 本阶段已完成自评（' + fmt(v.ts) + '）。此状态只记录你的自评与提交内容，不表示平台核实了证据或运行结果。变式追问：<i>' + esc(s.variant) + '</i><br>你的回答：<i>' + esc(v.variantAns) + '</i></div>';
    } else {
      html += '<label class="wb-label">提交内容（平台保存文字，不会运行代码或检查附件）</label>' +
        '<p class="wb-note wb-checklist">建议一并记录：作品路径；可复现步骤；测试命令与原始输出；尚未验证的部分。代码请先在本机运行并如实粘贴结果。</p>' +
        '<textarea id="wb-artifact" class="wb-area" rows="9" placeholder="粘贴交付物摘要，并附作品路径、复现步骤、测试输出和未验证项……">' + esc(st.draft || '') + '</textarea>' +
        '<label class="wb-self"><input type="checkbox" id="wb-helped"> 本阶段在 AI / 他人实质性帮助下完成（如实记录，不计入独立能力证据）</label>';
      var pending = st.status === 'submitted' || st.status === 'revise';
      if (pending && v) {
        html += renderReview(p, sid, s, v);
      } else {
        html += '<button id="wb-submit" class="wb-btn pri">保存提交文本并查看格式提示</button>';
      }
    }
    html += '</section>';
    view.innerHTML = html;

    var ta = $('#wb-artifact');
    if (ta) {
      ta.addEventListener('change', function () {
        var cur = stage(p.id, sid) || { status: 'not_started', versions: [] };
        cur.draft = ta.value;
        if (cur.status === 'not_started' && ta.value.trim()) cur.status = 'in_progress';
        saveStage(p.id, sid, cur);
      });
    }
    var sb = $('#wb-submit');
    if (sb) sb.onclick = function () {
      var text = $('#wb-artifact').value.trim();
      if (!text) { alert('请先粘贴提交内容'); return; }
      var helped = $('#wb-helped').checked;
      var auto = s.auto.map(function (a) { return { k: a.k, ok: new RegExp(a.re).test(text) }; });
      var ver = { ts: Date.now(), text: text, helped: helped, auto: auto, rubric: null, variantAns: '', statusLabel: '待评审' };
      var feedback = '关键词格式检查：' + auto.filter(function (a) { return a.ok; }).length + '/' + auto.length + ' 项匹配（只检查文本是否含关键词，不验证内容正确性）' +
        (auto.some(function (a) { return !a.ok; }) ? '（未匹配项：' + auto.filter(function (a) { return !a.ok; }).map(function (a) { return a.k; }).join('；') + '）' : '') +
        '。接下来请自行完成下方自评清单并记录证据位置。';
      ver.feedback = feedback;
      var cur = stage(p.id, sid) || { versions: [] };
      cur.status = 'submitted'; cur.versions = cur.versions || [];
      cur.versions.push(ver); cur.draft = text;
      saveStage(p.id, sid, cur);
      renderTask(p, sid);
    };
    bindReview(p, sid, s);
  }

  function renderReview(p, sid, s, v) {
    var html = '<div class="wb-review"><h4>自评清单：逐项记录依据</h4>' +
      '<p class="wb-note">请自行判断每项是否满足，并写下依据位置。勾选与文字由本人填写；页面只保存自评，不做独立评审。</p>';
    s.rubric.forEach(function (r, i) {
      var prev = v.rubric ? (v.rubric[i] || {}) : {};
      html += '<div class="wb-ritem" data-ri="' + i + '"><label><input type="checkbox" class="wb-r-ok" ' + (prev.ok ? 'checked' : '') + '> ' + esc(r.k) + '</label>' +
        '<textarea class="wb-r-ev" rows="2" placeholder="证据：在哪一节/哪张表/哪个测试用例……">' + esc(prev.ev || '') + '</textarea></div>';
    });
    html += '<div class="wb-variant"><b>迁移思考（自评记录）</b><p>' + esc(s.variant) + '</p>' +
      '<textarea id="wb-variant" class="wb-area" rows="3" placeholder="写下你的回答……">' + esc(v.variantAns || '') + '</textarea></div>';
    html += '<button id="wb-finish" class="wb-btn pri">保存自评</button> <span class="wb-note">逐项勾选并填写依据、回答迁移思考后，状态记为“自评完成”；否则提示补充。</span></div>';
    return html;
  }

  function bindReview(p, sid, s) {
    var fin = $('#wb-finish');
    if (!fin) return;
    fin.onclick = function () {
      var cur = stage(p.id, sid); if (!cur || !cur.versions.length) return;
      var ver = cur.versions[cur.versions.length - 1];
      var rubric = [];
      var gaps = [];
      document.querySelectorAll('.wb-ritem').forEach(function (el) {
        var i = parseInt(el.getAttribute('data-ri'), 10);
        var ok = $('.wb-r-ok', el).checked;
        var ev = $('.wb-r-ev', el).value.trim();
        rubric.push({ k: s.rubric[i].k, ok: ok, ev: ev });
        if (!ok || !ev) gaps.push(s.rubric[i].k);
      });
      var variantAns = $('#wb-variant').value.trim();
      ver.rubric = rubric; ver.variantAns = variantAns;
      ver.evidN = rubric.filter(function (r) { return r.ok && r.ev; }).length;
      if (gaps.length) {
        ver.statusLabel = '需修改';
        ver.feedback = '自评中有 ' + gaps.length + ' 项尚未勾选或填写依据：<b>' + gaps.map(esc).join('；') + '</b>。可补充后重新保存自评。';
        cur.status = 'revise';
      } else if (!variantAns) {
        ver.statusLabel = '需修改';
        ver.feedback = '自评清单已填写，但<b>迁移思考未作答</b>。补充后可保存自评记录。';
        cur.status = 'revise';
      } else {
        ver.statusLabel = '通过';
        ver.feedback = '自评已保存：' + rubric.length + '/' + rubric.length + ' 项已勾选并填写依据，迁移思考已回答' + (ver.helped ? '（本阶段在帮助下完成）' : '') + '。平台未核实这些依据。';
        cur.status = 'passed';
      }
      saveStage(p.id, sid, cur);
      renderTask(p, sid);
    };
  }

  // ---------------- 能力地图（项目内） ----------------
  function renderSkills(p) {
    var html = '<div class="crumb"><a href="#p/' + p.id + '">' + esc(p.title) + '</a><span>/</span><span>学习记录</span></div>';
    html += head('学习自评记录 · ' + esc(p.title), '六个维度显示诊断线索与阶段自评记录，不是能力测评或第三方认证。跨项目汇总见 <a href="profile.html">能力档案</a>。');
    html += '<div class="wb-skillgrid">';
    D.dims.forEach(function (d) {
      var st = dimState(p, d.id);
      var sid = dimStage(p, d.id);
      var stageDone = stage(p.id, sid) && stage(p.id, sid).status === 'passed';
      html += '<div class="wb-scard"><div class="wb-scard-h"><b>' + esc(d.name) + '</b><span class="' + DIM_CLS[st.s] + '">' + DIM_ST[st.s] + '</span></div>' +
        '<p class="wb-sdesc">' + esc(d.desc) + '</p>' +
        '<p class="wb-sfrom">' + esc(st.from) + '</p>' +
        '<div class="wb-sact">' + (stageDone ? '<span class="wb-done-mark">✅ 阶段「' + esc(stageTitle(p, sid)) + '」已自评完成</span>' :
          '<a href="#p/' + p.id + '/task-' + sid + '" class="wb-btn sm">学习：阶段「' + esc(stageTitle(p, sid)) + '」→</a>') + '</div></div>';
    });
    html += '</div>';
    html += '<section class="wb-sec"><h3>自评记录（本项目）</h3><p class="wb-note">每条记录包含：任务、版本、自填依据、是否在帮助下完成、日期。平台未核验记录内容。跨项目汇总见 <a href="profile.html">能力档案</a>；可到「数据」页导出。</p><ul class="wb-evlist">';
    var any = false;
    p.stages.forEach(function (s) {
      var st = stage(p.id, s.id); if (!st) return;
      st.versions.forEach(function (v, i) {
        if (v.statusLabel !== '通过') return;
        any = true;
        html += '<li><b>' + esc(s.title) + '</b> v' + (i + 1) + ' · ' + fmt(v.ts) + ' · 自填依据 ' + (v.evidN || 0) + ' 项 · ' + (v.helped ? '自报在帮助下完成' : '自报独立完成') + '</li>';
      });
    });
    if (!any) html += '<li class="wb-note">本项目暂无自评完成记录。保存第一个阶段的提交与自评后，这里会出现第一条记录。</li>';
    html += '</ul></section>';
    view.innerHTML = html;
  }

  // ---------------- 数据管理（全局） ----------------
  function allKeys() {
    var keys = [];
    for (var i = 0; i < localStorage.length; i++) {
      var k = localStorage.key(i);
      if (k && (k.indexOf('wb_') === 0)) keys.push(k);
    }
    return keys;
  }
  function renderData(p) {
    var html = '<div class="crumb"><a href="#p/' + p.id + '">' + esc(p.title) + '</a><span>/</span><span>数据</span></div>';
    html += head('数据管理', '全部实训状态保存在本浏览器。导出 JSON 可备份/迁移（含全部项目）；导入可恢复。') +
      '<div class="wb-card"><h3>导出 / 导入（全部项目）</h3>' +
      '<button id="wb-export" class="wb-btn pri">导出全部数据（JSON）</button> ' +
      '<label class="wb-btn file"><input type="file" id="wb-import" accept=".json">导入备份</label> ' +
      '<button id="wb-reset" class="wb-btn danger">清空全部数据</button>' +
      '<pre id="wb-io" class="wb-pre"></pre></div>';
    view.innerHTML = html;
    $('#wb-export').onclick = function () {
      var dump = { exportedAt: new Date().toISOString(), profile: profile(), overrides: LS.get('wb_overrides', []), projects: {} };
      D.projects.forEach(function (pr) { dump.projects[pr.id] = { diag: diag(pr.id), stages: stages(pr.id) }; });
      var blob = new Blob([JSON.stringify(dump, null, 2)], { type: 'application/json' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'fde-workbench-backup.json';
      a.click();
      $('#wb-io').textContent = '已导出 fde-workbench-backup.json';
    };
    $('#wb-import').onchange = function (e) {
      var f = e.target.files[0]; if (!f) return;
      var r = new FileReader();
      r.onload = function () {
        try {
          var d = JSON.parse(r.result);
          if (d.profile) LS.set(K_PROFILE, d.profile);
          var n = 0;
          if (d.projects) {
            Object.keys(d.projects).forEach(function (pid) {
              if (!proj(pid)) return;
              if (d.projects[pid].diag) LS.set(diagKey(pid), d.projects[pid].diag);
              if (d.projects[pid].stages) LS.set(stagesKey(pid), d.projects[pid].stages);
              n++;
            });
          } else if (d.stages) {                       // 旧版单项目备份
            LS.set(stagesKey(D.projects[0].id), d.stages);
            if (d.diag) LS.set(diagKey(D.projects[0].id), d.diag);
            n = 1;
          }
          $('#wb-io').textContent = '导入成功（' + n + ' 个项目），即将刷新…';
          setTimeout(function () { location.hash = '#home'; route(); }, 600);
        } catch (err) { $('#wb-io').textContent = '导入失败：' + err.message; }
      };
      r.readAsText(f);
    };
    $('#wb-reset').onclick = function () {
      if (!confirm('确定清空全部实训数据（目标/诊断/任务版本/证据，共 ' + D.projects.length + ' 个项目）？此操作不可撤销，建议先导出备份。')) return;
      if (!confirm('再次确认：真的要清空吗？')) return;
      allKeys().forEach(function (k) { LS.del(k); });
      location.hash = '#home'; route();
    };
  }

  route();
})();
