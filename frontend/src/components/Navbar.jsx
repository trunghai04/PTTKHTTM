import { Sparkles, Menu, X } from 'lucide-react';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 px-6 py-4 bg-white/80 backdrop-blur-xl border-b border-slate-200">
      <div className="max-w-[1440px] mx-auto flex justify-between items-center">
        <Link to="/" className="flex items-center gap-2">
          <Sparkles className="text-accent-blue w-8 h-8" />
          <span className="text-xl font-bold tracking-tight text-text-charcoal">
            LEXICA <span className="text-accent-purple">AI</span>
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-8 text-base font-semibold text-slate-600">
          <Link to="/spam" className="hover:text-accent-blue transition-colors">
            Spam Email
          </Link>
          <Link to="/news" className="hover:text-accent-blue transition-colors">
            Tin tức
          </Link>
          <Link to="/dashboard" className="hover:text-accent-blue transition-colors">
            Bảng điều khiển
          </Link>
          <Link to="/dashboard" className="hover:text-accent-blue transition-colors">
            Doanh nghiệp
          </Link>
        </div>

        <div className="flex items-center gap-4">
          <Link
            to="/spam"
            className="hidden md:block bg-text-charcoal text-white px-6 py-2.5 rounded-full font-semibold text-sm hover:bg-accent-blue transition-all shadow-lg shadow-blue-100"
          >
            Bắt đầu ngay
          </Link>
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
          <Link to="/dashboard" className="font-semibold text-slate-600">
            Bảng điều khiển
          </Link>
          <Link to="/dashboard" className="font-semibold text-slate-600">
            Doanh nghiệp
          </Link>
          <Link
            to="/spam"
            className="bg-text-charcoal text-white px-6 py-3 rounded-xl font-semibold text-center"
          >
            Bắt đầu ngay
          </Link>
        </motion.div>
      )}
    </nav>
  );
};

export default Navbar;

