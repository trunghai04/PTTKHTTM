import { Menu, X } from 'lucide-react';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [isAvatarMenuOpen, setIsAvatarMenuOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    try {
      const raw = localStorage.getItem('user');
      if (raw) {
        const parsed = JSON.parse(raw);
        setCurrentUser(parsed);
      }
    } catch {
      // ignore parse errors
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setCurrentUser(null);
    setIsAvatarMenuOpen(false);
    setIsOpen(false);
    navigate('/');
  };

  const isAdmin =
    !!currentUser?.role &&
    currentUser.role.toLowerCase() === 'admin';

  return (
    <nav className="sticky top-0 z-50 px-6 py-4 bg-white/80 backdrop-blur-xl border-b border-slate-200">
      <div className="max-w-[1440px] mx-auto flex justify-between items-center">
        <Link to="/" className="flex items-center gap-2">
          <img
            src="/logo_rounded.png"
            alt="BloopAI logo"
            className="w-8 h-8 rounded-full object-cover"
          />
          <span className="text-xl font-bold tracking-tight text-text-charcoal">
            Bloop<span className="text-accent-purple">AI</span>
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-8 text-base font-semibold text-slate-600">
          <Link to="/spam" className="hover:text-accent-blue transition-colors">
            Spam Email
          </Link>
          <Link to="/news" className="hover:text-accent-blue transition-colors">
            Tin tức
          </Link>
          <Link to="/docs" className="hover:text-accent-blue transition-colors">
            Tài liệu
          </Link>
          {isAdmin && (
            <Link to="/dashboard" className="hover:text-accent-blue transition-colors">
              Bảng điều khiển
            </Link>
          )}
          <Link to="/scan-history" className="hover:text-accent-blue transition-colors">
            Lịch sử quét
          </Link>
        </div>

        <div className="flex items-center gap-4">
          {currentUser ? (
            <div className="relative hidden md:block">
              <button
                type="button"
                className="flex items-center gap-2"
                onClick={() => setIsAvatarMenuOpen((prev) => !prev)}
              >
                <div className="w-9 h-9 rounded-full overflow-hidden border border-slate-200 bg-slate-100 flex items-center justify-center">
                  {currentUser.avatar_url ? (
                    <img
                      src={currentUser.avatar_url}
                      alt={currentUser.name || currentUser.email}
                      className="w-full h-full object-cover"
                      referrerPolicy="no-referrer"
                    />
                  ) : (
                    <span className="text-xs font-bold text-slate-700">
                      {(currentUser.name || currentUser.email || '?')
                        .charAt(0)
                        .toUpperCase()}
                    </span>
                  )}
                </div>
              </button>
              {isAvatarMenuOpen && (
                <div className="absolute right-0 mt-2 w-40 bg-white border border-slate-200 rounded-xl shadow-lg py-2 z-50">
                  {isAdmin && (
                    <button
                      type="button"
                      onClick={() => {
                        setIsAvatarMenuOpen(false);
                        navigate('/dashboard');
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
                    >
                      Bảng điều khiển
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    Đăng xuất
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link
              to="/login"
              className="hidden md:block bg-text-charcoal text-white px-6 py-2.5 rounded-full font-semibold text-sm hover:bg-accent-blue transition-all shadow-lg shadow-blue-100"
            >
              Bắt đầu ngay
            </Link>
          )}
          <button className="md:hidden" onClick={() => setIsOpen(!isOpen)}>
            {isOpen ? <X /> : <Menu />}
          </button>
        </div>
      </div>

      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden absolute top-full left-0 w-full bg-white border-b border-slate-200 p-6 flex flex-col gap-4 shadow-xl"
        >
          <Link to="/spam" className="font-semibold text-slate-600">
            Giải pháp
          </Link>
          <Link to="/news" className="font-semibold text-slate-600">
            Công nghệ
          </Link>
          <Link to="/docs" className="font-semibold text-slate-600">
            Tài liệu
          </Link>
          {isAdmin && (
            <Link to="/dashboard" className="font-semibold text-slate-600">
              Bảng điều khiển
            </Link>
          )}
          <Link to="/scan-history" className="font-semibold text-slate-600">
            Lịch sử quét
          </Link>
          {currentUser && isAdmin ? (
            <Link
              to="/dashboard"
              className="bg-text-charcoal text-white px-6 py-3 rounded-xl font-semibold text-center flex items-center justify-center gap-2"
            >
              <div className="w-8 h-8 rounded-full overflow-hidden border border-slate-200 bg-slate-100 flex items-center justify-center">
                {currentUser.avatar_url ? (
                  <img
                    src={currentUser.avatar_url}
                    alt={currentUser.name || currentUser.email}
                    className="w-full h-full object-cover"
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <span className="text-xs font-bold text-slate-700">
                    {(currentUser.name || currentUser.email || '?')
                      .charAt(0)
                      .toUpperCase()}
                  </span>
                )}
              </div>
              <span>Bảng điều khiển</span>
            </Link>
          ) : !currentUser ? (
            <Link
              to="/login"
              className="bg-text-charcoal text-white px-6 py-3 rounded-xl font-semibold text-center"
            >
              Bắt đầu ngay
            </Link>
          ) : null}
        </motion.div>
      )}
    </nav>
  );
};

export default Navbar;

