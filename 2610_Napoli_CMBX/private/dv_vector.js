// The blinded TR1 3x2pt + kappa data vector (house data-app), with toggles
// between the shear methods and CMB lensing surveys that have been measured.
//
// Nothing is drawn here: private/render_dv_vector.py renders the figure with
// matplotlib as two SVG layers, and this script only places, moves and fades
// them. "over" is the whole data vector as a triangle of panels in world
// coordinates (the figure box at rest on the overview); "near" is the CMB
// lensing row close up, with residual strips, drawn in the close-up camera's
// screen units and placed in the world so its columns lie exactly over the
// overview's. One matrix on one group is the camera, a uniform zoom (glyphs
// never stretch); the three rest states are three views of the world:
//   0  close on the kappa row's source-bin half: gamma_i x kappa
//   1  the same zoom, panned right to its lens-bin half: delta_i x kappa
//   2  pulled back to the whole triangle
// The close-up's row is taller than the overview's, so on the way out "near"
// shrinks with the camera and crossfades into "over", columns in register.
// Each layer's opacity is a function of the camera alone, so a camera at rest
// or in flight draws the same way. On the overview a cell lights under the pointer and a click opens that
// pair's own pre-rendered panel (Esc, Backspace or a click outside closes it).
// A do-nothing Web Animation is the clock, so finishing it (as the house
// checker does) lands the step; without Web Animations a step is instant.
// Data: private/dv_vector_app.json (blind cmbx_dr1_a).
House.app('dv_vector', function (figure, data, ctx) {
  'use strict';
  var T0 = performance.now();
  var NS = 'http://www.w3.org/2000/svg';
  var W = data.world.w, H = data.world.h, DW = data.detail.w, DH = data.detail.h;
  var PAN_MS = 900, ZOOM_MS = 1500;
  var frameEl = figure.querySelector('.frame');

  var el = function (tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (parent) parent.appendChild(n);
    return n;
  };
  var parse = function (markup) {
    var doc = new DOMParser().parseFromString(markup, 'image/svg+xml');
    return document.importNode(doc.documentElement, true);
  };
  // a rendered SVG's contents as one group in its own coordinates
  var group = function (markup, attrs) {
    var src = parse(markup), g = el('g', attrs);
    while (src.firstChild) g.appendChild(src.firstChild);
    return g;
  };

  // glyphs, markers and the shared style classes, once for every layer and card
  var defs = el('svg', { width: 0, height: 0, 'aria-hidden': 'true' });
  defs.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden;';
  defs.appendChild(parse('<svg xmlns="' + NS + '"><defs>' + data.glyphs + '</defs></svg>').firstChild);
  var css = el('style', {}, defs);
  css.textContent = data.css + [
    '.dvv-mpl * { stroke-linejoin: round; stroke-linecap: butt; }',
    '.dvv-hit { fill: transparent; cursor: pointer; }',
    '.dvv-hl { fill: none; stroke: var(--accent); stroke-width: 2px; pointer-events: none; }',
    '.dvv-ground { fill: var(--ground); }',
    '.dvv-card { fill: var(--ground); stroke: var(--rule); stroke-width: 1.5px; }',
    '.dvv-shadow { fill: var(--ink); opacity: 0.06; }',
    '.dvv-note { fill: var(--muted); font-style: italic; }',
    '.dvv-seg { fill: var(--ground); stroke: var(--rule); stroke-width: 1.5px; }',
    '.dvv-seg-on { fill: var(--panel); stroke: var(--muted); }',
    '.dvv-seg-text { fill: var(--ink); }',
    '.dvv-seg-off .dvv-seg { stroke-dasharray: 4 4; } .dvv-seg-off .dvv-seg-text { fill: var(--muted); font-style: italic; }',
  ].join('\n');
  frameEl.appendChild(defs);

  // the clock: a Web Animation that does nothing; finishing it lands the step
  var tick = document.createElement('span');
  tick.setAttribute('aria-hidden', 'true');
  tick.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden;';
  frameEl.appendChild(tick);

  // ── views and the camera ────────────────────────────────────────────────
  var camOf = function (v) { var s = W / v.w; return { s: s, tx: -v.x * s, ty: -v.y * s }; };
  var CAMS = data.views.map(camOf);
  var LZ = Math.log(CAMS[0].s);
  var smooth = function (a, b, x) { var t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
  var view = function (c) { return { x: -c.tx / c.s, y: -c.ty / c.s, w: W / c.s, h: H / c.s }; };
  // between two cameras the seen rectangle's centre moves straight and its size
  // changes geometrically, so a zoom reads as one steady pull
  var between = function (a, b, t) {
    var va = view(a), vb = view(b);
    var w = va.w * Math.pow(vb.w / va.w, t);
    var cx = va.x + va.w / 2 + (vb.x + vb.w / 2 - va.x - va.w / 2) * t;
    var cy = va.y + va.h / 2 + (vb.y + vb.h / 2 - va.y - va.h / 2) * t;
    return camOf({ x: cx - w / 2, y: cy - (w * H / W) / 2, w: w });
  };
  var ease = function (t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };

  var cardShown = function (on) { if (ui) ui.style.visibility = on ? 'hidden' : 'visible'; };

  function scene(variant) {
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, 'class': 'app-view', role: 'img' });
    var world = el('g', {}, svg);
    var N = data.near;
    var layer = {
      over: group(variant.layers.over, { 'class': 'dvv-mpl' }),
      near: group(variant.layers.near, { 'class': 'dvv-mpl', transform: 'translate(' + N.x + ' ' + N.y + ') scale(' + (1 / N.s) + ')' }),
    };
    world.appendChild(layer.over);
    world.appendChild(layer.near);

    var cam = { s: 1, tx: 0, ty: 0 };
    function render() {
      world.setAttribute('transform', 'matrix(' + cam.s + ' 0 0 ' + cam.s + ' ' + cam.tx + ' ' + cam.ty + ')');
      var z = Math.max(0, Math.min(1, (LZ - Math.log(cam.s)) / LZ));        // 0 close, 1 far
      var op = { over: smooth(0.1, 0.5, z), near: 1 - smooth(0.02, 0.42, z) };
      Object.keys(op).forEach(function (k) {
        layer[k].setAttribute('opacity', op[k].toFixed(3));
        layer[k].style.visibility = op[k] > 0.002 ? 'visible' : 'hidden';
      });
    }

    var flight = null;
    function land(k) {
      if (flight) { var f = flight; flight = null; cancelAnimationFrame(f.raf); try { f.clock.cancel(); } catch (e) { /* gone */ } }
      cam = { s: CAMS[k].s, tx: CAMS[k].tx, ty: CAMS[k].ty };
      render();
      svg.setAttribute('data-rest', k);              // at rest on step k (read by tests)
      hits.style.visibility = k === 2 ? 'visible' : 'hidden';
    }
    function fly(k) {
      var from = { s: cam.s, tx: cam.tx, ty: cam.ty }, to = CAMS[k];
      var dur = Math.abs(Math.log(from.s / to.s)) > 1e-6 ? ZOOM_MS : PAN_MS;
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

    // ── hover and the detail card (overview only) ─────────────────────────
    var hits = el('g', {}, svg), hl = el('rect', { 'class': 'dvv-hl', rx: 3 }, svg);
    hl.style.visibility = 'hidden';
    data.cells.forEach(function (c) {
      var h = el('rect', { x: c.x - 2, y: c.y - 1.5, width: c.w + 4, height: c.h + 3, 'class': 'dvv-hit' }, hits);
      h.addEventListener('pointerenter', function () {
        hl.setAttribute('x', c.x - 2); hl.setAttribute('y', c.y - 1.5); hl.setAttribute('width', c.w + 4); hl.setAttribute('height', c.h + 3);
        hl.style.visibility = 'visible';
      });
      h.addEventListener('pointerleave', function () { hl.style.visibility = 'hidden'; });
      h.addEventListener('click', function (e) { e.stopPropagation(); openCard(c); });
    });

    var card = null;
    function onKey(e) { if (e.key === 'Escape' || e.key === 'Backspace') { closeCard(); e.preventDefault(); e.stopPropagation(); } }
    function onDown(e) { if (card && !card.box.contains(e.target)) { closeCard(); e.stopPropagation(); e.preventDefault(); } }
    function openCard(c) {
      var t0 = performance.now();
      closeCard();
      var g = el('g', {}, svg);
      el('rect', { x: 0, y: 0, width: W, height: H, 'class': 'dvv-ground', opacity: 0.85 }, g);
      var box = el('g', {}, g);
      var bw = (H - 24) * DW / DH, B = { x: (W - bw) / 2, y: 12, w: bw, h: H - 24 };
      el('rect', { x: B.x + 2, y: B.y + 6, width: B.w, height: B.h, rx: 16, 'class': 'dvv-shadow' }, box);
      el('rect', { x: B.x, y: B.y, width: B.w, height: B.h, rx: 14, 'class': 'dvv-card' }, box);
      box.appendChild(group(variant.details[c.key],
        { 'class': 'dvv-mpl', transform: 'translate(' + B.x + ' ' + B.y + ') scale(' + (B.h / DH) + ')' }));
      var note = el('text', { x: B.x + B.w - 28, y: B.y + B.h - 22, 'text-anchor': 'end', 'font-size': 24, 'class': 'dvv-note' }, box);
      note.textContent = 'Esc to close';
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
      svg: svg, land: land, fly: fly, closeCard: closeCard, openCard: openCard,
      hover: function (on) { if (!on) hl.style.visibility = 'hidden'; },
    };
  }

  // ── toggles: shear method and CMB survey; a variant not measured is shown but disabled
  var ui = el('svg', { viewBox: '0 0 ' + W + ' ' + H, 'class': 'app-view dvv-ui' });
  ui.style.pointerEvents = 'none';
  var uiDone = false;
  var sel = Object.keys(data.variants)[0].split('|');
  function drawUI() {
    while (ui.firstChild) ui.removeChild(ui.firstChild);
    var x = W - 8, y = 14, h = 40, pad = 16, gap = 22;
    var groups = [['cmb', Object.keys(data.cmbs), data.cmbs], ['shear', Object.keys(data.shears), data.shears]];
    var ok = true;
    groups.forEach(function (gr) {
      for (var i = gr[1].length - 1; i >= 0; i--) {
        var id = gr[1][i];
        var want = gr[0] === 'cmb' ? sel[0] + '|' + id : id + '|' + sel[1];
        var on = gr[0] === 'cmb' ? sel[1] === id : sel[0] === id;
        var has = !!data.variants[want];
        var g = el('g', {}, ui);
        var r = el('rect', {}, g);
        var t = el('text', { 'font-size': 24, 'text-anchor': 'middle' }, g);
        t.textContent = gr[2][id];
        var w = t.getComputedTextLength();
        if (!w) { ok = false; return; }
        w += 2 * pad;
        r.setAttribute('x', x - w); r.setAttribute('y', y); r.setAttribute('width', w); r.setAttribute('height', h);
        r.setAttribute('rx', 6);
        r.setAttribute('class', 'dvv-seg' + (on ? ' dvv-seg-on' : ''));
        t.setAttribute('x', x - w / 2); t.setAttribute('y', y + h / 2 + 8);
        t.setAttribute('class', 'dvv-seg-text');
        el('title', {}, g).textContent = has ? gr[2][id] : gr[2][id] + ': not measured yet';
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
    var next = scene(data.variants[vk]);
    if (S) { S.closeCard(); frameEl.replaceChild(next.svg, S.svg); }
    else frameEl.insertBefore(next.svg, ui);
    S = next;
    sel = vk.split('|');
    S.land(state == null ? 0 : state);
    drawUI();
  }

  // ── steps ───────────────────────────────────────────────────────────────
  function step(k, animate) {
    k = Math.max(0, Math.min(2, k));
    if (!uiDone) drawUI();
    if (k !== 2) { S.closeCard(); S.hover(false); }
    var from = state;
    state = k;
    if (!animate || from == null || from === k) { S.land(k); return; }
    if (ctx.still()) {
      // reduced motion: the old view, frozen, fades out over the new one
      var ghost = S.svg.cloneNode(true);
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
    open: function (key) { var c = data.cells.filter(function (x) { return x.key === key; })[0]; if (c) S.openCard(c); },
  };
});
