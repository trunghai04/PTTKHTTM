import React, { useState, useEffect } from 'react';
import {
  Shield,
  Search,
  History,
  Zap,
  Paperclip,
  Trash2,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  Cpu,
  Terminal,
  BarChart3,
  Activity,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../api/client';
import Navbar from '../components/Navbar';

// --- Components ---

const Badge = ({ children, variant = 'default' }) => {
  const variants = {
    default: 'bg-slate-100 text-slate-600 border-slate-200',
    premium: 'bg-indigo-600 text-white shadow-lg shadow-indigo-200 uppercase tracking-widest text-[10px] font-black',
    danger: 'bg-red-100 text-red-600 text-[9px] font-black uppercase tracking-wider',
    success: 'bg-emerald-100 text-emerald-600 text-[9px] font-black uppercase tracking-wider',
  };
  
  return (
    <span className={`px-3 py-1 rounded-full border text-xs font-bold ${variants[variant]}`}>
      {children}
    </span>
  );
};

const Card = ({ children, className = "" }) => (
  <div className={`bg-white/70 backdrop-blur-xl border border-white/40 shadow-xl shadow-slate-200/50 rounded-[2.5rem] ${className}`}>
    {children}
  </div>
);

const HistoryItem = ({ type, title, time, confidence }) => (
  <motion.div 
    whileHover={{ y: -4, x: 2 }}
    className="group p-5 bg-slate-50/50 border border-slate-100 rounded-3xl cursor-pointer relative overflow-hidden transition-all hover:bg-white hover:border-indigo-200"
  >
    <div className="flex justify-between items-start mb-3">
      <Badge variant={type === 'SPAM' ? 'danger' : 'success'}>{type}</Badge>
      <span className="text-[10px] font-bold text-slate-400">{time}</span>
    </div>
    <p className="text-sm text-slate-600 line-clamp-2 font-semibold leading-relaxed mb-4">{title}</p>
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-400">
        {type === 'SPAM' ? <Zap size={12} /> : <CheckCircle2 size={12} />}
        {confidence} tin cậy
      </div>
      <div className="flex items-center gap-1 text-indigo-600 opacity-0 group-hover:opacity-100 transition-all transform translate-x-2 group-hover:translate-x-0">
        <span className="text-[10px] font-black uppercase tracking-tighter">Xem chi tiết</span>
        <ExternalLink size={14} />
      </div>
    </div>
  </motion.div>
);

// --- Main App ---

export default function App() {
  const [text, setText] = useState('');
  const [isBulkScan, setIsBulkScan] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [spamResult, setSpamResult] = useState(null);
  const [historyItems, setHistoryItems] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [error, setError] = useState(null);

  const characterCount = text.length;
  const estimatedRisk = text.length > 0 ? Math.min(Math.floor(text.length / 10), 98) : 0;

  const fetchHistory = async () => {
    try {
      setIsLoadingHistory(true);
      const res = await api.get('/api/spam/history', { params: { limit: 50 } });
      const mapped = (res.data || []).map((item) => {
        const isSpam = (String(item.predicted_label || '').toLowerCase() === 'spam');
        return {
          id: item.id,
          text: item.text,
          type: isSpam ? 'SPAM' : 'SAFE',
          confidence: Math.round((item.confidence || 0) * 100),
          created_at: item.created_at,
        };
      });
      setHistoryItems(mapped);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setIsAnalyzing(true);
    setError(null);
    try {
      if (isBulkScan) {
        const texts = text
          .split(/\r?\n/)
          .map((t) => t.trim())
          .filter(Boolean);

        const res = await api.post('/api/spam/predict/bulk', { texts });
        const results = res.data?.results || [];
        const total = res.data?.total || results.length || 0;
        const spamCount = res.data?.spam_count ?? results.filter((r) => String(r.label || '').toLowerCase() === 'spam').length;
        const notSpamCount = res.data?.not_spam_count ?? Math.max(0, total - spamCount);

        const avgConfidence =
          total > 0
            ? results.reduce((s, r) => s + (r.confidence || 0), 0) / total
            : 0;

        setSpamResult({
          label: spamCount >= notSpamCount ? 'spam' : 'not spam',
          confidence: avgConfidence,
          spam_probability: total > 0 ? spamCount / total : 0,
          not_spam_probability: total > 0 ? notSpamCount / total : 0,
          warning: total > 0 ? `Bulk scan: ${total} mẫu (Spam ${spamCount}, Hợp lệ ${notSpamCount}).` : null,
        });
      } else {
        const res = await api.post('/api/spam/predict', { text });
        setSpamResult(res.data);
      }
      await fetchHistory();
    } catch (e) {
      console.error(e);
      setError(e?.response?.data?.detail || 'Có lỗi khi gọi API kiểm tra spam');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleUploadTextFile = async (file) => {
    if (!file) return;
    const content = await file.text();
    setText(content || '');
  };

  const clearHistory = async () => {
    try {
      await api.delete('/api/spam/history');
      await fetchHistory();
    } catch (e) {
      console.error(e);
      setError(e?.response?.data?.detail || 'Không thể xóa lịch sử');
    }
  };

  const spamPercent = spamResult
    ? Math.round(
        (spamResult.spam_probability != null
          ? spamResult.spam_probability
          : String(spamResult.label || '').toLowerCase() === 'spam'
          ? spamResult.confidence
          : 1 - (spamResult.confidence || 0)
        ) * 100
      )
    : 0;
  const safePercent = spamResult ? Math.max(0, 100 - spamPercent) : 0;
  const confidencePercent = spamResult ? Math.round((spamResult.confidence || 0) * 100) : 0;

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 font-['Plus_Jakarta_Sans',sans-serif] selection:bg-indigo-100 selection:text-indigo-900">
      <Navbar />

      {/* Mesh Background Effect */}
      <div className="fixed inset-0 pointer-events-none opacity-40">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-200 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-200 rounded-full blur-[120px]" />
      </div>

      <main className="max-w-[1440px] mx-auto px-6 md:px-8 py-10">
        <div className="grid grid-cols-12 gap-6 lg:gap-10">
          
          {/* Left Column */}
          <div className="col-span-12 lg:col-span-8 space-y-8">
            
            {/* Email Analysis Section */}
            <Card className="overflow-hidden">
              <div className="p-6 md:p-10">
                <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                  <div>
                    <h2 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">Phân tích email</h2>
                    <p className="text-slate-500 font-medium text-sm mt-1">Kích hoạt bộ lọc thần kinh độ chính xác cao cho nội dung văn bản của bạn.</p>
                  </div>
                  <div className="flex flex-row md:flex-col items-center md:items-end gap-2">
                    <Badge variant="premium">AI cho doanh nghiệp</Badge>
                    <div className="flex items-center gap-2 px-3 py-1 bg-white/50 border border-slate-200 rounded-lg">
                      <span className="text-[10px] font-bold text-slate-600 uppercase">Quét hàng loạt</span>
                      <button
                        type="button"
                        onClick={() => setIsBulkScan(!isBulkScan)}
                        className={`relative inline-flex h-4 w-7 items-center rounded-full transition-colors focus:outline-none ${
                          isBulkScan ? 'bg-indigo-600' : 'bg-slate-300'
                        }`}
                        aria-pressed={isBulkScan}
                      >
                        <span
                          className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                            isBulkScan ? 'translate-x-3.5' : 'translate-x-0.5'
                          }`}
                        />
                      </button>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1 bg-white/50 border border-slate-200 rounded-lg">
                      <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                      <span className="text-[10px] font-bold text-slate-600">Mức độ rủi ro: <span className="text-emerald-600">Thấp</span></span>
                    </div>
                  </div>
                </div>

                {error && (
                  <p className="mb-4 text-sm font-semibold text-red-600">{error}</p>
                )}

                <div className="relative">
                  <textarea 
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    className="w-full h-64 md:h-80 p-6 md:p-8 bg-white/40 border-2 border-slate-200/50 rounded-3xl focus:ring-[12px] focus:ring-indigo-500/5 focus:border-indigo-500/30 outline-none transition-all resize-none text-slate-800 text-lg leading-relaxed placeholder:text-slate-400 placeholder:font-light" 
                    placeholder={isBulkScan ? "Mỗi dòng là 1 mẫu để quét hàng loạt..." : "Dán nội dung vào đây để phân tích chuyên sâu..."}
                  />
                  <div className="absolute bottom-6 left-6 md:left-8 flex flex-wrap gap-4">
                    <div className="px-3 py-1 bg-slate-900 text-white rounded-lg text-[11px] font-bold tracking-tight">
                      Số ký tự hiện tại: <span className="text-indigo-400">{characterCount.toLocaleString()}</span>
                    </div>
                    <div className="px-3 py-1 bg-white border border-slate-200 rounded-lg text-[11px] font-bold text-slate-600">
                      Ước tính rủi ro: <span className="text-indigo-600">{estimatedRisk}%</span>
                    </div>
                  </div>
                </div>

                <div className="mt-8 flex flex-col sm:flex-row items-center justify-between gap-6">
                  <div className="flex items-center gap-4">
                    <label className="p-3 bg-white text-slate-400 rounded-2xl hover:text-indigo-600 hover:shadow-xl transition-all border border-slate-100 shadow-sm cursor-pointer">
                      <Paperclip size={20} />
                      <input
                        type="file"
                        accept=".txt,text/plain"
                        className="hidden"
                        onChange={(e) => handleUploadTextFile(e.target.files?.[0])}
                      />
                    </label>
                    <button 
                      onClick={() => setText('')}
                      className="p-3 bg-white text-slate-400 rounded-2xl hover:text-red-500 hover:shadow-xl transition-all border border-slate-100 shadow-sm"
                    >
                      <Trash2 size={20} />
                    </button>
                  </div>
                  <button 
                    onClick={handleAnalyze}
                    disabled={isAnalyzing || !text.trim()}
                    className="w-full sm:w-auto bg-gradient-to-br from-indigo-600 to-purple-600 px-10 py-4 rounded-2xl text-white font-black flex items-center justify-center gap-3 shadow-2xl shadow-indigo-300 hover:scale-105 transition-transform active:scale-95 disabled:opacity-70"
                  >
                    <span className="text-lg">{isAnalyzing ? 'Đang phân tích...' : (isBulkScan ? 'Quét hàng loạt' : 'Kiểm tra spam')}</span>
                    <Zap size={20} className={isAnalyzing ? 'animate-pulse' : ''} />
                  </button>
                </div>
              </div>
            </Card>

            {/* Neural Scan Report */}
            <Card className="p-6 md:p-10 bg-white">
              <div className="flex flex-col md:flex-row items-start justify-between mb-10 gap-4">
                <div>
                  <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">Báo cáo quét thần kinh</h3>
                  <p className="text-sm font-medium text-slate-500">Phân bố xác suất từ mô hình backend</p>
                </div>
                <div className="flex items-center gap-4 bg-slate-50 p-3 rounded-2xl border border-slate-100">
                  <div className="flex gap-1 items-end h-6 px-2">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <motion.div 
                        key={i}
                        animate={{ height: [4, 24, 4] }}
                        transition={{ repeat: Infinity, duration: 1.2, delay: i * 0.1 }}
                        className="w-[3px] bg-indigo-600 rounded-full"
                      />
                    ))}
                  </div>
                  <span className="text-[10px] font-black text-indigo-600 uppercase tracking-widest">
                    {isAnalyzing ? 'Đang quét' : 'Sẵn sàng'}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                <div className="space-y-8">
                  <div>
                    <div className="flex justify-between items-end mb-3">
                      <span className="text-sm font-bold text-slate-600 uppercase tracking-wider">Độ tin cậy tổng thể</span>
                      <span className="text-4xl font-black text-slate-900">
                        {spamResult ? confidencePercent : '--'}
                        {spamResult && <span className="text-indigo-500 text-2xl">%</span>}
                      </span>
                    </div>
                    <div className="h-4 w-full bg-slate-100 rounded-full overflow-hidden p-1">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: spamResult ? `${confidencePercent}%` : '0%' }}
                        className="h-full bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full shadow-lg"
                      />
                    </div>
                  </div>
                  <div className="p-6 bg-red-50/50 rounded-3xl border border-red-100 flex gap-4">
                    <div className="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center text-red-600 flex-shrink-0">
                      <AlertTriangle size={20} />
                    </div>
                    <p className="text-sm text-red-800 leading-relaxed font-medium">
                      <strong className="block mb-1">Trạng thái mô hình</strong>
                      {spamResult?.warning || 'Kết quả từ API. Nếu độ tin cậy thấp, cân nhắc huấn luyện thêm dữ liệu.'}
                    </p>
                  </div>
                </div>

                <div className="space-y-6">
                  <span className="text-xs font-black text-slate-400 uppercase tracking-[0.2em]">Ma trận xác suất</span>
                  <div className="space-y-5">
                    <div className="relative bg-slate-50 p-4 rounded-2xl border border-slate-100">
                      <div className="flex justify-between text-sm mb-2">
                        <span className="font-bold text-slate-700">Dấu hiệu spam</span>
                        <span className="font-black text-red-600">{spamResult ? `${spamPercent}%` : '--'}</span>
                      </div>
                      <div className="h-1.5 w-full bg-slate-200 rounded-full overflow-hidden">
                        <motion.div 
                          initial={{ width: 0 }}
                          animate={{ width: spamResult ? `${spamPercent}%` : '0%' }}
                          className="h-full bg-red-500 rounded-full"
                        />
                      </div>
                    </div>
                    <div className="relative bg-slate-50 p-4 rounded-2xl border border-slate-100">
                      <div className="flex justify-between text-sm mb-2">
                        <span className="font-bold text-slate-700">Nội dung an toàn (ham)</span>
                        <span className="font-black text-emerald-600">{spamResult ? `${safePercent}%` : '--'}</span>
                      </div>
                      <div className="h-1.5 w-full bg-slate-200 rounded-full overflow-hidden">
                        <motion.div 
                          initial={{ width: 0 }}
                          animate={{ width: spamResult ? `${safePercent}%` : '0%' }}
                          className="h-full bg-emerald-500 rounded-full"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Right Column (Sidebar) */}
          <div className="col-span-12 lg:col-span-4 space-y-8">
            
            {/* History Card */}
            <Card className="p-8 flex flex-col h-full max-h-[850px] bg-white">
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                    <History size={18} className="text-slate-600" />
                  </div>
                  <h2 className="font-extrabold text-slate-900 tracking-tight">Lịch sử</h2>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={clearHistory}
                    className="text-[10px] font-black text-rose-600 hover:text-rose-800 uppercase tracking-widest bg-rose-50 px-3 py-1.5 rounded-full transition-all"
                  >
                    Xóa
                  </button>
                  <button
                    onClick={fetchHistory}
                    className="text-[10px] font-black text-indigo-600 hover:text-indigo-800 uppercase tracking-widest bg-indigo-50 px-3 py-1.5 rounded-full transition-all"
                  >
                    Làm mới
                  </button>
                </div>
              </div>

              <div className="space-y-4 overflow-y-auto pr-2 custom-scrollbar flex-grow">
                {isLoadingHistory && (
                  <p className="text-xs text-slate-400">Đang tải lịch sử...</p>
                )}
                {!isLoadingHistory && historyItems.length === 0 && (
                  <p className="text-xs text-slate-400">Chưa có bản ghi.</p>
                )}
                {historyItems.map((item) => (
                  <HistoryItem
                    key={item.id}
                    type={item.type}
                    title={item.text}
                    time={item.created_at ? new Date(item.created_at).toLocaleString('vi-VN') : ''}
                    confidence={`${item.confidence}%`}
                  />
                ))}
              </div>

              <div className="mt-8 pt-8 border-t border-slate-100 grid grid-cols-2 gap-4">
                <div className="bg-slate-50 p-4 rounded-2xl">
                  <div className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Độ chính xác</div>
                  <div className="text-xl font-black text-slate-900">
                    {spamResult ? `${confidencePercent}%` : '—'}
                  </div>
                </div>
                <div className="bg-slate-50 p-4 rounded-2xl">
                  <div className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Bản ghi</div>
                  <div className="text-xl font-black text-slate-900">{historyItems.length}</div>
                </div>
              </div>
            </Card>

            {/* API Forge Promo */}
            <motion.div 
              whileHover={{ scale: 1.02 }}
              className="bg-indigo-600 rounded-[2.5rem] p-8 text-white shadow-2xl shadow-indigo-300 relative overflow-hidden group cursor-pointer"
            >
              {/* Animated Particles */}
              <div className="absolute inset-0 overflow-hidden pointer-events-none">
                {[...Array(6)].map((_, i) => (
                  <motion.div
                    key={i}
                    animate={{ 
                      y: [0, -100], 
                      x: [0, Math.random() * 40 - 20],
                      opacity: [0, 0.5, 0] 
                    }}
                    transition={{ 
                      repeat: Infinity, 
                      duration: 3 + Math.random() * 2, 
                      delay: Math.random() * 2 
                    }}
                    className="absolute w-1 h-1 bg-white rounded-full"
                    style={{ 
                      left: `${Math.random() * 100}%`, 
                      bottom: '-10px' 
                    }}
                  />
                ))}
              </div>

              <div className="relative z-10">
                <div className="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center mb-6">
                  <Terminal size={24} />
                </div>
                <h4 className="text-xl font-extrabold mb-3 tracking-tight">Mở rộng với API Forge</h4>
                <p className="text-xs text-indigo-100/80 mb-6 leading-relaxed font-medium">Vận hành toàn bộ hạ tầng của bạn với động cơ phát hiện phản hồi 10ms của chúng tôi.</p>
                <button className="w-full bg-white text-indigo-600 py-4 rounded-2xl font-black text-sm hover:shadow-lg transition-all active:scale-95">
                  Đăng ký quyền truy cập API
                </button>
              </div>
              
              <div className="absolute -right-10 -bottom-10 w-40 h-40 bg-white/10 rounded-full blur-3xl group-hover:bg-white/20 transition-all duration-700" />
              <div className="absolute -left-10 -top-10 w-32 h-32 bg-indigo-400/20 rounded-full blur-2xl" />
            </motion.div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-20 py-12 border-t border-white/50 bg-white/20 backdrop-blur-sm">
        <div className="max-w-[1440px] mx-auto px-8 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <p className="text-sm font-bold text-slate-500">Hệ thống hoạt động ổn định: Nút toàn cầu v4.0</p>
          </div>
          <div className="flex items-center gap-10">
            <a href="#" className="text-xs font-black text-slate-400 hover:text-indigo-600 uppercase tracking-widest transition-colors">Pháp lý</a>
            <a href="#" className="text-xs font-black text-slate-400 hover:text-indigo-600 uppercase tracking-widest transition-colors">Bảo mật</a>
            <a href="#" className="text-xs font-black text-slate-400 hover:text-indigo-600 uppercase tracking-widest transition-colors">Trạng thái</a>
          </div>
          <p className="text-xs font-bold text-slate-400">© 2024 SpamGuard AI. Gói phân tích cao cấp.</p>
        </div>
      </footer>

      {/* Custom Scrollbar Styles */}
      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #e2e8f0;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #cbd5e1;
        }
      `}</style>
    </div>
  );
}
