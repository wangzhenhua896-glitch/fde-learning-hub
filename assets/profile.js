/* FDE 实训平台 · 能力档案
 * 数据：window.PF_DATA（构建时注入：projects 概要 + dims）
 * 状态：与 workbench.js 共用 localStorage（wb_stages_{pid} / wb_profile）
 * 只读聚合：不修改任何实训状态；导出 JSON / PNG 全部在本机完成。
 */
(function () {
  'use strict';
  var D = window.PF_DATA;
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };
  var ST_LABEL = { not_started: '未开始', in_progress: '进行中', submitted: '待评审', revise: '需修改', passed: '通过' };

  function stages(pid) { try { var v = localStorage.getItem('wb_stages_' + pid); return v ? JSON.parse(v) : {}; } catch (e) { return {}; } }
  function profile() { try { var v = localStorage.getItem('wb_profile'); return v ? JSON.parse(v) : null; } catch (e) { return null; } }

  // 聚合：每项目通过阶段；每维度通过数（跨项目）
  function aggregate() {
    var rows = [];
    var dimPassed = {}, dimHelped = {};
    D.dims.forEach(function (d) { dimPassed[d.id] = 0; dimHelped[d.id] = 0; });
    var totalPassed = 0, totalStages = 0, evTotal = 0;
    D.projects.forEach(function (p) {
      totalStages += p.stages.length;
      var st = stages(p.id);
      var passed = [];
      p.stages.forEach(function (s) {
        var rec = st[s.id];
        if (!rec || !rec.versions) return;
        rec.versions.forEach(function (v) {
          if (v.statusLabel !== '通过') return;
          passed.push({ stage: s.title, sid: s.id, dim: s.dim, ts: v.ts, evidN: v.evidN || 0, helped: !!v.helped, rubricN: v.rubric ? v.rubric.length : 0 });
          evTotal++;
          if (v.helped) dimHelped[s.dim]++; else { dimPassed[s.dim]++; }
        });
      });
      totalPassed += passed.length;
      if (passed.length) rows.push({ p: p, passed: passed });
    });
    return { rows: rows, dimPassed: dimPassed, dimHelped: dimHelped, totalPassed: totalPassed, totalStages: totalStages, evTotal: evTotal };
  }

  function fmt(ts) { var d = new Date(ts); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }

  // ---------------- 雷达 SVG ----------------
  function radarSVG(agg) {
    var W = 320, H = 320, cx = 160, cy = 160, R = 118, N = D.dims.length;
    var maxLv = D.projects.length;                       // 每维度最多通过的项目数
    function pt(i, r) { var a = -Math.PI / 2 + i * 2 * Math.PI / N; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; }
    var svg = '<svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" style="max-width:340px" role="img" aria-label="六维能力雷达">';
    for (var g = 1; g <= 4; g++) {
      var ring = [];
      for (var i = 0; i < N; i++) { var q = pt(i, R * g / 4); ring.push(q[0].toFixed(1) + ',' + q[1].toFixed(1)); }
      svg += '<polygon points="' + ring.join(' ') + '" fill="none" stroke="#d3d1c7" stroke-width="0.6"/>';
    }
    for (var j = 0; j < N; j++) {
      var e = pt(j, R);
      svg += '<line x1="' + cx + '" y1="' + cy + '" x2="' + e[0].toFixed(1) + '" y2="' + e[1].toFixed(1) + '" stroke="#d3d1c7" stroke-width="0.6"/>';
      var lp = pt(j, R + 20);
      svg += '<text x="' + lp[0].toFixed(1) + '" y="' + lp[1].toFixed(1) + '" font-size="12" text-anchor="middle" dominant-baseline="central" fill="#444441">' + esc(D.dimMap[D.dims[j].id]) + '</text>';
      var lv = pt(j, R + 32);
      svg += '<text x="' + lv[0].toFixed(1) + '" y="' + lv[1].toFixed(1) + '" font-size="11" text-anchor="middle" dominant-baseline="central" fill="#888780">' + agg.dimPassed[D.dims[j].id] + '/' + maxLv + '</text>';
    }
    var poly = [];
    for (var k = 0; k < N; k++) { var q2 = pt(k, R * Math.min(agg.dimPassed[D.dims[k].id], maxLv) / maxLv); poly.push(q2[0].toFixed(1) + ',' + q2[1].toFixed(1)); }
    svg += '<polygon points="' + poly.join(' ') + '" fill="rgba(83,74,183,0.18)" stroke="#534AB7" stroke-width="1.5"/>';
    for (var m = 0; m < N; m++) { var q3 = pt(m, R * Math.min(agg.dimPassed[D.dims[m].id], maxLv) / maxLv); svg += '<circle cx="' + q3[0].toFixed(1) + '" cy="' + q3[1].toFixed(1) + '" r="3" fill="#534AB7"/>'; }
    svg += '</svg>';
    return svg;
  }

  // ---------------- 渲染 ----------------
  var view = $('#pf-view');
  function render() {
    var agg = aggregate();
    var pr = profile();
    if (!agg.rows.length) {
      view.innerHTML = '<div class="wb-card focus"><h3>档案还是空的</h3>' +
        '<p>能力档案聚合的是你在实训平台<b>通过验收</b>的阶段证据。还没有通过记录——去实战工作台完成第一个阶段吧：从实训库选一个项目，走完「任务→提交→评审」即可产生第一条证据。</p>' +
        '<a class="wb-btn pri" href="workbench.html">进入实训库 →</a></div>';
      return;
    }
    var html = '<div class="pf-summary wb-card"><h3>总览' + (pr ? '<span class="pf-goal">目标：' + esc(pr.goal) + '</span>' : '') + '</h3>' +
      '<div class="pf-stats">' +
      '<div><b>' + agg.totalPassed + '</b><span>阶段通过 / ' + agg.totalStages + '</span></div>' +
      '<div><b>' + agg.rows.length + '</b><span>已启动项目 / ' + D.projects.length + '</span></div>' +
      '<div><b>' + agg.evTotal + '</b><span>条评审证据</span></div>' +
      '<div><b>' + agg.rows.reduce(function (a, r) { return a + r.passed.filter(function (x) { return x.helped; }).length; }, 0) + '</b><span>条在帮助下完成（不计独立证明）</span></div>' +
      '</div></div>';
    html += '<div class="pf-grid"><div class="wb-card"><h3>六维雷达</h3>' + radarSVG(agg) +
      '<p class="wb-note">读法：数值 = 该维度<b>独立完成并通过验收</b>的项目数（在帮助下完成的不计入；括号外数字为独立证据数）。避免伪精确百分比：每格背后是可回溯的证据。</p></div>';
    html += '<div class="wb-card"><h3>维度明细</h3><ul class="pf-dimlist">';
    D.dims.forEach(function (d) {
      var ind = agg.dimPassed[d.id], helped = agg.dimHelped[d.id];
      var st = ind > 0 ? 'passed' : (helped > 0 ? 'review' : 'unknown');
      var lbl = ind > 0 ? '有证据通过 ×' + ind : (helped > 0 ? '仅辅助证据 ×' + helped : '未评估');
      html += '<li><b>' + esc(d.name) + '</b><span class="ds' + { passed: '3', review: '2', unknown: '0' }[st] + '">' + lbl + '</span><p>' + esc(d.desc) + '</p></li>';
    });
    html += '</ul></div></div>';
    html += '<section class="wb-sec"><h3>证据清单（逐项可回溯）</h3>';
    agg.rows.forEach(function (r) {
      html += '<div class="wb-card"><h3>' + esc(r.p.title) + '<span class="wb-est">' + esc(r.p.tier) + ' · ' + r.passed.length + ' 阶段通过</span></h3><ul class="wb-evlist">';
      r.passed.forEach(function (e2) {
        html += '<li><b>' + esc(e2.stage) + '</b> · ' + fmt(e2.ts) + ' · 证据 ' + e2.evidN + ' 条 · ' + (e2.helped ? '<span class="wb-helped">在帮助下完成（不计独立证明）</span>' : '独立完成') + ' · <a href="workbench.html#p/' + r.p.id + '/task-' + esc(e2.sid) + '">查看</a></li>';
      });
      html += '</ul></div>';
    });
    html += '</section>';
    html += '<div class="wb-card"><h3>导出分享</h3>' +
      '<button id="pf-json" class="wb-btn pri">导出 JSON（完整数据备份）</button> ' +
      '<button id="pf-png" class="wb-btn pri">导出 PNG（分享图片）</button>' +
      '<pre id="pf-io" class="wb-pre"></pre>' +
      '<p class="wb-note">导出全部在本机完成，不经任何服务器。PNG 由 Canvas 绘制，可直接用于简历附件或面试展示。档案是<b>自评证据链</b>，非第三方认证——面试时请如实说明评审方式。</p></div>';
    view.innerHTML = html;
    $('#pf-json').onclick = function () {
      var dump = { exportedAt: new Date().toISOString(), kind: 'fde-ability-profile', profile: profile(), projects: {} };
      D.projects.forEach(function (p) { dump.projects[p.id] = stages(p.id); });
      var blob = new Blob([JSON.stringify(dump, null, 2)], { type: 'application/json' });
      var a = document.createElement('a'); a.href = URL.createObjectURL(blob);
      a.download = 'fde-ability-profile.json'; a.click();
      $('#pf-io').textContent = '已导出 fde-ability-profile.json';
    };
    $('#pf-png').onclick = function () { exportPNG(agg); };
  }

  // ---------------- PNG 导出（Canvas） ----------------
  function exportPNG(agg) {
    var W = 900, H = 1240;
    var cv = document.createElement('canvas'); cv.width = W; cv.height = H;
    var ctx = cv.getContext('2d');
    ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#26215C'; ctx.font = '700 34px -apple-system, "PingFang SC", sans-serif';
    ctx.fillText('FDE 实训平台 · 能力档案', 48, 64);
    ctx.fillStyle = '#888780'; ctx.font = '400 16px -apple-system, "PingFang SC", sans-serif';
    ctx.fillText('生成于 ' + fmt(Date.now()) + ' · 自评证据链（非第三方认证）· fde-learning-hub.app.workbuddy.host', 48, 94);
    var pr = profile();
    if (pr) { ctx.fillText('目标：' + pr.goal, 48, 120); }
    // 雷达
    var cx = 220, cy = 400, R = 150, N = D.dims.length, maxLv = D.projects.length;
    function pt(i, r) { var a = -Math.PI / 2 + i * 2 * Math.PI / N; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; }
    for (var g = 1; g <= 4; g++) {
      ctx.beginPath();
      for (var i = 0; i < N; i++) { var q = pt(i, R * g / 4); i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }
      ctx.closePath(); ctx.strokeStyle = '#d3d1c7'; ctx.lineWidth = 1; ctx.stroke();
    }
    ctx.beginPath();
    for (var k = 0; k < N; k++) { var q2 = pt(k, R * Math.min(agg.dimPassed[D.dims[k].id], maxLv) / maxLv); k ? ctx.lineTo(q2[0], q2[1]) : ctx.moveTo(q2[0], q2[1]); }
    ctx.closePath(); ctx.fillStyle = 'rgba(83,74,183,0.2)'; ctx.fill(); ctx.strokeStyle = '#534AB7'; ctx.lineWidth = 2; ctx.stroke();
    ctx.font = '400 15px -apple-system, "PingFang SC", sans-serif';
    for (var j = 0; j < N; j++) {
      var lp = pt(j, R + 26); var nm = D.dimMap[D.dims[j].id];
      ctx.fillStyle = '#444441'; ctx.textAlign = 'center';
      ctx.fillText(nm, lp[0], lp[1]);
      ctx.fillStyle = '#888780';
      ctx.fillText(agg.dimPassed[D.dims[j].id] + '/' + maxLv, lp[0], lp[1] + 20);
    }
    ctx.textAlign = 'left';
    // 维度数字列表
    var x0 = 470, y0 = 300;
    ctx.fillStyle = '#26215C'; ctx.font = '500 22px -apple-system, "PingFang SC", sans-serif';
    ctx.fillText('六维独立证据', x0, y0 - 30);
    ctx.font = '400 17px -apple-system, "PingFang SC", sans-serif';
    D.dims.forEach(function (d, i) {
      var ind = agg.dimPassed[d.id];
      ctx.fillStyle = ind > 0 ? '#3B6D11' : '#888780';
      ctx.fillText((ind > 0 ? '✓ ' : '· ') + d.name + '：' + ind + ' 个项目独立通过', x0, y0 + i * 34);
    });
    // 项目摘要
    var yy = 660;
    ctx.fillStyle = '#26215C'; ctx.font = '500 22px -apple-system, "PingFang SC", sans-serif';
    ctx.fillText('项目进度（' + agg.totalPassed + ' / ' + agg.totalStages + ' 阶段通过）', 48, yy);
    ctx.font = '400 17px -apple-system, "PingFang SC", sans-serif';
    yy += 38;
    D.projects.forEach(function (p) {
      var done = 0, st = stages(p.id);
      p.stages.forEach(function (s) { var r = st[s.id]; if (r && r.versions && r.versions.some(function (v) { return v.statusLabel === '通过'; })) done++; });
      ctx.fillStyle = '#2C2C2A';
      ctx.fillText('· ' + p.title + '：' + done + ' / ' + p.stages.length + ' 阶段', 48, yy); yy += 30;
    });
    ctx.fillStyle = '#888780'; ctx.font = '400 14px -apple-system, "PingFang SC", sans-serif';
    ctx.fillText('评审方式：量表逐项证据留痕 + 变式追问；代码任务本机运行后上传报告（平台未独立执行）。', 48, H - 60);
    ctx.fillText('明细与出处：实战工作台（workbench.html）· 数据导出：本页 JSON。', 48, H - 36);
    var a = document.createElement('a');
    a.href = cv.toDataURL('image/png');
    a.download = 'fde-ability-profile.png'; a.click();
    $('#pf-io').textContent = '已导出 fde-ability-profile.png';
  }

  render();
})();
