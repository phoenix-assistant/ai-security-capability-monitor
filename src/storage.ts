import fs from 'fs';
import path from 'path';

export interface CapabilityEntry {
  id: string;
  title: string;
  url: string;
  source: string;
  date: string;
  summary: string;
  capabilities: string[]; // taxonomy IDs
  riskScore: number;
  alertSent: boolean;
}

export interface Store {
  entries: CapabilityEntry[];
  lastUpdated: string;
}

const DATA_DIR = path.join(process.env.HOME || '~', '.ai-cap');
const DB_PATH = path.join(DATA_DIR, 'store.json');

function ensureDir(): void {
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
}

export function loadStore(): Store {
  ensureDir();
  if (!fs.existsSync(DB_PATH)) return { entries: [], lastUpdated: '' };
  return JSON.parse(fs.readFileSync(DB_PATH, 'utf-8'));
}

export function saveStore(store: Store): void {
  ensureDir();
  store.lastUpdated = new Date().toISOString();
  fs.writeFileSync(DB_PATH, JSON.stringify(store, null, 2));
}

export function addEntry(store: Store, entry: CapabilityEntry): boolean {
  if (store.entries.some(e => e.id === entry.id)) return false;
  store.entries.push(entry);
  return true;
}

export function createEntryId(url: string): string {
  const crypto = require('crypto');
  return crypto.createHash('sha256').update(url).digest('hex').slice(0, 12);
}
