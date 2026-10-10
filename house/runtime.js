// House deck runtime: reveal configuration and depth-on-demand overlays.
(function () {
  Reveal.initialize({
    width: 1920,
    height: 1080,
    margin: 0,
    minScale: 0.05,
    maxScale: 4,
    center: false,
    hash: true,
    history: false,
    controls: false,
    progress: true,
    slideNumber: false,
    transition: 'none',
    backgroundTransition: 'none',
    pdfSeparateFragments: true,
    pdfMaxPagesPerSlide: 1,
  });

  var openDetail = null;

  function close() {
    if (!openDetail) return;
    openDetail.classList.remove('open');
    openDetail = null;
    Reveal.configure({ keyboard: true });
  }

  function open(section, k) {
    close();
    var d = section.querySelector(':scope > .slide.detail[data-detail="' + k + '"]');
    if (!d) return;
    d.classList.add('open');
    openDetail = d;
    Reveal.configure({ keyboard: false });
  }

  document.addEventListener('click', function (e) {
    var chip = e.target.closest('.chip[data-open], .slide:not(.detail) [data-open]');
    if (chip) { hidePeek(); open(chip.closest('section'), chip.getAttribute('data-open')); e.stopPropagation(); return; }
    if (e.target.closest('.slide.detail .close') || e.target.matches('.slide.detail.notes.open')) { close(); e.stopPropagation(); }
  }, true);

  document.addEventListener('keydown', function (e) {
    if (openDetail && (e.key === 'Escape' || e.key === 'Backspace')) { close(); e.preventDefault(); e.stopPropagation(); }
  }, true);

  Reveal.addKeyBinding({ keyCode: 78, key: 'N', description: 'Open this slide\'s sources & notes' }, function () {
    var s = Reveal.getCurrentSlide();
    if (s && s.querySelector(':scope > .slide.detail.notes')) open(s, 'notes');
  });

  Reveal.addKeyBinding({ keyCode: 68, key: 'D', description: 'Open this slide\'s first detail' }, function () {
    var s = Reveal.getCurrentSlide();
    if (s && s.querySelector(':scope > .slide.detail[data-detail="0"]')) open(s, '0');
  });

  Reveal.on('slidechanged', close);

  // ── Peek: hovering an element that opens a detail shows the detail as a
  // popout beside it. The popout stays while the pointer is on the element or
  // on the popout, and lingers a moment after it leaves both, so the pointer
  // can cross the gap between them; a click opens the detail whole.
  var PEEK_IN = 90, PEEK_OUT = 380, PEEK_GAP = 18;
  var peek = null, peekFor = null, peekIn = 0, peekOut = 0;

  function peekCard(section, k) {
    var d = section.querySelector(':scope > .slide.detail[data-detail="' + k + '"]');
    if (!d) return null;
    var card = document.createElement('div');
    card.className = 'peek';
    var h = d.querySelector(':scope > h2');
    if (h) { var t = document.createElement('h3'); t.innerHTML = h.innerHTML; card.appendChild(t); }
    var text = d.querySelector(':scope > .body .text');
    if (text) card.appendChild(text.cloneNode(true));
    var figs = d.querySelectorAll(':scope > .body .people figure');
    if (figs.length) {
      var row = document.createElement('div');
      row.className = 'peek-people';
      figs.forEach(function (f) { row.appendChild(f.cloneNode(true)); });
      card.appendChild(row);
    }
    var hint = document.createElement('p');
    hint.className = 'peek-hint';
    hint.textContent = 'click to open';
    card.appendChild(hint);
    card.addEventListener('pointerenter', function () { clearTimeout(peekOut); });
    card.addEventListener('pointerleave', hidePeekSoon);
    card.addEventListener('click', function (e) {
      var s = peekFor && peekFor.closest('section'), key = peekFor && peekFor.getAttribute('data-open');
      hidePeek();
      if (s) open(s, key);
      e.stopPropagation();
    });
    return card;
  }

  function placePeek(card, el, section) {
    var scale = Reveal.getScale() || 1;
    var sr = section.getBoundingClientRect(), er = el.getBoundingClientRect();
    var W = 1920, H = 1080;
    var box = { l: (er.left - sr.left) / scale, t: (er.top - sr.top) / scale,
                w: er.width / scale, h: er.height / scale };
    var cw = card.offsetWidth, ch = card.offsetHeight;
    // beside the element, on whichever side has room; else below or above it
    var x, y;
    if (box.l + box.w + PEEK_GAP + cw <= W - 24) x = box.l + box.w + PEEK_GAP;
    else if (box.l - PEEK_GAP - cw >= 24) x = box.l - PEEK_GAP - cw;
    if (x !== undefined) y = Math.min(Math.max(box.t + box.h / 2 - ch / 2, 24), H - ch - 24);
    else {
      x = Math.min(Math.max(box.l + box.w / 2 - cw / 2, 24), W - cw - 24);
      y = box.t + box.h + PEEK_GAP + ch <= H - 24 ? box.t + box.h + PEEK_GAP : Math.max(box.t - PEEK_GAP - ch, 24);
    }
    card.style.left = x + 'px';
    card.style.top = y + 'px';
  }

  function showPeek(el) {
    if (openDetail || peekFor === el) return;
    hidePeek();
    var section = el.closest('section');
    var card = peekCard(section, el.getAttribute('data-open'));
    if (!card) return;
    section.appendChild(card);
    placePeek(card, el, section);
    card.classList.add('shown');
    el.classList.add('peeking');
    peek = card; peekFor = el;
  }

  function hidePeek() {
    clearTimeout(peekIn); clearTimeout(peekOut);
    if (peek) peek.remove();
    if (peekFor) peekFor.classList.remove('peeking');
    peek = null; peekFor = null;
  }

  function hidePeekSoon() {
    clearTimeout(peekIn); clearTimeout(peekOut);
    if (peek && peek.classList.contains('stepped')) return;  // a stepped popout stays for its step
    peekOut = setTimeout(hidePeek, PEEK_OUT);
  }

  document.addEventListener('pointerover', function (e) {
    if (e.pointerType === 'touch') return;
    var el = e.target.closest && e.target.closest('.slide:not(.detail) [data-open]:not(.chip):not(.notes-open)');
    if (!el) return;
    clearTimeout(peekOut);
    if (peekFor === el) return;
    clearTimeout(peekIn);
    peekIn = setTimeout(function () { showPeek(el); }, peek ? 0 : PEEK_IN);
  });
  document.addEventListener('pointerout', function (e) {
    var el = e.target.closest && e.target.closest('.slide:not(.detail) [data-open]:not(.chip):not(.notes-open)');
    if (!el || (e.relatedTarget && el.contains(e.relatedTarget))) return;
    if (peekFor === el) hidePeekSoon(); else clearTimeout(peekIn);
  });
  Reveal.on('slidechanged', hidePeek);
  Reveal.on('fragmentshown', hidePeek);
  Reveal.on('fragmenthidden', hidePeek);

  // ── Stepped popouts: an element that opens a detail and carries
  // data-peek-at="x y w" shows that detail's popout unasked while it is the
  // slide's latest step: a fragment (or an element inside one) while that
  // fragment is current, an element outside every fragment while no fragment
  // is shown. The card's top-left corner sits at (x, y) and its width is w, in
  // the units of the SVG the element is drawn in; hover and click work as for
  // any opener. A later step without one clears it.
  function stepPeek() {
    var s = Reveal.getCurrentSlide();
    if (!s || openDetail) return;
    var frame = s.querySelector(':scope > .slide:not(.detail)');
    if (!frame) return;
    var els = Array.prototype.slice.call(frame.querySelectorAll('[data-peek-at][data-open]'));
    var anyShown = frame.querySelector('.fragment.visible');
    var cur = els.filter(function (e) {
      var f = e.classList.contains('fragment') ? e : e.closest('.fragment');
      return f ? f.classList.contains('current-fragment') : !anyShown;
    })[0] || null;
    if (peek && peek.classList.contains('stepped') && peekFor !== cur) hidePeek();
    if (!cur || peekFor === cur) return;
    showPeek(cur);
    if (!peek) return;
    peek.classList.add('stepped');
    var a = cur.getAttribute('data-peek-at').trim().split(/[\s,]+/).map(Number);
    var svg = cur.ownerSVGElement || cur.closest('svg');
    var m = svg && svg.getScreenCTM();
    if (!m || a.length < 2) return;
    var scale = Reveal.getScale() || 1, sr = s.getBoundingClientRect();
    var p = svg.createSVGPoint(); p.x = a[0]; p.y = a[1]; p = p.matrixTransform(m);
    if (a[2]) peek.style.width = (a[2] * m.a / scale) + 'px';
    peek.style.left = ((p.x - sr.left) / scale) + 'px';
    peek.style.top = ((p.y - sr.top) / scale) + 'px';
    // portraits in balanced rows (3 + 3, not 5 + 1)
    var row = peek.querySelector('.peek-people'), figs = row ? row.children : [];
    if (figs.length > 1) {
      var fw = figs[0].offsetWidth, gap = parseFloat(getComputedStyle(row).columnGap) || 0;
      var per = Math.max(1, Math.floor((row.clientWidth + gap) / (fw + gap)));
      var cols = Math.ceil(figs.length / Math.ceil(figs.length / per));
      row.style.maxWidth = (cols * fw + (cols - 1) * gap + 1) + 'px';
    }
  }
  ['ready', 'slidechanged', 'fragmentshown', 'fragmenthidden'].forEach(function (ev) {
    Reveal.on(ev, function () { setTimeout(stepPeek, 0); });
  });
  // closing a detail brings back the step's popout
  var closeDetail = close;
  close = function () { var was = openDetail; closeDetail(); if (was) setTimeout(stepPeek, 0); };

  // ── Prism: a figure stack whose steps turn like the faces of a prism ──
  // <figure data-prism> holds a stack; each step turns the stack about its
  // horizontal axis to bring the next face round, and a face with
  // data-zoom="x y w h" instead arrives by zooming out, the previous face
  // shrinking into that box of it (percent of the image). The rest states are
  // the plain stack: this only animates the step between two of them, so the
  // report, a PDF and a reader who prefers reduced motion see the stack (and
  // reveal's fade between its frames).
  var TURN_MS = 950, ZOOM_MS = 1300, EASE = 'cubic-bezier(0.65, 0, 0.35, 1)';
  var still = window.matchMedia('(prefers-reduced-motion: reduce)');
  var running = [];

  function settle() {
    running.forEach(function (a) { a.finish(); });
    running = [];
  }

  function zoomBox(img) {
    var b = (img.getAttribute('data-zoom') || '').trim().split(/[\s,]+/).map(Number);
    return b.length === 4 && b.every(isFinite) ? b : null;
  }

  // the two faces, lower one first, animate from the lower to the upper state
  // (played backwards for a step back); the others hide for the duration
  function step(frame, lo, hi, back) {
    var faces = Array.prototype.slice.call(frame.querySelectorAll(':scope > img'));
    var anims = [];
    var common = { easing: EASE, direction: back ? 'reverse' : 'normal' };
    var box = zoomBox(hi);
    var token = frame.prismStep = {};
    var clear = function () {
      frame.classList.remove('turning', 'zooming', 'rolling');
      faces.forEach(function (f) { f.classList.remove('prism-off'); });
    };
    clear();
    frame.classList.add('turning', box ? 'zooming' : 'rolling');
    faces.forEach(function (f) { if (f !== lo && f !== hi) f.classList.add('prism-off'); });
    var shown = { opacity: 1, visibility: 'visible' };
    if (box) {
      // M = translate(x%, y%) scale(w/100, h/100) about the top left maps a
      // face onto the box; the previous face moves by P(t), from identity to
      // M, and the next by M⁻¹ P(t), from M⁻¹ to identity: the same motion
      var sx = box[2] / 100, sy = box[3] / 100;
      var P = function (t) { return 'translate(' + box[0] * t + '%, ' + box[1] * t + '%) scale(' + (1 + (sx - 1) * t) + ', ' + (1 + (sy - 1) * t) + ')'; };
      var inv = 'scale(' + 1 / sx + ', ' + 1 / sy + ') translate(' + -box[0] + '%, ' + -box[1] + '%) ';
      var o = { transformOrigin: '0 0', visibility: 'visible' };
      anims.push(lo.animate([
        Object.assign({ offset: 0, transform: P(0), opacity: 1 }, o),
        Object.assign({ offset: 0.22, opacity: 1 }, o),
        Object.assign({ offset: 0.48, opacity: 0 }, o),
        Object.assign({ offset: 1, transform: P(1), opacity: 0 }, o),
      ], Object.assign({ duration: ZOOM_MS }, common)));
      anims.push(hi.animate([
        Object.assign({ offset: 0, transform: inv + P(0), opacity: 0 }, o),
        Object.assign({ offset: 0.16, opacity: 0 }, o),
        Object.assign({ offset: 0.42, opacity: 1 }, o),
        Object.assign({ offset: 1, transform: inv + P(1), opacity: 1 }, o),
      ], Object.assign({ duration: ZOOM_MS }, common)));
    } else {
      // a prism with the faces on its sides, turning about its axis a depth
      // d behind the screen; it pulls back as it turns, as an object
      // turned in the hand does, and a face darkens as it turns from the light
      var d = frame.offsetHeight / 2, pull = 0.9 * d;
      var face = function (deg, z) { return 'translateZ(' + (-z) + 'px) translateZ(' + (-d) + 'px) rotateX(' + deg + 'deg) translateZ(' + d + 'px)'; };
      var key = function (deg0, z, light) { return Object.assign({ transform: face(deg0, z), filter: 'brightness(' + light + ')', backfaceVisibility: 'hidden' }, shown); };
      anims.push(lo.animate([key(0, 0, 1), key(45, pull, 0.86), key(90, 0, 0.55)], Object.assign({ duration: TURN_MS }, common)));
      anims.push(hi.animate([key(-90, 0, 0.55), key(-45, pull, 0.86), key(0, 0, 1)], Object.assign({ duration: TURN_MS }, common)));
    }
    running = anims;
    // a later step on the same frame owns its classes; only the latest clears them
    Promise.all(anims.map(function (a) { return a.finished; })).catch(function () {}).then(function () {
      if (frame.prismStep === token) clear();
    });
  }

  function onFragment(back) {
    return function (e) {
      settle();
      if (still.matches || (Reveal.isPrintView && Reveal.isPrintView())) return;
      // only a single step turns; a jump (a slide entered mid-way) just lands
      var faces = (e.fragments || []).filter(function (f) { return f.localName === 'img' && f.closest('figure[data-prism]'); });
      if (faces.length !== 1 || e.fragments.length !== 1) return;
      var hi = faces[0], lo = hi.previousElementSibling;
      while (lo && lo.localName !== 'img') lo = lo.previousElementSibling;
      if (lo) step(hi.parentElement, lo, hi, back);
    };
  }
  Reveal.on('fragmentshown', onFragment(false));
  Reveal.on('fragmenthidden', onFragment(true));
  Reveal.on('slidechanged', settle);

  // ── Apps: <figure data-app> drawn live by a script the build inlines ──
  // A script registers House.app(name, factory); factory(figure, data, ctx)
  // draws into the figure and returns { step(k, animate), leave() }. k is the
  // number of the figure's fragments shown, so the figure's fallback stack
  // drives the steps; animate is true for a single step forward or back
  // (false on a jump, a slide entered mid-way or a PDF). ctx.still() is true
  // when the reader prefers reduced motion: the app crossfades instead.
  var apps = {};
  function stepOf(fig) { return fig.querySelectorAll('.fragment.visible').length; }
  function mountApps() {
    if (!Reveal.isReady()) return;
    document.querySelectorAll('figure[data-app]').forEach(function (fig) {
      var factory = apps[fig.getAttribute('data-app')];
      if (fig.houseApp || !factory) return;
      // a copy made after mounting (reveal's print view clones each fragment
      // state) carries a frozen drawing: replace it with a live one
      fig.querySelectorAll('.app-view').forEach(function (v) { v.parentNode.removeChild(v); });
      var el = document.getElementById('house-data-' + fig.getAttribute('data-app-data'));
      var ctx = {
        keyboard: function (on) { Reveal.configure({ keyboard: on }); },
        still: function () { return still.matches; },
        // the app has these variants and draws one when asked; the deck's control
        // and shared choice drive it
        variants: function (keys, apply) {
          vOffer(fig.closest('.slide'), { has: function (k) { return keys.indexOf(k) >= 0; }, apply: apply });
        },
        // the axes the view on screen depends on (e.g. ['cmb'] on a clustering-only
        // panel); null returns to the slide's own data-variant-axes
        axes: function (list) { vSetAxes(fig.closest('.slide'), list); },
      };
      fig.houseApp = factory(fig, el ? JSON.parse(el.textContent) : null, ctx);
      fig.classList.add('app-live');
      fig.houseApp.step(stepOf(fig), false);
    });
  }
  function appFragments(e) {
    var done = [];
    (e.fragments || []).forEach(function (f) {
      var fig = f.closest('figure.app-live');
      if (!fig || done.indexOf(fig) >= 0) return;
      done.push(fig);
      fig.houseApp.step(stepOf(fig), e.fragments.length === 1 && !(Reveal.isPrintView && Reveal.isPrintView()));
    });
  }
  Reveal.on('ready', mountApps);
  Reveal.on('pdf-ready', mountApps);
  Reveal.on('fragmentshown', appFragments);
  Reveal.on('fragmenthidden', appFragments);
  Reveal.on('slidechanged', function (e) {
    if (e.previousSlide) e.previousSlide.querySelectorAll('figure.app-live').forEach(function (f) { if (f.houseApp.leave) f.houseApp.leave(); });
    e.currentSlide.querySelectorAll('figure.app-live').forEach(function (f) { f.houseApp.step(stepOf(f), false); });
  });

  // ── Variants: one choice per axis (deck.json "variants"), shared by the deck ──
  // A slide takes part when an <img> carries data-alt (the build maps each variant
  // it has to an asset), when an element carries data-variant (shown only for
  // those variants), or when an app offers variants through ctx.variants(keys, apply).
  // Each such slide gets one control in its bottom-right corner, a segmented
  // button group per axis. A choice made on any slide is the deck's choice: every
  // other slide shows it too, or its default where it lacks that variant, and its
  // control shows which variant is on screen. A variant a slide lacks is offered
  // disabled. A slide whose content depends on only some axes names them in
  // data-variant-axes="cmb" (an app can change this per view with ctx.axes); the
  // other axes' segments stay visible but faded and inert, still showing the
  // deck's choice, which they leave untouched. The report and a PDF show the default.
  var VDEF = (function () { var el = document.getElementById('house-variants'); return el ? JSON.parse(el.textContent) : null; })();
  var vAxes = VDEF ? Object.keys(VDEF) : [];
  var vState = {};
  vAxes.forEach(function (a) { vState[a] = Object.keys(VDEF[a])[0]; });
  var vKey = function (s) { return vAxes.map(function (a) { return s[a]; }).join('|'); };
  var V0 = vKey(vState);
  var vFrames = [];              // { frame, offers: [{ has(key), apply(key) }], control }
  var printing = function () { return !!(Reveal.isPrintView && Reveal.isPrintView()); };

  function vFrame(frame) {
    for (var i = 0; i < vFrames.length; i++) if (vFrames[i].frame === frame) return vFrames[i];
    var own = frame.getAttribute('data-variant-axes');
    var f = { frame: frame, offers: [], control: null, own: own ? own.trim().split(/\s+/) : null, app: null };
    vFrames.push(f);
    return f;
  }
  function vHas(f, key) { return key === V0 || f.offers.every(function (o) { return o.has(key); }); }
  function vLive(f) { var l = f.app || f.own; return l ? vAxes.filter(function (a) { return l.indexOf(a) >= 0; }) : vAxes; }
  // the variant on screen: the deck's choice; where the slide lacks it, the
  // choice on the live axes with the idle ones at their default; else the default
  function vShown(f) {
    var k = vKey(vState);
    if (vHas(f, k)) return k;
    var live = vLive(f), s = {};
    vAxes.forEach(function (a) { s[a] = live.indexOf(a) >= 0 ? vState[a] : Object.keys(VDEF[a])[0]; });
    k = vKey(s);
    return vHas(f, k) ? k : V0;
  }

  function vControl(f) {
    var c = document.createElement('div');
    c.className = 'variants';
    c.setAttribute('role', 'group');
    c.setAttribute('aria-label', 'Variant');
    vAxes.forEach(function (a) {
      var seg = document.createElement('span');
      seg.className = 'seg';
      seg.setAttribute('data-axis', a);
      Object.keys(VDEF[a]).forEach(function (o) {
        var b = document.createElement('button');
        b.type = 'button';
        b.textContent = VDEF[a][o];
        b.setAttribute('data-axis', a);
        b.setAttribute('data-option', o);
        b.addEventListener('click', function (e) { e.stopPropagation(); House.setVariant(a, o); });
        seg.appendChild(b);
      });
      c.appendChild(seg);
    });
    f.frame.appendChild(c);
    return c;
  }

  function vRender(f) {
    var key = printing() ? V0 : vShown(f);
    f.offers.forEach(function (o) { o.apply(key); });
    if (!f.control) return;
    var parts = key.split('|'), live = vLive(f);
    f.control.querySelectorAll('.seg').forEach(function (seg) {
      seg.classList.toggle('idle', live.indexOf(seg.getAttribute('data-axis')) < 0);
    });
    f.control.querySelectorAll('button').forEach(function (b) {
      var a = b.getAttribute('data-axis'), i = vAxes.indexOf(a), o = b.getAttribute('data-option');
      if (live.indexOf(a) < 0) {
        // an axis this view does not depend on: inert, showing the deck's choice
        var mine = vState[a] === o;
        b.classList.toggle('on', mine);
        b.disabled = true;
        b.title = 'this view does not depend on it';
        b.setAttribute('aria-pressed', mine ? 'true' : 'false');
        return;
      }
      var want = parts.slice();
      want[i] = o;
      var on = parts[i] === o, has = vHas(f, want.join('|'));
      b.classList.toggle('on', on);
      b.disabled = !has;
      b.title = has ? '' : b.textContent + ': not available on this slide';
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  function vOffer(frame, offer) {
    if (!VDEF || !frame) return;
    var f = vFrame(frame);
    f.offers.push(offer);
    if (!f.control && !printing()) f.control = vControl(f);
    vRender(f);
  }

  function vSetAxes(frame, list) {
    if (!VDEF || !frame) return;
    var f = vFrame(frame);
    f.app = list ? list.slice() : null;
    vRender(f);
  }

  function mountVariants() {
    if (!VDEF || !Reveal.isReady()) return;
    document.querySelectorAll('.reveal .slides .slide').forEach(function (frame) {
      if (frame.houseVariants) return;
      frame.houseVariants = true;
      var imgs = Array.prototype.slice.call(frame.querySelectorAll('img[data-alt]'));
      var texts = Array.prototype.slice.call(frame.querySelectorAll('[data-variant]'));
      if (!imgs.length && !texts.length) return;
      var maps = imgs.map(function (i) { try { return JSON.parse(i.getAttribute('data-alt')); } catch (e) { return {}; } });
      vOffer(frame, {
        has: function (key) { return maps.every(function (m) { return key in m; }); },
        apply: function (key) {
          var A = window.HouseAssets || {};
          imgs.forEach(function (img, n) {
            var asset = key === V0 ? img.getAttribute('data-asset') : maps[n][key];
            if (asset && A[asset] && img.getAttribute('src') !== A[asset]) img.setAttribute('src', A[asset]);
          });
          texts.forEach(function (el) {
            var show = el.getAttribute('data-variant').trim().split(/\s+/).indexOf(key) >= 0;
            if (show) el.removeAttribute('data-hide'); else el.setAttribute('data-hide', '');
          });
        },
      });
    });
  }
  Reveal.on('ready', mountVariants);
  Reveal.on('pdf-ready', mountVariants);

  // Hooks for the checker, for scripted capture and for app scripts.
  window.House = {
    open: open, close: function () { close(); }, settle: settle, stepPeek: stepPeek,
    app: function (name, factory) { apps[name] = factory; mountApps(); },
    variant: function () { return vKey(vState); },
    variantDefault: function () { return V0; },
    setVariant: function (axis, option) {
      if (!VDEF || !(axis in VDEF) || !(option in VDEF[axis])) return;
      vState[axis] = option;
      vFrames.forEach(vRender);
    },
  };
})();
