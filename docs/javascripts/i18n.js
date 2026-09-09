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

  // Zensical 0.0.58 leaves a few controls outside its theme translations.
  // Keep this adapter limited to controls, never article or search-result text.
  const initNativeMessages = () => {
    const roots = new WeakSet();
    const resultLabels = new WeakMap();
    const setAttribute = (element, name, value) => {
      if (element.getAttribute(name) !== value) element.setAttribute(name, value);
    };
    const localizeSearch = (root) => {
      const input = root.querySelector('input[role="combobox"]');
      if (!input) return;
      setAttribute(input, "placeholder", t("Search"));
      setAttribute(input, "aria-label", t("Search"));
      root.querySelectorAll("h3, h4").forEach((heading) => {
        if (!heading.childElementCount && ["Filters", "Tags"].includes(heading.textContent)) {
          const translated = t(heading.textContent);
          if (heading.textContent !== translated) heading.textContent = translated;
        }
        // Preserve the result-count element and Preact's existing text nodes.
        const count = Number(heading.firstElementChild?.textContent.replace(/[^0-9]/g, ""));
        if (!Number.isFinite(count)) return;
        heading.childNodes.forEach((node) => {
          if (node.nodeType !== Node.TEXT_NODE || (node.data.trim() !== "results" && !resultLabels.has(node))) return;
          if (!resultLabels.has(node)) resultLabels.set(node, [node.data.match(/^\s*/)[0], node.data.match(/\s*$/)[0]]);
          const [before, after] = resultLabels.get(node);
          const translated = before + t("search_result_label", { count }) + after;
          if (node.data !== translated) node.data = translated;
        });
      });
      [[".lucide-search", "Close search"], [".lucide-list-filter", "Search filters"]].forEach(([selector, key]) => {
        const button = root.querySelector(selector)?.closest("button");
        if (button) setAttribute(button, "aria-label", t(key));
      });
    };
    const localizeControls = () => {
      document.querySelectorAll('[data-md-type="select"]').forEach((button) => {
        setAttribute(button, "title", t("Toggle line selection"));
        setAttribute(button, "aria-label", t("Toggle line selection"));
      });
      for (const host of document.body.children) {
        const root = host.shadowRoot;
        if (!root || roots.has(root)) continue;
        roots.add(root);
        new MutationObserver(() => localizeSearch(root)).observe(root, {
          childList: true, subtree: true, characterData: true,
          attributes: true, attributeFilter: ["placeholder"],
        });
        localizeSearch(root);
      }
    };
    new MutationObserver(localizeControls).observe(document.body, { childList: true, subtree: true });
    localizeControls();
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initNativeMessages, { once: true });
  else initNativeMessages();

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
