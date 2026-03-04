import { useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import api from '../api/client';

export default function Login() {
  const [mode, setMode] = useState('login'); // login | register
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const navigate = useNavigate();
  const location = useLocation();

  const nextPath = useMemo(() => {
    const params = new URLSearchParams(location.search);
    return params.get('next') || '/dashboard';
  }, [location.search]);

  const queryError = useMemo(() => {
    const params = new URLSearchParams(location.search);
    const e = params.get('error');
    if (e === 'access_denied') return 'Bạn đã hủy đăng nhập Google.';
    if (e === 'missing_code' || e === 'token_exchange') return 'Đăng nhập Google không thành công. Thử lại.';
    if (e === 'server_config') return 'Máy chủ chưa cấu hình Google.';
    if (e === 'no_email') return 'Không lấy được email từ Google.';
    return null;
  }, [location.search]);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const url = mode === 'register' ? '/api/auth/register' : '/api/auth/login';
      const payload =
        mode === 'register'
          ? { email, password, name: name.trim() || null }
          : { email, password };

      const res = await api.post(url, payload);
      localStorage.setItem('access_token', res.data.access_token);
      localStorage.setItem('user', JSON.stringify(res.data.user));
      navigate(nextPath, { replace: true });
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || 'Đăng nhập thất bại');
    } finally {
      setLoading(false);
    }
  };

  const loginWithGoogle = async () => {
    setError(null);
    setLoading(true);
    try {
      const res = await api.get('/api/auth/google/login');
      if (res.data?.url) window.location.href = res.data.url;
      else setError('Không lấy được link đăng nhập Google');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Đăng nhập Google thất bại');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="mesh-bg" />

      <div className="max-w-md mx-auto px-6 py-16">
        <div className="bg-white/80 backdrop-blur-xl border border-slate-200 rounded-[2rem] shadow-xl p-8">
          <div className="flex items-center gap-2 mb-8">
            <button
              onClick={() => setMode('login')}
              className={`px-4 py-2 rounded-full text-sm font-bold ${
                mode === 'login' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-700'
              }`}
              type="button"
            >
              Đăng nhập
            </button>
            <button
              onClick={() => setMode('register')}
              className={`px-4 py-2 rounded-full text-sm font-bold ${
                mode === 'register' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-700'
              }`}
              type="button"
            >
              Đăng ký
            </button>
          </div>

          <h1 className="text-2xl font-extrabold text-slate-900 mb-2">
            {mode === 'register' ? 'Tạo tài khoản' : 'Chào mừng quay lại'}
          </h1>
          <p className="text-sm text-slate-500 mb-8">
            {mode === 'register'
              ? 'Tạo tài khoản để dùng các tính năng nâng cao.'
              : 'Đăng nhập để truy cập Dashboard và các chức năng quản trị.'}
          </p>

          {(error || queryError) && (
            <p className="text-sm font-semibold text-rose-600 mb-4">{error || queryError}</p>
          )}

          <form onSubmit={submit} className="space-y-4">
            {mode === 'register' && (
              <div>
                <label className="text-xs font-bold text-slate-600 uppercase tracking-wider">
                  Tên hiển thị
                </label>
                <input
                  className="mt-2 w-full px-4 py-3 rounded-2xl border border-slate-200 bg-white focus:outline-none focus:ring-4 focus:ring-slate-900/5"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Trung Hai"
                  autoComplete="name"
                />
              </div>
            )}

            <div>
              <label className="text-xs font-bold text-slate-600 uppercase tracking-wider">Email</label>
              <input
                className="mt-2 w-full px-4 py-3 rounded-2xl border border-slate-200 bg-white focus:outline-none focus:ring-4 focus:ring-slate-900/5"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                type="email"
                autoComplete="email"
                required
              />
            </div>

            <div>
              <label className="text-xs font-bold text-slate-600 uppercase tracking-wider">Mật khẩu</label>
              <input
                className="mt-2 w-full px-4 py-3 rounded-2xl border border-slate-200 bg-white focus:outline-none focus:ring-4 focus:ring-slate-900/5"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                type="password"
                autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
                required
              />
              {mode === 'register' && (
                <p className="mt-2 text-xs text-slate-400">Tối thiểu 6 ký tự.</p>
              )}
            </div>

            <button
              disabled={loading}
              className="w-full bg-slate-900 text-white py-3 rounded-2xl font-black hover:bg-slate-800 transition disabled:opacity-60"
              type="submit"
            >
              {loading ? 'Đang xử lý...' : mode === 'register' ? 'Đăng ký' : 'Đăng nhập'}
            </button>

            <div className="relative my-6">
              <span className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-slate-200" />
              </span>
              <span className="relative flex justify-center text-xs font-medium text-slate-500 uppercase">Hoặc</span>
            </div>
            <button
              type="button"
              disabled={loading}
              onClick={loginWithGoogle}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-2xl font-semibold border border-slate-200 bg-white hover:bg-slate-50 transition disabled:opacity-60"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Đăng nhập với Google
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

