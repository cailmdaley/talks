// Template contamination of the blinded TR1 3x2pt + kappa data vector (house data-app):
// for a chosen systematics template, X_l^{ab} / sigma_G for every pair, as a triangle
// of panels laid out cell for cell like the dv-vector slide's.
//
// Nothing is drawn here: private/render_systematics.py renders every panel with
// matplotlib as SVG, and this script places and swaps them. The app's own control
// (top right of the triangle) picks the template; the deck's variant control picks
// the shear method and CMB map. A click on a cell opens its card: the pair's X / sigma_G
// along the bottom and the template's cross with each of its tracers above (Esc,
// Backspace or a click outside closes it). The variant axes the view depends on follow
// the card: a lens-bin-only pair depends on neither, a shear tracer on the shear
// method, kappa on the CMB map.
// Data: private/systematics_app.json.
House.app('systematics', function (figure, data, ctx) {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';
  var W = data.world.w, H = data.world.h, DW = data.detail.w, DH = data.detail.h;
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

  var defs = el('svg', { width: 0, height: 0, 'aria-hidden': 'true' });
  defs.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden;';
  defs.appendChild(parse('<svg xmlns="' + NS + '"><defs>' + data.glyphs + '</defs></svg>').firstChild);
  el('style', {}, defs).textContent = data.css;
  frameEl.appendChild(defs);

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
  choice.style.left = (100 * data.choice.x / W) + '%';
  choice.style.top = (100 * data.choice.y / H) + '%';
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
  frameEl.appendChild(choice);
  function markChoice() {
    seg.querySelectorAll('button').forEach(function (b) {
      var on = b.getAttribute('data-option') === tpl;
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  // ── the triangle, its hover and the card ─────────────────────────────────
  var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, 'class': 'app-view', role: 'img' });
  frameEl.insertBefore(svg, choice);
  var layer = el('g', { 'class': 'app-mpl' }, svg);
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
    while (layer.firstChild) layer.removeChild(layer.firstChild);
    var src = group(data.over[tpl][vk], {});
    while (src.firstChild) layer.appendChild(src.firstChild);
    svg.setAttribute('data-template', tpl);
    svg.setAttribute('data-variant', vk);
  }

  var card = null;
  function onKey(e) { if (e.key === 'Escape' || e.key === 'Backspace') { closeCard(); e.preventDefault(); e.stopPropagation(); } }
  function onDown(e) {
    if (card && !card.box.contains(e.target) && !e.target.closest('.variants')) { closeCard(); e.stopPropagation(); e.preventDefault(); }
  }
  function openCard(key, instant) {
    closeCard();
    var t = key.split('_');
    var g = el('g', {}, svg);
    el('rect', { x: 0, y: 0, width: W, height: H, 'class': 'fill-ground', opacity: 0.85 }, g);
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
    var note = el('text', { x: B.x + B.w - 28, y: B.y + B.h - 22, 'text-anchor': 'end', 'font-size': 24, 'class': 'app-note' }, box);
    note.textContent = 'Esc to close';
    if (!instant && g.animate && !ctx.still()) try { g.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 160, easing: 'ease-out' }); } catch (e) { /* static */ }
    card = { g: g, box: box, key: key };
    choice.style.visibility = 'hidden';
    if (ctx.axes) ctx.axes(axesOf(t));
    ctx.keyboard(false);
    document.addEventListener('keydown', onKey, true);
    document.addEventListener('pointerdown', onDown, true);
    svg.setAttribute('data-open', key);
  }
  function closeCard() {
    if (!card) return;
    svg.removeChild(card.g);
    card = null;
    choice.style.visibility = '';
    if (ctx.axes) ctx.axes(null);
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
    var open = card && card.key;
    draw();
    if (open) openCard(open, true);
  }
  function setTemplate(t) { if (t === tpl) return; tpl = t; markChoice(); redraw(); }
  function use(k) { if (k === vk || data.variants.indexOf(k) < 0) return; vk = k; redraw(); }

  markChoice();
  draw();
  if (ctx.variants) ctx.variants(data.variants, use);
  return {
    step: function () {},
    leave: function () { closeCard(); },
    open: function (key) { openCard(key); },
    template: setTemplate,
  };
});
