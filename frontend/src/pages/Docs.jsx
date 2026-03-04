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
            Tài liệu Lexica AI – Spam &amp; News
          </h1>
          <p className="mt-3 text-slate-600 text-sm md:text-base max-w-2xl">
            Tóm tắt cách hệ thống hoạt động, kiến trúc mô hình, và hướng dẫn sử dụng các trang
            Spam Email, Tin tức và quét Gmail.
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
              <strong>Spam Email</strong>: phân loại nội dung email thành <strong>Spam</strong> hoặc{' '}
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
            <ul className="list-disc pl-5 text-sm text-slate-600 space-y-1">
              <li>
                <strong>Naive Bayes</strong>:
                <span className="ml-1">
                  \(\hat y = \arg\max\_c P(c)\prod\_i P(w\_i\mid c)\)
                </span>
              </li>
              <li>
                <strong>Logistic Regression</strong>:
                <span className="ml-1">
                  \(P(y=1\mid x) = \sigma(w^T x + b)\), với ngưỡng quyết định tối ưu F1.
                </span>
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
            <p className="text-sm text-slate-600">
              Mô hình sử dụng Logistic Regression đa lớp với Softmax, nghĩa là xác suất cho mỗi lớp j
              được tính bằng: P(y = j | x) = exp(z_j) / ∑_k exp(z_k), với z_j = w_j^T x + b_j và nhãn
              dự đoán là lớp có xác suất lớn nhất.
            </p>
            <p className="text-sm text-slate-600">
              Vector TF‑IDF dùng n‑gram (1–3) và bộ stopwords tiếng Việt để giữ lại cụm từ quan
              trọng.
            </p>
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
          Tài liệu này mô tả phiên bản demo của hệ thống Lexica AI – phù hợp cho mục đích học tập và
          trình bày đồ án.
        </footer>
      </main>
    </div>
  );
}

