// src/lib/d3-visualizer.ts
import * as d3 from 'd3';

/**
 * Types for node and link data expected by the visualizer.
 */
export interface AgentNode {
  id: string;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface LinkEdge {
  source: string | AgentNode;
  target: string | AgentNode;
}

/**
 * Render a D3 force‑directed simulation inside a given HTML container.
 *
 * The function is idempotent – calling it multiple times will clear the
 * previous SVG and create a fresh simulation based on the provided data.
 *
 * @param container The HTML element (usually a div) that will host the SVG.
 * @param nodes Array of node objects.
 * @param links Array of link objects.
 */
export function renderSimulation(
  container: HTMLElement,
  nodes: AgentNode[],
  links: LinkEdge[]
): void {
  // Clear any existing SVG content.
  d3.select(container).selectAll('svg').remove();

  const width = container.clientWidth;
  const height = container.clientHeight;

  const svg = d3
    .select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .style('overflow', 'visible');

  // Define a subtle glass‑morphic background for the simulation area.
  svg
    .append('rect')
    .attr('width', width)
    .attr('height', height)
    .attr('fill', 'rgba(255,255,255,0.1)')
    .attr('stroke', 'rgba(255,255,255,0.2)')
    .attr('stroke-width', 1)
    .style('backdrop-filter', 'blur(10px)');

  // Create a simulation with forces.
  const simulation = d3.forceSimulation(nodes as any)
    .force('link', d3.forceLink(links as any).id((d: any) => d.id).distance(150))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide(40));

  // Draw links.
  const link = svg
    .append('g')
    .attr('stroke', '#aaa')
    .attr('stroke-opacity', 0.6)
    .selectAll('line')
    .data(links)
    .enter()
    .append('line')
    .attr('stroke-width', 2);

  // Draw nodes.
  const node = svg
    .append('g')
    .selectAll('circle')
    .data(nodes)
    .enter()
    .append('circle')
    .attr('r', 20)
    .attr('fill', 'rgba(255,255,255,0.25)')
    .attr('stroke', 'rgba(255,255,255,0.6)')
    .attr('stroke-width', 2)
    .style('backdrop-filter', 'blur(4px)')
    .call(
      d3
        .drag<SVGCircleElement, AgentNode>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
    );

  // Add labels on nodes.
  const label = svg
    .append('g')
    .selectAll('text')
    .data(nodes)
    .enter()
    .append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', '.35em')
    .attr('font-size', '12px')
    .attr('fill', '#fff')
    .text((d) => d.id);

  // Tick handler to update positions.
  simulation.on('tick', () => {
    link
      .attr('x1', (d) => (d.source as AgentNode).x!)
      .attr('y1', (d) => (d.source as AgentNode).y!)
      .attr('x2', (d) => (d.target as AgentNode).x!)
      .attr('y2', (d) => (d.target as AgentNode).y!);

    node.attr('cx', (d) => d.x!).attr('cy', (d) => d.y!);

    label.attr('x', (d) => d.x!).attr('y', (d) => d.y!);
  });
}
