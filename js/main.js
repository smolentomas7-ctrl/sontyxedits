(function () {
  "use strict";

  var DEFAULT_LANG = "en";
  var STORE_KEY = "sontyx-lang";
  var dict = window.SONTYX_I18N || {};
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── Language ──────────────────────────────────────── */

  function lookup(lang, path) {
    return path.split(".").reduce(function (obj, key) {
      return obj && obj[key] !== undefined ? obj[key] : null;
    }, dict[lang]);
  }

  function setLanguage(lang) {
    if (!dict[lang]) lang = DEFAULT_LANG;

    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var value = lookup(lang, el.getAttribute("data-i18n"));
      if (typeof value === "string") el.textContent = value;
    });

    var title = lookup(lang, "meta.title");
    var desc = lookup(lang, "meta.description");
    if (title) document.title = title;

    var descTag = document.querySelector('meta[name="description"]');
    if (descTag && desc) descTag.setAttribute("content", desc);

    document.documentElement.lang = lang;
    document.documentElement.setAttribute("data-lang", lang);

    document.querySelectorAll("[data-lang-btn]").forEach(function (btn, index) {
      var active = btn.getAttribute("data-lang-btn") === lang;
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-pressed", String(active));
      if (active) moveThumb(btn, index);
    });

    try { localStorage.setItem(STORE_KEY, lang); } catch (e) { /* private mode */ }
  }

  function moveThumb(btn, index) {
    var thumb = btn.parentElement.querySelector(".segmented__thumb");
    if (thumb) thumb.style.transform = "translateX(" + index * 100 + "%)";
  }

  document.querySelectorAll("[data-lang-btn]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      setLanguage(btn.getAttribute("data-lang-btn"));
    });
  });

  var stored = null;
  try { stored = localStorage.getItem(STORE_KEY); } catch (e) { /* private mode */ }
  setLanguage(stored || DEFAULT_LANG);

  /* ── Nav state on scroll ───────────────────────────── */

  var nav = document.getElementById("nav");
  var onScroll = function () {
    nav.classList.toggle("is-scrolled", window.scrollY > 24);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ── Scroll reveal ─────────────────────────────────── */

  var revealables = document.querySelectorAll(".reveal");

  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealables.forEach(function (el) { el.classList.add("is-in"); });
  } else {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry, i) {
        if (!entry.isIntersecting) return;
        setTimeout(function () { entry.target.classList.add("is-in"); }, i * 70);
        revealObserver.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -60px 0px" });

    revealables.forEach(function (el) { revealObserver.observe(el); });
  }

  /* ── Stat counters ─────────────────────────────────── */

  var stats = document.querySelectorAll(".stat__num[data-count]");

  function countUp(el) {
    var target = parseInt(el.getAttribute("data-count"), 10);
    var suffix = el.getAttribute("data-suffix") || "";
    var duration = 1400;
    var start = performance.now();

    function frame(now) {
      var progress = Math.min((now - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (progress < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  if (!reduceMotion && "IntersectionObserver" in window) {
    var statObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        countUp(entry.target);
        statObserver.unobserve(entry.target);
      });
    }, { threshold: 0.6 });

    stats.forEach(function (el) { statObserver.observe(el); });
  }

  /* ── Portfolio hover preview ───────────────────────── */
  /* A card plays a clip only if it carries data-video="path/to/clip.mp4". */

  document.querySelectorAll(".work-card").forEach(function (card) {
    var src = card.getAttribute("data-video");
    if (!src) return;

    var video = null;

    function build() {
      if (video) return video;
      video = document.createElement("video");
      video.src = src;
      video.muted = true;
      video.loop = true;
      video.playsInline = true;
      video.preload = "none";
      video.setAttribute("aria-hidden", "true");
      var poster = card.getAttribute("data-poster");
      if (poster) video.poster = poster;
      card.querySelector(".work-card__media").appendChild(video);
      return video;
    }

    function play() {
      var v = build();
      var attempt = v.play();
      if (attempt && attempt.catch) attempt.catch(function () { /* autoplay blocked */ });
      card.classList.add("is-playing");
    }

    function stop() {
      if (!video) return;
      video.pause();
      video.currentTime = 0;
      card.classList.remove("is-playing");
    }

    card.addEventListener("mouseenter", play);
    card.addEventListener("mouseleave", stop);
    card.addEventListener("focusin", play);
    card.addEventListener("focusout", stop);
  });

  /* ── Footer year ───────────────────────────────────── */

  var year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();
})();
