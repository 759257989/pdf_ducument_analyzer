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
    <div className="h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded shadow w-80">
        <h2 className="text-xl font-semibold mb-4">
          {mode === 'login' ? 'Login' : 'Register'}
        </h2>
        <input
          placeholder="Username" value={username}
          onChange={e => setU(e.target.value)}
          className="w-full border rounded px-3 py-2 mb-2"
        />
        <input
          type="password" placeholder="Password (6-72 characters)" value={password}
          maxLength={72}
          onChange={e => setP(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && submit()}
          className="w-full border rounded px-3 py-2 mb-3"
        />
        {err && <div className="text-xs text-red-500 mb-2">{err}</div>}
        <button
          onClick={submit} disabled={loading || !username || password.length < 6 || password.length > 72}
          className="w-full bg-blue-500 text-white py-2 rounded disabled:opacity-50"
        >{loading ? '...' : (mode === 'login' ? 'Login' : 'Register')}</button>
        <div className="text-center text-sm text-gray-500 mt-3">
          {mode === 'login' ? 'No account?': 'Already have an account?'}
          <button
            onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setErr(null); }}
            className="text-blue-500 ml-1 hover:underline"
          >{mode === 'login' ? 'Register' : 'Login'}</button>
        </div>
      </div>
    </div>
  );
}