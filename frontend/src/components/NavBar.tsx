import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Menu, X } from 'lucide-react';

export default function NavBar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 100);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleMenu = () => setMobileOpen(!mobileOpen);

  const navClass = `nav ${scrolled ? 'scrolled' : ''}`;

  const links = [
    { href: '#features', label: 'Features' },
    { href: '#how-it-works', label: 'How It Works' },
    { href: '#simulations', label: 'Simulations' },
    { href: '#pricing', label: 'Pricing' },
    { href: '#enterprise', label: 'Enterprise' },
  ];

  return (
    <nav id="nav" className={navClass}>
      <div className="container flex justify-between items-center">
        {/* Logo */}
        <div className="logo flex items-center">
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="var(--gold)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="mr-2"
          >
            <polygon points="12 2 22 8 22 16 12 22 2 16 2 8 12 2" />
          </svg>
          <span className="text-gold-gradient" style={{ fontFamily: 'var(--font-display)', fontSize: '22px' }}>
            AgentVerse
          </span>
        </div>
        {/* Desktop Links */}
        <ul className="hidden md:flex space-x-6">
          {links.map((link) => (
            <li key={link.href}>
              <Link href={link.href} className="nav-link">
                {link.label}
              </Link>
            </li>
          ))}
        </ul>
        {/* CTA Buttons */}
        <div className="hidden md:flex space-x-4">
          <button className="btn ghost">Sign In</button>
          <button className="btn filled">Start Free Trial</button>
        </div>
        {/* Mobile Hamburger */}
        <button className="md:hidden" onClick={toggleMenu} aria-label="Menu">
          {mobileOpen ? <X size={24} strokeWidth={2} color="var(--gold)" /> : <Menu size={24} strokeWidth={2} color="var(--gold)" />}
        </button>
      </div>
      {/* Mobile Overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-90 flex flex-col items-center justify-center z-50">
          <ul className="flex flex-col space-y-6 text-2xl text-center">
            {links.map((link) => (
              <li key={link.href}>
                <Link href={link.href} onClick={() => setMobileOpen(false)} className="nav-link">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
          <div className="flex flex-col space-y-4 mt-8">
            <button className="btn ghost" onClick={() => setMobileOpen(false)}>
              Sign In
            </button>
            <button className="btn filled" onClick={() => setMobileOpen(false)}>
              Start Free Trial
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}
