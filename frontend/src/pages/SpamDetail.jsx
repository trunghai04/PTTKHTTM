import { useLocation, useNavigate } from 'react-router-dom';
import { Shield, Zap, CheckCircle2, ArrowLeft } from 'lucide-react';
import Navbar from '../components/Navbar';

export default function SpamDetail() {
  const location = useLocation();
  const navigate = useNavigate();
  const entry = location.state?.entry;

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800">
      <Navbar />

      <main className="max-w-3xl mx-auto px-6 py-10">
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-slate-900 mb-6"
        >
          <ArrowLeft size={16} />
          Quay lại
        </button>

        {!entry ? (
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <h1 className="text-xl font-extrabold text-slate-900 mb-2">Không tìm thấy bản ghi</h1>
            <p className="text-sm text-slate-600">
              Vui lòng mở lại từ trang <strong>Spam Email</strong> và chọn “Xem chi tiết” trên một bản ghi trong lịch sử.
            </p>
          </div>
        ) : (
          <div className="bg-white/80 backdrop-blur border border-slate-200 rounded-[2rem] p-8 shadow-xl">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-slate-100 flex items-center justify-center">
                  <Shield className="text-red-500" size={22} />
                </div>
                <div>
                  <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                    Chi tiết phân loại Spam
                  </h1>
                  <p className="text-xs text-slate-500">
                    {entry.created_at
                      ? new Date(entry.created_at).toLocaleString('vi-VN')
                      : '—'}
                  </p>
                </div>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                  entry.type === 'SPAM'
                    ? 'bg-rose-100 text-rose-700'
                    : 'bg-emerald-100 text-emerald-700'
                }`}
              >
                {entry.type === 'SPAM' ? 'Spam' : 'Không spam'}
              </span>
            </div>

            <div className="mb-6">
              <h2 className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] mb-2">
                Nội dung đã phân tích
              </h2>
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-sm leading-relaxed max-h-[300px] overflow-y-auto whitespace-pre-wrap">
                {entry.text}
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-slate-900 text-white flex items-center justify-center">
                  <Zap size={18} />
                </div>
                <div>
                  <p className="text-[11px] font-black text-slate-500 uppercase tracking-[0.18em]">
                    Độ tin cậy
                  </p>
                  <p className="text-xl font-extrabold text-slate-900">
                    {entry.confidence != null ? `${entry.confidence}%` : '—'}
                  </p>
                </div>
              </div>
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
                  <CheckCircle2 size={18} />
                </div>
                <div>
                  <p className="text-[11px] font-black text-slate-500 uppercase tracking-[0.18em]">
                    Nguồn dữ liệu
                  </p>
                  <p className="text-sm font-semibold text-slate-800">
                    Email thủ công / Gmail (tùy theo nơi gửi)
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

