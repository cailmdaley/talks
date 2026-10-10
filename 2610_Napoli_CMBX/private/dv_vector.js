// The blinded TR1 3x2pt + kappa data vector (house data-app), for each shear
// method and CMB lensing survey measured; the deck's variant control picks one.
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
  css.textContent = data.css;          // the figure's own classes; app chrome is house.css
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

  function scene(variant) {
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, 'class': 'app-view', role: 'img' });
    var world = el('g', {}, svg);
    var N = data.near;
    var layer = {
      over: group(variant.layers.over, { 'class': 'app-mpl' }),
      near: group(variant.layers.near, { 'class': 'app-mpl', transform: 'translate(' + N.x + ' ' + N.y + ') scale(' + (1 / N.s) + ')' }),
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
    var hits = el('g', {}, svg), hl = el('rect', { 'class': 'app-hl', rx: 3 }, svg);
    hl.style.visibility = 'hidden';
    data.cells.forEach(function (c) {
      var h = el('rect', { x: c.x - 2, y: c.y - 1.5, width: c.w + 4, height: c.h + 3, 'class': 'app-hit' }, hits);
      h.addEventListener('pointerenter', function () {
        hl.setAttribute('x', c.x - 2); hl.setAttribute('y', c.y - 1.5); hl.setAttribute('width', c.w + 4); hl.setAttribute('height', c.h + 3);
        hl.style.visibility = 'visible';
      });
      h.addEventListener('pointerleave', function () { hl.style.visibility = 'hidden'; });
      h.addEventListener('click', function (e) { e.stopPropagation(); openCard(c); });
    });

    var card = null;
    function onKey(e) { if (e.key === 'Escape' || e.key === 'Backspace') { closeCard(); e.preventDefault(); e.stopPropagation(); } }
    function onDown(e) { if (card && !card.box.contains(e.target) && !e.target.closest('.variants')) { closeCard(); e.stopPropagation(); e.preventDefault(); } }
    function openCard(c, instant) {
      var t0 = performance.now();
      closeCard();
      var g = el('g', {}, svg);
      el('rect', { x: 0, y: 0, width: W, height: H, 'class': 'fill-ground', opacity: 0.85 }, g);
      var box = el('g', {}, g);
      var bw = (H - 24) * DW / DH, B = { x: (W - bw) / 2, y: 12, w: bw, h: H - 24 };
      el('rect', { x: B.x + 2, y: B.y + 6, width: B.w, height: B.h, rx: 16, 'class': 'app-shadow' }, box);
      el('rect', { x: B.x, y: B.y, width: B.w, height: B.h, rx: 14, 'class': 'app-card' }, box);
      box.appendChild(group(variant.details[c.key],
        { 'class': 'app-mpl', transform: 'translate(' + B.x + ' ' + B.y + ') scale(' + (B.h / DH) + ')' }));
      var note = el('text', { x: B.x + B.w - 28, y: B.y + B.h - 22, 'text-anchor': 'end', 'font-size': 32, 'class': 'app-note' }, box);
      note.textContent = 'Esc to close';
      if (!instant && g.animate && !ctx.still()) try { g.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 160, easing: 'ease-out' }); } catch (e) { /* static */ }
      card = { g: g, box: box, key: c.key };
      axesFor(c.key);
      ctx.keyboard(false);
      document.addEventListener('keydown', onKey, true);
      document.addEventListener('pointerdown', onDown, true);
      svg.setAttribute('data-open-ms', (performance.now() - t0).toFixed(1));
    }
    function closeCard() {
      if (!card) return;
      svg.removeChild(card.g);
      card = null;
      axesFor(null);
      ctx.keyboard(true);
      document.removeEventListener('keydown', onKey, true);
      document.removeEventListener('pointerdown', onDown, true);
    }

    return {
      svg: svg, land: land, fly: fly, closeCard: closeCard, openCard: openCard,
      hover: function (on) { if (!on) hl.style.visibility = 'hidden'; },
      cardKey: function () { return card && card.key; },
    };
  }

  // the variant axes the view on screen depends on: a cell with a shear tracer (l*)
  // uses the shear method, one with kappa the CMB map; the close-ups follow their row
  var cellAxes = function (key) {
    var a = [];
    if (/(^|_)l\d/.test(key)) a.push('shear');
    if (/kappa/.test(key)) a.push('cmb');
    return a;
  };
  function axesFor(key) {
    if (!ctx.axes) return;
    if (key) ctx.axes(cellAxes(key));
    else ctx.axes(state === 1 ? ['cmb'] : null);
  }
  var S = null, state = null, shown = null;
  function use(vk) {
    if (vk === shown || !data.variants[vk]) return;
    var next = scene(data.variants[vk]);
    // an open detail card stays open across the switch, showing the same cell
    var open = S && S.cardKey();
    if (S) { S.closeCard(); frameEl.replaceChild(next.svg, S.svg); }
    else frameEl.appendChild(next.svg);
    S = next;
    shown = vk;
    S.land(state == null ? 0 : state);
    if (open) S.openCard(data.cells.filter(function (x) { return x.key === open; })[0], true);
  }

  // ── steps ───────────────────────────────────────────────────────────────
  function step(k, animate) {
    k = Math.max(0, Math.min(2, k));
    if (k !== 2) { S.closeCard(); S.hover(false); }
    var from = state;
    state = k;
    if (!S.cardKey()) axesFor(null);
    if (!animate || from == null || from === k) { S.land(k); return; }
    if (ctx.still()) {
      // reduced motion: the old view, frozen, fades out over the new one
      var ghost = S.svg.cloneNode(true);
      ghost.style.pointerEvents = 'none';
      S.svg.parentNode.insertBefore(ghost, S.svg.nextSibling);
      S.land(k);
      var gone = function () { if (ghost.parentNode) ghost.parentNode.removeChild(ghost); };
      try { ghost.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 450, easing: 'ease-in-out', fill: 'forwards' }).finished.then(gone, gone); }
      catch (e) { gone(); }
      return;
    }
    S.fly(k);
  }

  // the deck's variant control and shared choice pick the variant; the first is the
  // default, and without the house variants hook the default is all there is
  use(Object.keys(data.variants)[0]);
  if (ctx.variants) ctx.variants(Object.keys(data.variants), use);
  S.svg.setAttribute('data-mount-ms', (performance.now() - T0).toFixed(1));
  return {
    step: step,
    leave: function () { S.closeCard(); },
    open: function (key) { var c = data.cells.filter(function (x) { return x.key === key; })[0]; if (c) S.openCard(c); },
  };
});
