import { useEffect, useState } from 'react';
import {
  listDocuments, upload, deleteDocument, chat,
  type Document, type Citation,
} from './api';

type Msg = { role: 'user' | 'assistant'; content: string; citations?: Citation[] };

export default function App() {
  const [docs, setDocs] = useState<Document[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const refresh = async () => setDocs(await listDocuments());

  useEffect(() => { refresh(); }, []);

  // when there are processing documents, poll every 2 seconds
  useEffect(() => {
    if (docs.some(d => d.status === 'processing')) {
      const t = setInterval(refresh, 2000);
      return () => clearInterval(t);
    }
  }, [docs]);

  const handleUpload = async (f: File) => {
    await upload(f);
    refresh();
  };

  const handleAsk = async () => {
    if (!input.trim() || selected.size === 0 || loading) return;
    const q = input;
    setInput('');
    const next: Msg[] = [...messages, { role: 'user', content: q }];
    setMessages(next);
    setLoading(true);
    try {
      const resp = await chat(
        q,
        [...selected],
        next.slice(0, -1).map(m => ({ role: m.role, content: m.content })),
      );
      setMessages([...next, { role: 'assistant', content: resp.answer, citations: resp.citations }]);
    } catch (e: any) {
      setMessages([...next, { role: 'assistant', content: `error: ${e.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen flex">
      <aside className="w-80 border-r p-4 overflow-y-auto bg-gray-50">
        <h2 className="font-semibold mb-3">My documents</h2>
        <input
          type="file" accept="application/pdf"
          onChange={e => e.target.files?.[0] && handleUpload(e.target.files[0])}
          className="mb-4 text-sm"
        />
        {docs.length === 0 && <p className="text-sm text-gray-400">No PDF uploaded yet</p>}
        {docs.map(d => (
          <div key={d.id} className="mb-2 flex items-start gap-2">
            <input
              type="checkbox"
              disabled={d.status !== 'ready'}
              checked={selected.has(d.id)}
              onChange={e => {
                const s = new Set(selected);
                e.target.checked ? s.add(d.id) : s.delete(d.id);
                setSelected(s);
              }}
              className="mt-1"
            />
            <div className="flex-1 text-sm min-w-0">
              <div className="truncate" title={d.filename}>{d.filename}</div>
              <div className="text-xs text-gray-500">
                {d.status === 'ready' && `${d.page_count} pages · ${d.chunk_count} chunks`}
                {d.status === 'processing' && 'processing...'}
                {d.status === 'failed' && <span className="text-red-500">failed: {d.error}</span>}
              </div>
            </div>
            <button
              onClick={async () => { await deleteDocument(d.id); refresh(); }}
              className="text-xs text-red-500 hover:underline"
            >delete</button>
          </div>
        ))}
      </aside>

      <main className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-gray-400 text-center mt-20">
              Upload PDF, select documents, then ask questions below
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={m.role === 'user' ? 'text-right' : ''}>
              <div className={`inline-block max-w-3xl px-4 py-2 rounded-lg whitespace-pre-wrap ${
                m.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-100'
              }`}>
                {m.content}
                {m.citations && m.citations.length > 0 && (
                  <details className="mt-2 text-xs text-gray-600">
                    <summary className="cursor-pointer">citations ({m.citations.length})</summary>
                    {m.citations.map((c, j) => (
                      <div key={j} className="mt-1 border-l-2 pl-2">
                        <b>{c.filename} · page {c.page_number}</b>
                        <div className="text-gray-500">{c.snippet}...</div>
                      </div>
                    ))}
                  </details>
                )}
              </div>
            </div>
          ))}
          {loading && <div className="text-gray-400">thinking...</div>}
        </div>

        <div className="border-t p-4 flex gap-2">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleAsk()}
            placeholder={selected.size === 0 ? 'please select documents' : 'input question...'}
            disabled={selected.size === 0 || loading}
            className="flex-1 border rounded px-3 py-2"
          />
          <button
            onClick={handleAsk}
            disabled={selected.size === 0 || loading || !input.trim()}
            className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
          >send</button>
        </div>
      </main>
    </div>
  );
}