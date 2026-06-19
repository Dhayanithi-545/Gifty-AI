import axios from 'axios';
import type {
  RunRequest,
  RunResponse,
  ReviewActionRequest,
  ContactResult,
  HealthResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 second timeout
});

export const giftAPI = {
  // Health check
  async health(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>('/health');
    return response.data;
  },

  // Run pipeline for contacts
  async runPipeline(request: RunRequest): Promise<RunResponse> {
    try {
      const response = await api.post<RunResponse>('/run', request);
      return response.data;
    } catch (error: any) {
      // Re-throw with better error handling
      if (error.code === 'ECONNABORTED') {
        throw new Error('Request timeout - server took too long to respond');
      }
      if (error.response) {
        throw error;
      }
      if (error.message.includes('Network Error')) {
        throw new Error('Network error - unable to connect to server');
      }
      throw new Error('Failed to connect to the server');
    }
  },

  // Get all contacts
  async getAllContacts(): Promise<{ contacts: ContactResult[] }> {
    const response = await api.get<{ contacts: ContactResult[] }>('/contacts');
    return response.data;
  },

  // Get specific contact
  async getContact(name: string): Promise<ContactResult> {
    const response = await api.get<ContactResult>(`/contacts/${encodeURIComponent(name)}`);
    return response.data;
  },

  // Review actions (approve/reject/edit/regenerate)
  async reviewAction(request: ReviewActionRequest): Promise<ContactResult> {
    try {
      const response = await api.post<ContactResult>('/review', request);
      return response.data;
    } catch (error: any) {
      if (error.code === 'ECONNABORTED') {
        throw new Error('Request timeout - server took too long to respond');
      }
      if (error.response) {
        throw error;
      }
      if (error.message.includes('Network Error')) {
        throw new Error('Network error - unable to connect to server');
      }
      throw new Error('Failed to connect to the server');
    }
  },
};

export default giftAPI;
