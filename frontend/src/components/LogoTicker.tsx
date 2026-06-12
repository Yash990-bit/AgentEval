import React from 'react';
import { LucideIcon, ArrowRight } from 'lucide-react';

const logos = [
  'OpenAI Labs',
  'Anthropic Partners',
  'Scale AI',
  'Hugging Face',
  'Cohere',
  'Mistral AI',
  'Stability AI',
  'Runway ML',
  'Weights & Biases',
  'LangChain',
  'Together AI',
  'Replicate',
  'Modal Labs',
  'Anyscale',
  'Baseten',
];

export default function LogoTicker() {
  return (
    <section className="section" id="logo-ticker" style={{ overflow: 'hidden', position: 'relative' }}>
      <div className="flex-center" style={{ justifyContent: 'center' }}>
        <p className="text-gray" style={{ marginBottom: '0.5rem' }}>Trusted by engineering teams at</p>
      </div>
      <div className="flex-center" style={{ whiteSpace: 'nowrap', animation: 'ticker 30s linear infinite' }}>
        {logos.map((name, i) => (
          <span key={i} style={{ margin: '0 2rem', fontFamily: 'var(--font-body)', color: 'var(--gray)' }}>
            {name}
          </span>
        ))}
      </div>
      <style jsx>{`
        @keyframes ticker {
          0% { transform: translateX(100%); }
          100% { transform: translateX(-100%); }
        }
      `}</style>
    </section>
  );
}
