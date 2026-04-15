export type CapabilityCategory = 'offensive' | 'defensive';

export interface CapabilityType {
  id: string;
  name: string;
  category: CapabilityCategory;
  description: string;
  baseRisk: number; // 1-10
  keywords: string[];
}

export const TAXONOMY: CapabilityType[] = [
  // Offensive
  { id: 'jailbreak', name: 'Jailbreak', category: 'offensive', description: 'Techniques to bypass model safety filters', baseRisk: 8, keywords: ['jailbreak', 'bypass', 'safety filter', 'guardrail bypass', 'uncensored'] },
  { id: 'prompt-injection', name: 'Prompt Injection', category: 'offensive', description: 'Injecting malicious instructions into prompts', baseRisk: 9, keywords: ['prompt injection', 'indirect injection', 'instruction hijack', 'prompt attack'] },
  { id: 'model-stealing', name: 'Model Stealing', category: 'offensive', description: 'Extracting model weights or behavior', baseRisk: 7, keywords: ['model extraction', 'model stealing', 'weight theft', 'distillation attack', 'model clone'] },
  { id: 'data-poisoning', name: 'Data Poisoning', category: 'offensive', description: 'Corrupting training data to manipulate models', baseRisk: 8, keywords: ['data poisoning', 'backdoor', 'trojan', 'training attack'] },
  { id: 'adversarial-examples', name: 'Adversarial Examples', category: 'offensive', description: 'Crafted inputs that fool models', baseRisk: 6, keywords: ['adversarial', 'perturbation', 'evasion attack', 'adversarial example'] },
  { id: 'deepfake', name: 'Deepfake / Synthetic Media', category: 'offensive', description: 'AI-generated synthetic media for deception', baseRisk: 7, keywords: ['deepfake', 'synthetic media', 'face swap', 'voice clone'] },
  // Defensive
  { id: 'guardrails', name: 'Guardrails', category: 'defensive', description: 'Safety constraints and content filters', baseRisk: 2, keywords: ['guardrail', 'safety', 'content filter', 'moderation', 'alignment'] },
  { id: 'monitoring', name: 'AI Monitoring', category: 'defensive', description: 'Detection and observability for AI systems', baseRisk: 2, keywords: ['monitoring', 'detection', 'observability', 'anomaly detection', 'audit'] },
  { id: 'red-teaming', name: 'Red Teaming', category: 'defensive', description: 'Proactive security testing of AI systems', baseRisk: 3, keywords: ['red team', 'security testing', 'evaluation', 'benchmark'] },
  { id: 'watermarking', name: 'Watermarking', category: 'defensive', description: 'Marking AI-generated content for provenance', baseRisk: 1, keywords: ['watermark', 'provenance', 'c2pa', 'content authenticity'] },
];

export function classifyText(text: string): CapabilityType[] {
  const lower = text.toLowerCase();
  return TAXONOMY.filter(cap => cap.keywords.some(kw => lower.includes(kw)));
}
