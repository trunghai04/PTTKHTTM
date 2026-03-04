import { useLocation, useNavigate } from 'react-router-dom';
import { Newspaper, ArrowLeft, CheckCircle2 } from 'lucide-react';
import Navbar from '../components/Navbar';

export default function NewsDetail() {
  const location = useLocation();
  const navigate = useNavigate();
  const entry = location.state?.entry;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
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
              Vui lòng mở lại từ trang <strong>Tin tức</strong> và chọn “Chi tiết” trên một bản ghi
              trong lịch sử.
            </p>
          </div>
        ) : (
          <div className="bg-white/90 backdrop-blur border border-slate-200 rounded-[2rem] p-8 shadow-xl">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-blue-50 flex items-center justify-center">
                  <Newspaper className="text-blue-600" size={22} />
                </div>
                <div>
                  <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                    Chi tiết phân loại tin tức
                  </h1>
                  <p className="text-xs text-slate-500">
                    {entry.time || '—'}
                  </p>
                </div>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-slate-100 text-slate-700">
                {entry.topic || 'Chủ đề'}
              </span>
            </div>

            <div className="mb-6">
              <h2 className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] mb-2">
                Tóm tắt nội dung
              </h2>
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-sm leading-relaxed whitespace-pre-wrap">
                {entry.preview || 'Không có nội dung xem trước.'}
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center">
                  <CheckCircle2 size={18} />
                </div>
                <div>
                  <p className="text-[11px] font-black text-slate-500 uppercase tracking-[0.18em]">
                    Trạng thái bản ghi
                  </p>
                  <p className="text-sm font-semibold text-slate-900">
                    {entry.verified ? 'Đã lưu trong lịch sử' : 'Chỉ tồn tại trong phiên hiện tại'}
                  </p>
                </div>
              </div>
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-sm text-slate-600">
                <p className="text-[11px] font-black text-slate-500 uppercase tracking-[0.18em] mb-1">
                  Gợi ý giải thích
                </p>
                <p>
                  Chủ đề được suy ra dựa trên các cụm từ xuất hiện trong văn bản (TF‑IDF) và xác suất
                  Softmax từ mô hình Logistic Regression đa lớp.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

