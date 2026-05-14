/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect, useMemo } from 'react';
import {
  Newspaper as NewspaperIcon,
  Crown,
  History as HistoryIcon,
  BrainCircuit,
  Sparkles,
  FileUp,
  CheckCircle2,
  ChevronRight,
  Code2,
  Eraser,
  Info as InfoIcon,
  Activity,
  ShieldCheck,
  ExternalLink,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../api/client';
import Navbar from '../components/Navbar';
import { useNavigate } from 'react-router-dom';

export default function App() {
  const [inputText, setInputText] = useState('');
  const [isClassifying, setIsClassifying] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const isLoggedIn = !!localStorage.getItem('access_token');

  const wordCount = useMemo(() => {
    return inputText.trim() ? inputText.trim().split(/\s+/).length : 0;
  }, [inputText]);

  const fetchNewsHistory = async () => {
    try {
      if (!isLoggedIn) {
        // Khách: không gọi API, lịch sử chỉ tồn tại trong state
        setHistory([]);
        return;
      }
      const res = await api.get('/api/news/history', { params: { limit: 50 } });
      const mapped = (res.data || []).map((item) => ({
        id: item.id,
        topic: item.predicted_label || 'Other',
        preview: (item.text || '').substring(0, 100) + (item.text?.length > 100 ? '...' : ''),
        time: item.created_at ? new Date(item.created_at).toLocaleString('vi-VN') : '',
        verified: true,
      }));
      setHistory(mapped);
    } catch (e) {
      console.error(e);
    }
  };

  const handleUploadTextFile = async (file) => {
    if (!file) return;
    const content = await file.text();
    setInputText(content || '');
  };

  const clearHistory = async () => {
    try {
      if (isLoggedIn) {
        await api.delete('/api/news/history');
        await fetchNewsHistory();
      } else {
        // Khách: chỉ xóa lịch sử tạm thời trong state
        setHistory([]);
      }
    } catch (e) {
      console.error(e);
      setError(e?.response?.data?.detail || 'Không thể xóa lịch sử');
    }
  };

  useEffect(() => {
    fetchNewsHistory();
  }, []);

  const handleClassify = async () => {
    if (!inputText.trim()) return;
    setIsClassifying(true);
    setError(null);
    try {
      const res = await api.post('/api/news/predict', { text: inputText });
      const { label, confidence } = res.data;
      const confidencePercent = Math.round((confidence || 0) * 100);
      const otherPercent = Math.max(0, 100 - confidencePercent);
      setResult({
        confidence: confidencePercent,
        summary: `Mô hình dự đoán chủ đề "${label || 'N/A'}" với độ tin cậy ${confidencePercent}%.`,
        distribution: [
          { label: label || 'Chính', percentage: confidencePercent, color: 'bg-blue-500' },
          { label: 'Khác', percentage: otherPercent, color: 'bg-slate-300' },
        ],
      });
      if (isLoggedIn) {
        await fetchNewsHistory();
      } else {
        // Khách: cập nhật lịch sử tạm thời trong phiên hiện tại
        const preview = (inputText || '').substring(0, 100) + ((inputText || '').length > 100 ? '...' : '');
        const time = new Date().toLocaleString('vi-VN');
        const item = {
          id: Date.now(),
          topic: label || 'Other',
          preview,
          time,
          verified: false,
        };
        setHistory((prev) => [item, ...prev].slice(0, 50));
      }
    } catch (e) {
      console.error(e);
      setError(e?.response?.data?.detail || 'Có lỗi khi gọi API phân loại tin tức');
    } finally {
      setIsClassifying(false);
    }
  };

  return (
    <div className="min-h-screen font-sans">
      <Navbar />

      <main className="max-w-[1440px] mx-auto px-8 py-12">
        <div className="grid grid-cols-12 gap-10">
          {/* Main Content */}
          <div className="col-span-12 lg:col-span-8 space-y-10">
            {/* Input Section */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card rounded-[2.5rem] p-1"
            >
              <div className="p-10">
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">Phân tích tin tức</h2>
                    <p className="text-slate-500 font-medium text-sm mt-1">Phân loại bài báo bằng mô hình backend.</p>
                  </div>
                  {error && (
                    <p className="mb-2 text-xs font-semibold text-red-600">{error}</p>
                  )}
                  <div className="flex items-center gap-2 px-4 py-2 bg-white/60 border border-slate-100 rounded-2xl shadow-sm">
                    <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
                    <span className="text-[11px] font-bold text-slate-600">Model: <span className="text-blue-600">GPT-Neural-4</span></span>
                  </div>
                </div>

                <div className="relative group">
                  <textarea 
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    className="w-full h-80 p-10 bg-white/50 border border-slate-200/60 rounded-[2rem] focus:ring-[12px] focus:ring-blue-500/5 focus:border-blue-400/40 outline-none transition-all resize-none text-slate-700 text-lg leading-relaxed placeholder:text-slate-300 shadow-inner" 
                    placeholder="Dán toàn bộ nội dung bài báo hoặc bản tin vào đây để phân loại..."
                  />
                  <div className="absolute bottom-6 left-8 flex gap-3">
                    <div className="px-4 py-1.5 bg-slate-900/90 text-white rounded-full text-[10px] font-bold tracking-tight backdrop-blur-md">
                      Số từ hiện tại: <span className="text-blue-400">{wordCount}</span>
                    </div>
                    <div className="px-4 py-1.5 bg-white/80 border border-slate-200 rounded-full text-[10px] font-bold text-slate-600 backdrop-blur-md">
                      Gợi ý chủ đề: <span className="text-violet-600">{inputText ? 'Đang phân tích...' : 'Chờ nhập nội dung'}</span>
                    </div>
                  </div>
                  <div className="absolute top-6 right-8">
                    <button 
                      onClick={() => setInputText('')}
                      className="p-2 text-slate-400 hover:text-red-500 transition-colors" 
                      title="Xóa tất cả"
                    >
                      <Eraser size={20} />
                    </button>
                  </div>
                </div>

                <div className="mt-8 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 px-5 py-3 bg-slate-50 text-slate-600 rounded-2xl hover:bg-white hover:shadow-lg transition-all border border-slate-100 text-xs font-bold cursor-pointer">
                      <FileUp size={18} />
                      Nhập PDF/Văn bản
                      <input
                        type="file"
                        accept=".txt,text/plain"
                        className="hidden"
                        onChange={(e) => handleUploadTextFile(e.target.files?.[0])}
                      />
                    </label>
                    <div className="flex items-center gap-2 px-3">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Ưu tiên</span>
                      <input className="rounded text-blue-600 focus:ring-blue-500 w-4 h-4 border-slate-300" type="checkbox"/>
                    </div>
                  </div>
                  <button 
                    onClick={handleClassify}
                    disabled={isClassifying || !inputText.trim()}
                    className="bg-gradient-to-r from-blue-600 to-violet-600 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:scale-100 px-10 py-5 rounded-2xl text-white font-black flex items-center gap-4 shadow-2xl shadow-blue-200 transition-all"
                  >
                    <span className="text-base">{isClassifying ? 'Đang phân loại...' : 'Phân loại tin tức'}</span>
                    <Sparkles size={20} />
                  </button>
                </div>
              </div>
            </motion.div>

            {/* Report Section */}
            <AnimatePresence>
              {(result || isClassifying) && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="bg-white/80 rounded-[2.5rem] shadow-xl shadow-slate-100/50 border border-slate-200/40 p-10 backdrop-blur-sm"
                >
                  <div className="flex items-start justify-between mb-12">
                    <div>
                      <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">Báo cáo phân loại</h3>
                      <p className="text-sm font-medium text-slate-400">Phân bố chủ đề và chỉ số độ tin cậy chi tiết</p>
                    </div>
                    <div className="flex items-center gap-4 bg-slate-50/50 p-3 rounded-2xl border border-slate-100">
                      <div className="flex gap-1 items-end h-5 px-1">
                        <div className="waveform-bar" style={{ animationDelay: '0s' }}></div>
                        <div className="waveform-bar" style={{ animationDelay: '0.2s' }}></div>
                        <div className="waveform-bar" style={{ animationDelay: '0.4s' }}></div>
                        <div className="waveform-bar" style={{ animationDelay: '0.1s' }}></div>
                      </div>
                      <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Đang phân tích</span>
                    </div>
                  </div>

                  {isClassifying ? (
                    <div className="flex flex-col items-center justify-center py-20 space-y-4">
                      <div className="w-12 h-12 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
                      <p className="text-slate-400 font-bold text-sm animate-pulse">Đang xử lý các cụm ngữ nghĩa...</p>
                    </div>
                  ) : result && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-16">
                      <div className="space-y-10">
                        <div>
                          <div className="flex justify-between items-end mb-4">
                            <span className="text-[11px] font-black text-slate-400 uppercase tracking-[0.1em]">Độ tin cậy tổng thể</span>
                            <span className="text-4xl font-black text-slate-900">{result.confidence}<span className="text-blue-500 text-2xl">%</span></span>
                          </div>
                          <div className="h-4 w-full bg-slate-100/50 rounded-full overflow-hidden p-1">
                            <motion.div 
                              initial={{ width: 0 }}
                              animate={{ width: `${result.confidence}%` }}
                              className="h-full bg-gradient-to-r from-blue-500 to-violet-500 rounded-full shadow-sm"
                            />
                          </div>
                        </div>
                        <div className="p-8 bg-blue-50/40 rounded-[2rem] border border-blue-100/50 flex gap-5">
                          <div className="w-12 h-12 rounded-2xl bg-blue-500 flex items-center justify-center text-white flex-shrink-0 shadow-lg shadow-blue-200">
                            <BrainCircuit size={24} />
                          </div>
                          <div>
                            <h4 className="font-extrabold text-blue-900 text-sm mb-1">Tóm tắt insight chính</h4>
                            <p className="text-sm text-blue-800/80 leading-relaxed font-medium">
                              {result.summary}
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-6">
                        <span className="text-[11px] font-black text-slate-400 uppercase tracking-[0.2em]">Phân bố chủ đề</span>
                        <div className="space-y-4">
                          {result.distribution.map((topic, idx) => (
                            <div key={idx} className="space-y-2">
                              <div className="flex justify-between text-[13px]">
                                <span className="font-bold text-slate-700 flex items-center gap-2">
                                  <span className={`w-2 h-2 rounded-full ${topic.color}`}></span> {topic.label}
                                </span>
                                <span className="font-black text-slate-900">{topic.percentage}%</span>
                              </div>
                              <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                                <motion.div 
                                  initial={{ width: 0 }}
                                  animate={{ width: `${topic.percentage}%` }}
                                  className={`h-full ${topic.color} rounded-full`}
                                />
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Sidebar */}
          <div className="col-span-12 lg:col-span-4 space-y-10">
            {/* History Card */}
            <div className="bg-white/90 rounded-[2.5rem] shadow-xl shadow-slate-200/40 border border-slate-200/60 p-8 flex flex-col h-[740px]">
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center">
                    <HistoryIcon size={20} className="text-slate-500" />
                  </div>
                  <h2 className="font-extrabold text-slate-900 tracking-tight">Lịch sử</h2>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={clearHistory}
                    className="text-[10px] font-black text-rose-600 hover:text-rose-800 uppercase tracking-widest bg-rose-50 px-3 py-2 rounded-full transition-all border border-rose-100"
                  >
                    Xóa
                  </button>
                  <button
                    onClick={fetchNewsHistory}
                    className="text-[10px] font-black text-slate-400 hover:text-blue-600 uppercase tracking-widest bg-slate-50 px-3 py-2 rounded-full transition-all border border-slate-100"
                  >
                    Làm mới
                  </button>
                </div>
              </div>

              <div className="space-y-4 overflow-y-auto custom-scrollbar pr-2 flex-grow">
                {history.length === 0 && (
                  isLoggedIn ? (
                    <p className="text-xs text-slate-400">Chưa có bản ghi.</p>
                  ) : (
                    <div className="space-y-1 text-xs text-slate-400">
                      <p>Chưa có bản ghi.</p>
                      <p className="text-[11px]">
                        <span className="font-semibold text-slate-600">Chưa đăng nhập:</span>{' '}
                        lịch sử chỉ lưu tạm thời. Đăng nhập để giữ lịch sử lâu dài.
                      </p>
                    </div>
                  )
                )}
                {history.map((item) => (
                  <motion.div 
                    key={item.id}
                    layout
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    onClick={() =>
                      navigate('/news/detail', {
                        state: { entry: item },
                      })
                    }
                    className="group p-5 bg-white border border-slate-100 rounded-3xl cursor-pointer relative overflow-hidden shadow-sm hover:translate-y-[-4px] hover:bg-slate-50/50 transition-all"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <span className={`px-3 py-1 ${
                        item.topic === 'Politics' ? 'bg-blue-100/50 text-blue-600' :
                        item.topic === 'Sports' ? 'bg-green-100/50 text-green-600' :
                        item.topic === 'Technology' ? 'bg-violet-100/50 text-violet-600' :
                        'bg-slate-100 text-slate-600'
                      } text-[9px] font-black rounded-full uppercase tracking-wider`}>
                        {item.topic}
                      </span>
                      <span className="text-[10px] font-bold text-slate-400">{item.time}</span>
                    </div>
                    <p className="text-sm text-slate-700 line-clamp-2 font-semibold leading-relaxed mb-4">{item.preview}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-400 uppercase">
                        <CheckCircle2 size={14} className="text-green-500" />
                        Đã quét xác thực
                      </div>
                      <div className="flex items-center gap-1 text-blue-600 opacity-0 group-hover:opacity-100 transition-all transform translate-x-2 group-hover:translate-x-0">
                        <span className="text-[10px] font-black uppercase">Chi tiết</span>
                        <ChevronRight size={16} />
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              <div className="mt-8 pt-8 border-t border-slate-100 grid grid-cols-2 gap-4">
                <div className="bg-slate-50 p-4 rounded-2xl">
                  <div className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Bài viết</div>
                  <div className="text-xl font-black text-slate-900">{history.length}</div>
                </div>
                <div className="bg-slate-50 p-4 rounded-2xl">
                  <div className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Hiệu suất</div>
                  <div className="text-xl font-black text-slate-900">{result ? `${result.confidence}%` : '—'}</div>
                </div>
              </div>
            </div>

            {/* Enterprise Card */}
            <div className="bg-gradient-to-br from-blue-700 via-indigo-700 to-violet-800 rounded-[2.5rem] p-8 text-white shadow-2xl shadow-indigo-200/50 relative overflow-hidden group">
              {/* Decorative particles */}
              <div className="absolute inset-0 overflow-hidden pointer-events-none">
                {[...Array(5)].map((_, i) => (
                  <div 
                    key={i}
                    className="absolute bg-white/10 rounded-full blur-xl"
                    style={{
                      width: Math.random() * 100 + 50,
                      height: Math.random() * 100 + 50,
                      left: `${Math.random() * 100}%`,
                      top: `${Math.random() * 100}%`,
                      animation: `pulse ${Math.random() * 3 + 2}s infinite alternate`
                    }}
                  />
                ))}
              </div>

              <div className="relative z-10">
                <div className="w-14 h-14 rounded-2xl bg-white/10 backdrop-blur-md flex items-center justify-center mb-8 border border-white/20">
                  <Code2 size={30} />
                </div>
                <h4 className="text-2xl font-extrabold mb-4 tracking-tight leading-tight">Quyền truy cập API cho các tòa soạn tin tức</h4>
                <p className="text-sm text-blue-100/70 mb-8 leading-relaxed font-medium">Kết nối CMS của bạn với bộ máy phân loại của chúng tôi để sắp xếp tin tức theo thời gian thực.</p>
                <button className="w-full bg-white text-indigo-700 py-4 rounded-[1.25rem] font-black text-sm hover:bg-blue-50 transition-all shadow-xl active:scale-95">
                  Nâng cấp lên API Doanh nghiệp
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-20 py-16 border-t border-white/40 bg-white/30 backdrop-blur-md">
        <div className="max-w-[1440px] mx-auto px-8 flex flex-col md:flex-row justify-between items-center gap-10">
          <div className="flex items-center gap-3">
            <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></span>
            <p className="text-sm font-bold text-slate-500">All Neural Nodes Operational</p>
          </div>
          <div className="flex items-center gap-12">
            <a className="text-xs font-black text-slate-400 hover:text-blue-600 uppercase tracking-widest transition-colors" href="#">API Docs</a>
            <a className="text-xs font-black text-slate-400 hover:text-blue-600 uppercase tracking-widest transition-colors" href="#">Security</a>
            <a className="text-xs font-black text-slate-400 hover:text-blue-600 uppercase tracking-widest transition-colors" href="#">Terms</a>
          </div>
          <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">© 2024 NewsPage AI. Premium Tier.</p>
        </div>
      </footer>
    </div>
  );
}
