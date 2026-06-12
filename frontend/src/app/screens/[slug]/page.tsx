import React from 'react';
import ScreenDetailClient from './ScreenDetailClient';

// Return static params list for Next.js to export dynamic path html pages
export async function generateStaticParams() {
  return [
    { slug: 'coordinator' },
    { slug: 'planner' },
    { slug: 'researcher' },
    { slug: 'analyst' },
    { slug: 'security-auditor' }
  ];
}

// Next.js page component
export default async function Page(props: { params: Promise<{ slug: string }> }) {
  const resolvedParams = await props.params;
  return <ScreenDetailClient slug={resolvedParams.slug} />;
}
