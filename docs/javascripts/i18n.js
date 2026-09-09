/* Shared messages and full navigation between independently built editions. */
(() => {
  if (window.bedrockI18n) return;
  const language = document.documentElement.lang || "en";
  const messages = JSON.parse(document.getElementById("bdr-messages")?.textContent || "{}");
  const plurals = new Intl.PluralRules(language);
  const t = (key, values = {}) => {
    let message = messages[key] ?? key;
    if (typeof message === "object") message = message[plurals.select(values.count)] ?? message.other;
    return message.replace(/\{(\w+)\}/g, (match, name) => String(values[name] ?? match));
  };
  window.bedrockI18n = { language, t };

  const updateLinks = () => {
    const pageData = document.getElementById("bdr-page-languages");
    if (!pageData) return;
    const translations = JSON.parse(pageData.textContent);
    if (!Object.keys(translations).length) return;
    document.querySelectorAll("[data-language-code]").forEach((old) => {
      const code = old.dataset.languageCode;
      const name = old.dataset.languageName;
      const destination = translations[code];
      const control = document.createElement(destination ? "a" : "span");
      control.dataset.languageCode = code;
      control.dataset.languageName = name;
      const label = document.createElement("span");
      label.lang = code;
      label.textContent = name;
      control.append(label);
      if (destination) {
        control.href = destination.path;
        control.hreflang = code;
        control.lang = code;
        control.dataset.languageLink = "";
        if (code === language) {
          control.setAttribute("aria-current", "true");
          const check = document.createElement("span");
          check.textContent = "✓";
          check.setAttribute("aria-hidden", "true");
          control.append(check);
        }
      } else {
        control.className = "bdr-language__unavailable";
        control.setAttribute("aria-disabled", "true");
        const status = document.createElement("small");
        status.textContent = t("Translation not available");
        control.append(status);
      }
      old.replaceWith(control);
    });
    document.querySelectorAll("[data-language-menu]").forEach((menu) => { menu.open = false; });
  };
  if (typeof document$ !== "undefined") document$.subscribe(updateLinks);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", updateLinks, { once: true });
  else updateLinks();

  // Capture before Zensical's instant navigation. Changing edition must reload
  // the search index and messages, including when returning with browser Back.
  document.addEventListener("click", async (event) => {
    const link = event.target.closest?.("a[data-language-link]");
    if (!link) return;
    event.stopPropagation();
    if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const destination = new URL(link.href);
    if (location.hash && !destination.hash) {
      try {
        const response = await fetch(destination, { signal: AbortSignal.timeout(2000) });
        if (response.ok) {
          const target = new DOMParser().parseFromString(await response.text(), "text/html");
          if (target.getElementById(decodeURIComponent(location.hash.slice(1)))) destination.hash = location.hash;
        }
      } catch { /* The clean page URL remains a valid destination. */ }
    }
    location.assign(destination.href);
  }, true);
  document.addEventListener("click", (event) => {
    document.querySelectorAll("details[data-language-menu][open]").forEach((menu) => {
      if (!menu.contains(event.target)) menu.open = false;
    });
  });
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const menu = document.querySelector("details[data-language-menu][open]");
    if (menu) {
      menu.open = false;
      menu.querySelector("summary").focus();
    }
  });
})();
