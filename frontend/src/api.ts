
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
  
  export async function upload(file: File): Promise<Document> {
    const fd = new FormData();
    fd.append('file', file);
    const r = await fetch('/api/documents', { method: 'POST', body: fd });
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  }
  
  export async function listDocuments(): Promise<Document[]> {
    const r = await fetch('/api/documents');
    return r.json();
  }
  
  export async function deleteDocument(id: string): Promise<void> {
    await fetch(`/api/documents/${id}`, { method: 'DELETE' });
  }
  
  export async function chat(
    question: string,
    doc_ids: string[],
    history: { role: string; content: string }[],
  ): Promise<ChatResponse> {
    const r = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, doc_ids, history }),
    });
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  }