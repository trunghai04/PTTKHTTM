import {
  ShieldCheck,
  Newspaper,
  BarChart3,
  ArrowRight,
  Zap,
  Cpu,
  CheckCircle2,
  ChevronRight,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';

const Hero = () => {
  return (
    <section className="relative pt-20 pb-32 px-6 overflow-hidden">
      <div className="mesh-bg" />
      <div className="max-w-[1440px] mx-auto grid lg:grid-cols-2 gap-16 items-center">
        <motion.div 
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="space-y-8"
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-purple-200 bg-purple-50 text-accent-purple text-[10px] font-bold uppercase tracking-widest">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-purple opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-purple"></span>
            </span>
            Model NLP thế hệ mới
          </div>
          
          <h1 className="text-6xl lg:text-7xl font-extrabold leading-[1.1] text-text-charcoal tracking-tight">
            Phân loại văn bản với <br />
            <span className="accent-text-gradient">Độ chính xác tuyệt đối.</span>
          </h1>
          
          <p className="text-xl text-slate-600 max-w-xl leading-relaxed font-medium">
            Khai thác sức mạnh của các mạng nơ-ron tiên tiến để phân loại tin tức, phát hiện spam và rút ra insight sâu từ dữ liệu phi cấu trúc theo thời gian thực.
          </p>
          
          <div className="flex flex-wrap gap-4">
            <Link
              to="/spam"
              className="px-8 py-4 rounded-2xl bg-accent-blue text-white hover:bg-blue-700 transition-all font-bold flex items-center gap-2 shadow-xl shadow-blue-200 group"
            >
              Triển khai ngay 
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/docs"
              className="px-8 py-4 rounded-2xl border border-slate-200 bg-white text-text-charcoal font-bold hover:bg-slate-50 transition-all shadow-sm"
            >
              Xem tài liệu
            </Link>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="relative"
        >
          <div className="bg-white/90 backdrop-blur-xl p-6 rounded-[32px] border border-slate-200 shadow-2xl relative z-10">
            <div className="flex gap-2 mb-6 border-b border-slate-100 pb-4">
              <div className="w-3 h-3 rounded-full bg-red-400" />
              <div className="w-3 h-3 rounded-full bg-amber-400" />
              <div className="w-3 h-3 rounded-full bg-emerald-400" />
            </div>
            
            <div className="space-y-5 font-mono text-sm">
              <div className="space-y-2">
                <div className="flex gap-3 p-4 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-blue-600 font-bold shrink-0">ĐẦU VÀO:</span>
                  <span className="text-slate-600">"NÓNG: Thị trường lập đỉnh lịch sử khi nhóm cổ phiếu công nghệ tăng mạnh..."</span>
                </div>
                <motion.div 
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1 }}
                  className="flex gap-3 p-4 rounded-xl bg-blue-50 border border-blue-100"
                >
                  <span className="text-accent-blue font-bold shrink-0">KẾT QUẢ:</span>
                  <span className="text-slate-800 font-bold">KINH TẾ / TÍCH CỰC (độ tin cậy 0.984)</span>
                </motion.div>
              </div>

              <div className="space-y-2">
                <div className="flex gap-3 p-4 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-red-500 font-bold shrink-0">ĐẦU VÀO:</span>
                  <span className="text-slate-600">"KHẨN CẤP: Tài khoản của bạn đã bị tạm khóa. Nhấn vào đây..."</span>
                </div>
                <motion.div 
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.5 }}
                  className="flex gap-3 p-4 rounded-xl bg-red-50 border border-red-100"
                >
                  <span className="text-red-600 font-bold shrink-0">KẾT QUẢ:</span>
                  <span className="text-slate-800 font-bold">SPAM / RỦI RO CAO (độ tin cậy 0.999)</span>
                </motion.div>
              </div>
            </div>
          </div>
          
          {/* Decorative elements */}
          <div className="absolute -top-20 -right-20 w-64 h-64 bg-blue-400 rounded-full mix-blend-multiply filter blur-[100px] opacity-10 animate-pulse" />
          <div className="absolute -bottom-10 -left-10 w-64 h-64 bg-purple-400 rounded-full mix-blend-multiply filter blur-[100px] opacity-10 animate-pulse" />
        </motion.div>
      </div>
    </section>
  );
};

const Modules = () => {
  const modules = [
    {
      title: "Phát hiện spam",
      desc: "Lọc tự động nội dung độc hại, thư lừa đảo và tin nhắn không mong muốn với độ chính xác 99,9%.",
      icon: <ShieldCheck className="text-red-500 w-7 h-7" />,
      bg: "bg-red-50",
      border: "border-red-100",
      color: "text-accent-blue"
    },
    {
      title: "Phân loại tin tức",
      desc: "Phân loại lượng lớn tin tức vào các nhóm như Chính trị, Công nghệ, Thể thao trong vài mili-giây bằng các mô hình BERT.",
      icon: <Newspaper className="text-accent-purple w-7 h-7" />,
      bg: "bg-purple-50",
      border: "border-purple-100",
      color: "text-accent-purple"
    },
    {
      title: "Phân tích chuyên sâu",
      desc: "Trực quan hóa theo thời gian thực xu hướng phân loại, điểm tin cậy và phân bố dữ liệu lịch sử.",
      icon: <BarChart3 className="text-accent-blue w-7 h-7" />,
      bg: "bg-blue-50",
      border: "border-blue-100",
      color: "text-accent-blue"
    }
  ];

  return (
    <section className="py-32 px-6 max-w-[1440px] mx-auto">
      <div className="text-center mb-20">
        <h2 className="text-4xl font-extrabold mb-4 text-text-charcoal tracking-tight">Các Model thông minh</h2>
        <p className="text-slate-500 max-w-2xl mx-auto text-lg">Các bộ máy phân loại cấp doanh nghiệp được thiết kế cho độ tin cậy và khả năng mở rộng.</p>
      </div>
      
      <div className="grid md:grid-cols-3 gap-8">
        {modules.map((m, i) => (
          <motion.div 
            key={i}
            whileHover={{ y: -8 }}
            className="bg-white p-10 rounded-[32px] border border-slate-100 shadow-xl shadow-slate-100/50 group cursor-pointer transition-all"
          >
            <div className={`w-14 h-14 rounded-2xl ${m.bg} flex items-center justify-center mb-8 border ${m.border}`}>
              {m.icon}
            </div>
            <h3 className="text-2xl font-bold mb-4 text-text-charcoal group-hover:text-accent-blue transition-colors">{m.title}</h3>
            <p className="text-slate-500 mb-8 leading-relaxed">{m.desc}</p>
            <div className={`flex items-center text-sm font-bold ${m.color} gap-1 group-hover:gap-2 transition-all`}>
              Explore Module <ChevronRight className="w-4 h-4" />
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

const Pipeline = () => {
  return (
    <section className="py-32 px-6 bg-slate-50/50 border-y border-slate-200">
      <div className="max-w-[1440px] mx-auto">
        <div className="grid lg:grid-cols-2 gap-20 items-center">
          <div>
            <h2 className="text-4xl font-extrabold mb-12 text-text-charcoal tracking-tight">Quy trình xử lý tinh gọn</h2>
            <div className="space-y-12">
              {[
                { step: 1, title: "Tiếp nhận dữ liệu", desc: "Gửi văn bản qua REST API, WebSocket hoặc tải lên theo lô. Hỗ trợ hơn 40 ngôn ngữ ngay từ đầu.", color: "blue" },
                { step: 2, title: "Xử lý bằng mạng nơ-ron", desc: "Tập hợp mô hình của chúng tôi phân tích đồng thời ngữ nghĩa, ngữ cảnh và siêu dữ liệu.", color: "purple" },
                { step: 3, title: "Insight tức thì", desc: "Nhận phản hồi JSON với nhãn phân loại, điểm tin cậy và thông tin thực thể.", color: "emerald" }
              ].map((item, i) => (
                <div key={i} className="flex gap-6">
                  <div className={`flex-shrink-0 w-12 h-12 rounded-full border border-${item.color}-200 flex items-center justify-center text-${item.color}-600 font-bold bg-${item.color}-50 shadow-sm`}>
                    {item.step}
                  </div>
                  <div>
                    <h4 className="text-xl font-bold mb-2 text-text-charcoal">{item.title}</h4>
                    <p className="text-slate-500 leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="bg-white p-12 flex flex-col items-center justify-center text-center rounded-[48px] border border-slate-200 shadow-2xl shadow-slate-200/20 relative overflow-hidden">
            <div className="w-full max-w-sm aspect-square border-2 border-dashed border-slate-200 rounded-[40px] flex items-center justify-center relative bg-slate-50">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-48 h-48 bg-blue-400/10 rounded-full animate-pulse blur-3xl" />
              </div>
              <Cpu className="w-24 h-24 text-slate-300" />
              
              <div className="absolute -top-4 -left-4 bg-white border border-blue-200 px-5 py-2.5 text-xs font-mono rounded-xl shadow-lg text-blue-600 font-bold">
                TRANSFORMER_V4
              </div>
              <div className="absolute -bottom-4 -right-4 bg-white border border-purple-200 px-5 py-2.5 text-xs font-mono rounded-xl shadow-lg text-purple-600 font-bold">
                ENCODING_READY
              </div>
            </div>
            <p className="mt-10 text-sm text-slate-400 font-bold tracking-widest uppercase">Minh họa kiến trúc mạng nơ-ron nâng cao</p>
          </div>
        </div>
      </div>
    </section>
  );
};

const Stats = () => {
  return (
    <section className="py-24 px-6 max-w-[1440px] mx-auto text-center">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-12">
        {[
          { label: "Dự đoán mỗi ngày", val: "12M+", color: "text-accent-blue" },
          { label: "Độ chính xác của mô hình", val: "99.8%", color: "text-accent-purple" },
          { label: "Độ trễ xử lý", val: "45ms", color: "text-text-charcoal" },
          { label: "Thời gian hoạt động hệ thống", val: "24/7", color: "text-emerald-600" }
        ].map((s, i) => (
          <div key={i}>
            <div className={`text-5xl font-extrabold ${s.color} mb-3 tracking-tight`}>{s.val}</div>
            <p className="text-slate-500 text-[10px] uppercase tracking-[0.2em] font-bold">{s.label}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

const CTA = () => {
  return (
    <section className="py-32 px-6">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="max-w-5xl mx-auto bg-white p-16 md:p-24 text-center border border-slate-200 rounded-[48px] relative overflow-hidden shadow-2xl shadow-slate-200/30"
      >
        <div className="absolute -top-24 -left-24 w-80 h-80 bg-blue-50 rounded-full blur-[100px]" />
        <div className="absolute -bottom-24 -right-24 w-80 h-80 bg-purple-50 rounded-full blur-[100px]" />
        
        <div className="relative z-10">
          <h2 className="text-5xl md:text-6xl font-extrabold mb-8 text-text-charcoal tracking-tight">Sẵn sàng mở rộng năng lực AI của bạn?</h2>
          <p className="text-xl text-slate-500 mb-12 max-w-2xl mx-auto leading-relaxed">
            Gia nhập hơn 500+ doanh nghiệp đang dùng BloopAI để tự động hóa quy trình phân loại văn bản với độ chính xác cao.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-10 py-5 rounded-2xl bg-text-charcoal text-white font-bold hover:bg-accent-blue transition-all shadow-xl shadow-slate-200">
              Tạo tài khoản miễn phí
            </button>
            <button className="px-10 py-5 rounded-2xl bg-white border border-slate-200 text-text-charcoal font-bold hover:bg-slate-50 transition-all">
              Liên hệ kinh doanh
            </button>
          </div>
        </div>
      </motion.div>
    </section>
  );
};

const Footer = () => {
  return (
    <footer className="py-16 px-6 border-t border-slate-200 bg-white">
      <div className="max-w-[1440px] mx-auto flex flex-col md:flex-row justify-between items-center gap-12">
        <div className="flex items-center gap-2">
          <img
            src="/logo_rounded.png"
            alt="BloopAI logo"
            className="w-6 h-6 rounded-full object-cover"
          />
          <span className="font-bold text-text-charcoal text-lg">BloopAI</span>
        </div>
        
        <div className="flex flex-wrap justify-center gap-8 font-semibold text-sm text-slate-500">
          <a href="#" className="hover:text-accent-blue transition-colors">Chính sách bảo mật</a>
          <a href="#" className="hover:text-accent-blue transition-colors">Điều khoản dịch vụ</a>
          <a href="#" className="hover:text-accent-blue transition-colors">Trạng thái API</a>
          <a href="#" className="hover:text-accent-blue transition-colors">Liên hệ</a>
        </div>
        
        <p className="text-slate-400 text-sm">© 2026 BloopAI. Đã đăng ký bản quyền.</p>
      </div>
    </footer>
  );
};

export default function App() {
  return (
    <div className="min-h-screen selection:bg-blue-100 selection:text-blue-900">
      <Navbar />
      <main>
        <Hero />
        <Modules />
        <Pipeline />
        <Stats />
        <CTA />
      </main>
      <Footer />
    </div>
  );
}
