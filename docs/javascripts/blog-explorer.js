/* Search and browse the article catalog. The complete static list is the fallback. */
(() => {
  const registration = Symbol.for("bedrock.blogExplorer");
  if (window[registration]) return;
  window[registration] = true;

  const PAGE_SIZE = 12;
  const VIEW_STORAGE = "bedrock-blog-view";
  const RETURN_STORAGE = "bedrock-blog-return";
  const PARAMS = ["query", "topic", "format", "duration", "sort", "view", "page"];
  const DEFAULTS = {
    query: "", topic: "all", format: "all", duration: "all",
    sort: "newest", view: "list", page: 1,
  };
  const normalize = (value) => String(value || "")
    .normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ").trim();
  const list = (value) => Array.isArray(value) ? value.map(String) : [];
  let currentRoot = null;
  let lifecycle = null;

  const readPreferredView = () => {
    try {
      return localStorage.getItem(VIEW_STORAGE) === "grid" ? "grid" : "list";
    } catch {
      return "list";
    }
  };

  const addArticleReturnLink = () => {
    const postPath = location.pathname.indexOf("/blog/posts/");
    if (postPath < 0 || document.querySelector("[data-blog-return]")) return;
    const content = document.querySelector(".md-content__inner");
    if (!content) return;
    const catalogPath = `${location.pathname.slice(0, postPath)}/blog/`;
    let destination = new URL(catalogPath, location.origin);
    try {
      const saved = sessionStorage.getItem(RETURN_STORAGE);
      if (saved) {
        const previous = new URL(saved, location.origin);
        if (previous.origin === location.origin &&
          [catalogPath, catalogPath.slice(0, -1), `${catalogPath}index.html`].includes(previous.pathname)) {
          destination = previous;
        }
      }
    } catch { /* A plain catalog link works when storage is unavailable. */ }
    const link = document.createElement("a");
    link.className = "bdr-post-back";
    link.dataset.blogReturn = "";
    link.href = destination.href;
    link.textContent = "← Back to articles";
    const title = content.querySelector("h1");
    if (title) title.before(link);
    else content.prepend(link);
  };

  const init = async () => {
    addArticleReturnLink();
    const root = document.querySelector("[data-blog-explorer]");
    if (root === currentRoot) return;
    lifecycle?.abort();
    currentRoot = root;
    if (!root) return;
    lifecycle = new AbortController();
    const { signal } = lifecycle;
    const pagePath = location.pathname;
    const isCurrentPage = () => !signal.aborted && root.isConnected && location.pathname === pagePath;
    const results = root.querySelector("[data-blog-results]");
    const status = root.querySelector("[data-blog-load-status]");
    if (!results) return;

    let catalogUrl;
    try {
      catalogUrl = new URL(root.dataset.catalogUrl || "catalog.json",
        root.dataset.catalogBase || document.baseURI);
      const response = await fetch(catalogUrl, { signal });
      if (!response.ok) throw new Error("Catalog unavailable");
      const catalog = await response.json();
      if (!isCurrentPage()) return;
      if (!Array.isArray(catalog.articles)) throw new Error("Invalid catalog");

      const entries = Array.from(results.querySelectorAll("[data-article-id]"));
      const metadata = new Map(catalog.articles.map((article) => [article.id, article]));
      if (metadata.size !== entries.length || entries.some((entry) =>
        !metadata.has(entry.dataset.articleId))) throw new Error("Catalog does not match articles");
      const records = entries.map((element, order) => {
        const article = metadata.get(element.dataset.articleId);
        const title = String(article.title || "");
        const tags = list(article.tags);
        const topics = list(article.topics);
        const categories = list(article.categories);
        const description = String(article.description || "");
        return {
          ...article, title, tags, topics, categories, description, element, order,
          date: String(article.date || ""),
          minutes: Number(article.minutes) || 1,
          titleText: normalize(title),
          tagText: normalize([...tags, ...topics].join(" ")),
          descriptionText: normalize(description),
          searchText: normalize([title, description, article.search || "",
            ...tags, ...topics, ...categories].join(" ")),
        };
      });
      const topicLabels = new Map((catalog.topics || []).map((topic) => [topic.id, topic.label]));
      const formatLabels = new Map((catalog.categories || []).map((category) =>
        [category.id, category.label]));
      const query = root.querySelector("[data-blog-query]");
      const clearQuery = root.querySelector("[data-blog-clear-query]");
      const format = root.querySelector("[data-blog-format]");
      const duration = root.querySelector("[data-blog-duration]");
      const sort = root.querySelector("[data-blog-sort]");
      const defaultSortOption = sort?.querySelector("option[value='newest']");
      const defaultSortLabel = defaultSortOption?.textContent || "Newest first";
      const count = root.querySelector("[data-blog-count]");
      const range = root.querySelector("[data-blog-range]");
      const active = root.querySelector("[data-blog-active]");
      const empty = root.querySelector("[data-blog-empty]");
      const pagination = root.querySelector("[data-blog-pagination]");
      const headingContainer = root.querySelector("[data-blog-results-heading]");
      const heading = headingContainer?.querySelector("h1, h2, h3") || headingContainer;
      const topicsPanel = root.querySelector("[data-blog-topics-panel]");
      const topicButtons = Array.from(root.querySelectorAll("[data-blog-topic]"));
      const viewButtons = Array.from(root.querySelectorAll("[data-blog-view]"));
      let queryTimer = null;

      const readState = () => {
        const params = new URL(location.href).searchParams;
        const allowed = (name, choices, fallback) => choices.includes(params.get(name))
          ? params.get(name) : fallback;
        const rawPage = params.get("page") || "1";
        return {
          query: params.get("query") || "",
          topic: allowed("topic", ["all", ...topicLabels.keys()], "all"),
          format: allowed("format", ["all", ...formatLabels.keys()], "all"),
          duration: allowed("duration", ["all", "short", "long"], "all"),
          sort: allowed("sort", ["newest", "oldest", "shortest", "title"], "newest"),
          view: allowed("view", ["list", "grid"], readPreferredView()),
          page: /^\d+$/.test(rawPage) && Number.isSafeInteger(Number(rawPage))
            ? Math.max(1, Number(rawPage)) : 1,
        };
      };
      let state = readState();

      const writeState = (mode) => {
        const url = new URL(location.href);
        PARAMS.forEach((name) => {
          // A history entry must keep its layout even after the saved preference changes.
          if (name !== "view" && state[name] === DEFAULTS[name]) url.searchParams.delete(name);
          else url.searchParams.set(name, String(state[name]));
        });
        if (url.href !== location.href) {
          // Keep the theme's history state intact for instant navigation.
          history[mode === "push" ? "pushState" : "replaceState"](history.state, "", url);
        }
      };

      const focusResults = () => {
        if (!heading) return;
        if (!heading.hasAttribute("tabindex")) heading.tabIndex = -1;
        heading.focus({ preventScroll: true });
        (headingContainer || heading).scrollIntoView({ block: "start", behavior:
          matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth" });
      };

      const button = (label, className) => {
        const element = document.createElement("button");
        element.type = "button";
        element.className = className;
        element.textContent = label;
        return element;
      };

      const renderPills = () => {
        if (!active) return;
        const labels = [];
        if (state.query.trim()) labels.push(["query", `Search: ${state.query.trim()}`]);
        if (state.topic !== "all") labels.push(["topic", topicLabels.get(state.topic)]);
        if (state.format !== "all") labels.push(["format", formatLabels.get(state.format)]);
        if (state.duration !== "all") labels.push(["duration",
          state.duration === "short" ? "8 minutes or less" : "Over 8 minutes"]);
        const fragment = document.createDocumentFragment();
        labels.forEach(([key, label]) => {
          const pill = button(`${label} ×`, "bdr-filter-pill");
          pill.dataset.removeFilter = key;
          pill.setAttribute("aria-label", `Remove filter: ${label}`);
          fragment.append(pill);
        });
        if (labels.length > 1) {
          const reset = button("Clear all", "bdr-filter-pill bdr-filter-pill--reset");
          reset.dataset.blogReset = "";
          fragment.append(reset);
        }
        active.replaceChildren(fragment);
        active.hidden = labels.length === 0;
      };

      const renderPagination = (totalPages) => {
        if (!pagination) return;
        pagination.replaceChildren();
        pagination.hidden = totalPages <= 1;
        if (totalPages <= 1) return;
        const pageButton = (page, label, className = "") => {
          const control = button(label, `bdr-page ${className}`.trim());
          control.dataset.blogPage = String(page);
          return control;
        };
        const previous = pageButton(state.page - 1, "← Previous", "bdr-page--previous");
        previous.disabled = state.page === 1;
        previous.setAttribute("aria-label", "Previous page");
        pagination.append(previous);
        const pages = totalPages <= 7
          ? Array.from({ length: totalPages }, (_, index) => index + 1)
          : [...new Set([1, totalPages, state.page - 1, state.page, state.page + 1])]
            .filter((page) => page >= 1 && page <= totalPages).sort((a, b) => a - b);
        let last = 0;
        pages.forEach((page) => {
          if (page - last > 1) {
            const gap = document.createElement("span");
            gap.className = "bdr-page-gap";
            gap.textContent = "…";
            gap.setAttribute("aria-hidden", "true");
            pagination.append(gap);
          }
          const control = pageButton(page, String(page));
          control.setAttribute("aria-label", `Page ${page}`);
          if (page === state.page) control.setAttribute("aria-current", "page");
          pagination.append(control);
          last = page;
        });
        const next = pageButton(state.page + 1, "Next →", "bdr-page--next");
        next.disabled = state.page === totalPages;
        next.setAttribute("aria-label", "Next page");
        pagination.append(next);
      };

      const render = () => {
        const phrase = normalize(state.query);
        const tokens = phrase.split(" ").filter(Boolean);
        const eligible = records.filter((record) =>
          tokens.every((token) => record.searchText.includes(token)) &&
          (state.format === "all" || record.categories.includes(state.format)) &&
          (state.duration === "all" || (state.duration === "short"
            ? record.minutes <= 8 : record.minutes > 8)));
        const matching = eligible.filter((record) =>
          state.topic === "all" || record.topics.includes(state.topic));
        const relevance = (record) => (record.titleText.includes(phrase) ? 100 : 0) +
          tokens.reduce((score, token) => score +
            (record.titleText.includes(token) ? 20 : 0) +
            (record.tagText.includes(token) ? 8 : 0) +
            (record.descriptionText.includes(token) ? 4 : 0), 0);
        matching.sort((a, b) => {
          let difference = 0;
          if (state.sort === "title") difference = a.title.localeCompare(b.title, "en");
          else if (state.sort === "shortest") difference = a.minutes - b.minutes;
          else if (state.sort === "oldest") difference = a.date.localeCompare(b.date);
          else if (tokens.length) difference = relevance(b) - relevance(a);
          return difference || b.date.localeCompare(a.date) || a.order - b.order;
        });
        const total = matching.length;
        const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
        state.page = Math.min(state.page, totalPages);
        const start = (state.page - 1) * PAGE_SIZE;
        const visible = new Set(matching.slice(start, start + PAGE_SIZE));
        const matchingSet = new Set(matching);
        const ordered = [...matching, ...records.filter((record) => !matchingSet.has(record))];
        const fragment = document.createDocumentFragment();
        ordered.forEach((record) => {
          record.element.hidden = !visible.has(record);
          fragment.append(record.element);
        });
        results.append(fragment);
        root.dataset.view = state.view;
        root.dataset.filtered = String(Boolean(tokens.length || state.topic !== "all" ||
          state.format !== "all" || state.duration !== "all"));
        if (query && query.value !== state.query) query.value = state.query;
        if (clearQuery) clearQuery.hidden = !state.query;
        if (format) format.value = state.format;
        if (duration) duration.value = state.duration;
        if (sort) sort.value = state.sort;
        if (defaultSortOption) defaultSortOption.textContent = tokens.length ? "Best match" : defaultSortLabel;
        const countText = `${total} ${total === 1 ? "article" : "articles"}`;
        if (count && count.textContent !== countText) count.textContent = countText;
        if (range) range.textContent = total
          ? `Showing ${start + 1}–${Math.min(start + PAGE_SIZE, total)} of ${total}`
          : "Showing 0 of 0";
        if (empty) empty.hidden = total !== 0;
        topicButtons.forEach((control) => {
          const topic = control.dataset.blogTopic;
          const selected = topic === state.topic;
          control.classList.toggle("is-active", selected);
          control.setAttribute("aria-pressed", String(selected));
          const topicCount = control.querySelector("[data-topic-count]");
          if (topicCount) topicCount.textContent = String(topic === "all" ? eligible.length :
            eligible.filter((record) => record.topics.includes(topic)).length);
        });
        viewButtons.forEach((control) => {
          const selected = control.dataset.blogView === state.view;
          control.classList.toggle("is-active", selected);
          control.setAttribute("aria-pressed", String(selected));
        });
        renderPills();
        renderPagination(totalPages);
      };

      const commit = (patch, { mode = "push", scroll = false } = {}) => {
        if (!isCurrentPage()) return;
        const pending = queryTimer !== null;
        clearTimeout(queryTimer);
        queryTimer = null;
        state = { ...state, ...(pending && query ? { query: query.value, page: 1 } : {}), ...patch };
        render();
        writeState(mode);
        if (scroll) focusResults();
      };
      const reset = () => commit({ query: "", topic: "all", format: "all",
        duration: "all", sort: "newest", page: 1 });

      query?.addEventListener("input", () => {
        clearTimeout(queryTimer);
        if (clearQuery) clearQuery.hidden = !query.value;
        queryTimer = setTimeout(() => {
          queryTimer = null;
          commit({ query: query.value, page: 1 }, { mode: "replace" });
        }, 140);
      }, { signal });
      query?.addEventListener("keydown", (event) => {
        if (event.isComposing) return;
        if (event.key === "Enter") {
          event.preventDefault();
          event.stopPropagation();
          commit({ query: query.value, page: 1 }, { mode: "replace", scroll: true });
          return;
        }
        if (event.key !== "Escape" || !query.value) return;
        event.preventDefault();
        event.stopPropagation();
        commit({ query: "", page: 1 }, { mode: "replace" });
      }, { signal });
      clearQuery?.addEventListener("click", () => {
        commit({ query: "", page: 1 }, { mode: "replace" });
        query?.focus();
      }, { signal });
      [[format, "format"], [duration, "duration"], [sort, "sort"]].forEach(([control, key]) => {
        control?.addEventListener("change", () => commit({ [key]: control.value, page: 1 }), { signal });
      });

      root.addEventListener("click", (event) => {
        const control = event.target.closest("button, a");
        if (!control || !root.contains(control) || control.disabled) return;
        if (control.matches("a") && control.closest("[data-article-id]")) {
          try { sessionStorage.setItem(RETURN_STORAGE, location.href); } catch { /* Optional history shortcut. */ }
        }
        if (control.matches("[data-blog-topic]")) {
          commit({ topic: control.dataset.blogTopic, page: 1 });
          if (topicsPanel && matchMedia("(max-width: 760px)").matches) {
            topicsPanel.open = false;
            topicsPanel.querySelector("summary")?.focus();
          }
        } else if (control.matches("[data-blog-view]")) {
          const view = control.dataset.blogView;
          try { localStorage.setItem(VIEW_STORAGE, view); } catch { /* Storage is optional. */ }
          commit({ view });
        } else if (control.matches("[data-remove-filter]")) {
          const key = control.dataset.removeFilter;
          commit({ [key]: DEFAULTS[key], page: 1 });
          query?.focus();
        } else if (control.matches("[data-blog-reset]")) {
          reset();
          query?.focus();
        } else if (control.matches("[data-blog-page]")) {
          commit({ page: Number(control.dataset.blogPage) }, { scroll: true });
        } else if (control.matches("[data-blog-collection]")) {
          // The theme's instant-navigation listener ignores defaultPrevented.
          // Keep handled filters and modified native clicks out of that listener.
          event.stopPropagation();
          if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey ||
            control.target === "_blank" || control.hasAttribute("download")) return;
          event.preventDefault();
          commit({ topic: control.dataset.blogCollection, query: "", format: "all",
            duration: "all", page: 1 }, { scroll: true });
        }
      }, { signal });

      document.addEventListener("keydown", (event) => {
        if (event.key !== "/" || event.defaultPrevented || event.ctrlKey || event.metaKey ||
          event.altKey || event.isComposing || event.repeat || !query || !isCurrentPage()) return;
        const target = event.target;
        if (target.isContentEditable || target.closest("input, textarea, select, [contenteditable='true']")) return;
        if (document.querySelector("[data-md-toggle='search']:checked, #__search:checked, " +
          "[data-md-toggle='drawer']:checked, dialog[open], [aria-modal='true']:not([hidden])")) return;
        event.preventDefault();
        event.stopPropagation();
        query.focus();
      }, { signal, capture: true });

      window.addEventListener("popstate", () => {
        if (!isCurrentPage()) return;
        clearTimeout(queryTimer);
        queryTimer = null;
        state = readState();
        render();
      }, { signal });
      const desktopTopics = matchMedia("(min-width: 761px)");
      desktopTopics.addEventListener("change", (event) => {
        if (topicsPanel) topicsPanel.open = event.matches;
      }, { signal });
      signal.addEventListener("abort", () => clearTimeout(queryTimer), { once: true });
      render();
      writeState("replace");
      if (topicsPanel && matchMedia("(max-width: 760px)").matches) topicsPanel.open = false;
      root.querySelectorAll("[data-blog-controls]").forEach((element) => { element.hidden = false; });
      root.dataset.enhanced = "true";
      if (status) status.hidden = true;
    } catch (error) {
      if (!isCurrentPage()) return;
      // Filtering is optional: all server-rendered links remain usable when offline.
      results.querySelectorAll("[data-article-id]").forEach((entry) => { entry.hidden = false; });
      if (status) {
        const archive = document.createElement("a");
        archive.href = new URL("archive/", catalogUrl || document.baseURI).href;
        archive.textContent = "Browse the archive";
        status.replaceChildren(document.createTextNode(
          "Search is temporarily unavailable. All articles are listed below. "), archive);
        status.hidden = false;
      }
    }
  };

  if (typeof document$ !== "undefined") {
    document$.subscribe(init);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
