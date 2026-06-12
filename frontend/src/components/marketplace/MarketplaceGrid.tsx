// frontend/src/components/marketplace/MarketplaceGrid.tsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import TemplateCard from "./TemplateCard";
import { Template } from "../../types";

interface Props {
  onUseTemplate: (templateId: string) => void;
  onDetails?: (template: Template) => void;
}

const MarketplaceGrid: React.FC<Props> = ({ onUseTemplate, onDetails }) => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [sortBy, setSortBy] = useState<"popular" | "newest" | "performance">("popular");

  const fetchTemplates = async () => {
    const params: any = {};
    if (search) params.search = search;
    if (roleFilter) params.role = roleFilter;
    if (sortBy) params.sort = sortBy;
    const res = await axios.get("/api/v1/templates", { params });
    setTemplates(res.data);
  };

  useEffect(() => {
    fetchTemplates();
  }, [search, roleFilter, sortBy]);

  return (
    <div className="mp-container">
      <div className="mp-controls">
        <input
          type="text"
          placeholder="Search templates…"
          className="mp-input"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="mp-select"
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
        >
          <option value="">All Roles</option>
          <option value="research">Research</option>
          <option value="coding">Coding</option>
          <option value="data_analyst">Data Analyst</option>
          <option value="customer_support">Customer Support</option>
          <option value="strategic_planner">Strategic Planner</option>
          <option value="security_auditor">Security Auditor</option>
          <option value="negotiator">Negotiator</option>
          <option value="coordinator">Coordinator</option>
        </select>
        <select
          className="mp-select"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
        >
          <option value="popular">Most Popular</option>
          <option value="newest">Newest</option>
          <option value="performance">Best Performance</option>
        </select>
      </div>
      <div className="mp-grid">
        {templates.map((tpl) => (
          <TemplateCard
            key={tpl.id}
            template={tpl}
            onUse={() => onUseTemplate(tpl.id)}
            onDetails={onDetails ? () => onDetails(tpl) : undefined}
          />
        ))}
      </div>
    </div>
  );
};

export default MarketplaceGrid;
