(() => {
  const root = document.body;
  const toast = document.querySelector("[data-toast]");
  const bookmarkButton = document.querySelector("[data-bookmark]");
  const copyButton = document.querySelector("[data-copy-link]");
  const shortcutsButton = document.querySelector("[data-shortcuts]");
  const dialog = document.querySelector("[data-shortcut-dialog]");
  const storageKey = "zz-viewer-bookmarks-v1";

  const announce = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("is-visible");
    window.clearTimeout(announce.timer);
    announce.timer = window.setTimeout(() => toast.classList.remove("is-visible"), 1800);
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
        url: window.location.href,
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

  const move = (direction) => {
    const target = root.dataset[`nav${direction[0].toUpperCase()}${direction.slice(1)}`];
    if (target) window.location.assign(target);
  };

  document.addEventListener("keydown", (event) => {
    if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey) return;
    const element = event.target;
    if (element instanceof HTMLElement && (element.isContentEditable || /^(A|INPUT|TEXTAREA|SELECT|BUTTON)$/.test(element.tagName))) return;
    if (dialog?.open) return;

    const directions = { ArrowUp: "up", ArrowDown: "down", ArrowLeft: "left", ArrowRight: "right", Enter: "in", Escape: "out" };
    if (directions[event.key]) {
      event.preventDefault();
      move(directions[event.key]);
    } else if (event.key.toLowerCase() === "h") {
      event.preventDefault();
      move("home");
    } else if (event.key === "?") {
      event.preventDefault();
      dialog?.showModal();
    }
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

  updateBookmarkButton();
})();
