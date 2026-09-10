/* Keep Zensical's native renderer; move its complete host when expanding a diagram. */
(() => {
  if (window.bedrockDiagrams) return;
  window.bedrockDiagrams = true;
  const t = (key) => window.bedrockI18n.t(key);
  let active = null;
  const dialog = document.createElement("dialog");
  dialog.className = "bdr-diagram-dialog";
  dialog.setAttribute("aria-labelledby", "bdr-diagram-dialog-title");
  const header = document.createElement("div");
  header.className = "bdr-diagram-dialog__header";
  const title = document.createElement("strong");
  title.id = "bdr-diagram-dialog-title";
  const close = document.createElement("button");
  close.type = "button";
  close.textContent = t("Close diagram");
  close.addEventListener("click", () => dialog.close());
  header.append(title, close);
  const body = document.createElement("div");
  body.className = "bdr-diagram-dialog__body";
  dialog.append(header, body);
  document.body.append(dialog);
  dialog.addEventListener("close", () => {
    if (!active) return;
    const { viewport, marker, button } = active;
    if (marker.isConnected) {
      marker.replaceWith(viewport);
      button.focus({ preventScroll: true });
    } else viewport.remove();
    active = null;
  });
  dialog.addEventListener("click", (event) => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });

  let cleanups = [];
  const init = () => {
    if (dialog.open) dialog.close();
    cleanups.forEach((cleanup) => cleanup());
    cleanups = [];
    document.querySelectorAll("figure.bdr-diagram").forEach((figure) => {
      const viewport = figure.querySelector(".bdr-diagram__viewport");
      const caption = figure.querySelector("figcaption");
      if (!viewport || !caption) return;
      const heading = caption.querySelector("strong").textContent;
      viewport.tabIndex = 0;
      viewport.setAttribute("role", "region");
      viewport.setAttribute("aria-label", heading);
      let button = caption.querySelector(".bdr-diagram__expand");
      if (!button) {
        button = document.createElement("button");
        button.type = "button";
        button.className = "bdr-diagram__expand";
        button.textContent = t("Expand diagram") + " ↗";
        button.setAttribute("aria-haspopup", "dialog");
        button.addEventListener("click", () => {
          // Reserve the space so opening the dialog does not move the article.
          const marker = document.createElement("div");
          marker.style.height = viewport.getBoundingClientRect().height + "px";
          marker.setAttribute("aria-hidden", "true");
          viewport.before(marker);
          active = { viewport, marker, button };
          title.textContent = heading;
          body.append(viewport);
          dialog.showModal();
        });
        caption.append(button);
      }
      let hint = figure.querySelector(".bdr-diagram__hint");
      if (!hint) {
        hint = document.createElement("span");
        hint.className = "bdr-diagram__hint";
        hint.textContent = t("Scroll horizontally to see the whole diagram");
        figure.querySelector(".bdr-diagram__caption").append(hint);
      }
      const update = () => {
        const rendered = !!viewport.querySelector("div.mermaid");
        button.hidden = !rendered;
        hint.hidden = !rendered || viewport.scrollWidth <= viewport.clientWidth + 1;
      };
      // Defer DOM changes beyond ResizeObserver delivery (notably in WebKit).
      let frame = 0;
      const scheduleUpdate = () => {
        if (!frame) frame = requestAnimationFrame(() => { frame = 0; update(); });
      };
      const resize = new ResizeObserver(scheduleUpdate);
      resize.observe(viewport);
      const mutation = new MutationObserver(scheduleUpdate);
      mutation.observe(viewport, { childList: true });
      cleanups.push(() => { resize.disconnect(); mutation.disconnect(); cancelAnimationFrame(frame); });
      update();
    });
  };
  if (typeof document$ !== "undefined") document$.subscribe(init);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
