import Parser from 'rss-parser';
import { classifyText } from './taxonomy';
import { scoreRisk } from './scorer';
import { CapabilityEntry, createEntryId } from './storage';

const parser = new Parser({ timeout: 15000 });

export interface FeedSource {
  name: string;
  url: string;
}

export const DEFAULT_FEEDS: FeedSource[] = [
  { name: 'arXiv CS.CR', url: 'https://rss.arxiv.org/rss/cs.CR' },
  { name: 'arXiv CS.AI', url: 'https://rss.arxiv.org/rss/cs.AI' },
  { name: 'BleepingComputer', url: 'https://www.bleepingcomputer.com/feed/' },
  { name: 'Wired Security', url: 'https://www.wired.com/feed/category/security/latest/rss' },
];

export async function fetchFeed(source: FeedSource): Promise<CapabilityEntry[]> {
  try {
    const feed = await parser.parseURL(source.url);
    const entries: CapabilityEntry[] = [];

    for (const item of feed.items || []) {
      const text = `${item.title || ''} ${item.contentSnippet || item.content || ''}`;
      const caps = classifyText(text);
      if (caps.length === 0) continue;

      const capIds = caps.map(c => c.id);
      const entry: CapabilityEntry = {
        id: createEntryId(item.link || item.title || ''),
        title: item.title || 'Untitled',
        url: item.link || '',
        source: source.name,
        date: item.isoDate || item.pubDate || new Date().toISOString(),
        summary: (item.contentSnippet || '').slice(0, 300),
        capabilities: capIds,
        riskScore: scoreRisk({ capabilities: capIds, title: item.title || '', summary: item.contentSnippet || '' }),
        alertSent: false,
      };
      entries.push(entry);
    }
    return entries;
  } catch (err) {
    console.error(`Failed to fetch ${source.name}: ${(err as Error).message}`);
    return [];
  }
}

export async function fetchAllFeeds(feeds: FeedSource[] = DEFAULT_FEEDS): Promise<CapabilityEntry[]> {
  const results = await Promise.allSettled(feeds.map(f => fetchFeed(f)));
  return results.flatMap(r => r.status === 'fulfilled' ? r.value : []);
}
