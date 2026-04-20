import { useState } from 'react';
import { login, register } from './api';
import { setAuth } from './auth';

export default function Login({ onDone }: { onDone: () => void }) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [username, setU] = useState('');
  const [password, setP] = useState('');
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setErr(null); setLoading(true);
    try {
      const fn = mode === 'login' ? login : register;
      const { token, username: u } = await fn(username, password);
      setAuth(token, u);
      onDone();
    } catch (e: any) {
      setErr(e.message);
    } finally { setLoading(false); }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-zinc-100 text-zinc-900 px-4">
      <div className="w-full max-w-sm bg-white border border-zinc-200 rounded-2xl shadow-sm p-7">
        <div className="mb-6">
          <p className="text-[11px] uppercase tracking-[0.16em] text-zinc-400">PDF Assistant</p>
          <h2 className="text-2xl font-semibold mt-1">
            {mode === 'login' ? 'Welcome back' : 'Create account'}
          </h2>
          <p className="text-sm text-zinc-500 mt-1">
            {mode === 'login'
              ? 'Sign in to continue your conversations.'
              : 'Register to save documents and chat history.'}
          </p>
        </div>
        <input
          placeholder="Username"
          value={username}
          onChange={e => setU(e.target.value)}
          className="w-full rounded-xl border border-zinc-300 bg-zinc-50 px-3.5 py-2.5 text-sm
          outline-none focus:ring-2 focus:ring-[#4052D6]/30 focus:border-[#4052D6] mb-2.5"
        />
        <input
          type="password"
          placeholder="Password (6-72 characters)"
          value={password}
          maxLength={72}
          onChange={e => setP(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && submit()}
          className="w-full rounded-xl border border-zinc-300 bg-zinc-50 px-3.5 py-2.5 text-sm
          outline-none focus:ring-2 focus:ring-[#4052D6]/30 focus:border-[#4052D6] mb-3"
        />
        {err && <div className="text-xs text-red-500 mb-3">{err}</div>}
        <button
          onClick={submit}
          disabled={loading || !username || password.length < 6 || password.length > 72}
          className="w-full h-10 rounded-xl bg-[#4052D6] hover:bg-[#3446C6] text-white text-sm font-medium
          disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Please wait...' : (mode === 'login' ? 'Log in' : 'Sign up')}
        </button>
        <div className="text-center text-sm text-zinc-500 mt-4">
          {mode === 'login' ? 'No account?' : 'Already have an account?'}
          <button
            onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setErr(null); }}
            className="text-[#4052D6] ml-1 hover:text-[#3446C6]"
          >
            {mode === 'login' ? 'Create one' : 'Log in'}
          </button>
        </div>
      </div>
    </div>
  );
}