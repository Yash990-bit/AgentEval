import React, { useEffect, useRef, useState } from 'react';

export default function Metrics() {
  const stats = [
    { label: 'Agents Simulated', value: 50000000 },
    { label: 'Simulations Run', value: 120000000 },
    { label: 'Uptime', value: 99.9, suffix: '%' },
    { label: 'Enterprise Clients', value: 238 },
  ];

  const [counts, setCounts] = useState(stats.map(() => 0));
  const refs = useRef<(HTMLSpanElement | null)[]>([]);

  useEffect(() => {
    const durations = 2000; // ms
    const start = performance.now();
    const animate = (now: number) => {
      const progress = Math.min((now - start) / durations, 1);
      const newCounts = stats.map((s, i) => Math.floor(s.value * progress));
      setCounts(newCounts);
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, []);

  return (
    <section className="section" id="metrics">
      <div className="container">
        <h2 className="section-title">Trusted by the world’s leading AI teams</h2>
        <div className="cards-grid">
          {stats.map((s, i) => (
            <div className="card" key={i}>
              <h4 className="counter" ref={el => { refs.current[i] = el; }}>{counts[i].toLocaleString()}{s.suffix || ''}</h4>
              <p>{s.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
