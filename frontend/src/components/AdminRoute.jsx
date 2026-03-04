import { Navigate, useLocation } from 'react-router-dom';

export default function AdminRoute({ children }) {
  const token = localStorage.getItem('access_token');
  const location = useLocation();

  if (!token) {
    const next = encodeURIComponent(location.pathname + location.search);
    return <Navigate to={`/login?next=${next}`} replace />;
  }

  let user = null;
  try {
    const raw = localStorage.getItem('user');
    if (raw) {
      user = JSON.parse(raw);
    }
  } catch {
    user = null;
  }

  if (!user || !user.role || user.role.toLowerCase() !== 'admin') {
    return <Navigate to="/" replace />;
  }

  return children;
}

