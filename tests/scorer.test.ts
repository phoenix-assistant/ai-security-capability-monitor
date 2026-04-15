import { scoreRisk } from '../src/scorer';

describe('scoreRisk', () => {
  it('returns 1 for no capabilities', () => {
    expect(scoreRisk({ capabilities: [], title: '', summary: '' })).toBe(1);
  });

  it('scores prompt injection high', () => {
    const score = scoreRisk({ capabilities: ['prompt-injection'], title: 'Prompt Injection Attack', summary: 'New technique' });
    expect(score).toBeGreaterThanOrEqual(8);
  });

  it('boosts score for urgency terms', () => {
    const base = scoreRisk({ capabilities: ['jailbreak'], title: 'Jailbreak method', summary: 'A new approach' });
    const urgent = scoreRisk({ capabilities: ['jailbreak'], title: 'Critical zero-day jailbreak', summary: 'Active attack in the wild' });
    expect(urgent).toBeGreaterThanOrEqual(base);
  });

  it('caps defensive-only items at 3', () => {
    const score = scoreRisk({ capabilities: ['guardrails', 'monitoring'], title: 'New guardrails', summary: 'Safety improvement' });
    expect(score).toBeLessThanOrEqual(3);
  });

  it('boosts for multiple offensive capabilities', () => {
    const single = scoreRisk({ capabilities: ['jailbreak'], title: 'test', summary: '' });
    const multi = scoreRisk({ capabilities: ['jailbreak', 'prompt-injection'], title: 'test', summary: '' });
    expect(multi).toBeGreaterThanOrEqual(single);
  });

  it('always returns between 1 and 10', () => {
    for (const caps of [['jailbreak'], ['guardrails'], ['prompt-injection', 'model-stealing', 'data-poisoning']]) {
      const score = scoreRisk({ capabilities: caps, title: 'critical zero-day exploit in the wild', summary: 'emergency active attack' });
      expect(score).toBeGreaterThanOrEqual(1);
      expect(score).toBeLessThanOrEqual(10);
    }
  });
});
