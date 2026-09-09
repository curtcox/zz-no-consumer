(() => {
  const $ = id => document.getElementById(id);
  let catalog, state, mode = '', pending, generation = 0;
  const showError = message => { $('error').textContent = message; $('error').hidden = !message; };
  async function request(url, options) {
    const response = await fetch(url, options);
    if (!response.ok) throw new Error(`Request failed (${response.status}). Try again.`);
    return response;
  }
  async function render() {
    if (!catalog || !state) return;
    if (catalog.build && state.build !== catalog.build) { showError('The local server restarted. Reload this display to load matching assets.'); return; }
    if (state.restart_required) { showError('Viewer code changed. Restart the local server, then reload this display.'); return; }
    $('page').value = state.page;
    $('current').textContent = `Page ${String(state.page).padStart(3, '0')}`;
    const index = catalog.pages.findIndex(p => p.number === state.page);
    $('previous').disabled = index === 0;
    $('next').disabled = index === catalog.pages.length - 1;
    $('welcome').hidden = !!mode;
    $('selector').hidden = mode !== 'selector';
    pending?.abort();
    const mine = ++generation;
    $('view').replaceChildren();
    showError('');
    if (!mode || mode === 'selector') return;
    pending = new AbortController();
    try {
      const response = await request(`/api/view?mode=${mode}&page=${state.page}`, {signal: pending.signal});
      const content = await response.text();
      if (mine !== generation) return;
      $('view').innerHTML = content;
      // Text references are local independent readings, not global page controls.
      $('view').querySelectorAll('a').forEach(a => { a.target = '_blank'; a.rel = 'noopener'; });
      window.scrollTo(0, 0);
      if (catalog.layout_version !== '2') showError('Using the compatibility layout. Restart the local server to enable exact panel sizing.');
      await Promise.all([...$('view').querySelectorAll('.page-art img')].map(img => img.decode().catch(() => {})));
      if (mine !== generation) return;
      if ($('view').querySelector('.page-art') && window.auditPanelFit) {
        const errors = await window.auditPanelFit($('view'), {allowLegacy: catalog.layout_version !== '2'});
        if (errors.length) showError('Panel display failed its visibility check. Reload or restart the local server.');
        window.panelAuditResult = errors;
      }
    } catch (error) {
      if (mine === generation && error.name !== 'AbortError') showError(error.message);
    }
  }
  function choose(value) {
    mode = Object.hasOwn(catalog.modes, value) ? value : '';
    $('mode').value = mode;
    history.replaceState(null, '', mode ? `/?mode=${mode}` : '/');
    document.title = mode ? `${catalog.modes[mode]} · Local book room` : 'Local book room';
    render();
  }
  async function select(page) {
    try {
      await request('/api/state', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({page})});
    } catch (error) { showError(error.message); }
  }
  $('mode').addEventListener('change', event => choose(event.target.value));
  $('page').addEventListener('change', event => select(Number(event.target.value)));
  for (const [id, step] of [['previous', -1], ['next', 1]]) {
    $(id).onclick = () => {
      const index = catalog.pages.findIndex(p => p.number === state.page);
      const next = catalog.pages[index + step];
      if (next) select(next.number);
    };
  }
  $('fullscreen').onclick = async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch (_) { showError('Use your browser’s full-screen command on this device.'); }
  };
  async function start() {
    try {
      catalog = await (await request('/api/catalog')).json();
      for (const [value, label] of Object.entries(catalog.modes)) {
        $('mode').add(new Option(label, value));
        const button = document.createElement('button');
        button.textContent = label;
        button.onclick = () => choose(value);
        $('choices').append(button);
      }
      for (const p of catalog.pages) $('page').add(new Option(`${String(p.number).padStart(3, '0')} · ${p.title}`, p.number));
      choose(new URLSearchParams(location.search).get('mode'));
      const receive = message => {
        if (message.type === 'state') {
          const changed = !state || state.page !== message.state.page || state.revision !== message.state.revision || state.restart_required !== message.state.restart_required || state.build !== message.state.build;
          state = message.state;
          $('status').textContent = `Live · page ${String(state.page).padStart(3, '0')}`;
          $('status').className = 'live';
          if (changed) render();
        } else {
          $('status').textContent = 'Disconnected · reconnecting…';
          $('status').className = '';
        }
      };
      // One event stream per browser profile avoids HTTP/1 connection limits
      // when a user opens all ten displays in separate windows.
      let worker, polling = false;
      function startPolling() {
        if (polling) return;
        polling = true;
        const poll = async () => {
          try { receive({type: 'state', state: await (await request('/api/state')).json()}); }
          catch (_) { receive({type: 'disconnected'}); }
          setTimeout(poll, 500);
        };
        poll();
      }
      if (typeof SharedWorker !== 'undefined') {
        try {
          worker = new SharedWorker('/sync.js');
          worker.port.onmessage = event => receive(event.data);
          worker.port.start();
          worker.onerror = () => { worker.port.close(); startPolling(); };
          window.addEventListener('pagehide', () => {
            worker.port.postMessage('close');
          });
          window.addEventListener('pageshow', event => { if (event.persisted) location.reload(); });
        } catch (_) { worker = null; }
      }
      if (!worker) startPolling();
    } catch (error) {
      showError(`${error.message} Reload to reconnect.`);
    }
  }
  start();
})();
