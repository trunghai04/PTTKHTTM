import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import api from '../api/client';

export default function ScanHistory() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [error, setError] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/api/gmail/history?limit=100');
      setList(Array.isArray(res.data) ? res.data : []);
    } catch (e) {
      setError(e?.response?.data?.detail || 'Không tải được lịch sử');
      setList([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const runGmailScan = async () => {
    setScanning(true);
    setScanResult(null);
    setError(null);
    try {
      // Quét nhiều email hơn (ví dụ 200 gần nhất)
      const res = await api.post('/api/gmail/scan?max_messages=200');
      setScanResult(res.data);
      await fetchHistory();
    } catch (e) {
      setError(e?.response?.data?.detail || 'Quét Gmail thất bại');
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="max-w-4xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-extrabold text-slate-900 mb-2">Lịch sử quét</h1>
        <p className="text-slate-600 mb-8">
          Quét hộp thư Gmail và xem kết quả phân loại spam tại đây.
        </p>

        <div className="bg-white/80 backdrop-blur border border-slate-200 rounded-2xl p-6 shadow-sm mb-8">
          <h2 className="text-lg font-bold text-slate-800 mb-2">Quét Gmail</h2>
          <p className="text-sm text-slate-500 mb-4">
            Đăng nhập bằng Google trước, sau đó nhấn nút bên dưới để quét tối đa 200 email gần nhất.
          </p>
          <button
            type="button"
            disabled={scanning}
            onClick={runGmailScan}
            className="px-6 py-3 rounded-xl font-semibold bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-60 transition"
          >
            {scanning ? 'Đang quét...' : 'Quét Gmail'}
          </button>
          {scanResult && (
            <p className="mt-4 text-sm text-slate-600">
              Đã quét: <strong>{scanResult.scanned}</strong> — Spam: <strong>{scanResult.spam_count}</strong>, Không spam: <strong>{scanResult.not_spam_count}</strong>
            </p>
          )}
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-sm">
            {error}
          </div>
        )}

        <div className="bg-white/80 backdrop-blur border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-200 flex justify-between items-center">
            <h2 className="text-lg font-bold text-slate-800">Kết quả quét Gmail</h2>
            <button
              type="button"
              onClick={fetchHistory}
              disabled={loading}
              className="text-sm font-medium text-slate-600 hover:text-slate-900 disabled:opacity-60"
            >
              Làm mới
            </button>
          </div>
          <div className="divide-y divide-slate-100 max-h-[60vh] overflow-y-auto">
            {loading ? (
              <div className="p-8 text-center text-slate-500">Đang tải...</div>
            ) : list.length === 0 ? (
              <div className="p-8 text-center text-slate-500">Chưa có lịch sử quét Gmail.</div>
            ) : (
              list.map((item) => (
                <div key={item.id} className="p-4 hover:bg-slate-50/80">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      {item.email_subject && (
                        <p className="font-semibold text-slate-800 truncate">{item.email_subject}</p>
                      )}
                      {item.email_snippet && (
                        <p className="text-sm text-slate-600 mt-1 line-clamp-2">{item.email_snippet}</p>
                      )}
                      {!item.email_subject && !item.email_snippet && (
                        <p className="text-sm text-slate-600 line-clamp-2">{item.text?.slice(0, 200)}</p>
                      )}
                      <p className="text-xs text-slate-400 mt-1">
                        {item.created_at ? new Date(item.created_at).toLocaleString('vi-VN') : ''}
                      </p>
                    </div>
                    <span
                      className={`shrink-0 px-2 py-1 rounded-lg text-xs font-semibold ${
                        (item.predicted_label || '').toLowerCase() === 'spam'
                          ? 'bg-rose-100 text-rose-700'
                          : 'bg-emerald-100 text-emerald-700'
                      }`}
                    >
                      {item.predicted_label || '—'}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
