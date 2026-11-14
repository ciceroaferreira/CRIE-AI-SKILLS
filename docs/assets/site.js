// Language toggle (pt/en) + copy buttons. Works without JS: both languages are in the HTML; default pt.
(function () {
  var root = document.documentElement;
  function pick() {
    var h = (location.hash || "").replace("#", "");
    if (h === "en" || h === "pt") return h;
    try { var s = localStorage.getItem("crie-lang"); if (s === "en" || s === "pt") return s; } catch (e) {}
    var nav = (navigator.language || "").toLowerCase();
    return nav.indexOf("pt") === 0 ? "pt" : (nav ? "en" : "pt");
  }
  function set(l) {
    root.setAttribute("data-lang", l);
    root.setAttribute("lang", l === "en" ? "en" : "pt-BR");
    document.querySelectorAll(".langbar button").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.lang === l)); });
    document.querySelectorAll(".copy").forEach(function (b) { b.textContent = l === "en" ? "Copy" : "Copiar"; });
    try { localStorage.setItem("crie-lang", l); } catch (e) {}
    document.dispatchEvent(new CustomEvent("langchange", { detail: l }));
  }
  window.crieLang = function () { return root.getAttribute("data-lang") || "pt"; };
  document.addEventListener("DOMContentLoaded", function () {
    set(pick());
    document.querySelectorAll(".langbar button").forEach(function (b) { b.addEventListener("click", function () { set(b.dataset.lang); }); });
    document.addEventListener("click", function (ev) {
      var btn = ev.target.closest(".copy"); if (!btn) return;
      var txt = btn.parentElement.querySelector("code, .t") ? btn.parentElement.querySelector("code, .t").textContent : btn.parentElement.textContent.replace(btn.textContent, "");
      var done = function () { var o = btn.textContent; btn.textContent = crieLang() === "en" ? "Copied" : "Copiado"; setTimeout(function () { btn.textContent = o; }, 1400); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt.trim()).then(done, function () {});
    });
  });
  window.addEventListener("hashchange", function () { var h = location.hash.replace("#", ""); if (h === "en" || h === "pt") set(h); });
})();
