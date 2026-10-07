// The blinded TR1 3x2pt + kappa data vector, drawn live (house data-app), with
// toggles between the shear methods and CMB lensing surveys that have been measured.
//
// One drawing, one camera. The drawing is the whole data vector as a lower
// triangle of panels (columns gamma_1..6 then delta_1..6, kappa at the base),
// in which the kappa row's panels are the detailed ones, with their residual
// strips. A single matrix on one group is the camera; the three rest states are
// three cameras:
//   0  close on the kappa row's source-bin half: gamma_i x kappa
//   1  the same zoom, panned right to its lens-bin half: delta_i x kappa
//   2  pulled back to the whole triangle
// The camera's x and y scales differ (the row is seen taller than it sits in
// the triangle); strokes do not scale (vector-effect), so points stay round.
// Labels live outside the drawing, are placed from the camera on every frame,
// and fade as functions of the camera alone, so any camera, at rest or in
// flight, draws the same way. In state 2 a cell lights under the pointer and a
// click opens it as a detailed panel (Esc or a click outside closes it).
// Plain SVG attributes and requestAnimationFrame only; a do-nothing Web
// Animation is the clock, so finishing it (as the house checker does) lands the
// step, and without Web Animations a step is instant.
// A toggle rebuilds the drawing from another variant and lands it on the current step.
// Data: private/dv_vector.json from private/make_dv_vector.py (blind cmbx_dr1_a).
House.app('dv_vector', function (figure, data, ctx) {
  'use strict';
  var T0 = performance.now();
  var NS = 'http://www.w3.org/2000/svg';
  var W = 1712, H = 771;                         // the figure layout's whole body
  var PAN_MS = 900, ZOOM_MS = 1500;
  var frameEl = figure.querySelector('.frame');

  // the clock: a Web Animation that does nothing; finishing it lands the step
  var tick = document.createElement('span');
  tick.setAttribute('aria-hidden', 'true');
  tick.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden;';
  frameEl.appendChild(tick);

  // the toggles step aside while a detail card is open
  function cardShown(on) { if (ui) ui.style.visibility = on ? 'hidden' : 'visible'; }

  function scene(pairs, vk) {
  var shearName = data.shears[vk.split('|')[0]], cmbName = data.cmbs[vk.split('|')[1]];

  // ── data ────────────────────────────────────────────────────────────────
  var sym = function (t) { return t === 'kappa' ? ['κ'] : [t[0] === 'l' ? 'γ' : 'δ', +t.slice(1) + 1]; };
  var name = function (t) { return t === 'kappa' ? 'CMB lensing' : (t[0] === 'l' ? 'source bin ' : 'lens bin ') + (+t.slice(1) + 1); };
  var L0 = Math.log10(100 / 1.12), L1 = Math.log10(3000 * 1.12);
  var ux = function (ell) { return (Math.log10(ell) - L0) / (L1 - L0); };
  var fam = {};
  Object.keys(pairs).forEach(function (k) {
    var p = pairs[k];
    p.key = k;
    var m = 0;
    p.ell.forEach(function (l, i) { m = Math.max(m, Math.abs(l * p.th[i])); });
    p.e = -Math.floor(Math.log10(m));
    var f = Math.pow(10, p.e);
    p.v = p.ell.map(function (l, i) { return l * p.cl[i] * f; });
    p.s = p.ell.map(function (l, i) { return l * p.sig[i] * f; });
    p.t = p.ell.map(function (l, i) { return l * p.th[i] * f; });
    p.r = p.cl.map(function (c, i) { return (c - p.th[i]) / p.sig[i]; });
    p.x = p.ell.map(ux);
    p.nfit = p.fit.reduce(function (a, b) { return a + b; }, 0);
    var edge = function (i) { return i <= 0 ? 0 : i >= p.ell.length ? 1 : (p.x[i - 1] + p.x[i]) / 2; };
    p.cuts = [];
    for (var i = 0; i < p.fit.length; i++) {
      if (p.fit[i]) continue;
      var j = i;
      while (j + 1 < p.fit.length && !p.fit[j + 1]) j++;
      p.cuts.push([edge(i), edge(j + 1)]);
      i = j;
    }
    fam[p.family] = Math.min(fam[p.family] == null ? 99 : fam[p.family], p.e);
  });

  var nice = function (lo, hi, n) {
    var raw = (hi - lo) / (n || 4), mag = Math.pow(10, Math.floor(Math.log10(raw)));
    var step = [1, 2, 2.5, 5, 10].map(function (m) { return m * mag; }).filter(function (s) { return s >= raw; })[0];
    var out = [];
    for (var v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(Math.round(v / step) * step);
    return out;
  };
  var fmt = function (v) { return (Math.abs(v) < 1e-9 ? '0' : String(+v.toPrecision(3))).replace('-', '−'); };
  // a small panel's y-range: the fiducial and the bands inside the cut
  var quietRange = function (p) {
    var lo = 0, hi = 0;
    p.t.forEach(function (t) { lo = Math.min(lo, t); hi = Math.max(hi, t); });
    p.v.forEach(function (v, i) { if (p.fit[i]) { lo = Math.min(lo, v - p.s[i]); hi = Math.max(hi, v + p.s[i]); } });
    var span = hi - lo || 1;
    return [lo - 0.22 * span, hi + 0.3 * span];
  };
  // the kappa row's shared y-range per half: every band and its error bar
  var fullRange = function (list) {
    var lo = 0, hi = 0;
    list.forEach(function (p) {
      var k = Math.pow(10, fam[p.family] - p.e);
      p.v.forEach(function (v, i) { lo = Math.min(lo, (v - p.s[i]) * k); hi = Math.max(hi, (v + p.s[i]) * k); });
    });
    var span = hi - lo;
    return [lo - 0.05 * span, hi + 0.3 * span];
  };

  // ── svg helpers ─────────────────────────────────────────────────────────
  var el = function (tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    for (var a in attrs) if (attrs[a] != null) n.setAttribute(a, attrs[a]);
    if (parent) parent.appendChild(n);
    return n;
  };
  // text with sub- and superscripts (parts: strings or [text, 'sub'|'sup']),
  // shifted with dy, which every engine supports
  var text = function (parent, x, y, parts, o) {
    o = o || {};
    var size = o.size || 28;
    var t = el('text', { x: x, y: y, 'font-size': size, 'text-anchor': o.anchor || 'start',
      transform: o.rotate ? 'rotate(-90 ' + x + ' ' + y + ')' : null, 'class': o.cls || null }, parent);
    if (o.italic) t.setAttribute('font-style', 'italic');
    var shift = 0;
    (Array.isArray(parts) ? parts : [parts]).forEach(function (part) {
      var s = el('tspan', {}, t), want = 0;
      if (Array.isArray(part)) {
        s.textContent = part[0];
        if (part[1] === 'it' || part[2]) s.setAttribute('font-style', 'italic');
        if (part[1] === 'sub' || part[1] === 'sup') {
          s.setAttribute('font-size', Math.max(24, Math.round(size * 0.72)));
          want = part[1] === 'sub' ? 0.22 * size : -0.4 * size;
        }
      } else s.textContent = part;
      if (want !== shift) { s.setAttribute('dy', want - shift); shift = want; }
    });
    return t;
  };
  // a tracer as math: a Greek letter with its bin as a subscript (upright: the
  // deck face's italic delta is a partial-derivative sign)
  var symParts = function (t) { var s = sym(t); return s.length > 1 ? [s[0], [String(s[1]), 'sub']] : s; };

  var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, 'class': 'app-view', role: 'img',
    'aria-label': 'The blinded TR1 ' + shearName + ' by ' + cmbName + ' 3x2pt plus CMB lensing data vector' });
  el('style', {}, svg).textContent = [
    '.dvv-pt { fill: none; stroke-linecap: round; vector-effect: non-scaling-stroke; stroke-width: var(--dvv-dot, 8px); }',
    '.dvv-halo { fill: none; stroke-linecap: round; vector-effect: non-scaling-stroke; stroke: var(--ground); stroke-width: calc(var(--dvv-dot, 8px) + 3px); }',
    '.dvv-bar { fill: none; vector-effect: non-scaling-stroke; stroke-width: var(--dvv-bar, 2px); }',
    '.dvv-line { fill: none; vector-effect: non-scaling-stroke; stroke-width: var(--dvv-line, 2.2px); stroke-linejoin: round; }',
    '.dvv-spine { fill: none; vector-effect: non-scaling-stroke; stroke: var(--muted); stroke-width: 1.3px; stroke-opacity: var(--dvv-spine, 1); }',
    '.dvv-tick { fill: none; stroke: var(--muted); stroke-width: 1.3px; }',
    '.dvv-in { stroke: var(--cobalt); } .dvv-out { stroke: #A9B0BB; } .dvv-th { stroke: var(--ink); }',
    '.dvv-cut { fill: #8E99A9; fill-opacity: 0.14; }',
    '.dvv-b2 { fill: var(--rule); fill-opacity: 0.22; } .dvv-b1 { fill: var(--rule); fill-opacity: 0.5; }',
    '.dvv-zero { stroke: var(--rule); vector-effect: non-scaling-stroke; stroke-width: 1.3px; }',
    '.dvv-muted { fill: var(--muted); }',
    '.dvv-ground { fill: var(--ground); }',
    '.dvv-hit { fill: transparent; cursor: pointer; }',
    '.dvv-hl { fill: none; stroke: var(--accent); stroke-width: 3px; pointer-events: none; }',
    '.dvv-card { fill: var(--ground); stroke: var(--rule); stroke-width: 1.5px; }',
    '.dvv-shadow { fill: #1E2A40; fill-opacity: 0.07; }',
  ].join('\n');
  var defs = el('defs', {}, svg);
  var clip = el('clipPath', { id: 'dvv-unit', clipPathUnits: 'userSpaceOnUse' }, defs);
  el('rect', { x: 0, y: -0.01, width: 1, height: 1.02 }, clip);

  // a point: a vertical segment far shorter than a pixel, so its round caps
  // draw a dot in every engine (a zero-length one is a dash in Firefox)
  var dot = function (x, y, eps) { return 'M' + x + ' ' + (y - eps) + ' V' + (y + eps); };
  // a panel's data box and residual strip, in unit coordinates
  var drawData = function (g, p, ylim) {
    p.cuts.forEach(function (c) { el('rect', { x: c[0], y: 0, width: c[1] - c[0], height: 1, 'class': 'dvv-cut' }, g); });
    var inner = el('g', { transform: 'translate(0 ' + (ylim[1] / (ylim[1] - ylim[0])) + ') scale(1 ' + (-1 / (ylim[1] - ylim[0])) + ')' },
      el('g', { 'clip-path': 'url(#dvv-unit)' }, g));
    el('path', { d: 'M0 0 H1', 'class': 'dvv-zero' }, inner);
    el('path', { d: 'M' + p.x.map(function (x, i) { return x + ' ' + p.t[i]; }).join(' L'), 'class': 'dvv-line dvv-th' }, inner);
    var eps = 1e-4 * (ylim[1] - ylim[0]);
    ['out', 'in'].forEach(function (which) {
      var bars = '', pts = '';
      p.x.forEach(function (x, i) {
        if (!!p.fit[i] !== (which === 'in')) return;
        bars += 'M' + x + ' ' + (p.v[i] - p.s[i]) + ' V' + (p.v[i] + p.s[i]);
        pts += dot(x, p.v[i], eps);
      });
      if (bars) el('path', { d: bars, 'class': 'dvv-bar dvv-' + which }, inner);
      if (pts) { el('path', { d: pts, 'class': 'dvv-halo' }, inner); el('path', { d: pts, 'class': 'dvv-pt dvv-' + which }, inner); }
    });
    el('path', { d: 'M0 0 V1 H1', 'class': 'dvv-spine' }, g);
  };
  var R = 3.9;
  var drawResid = function (g, p) {
    var y = function (r) { return (R - r) / (2 * R); };
    el('rect', { x: 0, y: y(2), width: 1, height: y(-2) - y(2), 'class': 'dvv-b2' }, g);
    el('rect', { x: 0, y: y(1), width: 1, height: y(-1) - y(1), 'class': 'dvv-b1' }, g);
    p.cuts.forEach(function (c) { el('rect', { x: c[0], y: 0, width: c[1] - c[0], height: 1, 'class': 'dvv-cut' }, g); });
    el('path', { d: 'M0 ' + y(0) + ' H1', 'class': 'dvv-zero' }, g);
    ['out', 'in'].forEach(function (which) {
      var pts = '';
      p.x.forEach(function (x, i) {
        if (!!p.fit[i] !== (which === 'in')) return;
        if (!p.fit[i] && Math.abs(p.r[i]) >= R - 0.2) return;              // excluded, beyond the strip: left off
        pts += dot(x, y(Math.max(-(R - 0.2), Math.min(R - 0.2, p.r[i]))), 1e-4);   // in the cut: on its edge
      });
      if (pts) el('path', { d: pts, 'class': 'dvv-pt dvv-' + which }, g);
    });
    el('path', { d: 'M0 0 V1 H1', 'class': 'dvv-spine' }, g);
  };
  var unitBox = function (parent, r) {
    return el('g', { transform: 'translate(' + r.x + ' ' + r.y + ') scale(' + r.w + ' ' + r.h + ')' }, parent);
  };
  var ylabel = function (e) { return ['ℓ', ['C', 'it'], ['ℓ', 'sub'], '  [10', ['−' + e, 'sup'], ']']; };
  var rlabel = ['Δ/', ['σ', 'it']];

  // ── keys (legends): a swatch before each label ──────────────────────────
  var LABEL = { pt: ['blinded data ± ', ['σ', 'it']], th: 'fiducial model', cut: 'outside the scale cut' };
  var swatch = function (g, x, y, kind) {
    if (kind === 'pt') {
      el('path', { d: 'M' + x + ' ' + (y - 24) + ' v28', 'class': 'dvv-bar dvv-in', style: 'stroke-width:2px' }, g);
      el('path', { d: dot(x, y - 10, 0.01), 'class': 'dvv-pt dvv-in', style: 'stroke-width:8px' }, g);
    } else if (kind === 'th') el('path', { d: 'M' + (x - 16) + ' ' + (y - 10) + ' h32', 'class': 'dvv-line dvv-th', style: 'stroke-width:2.2px' }, g);
    else el('rect', { x: x - 16, y: y - 26, width: 32, height: 32, rx: 3, 'class': 'dvv-cut' }, g);
  };
  var keys = [];
  // right-aligned on one line (right, y), or stacked from its top left (stack)
  var drawKey = function (k) {
    if (k.done) return;
    if (k.stack) {
      k.items.forEach(function (it, i) {
        swatch(k.g, k.stack.x + 16, k.stack.y + i * 44, it);
        text(k.g, k.stack.x + 44, k.stack.y + i * 44, LABEL[it], { size: 26 });
      });
      k.done = true;
      return;
    }
    if (k.left != null) {
      var lx = k.left;
      for (var j = 0; j < k.items.length; j++) {
        var lt = text(k.g, lx + 40, k.y, LABEL[k.items[j]], { size: 26 });
        var lw = lt.getComputedTextLength();
        if (!lw) { while (k.g.firstChild) k.g.removeChild(k.g.firstChild); return; }
        swatch(k.g, lx + 16, k.y, k.items[j]);
        lx += 40 + lw + 44;
      }
      k.done = true;
      return;
    }
    var x = k.right;
    for (var i = k.items.length - 1; i >= 0; i--) {
      var t = text(k.g, x, k.y, LABEL[k.items[i]], { size: 26, anchor: 'end' });
      var w = t.getComputedTextLength();
      if (!w) { while (k.g.firstChild) k.g.removeChild(k.g.firstChild); return; }   // not rendered yet
      swatch(k.g, x - w - 24, k.y, k.items[i]);
      x -= w + 24 + 16 + 44;
    }
    k.done = true;
  };

  // ── the drawing: the triangle, with the kappa row as detailed panels ─────
  var GX = 58, GY = 2, KG = 14, LAB = 42, HK = 100;
  var CP = (W - GX - 2) / 12, CW = CP - 10;
  var RP = (H - GY - KG - HK - LAB) / 12, CH = RP - 7;
  var cell = function (row, col) {
    return row === 12 ? { x: GX + col * CP, y: GY + 12 * RP + KG, w: CW, h: HK } : { x: GX + col * CP, y: GY + row * RP, w: CW, h: CH };
  };
  // close up, the kappa row is seen at (SX, SY): main 440 and strip 162 tall,
  // six panels between LEFT and the right edge
  var LEFT = 118, MAIN = { y: 70, h: 440 }, SGAP = 12, STRIP = 162;
  var SX = (W - 8 - LEFT) / (5 * CP + CW), SY = (MAIN.h + SGAP + STRIP) / HK;
  var close = function (half) { var c = cell(12, 6 * half); return { sx: SX, sy: SY, tx: LEFT - SX * c.x, ty: MAIN.y - SY * c.y }; };
  var CAMS = [close(0), close(1), { sx: 1, sy: 1, tx: 0, ty: 0 }];

  var TR = ['l0', 'l1', 'l2', 'l3', 'l4', 'l5', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5'];
  var keyOf = function (a, b) {
    if (a === 'kappa') return 'kappa_' + b;
    var rank = function (t) { return (t[0] === 'g' ? 0 : 10) + +t.slice(1); };
    return rank(a) <= rank(b) ? a + '_' + b : b + '_' + a;
  };
  var cells = [];
  TR.forEach(function (a, r) { TR.slice(0, r + 1).forEach(function (b, c) { cells.push({ key: keyOf(a, b), row: r, col: c, a: a, b: b }); }); });
  TR.forEach(function (b, c) { cells.push({ key: keyOf('kappa', b), row: 12, col: c, a: 'kappa', b: b }); });
  var rowYlim = {
    LK: fullRange([0, 1, 2, 3, 4, 5].map(function (i) { return pairs['kappa_l' + i]; })),
    GK: fullRange([0, 1, 2, 3, 4, 5].map(function (i) { return pairs['kappa_g' + i]; })),
  };
  var kparts = function (c) {   // a kappa cell's main box and strip, in drawing coordinates
    var r = cell(12, c.col), hm = MAIN.h / SY, hg = SGAP / SY;
    return { main: { x: r.x, y: r.y, w: r.w, h: hm }, strip: { x: r.x, y: r.y + hm + hg, w: r.w, h: STRIP / SY } };
  };

  var world = el('g', {}, svg);
  var tint = el('rect', { x: cell(12, 0).x - 6, y: cell(12, 0).y - 5, width: 11 * CP + CW + 12, height: HK + 10, rx: 4 }, world);
  tint.style.fill = 'var(--rule)';
  cells.forEach(function (c) {
    var p = pairs[c.key];
    if (c.row < 12) { drawData(unitBox(world, cell(c.row, c.col)), p, quietRange(p)); return; }
    var k = Math.pow(10, fam[p.family] - p.e), kp = kparts(c);
    drawData(unitBox(world, kp.main), p, rowYlim[p.family].map(function (v) { return v / k; }));
    drawResid(unitBox(world, kp.strip), p);
  });

  // ── labels, placed from the camera ──────────────────────────────────────
  var labels = [];   // { el, at(cam) -> [x, y] or null, op(z, p, cam) -> opacity }
  var smooth = function (a, b, x) { var t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
  var closeOp = function (z) { return 1 - smooth(0, 0.3, z); };      // close-up labels on the panels leave early
  var fixedOp = function (z) { return 1 - smooth(0, 0.035, z); };    // those fixed to the screen leave at once
  var farOp = function (z) { return smooth(0.62, 1, z); };           // triangle labels arrive late
  var sx = function (cam, x) { return cam.tx + cam.sx * x; };
  var sy = function (cam, y) { return cam.ty + cam.sy * y; };
  var inView = function (cam, c) {                                    // a kappa cell clear of the gutter
    var x0 = sx(cam, cell(12, c.col).x), x1 = x0 + cam.sx * CW;
    return x1 > LEFT - 1 && x0 < W + 1;
  };
  var label = function (node, at, op) { labels.push({ el: node, at: at, op: op }); return node; };

  // per kappa panel: its pair as math, ticks on both axes (majors labelled under
  // the strip, minors bare), and the multipole label
  var MAJOR = [100, 1000], MINOR = [200, 300, 400, 500, 600, 700, 800, 900, 2000, 3000];
  var yTicks = function (yl) { return nice(yl[0], yl[1] - 0.12 * (yl[1] - yl[0]), 3); };
  var near = el('g', {}, svg);
  cells.filter(function (c) { return c.row === 12; }).forEach(function (c) {
    var kp = kparts(c), yl = rowYlim[pairs[c.key].family];
    var n = text(near, 0, 0, [].concat(symParts(c.b), ['κ']), { size: 34, anchor: 'end' });
    label(n, function (cam) { return [sx(cam, kp.main.x + kp.main.w) - 14, sy(cam, kp.main.y) + 40]; },
      function (z, p, cam) { return inView(cam, c) ? closeOp(z) : 0; });
    var ticks = el('path', { 'class': 'dvv-tick' }, near);
    label(ticks, null, function (z, p, cam) {
      var d = '', yb = sy(cam, kp.strip.y + kp.strip.h), xl = sx(cam, kp.main.x);
      MAJOR.forEach(function (l) { d += 'M' + sx(cam, kp.strip.x + kp.strip.w * ux(l)) + ' ' + yb + ' v9'; });
      MINOR.forEach(function (l) { d += 'M' + sx(cam, kp.strip.x + kp.strip.w * ux(l)) + ' ' + yb + ' v5'; });
      yTicks(yl).forEach(function (v) {
        d += 'M' + xl + ' ' + sy(cam, kp.main.y + kp.main.h * (yl[1] - v) / (yl[1] - yl[0])) + ' h-7';
      });
      [-2, 2].forEach(function (r) { d += 'M' + xl + ' ' + sy(cam, kp.strip.y + kp.strip.h * (R - r) / (2 * R)) + ' h-7'; });
      ticks.setAttribute('d', d);
      return inView(cam, c) ? closeOp(z) : 0;
    });
    MAJOR.forEach(function (l) {
      var t = text(near, 0, 0, String(l), { size: 26, anchor: 'middle', cls: 'dvv-muted' });
      label(t, function (cam) { return [sx(cam, kp.strip.x + kp.strip.w * ux(l)), sy(cam, kp.strip.y + kp.strip.h) + 36]; },
        function (z, p, cam) { return inView(cam, c) ? closeOp(z) : 0; });
    });
    var ell = text(near, 0, 0, [['ℓ', 'it']], { size: 30, anchor: 'middle' });
    label(ell, function (cam) { return [sx(cam, kp.strip.x + kp.strip.w / 2), sy(cam, kp.strip.y + kp.strip.h) + 74]; },
      function (z, p, cam) { return inView(cam, c) ? closeOp(z) : 0; });
  });
  // the gutter: a quiet column for the y axes, the panels sliding beneath it
  var gutter = el('g', {}, svg);
  el('rect', { x: -2, y: 0, width: LEFT - 8, height: H, 'class': 'dvv-ground' }, gutter);
  label(gutter, null, function (z) { return fixedOp(z); });
  [['l', 'LK'], ['g', 'GK']].forEach(function (h, half) {
    var g = el('g', {}, svg), yl = rowYlim[h[1]];
    var Y = function (v) { return MAIN.y + MAIN.h * (yl[1] - v) / (yl[1] - yl[0]); };
    var RY = function (r) { return MAIN.y + MAIN.h + SGAP + STRIP * (R - r) / (2 * R); };
    var d = '';
    yTicks(yl).forEach(function (v) {
      d += 'M' + (LEFT - 8) + ' ' + Y(v) + ' h8';
      text(g, LEFT - 14, Y(v) + 9, fmt(v), { size: 26, anchor: 'end', cls: 'dvv-muted' });
    });
    [-2, 2].forEach(function (r) {
      d += 'M' + (LEFT - 8) + ' ' + RY(r) + ' h8';
      text(g, LEFT - 14, RY(r) + 9, (r > 0 ? '+' : '−') + '2', { size: 26, anchor: 'end', cls: 'dvv-muted' });
    });
    el('path', { d: d, 'class': 'dvv-tick' }, g);
    text(g, LEFT - 66, MAIN.y + MAIN.h / 2, ylabel(fam[h[1]]), { size: 30, anchor: 'middle', rotate: true });
    text(g, LEFT - 66, MAIN.y + MAIN.h + SGAP + STRIP / 2, rlabel, { size: 30, anchor: 'middle', rotate: true });
    label(g, null, function (z, p) { return fixedOp(z) * (half ? smooth(0.45, 0.6, p) : 1 - smooth(0.4, 0.55, p)); });
    // the half's key on the header line, left; the toggles sit on its right
    var key = el('g', {}, svg);
    keys.push({ g: key, left: LEFT - 8, y: 48, items: ['pt', 'th'].concat(half ? ['cut'] : []) });
    label(key, null, function (z, p) { return fixedOp(z) * (half ? smooth(0.5, 0.9, p) : 1 - smooth(0.1, 0.5, p)); });
  });

  // the triangle's labels: rows, columns, and in its empty corner the title,
  // counts, key, source and the click hint
  var far = el('g', {}, svg);
  var at = function (wx, wy) { return function (cam) { return [sx(cam, wx), sy(cam, wy)]; }; };
  TR.concat(['kappa']).forEach(function (t, i) {
    var c = cell(i, 0);
    label(text(far, 0, 0, symParts(t), { size: 28, anchor: 'end' }), at(GX - 14, c.y + c.h / 2 + 10), farOp);
  });
  TR.forEach(function (t, i) {
    var b = cell(12, i);
    label(text(far, 0, 0, symParts(t), { size: 28, anchor: 'middle' }), at(b.x + b.w / 2, b.y + b.h + 34), farOp);
  });
  var nb = 0, nf = 0;
  Object.keys(pairs).forEach(function (k) { nb += pairs[k].ell.length; nf += pairs[k].nfit; });
  var corner = el('g', {}, far);
  text(corner, cell(0, 2).x, cell(0, 0).y + 36, 'TR1 ' + shearName + ' × ' + cmbName, { size: 34 });
  text(corner, cell(1, 2).x, cell(1, 0).y + 34, Object.keys(pairs).length + ' spectra, ' + nb + ' bandpowers, ' + nf + ' inside the scale cut',
    { size: 26, cls: 'dvv-muted' });
  var tkey = el('g', {}, corner);
  keys.push({ g: tkey, items: ['pt', 'th', 'cut'], stack: { x: cell(0, 6).x + 40, y: cell(2, 0).y + 40 } });
  text(corner, W - 8, cell(6, 0).y + 34, 'click a panel to open it', { size: 24, anchor: 'end', cls: 'dvv-muted dvv-hint', italic: true });
  // the block keeps its shape and rides on the camera from its top-left anchor
  var PX = cell(0, 2).x, PY = cell(0, 0).y;
  label(corner, function (cam) { return [sx(cam, PX) - PX, sy(cam, PY) - PY]; }, farOp);

  // ── the camera ──────────────────────────────────────────────────────────
  var cam = { sx: 1, sy: 1, tx: 0, ty: 0 };
  var LZ = Math.log(SY);
  function render() {
    world.setAttribute('transform', 'matrix(' + cam.sx + ' 0 0 ' + cam.sy + ' ' + cam.tx + ' ' + cam.ty + ')');
    var z = Math.max(0, Math.min(1, (LZ - Math.log(cam.sy)) / LZ));                     // 0 close, 1 far
    var wx = (LEFT - cam.tx) / cam.sx, a = cell(12, 0).x, b = cell(12, 6).x;
    var p = Math.max(0, Math.min(1, (wx - a) / (b - a)));                                 // 0 source half, 1 lens half
    var mix = function (u, v) { return u + (v - u) * z; };
    svg.style.setProperty('--dvv-dot', mix(8, 4.5) + 'px');
    svg.style.setProperty('--dvv-bar', mix(2, 1.2) + 'px');
    svg.style.setProperty('--dvv-line', mix(2.2, 1.5) + 'px');
    svg.style.setProperty('--dvv-spine', mix(1, 0.4));
    tint.setAttribute('opacity', 0.5 * farOp(z));
    labels.forEach(function (l) {
      var o = l.op(z, p, cam);
      if (l.at && o > 0.001) {
        var q = l.at(cam);
        if (l.el.localName === 'text') { l.el.setAttribute('x', q[0]); l.el.setAttribute('y', q[1]); }
        else l.el.setAttribute('transform', 'translate(' + q[0] + ' ' + q[1] + ')');
      }
      l.el.setAttribute('opacity', o);
      l.el.style.visibility = o > 0.001 ? 'visible' : 'hidden';
    });
  }
  // between two cameras: the seen rectangle's centre moves straight, its size
  // changes geometrically, so a zoom reads as one steady pull
  var view = function (c) { return { x: -c.tx / c.sx, y: -c.ty / c.sy, w: W / c.sx, h: H / c.sy }; };
  var between = function (a, b, t) {
    var va = view(a), vb = view(b);
    var w = va.w * Math.pow(vb.w / va.w, t), h = va.h * Math.pow(vb.h / va.h, t);
    var cx = va.x + va.w / 2 + (vb.x + vb.w / 2 - va.x - va.w / 2) * t;
    var cy = va.y + va.h / 2 + (vb.y + vb.h / 2 - va.y - va.h / 2) * t;
    var s = { sx: W / w, sy: H / h };
    s.tx = -(cx - w / 2) * s.sx;
    s.ty = -(cy - h / 2) * s.sy;
    return s;
  };
  var ease = function (t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };

  var flight = null;
  function land(k) {
    if (flight) { var f = flight; flight = null; cancelAnimationFrame(f.raf); try { f.clock.cancel(); } catch (e) { /* gone */ } }
    cam = { sx: CAMS[k].sx, sy: CAMS[k].sy, tx: CAMS[k].tx, ty: CAMS[k].ty };
    render();
    svg.setAttribute('data-rest', k);              // at rest on step k (read by tests)
    hits.style.visibility = k === 2 ? 'visible' : 'hidden';
  }
  function fly(k) {
    var from = { sx: cam.sx, sy: cam.sy, tx: cam.tx, ty: cam.ty }, to = CAMS[k];
    var dur = Math.abs(Math.log(from.sy / to.sy)) > 1e-6 ? ZOOM_MS : PAN_MS;
    var clock;
    try { clock = tick.animate([{ opacity: 0 }, { opacity: 0 }], { duration: dur }); } catch (e) { clock = null; }
    if (!clock || !clock.finished) { land(k); return; }
    var f = { clock: clock, raf: 0 };
    flight = f;
    svg.removeAttribute('data-rest');
    hits.style.visibility = 'hidden';
    var frame = function () {
      if (flight !== f) return;
      var t = Math.min(1, (clock.currentTime || 0) / dur);
      if (t >= 1 || clock.playState === 'finished') { land(k); return; }
      cam = between(from, to, ease(t));
      render();
      f.raf = requestAnimationFrame(frame);
    };
    clock.finished.then(function () { if (flight === f) land(k); }, function () {});
    f.raf = requestAnimationFrame(frame);
  }

  // ── hover and the detail card (state 2) ─────────────────────────────────
  var hits = el('g', {}, svg), hl = el('rect', { 'class': 'dvv-hl', rx: 4 }, svg);
  hl.style.visibility = 'hidden';
  cells.forEach(function (c) {
    var r = cell(c.row, c.col);
    var h = el('rect', { x: r.x - 4, y: r.y - 3, width: r.w + 8, height: r.h + 6, 'class': 'dvv-hit' }, hits);
    h.addEventListener('pointerenter', function () {
      hl.setAttribute('x', r.x - 4); hl.setAttribute('y', r.y - 3); hl.setAttribute('width', r.w + 8); hl.setAttribute('height', r.h + 6);
      hl.style.visibility = 'visible';
    });
    h.addEventListener('pointerleave', function () { hl.style.visibility = 'hidden'; });
    h.addEventListener('click', function (e) { e.stopPropagation(); openCard(c); });
  });

  var card = null;
  var drawAxes = function (g, m, s, ylim) {
    var Y = function (v) { return m.y + m.h * (ylim[1] - v) / (ylim[1] - ylim[0]); };
    var RY = function (r) { return s.y + s.h * (R - r) / (2 * R); };
    var d = '';
    nice(ylim[0], ylim[1] - 0.12 * (ylim[1] - ylim[0]), 3).forEach(function (v) {
      d += 'M' + (m.x - 8) + ' ' + Y(v) + ' h8';
      text(g, m.x - 14, Y(v) + 9, fmt(v), { size: 26, anchor: 'end', cls: 'dvv-muted' });
    });
    [-2, 2].forEach(function (r) {
      d += 'M' + (s.x - 8) + ' ' + RY(r) + ' h8';
      text(g, s.x - 14, RY(r) + 9, (r > 0 ? '+' : '−') + '2', { size: 26, anchor: 'end', cls: 'dvv-muted' });
    });
    [100, 1000].forEach(function (l) {
      var x = s.x + s.w * ux(l);
      d += 'M' + x + ' ' + (s.y + s.h) + ' v9';
      text(g, x, s.y + s.h + 36, String(l), { size: 26, anchor: 'middle', cls: 'dvv-muted' });
    });
    [200, 300, 400, 500, 600, 700, 800, 900, 2000, 3000].forEach(function (l) { d += 'M' + (s.x + s.w * ux(l)) + ' ' + (s.y + s.h) + ' v5'; });
    el('path', { d: d, 'class': 'dvv-tick' }, g);
  };
  function onKey(e) { if (e.key === 'Escape' || e.key === 'Backspace') { closeCard(); e.preventDefault(); e.stopPropagation(); } }
  function onDown(e) { if (card && !card.box.contains(e.target)) { closeCard(); e.stopPropagation(); e.preventDefault(); } }
  function openCard(c) {
    var t0 = performance.now();
    closeCard();
    var p = pairs[c.key];
    var g = el('g', {}, svg);
    el('rect', { x: 0, y: 0, width: W, height: H, 'class': 'dvv-ground', opacity: 0.82 }, g);
    var box = el('g', {}, g);
    ['--dvv-dot', '--dvv-bar', '--dvv-line', '--dvv-spine'].forEach(function (v, i) { box.style.setProperty(v, ['8px', '2px', '2.2px', '1'][i]); });
    var B = { x: 140, y: 12, w: W - 280, h: H - 24 };
    el('rect', { x: B.x + 2, y: B.y + 6, width: B.w, height: B.h, rx: 16, 'class': 'dvv-shadow' }, box);
    el('rect', { x: B.x, y: B.y, width: B.w, height: B.h, rx: 14, 'class': 'dvv-card' }, box);
    text(box, B.x + 48, B.y + 60, [].concat(symParts(c.a), [' × '], symParts(c.b)), { size: 40 });
    var note = p.nfit === p.fit.length ? 'every band inside the validated linear-bias cut'
      : p.nfit === 0 ? 'every band outside the validated linear-bias cut'
      : p.nfit + ' of ' + p.fit.length + ' bands inside the validated linear-bias cut';
    text(box, B.x + 48, B.y + 100, name(c.a) + ' × ' + name(c.b) + ', blinded; ' + note, { size: 26, cls: 'dvv-muted' });
    var k = { g: el('g', {}, box), right: B.x + B.w - 40, y: B.y + 60, items: ['pt', 'th'].concat(p.nfit < p.fit.length ? ['cut'] : []) };
    drawKey(k);
    var m = { x: B.x + 150, y: B.y + 140, w: B.w - 196, h: 320 }, s = { x: m.x, y: m.y + m.h + 12, w: m.w, h: 132 };
    var lo = 0, hi = 0;
    p.t.forEach(function (t) { lo = Math.min(lo, t); hi = Math.max(hi, t); });
    p.v.forEach(function (v, i) {
      if (!p.fit[i] && Math.abs(p.r[i]) > 4) return;    // one far outside the cut would flatten the rest
      lo = Math.min(lo, v - p.s[i]); hi = Math.max(hi, v + p.s[i]);
    });
    var q = [lo - 0.06 * (hi - lo), hi + 0.1 * (hi - lo)];
    drawData(unitBox(box, m), p, q);
    drawResid(unitBox(box, s), p);
    drawAxes(box, m, s, q);
    text(box, m.x - 96, m.y + m.h / 2, ylabel(p.e), { size: 30, anchor: 'middle', rotate: true });
    text(box, s.x - 96, s.y + s.h / 2, rlabel, { size: 30, anchor: 'middle', rotate: true });
    text(box, m.x + m.w / 2, s.y + s.h + 72, [['ℓ', 'it']], { size: 30, anchor: 'middle' });
    // what the strip cannot show, said plainly
    var edge = [];
    p.r.forEach(function (r, i) { if (p.fit[i] && Math.abs(r) >= R - 0.2) edge.push((r > 0 ? '+' : '−') + Math.abs(r).toFixed(1)); });
    var off = p.r.filter(function (r, i) { return !p.fit[i] && Math.abs(r) >= R - 0.2; }).length;
    var says = edge.length ? ['on the strip edge, inside the cut: ' + edge.join(', '), [' σ', 'it']] : [];
    if (off) says.push((says.length ? '; ' : '') + off + (off > 1 ? ' bands' : ' band') + ' outside the cut lie beyond the strip');
    if (says.length) text(box, B.x + 48, B.y + B.h - 24, says, { size: 24, cls: 'dvv-muted', italic: true });
    text(box, B.x + B.w - 40, B.y + B.h - 24, 'Esc to close', { size: 24, anchor: 'end', cls: 'dvv-muted', italic: true });
    if (g.animate && !ctx.still()) try { g.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 160, easing: 'ease-out' }); } catch (e) { /* static */ }
    card = { g: g, box: box };
    cardShown(true);
    ctx.keyboard(false);
    document.addEventListener('keydown', onKey, true);
    document.addEventListener('pointerdown', onDown, true);
    svg.setAttribute('data-open-ms', (performance.now() - t0).toFixed(1));
  }
  function closeCard() {
    if (!card) return;
    svg.removeChild(card.g);
    card = null;
    cardShown(false);
    ctx.keyboard(true);
    document.removeEventListener('keydown', onKey, true);
    document.removeEventListener('pointerdown', onDown, true);
  }

  return {
    svg: svg, land: land, fly: fly, closeCard: closeCard, openCard: openCard, cells: cells,
    ready: function () { keys.forEach(drawKey); },
    hover: function (on) { if (!on) hl.style.visibility = 'hidden'; },
  };
  }

  // ── toggles: shear method and CMB survey; a variant not measured is shown but disabled
  var ui = document.createElementNS(NS, 'svg');
  ui.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
  ui.setAttribute('class', 'app-view dvv-ui');
  ui.style.pointerEvents = 'none';
  var uiStyle = document.createElementNS(NS, 'style');
  uiStyle.textContent = [
    '.dvv-seg { fill: var(--ground); stroke: var(--rule); stroke-width: 1.5px; }',
    '.dvv-seg-on { fill: var(--panel); stroke: var(--muted); }',
    '.dvv-seg-text { fill: var(--ink); }',
    '.dvv-seg-off .dvv-seg { stroke-dasharray: 4 4; } .dvv-seg-off .dvv-seg-text { fill: var(--muted); font-style: italic; }',
  ].join('\n');
  ui.appendChild(uiStyle);
  var uiDone = false;
  var sel = Object.keys(data.variants)[0].split('|');
  function drawUI() {
    while (ui.childNodes.length > 1) ui.removeChild(ui.lastChild);
    var x = W - 8, y = 18, h = 40, pad = 16, gap = 22;
    var groups = [['cmb', Object.keys(data.cmbs), data.cmbs], ['shear', Object.keys(data.shears), data.shears]];
    var ok = true;
    groups.forEach(function (gr) {
      for (var i = gr[1].length - 1; i >= 0; i--) {
        var id = gr[1][i];
        var want = gr[0] === 'cmb' ? sel[0] + '|' + id : id + '|' + sel[1];
        var on = gr[0] === 'cmb' ? sel[1] === id : sel[0] === id;
        var has = !!data.variants[want];
        var g = document.createElementNS(NS, 'g');
        ui.appendChild(g);
        var r = document.createElementNS(NS, 'rect');
        var t = document.createElementNS(NS, 'text');
        t.textContent = gr[2][id];
        t.setAttribute('font-size', 24);
        t.setAttribute('text-anchor', 'middle');
        g.appendChild(r); g.appendChild(t);
        var w = t.getComputedTextLength();
        if (!w) { ok = false; return; }
        w += 2 * pad;
        r.setAttribute('x', x - w); r.setAttribute('y', y); r.setAttribute('width', w); r.setAttribute('height', h);
        r.setAttribute('rx', 6);
        r.setAttribute('class', 'dvv-seg' + (on ? ' dvv-seg-on' : ''));
        t.setAttribute('x', x - w / 2); t.setAttribute('y', y + h / 2 + 8);
        t.setAttribute('class', 'dvv-seg-text');
        var tip = document.createElementNS(NS, 'title');
        tip.textContent = has ? gr[2][id] : gr[2][id] + ': not measured yet';
        g.appendChild(tip);
        if (!has) g.setAttribute('class', 'dvv-seg-off');
        else if (!on) {
          g.style.pointerEvents = 'auto';
          g.style.cursor = 'pointer';
          g.addEventListener('click', (function (vk) { return function (e) { e.stopPropagation(); use(vk); }; })(want));
        }
        x -= w - 1.5;
      }
      x -= gap;
    });
    uiDone = ok;
  }

  var S = null, state = null;
  function use(vk) {
    var next = scene(data.variants[vk], vk);
    if (S) { S.closeCard(); frameEl.replaceChild(next.svg, S.svg); }
    else frameEl.insertBefore(next.svg, ui);
    S = next;
    sel = vk.split('|');
    S.ready();
    S.land(state == null ? 0 : state);
    drawUI();
  }

  // ── steps ───────────────────────────────────────────────────────────────
  function step(k, animate) {
    k = Math.max(0, Math.min(2, k));
    S.ready();
    if (!uiDone) drawUI();
    if (k !== 2) { S.closeCard(); S.hover(false); }
    var from = state;
    state = k;
    if (!animate || from == null || from === k) { S.land(k); return; }
    if (ctx.still()) {
      // reduced motion: the old view, frozen, fades out over the new one
      var ghost = S.svg.cloneNode(true);
      Array.prototype.forEach.call(ghost.querySelectorAll('[id]'), function (n) { n.removeAttribute('id'); });
      ghost.style.pointerEvents = 'none';
      S.svg.parentNode.insertBefore(ghost, ui);
      S.land(k);
      var gone = function () { if (ghost.parentNode) ghost.parentNode.removeChild(ghost); };
      try { ghost.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 450, easing: 'ease-in-out', fill: 'forwards' }).finished.then(gone, gone); }
      catch (e) { gone(); }
      return;
    }
    S.fly(k);
  }

  frameEl.appendChild(ui);
  use(Object.keys(data.variants)[0]);
  S.svg.setAttribute('data-mount-ms', (performance.now() - T0).toFixed(1));
  return {
    step: step,
    leave: function () { S.closeCard(); },
    open: function (key) { var c = S.cells.filter(function (x) { return x.key === key; })[0]; if (c) S.openCard(c); },
  };
});
