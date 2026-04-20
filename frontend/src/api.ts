
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
      throw new Error('Login expired');
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
        `This PDF has already been uploaded: ${body.detail.existing_filename}`,
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
  
  export type Conversation = {
    id: string;
    title: string;
    created_at: string;
  };
  
  export type MessageFromServer = {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    citations: Citation[];
    created_at: string;
  };
  
  export type ConversationDetail = Conversation & { messages: MessageFromServer[] };
  
  export async function listConversations(): Promise<Conversation[]> {
    const r = await authFetch('/api/conversations');
    return r.json();
  }
  
  export async function getConversation(id: string): Promise<ConversationDetail> {
    const r = await authFetch(`/api/conversations/${id}`);
    return r.json();
  }
  
  export async function deleteConversation(id: string): Promise<void> {
    await authFetch(`/api/conversations/${id}`, { method: 'DELETE' });
  }

  export async function chat(
    question: string,
    doc_ids: string[],
    conversation_id: string | null,
  ): Promise<ChatResponse & { conversation_id: string }> {
    const r = await authFetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, doc_ids, conversation_id }),
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
    if (!r.ok) throw new Error((await r.json()).detail || 'Login failed');
    return r.json() as Promise<{ token: string; username: string }>;
  }

  export async function register(username: string, password: string) {
    const r = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!r.ok) throw new Error((await r.json()).detail || 'Registration failed');
    return r.json() as Promise<{ token: string; username: string }>;
  }