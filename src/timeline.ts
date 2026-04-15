import chalk from 'chalk';
import { CapabilityEntry } from './storage';
import { TAXONOMY } from './taxonomy';

export function renderTimeline(entries: CapabilityEntry[], limit = 30): string {
  const sorted = [...entries].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()).slice(0, limit);

  if (sorted.length === 0) return chalk.yellow('No entries found. Run `ai-cap update` first.');

  const lines: string[] = [chalk.bold('\n📅 AI Security Capability Timeline\n')];

  for (const e of sorted) {
    const date = new Date(e.date).toISOString().slice(0, 10);
    const riskColor = e.riskScore >= 7 ? chalk.red : e.riskScore >= 4 ? chalk.yellow : chalk.green;
    const cats = e.capabilities.map(id => {
      const t = TAXONOMY.find(x => x.id === id);
      return t ? (t.category === 'offensive' ? chalk.red(t.name) : chalk.cyan(t.name)) : id;
    }).join(', ');

    lines.push(`  ${chalk.gray(date)} ${riskColor(`[Risk ${e.riskScore}]`)} ${chalk.white(e.title)}`);
    lines.push(`           ${chalk.gray(e.source)} · ${cats}`);
    lines.push('');
  }

  return lines.join('\n');
}
