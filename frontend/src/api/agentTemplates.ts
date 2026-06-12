import axios from 'axios';

export interface Template {
  id: string;
  name: string;
  role: string;
  description?: string;
  system_prompt?: string;
  tags?: string[];
  use_count?: number;
}

export const fetchTemplates = async (params?: any) => {
  const response = await axios.get('/api/v1/templates', { params });
  return response.data as Template[];
};

export const createTemplate = async (payload: any) => {
  const response = await axios.post('/api/v1/templates', payload);
  return response.data as Template;
};

export const useTemplate = async (templateId: string) => {
  await axios.post(`/api/v1/templates/${templateId}/use`);
};

export const forkTemplate = async (templateId: string) => {
  const response = await axios.post(`/api/v1/templates/${templateId}/fork`);
  return response.data as Template;
};
