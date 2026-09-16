'use strict';
// Keyboard reader for the incident-movement draft preview. READER_DATA is
// written by edition_pages.py preview as reader-data.js.
const pages = READER_DATA.pages;
const N = pages.length;
const pad = n => String(n).padStart(3, '0');

// Flat reading order: page by page, rows top to bottom, slots left to right.
// Every slot position is a stop, including empty ones. grid maps page
// number -> one list of {col, si} per row.
const stream = [];
const grid = new Map();
pages.forEach(pg => {
  const rows = pg.rows.map(() => []);
  pg.rows.forEach((row, r) => row.slots.forEach((slot, col) => {
    rows[r].push({col, si: stream.length});
    stream.push({key: slot ? slot.key : null, stamp: slot ? slot.stamp : null,
                 owner: row.owner, page: pg.n, row: r, col});
  }));
  grid.set(pg.n, rows);
});

let mode = 'spread';
let page = 1;
let pi = 0;

const stage = document.getElementById('stage');
const hud = document.getElementById('hud');

function firstPanelOf(n) {
  for (let p = n; p <= N; p++)
    for (const row of grid.get(p))
      if (row.length) return row[0].si;
  for (let p = n - 1; p >= 1; p--)
    for (const row of grid.get(p))
      if (row.length) return row[0].si;
  return 0;
}

// First page visible in the spread containing n: book parity, so page 1
// stands alone as a recto and pairs run 2-3, 4-5, ...
function spreadFirst(n) {
  const left = n % 2 === 0 ? n : n - 1;
  return left >= 1 ? left : Math.min(N, left + 1);
}

function vertical(dir) {
  const p = stream[pi];
  const rows = grid.get(p.page);
  const r = p.row + dir;
  if (r < 0 || r >= rows.length || !rows[r].length) return pi;
  return rows[r][Math.min(p.col, rows[r].length - 1)].si;
}

function render() {
  if (mode === 'spread') {
    const left = page % 2 === 0 ? page : page - 1;
    const L = left >= 1 ? left : null;
    const R = left + 1 <= N ? left + 1 : null;
    stage.innerHTML = '<div class="spread">' +
      (L ? `<img src="pages/${pad(L)}.svg" alt="Page ${pad(L)}">`
         : '<div class="blank" aria-label="Blank facing page"></div>') +
      (R ? `<img src="pages/${pad(R)}.svg" alt="Page ${pad(R)}">` : '') +
      '</div>';
    const shown = [L, R].filter(Boolean);
    hud.innerHTML = `<span>pages ${shown.map(pad).join('–')} · ` +
      `${pages[shown[0] - 1].chapter} · ${N} pages</span>` +
      '<span class="keys">space panel · ← → spread</span>';
    history.replaceState(null, '', `#spread=${page}`);
  } else {
    const p = stream[pi];
    const src = p.key ? `panels/${p.key}.svg` : 'empty.svg';
    const label = p.key ? `${p.key} · ${p.owner} · ${p.stamp}` : `empty · ${p.owner}`;
    stage.innerHTML = `<div class="panelview"><img src="${src}" alt="${p.key || 'empty panel'}"></div>`;
    hud.innerHTML = `<span>${label} · page ${pad(p.page)}` +
      ` · panel ${pi + 1}/${stream.length}</span>` +
      '<span class="keys">space spread · ← → panel · ↑ ↓ row</span>';
    history.replaceState(null, '', `#panel=${p.key || p.page + ':' + p.row + ':' + p.col}`);
  }
}

addEventListener('keydown', e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  switch (e.key) {
    case ' ':
    case 'Spacebar':
      if (mode === 'spread') {
        mode = 'panel';
        pi = firstPanelOf(spreadFirst(page));
      } else {
        mode = 'spread';
      }
      break;
    case 'ArrowLeft':
      if (mode === 'spread') page = Math.max(1, page - 2);
      else pi = Math.max(0, pi - 1);
      break;
    case 'ArrowRight':
      if (mode === 'spread') page = Math.min(N, page + 2);
      else pi = Math.min(stream.length - 1, pi + 1);
      break;
    case 'ArrowUp':
      if (mode !== 'panel') return;
      pi = vertical(-1);
      break;
    case 'ArrowDown':
      if (mode !== 'panel') return;
      pi = vertical(1);
      break;
    default:
      return;
  }
  e.preventDefault();
  if (mode === 'panel') page = stream[pi].page;
  render();
});

(function init() {
  const m = location.hash.match(/^#(spread|panel)=(.+)$/);
  if (m && m[1] === 'panel') {
    let i = -1;
    if (m[2].includes(':')) {           // empty slot: page:row:col
      const [pg, r, c] = m[2].split(':').map(Number);
      const rows = grid.get(pg);
      if (rows && rows[r] && rows[r][c]) i = rows[r][c].si;
    } else {
      i = stream.findIndex(p => p.key === m[2]);
    }
    if (i >= 0) { mode = 'panel'; pi = i; }
  } else if (m && m[1] === 'spread') {
    const n = parseInt(m[2], 10);
    if (n >= 1 && n <= N) page = n;
  }
  if (mode === 'panel') page = stream[pi].page;
  render();
})();
