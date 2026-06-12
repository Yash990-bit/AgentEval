import React from 'react';

export default function FinalCTA() {
  return (
    <section className="section" id="final-cta" style={{ position: 'relative', padding: '6rem 0', background: 'var(--bg)' }}>
      {/* Watermark text */}
      <div style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        pointerEvents: 'none',
        color: 'var(--gold-glow)',
        fontSize: '12rem',
        fontFamily: 'var(--font-display)',
        userSelect: 'none',
        opacity: 0.1,
        transform: 'scale(1.2)'
      }}>
        AgentVerse
      </div>
      <div className="container" style={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
        <h2 className="section-title" style={{ color: 'var(--gold)' }}>Ready to Simulate the Future?</h2>
        <p style={{ color: 'var(--gray)', margin: '1rem 0' }}>
          Join the leading AI teams that trust AgentVerse for safe, scalable, and intelligent agent simulations.
        </p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '1.5rem' }}>
          <button className="btn filled">Start Free Trial</button>
          <button className="btn ghost">Book a Demo</button>
        </div>
        <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'center', gap: '1rem' }}>
          <span className="pill">SOC 2 Certified</span>
          <span className="pill">ISO 27001</span>
          <span className="pill">GDPR Ready</span>
        </div>
      </div>
    </section>
  );
}
