/* Novella reader.

Deliberately smaller than the viewer's script. A chapter of prose has no panels, no
image modes, and no eight-direction wayfinding, so this carries only what a reader
uses: two settings, three moves, and the spacebar.

Settings live in the page fragment, the same convention the viewer uses, so a copied
link reopens the same view. Page anchors (#p045) are *not* settings — they are the
book's own addresses, and this script leaves any fragment it does not recognise alone
so a bookmarked page still lands where it should. */

(() => {
  const root = document.body;
  const docElement = document.documentElement;
  const toast = document.querySelector("[data-toast]");
  const copyButton = document.querySelector("[data-copy-link]");
  const panel = document.querySelector("[data-settings-panel]");
  const panelToggles = Array.from(document.querySelectorAll("[data-settings-toggle]"));
  const optionButtons = Array.from(document.querySelectorAll("[data-setting]"));

  const allowed = { theme: ["dark", "light"], full: ["off", "on"] };
  const defaults = { theme: "dark", full: "off" };
  const settingKeys = Object.keys(defaults);

  const announce = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("is-visible");
    window.clearTimeout(announce.timer);
    announce.timer = window.setTimeout(() => toast.classList.remove("is-visible"), 1800);
  };

  /* The fragment carries settings *and* the page anchor. Split them, keep both. */

  const splitHash = (hash) => {
    const settings = { ...defaults };
    const rest = [];
    hash.replace(/^#/, "").split("&").filter(Boolean).forEach((pair) => {
      const [rawKey, rawValue] = pair.split("=");
      const key = decodeURIComponent(rawKey || "");
      const value = decodeURIComponent(rawValue || "");
      if (allowed[key] && allowed[key].includes(value)) settings[key] = value;
      else rest.push(pair);
    });
    return { settings, anchor: rest[0] || "" };
  };

  const currentSettings = () => {
    const settings = {};
    settingKeys.forEach((key) => {
      const value = docElement.getAttribute(`data-${key}`);
      settings[key] = allowed[key].includes(value) ? value : defaults[key];
    });
    return settings;
  };

  const settingsHash = (settings) =>
    settingKeys.filter((key) => settings[key] !== defaults[key]).map((key) => `${key}=${settings[key]}`);

  const composeHash = (settings, anchor) => {
    const parts = settingsHash(settings);
    if (anchor) parts.push(anchor);
    return parts.length ? `#${parts.join("&")}` : "";
  };

  const isInternal = (anchor) => {
    const href = anchor.getAttribute("href") || "";
    return Boolean(href) && !href.startsWith("#") && !/^[a-z][a-z0-9+.-]*:/i.test(href);
  };

  /* Carry the settings onto outgoing links, but never onto a download: a query-free
     file address is what the browser saves, and a fragment on it helps nobody. */

  const syncLinks = (settings) => {
    const hash = composeHash(settings, "");
    document.querySelectorAll("a[href]").forEach((anchor) => {
      if (!isInternal(anchor) || anchor.hasAttribute("download")) return;
      if (!anchor.dataset.baseHref) {
        anchor.dataset.baseHref = (anchor.getAttribute("href") || "").split("#")[0];
      }
      anchor.setAttribute("href", anchor.dataset.baseHref + hash);
    });
  };

  const refreshSettingsUi = () => {
    const settings = currentSettings();
    optionButtons.forEach((button) => {
      button.setAttribute("aria-pressed", String(settings[button.dataset.setting] === button.dataset.value));
    });
  };

  const applySettings = (settings, { record } = { record: true }) => {
    settingKeys.forEach((key) => docElement.setAttribute(`data-${key}`, settings[key]));
    if (record) {
      const anchor = splitHash(window.location.hash).anchor;
      const url = window.location.pathname + window.location.search + composeHash(settings, anchor);
      try {
        window.history.replaceState(null, "", url);
      } catch (_) {
        // Some browsers refuse replaceState on file:// URLs; the fragment still works.
        window.location.hash = composeHash(settings, anchor);
      }
    }
    syncLinks(settings);
    refreshSettingsUi();
  };

  const setSetting = (key, value) => {
    if (!allowed[key] || !allowed[key].includes(value)) return;
    applySettings({ ...currentSettings(), [key]: value });
  };

  const cycleSetting = (key) => {
    const values = allowed[key];
    setSetting(key, values[(values.indexOf(currentSettings()[key]) + 1) % values.length]);
  };

  const setPanel = (open) => {
    if (!panel) return;
    panel.hidden = !open;
    panelToggles.forEach((button) => button.setAttribute("aria-expanded", String(open)));
    if (open) panel.querySelector(".settings__option")?.focus();
  };

  panelToggles.forEach((button) => button.addEventListener("click", () => setPanel(Boolean(panel?.hidden))));
  document.querySelector("[data-settings-close]")?.addEventListener("click", () => {
    setPanel(false);
    panelToggles[0]?.focus();
  });
  optionButtons.forEach((button) => {
    button.addEventListener("click", () => setSetting(button.dataset.setting, button.dataset.value));
  });
  document.addEventListener("click", (event) => {
    if (!panel || panel.hidden) return;
    if (panel.contains(event.target) || panelToggles.some((button) => button.contains(event.target))) return;
    setPanel(false);
  });

  copyButton?.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      announce("Link copied");
    } catch (_) {
      announce("Copy the address from your browser");
    }
  });

  const move = (direction) => {
    const target = root.dataset[`nav${direction[0].toUpperCase()}${direction.slice(1)}`];
    if (target) window.location.assign(target.split("#")[0] + composeHash(currentSettings(), ""));
  };

  /* Space reads: down this chapter, then on to the next one, and home from the last. */

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

  const letters = {
    h: () => move("home"),
    s: () => setPanel(Boolean(panel?.hidden)),
    f: () => cycleSetting("full"),
    d: () => cycleSetting("theme"),
    j: () => move("next"),
    k: () => move("previous"),
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

    if (event.key === " " || event.code === "Space") {
      event.preventDefault();
      advance(event.shiftKey);
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      move("next");
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      move("previous");
    } else if (letters[event.key.toLowerCase()]) {
      event.preventDefault();
      letters[event.key.toLowerCase()]();
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
    applySettings(splitHash(window.location.hash).settings, { record: false });
  });

  applySettings(currentSettings(), { record: false });

  /* A link arriving as `#theme=light&p045` is one fragment to the browser, not two, so
     the anchor never resolves on its own. Scroll to it once the settings are applied. */
  const arriving = splitHash(window.location.hash).anchor;
  if (arriving) document.getElementById(arriving)?.scrollIntoView();
})();
