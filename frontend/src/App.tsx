import { useEffect, useState } from 'react';
import {
  listDocuments, upload, deleteDocument, chat,
  listConversations, getConversation, deleteConversation,
  type Document, type Citation, type Conversation,
} from './api';
import Login from './Login';
import { clearAuth, getToken, getUsername } from './auth';

type Msg = { role: 'user' | 'assistant'; content: string; citations?: Citation[] };

export default function App() {
  const [authed, setAuthed] = useState(!!getToken());
  const [docs, setDocs] = useState<Document[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConvId, setCurrentConvId] = useState<string | null>(null);

  const refresh = async () => setDocs(await listDocuments());
  const refreshConversations = async () => {
    setConversations(await listConversations());
  };
  const [uploadError, setUploadError] = useState<string | null>(null);

  useEffect(() => {
    if (!authed) return;
    refresh();
    refreshConversations();
  }, [authed]);

  // when there are processing documents, poll every 2 seconds
  useEffect(() => {
    if (docs.some(d => d.status === 'processing')) {
      const t = setInterval(refresh, 2000);
      return () => clearInterval(t);
    }
  }, [docs]);

  const openConversation = async (id: string) => {
    const conv = await getConversation(id);
    setMessages(conv.messages.map(m => ({
      role: m.role,
      content: m.content,
      citations: m.citations,
    })));
    setCurrentConvId(id);
  };

  const newConversation = () => {
    setMessages([]);
    setCurrentConvId(null);
  };

  const removeConversation = async (id: string) => {
    await deleteConversation(id);
    if (id === currentConvId) newConversation();
    refreshConversations();
  };

  const handleUpload = async (f: File) => {
    setUploadError(null);
    try {
      await upload(f);
      refresh();
    } catch (e: any) {
      setUploadError(e.message);
    }
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
        currentConvId,
      );
      setCurrentConvId(resp.conversation_id);
      setMessages([...next, { role: 'assistant', content: resp.answer, citations: resp.citations }]);
      refreshConversations();
    } catch (e: any) {
      setMessages([...next, { role: 'assistant', content: `Error: ${e.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  if (!authed) {
    return <Login onDone={() => setAuthed(true)} />;
  }

  return (
    <div className="h-screen flex bg-zinc-100 text-zinc-900">
      <aside className="w-80 border-r border-zinc-800/70 bg-zinc-900 text-zinc-100 flex flex-col">
        <div className="p-4 flex items-center justify-between border-b border-zinc-800/80">
          <div className="min-w-0">
            <p className="text-[11px] uppercase tracking-wider text-zinc-400">Workspace</p>
            <p className="text-sm font-medium truncate">{getUsername()}</p>
          </div>
          <button
            onClick={() => { clearAuth(); setAuthed(false); }}
            className="text-xs text-zinc-400 hover:text-red-400 transition-colors"
          >Log out</button>
        </div>
        <div className="p-4 border-b border-zinc-800/80">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-3">Documents</h2>
          <input
            type="file"
            accept="application/pdf"
            onChange={e => e.target.files?.[0] && handleUpload(e.target.files[0])}
            className="mb-3 block w-full text-xs text-zinc-300
            file:mr-2 file:rounded-md file:border-0
            file:bg-zinc-700 file:px-2 file:py-1.5 file:text-xs file:font-medium file:text-zinc-100
            hover:file:bg-zinc-600"
          />
          {uploadError && <div className="text-xs text-red-300 mb-3">{uploadError}</div>}
          {docs.length === 0 && <p className="text-xs text-zinc-500">No PDF uploaded yet</p>}
          {docs.map(d => (
            <div key={d.id} className="mb-2 rounded-lg border border-zinc-800 bg-zinc-800/40 p-2.5 flex items-start gap-2">
              <input
                type="checkbox"
                disabled={d.status !== 'ready'}
                checked={selected.has(d.id)}
                onChange={e => {
                  const s = new Set(selected);
                  e.target.checked ? s.add(d.id) : s.delete(d.id);
                  setSelected(s);
                }}
                className="mt-1 accent-[#4052D6]"
              />
              <div className="flex-1 text-sm min-w-0">
                <div className="truncate text-sm text-zinc-100" title={d.filename}>{d.filename}</div>
                <div className="text-xs text-zinc-400 mt-0.5">
                  {d.status === 'ready' && `${d.page_count} pages · ${d.chunk_count} chunks`}
                  {d.status === 'processing' && 'processing...'}
                  {d.status === 'failed' && <span className="text-red-300">failed: {d.error}</span>}
                </div>
              </div>
              <button
                onClick={async () => { await deleteDocument(d.id); refresh(); }}
                className="text-xs text-zinc-400 hover:text-red-400 transition-colors"
              >delete</button>
            </div>
          ))}
        </div>
        <div className="p-4 flex-1">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">Conversations</h2>
            <button
              onClick={newConversation}
              className="text-xs bg-zinc-700 hover:bg-zinc-600 text-zinc-100 px-2.5 py-1.5 rounded-md transition-colors"
            >
              + New
            </button>
          </div>
          {conversations.length === 0 && (
            <p className="text-xs text-zinc-500">No conversations yet</p>
          )}
          {conversations.map(c => (
            <div
              key={c.id}
              className={`group px-2.5 py-2 rounded-md cursor-pointer flex items-center border text-sm ${
                c.id === currentConvId
                  ? 'bg-zinc-800 border-zinc-700 text-zinc-100'
                  : 'border-transparent hover:bg-zinc-800/70 text-zinc-300'
              }`}
              onClick={() => openConversation(c.id)}
            >
              <span className="flex-1 text-sm truncate">{c.title}</span>
              <button
                onClick={e => { e.stopPropagation(); removeConversation(c.id); }}
                className="opacity-0 group-hover:opacity-100 text-xs text-zinc-400 hover:text-red-400 ml-2 transition"
              >Delete</button>
            </div>
          ))}
        </div>
      </aside>

      <main className="flex-1 flex flex-col bg-zinc-50">
        <div className="border-b border-zinc-200/80 px-6 py-3 bg-white/70 backdrop-blur-sm">
          <p className="text-sm text-zinc-600">
            {selected.size > 0 ? `${selected.size} document(s) selected` : 'Select documents to start chatting'}
          </p>
        </div>
        <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6">
          <div className="mx-auto w-full max-w-3xl space-y-6">
          {messages.length === 0 && (
            <div className="text-zinc-400 text-center mt-20">
              Ask a question about your selected documents
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] px-4 py-3 rounded-2xl whitespace-pre-wrap shadow-sm ${
                m.role === 'user'
                  ? 'bg-[#4052D6] text-white rounded-br-md'
                  : 'bg-white text-zinc-800 border border-zinc-200 rounded-bl-md'
                }`}>
                {m.content}
                {m.citations && m.citations.length > 0 && (
                  <details className={`mt-3 text-xs ${m.role === 'user' ? 'text-[#E2E5FF]' : 'text-zinc-500'}`}>
                    <summary className="cursor-pointer">citations ({m.citations.length})</summary>
                    {m.citations.map((c, j) => (
                      <div key={j} className={`mt-1.5 border-l-2 pl-2 ${m.role === 'user' ? 'border-[#B3BBFF]' : 'border-zinc-300'}`}>
                        <b>{c.filename} · page {c.page_number}</b>
                        <div className={m.role === 'user' ? 'text-[#E2E5FF]' : 'text-zinc-500'}>{c.snippet}...</div>
                      </div>
                    ))}
                  </details>
                )}
              </div>
            </div>
          ))}
          {loading && <div className="text-zinc-400 text-sm">Thinking...</div>}
          </div>
        </div>

        <div className="border-t border-zinc-200 bg-white px-4 py-4">
          <div className="mx-auto max-w-3xl flex gap-2 items-end">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleAsk()}
              placeholder={selected.size === 0 ? 'Please select documents first' : 'Message your documents...'}
              disabled={selected.size === 0 || loading}
              className="flex-1 rounded-2xl border border-zinc-300 bg-zinc-50 px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-[#4052D6]/30 focus:border-[#4052D6]"
            />
            <button
              onClick={handleAsk}
              disabled={selected.size === 0 || loading || !input.trim()}
              className="h-11 px-4 rounded-xl bg-[#4052D6] text-white text-sm font-medium hover:bg-[#3446C6] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}