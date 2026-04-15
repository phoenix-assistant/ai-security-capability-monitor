#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import { fetchAllFeeds } from './aggregator';
import { loadStore, saveStore, addEntry } from './storage';
import { checkAlerts, formatAlerts } from './alerter';
import { renderTimeline } from './timeline';
import { TAXONOMY } from './taxonomy';

const program = new Command();

program
  .name('ai-cap')
  .description('AI Security Capability Monitor — track emerging AI offensive & defensive capabilities')
  .version('1.0.0');

program
  .command('update')
  .description('Fetch latest entries from RSS feeds')
  .action(async () => {
    console.log(chalk.blue('🔄 Fetching feeds...'));
    const store = loadStore();
    const entries = await fetchAllFeeds();
    let added = 0;
    for (const e of entries) {
      if (addEntry(store, e)) added++;
    }
    saveStore(store);
    console.log(chalk.green(`✅ Added ${added} new entries (${store.entries.length} total)`));

    const alerts = checkAlerts(store);
    console.log(formatAlerts(alerts));
  });

program
  .command('report')
  .description('Show capability report')
  .option('--risk-min <n>', 'Minimum risk score to show', '1')
  .option('--category <cat>', 'Filter by category (offensive/defensive)')
  .action((opts) => {
    const store = loadStore();
    const minRisk = parseInt(opts.riskMin, 10) || 1;
    let filtered = store.entries.filter(e => e.riskScore >= minRisk);
    if (opts.category) filtered = filtered.filter(e => {
      return e.capabilities.some(id => {
        const t = TAXONOMY.find(x => x.id === id);
        return t?.category === opts.category;
      });
    });

    filtered.sort((a, b) => b.riskScore - a.riskScore);

    console.log(chalk.bold(`\n📊 AI Security Report (risk >= ${minRisk})\n`));
    console.log(`Total: ${filtered.length} entries\n`);

    for (const e of filtered.slice(0, 50)) {
      const riskColor = e.riskScore >= 7 ? chalk.red : e.riskScore >= 4 ? chalk.yellow : chalk.green;
      console.log(`  ${riskColor(`[${e.riskScore}]`)} ${e.title}`);
      console.log(`      ${chalk.gray(e.source)} · ${chalk.gray(e.capabilities.join(', '))} · ${chalk.gray(e.url)}`);
    }
    console.log('');
  });

program
  .command('timeline')
  .description('Show chronological timeline of developments')
  .option('--limit <n>', 'Max entries to show', '30')
  .action((opts) => {
    const store = loadStore();
    console.log(renderTimeline(store.entries, parseInt(opts.limit, 10)));
  });

program
  .command('taxonomy')
  .description('Show capability taxonomy')
  .action(() => {
    console.log(chalk.bold('\n🏷️  AI Security Capability Taxonomy\n'));
    for (const cat of ['offensive', 'defensive'] as const) {
      console.log(chalk.bold(cat === 'offensive' ? chalk.red('  ⚔️  Offensive') : chalk.cyan('  🛡️  Defensive')));
      for (const t of TAXONOMY.filter(x => x.category === cat)) {
        const risk = t.baseRisk >= 7 ? chalk.red(`[${t.baseRisk}]`) : chalk.yellow(`[${t.baseRisk}]`);
        console.log(`    ${risk} ${t.name} — ${chalk.gray(t.description)}`);
      }
      console.log('');
    }
  });

program.parse();
