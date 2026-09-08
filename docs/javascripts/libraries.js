/* Local package search and install-command copying; the directory also works without JS. */
(() => {
  const registration = Symbol.for("bedrock.libraryDirectory");
  if (window[registration]) return;
  window[registration] = true;
  let currentRoot = null;
  let lifecycle = null;
  const normalize = (text) => text.normalize("NFKD").toLowerCase().replace(/[^\p{L}\p{N}]+/gu, " ").trim();

  const init = () => {
    const root = document.querySelector("[data-library-page]");
    if (root === currentRoot) return;
    lifecycle?.abort();
    currentRoot = root;
    if (!root) return;
    lifecycle = new AbortController();
    const { signal } = lifecycle;
    const query = root.querySelector("[data-library-query]");
    const clear = root.querySelector("[data-library-clear]");
    const status = root.querySelector("[data-library-status]");
    const empty = root.querySelector("[data-library-empty]");
    const groups = [...root.querySelectorAll("[data-library-group]")];
    const records = [...root.querySelectorAll("[data-library-package]")].map((element) => ({
      element, text: normalize(element.textContent),
    }));
    const copyStatus = root.querySelector("[data-library-copy-status]");
    const timers = new Set();

    const filter = () => {
      const tokens = normalize(query.value).split(" ").filter(Boolean);
      let count = 0;
      records.forEach(({ element, text }) => {
        element.hidden = !tokens.every((token) => text.includes(token));
        if (!element.hidden) count += 1;
      });
      groups.forEach((group) => { group.hidden = !group.querySelector("[data-library-package]:not([hidden])"); });
      clear.hidden = query.value.length === 0;
      status.hidden = tokens.length === 0;
      const message = `${count} ${count === 1 ? "package" : "packages"} found`;
      if (status.textContent !== message) status.textContent = message;
      empty.hidden = count > 0;
    };
    const reset = () => { query.value = ""; filter(); };

    query.addEventListener("input", filter, { signal });
    query.addEventListener("keydown", (event) => {
      if (event.isComposing) return;
      if (event.key === "Escape") {
        event.stopPropagation();
        reset();
      } else if (event.key === "Enter") {
        event.preventDefault();
        const target = records.find(({ element }) => !element.hidden)?.element.querySelector("h3 a");
        if (target) {
          target.focus({ preventScroll: true });
          target.closest("article").scrollIntoView({ block: "start", behavior: "instant" });
        }
      }
    }, { signal });

    root.addEventListener("click", async (event) => {
      const control = event.target.closest("button, a");
      if (!control || !root.contains(control)) return;
      if (control.matches("[data-library-clear], [data-library-reset]")) {
        reset(); query.focus();
      } else if (control instanceof HTMLAnchorElement && control.hash &&
        control.origin === location.origin && control.pathname === location.pathname) {
        // A topic jump must not point at a section hidden by the previous query.
        reset();
      } else if (control.matches("[data-copy-command]")) {
        try {
          await navigator.clipboard.writeText(control.dataset.copyCommand);
          if (signal.aborted || !root.isConnected) return;
          control.dataset.copied = "true";
          control.title = "Copied";
          copyStatus.textContent = `Copied: ${control.dataset.copyCommand}`;
          const icon = control.querySelector("svg");
          if (icon) icon.setAttribute("hidden", "");
          if (!control.querySelector("[data-copy-check]")) {
            const check = document.createElement("span");
            check.dataset.copyCheck = "";
            check.setAttribute("aria-hidden", "true");
            check.textContent = "✓";
            control.append(check);
          }
          const timer = setTimeout(() => {
            delete control.dataset.copied;
            control.title = "Copy install command";
            control.querySelector("[data-copy-check]")?.remove();
            if (icon) icon.removeAttribute("hidden");
            timers.delete(timer);
          }, 1800);
          timers.add(timer);
        } catch {
          if (signal.aborted) return;
          const command = control.parentElement.querySelector("code");
          const range = document.createRange();
          range.selectNodeContents(command);
          const selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
          copyStatus.textContent = "Select and copy the highlighted install command.";
        }
      }
    }, { signal });
    signal.addEventListener("abort", () => timers.forEach(clearTimeout), { once: true });
    root.querySelectorAll("[data-library-controls], [data-copy-command]").forEach((element) => { element.hidden = false; });
    filter();
    root.dataset.enhanced = "true";
  };
  if (typeof document$ !== "undefined") document$.subscribe(init);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
