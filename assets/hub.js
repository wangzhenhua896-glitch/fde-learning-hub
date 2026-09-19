(function () {
  'use strict';

  /* ---------- 侧栏抽屉（移动端） ---------- */
  var side = document.getElementById('side');
  var mask = document.getElementById('mask');
  var menuBtn = document.querySelector('.menu-btn');
  function closeSide() { if (side) side.classList.remove('open'); if (mask) mask.classList.remove('show'); }
  if (menuBtn) {
    menuBtn.addEventListener('click', function () {
      var open = side.classList.toggle('open');
      if (mask) mask.classList.toggle('show', open);
    });
  }
  if (mask) mask.addEventListener('click', closeSide);

  /* ---------- 侧栏分组折叠 ---------- */
  document.querySelectorAll('.sgroup-h').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var g = btn.parentElement;
      g.classList.toggle('open');
      btn.setAttribute('aria-expanded', g.classList.contains('open') ? 'true' : 'false');
    });
  });
  // 当前章节所在分组滚动到视野内
  var on = document.querySelector('.slist a.on');
  if (on && side && window.innerWidth > 1000) {
    var top = on.offsetTop - side.clientHeight / 2;
    if (top > 0) side.scrollTop = top;
  }

  /* ---------- 标题锚点 ---------- */
  var prose = document.getElementById('prose');
  if (prose) {
    prose.querySelectorAll('h2[id],h3[id],h4[id]').forEach(function (h) {
      var a = document.createElement('a');
      a.className = 'anchor';
      a.href = '#' + h.id;
      a.textContent = '#';
      a.setAttribute('aria-hidden', 'true');
      h.insertBefore(a, h.firstChild);
    });

    /* ---------- 代码块复制 ---------- */
    prose.querySelectorAll('pre').forEach(function (pre) {
      var btn = document.createElement('button');
      btn.className = 'copy-btn';
      btn.type = 'button';
      btn.textContent = '复制';
      btn.addEventListener('click', function () {
        var code = pre.querySelector('code');
        var txt = code ? code.innerText : pre.innerText;
        var done = function () { btn.textContent = '已复制'; setTimeout(function () { btn.textContent = '复制'; }, 1400); };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(txt).then(done, function () { fallback(txt, done); });
        } else { fallback(txt, done); }
      });
      pre.appendChild(btn);
    });
  }
  function fallback(txt, cb) {
    var ta = document.createElement('textarea');
    ta.value = txt; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); cb(); } catch (e) {}
    document.body.removeChild(ta);
  }

  /* ---------- 阅读进度 + 回顶 + 页内目录高亮 ---------- */
  var rbar = document.getElementById('rbar');
  var totop = document.getElementById('totop');
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll('.ptoc a'));
  var heads = tocLinks.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  function onScroll() {
    var h = document.documentElement.scrollHeight - window.innerHeight;
    var y = window.scrollY || document.documentElement.scrollTop;
    if (rbar) rbar.style.width = (h > 0 ? Math.min(100, (y / h) * 100) : 0) + '%';
    if (totop) totop.classList.toggle('show', y > 620);
    if (tocLinks.length) {
      var idx = 0;
      for (var i = 0; i < heads.length; i++) {
        if (heads[i] && heads[i].getBoundingClientRect().top <= 110) idx = i;
      }
      tocLinks.forEach(function (a, i) { a.classList.toggle('on', i === idx); });
    }
  }
  var raf = false;
  window.addEventListener('scroll', function () {
    if (raf) return; raf = true;
    requestAnimationFrame(function () { raf = false; onScroll(); });
  }, { passive: true });
  onScroll();
  if (totop) totop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });

  /* ---------- 全站搜索 ---------- */
  var input = document.getElementById('q');
  var panel = document.getElementById('search-panel');
  if (!input || !panel) return;

  var DATA = null, loading = false, results = [], act = -1, searching = false;

  function base() { return location.pathname.replace(/[^/]*$/, ''); }

  function load() {
    if (DATA || loading) return;
    loading = true;
    fetch(base() + 'search.json')
      .then(function (r) { return r.json(); })
      .then(function (d) { DATA = d; loading = false; if (input.value.trim().length >= 2) run(input.value); })
      .catch(function () { loading = false; });
  }

  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]; }); }

  function run(q) {
    q = q.trim().toLowerCase();
    if (q.length < 2) { hide(); return; }
    if (!DATA) { load(); return; }
    var terms = q.split(/\s+/).filter(Boolean);
    var out = [];
    for (var i = 0; i < DATA.length; i++) {
      var d = DATA[i];
      var hay = (d.t + ' ' + d.h + ' ' + d.x).toLowerCase();
      var ok = true, score = 0;
      for (var j = 0; j < terms.length; j++) {
        var p = hay.indexOf(terms[j]);
        if (p < 0) { ok = false; break; }
        score += (hay.indexOf(terms[j]) < (d.t + d.h).length) ? 4 : 1;
        score += Math.max(0, 3 - Math.floor(p / 60));
      }
      if (ok) {
        if (d.t.toLowerCase().indexOf(terms[0]) >= 0) score += 8;
        out.push({ d: d, s: score });
      }
      if (out.length > 400) break;
    }
    out.sort(function (a, b) { return b.s - a.s; });
    results = out.slice(0, 40);
    act = -1;
    render(q);
  }

  function mark(text, terms) {
    var t = esc(text);
    terms.forEach(function (term) {
      if (!term) return;
      t = t.replace(new RegExp('(' + term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'), '<mark>$1</mark>');
    });
    return t;
  }

  function render(q) {
    var terms = q.trim().toLowerCase().split(/\s+/).filter(Boolean);
    if (!results.length) {
      panel.hidden = false;
      panel.innerHTML = '<div class="sp-empty">没有找到匹配内容，试试更短的关键词。</div>';
      return;
    }
    var h = ['<div class="sp-head">找到 ' + results.length + ' 条相关段落 · ↑↓ 选择，回车打开</div>'];
    results.forEach(function (r, i) {
      var d = r.d;
      h.push('<a class="sp-item" data-i="' + i + '" href="' + d.u + '.html' + (d.a ? '#' + d.a : '') + '">' +
        '<div class="sp-t"><em>' + esc(d.t.slice(0, 18)) + '</em>' + mark(d.h, terms) + '</div>' +
        '<div class="sp-x">' + mark(d.x, terms) + '</div></a>');
    });
    panel.innerHTML = h.join('');
    panel.hidden = false;
  }

  function hide() { panel.hidden = true; panel.innerHTML = ''; act = -1; }

  function go(i) {
    var r = results[i];
    if (!r) return;
    location.href = r.d.u + '.html' + (r.d.a ? '#' + r.d.a : '');
  }

  function highlight(i) {
    panel.querySelectorAll('.sp-item').forEach(function (el, j) {
      el.classList.toggle('act', j === i);
    });
    var el = panel.querySelectorAll('.sp-item')[i];
    if (el) el.scrollIntoView({ block: 'nearest' });
  }

  var timer = null;
  input.addEventListener('input', function () {
    clearTimeout(timer);
    var v = input.value;
    timer = setTimeout(function () { run(v); }, 110);
  });
  input.addEventListener('focus', function () { load(); if (input.value.trim().length >= 2) run(input.value); });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); if (!results.length && input.value.trim().length >= 2) run(input.value); act = Math.min(act + 1, results.length - 1); highlight(act); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); act = Math.max(act - 1, 0); highlight(act); }
    else if (e.key === 'Enter') { e.preventDefault(); go(act < 0 ? 0 : act); }
    else if (e.key === 'Escape') { input.blur(); hide(); }
  });
  document.addEventListener('click', function (e) {
    if (!panel.contains(e.target) && e.target !== input) hide();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== input) {
      e.preventDefault(); input.focus(); input.select();
    }
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); input.focus(); input.select(); }
  });
})();

/* ==================== FDE Hub：学习进度（localStorage 自适应） ==================== */
(function () {
  'use strict';
  var KEY = 'fdehub-progress';
  var PROG = {};
  try { PROG = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { PROG = {}; }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(PROG)); } catch (e) {} }
  function pcount(pid) {
    var n = 0;
    for (var k in PROG) { if (PROG[k] && k.indexOf(pid + '-') === 0) n++; }
    return n;
  }
  function isRead(slug) { return !!PROG['read:' + slug]; }

  /* 内容页：标记已读 */
  var mb = document.querySelector('.mark-btn');
  if (mb) {
    var slug = mb.getAttribute('data-mark');
    var paint = function () {
      var on = isRead(slug);
      mb.classList.toggle('done', on);
      mb.textContent = on ? '✓ 已标记为已读' : '✓ 标记为已读';
    };
    paint();
    mb.addEventListener('click', function () {
      PROG['read:' + slug] = !isRead(slug);
      if (!PROG['read:' + slug]) delete PROG['read:' + slug];
      save(); paint();
    });
  }

  /* 路径页：打卡 */
  var boxes = document.querySelectorAll('.ckb[data-iid]');
  if (boxes.length) {
    var pid = boxes[0].getAttribute('data-iid').split('-')[0];
    var stages = {};
    boxes.forEach(function (b) {
      var iid = b.getAttribute('data-iid');
      var stage = iid.split('-')[1];
      (stages[stage] = stages[stage] || []).push(iid);
      var paint = function () {
        var on = !!PROG[iid];
        b.classList.toggle('done', on);
        b.closest('.item-row').classList.toggle('done-row', on);
      };
      paint();
      b.addEventListener('click', function () {
        PROG[iid] = !PROG[iid];
        if (!PROG[iid]) delete PROG[iid];
        save(); paint(); update();
      });
    });
    function update() {
      var total = 0, done = 0;
      for (var s in stages) {
        var dn = stages[s].filter(function (i) { return PROG[i]; }).length;
        total += stages[s].length; done += dn;
        var bar = document.querySelector('[data-sp="' + pid + '-' + s + '"]');
        var num = document.querySelector('[data-spn="' + pid + '-' + s + '"]');
        if (bar) bar.style.width = (dn / stages[s].length * 100) + '%';
        if (num) num.textContent = dn + '/' + stages[s].length;
      }
      var ring = document.getElementById('ring-' + pid);
      var rtxt = document.getElementById('ringtxt-' + pid);
      var pct = total ? Math.round(done / total * 100) : 0;
      if (ring) ring.setAttribute('stroke-dashoffset', 226.2 * (1 - pct / 100));
      if (rtxt) rtxt.textContent = pct + '%';
      paintSide(); paintHome();
    }
    update();
  }

  /* 侧栏迷你进度条 + 首页目标卡进度 */
  function paintSide() {
    document.querySelectorAll('a[data-progress-key]').forEach(function (a) {
      var pid = a.getAttribute('data-progress-key');
      var total = parseInt(a.getAttribute('data-total') || '0', 10);
      var bar = a.querySelector('.mini-bar');
      if (bar && total) {
        var pct = pcount(pid) / total;
        bar.classList.add('has');
        bar.innerHTML = '<i style="width:' + Math.round(pct * 100) + '%"></i>';
      }
    });
    var sp = document.getElementById('side-progress');
    if (sp) {
      var tot = 0, dn = 0;
      document.querySelectorAll('a[data-progress-key]').forEach(function (a) {
        var pid = a.getAttribute('data-progress-key');
        tot += parseInt(a.getAttribute('data-total') || '0', 10);
        dn += pcount(pid);
      });
      sp.textContent = tot ? '总进度：' + dn + ' / ' + tot + ' 项已完成' : '';
    }
  }
  function paintHome() {
    document.querySelectorAll('[data-gp]').forEach(function (el) {
      var pid = el.getAttribute('data-gp');
      var total = parseInt(el.getAttribute('data-total') || '0', 10);
      if (!total) {
        var a = document.querySelector('a[data-progress-key="' + pid + '"]');
        total = a ? parseInt(a.getAttribute('data-total') || '0', 10) : 0;
      }
      if (total) el.textContent = pcount(pid) + '/' + total;
    });
  }
  paintSide(); paintHome();
})();
