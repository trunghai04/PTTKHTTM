import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

export default function GoogleAuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get('token');
    const next = searchParams.get('next') || '/dashboard';
    if (token) {
      localStorage.setItem('access_token', token);
      fetchUserAndRedirect(token, next, navigate);
    } else {
      navigate('/login?error=missing_token', { replace: true });
    }
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <p className="text-slate-600 font-medium">Đang đăng nhập...</p>
    </div>
  );
}

async function fetchUserAndRedirect(token, next, navigate) {
  try {
    const baseURL = import.meta.env.VITE_API_URL || '';
    const res = await fetch(`${baseURL}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      const user = await res.json();
      localStorage.setItem('user', JSON.stringify(user));
    }
  } catch (_) {}
  navigate(next, { replace: true });
}
