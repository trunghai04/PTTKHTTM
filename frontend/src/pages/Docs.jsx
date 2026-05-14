import Navbar from '../components/Navbar';
import { ShieldCheck, Newspaper, Mail, BrainCircuit, BookOpen } from 'lucide-react';

export default function Docs() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <Navbar />

      <main className="max-w-5xl mx-auto px-6 py-12">
        {/* Header */}
        <header className="mb-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-[11px] font-bold text-indigo-700 uppercase tracking-[0.2em]">
            <BookOpen size={14} />
            <span>Tài liệu hệ thống</span>
          </div>
          <h1 className="mt-4 text-3xl md:text-4xl font-extrabold text-slate-900 tracking-tight">
            Tài liệu BloopAI – Spam &amp; News
          </h1>
          <p className="mt-3 text-slate-600 text-sm md:text-base max-w-2xl">
            Tóm tắt cách hệ thống hoạt động, kiến trúc mô hình, và hướng dẫn sử dụng các trang
            Spam, Tin tức và quét Gmail.
          </p>
        </header>

        {/* Architecture */}
        <section className="mb-10 space-y-3">
          <h2 className="text-xl font-extrabold text-slate-900 flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-bold">
              1
            </span>
            Kiến trúc tổng quan
          </h2>
          <p className="text-sm text-slate-600">
            Hệ thống chia làm hai mô-đun chính:
          </p>
          <ul className="list-disc pl-5 text-sm text-slate-600 space-y-1">
            <li>
              <strong>Spam</strong>: phân loại nội dung thành <strong>Spam</strong> hoặc{' '}
              <strong>Not Spam</strong> bằng mô hình Naive Bayes / Logistic Regression với TF‑IDF.
            </li>
            <li>
              <strong>Tin tức</strong>: phân loại văn bản vào các chủ đề tin tức (Thể thao, Chính trị,
              Kinh tế, Công nghệ, Giải trí, ...) bằng Logistic Regression đa lớp (Softmax).
            </li>
          </ul>
        </section>

        {/* Spam module */}
        <section className="mb-10 grid md:grid-cols-2 gap-6 items-start">
          <div className="space-y-3">
            <h2 className="text-xl font-extrabold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="text-red-500" />
              Spam Email
            </h2>
            <p className="text-sm text-slate-600">
              Văn bản được tiền xử lý bằng hàm <code className="font-mono">clean_text</code>{' '}
              (lowercase, bỏ URL, email, ký tự đặc biệt) rồi chuyển sang vector TF‑IDF.
            </p>
            <ul className="list-disc pl-5 text-sm text-slate-600 space-y-4">
              <li>
                <strong>Naive Bayes</strong>:
                <div className="mt-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-5 shadow-sm overflow-x-auto">
                  <div className="min-w-max text-center text-2xl md:text-3xl font-serif italic text-slate-900 whitespace-nowrap">
                    ŷ = argmax<sub className="align-sub text-[0.72em]">c<sub className="align-sub text-[0.72em]">j</sub></sub> P(c<sub className="align-sub text-[0.72em]">j</sub>) ∏ P(x<sub className="align-sub text-[0.72em]">i</sub>|c<sub className="align-sub text-[0.72em]">j</sub>)
                  </div>
                </div>
                <p className="mt-2 text-slate-600">
                  Nghĩa là ta chọn lớp <code className="font-mono">c_j</code> có giá trị lớn nhất
                  của tích giữa xác suất tiên nghiệm <code className="font-mono">P(c_j)</code> và
                  xác suất có điều kiện của các đặc trưng <code className="font-mono">P(x_i|c_j)</code>.
                </p>
              </li>
              <li>
                <strong>Logistic Regression</strong>:
                <div className="mt-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-5 shadow-sm">
                  <div className="text-center text-2xl md:text-3xl font-serif italic text-slate-900 leading-relaxed">
                    <div className="whitespace-nowrap">
                      P(y = 1 | x) = σ(w^T x + b)
                    </div>
                    <div className="mt-3 whitespace-nowrap">
                      σ(z) = <span className="inline-flex flex-col items-center align-middle mx-1 text-center leading-none"><span className="border-b border-current px-1 pb-1">1</span><span className="px-1 pt-1">1 + e<sup>−z</sup></span></span>
                    </div>
                  </div>
                </div>
                <p className="mt-2 text-slate-600">
                  Mô hình dự đoán spam khi xác suất vượt qua ngưỡng quyết định tối ưu theo F1.
                </p>
              </li>
            </ul>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-4 text-xs font-mono text-slate-700 space-y-2">
            <div className="font-bold text-slate-900 mb-1">Ví dụ request API</div>
            <pre className="whitespace-pre-wrap">
{`POST /api/spam/predict
Body:
{
  "text": "KHẨN: Tài khoản của bạn đã bị khóa, nhấn vào đây..."
}

Response:
{
  "label": "Spam",
  "confidence": 0.9971,
  "spam_probability": 0.9971,
  "not_spam_probability": 0.0029
}`}
            </pre>
          </div>
        </section>

        {/* News module */}
        <section className="mb-10 grid md:grid-cols-2 gap-6 items-start">
          <div className="space-y-3">
            <h2 className="text-xl font-extrabold text-slate-900 flex items-center gap-2">
              <Newspaper className="text-indigo-500" />
              Phân loại Tin tức
            </h2>
            <div className="text-sm text-slate-600">
              <p>
                Mô hình sử dụng Logistic Regression đa lớp với Softmax. Xác suất của mỗi lớp
                <code className="font-mono">c_j</code> được tính theo công thức sau.
              </p>
              <div className="mt-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-5 shadow-sm overflow-x-auto">
                <div className="min-w-max text-center text-2xl md:text-3xl font-serif italic text-slate-900 leading-relaxed whitespace-nowrap">
                  <div>P(y = c<sub className="align-sub text-[0.72em]">j</sub> | x) = e<sup>z<sub className="align-sub text-[0.72em]">j</sub></sup> / Σ e<sup>z<sub className="align-sub text-[0.72em]">k</sub></sup></div>
                  <div className="mt-3">z<sub className="align-sub text-[0.72em]">j</sub> = w<sub className="align-sub text-[0.72em]">j</sub><sup>T</sup> x + b<sub className="align-sub text-[0.72em]">j</sub></div>
                </div>
              </div>
              <p className="mt-3">
                Nhãn dự đoán cuối cùng là lớp có xác suất lớn nhất.
              </p>
            </div>
            <div className="text-sm text-slate-600">
              <p>
                Vector TF‑IDF dùng n‑gram (1–3) và bộ stopwords tiếng Việt để giữ lại cụm từ quan
                trọng.
              </p>
              <div className="mt-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-5 shadow-sm overflow-x-auto">
                <div className="min-w-max text-center text-2xl md:text-3xl font-serif italic text-slate-900 leading-relaxed whitespace-nowrap">
                  P(y = c<sub className="align-sub text-[0.72em]">j</sub> | x) = e<sup>z<sub className="align-sub text-[0.72em]">j</sub></sup> / Σ e<sup>z<sub className="align-sub text-[0.72em]">k</sub></sup>
                </div>
              </div>
            </div>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-4 text-xs font-mono text-slate-700 space-y-2">
            <div className="font-bold text-slate-900 mb-1">Ví dụ request API</div>
            <pre className="whitespace-pre-wrap">
{`POST /api/news/predict
Body:
{
  "text": "Messi ghi bàn giúp đội tuyển Argentina giành chiến thắng..."
}

Response:
{
  "label": "Thể thao",
  "confidence": 0.9821
}`}
            </pre>
          </div>
        </section>

        {/* Gmail scan */}
        <section className="mb-10 space-y-3">
          <h2 className="text-xl font-extrabold text-slate-900 flex items-center gap-2">
            <Mail className="text-emerald-500" />
            Quét Gmail
          </h2>
          <p className="text-sm text-slate-600">
            Sau khi đăng nhập bằng Google, hệ thống dùng <code className="font-mono">gmail.readonly</code>{' '}
            và refresh token để đọc tiêu đề, snippet và nội dung email, sau đó chạy Spam classifier
            cho từng thư.
          </p>
          <ul className="list-disc pl-5 text-sm text-slate-600 space-y-1">
            <li>Endpoint: <code className="font-mono">POST /api/gmail/scan?max_messages=200</code></li>
            <li>Kết quả được lưu vào bảng lịch sử và hiển thị tại trang “Lịch sử quét”.</li>
          </ul>
        </section>

        {/* Frontend pages */}
        <section className="mb-12 space-y-3">
          <h2 className="text-xl font-extrabold text-slate-900 flex items-center gap-2">
            <BrainCircuit className="text-purple-500" />
            Hướng dẫn sử dụng giao diện
          </h2>
          <ul className="list-disc pl-5 text-sm text-slate-600 space-y-1">
            <li>
              <strong>Trang Spam Email</strong>: dán nội dung email vào ô nhập → bấm “Kiểm tra spam”.
              Bên phải là lịch sử, có thể xem chi tiết và độ tin cậy.
            </li>
            <li>
              <strong>Trang Tin tức</strong>: dán nội dung bài báo → bấm “Phân loại tin tức”. Phần
              báo cáo hiển thị chủ đề chính và phân bố xác suất.
            </li>
            <li>
              <strong>Trang Lịch sử quét</strong>: đăng nhập bằng Google, sau đó bấm “Quét Gmail” để
              phân tích hàng loạt email.
            </li>
          </ul>
        </section>

        <footer className="pt-6 border-t border-slate-200 text-xs text-slate-500">
          Tài liệu này mô tả phiên bản demo của hệ thống BloopAI – phù hợp cho mục đích học tập và
          trình bày đồ án.
        </footer>
      </main>
    </div>
  );
}

