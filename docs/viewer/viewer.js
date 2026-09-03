(() => {
  const root = document.body;
  const docElement = document.documentElement;
  const toast = document.querySelector("[data-toast]");
  const bookmarkButton = document.querySelector("[data-bookmark]");
  const copyButton = document.querySelector("[data-copy-link]");
  const shortcutsButton = document.querySelector("[data-shortcuts]");
  const dialog = document.querySelector("[data-shortcut-dialog]");
  const panel = document.querySelector("[data-settings-panel]");
  const panelToggles = Array.from(document.querySelectorAll("[data-settings-toggle]"));
  const optionButtons = Array.from(document.querySelectorAll("[data-setting]"));
  const storageKey = "zz-viewer-bookmarks-v1";

  const allowed = {
    theme: ["dark", "light"],
    nav: ["on", "off"],
    full: ["off", "on"],
    mode: ["both", "image", "text"],
  };
  const defaults = { theme: "dark", nav: "on", full: "off", mode: "both" };
  const settingKeys = Object.keys(defaults);

  const announce = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("is-visible");
    window.clearTimeout(announce.timer);
    announce.timer = window.setTimeout(() => toast.classList.remove("is-visible"), 1800);
  };

  /* Settings live in the page fragment so a copied link restores the whole view. */

  const parseHash = (hash) => {
    const settings = { ...defaults };
    hash.replace(/^#/, "").split("&").forEach((pair) => {
      const [rawKey, rawValue] = pair.split("=");
      const key = decodeURIComponent(rawKey || "");
      const value = decodeURIComponent(rawValue || "");
      if (allowed[key] && allowed[key].includes(value)) settings[key] = value;
    });
    return settings;
  };

  const currentSettings = () => {
    const settings = {};
    settingKeys.forEach((key) => {
      const value = docElement.getAttribute(`data-${key}`);
      settings[key] = allowed[key].includes(value) ? value : defaults[key];
    });
    return settings;
  };

  const settingsHash = (settings) => {
    const parts = settingKeys
      .filter((key) => settings[key] !== defaults[key])
      .map((key) => `${key}=${settings[key]}`);
    return parts.length ? `#${parts.join("&")}` : "";
  };

  const isInternal = (anchor) => {
    const href = anchor.getAttribute("href") || "";
    return Boolean(href) && !href.startsWith("#") && !/^[a-z][a-z0-9+.-]*:/i.test(href);
  };

  const syncLinks = (hash) => {
    document.querySelectorAll("a[href]").forEach((anchor) => {
      if (!isInternal(anchor)) return;
      if (!anchor.dataset.baseHref) {
        anchor.dataset.baseHref = (anchor.getAttribute("href") || "").split("#")[0];
      }
      anchor.setAttribute("href", anchor.dataset.baseHref + hash);
    });
  };

  const refreshSettingsUi = () => {
    const settings = currentSettings();
    optionButtons.forEach((button) => {
      const active = settings[button.dataset.setting] === button.dataset.value;
      button.setAttribute("aria-pressed", String(active));
    });
  };

  const applySettings = (settings, { record } = { record: true }) => {
    settingKeys.forEach((key) => docElement.setAttribute(`data-${key}`, settings[key]));
    const hash = settingsHash(settings);
    if (record) {
      const url = window.location.pathname + window.location.search + hash;
      try {
        window.history.replaceState(null, "", url);
      } catch (_) {
        // Some browsers refuse replaceState on file:// URLs; the fragment still works.
        window.location.hash = hash;
      }
    }
    syncLinks(hash);
    refreshSettingsUi();
  };

  const setSetting = (key, value) => {
    if (!allowed[key] || !allowed[key].includes(value)) return;
    applySettings({ ...currentSettings(), [key]: value });
  };

  const cycleSetting = (key) => {
    const values = allowed[key];
    const next = values[(values.indexOf(currentSettings()[key]) + 1) % values.length];
    setSetting(key, next);
  };

  const bookmarkId = root.dataset.entityId;
  const bookmarkKind = root.dataset.entityKind;

  const readBookmarks = () => {
    try {
      return JSON.parse(localStorage.getItem(storageKey) || "[]");
    } catch (_) {
      return [];
    }
  };

  const writeBookmarks = (bookmarks) => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(bookmarks));
    } catch (_) {
      announce("Bookmarks are unavailable in this browser");
    }
  };

  const updateBookmarkButton = () => {
    if (!bookmarkButton) return;
    const active = readBookmarks().some((item) => item.id === bookmarkId);
    bookmarkButton.setAttribute("aria-pressed", String(active));
    bookmarkButton.innerHTML = `${active ? "★" : "☆"} <span>${active ? "Saved" : "Bookmark"}</span>`;
  };

  bookmarkButton?.addEventListener("click", () => {
    const bookmarks = readBookmarks();
    const existing = bookmarks.findIndex((item) => item.id === bookmarkId);
    if (existing >= 0) {
      bookmarks.splice(existing, 1);
      announce("Bookmark removed");
    } else {
      bookmarks.unshift({
        id: bookmarkId,
        kind: bookmarkKind,
        title: document.querySelector("h1")?.textContent || document.title,
        url: window.location.href.split("#")[0],
      });
      announce("Bookmark saved on this device");
    }
    writeBookmarks(bookmarks);
    updateBookmarkButton();
  });

  copyButton?.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      announce("Permanent link copied");
    } catch (_) {
      announce("Copy the address from your browser");
    }
  });

  shortcutsButton?.addEventListener("click", () => dialog?.showModal());
  document.querySelector("[data-close-dialog]")?.addEventListener("click", () => dialog?.close());
  dialog?.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });

  const setPanel = (open) => {
    if (!panel) return;
    panel.hidden = !open;
    panelToggles.forEach((button) => button.setAttribute("aria-expanded", String(open)));
    if (open) panel.querySelector(".settings__option")?.focus();
  };

  panelToggles.forEach((button) => {
    button.addEventListener("click", () => setPanel(Boolean(panel?.hidden)));
  });
  document.querySelector("[data-settings-close]")?.addEventListener("click", () => {
    setPanel(false);
    panelToggles[0]?.focus();
  });
  optionButtons.forEach((button) => {
    button.addEventListener("click", () => setSetting(button.dataset.setting, button.dataset.value));
  });
  document.addEventListener("click", (event) => {
    if (!panel || panel.hidden) return;
    const target = event.target;
    if (panel.contains(target) || panelToggles.some((button) => button.contains(target))) return;
    setPanel(false);
  });

  const move = (direction) => {
    const target = root.dataset[`nav${direction[0].toUpperCase()}${direction.slice(1)}`];
    if (target) window.location.assign(target.split("#")[0] + settingsHash(currentSettings()));
  };

  /* Space walks the whole book: down the current view, then on to the next node. */

  const scrollStep = () => Math.max(window.innerHeight - 96, 160);
  const atBottom = () => window.innerHeight + window.scrollY >= docElement.scrollHeight - 2;
  const atTop = () => window.scrollY <= 2;

  const advance = (backwards) => {
    if (backwards) {
      if (atTop()) move("previous");
      else window.scrollBy({ top: -scrollStep(), behavior: "smooth" });
      return;
    }
    if (atBottom()) move("next");
    else window.scrollBy({ top: scrollStep(), behavior: "smooth" });
  };

  const directions = { ArrowUp: "up", ArrowDown: "down", ArrowLeft: "left", ArrowRight: "right", Enter: "in", Escape: "out" };
  const letters = {
    h: () => move("home"),
    s: () => setPanel(Boolean(panel?.hidden)),
    f: () => cycleSetting("full"),
    n: () => cycleSetting("nav"),
    d: () => cycleSetting("theme"),
    m: () => cycleSetting("mode"),
  };

  document.addEventListener("keydown", (event) => {
    if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey) return;

    if (event.key === "Escape" && panel && !panel.hidden) {
      event.preventDefault();
      setPanel(false);
      panelToggles[0]?.focus();
      return;
    }

    const element = event.target;
    if (element instanceof HTMLElement && (element.isContentEditable || /^(A|INPUT|TEXTAREA|SELECT|BUTTON)$/.test(element.tagName))) return;
    if (dialog?.open) return;

    if (event.key === " " || event.code === "Space") {
      event.preventDefault();
      advance(event.shiftKey);
    } else if (directions[event.key]) {
      event.preventDefault();
      move(directions[event.key]);
    } else if (letters[event.key.toLowerCase()]) {
      event.preventDefault();
      letters[event.key.toLowerCase()]();
    } else if (event.key === "?") {
      event.preventDefault();
      dialog?.showModal();
    }
  });

  document.querySelector(".skip-link")?.addEventListener("click", (event) => {
    const target = document.getElementById("content");
    if (!target) return;
    event.preventDefault();
    target.setAttribute("tabindex", "-1");
    target.focus();
    target.scrollIntoView();
  });

  window.addEventListener("hashchange", () => {
    applySettings(parseHash(window.location.hash), { record: false });
  });

  const shelf = document.querySelector("[data-bookmark-shelf]");
  const list = document.querySelector("[data-bookmark-list]");
  if (shelf && list) {
    const bookmarks = readBookmarks();
    if (bookmarks.length) {
      shelf.hidden = false;
      list.className = "bookmark-list";
      bookmarks.forEach((item) => {
        const link = document.createElement("a");
        link.href = item.url;
        link.textContent = `${item.title} · ${item.kind}`;
        list.appendChild(link);
      });
    }
  }

  applySettings(currentSettings(), { record: false });
  updateBookmarkButton();
})();
