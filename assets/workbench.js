/* FDE 学习工作台 P1 —— 静态优先实现
 * 数据：window.WB_DATA（构建时注入）· 状态：localStorage（wb_ 前缀）
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
    set: function (k, v) { localStorage.setItem(k, JSON.stringify(v)); }
  };

  var K_PROFILE = 'wb_profile', K_DIAG = 'wb_diag', K_STAGES = 'wb_stages';
  var ST_LABEL = { not_started: '未开始', in_progress: '进行中', submitted: '待评审', revise: '需修改', passed: '通过' };
  var ST_CLS = { not_started: 'st0', in_progress: 'st1', submitted: 'st2', revise: 'st3', passed: 'st4' };
  var DIM_ST = { unknown: '未评估', practicing: '练习中', review: '待复核', passed: '有证据通过' };
  var DIM_CLS = { unknown: 'ds0', practicing: 'ds1', review: 'ds2', passed: 'ds3' };
  // 阶段→维度（能力证据来源）
  var DIM_STAGE = {}; D.stages.forEach(function (s) { DIM_STAGE[s.dim] = s.id; });

  function profile() { return LS.get(K_PROFILE, null); }
  function diag() { return LS.get(K_DIAG, null); }
  function stages() { return LS.get(K_STAGES, {}); }
  function stage(sid) { return stages()[sid] || null; }
  function saveStage(sid, obj) { var all = stages(); all[sid] = obj; LS.set(K_STAGES, all); }
  function fmt(ts) { var d = new Date(ts); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0') + ' ' + String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0'); }

  // ---------------- 状态派生 ----------------
  function nextStage() {
    for (var i = 0; i < D.stages.length; i++) {
      var st = stage(D.stages[i].id);
      if (!st || st.status !== 'passed') return D.stages[i];
    }
    return null;
  }
  function doneCount() {
    var n = 0; D.stages.forEach(function (s) { if (stage(s.id) && stage(s.id).status === 'passed') n++; }); return n;
  }
  // 能力状态推导：阶段通过→该维度"有证据通过"；提交待评审/需修改→"待复核"；进行中→"练习中"；否则按诊断题给"练习中"线索，无则"未评估"
  function dimState(dim) {
    var sid = DIM_STAGE[dim]; var st = stage(sid);
    var q = diag(); var quizHint = null;
    if (q && q.result) {
      var r = q.result[dim];
      if (r && r.ok === 2) quizHint = 'practicing';
    }
    if (st) {
      if (st.status === 'passed') return { s: 'passed', from: '阶段「' + stageTitle(sid) + '」验收通过，证据 ' + latestVersion(sid).evidN + ' 条' };
      if (st.status === 'submitted' || st.status === 'revise') return { s: 'review', from: '阶段「' + stageTitle(sid) + '」' + ST_LABEL[st.status] + '，评审通过后升级' };
      if (st.status === 'in_progress') return { s: 'practicing', from: '阶段「' + stageTitle(sid) + '」进行中' };
    }
    if (quizHint) return { s: quizHint, from: '诊断题全部答对（仅线索，完成对应阶段后转为有证据通过）' };
    return { s: 'unknown', from: '无证据。完成诊断与对应阶段后更新' };
  }
  function stageTitle(sid) { for (var i = 0; i < D.stages.length; i++) if (D.stages[i].id === sid) return D.stages[i].title; return sid; }
  function latestVersion(sid) { var st = stage(sid); return st && st.versions.length ? st.versions[st.versions.length - 1] : null; }

  // ---------------- 路由与渲染 ----------------
  var view = $('#wb-view');
  function route() {
    var h = location.hash.replace('#', '') || 'today';
    if (h === 'today') renderToday();
    else if (h === 'diag') renderDiag();
    else if (h === 'skills') renderSkills();
    else if (h === 'data') renderData();
    else if (h.indexOf('task-') === 0) renderTask(h.slice(5));
    else renderToday();
    document.querySelectorAll('.wb-tab').forEach(function (a) {
      var on = a.getAttribute('href') === '#' + h || (h.indexOf('task-') === 0 && a.getAttribute('href') === '#tasks');
      a.classList.toggle('on', !!on);
    });
  }
  window.addEventListener('hashchange', route);

  function head(title, sub) {
    return '<div class="wb-head"><h2>' + esc(title) + '</h2>' + (sub ? '<p class="wb-sub">' + esc(sub) + '</p>' : '') + '</div>';
  }

  // ---------------- 今日 ----------------
  function renderToday() {
    var p = profile();
    if (!p) { renderOnboard(); return; }
    var ns = nextStage();
    var html = head('今日任务', D.project.one_liner);
    html += '<div class="wb-progress"><div class="wb-progress-bar"><i style="width:' + (doneCount() / D.stages.length * 100) + '%"></i></div>' +
      '<span>' + doneCount() + ' / ' + D.stages.length + ' 阶段通过</span></div>';
    if (ns) {
      var st = stage(ns.id);
      var last = st && st.versions.length ? st.versions[st.versions.length - 1] : null;
      html += '<div class="wb-card focus">' +
        '<div class="wb-card-tag">' + esc(ST_LABEL[st ? st.status : 'not_started']) + '</div>' +
        '<h3>' + esc(ns.title) + '<span class="wb-est">预计 ' + esc(ns.est) + '</span></h3>' +
        '<p>' + esc(ns.goal) + '</p>' +
        '<div class="wb-next"><b>下一项交付物：</b>' + esc(ns.deliver.join('、')) + '</div>' +
        (last && last.feedback ? '<div class="wb-feedback"><b>最近一次反馈（' + fmt(last.ts) + '）：</b>' + last.feedback + '</div>' : '') +
        '<a class="wb-btn pri" href="#task-' + ns.id + '">' + (st && st.status !== 'not_started' ? '继续任务 →' : '开始任务 →') + '</a></div>';
    } else {
      html += '<div class="wb-card focus"><h3>🎉 全部 7 个阶段验收通过</h3><p>你已获得「' + esc(D.project.title) + '」完整作品集。可到「数据」页导出全部证据留档。</p></div>';
    }
    // 诊断入口
    var dg = diag();
    html += '<div class="wb-grid2">' +
      '<div class="wb-card"><h3>📋 基础诊断</h3><p>' + (dg && dg.done ? '已完成（' + fmt(dg.ts) + '）。诊断结果只是线索，能力状态以阶段证据为准。' : '12 道知识题（6 维度 × 2 题）+ 1 个自评线索。约 10 分钟。') + '</p><a class="wb-btn" href="#diag">' + (dg && dg.done ? '查看/重做诊断' : '开始诊断') + '</a></div>' +
      '<div class="wb-card"><h3>🗺 能力地图</h3><p>六个维度的证据与差距：每个维度显示当前状态、证据来源、以及"补哪一个任务"。</p><a class="wb-btn" href="#skills">查看能力地图</a></div></div>';
    html += '<p class="wb-note">状态保存在本浏览器（localStorage），可到「数据」页导出备份。评审方式：确定性格式检查 + 量表逐项证据留痕；P2 将接入模型评审与独立复核。</p>';
    view.innerHTML = html;
  }

  function renderOnboard() {
    view.innerHTML = head('开始你的 FDE 实战', D.project.desc) +
      '<div class="wb-card focus"><h3>目标确认</h3>' +
      '<label class="wb-label">目标岗位 / 一句话目标</label>' +
      '<input id="wb-goal" class="wb-input" placeholder="如：3 个月内转岗 FDE（工程师路径）" value="工程师转型 FDE">' +
      '<label class="wb-label">每周可投入时间</label>' +
      '<select id="wb-hours" class="wb-input"><option value="3-5h">3-5 小时</option><option value="5-10h">5-10 小时</option><option value="10h+">10 小时以上</option></select>' +
      '<p class="wb-note">首版智能教学只支持<b>工程师转型路径</b>与项目「' + esc(D.project.title) + '」；其他人群路径保留为后续版本。</p>' +
      '<button id="wb-go" class="wb-btn pri">确认目标，进入诊断</button></div>';
    $('#wb-go').onclick = function () {
      LS.set(K_PROFILE, { goal: $('#wb-goal').value || '工程师转型 FDE', hours: $('#wb-hours').value, createdAt: Date.now() });
      location.hash = '#diag';
    };
  }

  // ---------------- 诊断 ----------------
  var diagDraft = {};
  function renderDiag() {
    var dg = diag();
    var html = head('基础诊断', '12 道题 × 6 个维度。诊断结果只作为学习线索：<b>答错不会给你打低分，只标记该维度"未评估/需补课"</b>；能力状态以阶段作品的证据为准。');
    if (dg && dg.done && !diagDraft._editing) {
      html += '<div class="wb-card"><h3>上次诊断结果（' + fmt(dg.ts) + '）</h3>';
      html += '<div class="wb-dimgrid">' + D.dims.map(function (d) {
        var r = dg.result[d.id] || { ok: 0, n: 2 };
        var st = dimState(d.id);
        return '<div class="wb-dim"><b>' + esc(d.name) + '</b><span>题目 ' + r.ok + '/' + r.n + '</span><span class="' + DIM_CLS[st.s] + '">' + DIM_ST[st.s] + '</span></div>';
      }).join('') + '</div>';
      html += '<p class="wb-note">维度与阶段对应：' + D.dims.map(function (d) { return esc(d.name) + '→' + esc(stageTitle(DIM_STAGE[d.id])); }).join(' · ') + '</p>';
      html += '<button id="wb-redo" class="wb-btn">重做诊断</button> <a class="wb-btn pri" href="#today">回到今日任务</a></div>';
      view.innerHTML = html;
      $('#wb-redo').onclick = function () { diagDraft._editing = true; renderDiag(); };
      return;
    }
    html += '<div class="wb-quiz">';
    D.quiz.forEach(function (q, i) {
      html += '<div class="wb-q" data-qid="' + q.id + '"><div class="wb-q-t">' + (i + 1) + '. ' + esc(q.q) + '<span class="wb-q-dim">' + esc(D.dimMap[q.dim]) + '</span></div>';
      q.opts.forEach(function (o, j) {
        html += '<label class="wb-opt"><input type="radio" name="' + q.id + '" value="' + j + '"> ' + esc(o) + '</label>';
      });
      html += '</div>';
    });
    html += '</div>';
    html += '<div class="wb-card"><h3>自评线索（不计入能力状态）</h3><p class="wb-note">以下仅用于校准辅导深度；无证据的自评不会提升能力状态。</p>';
    D.dims.forEach(function (d) {
      html += '<label class="wb-self"><input type="checkbox" data-dim="' + d.id + '"> ' + esc(D.selfRate[d.id]) + '</label>';
    });
    html += '</div>';
    html += '<button id="wb-submit-diag" class="wb-btn pri">提交诊断</button>';
    view.innerHTML = html;
    $('#wb-submit-diag').onclick = function () {
      var answers = {}, missing = 0;
      D.quiz.forEach(function (q) {
        var sel = document.querySelector('input[name="' + q.id + '"]:checked');
        if (sel) answers[q.id] = parseInt(sel.value, 10); else missing++;
      });
      if (missing) { alert('还有 ' + missing + ' 道题未作答'); return; }
      var self = {};
      document.querySelectorAll('.wb-self input:checked').forEach(function (el) { self[el.getAttribute('data-dim')] = true; });
      var result = {};
      D.dims.forEach(function (d) { result[d.id] = { ok: 0, n: 0 }; });
      D.quiz.forEach(function (q) {
        result[q.dim].n++;
        if (answers[q.id] === q.ans) result[q.dim].ok++;
      });
      LS.set(K_DIAG, { answers: answers, self: self, result: result, done: true, ts: Date.now() });
      diagDraft._editing = false;
      renderDiag();
    };
  }

  // ---------------- 任务详情 ----------------
  function renderTask(sid) {
    var s = null;
    for (var i = 0; i < D.stages.length; i++) if (D.stages[i].id === sid) s = D.stages[i];
    if (!s) { view.innerHTML = head('任务不存在'); return; }
    var st = stage(sid) || { status: 'not_started', versions: [] };
    var html = '<div class="crumb"><a href="#today">工作台</a><span>/</span><span>' + esc(s.title) + '</span></div>';
    html += '<div class="wb-status ' + ST_CLS[st.status] + '">状态：' + ST_LABEL[st.status] + '</div>';

    // ① 任务及验收要求
    html += '<section class="wb-sec"><h3>① 任务及验收要求</h3><p>' + esc(s.goal) + '</p>';
    html += '<div class="wb-cols"><div><b>交付物</b><ul>' + s.deliver.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>' +
      '<div><b>可检验标准</b><ul>' + s.checks.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div></div>';
    html += '<details class="wb-details"><summary>评审量表（' + s.rubric.length + ' 项，逐项需证据）</summary><ul class="wb-rubric-list">' +
      s.rubric.map(function (r) { return '<li>' + esc(r.k) + '<p class="wb-hint">提示：' + esc(r.hint) + '</p></li>'; }).join('') + '</ul></details></section>';

    // ② 资料与辅导（带出处）
    html += '<section class="wb-sec"><h3>② 资料与辅导<span class="wb-srcnote">（全部带出处，点击直达）</span></h3>';
    html += s.resources.map(function (r) {
      return '<div class="wb-res"><a href="' + esc(r.u) + '.html" target="_blank" rel="noopener"><b>' + esc(r.t) + '</b></a>' +
        '<span class="wb-res-src">出处：' + esc(r.src) + '</span><p>' + esc(r.why) + '</p></div>';
    }).join('') + '</section>';

    // ③ 提交及反馈
    html += '<section class="wb-sec"><h3>③ 提交及反馈</h3>';
    var v = latestVersion(sid);
    if (v) {
      html += '<div class="wb-versions"><b>版本历史</b><ul>' + st.versions.map(function (ver, i) {
        return '<li>v' + (i + 1) + ' · ' + fmt(ver.ts) + ' · ' + esc(ver.statusLabel) + (ver.helped ? ' · <span class="wb-helped">在帮助下完成</span>' : '') + '</li>';
      }).join('') + '</ul></div>';
      if (v.feedback) html += '<div class="wb-feedback big"><b>最新反馈：</b>' + v.feedback + '</div>';
    }
    if (st.status === 'passed') {
      html += '<div class="wb-passed">✅ 本阶段已通过（' + fmt(v.ts) + '）。证据已计入能力档案；变式追问：<i>' + esc(s.variant) + '</i><br>你的回答：<i>' + esc(v.variantAns) + '</i></div>';
    } else {
      html += '<label class="wb-label">提交内容（粘贴需求文档 / 测试报告 / 说明文字；代码任务请在<b>本机运行</b>后粘贴结果与报告——平台未独立执行你的代码）</label>' +
        '<textarea id="wb-artifact" class="wb-area" rows="9" placeholder="粘贴本阶段交付物……">' + esc(st.draft || '') + '</textarea>' +
        '<label class="wb-self"><input type="checkbox" id="wb-helped"> 本阶段在 AI / 他人实质性帮助下完成（如实记录，不计入独立能力证据）</label>';
      // 评审区（有待评审版本时显示）
      var pending = st.status === 'submitted' || st.status === 'revise';
      if (pending && v) {
        html += renderReview(sid, s, v);
      } else {
        html += '<button id="wb-submit" class="wb-btn pri">提交本版本（进入评审）</button>';
      }
    }
    html += '</section>';
    view.innerHTML = html;

    // 事件绑定
    var ta = $('#wb-artifact');
    if (ta) {
      ta.addEventListener('change', function () {
        var cur = stage(sid) || { status: 'not_started', versions: [] };
        cur.draft = ta.value;
        if (cur.status === 'not_started' && ta.value.trim()) cur.status = 'in_progress';
        saveStage(sid, cur);
      });
    }
    var sb = $('#wb-submit');
    if (sb) sb.onclick = function () {
      var text = $('#wb-artifact').value.trim();
      if (!text) { alert('请先粘贴提交内容'); return; }
      var helped = $('#wb-helped').checked;
      // 确定性格式检查（诚实标注：这是格式检查，不是质量评分）
      var auto = s.auto.map(function (a) { return { k: a.k, ok: new RegExp(a.re).test(text) }; });
      var ver = { ts: Date.now(), text: text, helped: helped, auto: auto, rubric: null, variantAns: '', statusLabel: '待评审' };
      var feedback = '格式检查：' + auto.filter(function (a) { return a.ok; }).length + '/' + auto.length + ' 项通过' +
        (auto.some(function (a) { return !a.ok; }) ? '（未通过项：' + auto.filter(function (a) { return !a.ok; }).map(function (a) { return a.k; }).join('；') + '）——补齐后再进入量表评审更顺' : '') +
        '。请继续完成下方量表评审：逐项给出证据。';
      ver.feedback = feedback;
      var cur = stage(sid) || { versions: [] };
      cur.status = 'submitted'; cur.versions = cur.versions || [];
      cur.versions.push(ver); cur.draft = text;
      saveStage(sid, cur);
      renderTask(sid);
    };
    bindReview(sid, s);
  }

  function renderReview(sid, s, v) {
    var html = '<div class="wb-review"><h4>评审：逐项给出证据</h4>' +
      '<p class="wb-note">评审方式说明：P1 为<b>量表评审 + 证据留痕</b>（每项须写出你如何满足、证据在哪），全部项有证据 + 变式追问回答后转为「通过」。P2 将加入模型评审与独立抽样复核。</p>';
    s.rubric.forEach(function (r, i) {
      var prev = v.rubric ? (v.rubric[i] || {}) : {};
      html += '<div class="wb-ritem" data-ri="' + i + '"><label><input type="checkbox" class="wb-r-ok" ' + (prev.ok ? 'checked' : '') + '> ' + esc(r.k) + '</label>' +
        '<textarea class="wb-r-ev" rows="2" placeholder="证据：在哪一节/哪张表/哪个测试用例……">' + esc(prev.ev || '') + '</textarea></div>';
    });
    html += '<div class="wb-variant"><b>变式追问（防投机：必须现场作答）</b><p>' + esc(s.variant) + '</p>' +
      '<textarea id="wb-variant" class="wb-area" rows="3" placeholder="写下你的回答……">' + esc(v.variantAns || '') + '</textarea></div>';
    html += '<button id="wb-finish" class="wb-btn pri">完成评审</button> <span class="wb-note">全部量表项有证据且变式已答 → 通过；否则 → 需修改（会列出缺口）</span></div>';
    return html;
  }

  function bindReview(sid, s) {
    var fin = $('#wb-finish');
    if (!fin) return;
    fin.onclick = function () {
      var cur = stage(sid); if (!cur || !cur.versions.length) return;
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
        ver.feedback = '未满足 ' + gaps.length + ' 项：<b>' + gaps.map(esc).join('；') + '</b>。逐项补证据后重新完成评审。';
        cur.status = 'revise';
      } else if (!variantAns) {
        ver.statusLabel = '需修改';
        ver.feedback = '量表项已齐，但<b>变式追问未作答</b>——没有迁移证据不能记为掌握。';
        cur.status = 'revise';
      } else {
        ver.statusLabel = '通过';
        ver.feedback = '通过：量表 ' + rubric.length + '/' + rubric.length + ' 项有证据，变式追问已作答' + (ver.helped ? '（注意：本阶段标记为"在帮助下完成"，该证据不计入独立能力证明）' : '') + '。';
        cur.status = 'passed';
      }
      saveStage(sid, cur);
      renderTask(sid);
    };
  }

  // ---------------- 能力地图 ----------------
  function renderSkills() {
    var html = head('能力地图', '六个维度 × 四种状态（未评估 / 练习中 / 待复核 / 有证据通过）。避免伪精确的百分比：只有阶段验收证据能提升状态。');
    html += '<div class="wb-skillgrid">';
    D.dims.forEach(function (d) {
      var st = dimState(d.id);
      var sid = DIM_STAGE[d.id];
      var stageDone = stage(sid) && stage(sid).status === 'passed';
      html += '<div class="wb-scard"><div class="wb-scard-h"><b>' + esc(d.name) + '</b><span class="' + DIM_CLS[st.s] + '">' + DIM_ST[st.s] + '</span></div>' +
        '<p class="wb-sdesc">' + esc(d.desc) + '</p>' +
        '<p class="wb-sfrom">' + esc(st.from) + '</p>' +
        '<div class="wb-sact">' + (stageDone ? '<span class="wb-done-mark">✅ 阶段「' + esc(stageTitle(sid)) + '」已通过</span>' :
          '<a href="#task-' + sid + '" class="wb-btn sm">补：阶段「' + esc(stageTitle(sid)) + '」→</a>') + '</div></div>';
    });
    html += '</div>';
    // 证据台账
    html += '<section class="wb-sec"><h3>证据台账</h3><p class="wb-note">每条证据包含：任务、版本、评审依据、是否在帮助下完成、日期。可到「数据」页导出。</p><ul class="wb-evlist">';
    var any = false;
    D.stages.forEach(function (s) {
      var st = stage(s.id); if (!st) return;
      st.versions.forEach(function (v, i) {
        if (v.statusLabel !== '通过') return;
        any = true;
        html += '<li><b>' + esc(s.title) + '</b> v' + (i + 1) + ' · ' + fmt(v.ts) + ' · 证据 ' + (v.evidN || 0) + ' 条 · ' + (v.helped ? '在帮助下完成（不计独立证明）' : '独立完成') + '</li>';
      });
    });
    if (!any) html += '<li class="wb-note">暂无通过记录。完成第一个阶段的提交—反馈—修改—通过循环后，这里会出现第一条证据。</li>';
    html += '</ul></section>';
    view.innerHTML = html;
  }

  // ---------------- 数据管理 ----------------
  function renderData() {
    view.innerHTML = head('数据管理', '全部学习状态保存在本浏览器。导出 JSON 可备份/迁移；导入可恢复。') +
      '<div class="wb-card"><h3>导出 / 导入</h3>' +
      '<button id="wb-export" class="wb-btn pri">导出全部数据（JSON）</button> ' +
      '<label class="wb-btn file"><input type="file" id="wb-import" accept=".json">导入备份</label> ' +
      '<button id="wb-reset" class="wb-btn danger">清空全部数据</button>' +
      '<pre id="wb-io" class="wb-pre"></pre></div>';
    $('#wb-export').onclick = function () {
      var dump = { exportedAt: new Date().toISOString(), profile: profile(), diag: diag(), stages: stages() };
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
          if (d.diag) LS.set(K_DIAG, d.diag);
          if (d.stages) LS.set(K_STAGES, d.stages);
          $('#wb-io').textContent = '导入成功，即将刷新…';
          setTimeout(function () { location.hash = '#today'; route(); }, 600);
        } catch (err) { $('#wb-io').textContent = '导入失败：' + err.message; }
      };
      r.readAsText(f);
    };
    $('#wb-reset').onclick = function () {
      if (!confirm('确定清空全部学习数据（目标/诊断/任务版本/证据）？此操作不可撤销，建议先导出备份。')) return;
      if (!confirm('再次确认：真的要清空吗？')) return;
      localStorage.removeItem(K_PROFILE); localStorage.removeItem(K_DIAG); localStorage.removeItem(K_STAGES);
      location.hash = '#today'; route();
    };
  }

  route();
})();
