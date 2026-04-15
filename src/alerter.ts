import chalk from 'chalk';
import { CapabilityEntry, Store, saveStore } from './storage';

export const DEFAULT_RISK_THRESHOLD = 7;

export function checkAlerts(store: Store, threshold = DEFAULT_RISK_THRESHOLD): CapabilityEntry[] {
  const newAlerts = store.entries.filter(e => e.riskScore >= threshold && !e.alertSent);

  for (const entry of newAlerts) {
    entry.alertSent = true;
  }

  if (newAlerts.length > 0) saveStore(store);
  return newAlerts;
}

export function formatAlerts(alerts: CapabilityEntry[]): string {
  if (alerts.length === 0) return chalk.green('✅ No new high-risk items.');

  const lines = [chalk.red.bold(`\n🚨 ${alerts.length} HIGH-RISK ITEM(S) DETECTED\n`)];
  for (const a of alerts) {
    lines.push(`  ${chalk.red(`[Risk ${a.riskScore}]`)} ${chalk.bold(a.title)}`);
    lines.push(`  ${chalk.gray(a.url)}`);
    lines.push(`  ${chalk.gray(a.summary.slice(0, 120))}`);
    lines.push('');
  }
  return lines.join('\n');
}
