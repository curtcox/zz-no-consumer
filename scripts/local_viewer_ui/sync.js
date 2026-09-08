/* Share one live connection across every window in this browser profile. */
const ports = new Set();
let state, connected = false;
const events = new EventSource('/events');
function broadcast(message) {
  for (const port of ports) port.postMessage(message);
}
events.onmessage = event => {
  state = JSON.parse(event.data);
  connected = true;
  broadcast({type: 'state', state});
};
events.onerror = () => { connected = false; broadcast({type: 'disconnected'}); };
onconnect = event => {
  const port = event.ports[0];
  ports.add(port);
  port.onmessage = message => {
    if (message.data === 'close') { ports.delete(port); port.close(); }
  };
  port.start();
  if (state && connected) port.postMessage({type: 'state', state});
  else port.postMessage({type: 'disconnected'});
};
