"use client";

import React from 'react';
import { usePathname } from 'next/navigation';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import '../globals.css';
import axios from 'axios';

if (typeof window !== 'undefined') {
  let apiBase = process.env.NEXT_PUBLIC_API_URL;
  if (apiBase) {
    // Sanitize by stripping trailing /api/v1, /api, or /
    apiBase = apiBase.replace(/\/api\/v1\/?$/, '').replace(/\/api\/?$/, '').replace(/\/$/, '');
    axios.defaults.baseURL = apiBase;
  } else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    axios.defaults.baseURL = 'http://localhost:8000';
  }
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isRootSpa = pathname === '/';

  if (isRootSpa) {
    return (
      <html lang="en">
        <body className="antialiased">
          {children}
        </body>
      </html>
    );
  }

  return (
    <html lang="en">
      <body className="antialiased">
        <Sidebar />
        <Header />
        <main className="ml-60 pt-16 overflow-auto" style={{ height: 'calc(100vh - 64px)' }}>
          {children}
        </main>
      </body>
    </html>
  );
}
