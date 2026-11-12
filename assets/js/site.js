/* Fish Factory — small progressive enhancements. No dependencies. */
(function () {
  "use strict";

  var root = document.documentElement;
  var isWebView = root.classList.contains("webview");

  /* ---- Mobile navigation ---- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    var setOpen = function (open) {
      nav.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    };
    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setOpen(false);
        toggle.focus();
      }
    });
  }

  /* ---- Copy to clipboard with visible + announced confirmation ---- */
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand("copy") ? resolve() : reject();
      } catch (err) {
        reject(err);
      }
      document.body.removeChild(ta);
    });
  }

  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    var label = btn.querySelector("[data-copy-label]");
    var status = document.getElementById(btn.getAttribute("aria-describedby") || "");
    var idle = label ? label.textContent : "";
    var timer;
    btn.addEventListener("click", function () {
      var value = btn.getAttribute("data-copy");
      copyText(value).then(
        function () {
          btn.classList.add("is-copied");
          if (label) label.textContent = "Copied";
          if (status) status.textContent = value + " copied to clipboard";
        },
        function () {
          if (label) label.textContent = "Press Ctrl/⌘+C";
          if (status) status.textContent = "Copy failed. The address is " + value;
        }
      ).then(function () {
        clearTimeout(timer);
        timer = setTimeout(function () {
          btn.classList.remove("is-copied");
          if (label) label.textContent = idle;
          if (status) status.textContent = "";
        }, 2200);
      });
    });
  });

  /* ---- Documents: open the table of contents on wide screens ---- */
  var toc = document.querySelector("details.toc");
  if (toc && !isWebView && window.matchMedia("(min-width: 64rem)").matches) {
    toc.open = true;
  }

  /* ---- WebView mode: keep ?webview=1 (and theme) when moving between documents ---- */
  if (isWebView) {
    var params = new URLSearchParams(window.location.search);
    document.querySelectorAll("a[href]").forEach(function (a) {
      var href = a.getAttribute("href");
      if (!href || href.charAt(0) === "#" || /^(mailto:|tel:)/i.test(href)) return;
      var url;
      try {
        url = new URL(href, window.location.href);
      } catch (err) {
        return;
      }
      if (url.origin !== window.location.origin) return;
      url.searchParams.set("webview", "1");
      var theme = params.get("theme");
      if (theme) url.searchParams.set("theme", theme);
      a.setAttribute("href", url.pathname + url.search + url.hash);
    });
  }
})();
