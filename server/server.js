// ATU HelpDesk — минимальный backend.
// Хранит вызовы специалиста в JSON-файле (data/calls.json).
// Для нагрузки в несколько параллельных вызовов этого достаточно;
// при росте — заменить readCalls/writeCalls на настоящую БД (SQLite/Postgres),
// сигнатуры остальных функций менять не придётся.

const express = require('express');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PORT = process.env.PORT || 3000;
const DATA_DIR = path.join(__dirname, 'data');
const CALLS_FILE = path.join(DATA_DIR, 'calls.json');
const APP_DIR = path.join(__dirname, '..', 'app');

if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
if (!fs.existsSync(CALLS_FILE)) fs.writeFileSync(CALLS_FILE, '[]', 'utf8');

// Простая последовательная очередь записи, чтобы параллельные запросы
// (несколько классов жмут кнопку одновременно) не затирали друг друга.
let writeQueue = Promise.resolve();
function readCalls() {
  try {
    const raw = fs.readFileSync(CALLS_FILE, 'utf8');
    return JSON.parse(raw || '[]');
  } catch (e) {
    console.error('readCalls error', e);
    return [];
  }
}
function writeCalls(calls) {
  writeQueue = writeQueue.then(() => new Promise((resolve, reject) => {
    fs.writeFile(CALLS_FILE, JSON.stringify(calls, null, 1), 'utf8', (err) => {
      if (err) { console.error('writeCalls error', err); reject(err); }
      else resolve();
    });
  }));
  return writeQueue;
}

const app = express();
app.use(express.json());

// --- API ---
app.get('/api/calls', (req, res) => {
  res.json(readCalls());
});

app.post('/api/calls', async (req, res) => {
  const { room, buildingName } = req.body || {};
  if (!room || typeof room !== 'string') {
    return res.status(400).json({ error: 'room is required' });
  }
  const calls = readCalls();
  const call = {
    id: 'c' + Date.now().toString(36) + crypto.randomBytes(3).toString('hex'),
    room,
    buildingName: buildingName || '',
    createdAt: Date.now(),
    status: 'new',
  };
  calls.push(call);
  try {
    await writeCalls(calls);
    res.status(201).json(readCalls());
  } catch (e) {
    res.status(500).json({ error: 'failed to save call' });
  }
});

app.patch('/api/calls/:id', async (req, res) => {
  const { status } = req.body || {};
  if (!['new', 'accepted', 'closed'].includes(status)) {
    return res.status(400).json({ error: 'invalid status' });
  }
  const calls = readCalls();
  const idx = calls.findIndex(c => c.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'call not found' });
  calls[idx].status = status;
  try {
    await writeCalls(calls);
    res.json(readCalls());
  } catch (e) {
    res.status(500).json({ error: 'failed to update call' });
  }
});

app.delete('/api/calls', async (req, res) => {
  try {
    await writeCalls([]);
    res.json([]);
  } catch (e) {
    res.status(500).json({ error: 'failed to clear calls' });
  }
});

app.get('/healthz', (req, res) => res.send('ok'));

// --- статика: терминал и табло ---
app.use('/', express.static(APP_DIR));

app.listen(PORT, () => {
  console.log(`ATU HelpDesk server listening on port ${PORT}`);
});
