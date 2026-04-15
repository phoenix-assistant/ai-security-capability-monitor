import { TAXONOMY, CapabilityType } from './taxonomy';

export interface ScoringFactors {
  capabilities: string[];
  title: string;
  summary: string;
}

/**
 * Score risk 1-10 based on matched capabilities and content signals.
 */
export function scoreRisk(factors: ScoringFactors): number {
  const { capabilities, title, summary } = factors;
  if (capabilities.length === 0) return 1;

  // Base: max base risk of matched capabilities
  const matched = capabilities
    .map(id => TAXONOMY.find(t => t.id === id))
    .filter((t): t is CapabilityType => !!t);

  let score = Math.max(...matched.map(t => t.baseRisk), 1);

  // Boost for multiple offensive capabilities
  const offensiveCount = matched.filter(t => t.category === 'offensive').length;
  if (offensiveCount >= 2) score = Math.min(10, score + 1);

  // Boost for urgency signals
  const text = `${title} ${summary}`.toLowerCase();
  const urgencyTerms = ['zero-day', '0-day', 'critical', 'exploit', 'in the wild', 'active attack', 'emergency'];
  if (urgencyTerms.some(t => text.includes(t))) score = Math.min(10, score + 1);

  // Defensive-only items get lower scores
  if (matched.every(t => t.category === 'defensive')) score = Math.min(score, 3);

  return Math.max(1, Math.min(10, Math.round(score)));
}
