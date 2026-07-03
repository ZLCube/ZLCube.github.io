const $ = (id) => document.getElementById(id);

const themeMeta = {
  instagram: { status: 'Activo ahora', icons: '⌕ ⋮', footer: 'Mensaje...', footerIcon: '♡' },
  whatsapp: { status: 'en línea', icons: '☎ ⋮', footer: 'Mensaje', footerIcon: '🎙' },
  telegram: { status: 'en línea', icons: '☎ ⋮', footer: 'Mensaje', footerIcon: '➤' },
  teams: { status: 'Disponible', icons: '☎ ⋯', footer: 'Escribe un mensaje', footerIcon: '+' },
  twitter: { status: '@destination', icons: 'ⓘ', footer: 'Comienza un mensaje', footerIcon: '♡' }
};

const state = { messages: [], index: 0, playing: false, paused: false, timers: [] };

function sleep(ms) {
  return new Promise((resolve) => {
    const t = setTimeout(resolve, ms);
    state.timers.push(t);
  });
}
function clearTimers() { state.timers.forEach(clearTimeout); state.timers = []; }

function getConfig() {
  return {
    theme: $('themeSelect').value,
    sourceName: $('sourceName').value.trim() || 'yo',
    destName: $('destName').value.trim() || 'el',
    sourceAvatar: $('sourceAvatar').value.trim(),
    destAvatar: $('destAvatar').value.trim(),
    statusText: $('statusText').value.trim(),
    baseDelay: Number($('baseDelay').value) || 0,
    typingSpeed: Number($('typingSpeed').value) || 0,
    avatarMode: $('avatarMode').value,
    nameMode: $('nameMode').value,
    backgroundMode: $('backgroundMode').value,
    chromaColor: $('chromaColor').value || '#00ff00'
  };
}

function applyTheme() {
  const cfg = getConfig();
  document.documentElement.style.setProperty('--chroma', cfg.chromaColor);
  document.body.classList.toggle('chroma-active', cfg.backgroundMode === 'chroma');
  document.body.className = document.body.className
    .split(' ')
    .filter(c => !c.startsWith('theme-'))
    .join(' ');
  document.body.classList.add(`theme-${cfg.theme}`);

  const meta = themeMeta[cfg.theme] || themeMeta.instagram;
  $('headerIcons').textContent = meta.icons;
  $('footerPlaceholder').textContent = meta.footer;
  $('footerIcon').textContent = meta.footerIcon;

  if (!$('statusText').value.trim() || Object.values(themeMeta).some(t => t.status === $('statusText').value.trim())) {
    $('statusText').value = meta.status;
  }
  applyHeader();
}

function applyHeader() {
  const cfg = getConfig();
  $('headerName').textContent = cfg.destName;
  $('headerAvatar').src = cfg.destAvatar;
  $('headerStatus').textContent = cfg.statusText || (themeMeta[cfg.theme]?.status || 'Activo ahora');
}

function parseMessages() {
  try {
    const parsed = JSON.parse($('scriptInput').value);
    if (!Array.isArray(parsed)) throw new Error('El JSON debe ser una lista []');
    return parsed.map((msg) => ({
      from: msg.from === 'dest' ? 'dest' : 'source',
      text: String(msg.text ?? ''),
      delay: Number(msg.delay ?? 0)
    }));
  } catch (error) {
    alert('JSON inválido: ' + error.message);
    return [];
  }
}

function scrollBottom() {
  const area = $('chatArea');
  area.scrollTop = area.scrollHeight;
}

function shouldShowAvatar(from, cfg) {
  if (cfg.avatarMode === 'none') return false;
  if (cfg.avatarMode === 'both') return true;
  return from === 'dest';
}

function shouldShowName(from, cfg) {
  if (cfg.nameMode === 'none') return false;
  if (cfg.nameMode === 'both') return true;
  return from === 'dest';
}

function avatarFor(from, cfg) {
  return from === 'source' ? cfg.sourceAvatar : cfg.destAvatar;
}

function nameFor(from, cfg) {
  return from === 'source' ? cfg.sourceName : cfg.destName;
}

function addAvatar(row, from, cfg) {
  if (!shouldShowAvatar(from, cfg)) {
    row.classList.add('no-avatar');
    return;
  }
  const avatar = document.createElement('img');
  avatar.className = 'avatar';
  avatar.src = avatarFor(from, cfg);
  avatar.alt = nameFor(from, cfg);
  row.appendChild(avatar);
}

function addTyping(from) {
  const cfg = getConfig();
  const row = document.createElement('div');
  row.className = `messageRow ${from} typing`;
  row.dataset.typing = 'true';

  if (from === 'dest') addAvatar(row, from, cfg);

  const content = document.createElement('div');
  content.className = 'messageContent';

  if (shouldShowName(from, cfg)) {
    const sender = document.createElement('span');
    sender.className = 'senderName';
    sender.textContent = nameFor(from, cfg);
    content.appendChild(sender);
  }

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = '•••';
  content.appendChild(bubble);
  row.appendChild(content);

  if (from === 'source') addAvatar(row, from, cfg);

  $('chatArea').appendChild(row);
  scrollBottom();
  return row;
}

function addMessage(message) {
  const cfg = getConfig();
  const row = document.createElement('div');
  row.className = `messageRow ${message.from}`;

  if (message.from === 'dest') addAvatar(row, message.from, cfg);

  const content = document.createElement('div');
  content.className = 'messageContent';

  if (shouldShowName(message.from, cfg)) {
    const sender = document.createElement('span');
    sender.className = 'senderName';
    sender.textContent = nameFor(message.from, cfg);
    content.appendChild(sender);
  }

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = message.text;
  content.appendChild(bubble);
  row.appendChild(content);

  if (message.from === 'source') addAvatar(row, message.from, cfg);

  $('chatArea').appendChild(row);
  scrollBottom();
}

async function play() {
  if (state.playing && state.paused) { state.paused = false; return; }
  if (state.playing) return;

  applyHeader();
  state.messages = parseMessages();
  if (!state.messages.length) return;
  state.playing = true;
  state.paused = false;

  while (state.index < state.messages.length && state.playing) {
    while (state.paused) await sleep(120);
    const msg = state.messages[state.index];
    const cfg = getConfig();
    const wait = msg.delay || cfg.baseDelay;
    if (wait > 0) await sleep(wait);
    if (!state.playing) break;

    const typing = addTyping(msg.from);
    const typingMs = Math.min(1800, Math.max(350, msg.text.length * cfg.typingSpeed));
    await sleep(typingMs);
    typing.remove();
    if (!state.playing) break;

    addMessage(msg);
    state.index += 1;
  }
  state.playing = false;
}

function pause() { if (state.playing) state.paused = true; }
function reset() { clearTimers(); state.playing = false; state.paused = false; state.index = 0; $('chatArea').innerHTML = ''; applyHeader(); }
function clearChat() { reset(); }

$('playBtn').addEventListener('click', play);
$('pauseBtn').addEventListener('click', pause);
$('resetBtn').addEventListener('click', reset);
$('clearBtn').addEventListener('click', clearChat);
$('themeSelect').addEventListener('change', applyTheme);
$('backgroundMode').addEventListener('change', applyTheme);
$('chromaColor').addEventListener('input', applyTheme);
$('avatarMode').addEventListener('change', reset);
$('nameMode').addEventListener('change', reset);
$('toggleChromaBtn').addEventListener('click', () => {
  $('backgroundMode').value = $('backgroundMode').value === 'chroma' ? 'normal' : 'chroma';
  applyTheme();
});
$('toggleControls').addEventListener('click', () => {
  document.body.classList.toggle('hide-controls');
  $('toggleControls').textContent = document.body.classList.contains('hide-controls') ? 'Mostrar controles' : 'Ocultar controles';
});
['sourceName', 'destName', 'sourceAvatar', 'destAvatar', 'statusText'].forEach((id) => $(id).addEventListener('input', applyHeader));

applyTheme();
