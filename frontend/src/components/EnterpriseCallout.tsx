import React from 'react';

export default function EnterpriseCallout() {
  return (
    <section className="section" id="enterprise" style={{ background: 'var(--card)', padding: '4rem 0', position: 'relative' }}>
      {/* Hexagon pattern background */}
      <div style={{
        position: 'absolute',
        inset: 0,
        backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\"200\" height=\"200\" viewBox=\"0 0 100 100\" xmlns=\"http://www.w3.org/2000/svg\"%3E%3Cpolygon points=\"50,0 61,35 98,35 68,57 79,91 50,70 21,91 32,57 2,35 39,35\" fill=\"%23D4AF37\" fill-opacity=\"0.07\" stroke=\"%23D4AF37\" stroke-width=\"0.5\"/%3E%3C/svg%3E")',
        opacity: 0.2,
        zIndex: 0
      }} />
      <div className="container" style={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
        <h2 className="section-title" style={{ color: 'var(--gold)' }}>Enterprise Ready</h2>
        <p style={{ color: 'var(--gray)', margin: '1rem 0' }}>
          Tailor‑made SLAs, dedicated support, and on‑prem deployments for mission‑critical workloads.
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap', marginTop: '1rem' }}>
          <span className="pill">99.9% SLA</span>
          <span className="pill">On‑prem Docker</span>
          <span className="pill">Dedicated Account</span>
        </div>
        <button className="btn filled" style={{ marginTop: '2rem' }}>Contact Sales</button>
      </div>
    </section>
  );
}
