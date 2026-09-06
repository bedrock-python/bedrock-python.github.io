/* Bedrock Python — small enhancements.
 *
 * 1. Client-side category filter for the blog index chips.
 *    The "All" chip and category chips (data-bdr-filter="<slug>") filter
 *    cards in the grid by their data-bdr-cat (space-separated).
 *    Real category-page links (e.g. category/libraries/) still navigate.
 *
 * 2. Live package versions. Every element with data-pypi="<package>" ships
 *    with the version that was current when the page was written; on load it
 *    is replaced with whatever PyPI reports now, so the catalog does not go
 *    stale between site deploys. Any failure leaves the static text in place.
 *
 * 3. Links to other sites open in a new tab; anything on our own host
 *    (this site and every library's docs under bedrock-python.github.io)
 *    stays in the current tab. The host comes from the canonical link, so
 *    a local `zensical serve` behaves like production. An author-set
 *    target is left alone.
 *
 * 4. Wire `document$` for instant-navigation compatibility.
 */

const initBlogFilter = () => {
  // Filter chips on the blog index. Only intercept clicks for the "All" chip;
  // category chips link to real category pages so they work without JS too,
  // but if we're on the blog index, prefer client-side filtering.
  const chipsRoot = document.querySelector("[data-bdr-chips]");
  const grid = document.querySelector("[data-bdr-grid]");
  if (!chipsRoot || !grid) return;

  const chips = chipsRoot.querySelectorAll("[data-bdr-filter]");
  const cards = grid.querySelectorAll(".bdr-card");

  chips.forEach((chip) => {
    chip.addEventListener("click", (event) => {
      const filter = chip.dataset.bdrFilter;
      // Don't intercept the Archive chip — it has its own page.
      if (filter === "archive") return;
      event.preventDefault();

      chips.forEach((c) => c.classList.remove("is-active"));
      chip.classList.add("is-active");

      cards.forEach((card) => {
        const cats = (card.dataset.bdrCat || "").split(/\s+/);
        const match = filter === "all" || cats.includes(filter);
        card.style.display = match ? "" : "none";
      });
    });
  });
};

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

const initBedrock = () => {
  initBlogFilter();
  refreshPypiVersions();
  openExternalLinksInNewTab();
};

if (typeof document$ !== "undefined") {
  // Material's instant-navigation observable: re-run on every page load.
  document$.subscribe(initBedrock);
} else {
  document.addEventListener("DOMContentLoaded", initBedrock);
}
