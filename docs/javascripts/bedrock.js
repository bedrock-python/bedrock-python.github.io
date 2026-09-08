/* Bedrock Python — small enhancements.
 *
 * 1. Live package versions. Every element with data-pypi="<package>" ships
 *    with the version that was current when the page was written; on load it
 *    is replaced with whatever PyPI reports now, so the catalog does not go
 *    stale between site deploys. Any failure leaves the static text in place.
 *
 * 2. Links to other sites open in a new tab; anything on our own host
 *    (this site and every library's docs under bedrock-python.github.io)
 *    stays in the current tab. The host comes from the canonical link, so
 *    a local `zensical serve` behaves like production. An author-set
 *    target is left alone.
 *
 * 3. Wire `document$` for instant-navigation compatibility.
 *    Article discovery lives in blog-explorer.js.
 */

const refreshPypiVersions = () => {
  const nodes = document.querySelectorAll("[data-pypi]");
  if (nodes.length === 0) return;

  // One request per package even when it appears on the page more than once.
  const byPackage = new Map();
  nodes.forEach((node) => {
    const pkg = node.dataset.pypi;
    if (!byPackage.has(pkg)) byPackage.set(pkg, []);
    byPackage.get(pkg).push(node);
  });

  byPackage.forEach((targets, pkg) => {
    fetch(`https://pypi.org/pypi/${encodeURIComponent(pkg)}/json`, {
      headers: { Accept: "application/json" },
    })
      .then((response) => (response.ok ? response.json() : null))
      .then((data) => {
        const version = data && data.info && data.info.version;
        if (!version) return;
        targets.forEach((node) => {
          node.textContent = `v${version}`;
        });
      })
      .catch(() => {
        /* Offline or blocked: the static version stays. */
      });
  });
};

const openExternalLinksInNewTab = () => {
  const canonical = document.querySelector('link[rel="canonical"]');
  const siteHost = canonical ? new URL(canonical.href).hostname : location.hostname;
  document
    .querySelectorAll('a[href^="http://"], a[href^="https://"]')
    .forEach((link) => {
      if (link.target) return;
      if (link.hostname === siteHost || link.hostname === location.hostname) return;
      link.target = "_blank";
      link.rel = link.rel ? `${link.rel} noopener` : "noopener";
    });
};

// The fullscreen search overlay needs an explicit exit on touch screens.
const initMobileSearchClose = () => {
  if (!document.querySelector("#__search") || document.querySelector("[data-bdr-search-close]")) return;
  const button = document.createElement("button");
  button.type = "button";
  button.className = "bdr-mobile-search-close";
  button.dataset.bdrSearchClose = "";
  button.textContent = "Close search";
  button.hidden = true;
  button.addEventListener("click", () => {
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    const trigger = document.querySelector('.md-header label[for="__search"]');
    if (trigger) {
      trigger.tabIndex = -1;
      trigger.focus();
    }
  });
  document.body.append(button);

  // Zensical renders search in an open shadow root. Its checkbox alone does
  // not reflect closing with Escape or opening with the keyboard shortcut.
  const searchRoots = new Set();
  const syncSearchState = () => {
    const open = [...searchRoots].some((root) => {
      const input = root.querySelector('[role="combobox"]');
      return input?.getClientRects().length && getComputedStyle(input).pointerEvents !== "none";
    });
    button.hidden = !open;
    const toggle = document.querySelector("#__search");
    if (toggle) toggle.checked = open;
  };
  const observeSearch = () => {
    for (const host of document.body.children) {
      const root = host.shadowRoot;
      if (!root || searchRoots.has(root)) continue;
      searchRoots.add(root);
      new MutationObserver(syncSearchState).observe(root, {
        childList: true, subtree: true, attributes: true,
        attributeFilter: ["class", "style", "hidden"],
      });
    }
    syncSearchState();
  };
  new MutationObserver(observeSearch).observe(document.body, { childList: true });
  observeSearch();
};

const initBedrock = () => {
  refreshPypiVersions();
  openExternalLinksInNewTab();
  initMobileSearchClose();
};

if (typeof document$ !== "undefined") {
  // Material's instant-navigation observable: re-run on every page load.
  document$.subscribe(initBedrock);
} else {
  document.addEventListener("DOMContentLoaded", initBedrock);
}
