/* FDE 知识图谱：力导向布局 + 画布交互 */
(function () {
  'use strict';
  var canvas = document.getElementById('gcanvas');
  if (!canvas || typeof NODES === 'undefined') return;
  var ctx = canvas.getContext('2d');
  var wrap = canvas.parentElement;

  var DOMAIN_LIST = Object.keys(DOMAINS);
  var nodes = NODES.map(function (n, i) {
    var deg = EDGES.filter(function (e) { return e[0] === n.id || e[1] === n.id; }).length;
    var di = DOMAIN_LIST.indexOf(n.d);
    var ang = (di / DOMAIN_LIST.length) * Math.PI * 2 + 0.4 * (i % 5);
    var rad = 150 + 30 * Math.sin(i * 2.3);
    return { id: n.id, l: n.l, d: n.d, x: n.x, lv: n.lv, r: n.r, deg: deg,
      px: Math.cos(ang) * rad, py: Math.sin(ang) * rad, vx: 0, vy: 0, fixed: false };
  });
  var byId = {}; nodes.forEach(function (n) { byId[n.id] = n; });
  var edges = EDGES.map(function (e) { return { a: byId[e[0]], b: byId[e[1]], t: e[2] }; }).filter(function (e) { return e.a && e.b; });

  var W = 0, H = 0, view = { x: 0, y: 0, k: 1 };
  function resize() {
    W = wrap.clientWidth; H = wrap.clientHeight;
    canvas.width = W * devicePixelRatio; canvas.height = H * devicePixelRatio;
    ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
  }
  resize();
  window.addEventListener('resize', function () { resize(); });

  /* 域过滤 */
  var off = {};
  var chips = document.getElementById('chips');
  DOMAIN_LIST.forEach(function (d) {
    var b = document.createElement('button');
    b.className = 'chip'; b.type = 'button';
    b.innerHTML = '<span class="dot" style="background:' + DOMAINS[d][1] + '"></span>' + DOMAINS[d][0] +
      ' <span style="color:var(--ink3);font-weight:500">' + nodes.filter(function (n) { return n.d === d; }).length + '</span>';
    b.addEventListener('click', function () {
      off[d] = !off[d]; b.classList.toggle('off', !!off[d]);
    });
    chips.appendChild(b);
  });
  var legend = document.getElementById('legend');
  legend.innerHTML = '实线箭头 = 前置依赖 · 虚线 = 相关 · 节点大小 = 关联数';

  /* 模拟 */
  var alpha = 1;
  function tick() {
    alpha += (0.02 - alpha) * 0.02; if (alpha < 0.015) alpha = 0.015;
    var i, j, a, b;
    for (i = 0; i < nodes.length; i++) for (j = i + 1; j < nodes.length; j++) {
      a = nodes[i]; b = nodes[j];
      var dx = a.px - b.px, dy = a.py - b.py, d2 = dx * dx + dy * dy || 1;
      if (a.d !== b.d) d2 *= 2.2;
      var f = 2600 / d2, d = Math.sqrt(d2);
      f = Math.min(f, 12); dx /= d; dy /= d;
      a.vx += dx * f * alpha; a.vy += dy * f * alpha;
      b.vx -= dx * f * alpha; b.vy -= dy * f * alpha;
    }
    edges.forEach(function (e) {
      var dx = e.b.px - e.a.px, dy = e.b.py - e.a.py, d = Math.sqrt(dx * dx + dy * dy) || 1;
      var want = e.t === 'pre' ? 105 : 130;
      var f = (d - want) * 0.014;
      dx /= d; dy /= d;
      e.a.vx += dx * f; e.a.vy += dy * f;
      e.b.vx -= dx * f; e.b.vy -= dy * f;
    });
    nodes.forEach(function (n) {
      n.vx += -n.px * 0.0035; n.vy += -n.py * 0.0035;
      if (!n.fixed) { n.px += n.vx; n.py += n.vy; }
      n.vx *= 0.86; n.vy *= 0.86;
    });
  }

  function w2s(x, y) { return [view.x + x * view.k + W / 2, view.y + y * view.k + H / 2]; }
  function s2w(x, y) { return [(x - W / 2 - view.x) / view.k, (y - H / 2 - view.y) / view.k]; }

  var hover = null, selected = null, dragged = null, panning = false, lastM = [0, 0], moved = 0;

  function draw() {
    tick();
    ctx.clearRect(0, 0, W, H);
    // 边
    edges.forEach(function (e) {
      if (off[e.a.d] || off[e.b.d]) return;
      var p1 = w2s(e.a.px, e.a.py), p2 = w2s(e.b.px, e.b.py);
      var hot = hover && (hover === e.a || hover === e.b) || selected && (selected === e.a || selected === e.b);
      ctx.beginPath();
      var mx = (p1[0] + p2[0]) / 2, my = (p1[1] + p2[1]) / 2;
      var nx = -(p2[1] - p1[1]), ny = p2[0] - p1[0];
      var nl = Math.sqrt(nx * nx + ny * ny) || 1;
      var bow = e.t === 'rel' ? 10 : 5;
      ctx.moveTo(p1[0], p1[1]);
      ctx.quadraticCurveTo(mx + nx / nl * bow, my + ny / nl * bow, p2[0], p2[1]);
      ctx.strokeStyle = hot ? '#2563eb' : (e.t === 'pre' ? 'rgba(90,110,140,.4)' : 'rgba(140,150,165,.22)');
      ctx.lineWidth = hot ? 1.8 : 1.1;
      ctx.setLineDash(e.t === 'rel' ? [4, 4] : []);
      ctx.stroke();
      ctx.setLineDash([]);
      if (e.t === 'pre') { // 箭头
        var ang = Math.atan2(p2[1] - (my + ny / nl * bow), p2[0] - (mx + nx / nl * bow));
        var rr = (11 + Math.max(e.b.deg, 3) * 0.7) * view.k;
        ctx.beginPath();
        ctx.moveTo(p2[0], p2[1]);
        ctx.lineTo(p2[0] - 8 * Math.cos(ang - 0.42), p2[1] - 8 * Math.sin(ang - 0.42));
        ctx.lineTo(p2[0] - 8 * Math.cos(ang + 0.42), p2[1] - 8 * Math.sin(ang + 0.42));
        ctx.closePath();
        ctx.fillStyle = hot ? '#2563eb' : 'rgba(90,110,140,.42)';
        ctx.fill();
      }
    });
    // 节点
    nodes.forEach(function (n) {
      if (off[n.d]) return;
      var p = w2s(n.px, n.py);
      var rad = (10 + Math.max(n.deg, 3) * 0.85) * view.k;
      var hot = hover === n || selected === n;
      var dim = (hover || selected) && !hot &&
        !edges.some(function (e) { return (e.a === (hover || selected) && e.b === n) || (e.b === (hover || selected) && e.a === n); });
      ctx.beginPath();
      ctx.arc(p[0], p[1], rad + (hot ? 2.5 : 0), 0, Math.PI * 2);
      ctx.fillStyle = DOMAINS[n.d][1];
      ctx.globalAlpha = dim ? 0.25 : 1;
      ctx.fill();
      ctx.globalAlpha = 1;
      if (hot) { ctx.strokeStyle = '#16191d'; ctx.lineWidth = 1.6; ctx.stroke(); }
      ctx.fillStyle = dim ? 'rgba(80,90,105,.35)' : '#3c4552';
      ctx.font = (hot ? '600 ' : '') + Math.max(11, 11.5 * Math.min(view.k, 1.15)) + 'px -apple-system,PingFang SC,sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(n.l, p[0], p[1] + rad + 13);
    });
    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);

  function pick(mx, my) {
    var best = null, bd = 1e9;
    nodes.forEach(function (n) {
      if (off[n.d]) return;
      var p = w2s(n.px, n.py);
      var rad = (10 + Math.max(n.deg, 3) * 0.85) * view.k;
      var d = Math.hypot(mx - p[0], my - p[1]);
      if (d < rad + 6 && d < bd) { best = n; bd = d; }
    });
    return best;
  }

  var panel = document.getElementById('npanel');
  function showPanel(n) {
    if (!n) { panel.hidden = true; return; }
    var pre = edges.filter(function (e) { return e.b === n && e.t === 'pre'; }).map(function (e) { return e.a; });
    var nxt = edges.filter(function (e) { return e.a === n && e.t === 'pre'; }).map(function (e) { return e.b; });
    var h = '<button class="np-close" type="button" aria-label="关闭">✕</button>' +
      '<h3><span class="np-dot" style="background:' + DOMAINS[n.d][1] + '"></span>' + n.l +
      '<span class="np-lv">' + n.lv + '</span></h3>' +
      '<div class="np-desc">' + n.x + '</div>';
    if (pre.length) h += '<div class="np-sec">建议先学</div>' + pre.map(function (m) {
      return '<button class="np-link nav-n" data-id="' + m.id + '" type="button">' + m.l + '</button>';
    }).join('');
    if (nxt.length) h += '<div class="np-sec">下一步</div>' + nxt.map(function (m) {
      return '<button class="np-link nav-n" data-id="' + m.id + '" type="button">' + m.l + '</button>';
    }).join('');
    h += '<div class="np-sec">对应内容</div>' + n.r.map(function (r) {
      return '<a class="np-link" href="' + r.u + '">' + r.t + '</a>';
    }).join('');
    panel.innerHTML = h;
    panel.hidden = false;
    panel.querySelector('.np-close').addEventListener('click', function () { selected = null; panel.hidden = true; });
    panel.querySelectorAll('.nav-n').forEach(function (b) {
      b.addEventListener('click', function () { var t = byId[b.getAttribute('data-id')]; selected = t; showPanel(t); });
    });
  }

  canvas.addEventListener('mousemove', function (ev) {
    var rect = canvas.getBoundingClientRect();
    var mx = ev.clientX - rect.left, my = ev.clientY - rect.top;
    if (dragged) {
      var w = s2w(mx, my);
      dragged.px = w[0]; dragged.py = w[1]; dragged.vx = dragged.vy = 0;
      moved++; return;
    }
    if (panning) { view.x += mx - lastM[0]; view.y += my - lastM[1]; lastM = [mx, my]; return; }
    hover = pick(mx, my);
    canvas.style.cursor = hover ? 'pointer' : 'grab';
  });
  canvas.addEventListener('mousedown', function (ev) {
    var rect = canvas.getBoundingClientRect();
    var mx = ev.clientX - rect.left, my = ev.clientY - rect.top;
    var n = pick(mx, my);
    moved = 0;
    if (n) { dragged = n; selected = n; showPanel(n); }
    else { panning = true; selected = null; panel.hidden = true; }
    lastM = [mx, my];
    canvas.classList.add('grabbing');
  });
  window.addEventListener('mouseup', function () {
    dragged = null; panning = false; canvas.classList.remove('grabbing');
  });
  canvas.addEventListener('wheel', function (ev) {
    ev.preventDefault();
    var rect = canvas.getBoundingClientRect();
    var mx = ev.clientX - rect.left, my = ev.clientY - rect.top;
    var k2 = Math.min(2.2, Math.max(0.45, view.k * (ev.deltaY < 0 ? 1.08 : 0.925)));
    var w = s2w(mx, my);
    view.k = k2;
    view.x = mx - W / 2 - w[0] * view.k;
    view.y = my - H / 2 - w[1] * view.k;
  }, { passive: false });
  canvas.addEventListener('click', function (ev) {
    if (moved > 4) return;
    var rect = canvas.getBoundingClientRect();
    var n = pick(ev.clientX - rect.left, ev.clientY - rect.top);
    if (n) { selected = n; showPanel(n); }
  });
})();
