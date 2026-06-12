import React from 'react';
import { Template } from '../../types';

interface Props {
  template: Template | null;
  onClose: () => void;
  onUse: (id: string) => void;
  onFork: (id: string) => void;
}

const TemplateDetailModal: React.FC<Props> = ({ template, onClose, onUse, onFork }) => {
  if (!template) return null;
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center backdrop-blur-sm">
      <div className="bg-gray-900 bg-opacity-90 rounded-xl p-6 w-11/12 max-w-2xl text-white shadow-lg relative">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-400 hover:text-white text-xl"
        >✕</button>
        <h2 className="text-2xl font-bold mb-4">{template.name}</h2>
        <p className="mb-2"><strong>Role:</strong> {template.role}</p>
        <p className="mb-2"><strong>Description:</strong> {template.description}</p>
        <pre className="bg-gray-800 p-3 rounded overflow-auto mb-4" style={{ maxHeight: '200px' }}>
{template.system_prompt}
        </pre>
        <div className="flex space-x-4">
          <button
            onClick={() => onUse(template.id)}
            className="bg-indigo-600 hover:bg-indigo-500 text-white py-1 px-3 rounded"
          >Use</button>
          <button
            onClick={() => onFork(template.id)}
            className="bg-green-600 hover:bg-green-500 text-white py-1 px-3 rounded"
          >Fork</button>
        </div>
      </div>
    </div>
  );
};

export default TemplateDetailModal;
