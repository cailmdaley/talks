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
    plugins: [RevealNotes],
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
    if (chip) { open(chip.closest('section'), chip.getAttribute('data-open')); e.stopPropagation(); return; }
    if (e.target.closest('.slide.detail .close')) { close(); e.stopPropagation(); }
  }, true);

  document.addEventListener('keydown', function (e) {
    if (openDetail && (e.key === 'Escape' || e.key === 'Backspace')) { close(); e.preventDefault(); e.stopPropagation(); }
  }, true);

  Reveal.addKeyBinding({ keyCode: 68, key: 'D', description: 'Open this slide\'s first detail' }, function () {
    var s = Reveal.getCurrentSlide();
    if (s && s.querySelector(':scope > .slide.detail')) open(s, '0');
  });

  Reveal.on('slidechanged', close);

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
    open: open, close: close, settle: settle,
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
