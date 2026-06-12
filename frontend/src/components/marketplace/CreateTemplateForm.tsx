import React, { useState } from 'react';
import axios from 'axios';
import { RoleEnum } from '../../types';

interface Props {
  onClose: () => void;
  onCreate: () => void; // callback to refresh list after creation
}

const CreateTemplateForm: React.FC<Props> = ({ onClose, onCreate }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [role, setRole] = useState<RoleEnum>('research');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await axios.post('/api/v1/templates', {
        name,
        description,
        role,
        system_prompt: systemPrompt,
        // other fields can be added as needed
      });
      onCreate();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create template');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center backdrop-blur-sm">
      <div className="bg-gray-900 bg-opacity-90 rounded-xl p-6 w-11/12 max-w-lg text-white shadow-lg relative">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-400 hover:text-white text-xl"
        >
          ✕
        </button>
        <h2 className="text-2xl font-bold mb-4">Create New Template</h2>
        {error && (
          <div className="bg-red-600 text-white p-2 rounded mb-4">{error}</div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Template Name"
            className="w-full border rounded p-2 text-black"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <select
            className="w-full border rounded p-2 text-black"
            value={role}
            onChange={(e) => setRole(e.target.value as RoleEnum)}
          >
            <option value="research">Research</option>
            <option value="coding">Coding</option>
            <option value="data_analyst">Data Analyst</option>
            <option value="customer_support">Customer Support</option>
            <option value="strategic_planner">Strategic Planner</option>
            <option value="security_auditor">Security Auditor</option>
            <option value="negotiator">Negotiator</option>
            <option value="coordinator">Coordinator</option>
          </select>
          <textarea
            placeholder="Description"
            className="w-full border rounded p-2 text-black"
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          />
          <textarea
            placeholder="System Prompt (instructions for the agent)"
            className="w-full border rounded p-2 text-black"
            rows={5}
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            required
          />
          <button
            type="submit"
            className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded"
          >
            Create Template
          </button>
        </form>
      </div>
    </div>
  );
};

export default CreateTemplateForm;
