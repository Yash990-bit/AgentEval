import React from 'react';
import { Template } from '../../types';

interface Props {
  template: Template;
  onUse: () => void;
  onDetails?: (template: Template) => void;
}

const TemplateCard: React.FC<Props> = ({ template, onUse, onDetails }) => {
  const handleDetails = () => {
    if (onDetails) onDetails(template);
  };

  return (
    <div className="bg-white bg-opacity-20 backdrop-blur-lg rounded-xl shadow-lg p-4 flex flex-col transition-transform hover:scale-105">
      <h3 className="text-lg font-semibold text-white mb-2" title={template.name}>
        {template.name.length > 30 ? `${template.name.slice(0, 27)}...` : template.name}
      </h3>
      <p className="text-sm text-gray-200 flex-grow" title={template.description}>
        {template.description.length > 80 ? `${template.description.slice(0, 77)}...` : template.description}
      </p>
      <div className="mt-4 flex justify-between">
        <button
          onClick={onUse}
          className="bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium py-1 px-3 rounded"
        >
          Use
        </button>
        {onDetails && (
          <button
            onClick={handleDetails}
            className="bg-gray-600 hover:bg-gray-500 text-white text-sm font-medium py-1 px-3 rounded"
          >
            Details
          </button>
        )}
      </div>
    </div>
  );
};

export default TemplateCard;
