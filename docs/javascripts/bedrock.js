/* Bedrock Python — small enhancements.
 *
 * 1. Client-side category filter for the blog index chips.
 *    The "All" chip and category chips (data-bdr-filter="<slug>") filter
 *    cards in the grid by their data-bdr-cat (space-separated).
 *    Real category-page links (e.g. category/libraries/) still navigate.
 *
 * 2. Wire `document$` for instant-navigation compatibility.
 */

const initBedrock = () => {
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

if (typeof document$ !== "undefined") {
  // Material's instant-navigation observable: re-run on every page load.
  document$.subscribe(initBedrock);
} else {
  document.addEventListener("DOMContentLoaded", initBedrock);
}
