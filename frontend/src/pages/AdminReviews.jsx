import { useEffect, useMemo, useState } from 'react';
import { CheckCircle2, XCircle, RefreshCw, ShieldAlert, ArrowLeft, Filter, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import Navbar from '../components/Navbar';
import api from '../api/client';

const badgeClass = (type, variant = 'neutral') => {
  if (type === 'spam') return variant === 'soft' ? 'bg-rose-50 text-rose-700 border-rose-100' : 'bg-rose-600 text-white';
  if (type === 'news') return variant === 'soft' ? 'bg-indigo-50 text-indigo-700 border-indigo-100' : 'bg-indigo-600 text-white';
  return variant === 'soft' ? 'bg-slate-100 text-slate-600 border-slate-200' : 'bg-slate-900 text-white';
};

const statusMeta = {
  pending: { label: 'Chờ duyệt', className: 'bg-amber-50 text-amber-700 border-amber-100' },
  approved: { label: 'Đã duyệt', className: 'bg-emerald-50 text-emerald-700 border-emerald-100' },
  rejected: { label: 'Từ chối', className: 'bg-rose-50 text-rose-700 border-rose-100' },
};

export default function AdminReviews() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionId, setActionId] = useState(null);
  const [filter, setFilter] = useState('pending');

  const load = async (status = filter) => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get('/api/stats/reviews', { params: { status } });
      setItems(res.data || []);
    } catch (e) {
      setError(e?.response?.data?.detail || 'Không tải được danh sách');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [filter]);

  const review = async (id, approve) => {
    try {
      setActionId(id);
      await api.post(`/api/stats/predictions/${id}/review`, {
        approve,
        reviewed_label: approve ? undefined : null,
      });
      await load();
    } catch (e) {
      setError(e?.response?.data?.detail || 'Không thể duyệt bản ghi');
    } finally {
      setActionId(null);
    }
  };

  const filteredItems = useMemo(() => items, [items]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <Navbar />
      <div className="max-w-7xl mx-auto px-6 py-10 space-y-6">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <Link to="/dashboard" className="inline-flex items-center gap-2 px-3 py-2 rounded-2xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-50">
              <ArrowLeft size={16} /> Bảng điều khiển
            </Link>
            <div>
              <p className="text-xs font-black tracking-[0.2em] uppercase text-slate-400">Admin</p>
              <h1 className="text-3xl font-extrabold">Duyệt dự đoán AI</h1>
            </div>
          </div>
          <button onClick={load} className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-900 text-white font-bold">
            <RefreshCw size={16} /> Làm mới
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-4 rounded-3xl bg-white border border-slate-200 shadow-sm">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-black uppercase tracking-[0.16em]"><Filter size={14} /> Bộ lọc</div>
            <div className="mt-3 flex flex-wrap gap-2">
              {['pending', 'approved', 'rejected', 'all'].map((key) => (
                <button
                  key={key}
                  onClick={() => {
                    setFilter(key);
                    load(key);
                  }}
                  className={`px-3 py-1.5 rounded-full text-xs font-bold border transition-colors ${filter === key ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'}`}
                >
                  {key === 'pending' ? 'Chờ duyệt' : key === 'approved' ? 'Đã duyệt' : key === 'rejected' ? 'Từ chối' : 'Tất cả'}
                </button>
              ))}
            </div>
          </div>
          <div className="p-4 rounded-3xl bg-white border border-slate-200 shadow-sm">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-black uppercase tracking-[0.16em]"><Sparkles size={14} /> Tổng bản ghi</div>
            <div className="mt-3 text-3xl font-extrabold">{items.length}</div>
          </div>
          <div className="p-4 rounded-3xl bg-white border border-slate-200 shadow-sm">
            <div className="flex items-center gap-2 text-slate-500 text-xs font-black uppercase tracking-[0.16em]"><ShieldAlert size={14} /> Trạng thái</div>
            <div className="mt-3 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-50 text-amber-700 text-sm font-bold border border-amber-100">
              Chỉ admin mới được duyệt
            </div>
          </div>
        </div>

        {error && <div className="p-4 rounded-2xl bg-rose-50 text-rose-700 font-semibold">{error}</div>}

        <div className="grid gap-4">
          {loading ? (
            <div className="p-8 rounded-3xl bg-white border border-slate-200">Đang tải...</div>
          ) : filteredItems.length === 0 ? (
            <div className="p-8 rounded-3xl bg-white border border-slate-200 flex items-center gap-3 text-slate-500">
              <ShieldAlert /> Chưa có bản ghi phù hợp bộ lọc.
            </div>
          ) : filteredItems.map((item) => {
            const meta = statusMeta[item.review_status || 'pending'] || statusMeta.pending;
            return (
              <motion.div key={item.id} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="p-5 rounded-3xl bg-white border border-slate-200 shadow-sm">
                <div className="flex items-start justify-between gap-4 flex-col lg:flex-row">
                  <div className="space-y-3 w-full">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-black uppercase border ${badgeClass(item.type, 'soft')}`}>{item.type}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-black uppercase border ${meta.className}`}>{meta.label}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-black uppercase border ${badgeClass(item.predicted_label?.toLowerCase?.() === 'spam' ? 'spam' : 'news', 'soft')}`}>{item.predicted_label}</span>
                      <span className="text-xs text-slate-400">Confidence {Math.round((item.confidence || 0) * 100)}%</span>
                    </div>
                    <p className="text-sm leading-6 text-slate-700 whitespace-pre-wrap bg-slate-50 border border-slate-100 rounded-2xl p-4">{item.text}</p>
                    <div className="text-xs text-slate-400 flex flex-wrap gap-3">
                      <span>ID #{item.id}</span>
                      <span>{item.created_at ? new Date(item.created_at).toLocaleString('vi-VN') : '—'}</span>
                      <span>Nguồn: {item.source || 'manual'}</span>
                    </div>
                  </div>
                  <div className="flex gap-2 shrink-0 flex-wrap lg:flex-col xl:flex-row">
                    <button disabled={actionId === item.id} onClick={() => review(item.id, true)} className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl bg-emerald-600 text-white font-bold disabled:opacity-60">
                      <CheckCircle2 size={16} /> Duyệt
                    </button>
                    <button disabled={actionId === item.id} onClick={() => review(item.id, false)} className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl bg-rose-600 text-white font-bold disabled:opacity-60">
                      <XCircle size={16} /> Từ chối
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
