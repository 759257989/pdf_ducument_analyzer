
import { clearAuth, getToken } from './auth';

export type Document = {
    id: string;
    filename: string;
    page_count: number;
    chunk_count: number;
    status: 'processing' | 'ready' | 'failed';
    error?: string;
  };
  
  export type Citation = {
    doc_id: string;
    filename: string;
    page_number: number;
    snippet: string;
  };
  
  export type ChatResponse = { answer: string; citations: Citation[] };

  async function authFetch(url: string, init: RequestInit = {}): Promise<Response> {
    const token = getToken();
    const r = await fetch(url, {
      ...init,
      headers: {
        ...(init.headers || {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });
    if (r.status === 401) {
      clearAuth();
      window.location.reload();
      throw new Error('登录已过期');
    }
    return r;
  }
  
  export async function upload(file: File): Promise<Document> {
    const fd = new FormData();
    fd.append('file', file);
    const r = await authFetch('/api/documents', { method: 'POST', body: fd });
    if (r.status === 409) {
        const body = await r.json();
        throw new Error(
        `该 PDF 已上传过：${body.detail.existing_filename}`,
        );
    }
    if (!r.ok) throw new Error(await r.text());
    return r.json();
    }
  
  export async function listDocuments(): Promise<Document[]> {
    const r = await authFetch('/api/documents');
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  }
  
  export async function deleteDocument(id: string): Promise<void> {
    const r = await authFetch(`/api/documents/${id}`, { method: 'DELETE' });
    if (!r.ok) throw new Error(await r.text());
  }
  
  export async function chat(
    question: string,
    doc_ids: string[],
    history: { role: string; content: string }[],
  ): Promise<ChatResponse> {
    const r = await authFetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, doc_ids, history }),
    });
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  }

  export async function login(username: string, password: string) {
    const r = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!r.ok) throw new Error((await r.json()).detail || '登录失败');
    return r.json() as Promise<{ token: string; username: string }>;
  }

  export async function register(username: string, password: string) {
    const r = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!r.ok) throw new Error((await r.json()).detail || '注册失败');
    return r.json() as Promise<{ token: string; username: string }>;
  }