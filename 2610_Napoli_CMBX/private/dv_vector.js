// The blinded TR1 x SPT-3G 3x2pt + kappa data vector, drawn live (house data-app).
//
// One scene, three rest states:
//   0  the kappa row, source bins: gamma_i x kappa, six detailed panels
//   1  the same row, panned right to the lens bins: delta_i x kappa
//   2  the whole vector, a lower triangle of 90 small panels with the kappa row
//      at its base (columns gamma_1..6 then delta_1..6, as the row pans)
// Every panel is one group drawn in unit coordinates and placed by a rect per
// state, so the pan and the zoom are tweens of those rects; strokes do not
// scale (vector-effect), so points stay round however a panel is stretched.
// In state 2 a cell lights up under the pointer and a click opens it as a
// detailed panel over the figure (Esc or a click outside closes it).
// Data: private/dv_vector.json from private/make_dv_vector.py (blind cmbx_dr1_a).
House.app('dv_vector', function (figure, data, ctx) {
  'use strict';
  var T0 = performance.now();
  var NS = 'http://www.w3.org/2000/svg';
  var W = 1712, H = 723;
  var PAN_MS = 1000, ZOOM_MS = 1400, EASE = 'cubic-bezier(0.65, 0, 0.35, 1)';

  // ── data ────────────────────────────────────────────────────────────────
  var sym = function (t) {
    if (t === 'kappa') return ['κ'];
    return [t[0] === 'l' ? 'γ' : 'δ', +t.slice(1) + 1];
  };
  var name = function (t) { return t === 'kappa' ? 'CMB lensing' : (t[0] === 'l' ? 'source bin ' : 'lens bin ') + (+t.slice(1) + 1); };
  var pairs = data.pairs;
  var L0 = Math.log10(100 / 1.12), L1 = Math.log10(3000 * 1.12);
  var ux = function (ell) { return (Math.log10(ell) - L0) / (L1 - L0); };

  // per pair: values scaled by 10^e so numbers on axes are of order one
  var fam = {};
  Object.keys(pairs).forEach(function (k) {
    var p = pairs[k];
    p.key = k;
    var m = 0;
    p.ell.forEach(function (l, i) { m = Math.max(m, Math.abs(l * p.th[i])); });
    p.e = -Math.floor(Math.log10(m));
    p.v = p.ell.map(function (l, i) { return l * p.cl[i] * Math.pow(10, p.e); });
    p.s = p.ell.map(function (l, i) { return l * p.sig[i] * Math.pow(10, p.e); });
    p.t = p.ell.map(function (l, i) { return l * p.th[i] * Math.pow(10, p.e); });
    p.r = p.cl.map(function (c, i) { return (c - p.th[i]) / p.sig[i]; });
    p.x = p.ell.map(ux);
    p.nfit = p.fit.reduce(function (a, b) { return a + b; }, 0);
    // excluded ell ranges, edges halfway (in log ell) between bands
    var edge = function (i) {
      if (i <= 0) return 0;
      if (i >= p.ell.length) return 1;
      return (p.x[i - 1] + p.x[i]) / 2;
    };
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
  // one exponent per family on the detailed row (shared axes)
  var famE = function (f) { return fam[f]; };

  var nice = function (lo, hi, n) {
    var raw = (hi - lo) / (n || 4), mag = Math.pow(10, Math.floor(Math.log10(raw)));
    var step = [1, 2, 2.5, 5, 10].map(function (m) { return m * mag; }).filter(function (s) { return s >= raw; })[0];
    var out = [];
    for (var v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(Math.round(v / step) * step);
    return out;
  };
  var fmt = function (v) {
    var s = Math.abs(v) < 1e-9 ? '0' : String(+v.toPrecision(3));
    return s.replace('-', '−');
  };
  // y-range of a small panel: the fiducial and the bands inside the cut, so an
  // excluded outlier is clipped at the edge rather than setting the scale
  var quietRange = function (p, scale) {
    scale = scale || 1;
    var lo = 0, hi = 0;
    p.t.forEach(function (t, i) { lo = Math.min(lo, t * scale); hi = Math.max(hi, t * scale); });
    p.v.forEach(function (v, i) {
      if (!p.fit[i]) return;
      lo = Math.min(lo, (v - p.s[i]) * scale); hi = Math.max(hi, (v + p.s[i]) * scale);
    });
    var span = hi - lo || 1;
    return [lo - 0.22 * span, hi + 0.3 * span];
  };
  // y-range of a detailed panel: every band and its error bar
  var fullRange = function (list, top) {
    var lo = 0, hi = 0;
    list.forEach(function (p) {
      var k = Math.pow(10, famE(p.family) - p.e);
      p.v.forEach(function (v, i) { lo = Math.min(lo, (v - p.s[i]) * k); hi = Math.max(hi, (v + p.s[i]) * k); });
    });
    var span = hi - lo;
    return [lo - 0.05 * span, hi + (top || 0.25) * span];
  };

  // ── svg helpers ─────────────────────────────────────────────────────────
  var el = function (tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    for (var a in attrs) if (attrs[a] != null) n.setAttribute(a, attrs[a]);
    if (parent) parent.appendChild(n);
    return n;
  };
  // text with sub- and superscripts: parts are strings or [text, 'sub'|'sup']
  var text = function (parent, x, y, parts, o) {
    o = o || {};
    var t = el('text', { x: x, y: y, 'font-size': o.size || 28, 'text-anchor': o.anchor || 'start',
      transform: o.rotate ? 'rotate(-90 ' + x + ' ' + y + ')' : null, 'class': o.cls || null }, parent);
    if (o.fill) t.style.fill = o.fill;
    if (o.italic) t.setAttribute('font-style', 'italic');
    (Array.isArray(parts) ? parts : [parts]).forEach(function (part) {
      var s = el('tspan', {}, t);
      if (Array.isArray(part)) {
        s.textContent = part[0];
        s.setAttribute('font-size', Math.max(24, Math.round((o.size || 28) * 0.8)));
        s.setAttribute('baseline-shift', part[1] === 'sub' ? '-22%' : '38%');
      } else s.textContent = part;
    });
    return t;
  };
  var symParts = function (t) { var s = sym(t); return s.length > 1 ? [s[0], [String(s[1]), 'sub']] : s; };
  var rectT = function (r) { return 'translate(' + r.x + 'px, ' + r.y + 'px) scale(' + r.w + ', ' + Math.max(r.h, 0.001) + ')'; };
  var ylimT = function (y) { return 'translate(0px, ' + (y[1] / (y[1] - y[0])) + 'px) scale(1, ' + (-1 / (y[1] - y[0])) + ')'; };

  var VARS = ['--dvv-dot', '--dvv-bar', '--dvv-line', '--dvv-spine'];
  var ROWW = ['11px', '2.4px', '3px', '1'], TRIW = ['5px', '1.4px', '2px', '0.4'];
  var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, 'class': 'app-view', role: 'img',
    'aria-label': 'The blinded TR1 by SPT-3G 3x2pt plus CMB lensing data vector' });
  var css = el('style', {}, svg);
  css.textContent = [
    '.dvv-pt { fill: none; stroke-linecap: round; vector-effect: non-scaling-stroke; stroke-width: var(--dvv-dot, 11px); }',
    '.dvv-bar { fill: none; vector-effect: non-scaling-stroke; stroke-width: var(--dvv-bar, 2.4px); }',
    '.dvv-line { fill: none; vector-effect: non-scaling-stroke; stroke-width: var(--dvv-line, 3px); stroke-linejoin: round; }',
    '.dvv-spine { fill: none; vector-effect: non-scaling-stroke; stroke: var(--muted); stroke-width: 1.4px; stroke-opacity: var(--dvv-spine, 1); }',
    '.dvv-in { stroke: var(--cobalt); } .dvv-out { stroke: #A1A9B5; }',
    '.dvv-th { stroke: var(--ochre); }',
    '.dvv-cut { fill: #8E99A9; fill-opacity: 0.17; }',
    '.dvv-b2 { fill: var(--rule); fill-opacity: 0.35; } .dvv-b1 { fill: var(--rule); fill-opacity: 0.6; }',
    '.dvv-zero { stroke: var(--muted); stroke-opacity: 0.5; vector-effect: non-scaling-stroke; stroke-width: 1.2px; }',
    '.dvv-muted { fill: var(--muted); }',
    '.dvv-hit { fill: transparent; cursor: pointer; }',
    '.dvv-hl { fill: none; stroke: var(--accent); stroke-width: 3px; pointer-events: none; }',
    '.dvv-card { fill: var(--ground); stroke: var(--rule); stroke-width: 1.5px; filter: drop-shadow(0 6px 18px rgba(20, 30, 50, 0.16)); }',
  ].join('\n');
  try {
    if (CSS.registerProperty && !window.__dvvProps) {
      window.__dvvProps = true;
      VARS.slice(0, 3).forEach(function (n, i) {
        CSS.registerProperty({ name: n, syntax: '<length>', inherits: true, initialValue: ROWW[i] });
      });
      CSS.registerProperty({ name: '--dvv-spine', syntax: '<number>', inherits: true, initialValue: '1' });
    }
  } catch (e) { /* already registered */ }
  var defs = el('defs', {}, svg);
  var clip = el('clipPath', { id: 'dvv-unit', clipPathUnits: 'userSpaceOnUse' }, defs);
  el('rect', { x: 0, y: -0.01, width: 1, height: 1.02 }, clip);

  // ── one panel: data box (and residual strip) in unit coordinates ─────────
  var drawData = function (g, p) {
    p.cuts.forEach(function (c) { el('rect', { x: c[0], y: 0, width: c[1] - c[0], height: 1, 'class': 'dvv-cut' }, g); });
    var clipped = el('g', { 'clip-path': 'url(#dvv-unit)' }, g);
    var inner = el('g', {}, clipped);
    var z = el('path', { d: 'M0 0 H1', 'class': 'dvv-zero' }, inner);
    var th = 'M' + p.x.map(function (x, i) { return x + ' ' + p.t[i]; }).join(' L');
    el('path', { d: th, 'class': 'dvv-line dvv-th' }, inner);
    ['out', 'in'].forEach(function (which) {
      var bars = '', pts = '';
      p.x.forEach(function (x, i) {
        if (!!p.fit[i] !== (which === 'in')) return;
        bars += 'M' + x + ' ' + (p.v[i] - p.s[i]) + ' V' + (p.v[i] + p.s[i]);
        pts += 'M' + x + ' ' + p.v[i] + ' h0';
      });
      if (bars) el('path', { d: bars, 'class': 'dvv-bar dvv-' + which }, inner);
      if (pts) el('path', { d: pts, 'class': 'dvv-pt dvv-' + which }, inner);
    });
    el('path', { d: 'M0 0 V1 H1', 'class': 'dvv-spine' }, g);
    return inner;
  };
  var drawResid = function (g, p) {
    var R = 3.9, y = function (r) { return (R - r) / (2 * R); };
    el('rect', { x: 0, y: y(2), width: 1, height: y(-2) - y(2), 'class': 'dvv-b2' }, g);
    el('rect', { x: 0, y: y(1), width: 1, height: y(-1) - y(1), 'class': 'dvv-b1' }, g);
    p.cuts.forEach(function (c) { el('rect', { x: c[0], y: 0, width: c[1] - c[0], height: 1, 'class': 'dvv-cut' }, g); });
    el('path', { d: 'M0 ' + y(0) + ' H1', 'class': 'dvv-zero' }, g);
    ['out', 'in'].forEach(function (which) {
      var pts = '';
      p.x.forEach(function (x, i) {
        if (!!p.fit[i] !== (which === 'in')) return;
        if (!p.fit[i] && Math.abs(p.r[i]) >= R - 0.2) return;              // excluded, beyond the strip: left off
        var r = Math.max(-(R - 0.2), Math.min(R - 0.2, p.r[i]));          // in the cut, beyond it: on its edge
        pts += 'M' + x + ' ' + y(r) + ' h0';
      });
      if (pts) el('path', { d: pts, 'class': 'dvv-pt dvv-' + which }, g);
    });
    el('path', { d: 'M0 0 V1 H1', 'class': 'dvv-spine' }, g);
  };

  // axes in screen coordinates for a detailed panel at rect m (and strip s)
  var drawAxes = function (g, m, s, ylim, o) {
    var Y = function (v) { return m.y + m.h * (ylim[1] - v) / (ylim[1] - ylim[0]); };
    var ticks = nice(ylim[0], ylim[1] - 0.12 * (ylim[1] - ylim[0]), 3);
    var d = '';
    ticks.forEach(function (v) {
      d += 'M' + (m.x - 8) + ' ' + Y(v) + ' h8';
      if (o.labels) text(g, m.x - 14, Y(v) + 9, fmt(v), { size: 26, anchor: 'end', cls: 'dvv-muted' });
    });
    var R = 3.9, RY = function (r) { return s.y + s.h * (R - r) / (2 * R); };
    [-2, 2].forEach(function (r) {
      d += 'M' + (s.x - 8) + ' ' + RY(r) + ' h8';
      if (o.labels) text(g, s.x - 14, RY(r) + 9, (r > 0 ? '+' : '−') + '2', { size: 26, anchor: 'end', cls: 'dvv-muted' });
    });
    (o.xt || [100, 300, 1000]).forEach(function (l) {
      var x = s.x + s.w * ux(l);
      d += 'M' + x + ' ' + (s.y + s.h) + ' v8';
      text(g, x, s.y + s.h + 36, String(l), { size: 26, anchor: 'middle', cls: 'dvv-muted' });
    });
    el('path', { d: d, 'class': 'dvv-spine' }, g);
    if (o.bin) text(g, m.x + m.w - 12, m.y + 34, o.bin, { size: 28, anchor: 'end' });
    if (o.ylabel) {
      text(g, m.x - 66, m.y + m.h / 2, o.ylabel, { size: 30, anchor: 'middle', rotate: true });
      text(g, s.x - 66, s.y + s.h / 2, ['Δ/σ', ['G', 'sub']], { size: 30, anchor: 'middle', rotate: true });
    }
  };
  var ylabel = function (e) { return ['10', [String(e), 'sup'], ' ℓ C', ['ℓ', 'sub']]; };

  // ── layouts ─────────────────────────────────────────────────────────────
  // the kappa row: gamma_1..6 then delta_1..6, a frame width apart
  var LEFT = 118, GAP = 18, PW = (W - LEFT - 10 - 5 * GAP) / 6;
  var MAIN = { y: 78, h: 392 }, STRIP = { y: 482, h: 150 };
  var rowKeys = [0, 1, 2, 3, 4, 5].map(function (i) { return 'kappa_l' + i; })
    .concat([0, 1, 2, 3, 4, 5].map(function (i) { return 'kappa_g' + i; }));
  var rowX = function (j) { return (j < 6 ? 0 : W) + LEFT + (j % 6) * (PW + GAP); };

  // the triangle: rows and columns gamma_1..6, delta_1..6, kappa at the base
  var TR = ['l0', 'l1', 'l2', 'l3', 'l4', 'l5', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5'];
  var keyOf = function (a, b) {
    if (a === 'kappa') return 'kappa_' + b;
    var rank = function (t) { return (t[0] === 'g' ? 0 : 10) + +t.slice(1); };
    return rank(a) <= rank(b) ? a + '_' + b : b + '_' + a;
  };
  var GX = 76, GY = 64, KAPPA_GAP = 16, LAB = 44;
  var CP = (W - GX - 2) / 12, CW = CP - 10;
  var RP = (H - GY - LAB - KAPPA_GAP) / 13, CH = RP - 7;
  var cell = function (row, col) {
    return { x: GX + col * CP, y: GY + row * RP + (row === 12 ? KAPPA_GAP : 0), w: CW, h: CH };
  };
  var cells = [];
  TR.forEach(function (a, r) { TR.slice(0, r + 1).forEach(function (b, c) { cells.push({ key: keyOf(a, b), row: r, col: c, a: a, b: b }); }); });
  TR.forEach(function (b, c) { cells.push({ key: keyOf('kappa', b), row: 12, col: c, a: 'kappa', b: b }); });

  // ── scene ───────────────────────────────────────────────────────────────
  var scene = el('g', {}, svg);
  var tint = el('g', {}, scene);                 // the kappa row's band, in state 2
  var nodes = [];                                // { el, poses: [state 0, 1, 2] }
  var keys = [];                                 // legends, laid out once text can be measured
  // arrive: when, as a fraction of the zoom, an arriving element starts to fade in
  var add = function (node, poses, arrive) { nodes.push({ el: node, poses: poses, arrive: arrive }); return node; };
  var hidden = { o: 0, v: false };

  var rowYlim = {
    LK: fullRange(rowKeys.slice(0, 6).map(function (k) { return pairs[k]; }), 0.3),
    GK: fullRange(rowKeys.slice(6).map(function (k) { return pairs[k]; }), 0.3),
  };
  cells.forEach(function (c) {
    var p = pairs[c.key];
    var tri = cell(c.row, c.col);
    var outer = el('g', {}, scene);
    var inner = drawData(outer, p);
    var q = quietRange(p);
    var j = rowKeys.indexOf(c.key);
    if (j >= 0) {
      // in the row, the panel shares its half's axes (one exponent per family)
      var k = Math.pow(10, famE(p.family) - p.e);
      var yl = rowYlim[p.family].map(function (v) { return v / k; });
      var m0 = { x: rowX(j), y: MAIN.y, w: PW, h: MAIN.h };
      var m1 = { x: rowX(j) - W, y: MAIN.y, w: PW, h: MAIN.h };
      add(outer, [{ t: rectT(m0), o: 1, v: j < 6 }, { t: rectT(m1), o: 1, v: j >= 6 }, { t: rectT(tri), o: 1, v: true }]);
      add(inner, [{ t: ylimT(yl) }, { t: ylimT(yl) }, { t: ylimT(q) }]);
      var strip = el('g', {}, scene);
      drawResid(strip, p);
      var flat = { x: tri.x, y: tri.y + tri.h, w: tri.w, h: 0.001 };
      add(strip, [{ t: rectT({ x: m0.x, y: STRIP.y, w: PW, h: STRIP.h }), o: 1, v: j < 6 },
        { t: rectT({ x: m1.x, y: STRIP.y, w: PW, h: STRIP.h }), o: 1, v: j >= 6 },
        { t: rectT(flat), o: 0, v: false }]);
    } else {
      // above the row, off the top of the frame, at the zoom the row is seen at
      var ref = function (state) {
        var anchor = cell(12, state === 0 ? 0 : 6), s = PW / CW;
        return { x: LEFT + s * (tri.x - anchor.x), y: MAIN.y + s * (tri.y - anchor.y), w: s * tri.w, h: s * tri.h };
      };
      add(outer, [{ t: rectT(ref(0)), o: 0, v: false }, { t: rectT(ref(1)), o: 0, v: false }, { t: rectT(tri), o: 1, v: true }], 0.22);
      add(inner, [{ t: ylimT(q) }, { t: ylimT(q) }, { t: ylimT(q) }]);
    }
  });
  // point and line weights: detailed in the row, fine in the triangle
  add(svg, [{ vars: ROWW }, { vars: ROWW }, { vars: TRIW }]);

  // decor of the row: one group per half, in screen coordinates, panned with it
  [['l', 'LK', 'TR1 shear × SPT-3G κ · blinded', 'source bin '], ['g', 'GK', 'TR1 galaxies × SPT-3G κ · blinded', 'lens bin ']].forEach(function (h, half) {
    var g = el('g', {}, scene);
    var x0 = half * W;
    var halfKeys = rowKeys.slice(half * 6, half * 6 + 6);
    var yl = rowYlim[h[1]];
    halfKeys.forEach(function (k, i) {
      var m = { x: rowX(half * 6 + i), y: MAIN.y, w: PW, h: MAIN.h }, s = { x: m.x, y: STRIP.y, w: PW, h: STRIP.h };
      drawAxes(g, m, s, yl, { labels: i === 0, bin: h[3] + (i + 1), ylabel: i === 0 ? ylabel(famE(h[1])) : null });
    });
    text(g, x0 + LEFT + 3 * (PW + GAP) - GAP / 2, H - 14, ['multipole ', 'ℓ'], { size: 28, anchor: 'middle' });
    text(g, x0 + LEFT, 40, h[2], { size: 32 });
    // key, right-aligned on the header line
    keys.push({ g: el('g', {}, g), right: x0 + W - 10, y: 40, items: ['pt', 'th'].concat(half ? ['cut'] : []) });
    add(g, [{ t: 'translate(0px, 0px)', o: 1, v: half === 0 }, { t: 'translate(' + (-W) + 'px, 0px)', o: 1, v: half === 1 },
      { t: 'translate(' + (-W * half) + 'px, 0px)', o: 0, v: false }]);
  });

  // decor of the triangle
  var tdec = el('g', {}, scene);
  TR.forEach(function (t, i) {
    var c = cell(i, 0), b = cell(12, i);
    text(tdec, GX - 14, c.y + c.h / 2 + 10, symParts(t), { size: 28, anchor: 'end' });
    text(tdec, b.x + b.w / 2, b.y + b.h + 36, symParts(t), { size: 28, anchor: 'middle' });
  });
  var kc = cell(12, 0);
  text(tdec, GX - 14, kc.y + kc.h / 2 + 10, 'κ', { size: 28, anchor: 'end' });
  var nb = 0, nf = 0;
  Object.keys(pairs).forEach(function (k) { nb += pairs[k].ell.length; nf += pairs[k].nfit; });
  var hc = cell(0, 3);
  text(tdec, hc.x, GY + 26, 'The blinded TR1 × SPT-3G data vector', { size: 32 });
  text(tdec, hc.x, GY + 70, Object.keys(pairs).length + ' spectra · ' + nb + ' bandpowers · ' + nf + ' inside the scale cut',
    { size: 26, cls: 'dvv-muted' });
  keys.push({ g: el('g', {}, tdec), items: ['pt', 'th', 'cut'], stack: { x: cell(2, 7).x, y: cell(2, 7).y + 30 } });
  text(tdec, cell(5, 9).x + CW, cell(5, 9).y + 30, 'click a panel to open it', { size: 24, anchor: 'end', cls: 'dvv-muted dvv-hint', italic: true });
  add(tdec, [{ o: 0, v: false }, { o: 0, v: false }, { o: 1, v: true }]);
  var kr = cell(12, 0), kr2 = cell(12, 11);
  el('rect', { x: kr.x - 6, y: kr.y - 5, width: kr2.x + kr2.w - kr.x + 12, height: kr.h + 10, rx: 4 }, tint);
  tint.style.fill = 'var(--rule)';
  add(tint, [{ o: 0, v: false }, { o: 0, v: false }, { o: 0.5, v: true }]);

  // ── keys (legends): a swatch before each label ──────────────────────────
  var LABEL = { pt: ['blinded data ± σ', ['G', 'sub']], th: 'windowed fiducial', cut: 'outside validated linear-bias cut' };
  function swatch(g, x, y, kind) {
    if (kind === 'pt') {
      el('path', { d: 'M' + x + ' ' + (y - 24) + ' v28', 'class': 'dvv-bar dvv-in', style: 'stroke-width:2.4px' }, g);
      el('path', { d: 'M' + x + ' ' + (y - 10) + ' h0', 'class': 'dvv-pt dvv-in', style: 'stroke-width:11px' }, g);
    } else if (kind === 'th') el('path', { d: 'M' + (x - 16) + ' ' + (y - 10) + ' h32', 'class': 'dvv-line dvv-th', style: 'stroke-width:3px' }, g);
    else el('rect', { x: x - 16, y: y - 26, width: 32, height: 32, rx: 3, 'class': 'dvv-cut' }, g);
  }
  // right-aligned on one line (right, y), or stacked from its top left (stack)
  function drawKey(k) {
    if (k.done) return true;
    if (k.stack) {
      k.items.forEach(function (it, i) {
        var y = k.stack.y + i * 44;
        swatch(k.g, k.stack.x + 16, y, it);
        text(k.g, k.stack.x + 44, y, LABEL[it], { size: 26 });
      });
      return (k.done = true);
    }
    var x = k.right, ts = [];
    for (var i = k.items.length - 1; i >= 0; i--) {
      var t = text(k.g, x, k.y, LABEL[k.items[i]], { size: 26, anchor: 'end' });
      var w = t.getComputedTextLength();
      if (!w) { while (k.g.firstChild) k.g.firstChild.remove(); return false; }   // not rendered yet
      swatch(k.g, x - w - 24, k.y, k.items[i]);
      x -= w + 24 + 16 + 44;
    }
    return (k.done = true);
  }
  function layoutKeys() { keys.forEach(drawKey); }

  // ── hover and the detail panel (state 2) ───────────────────────────────
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
    h.addEventListener('click', function (e) { e.stopPropagation(); open(c); });
  });

  var card = null, lastOpenMs = null;
  function onKey(e) {
    if (e.key === 'Escape' || e.key === 'Backspace') { close(); e.preventDefault(); e.stopPropagation(); }
  }
  function onDown(e) { if (card && !card.box.contains(e.target)) { close(); e.stopPropagation(); e.preventDefault(); } }
  function open(c) {
    var t0 = performance.now();
    close();
    var p = pairs[c.key];
    var g = el('g', {}, svg);
    var veil = el('rect', { x: 0, y: 0, width: W, height: H }, g);
    veil.style.fill = 'var(--ground)'; veil.style.fillOpacity = '0.82';
    var box = el('g', {}, g);
    VARS.forEach(function (v, i) { box.style.setProperty(v, ['9px', '2.2px', '3px', '1'][i]); });
    var B = { x: 140, y: 12, w: W - 280, h: H - 24 };
    el('rect', { x: B.x, y: B.y, width: B.w, height: B.h, rx: 14, 'class': 'dvv-card' }, box);
    var t1 = text(box, B.x + 48, B.y + 60, [].concat(symParts(c.a), [' × '], symParts(c.b)), { size: 40 });
    var note = p.nfit === p.fit.length ? 'every band inside the validated linear-bias cut'
      : p.nfit === 0 ? 'every band outside the validated linear-bias cut'
      : p.nfit + ' of ' + p.fit.length + ' bands inside the validated linear-bias cut';
    text(box, B.x + 48, B.y + 100, name(c.a) + ' × ' + name(c.b) + ' · blinded · ' + note, { size: 26, cls: 'dvv-muted' });
    drawKey({ g: el('g', {}, box), right: B.x + B.w - 40, y: B.y + 60, items: ['pt', 'th'].concat(p.nfit < p.fit.length ? ['cut'] : []) });
    var m = { x: B.x + 150, y: B.y + 140, w: B.w - 196, h: 300 }, s = { x: m.x, y: m.y + m.h + 12, w: m.w, h: 118 };
    var q = (function () {
      var lo = 0, hi = 0;
      p.t.forEach(function (t) { lo = Math.min(lo, t); hi = Math.max(hi, t); });
      p.v.forEach(function (v, i) {
        // every band, unless one far outside the cut would flatten the rest
        if (!p.fit[i] && Math.abs(p.r[i]) > 4) return;
        lo = Math.min(lo, v - p.s[i]); hi = Math.max(hi, v + p.s[i]);
      });
      var span = hi - lo;
      return [lo - 0.06 * span, hi + 0.1 * span];
    })();
    var dg = el('g', { transform: 'translate(' + m.x + ' ' + m.y + ') scale(' + m.w + ' ' + m.h + ')' }, box);
    var inner = drawData(dg, p);
    inner.setAttribute('transform', 'translate(0 ' + (q[1] / (q[1] - q[0])) + ') scale(1 ' + (-1 / (q[1] - q[0])) + ')');
    var rg = el('g', { transform: 'translate(' + s.x + ' ' + s.y + ') scale(' + s.w + ' ' + s.h + ')' }, box);
    drawResid(rg, p);
    drawAxes(box, m, s, q, { labels: true, ylabel: ylabel(p.e), xt: [100, 300, 1000, 3000] });
    text(box, m.x + m.w / 2, s.y + s.h + 76, ['multipole ', 'ℓ'], { size: 28, anchor: 'middle' });
    // what the strip cannot show, said plainly
    var edge = [];
    p.r.forEach(function (r, i) { if (p.fit[i] && Math.abs(r) >= 3.7) edge.push((r > 0 ? '+' : '−') + Math.abs(r).toFixed(1)); });
    var off = p.r.filter(function (r, i) { return !p.fit[i] && Math.abs(r) >= 3.7; }).length;
    var says = [];
    if (edge.length) says = ['on the strip edge, inside the cut: ' + edge.join(', ') + ' σ', ['G', 'sub']];
    if (off) says.push((says.length ? ' · ' : '') + off + (off > 1 ? ' bands' : ' band') + ' outside the cut lie beyond the strip');
    if (says.length) text(box, B.x + 48, B.y + B.h - 24, says, { size: 24, cls: 'dvv-muted', italic: true });
    text(box, B.x + B.w - 40, B.y + B.h - 24, 'Esc to close', { size: 24, anchor: 'end', cls: 'dvv-muted', italic: true });
    g.animate([{ opacity: 0 }, { opacity: 1 }], { duration: ctx.still() ? 0 : 160, easing: 'ease-out' });
    box.animate([{ transform: 'translateY(10px)' }, { transform: 'translateY(0px)' }], { duration: ctx.still() ? 0 : 220, easing: 'ease-out' });
    card = { g: g, box: box };
    ctx.keyboard(false);
    document.addEventListener('keydown', onKey, true);
    document.addEventListener('pointerdown', onDown, true);
    lastOpenMs = performance.now() - t0;
    svg.dataset.openMs = lastOpenMs.toFixed(1);
  }
  function close() {
    if (!card) return;
    card.g.remove();
    card = null;
    ctx.keyboard(true);
    document.removeEventListener('keydown', onKey, true);
    document.removeEventListener('pointerdown', onDown, true);
  }

  // ── states ──────────────────────────────────────────────────────────────
  var state = null, running = [];
  var apply = function (n, p) {
    if (p.t) n.style.transform = p.t;
    if (p.o != null) n.style.opacity = p.o;
    if (p.v != null) n.style.visibility = p.v ? 'visible' : 'hidden';
    if (p.vars) VARS.forEach(function (v, i) { n.style.setProperty(v, p.vars[i]); });
  };
  function step(k, animate) {
    k = Math.max(0, Math.min(2, k));
    layoutKeys();
    running.forEach(function (a) { a.finish(); });
    running = [];
    var from = state;
    state = k;
    if (k !== 2) { close(); hl.style.visibility = 'hidden'; }
    hits.style.visibility = k === 2 ? 'visible' : 'hidden';
    var single = animate && from != null && from !== k && Math.abs(from - k) === 1;
    if (single && ctx.still()) {
      // reduced motion: the old state, frozen, fades out over the new one
      var ghost = svg.cloneNode(true);
      ghost.querySelectorAll('[id]').forEach(function (n) { n.removeAttribute('id'); });
      ghost.style.pointerEvents = 'none';
      svg.parentNode.appendChild(ghost);
      var fade = ghost.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 450, easing: 'ease-in-out', fill: 'forwards' });
      fade.finished.then(function () { ghost.remove(); }, function () { ghost.remove(); });
      running.push(fade);
    }
    nodes.forEach(function (n) { apply(n.el, n.poses[k]); });
    if (!single || ctx.still()) return;
    var zoom = from + k === 3, dur = zoom ? ZOOM_MS : PAN_MS;
    nodes.forEach(function (n) {
      var a = n.poses[from], b = n.poses[k];
      if (a.v === false && b.v === false) return;
      var kf;
      if (a.vars) kf = [0, 1].map(function (i) {
        var p = [a, b][i], f = {};
        VARS.forEach(function (v, j) { f[v] = p.vars[j]; });
        return f;
      });
      else {
        var oa = a.o == null ? 1 : a.o, ob = b.o == null ? 1 : b.o;
        var s0 = { visibility: 'visible', opacity: oa }, s1 = { visibility: 'visible', opacity: ob };
        if (a.t) { s0.transform = a.t; s1.transform = b.t; }
        if (oa > ob) kf = [s0, { visibility: 'visible', opacity: ob, offset: 0.18 }, s1];         // leaving: gone early
        else if (oa < ob) kf = [s0, { visibility: 'visible', opacity: oa, offset: n.arrive || 0.6 }, s1];   // arriving: fades in late
        else kf = [s0, s1];
      }
      running.push(n.el.animate(kf, { duration: dur, easing: EASE }));
    });
  }

  figure.querySelector('.frame').appendChild(svg);
  svg.dataset.mountMs = (performance.now() - T0).toFixed(1);
  return { step: step, leave: close, open: function (key) { var c = cells.filter(function (x) { return x.key === key; })[0]; if (c) open(c); } };
});
