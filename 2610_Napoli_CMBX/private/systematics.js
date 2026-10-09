// Template contamination of the blinded TR1 3x2pt + kappa data vector (house data-app):
// for a chosen systematics template, X_l^{ab} / sigma_ab for every pair, laid out cell for
// cell like the dv-vector slide:
//   0  one pair's card, gamma_6 x kappa, filling the figure: its contamination and the
//      two template crosses it is made from
//   1  the card shrinks into its cell of the whole triangle
// Nothing is drawn here: private/render_systematics.py renders every panel with
// matplotlib as SVG ("over" the whole triangle in the dv-vector slide's geometry, and
// the card's pieces), and this script places, moves, fades and swaps them. The app's own
// control picks the template at every step; the deck's variant control picks the shear
// method and CMB map. On the overview a click on a cell opens its card the same way:
// the pair's X / sigma_ab along the bottom and the template's cross with
// each of its tracers above, each with its chi^2 PTE (Esc, Backspace or a click outside
// closes it). The template control moves onto the card while it is open. The variant
// axes the view depends on follow the step and the card. A do-nothing Web Animation is
// the clock, so finishing it (as the house checker does) lands the step.
// Data: private/systematics_app.json.
House.app('systematics', function (figure, data, ctx) {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';
  var W = data.world.w, H = data.world.h, DW = data.detail.w, DH = data.detail.h;
  var ZOOM_MS = 1300, INTRO = 'kappa_l5';
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
  var group = function (markup, attrs) {
    var src = parse(markup), g = el('g', attrs);
    while (src.firstChild) g.appendChild(src.firstChild);
    return g;
  };
  var fill = function (target, markup) {
    while (target.firstChild) target.removeChild(target.firstChild);
    var src = parse(markup);
    while (src.firstChild) target.appendChild(src.firstChild);
  };

  var defs = el('svg', { width: 0, height: 0, 'aria-hidden': 'true' });
  defs.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden;';
  defs.appendChild(parse('<svg xmlns="' + NS + '"><defs>' + data.glyphs + '</defs></svg>').firstChild);
  el('style', {}, defs).textContent = data.css;
  frameEl.appendChild(defs);

  // the clock: a Web Animation that does nothing; finishing it lands the step
  var tick = document.createElement('span');
  tick.setAttribute('aria-hidden', 'true');
  tick.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden;';
  frameEl.appendChild(tick);

  // the variant parts a pair or a tracer depends on, as in the renderer's ids
  var dep = function (tracers, vk) {
    var p = vk.split('|');
    var s = tracers.some(function (t) { return t[0] === 'l'; }) ? p[0] : '-';
    var c = tracers.indexOf('kappa') >= 0 ? p[1] : '-';
    return s + '|' + c;
  };
  var axesOf = function (tracers) {
    var a = [];
    if (tracers.some(function (t) { return t[0] === 'l'; })) a.push('shear');
    if (tracers.indexOf('kappa') >= 0) a.push('cmb');
    return a;
  };

  // ── the template control: the house control, inside the figure ───────────
  var tpl = data.templates[0][0], vk = data.variants[0];
  var choice = document.createElement('div');
  choice.className = 'variants app-choice';
  choice.setAttribute('role', 'group');
  choice.setAttribute('aria-label', 'Template');
  var restPlace = function () {
    choice.style.right = '';
    choice.style.left = (100 * data.choice.x / W) + '%';
    choice.style.top = (100 * data.choice.y / H) + '%';
  };
  restPlace();
  var seg = document.createElement('span');
  seg.className = 'seg';
  data.templates.forEach(function (t) {
    var b = document.createElement('button');
    b.type = 'button';
    b.textContent = t[1];
    b.setAttribute('data-option', t[0]);
    b.addEventListener('click', function (e) { e.stopPropagation(); setTemplate(t[0]); });
    seg.appendChild(b);
  });
  choice.appendChild(seg);
  function markChoice() {
    seg.querySelectorAll('button').forEach(function (b) {
      var on = b.getAttribute('data-option') === tpl;
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  // ── the scene: one world group under one camera, the card above it ──────
  var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, 'class': 'app-view', role: 'img' });
  frameEl.appendChild(svg);
  frameEl.appendChild(choice);
  var over = el('g', { 'class': 'app-mpl' }, svg);
  var cellOf = {};
  data.cells.forEach(function (c) { cellOf[c.key] = c; });
  var hits = el('g', {}, svg), hl = el('rect', { 'class': 'app-hl', rx: 3 }, svg);
  hl.style.visibility = 'hidden';
  data.cells.forEach(function (c) {
    var h = el('rect', { x: c.x - 2, y: c.y - 1.5, width: c.w + 4, height: c.h + 3, 'class': 'app-hit' }, hits);
    h.addEventListener('pointerenter', function () {
      hl.setAttribute('x', c.x - 2); hl.setAttribute('y', c.y - 1.5); hl.setAttribute('width', c.w + 4); hl.setAttribute('height', c.h + 3);
      hl.style.visibility = 'visible';
    });
    h.addEventListener('pointerleave', function () { hl.style.visibility = 'hidden'; });
    h.addEventListener('click', function (e) { e.stopPropagation(); openCard(c.key); });
  });

  function draw() {
    fill(over, data.over[tpl][vk]);
    svg.setAttribute('data-template', tpl);
    svg.setAttribute('data-variant', vk);
  }

  var state = null, flight = null;
  function land(k) {
    if (flight) { var f = flight; flight = null; cancelAnimationFrame(f.raf); try { f.clock.cancel(); } catch (e) { /* gone */ } }
    if (k === 0) openCard(INTRO, true, true);
    else if (card && card.intro) closeCard();
    svg.setAttribute('data-rest', k);              // at rest on step k (read by tests)
    hits.style.visibility = k === 1 ? 'visible' : 'hidden';
  }
  // the intro card between its full size (t = 0) and its cell on the triangle (t = 1)
  function shrink(t) {
    var B = card.B, c = cellOf[INTRO];
    var s = Math.exp(Math.log(c.w / B.w) * t);         // log-uniform: a steady zoom
    var cx = B.x + B.w / 2 + (c.x + c.w / 2 - B.x - B.w / 2) * t;
    var cy = B.y + B.h / 2 + (c.y + c.h / 2 - B.y - B.h / 2) * t;
    card.box.setAttribute('transform', 'translate(' + cx + ' ' + cy + ') scale(' + s + ') translate(' + -(B.x + B.w / 2) + ' ' + -(B.y + B.h / 2) + ')');
    card.box.setAttribute('opacity', (1 - Math.max(0, (t - 0.75) / 0.25)).toFixed(3));
    card.veil.setAttribute('opacity', (1 - t).toFixed(3));
  }
  function fly(k) {
    var dur = ZOOM_MS, clock;
    if (k === 0) { openCard(INTRO, true, true); shrink(1); }
    if (!card) { land(k); return; }
    try { clock = tick.animate([{ opacity: 0 }, { opacity: 0 }], { duration: dur }); } catch (e) { clock = null; }
    if (!clock || !clock.finished) { land(k); return; }
    var f = { clock: clock, raf: 0 };
    flight = f;
    restPlace();                                   // the template control waits at its rest place
    svg.removeAttribute('data-rest');
    hits.style.visibility = 'hidden';
    var frame = function () {
      if (flight !== f) return;
      var t = Math.min(1, (clock.currentTime || 0) / dur);
      if (t >= 1 || clock.playState === 'finished') { land(k); return; }
      var e = ease(t);
      shrink(k === 1 ? e : 1 - e);
      f.raf = requestAnimationFrame(frame);
    };
    clock.finished.then(function () { if (flight === f) land(k); }, function () {});
    f.raf = requestAnimationFrame(frame);
  }
  var ease = function (t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };

  // the variant axes the view on screen depends on
  function axesFor() {
    if (!ctx.axes) return;
    if (card) ctx.axes(axesOf(card.key.split('_')));
    else ctx.axes(null);
  }

  // ── the card ─────────────────────────────────────────────────────────────
  var card = null;
  function onKey(e) { if (e.key === 'Escape' || e.key === 'Backspace') { closeCard(); e.preventDefault(); e.stopPropagation(); } }
  function onDown(e) {
    if (card && !card.box.contains(e.target) && !e.target.closest('.variants')) { closeCard(); e.stopPropagation(); e.preventDefault(); }
  }
  // the template control rides on a card, at its top right
  function onCard(B) {
    choice.style.left = '';
    choice.style.right = (100 * (W - (B.x + B.w - 26)) / W) + '%';
    choice.style.top = (100 * (B.y + 22) / H) + '%';
  }
  // intro: the step-0 card, which is the slide's own view rather than an overlay: an opaque
  // ground, no close hint, and the keyboard and pointer stay with the deck
  function openCard(key, instant, intro) {
    if (card && card.intro && intro && card.key === key && card.tpl === tpl && card.vk === vk) { shrink(0); onCard(card.B); return; }
    closeCard();
    var t = key.split('_');
    var g = el('g', {}, svg);
    var veil = el('rect', { x: 0, y: 0, width: W, height: H, 'class': 'fill-ground', opacity: intro ? 1 : 0.85 }, g);
    var box = el('g', {}, g);
    var bw = (H - 24) * DW / DH, B = { x: (W - bw) / 2, y: 12, w: bw, h: H - 24 }, s = B.h / DH;
    el('rect', { x: B.x + 2, y: B.y + 6, width: B.w, height: B.h, rx: 16, 'class': 'app-shadow' }, box);
    el('rect', { x: B.x, y: B.y, width: B.w, height: B.h, rx: 14, 'class': 'app-card' }, box);
    var inner = el('g', { transform: 'translate(' + B.x + ' ' + B.y + ') scale(' + s + ')' }, box);
    inner.appendChild(group(data.xcard[tpl][key + '|' + dep(t, vk)], { 'class': 'app-mpl' }));
    var tracers = t[0] === t[1] ? [t[0]] : sortTracers(t);
    tracers.forEach(function (tr, i) {
      var slot = data.slots[i];
      inner.appendChild(group(data.crossp[tpl][tr + '|' + dep([tr], vk)],
        { 'class': 'app-mpl', transform: 'translate(' + slot[0] + ' ' + slot[1] + ')' }));
    });
    if (!intro) {
      var note = el('text', { x: B.x + B.w - 28, y: B.y + B.h - 22, 'text-anchor': 'end', 'font-size': 24, 'class': 'app-note' }, box);
      note.textContent = 'Esc to close';
    }
    if (!instant && g.animate && !ctx.still()) try { g.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 160, easing: 'ease-out' }); } catch (e) { /* static */ }
    card = { g: g, box: box, veil: veil, B: B, key: key, intro: !!intro, tpl: tpl, vk: vk };
    onCard(B);
    axesFor();
    if (intro) return;
    ctx.keyboard(false);
    document.addEventListener('keydown', onKey, true);
    document.addEventListener('pointerdown', onDown, true);
    svg.setAttribute('data-open', key);
  }
  function closeCard() {
    if (!card) return;
    var intro = card.intro;
    svg.removeChild(card.g);
    card = null;
    restPlace();
    axesFor();
    if (intro) return;
    ctx.keyboard(true);
    document.removeEventListener('keydown', onKey, true);
    document.removeEventListener('pointerdown', onDown, true);
    svg.removeAttribute('data-open');
  }
  // a pair's tracers in reading order: source bins first, lower bin first, kappa last
  function sortTracers(t) {
    var rank = function (x) { return x === 'kappa' ? 100 : (x[0] === 'l' ? 0 : 10) + parseInt(x.slice(1), 10); };
    return t.slice().sort(function (a, b) { return rank(a) - rank(b); });
  }

  function redraw() {
    var open = card && card.key, intro = card && card.intro;
    draw();
    if (open) openCard(open, true, intro);
  }
  function setTemplate(t) { if (t === tpl) return; tpl = t; markChoice(); redraw(); }
  function use(k) { if (k === vk || data.variants.indexOf(k) < 0) return; vk = k; redraw(); }

  // ── steps ───────────────────────────────────────────────────────────────
  function step(k, animate) {
    k = Math.max(0, Math.min(1, k));
    if (card && !card.intro) closeCard();
    if (k !== 1) hl.style.visibility = 'hidden';
    var from = state;
    state = k;
    axesFor();
    if (!animate || from == null || from === k) { land(k); return; }
    if (ctx.still()) {
      // reduced motion: the old view, frozen, fades out over the new one
      var ghost = svg.cloneNode(true);
      ghost.removeAttribute('data-rest');
      ghost.style.pointerEvents = 'none';
      svg.parentNode.insertBefore(ghost, svg.nextSibling);
      land(k);
      var gone = function () { if (ghost.parentNode) ghost.parentNode.removeChild(ghost); };
      try { ghost.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 450, easing: 'ease-in-out', fill: 'forwards' }).finished.then(gone, gone); }
      catch (e) { gone(); }
      return;
    }
    fly(k);
  }

  markChoice();
  draw();
  land(0);
  state = 0;
  if (ctx.variants) ctx.variants(data.variants, use);
  return {
    step: step,
    leave: function () { if (card && !card.intro) closeCard(); },
    open: function (key) { openCard(key); },
    template: setTemplate,
  };
});
