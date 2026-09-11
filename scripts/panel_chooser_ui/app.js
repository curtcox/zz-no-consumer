// The panel key in the address bar is the only state this app has. Prior/Next
// and a hand-edited URL are the same operation, so both land in render().
'use strict';

const KEY = /^\d{3}-\d{2}$/;
const el = (id) => document.getElementById(id);

function key() {
  const found = location.pathname.replace(/^\//, '');
  return KEY.test(found) ? found : null;
}

function say(text) {
  const box = el('message');
  box.textContent = text || '';
  box.hidden = !text;
}

function when(stamp) {
  if (!stamp) return '';
  const made = new Date(stamp);
  if (isNaN(made)) return stamp;
  const days = (Date.now() - made) / 86400000;
  const ago = days < 1 ? 'today' : days < 2 ? 'yesterday' : `${Math.floor(days)} days ago`;
  return `${made.toLocaleString()} · ${ago}`;
}

function size(bytes) {
  return bytes ? `${Math.round(bytes / 1024)} KB` : '';
}

function badge(text, kind) {
  const span = document.createElement('span');
  span.className = 'badge' + (kind ? ' ' + kind : '');
  span.textContent = text;
  return span;
}

function card(choice, panel) {
  const figure = document.createElement('figure');
  figure.className = choice.status === 'chosen' ? 'chosen'
    : choice.status === 'rejected' ? 'rejected' : '';

  // Full size opens in its own tab: judging a crop needs the real pixels.
  const link = document.createElement('a');
  link.href = choice.url;
  link.target = '_blank';
  link.rel = 'noopener';
  const image = document.createElement('img');
  image.src = choice.url;
  image.loading = 'lazy';
  image.alt = `${panel} ${choice.id}`;
  link.append(image);

  const caption = document.createElement('figcaption');
  const badges = document.createElement('div');
  badges.className = 'badges';
  const name = document.createElement('span');
  name.className = 'name';
  name.textContent = choice.kind === 'candidate' ? choice.id.slice(0, 12) : choice.id;
  badges.append(name);
  if (choice.status === 'chosen') badges.append(badge('chosen — the book shows this', 'is-chosen'));
  if (choice.status === 'rejected') badges.append(badge('rejected', 'is-rejected'));
  if (choice.kind === 'candidate') badges.append(badge('local candidate', 'is-local'));
  if (choice.kind === 'generated') badges.append(badge('reference only'));
  if (choice.stage) badges.append(badge(choice.stage));

  const meta = document.createElement('p');
  meta.className = 'meta';
  meta.textContent = [choice.provider, choice.seed && `seed ${choice.seed}`,
    choice.width && `${choice.width}×${choice.height}`, size(choice.bytes),
    when(choice.created)].filter(Boolean).join(' · ');

  caption.append(badges, meta);
  if (choice.note) {
    const note = document.createElement('p');
    note.className = 'note';
    note.textContent = choice.note;
    caption.append(note);
  }

  const actions = document.createElement('div');
  actions.className = 'actions';
  if (choice.promote) {
    actions.append(button('Promote & choose', 'promote', () => promote(panel, choice)));
  } else if (choice.selectable) {
    if (choice.status !== 'chosen') actions.append(button('Choose', 'act', () => decide(panel, choice.id, 'choose')));
    if (choice.status !== 'rejected') actions.append(button('Reject', 'undo', () => decide(panel, choice.id, 'reject')));
    if (choice.status !== 'candidate') actions.append(button('Clear', '', () => decide(panel, choice.id, 'clear')));
  }
  if (actions.children.length) caption.append(actions);

  figure.append(link, caption);
  return figure;
}

function button(text, kind, run) {
  const control = document.createElement('button');
  control.type = 'button';
  control.className = kind;
  control.textContent = text;
  control.addEventListener('click', () => {
    for (const other of document.querySelectorAll('button')) other.disabled = true;
    run().finally(() => { for (const other of document.querySelectorAll('button')) other.disabled = false; });
  });
  return control;
}

async function post(path, body) {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || response.statusText);
  return data;
}

async function decide(panel, id, action) {
  try {
    say('');
    draw(await post('/api/decide', { panel, id, action }));
  } catch (error) {
    say(String(error.message));
  }
}

async function promote(panel, choice) {
  // Copying an untracked candidate into the repository is a write worth naming.
  if (!confirm(`Copy this local candidate into assets/art/panels/${panel}/ as a new `
    + `version, record it in data/panel-art.tsv, and choose it for the book?`)) return;
  try {
    say('');
    draw(await post('/api/promote', { panel, id: choice.id }));
  } catch (error) {
    say(String(error.message));
  }
}

function draw(view) {
  el('panel').textContent = view.panel;
  el('title').textContent = `Page ${view.page} · ${view.title}`;
  el('position').textContent = `Panel ${view.position} of ${view.total}`;
  el('decided').textContent = `${view.decided} decided`;
  el('script').textContent = view.script || '(no script text)';
  document.title = `${view.panel} · panel chooser`;

  el('prior').disabled = !view.prior;
  el('next').disabled = !view.next;
  el('prior').onclick = () => view.prior && go(view.prior);
  el('next').onclick = () => view.next && go(view.next);

  const choices = el('choices');
  choices.replaceChildren();
  if (!view.choices.length) {
    const empty = document.createElement('p');
    empty.className = 'aside';
    empty.textContent = 'No generated images for this panel yet.';
    choices.append(empty);
  }
  for (const choice of view.choices) choices.append(card(choice, view.panel));

  const reference = el('reference');
  reference.replaceChildren();
  for (const choice of view.reference) reference.append(card(choice, view.panel));
}

async function render() {
  const panel = key();
  if (!panel) { say('Not a panel key. The address is a panel, like /045-03.'); return; }
  try {
    const response = await fetch(`/api/panel/${panel}`);
    const view = await response.json();
    if (!response.ok) throw new Error(view.error || response.statusText);
    say('');
    draw(view);
  } catch (error) {
    say(String(error.message));
  }
}

function go(panel) {
  history.pushState({}, '', '/' + panel);
  window.scrollTo(0, 0);
  render();
}

addEventListener('popstate', render);
addEventListener('keydown', (event) => {
  if (event.target.matches('input, textarea') || event.metaKey || event.ctrlKey || event.altKey) return;
  const prior = el('prior'), next = el('next');
  if (event.key === 'ArrowLeft' && !prior.disabled) { event.preventDefault(); prior.onclick(); }
  if (event.key === 'ArrowRight' && !next.disabled) { event.preventDefault(); next.onclick(); }
});
render();
