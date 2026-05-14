import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
} from 'recharts';
import {
  TrendingUp,
  ShieldAlert,
  Newspaper,
  CheckCircle2,
  Settings2,
  RefreshCw,
} from 'lucide-react';
import { motion } from 'framer-motion';
import api from '../api/client';
import Navbar from '../components/Navbar';

const cn = (...classes) => classes.filter(Boolean).join(' ');

// --- Components ---

const StatCard = ({
  title,
  value,
  trend = 'up', // 'up' | 'down' | 'stable'
  trendValue,
  icon,
  iconBg,
  iconColor,
  sparklinePoints,
  sparklineColor,
}) => {
  const trendColor =
    trend === 'up'
      ? 'text-emerald-500'
      : trend === 'down'
      ? 'text-rose-500'
      : 'text-slate-500';

  const Icon = icon;

  return (
  <motion.div 
    initial={{ opacity: 0, y: 14 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-white/95 backdrop-blur-md shadow-[0_14px_30px_rgba(15,23,42,0.08)] px-5 py-4 rounded-3xl flex flex-col justify-between"
  >
    <div className="flex justify-between items-start mb-3">
      <div className={cn("p-2.5 rounded-2xl shadow-sm", iconBg, iconColor)}>
        {Icon && <Icon className="w-6 h-6" />}
      </div>
      <svg
        width="72"
        height="22"
        viewBox="0 0 80 30"
        fill="none"
        className="mt-1"
      >
        <polyline
          points={sparklinePoints}
          fill="none"
          stroke={sparklineColor}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </div>
    <div>
      <p className="text-xs font-semibold text-slate-500">{title}</p>
      <div className="flex items-baseline gap-2 mt-1">
        <h2 className="text-2xl font-bold text-slate-900">{value}</h2>
        <span className={cn("text-xs font-bold", trendColor)}>
          {trendValue}
        </span>
      </div>
    </div>
  </motion.div>
);
};

const ProgressBar = ({ label, value, percentage, color }) => (
  <div>
    <div className="flex justify-between items-center mb-2">
      <span className="text-sm font-semibold text-slate-600">{label}</span>
      <span className="text-sm font-bold text-slate-900">{value}</span>
    </div>
    <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
      <motion.div 
        initial={{ width: 0 }}
        animate={{ width: `${percentage}%` }}
        transition={{ duration: 1, ease: "easeOut" }}
        className={cn("h-full rounded-full", color)} 
      />
    </div>
  </div>
);

export default function App() {
  const [timeRange, setTimeRange] = useState('Tháng');
  const [stats, setStats] = useState(null);
  const [topicData, setTopicData] = useState([]);
  const [spamData, setSpamData] = useState([]);
  const [monthlyData, setMonthlyData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timelineRange, setTimelineRange] = useState('month');

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [overviewRes, newsCatRes] = await Promise.all([
        api.get('/api/stats/overview'),
        api.get('/api/stats/news/categories'),
      ]);
      const overview = overviewRes.data;
      const categories = newsCatRes.data || [];
      setStats(overview);

      const totalNews = categories.reduce((s, c) => s + (c.count || 0), 0);
      const palette = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#06b6d4'];
      setTopicData(
        totalNews > 0
          ? categories.map((c, idx) => ({
              name: c.category || 'Khác',
              value: Math.round(((c.count || 0) / totalNews) * 100),
              color: palette[idx % palette.length],
            }))
          : []
      );

      const total = overview.total_predictions || 0;
      const spamTotal = overview.spam_total || 0;
      const spamRate = total ? Math.round((spamTotal / total) * 100) : 0;
      setSpamData([
        { name: 'Hợp lệ', value: 100 - spamRate, color: '#3b82f6' },
        { name: 'Spam', value: spamRate, color: '#f43f5e' },
      ]);

      // timeline fetched in separate effect based on selected range
    } catch (e) {
      console.error(e);
      setError('Không lấy được số liệu từ API');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  useEffect(() => {
    const mapRange = (label) => {
      if (label === 'Ngày') return 'day';
      if (label === 'Năm') return 'year';
      return 'month';
    };
    setTimelineRange(mapRange(timeRange));
  }, [timeRange]);

  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        const res = await api.get('/api/stats/timeline', {
          params: { range: timelineRange, limit: timelineRange === 'day' ? 30 : 12 },
        });
        const rows = res.data || [];
        const mapped = rows.map((r, idx) => {
          const bucket = r.bucket || '';
          let label = bucket;
          if (timelineRange === 'month' && bucket.includes('-')) {
            const parts = bucket.split('-');
            const monthPart = parts[1] || '';
            label = `Th${monthPart}`;
          }
          return {
            name: label,
            total: r.total ?? 0,
            news: r.news_total ?? 0,
            spam: r.spam_total ?? 0,
            active: idx === rows.length - 1,
          };
        });
        setMonthlyData(mapped);
      } catch (e) {
        console.error(e);
        // keep old chart if any; but set an error message
        setError((prev) => prev || 'Không lấy được timeline từ API');
      }
    };

    fetchTimeline();
  }, [timelineRange]);

  const totalPred = stats?.total_predictions ?? 0;
  const spamTotal = stats?.spam_total ?? 0;
  const newsTotal = stats?.news_total ?? 0;
  const avgConf = stats?.average_confidence ?? 0;
  const spamRate = totalPred ? Math.round((spamTotal / totalPred) * 100) : 0;
  const avgConfPercent = Math.round(avgConf * 1000) / 10;

  const rangeNewsTotal = monthlyData.reduce((sum, item) => sum + (item.news || 0), 0);
  const rangeSpamTotal = monthlyData.reduce((sum, item) => sum + (item.spam || 0), 0);
  const rangeTotal = rangeNewsTotal + rangeSpamTotal;

  // --- Trend calculations based on last vs previous bucket in timeline ---
  const lastPoint = monthlyData.length >= 1 ? monthlyData[monthlyData.length - 1] : null;
  const prevPoint = monthlyData.length >= 2 ? monthlyData[monthlyData.length - 2] : null;

  const calcChange = (current, previous) => {
    if (current == null || previous == null || previous === 0) return null;
    return ((current - previous) / previous) * 100;
  };

  const totalChange = calcChange(lastPoint?.total, prevPoint?.total);

  const lastSpamRate =
    lastPoint && lastPoint.total ? (lastPoint.spam / lastPoint.total) * 100 : null;
  const prevSpamRate =
    prevPoint && prevPoint.total ? (prevPoint.spam / prevPoint.total) * 100 : null;
  const spamRateChange = calcChange(lastSpamRate, prevSpamRate);

  const newsChange = calcChange(lastPoint?.news, prevPoint?.news);

  const formatChange = (val) => {
    if (val == null || Number.isNaN(val)) return '—';
    const rounded = Math.round(val * 10) / 10;
    const sign = rounded > 0 ? '+' : '';
    return `${sign}${rounded}%`;
  };

  const totalTrend = totalChange == null ? 'stable' : totalChange >= 0 ? 'up' : 'down';
  const spamTrend = spamRateChange == null ? 'stable' : spamRateChange >= 0 ? 'up' : 'down';
  const newsTrend = newsChange == null ? 'stable' : newsChange >= 0 ? 'up' : 'down';

  return (
    <div className="p-8 text-slate-800">
      <Navbar />
      <div className="mesh-bg" />
      
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end mb-10 gap-4">
          <div>
            <h1 className="text-4xl font-bold tracking-tight text-slate-900">Dashboard</h1>
            <p className="text-slate-500 mt-2 font-medium">Thống kê dữ liệu</p>
          </div>
          {error && (
            <p className="text-sm font-semibold text-red-600">{error}</p>
          )}
          <div className="flex items-center gap-4">
            <div className="text-right mr-4 hidden md:block">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Trạng thái hệ thống</p>
              <p className="text-sm font-medium text-emerald-600 flex items-center justify-end gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" /> Đang hoạt động
              </p>
            </div>
            <button
              onClick={fetchDashboardData}
              className="glass-card p-3 rounded-2xl flex items-center justify-center hover:bg-white/80 transition-all duration-300"
            >
              <Settings2 className="w-6 h-6 text-slate-600" />
            </button>
          </div>
        </header>

        {/* Top Stats */}
        <section className="relative rounded-[2.5rem] bg-gradient-to-r from-slate-50 via-white to-slate-50 px-4 py-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard 
              title="Total Predictions"
              value={loading ? '...' : totalPred.toLocaleString('en-US')}
              trend={totalTrend}
              trendValue={formatChange(totalChange)}
              icon={TrendingUp}
              iconBg="bg-indigo-50"
              iconColor="text-indigo-600"
              sparklinePoints="0,20 10,15 20,25 30,10 40,18 50,5 60,15 70,8 80,12"
              sparklineColor="#818cf8"
            />
            <StatCard 
              title="Spam Detected"
              value={loading ? '...' : `${spamRate}%`}
              trend={spamTrend}
              trendValue={formatChange(spamRateChange)}
              icon={ShieldAlert}
              iconBg="bg-rose-50"
              iconColor="text-rose-600"
              sparklinePoints="0,10 10,25 20,15 30,28 40,12 50,20 60,8 70,18 80,5"
              sparklineColor="#fb7185"
            />
            <StatCard 
              title="News Processed"
              value={loading ? '...' : newsTotal.toLocaleString('en-US')}
              trend={newsTrend}
              trendValue={formatChange(newsChange)}
              icon={Newspaper}
              iconBg="bg-amber-50"
              iconColor="text-amber-600"
              sparklinePoints="0,25 15,10 30,20 45,5 60,15 80,10"
              sparklineColor="#fbbf24"
            />
            <StatCard 
              title="Avg Confidence"
              value={loading ? '...' : `${avgConfPercent}%`}
              trend="stable"
              trendValue="Stable"
              icon={CheckCircle2}
              iconBg="bg-emerald-50"
              iconColor="text-emerald-600"
              sparklinePoints="0,15 20,15 40,10 60,10 80,5"
              sparklineColor="#34d399"
            />
          </div>
        </section>

        {/* Donut Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-card p-8 rounded-[2.5rem] relative overflow-hidden"
          >
            <div className="flex justify-between items-center mb-8">
              <h3 className="text-xl font-bold text-slate-800">Chủ đề Tin tức</h3>
              <div className="text-xs font-bold text-slate-400 uppercase tracking-widest">Phân bổ tổng thể</div>
            </div>
            <div className="flex flex-col sm:flex-row items-center justify-between gap-8">
              <div className="relative w-48 h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={topicData.length ? topicData : [{ name: 'Chưa có', value: 100, color: '#e2e8f0' }]}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                      stroke="none"
                    >
                      {(topicData.length ? topicData : [{ name: 'Chưa có', value: 100, color: '#e2e8f0' }]).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-2xl font-bold">
                    {loading ? '...' : (stats?.news_total ?? 0).toLocaleString('vi-VN')}
                  </span>
                  <span className="text-[10px] text-slate-400 uppercase font-bold">Tổng</span>
                </div>
              </div>
              <div className="space-y-4 flex-1">
                {!loading && topicData.length === 0 && (
                  <p className="text-xs text-slate-400">Chưa có thống kê chủ đề.</p>
                )}
                {topicData.map((topic) => (
                  <div key={topic.name} className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: topic.color }} />
                    <span className="text-sm font-medium text-slate-600">{topic.name}</span>
                    <span className="text-xs font-bold text-slate-400 ml-auto">{topic.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-card p-8 rounded-[2.5rem] relative overflow-hidden"
          >
            <div className="flex justify-between items-center mb-8">
              <h3 className="text-xl font-bold text-slate-800">Tỉ lệ Phát hiện</h3>
              <div className="text-xs font-bold text-slate-400 uppercase tracking-widest">Đã Quét</div>
            </div>
            <div className="flex flex-col sm:flex-row items-center justify-between gap-8">
              <div className="relative w-48 h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={spamData.length ? spamData : [{ name: 'Hợp lệ', value: 100, color: '#3b82f6' }]}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={0}
                      dataKey="value"
                      stroke="none"
                      startAngle={90}
                      endAngle={-270}
                    >
                      {(spamData.length ? spamData : [{ name: 'Hợp lệ', value: 100, color: '#3b82f6' }]).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-2xl font-bold">{loading ? '...' : `${spamRate}%`}</span>
                  <span className="text-[10px] text-slate-400 uppercase font-bold">Spam</span>
                </div>
              </div>
              <div className="space-y-4 w-full sm:w-1/2">
                <div className="p-4 rounded-2xl bg-blue-50/50 border border-blue-100">
                  <div className="flex justify-between mb-1">
                    <span className="text-xs font-bold text-blue-600 uppercase">Hợp lệ</span>
                    <span className="text-xs font-bold text-blue-900">{loading ? '...' : `${100 - spamRate}%`}</span>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-1.5">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: loading ? '0%' : `${100 - spamRate}%` }}
                      className="bg-blue-600 h-1.5 rounded-full" 
                    />
                  </div>
                </div>
                <div className="p-4 rounded-2xl bg-rose-50/50 border border-rose-100">
                  <div className="flex justify-between mb-1">
                    <span className="text-xs font-bold text-rose-600 uppercase">Đã lọc</span>
                    <span className="text-xs font-bold text-rose-900">{loading ? '...' : `${spamRate}%`}</span>
                  </div>
                  <div className="w-full bg-rose-200 rounded-full h-1.5">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: loading ? '0%' : `${spamRate}%` }}
                      className="bg-rose-600 h-1.5 rounded-full" 
                    />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Main Chart */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-8 rounded-[2.5rem]"
        >
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-10 gap-4">
            <div>
              <h3 className="text-xl font-bold text-slate-800">Hoạt động phân loại theo thời gian</h3>
              <p className="text-sm text-slate-400 font-medium">
                Số lượng tin tức và spam theo {timeRange.toLowerCase()}
              </p>
            </div>
            <div className="flex gap-2 bg-slate-100/50 p-1 rounded-full">
              {['Ngày', 'Tháng', 'Năm'].map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={cn(
                    "px-4 py-1.5 rounded-full text-xs font-bold transition-all duration-300",
                    timeRange === range 
                      ? "bg-indigo-600 text-white shadow-lg shadow-indigo-200" 
                      : "text-slate-500 hover:text-slate-700"
                  )}
                >
                  {range}
                </button>
              ))}
            </div>
          </div>
          
          <div className="h-[260px] w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={
                  monthlyData.length
                    ? monthlyData
                    : [{ name: '-', total: 0, news: 0, spam: 0, active: false }]
                }
                margin={{ top: 0, right: 0, left: -20, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis 
                  dataKey="name" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fontSize: 10, fontWeight: 700, fill: '#94a3b8' }}
                  dy={10}
                />
                <YAxis hide />
                <Tooltip 
                  cursor={{ fill: '#f8fafc' }}
                  contentStyle={{ 
                    borderRadius: '12px', 
                    border: 'none', 
                    boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
                    fontSize: '12px',
                    fontWeight: 'bold'
                  }}
                  formatter={(value, name) => {
                    if (name === 'total') return [value, 'Total Predictions'];
                    if (name === 'spam') return [value, 'Spam Detected'];
                    if (name === 'news') return [value, 'News Processed'];
                    return [value, name];
                  }}
                  labelFormatter={(label) => `Thời gian: ${label}`}
                />
                <Bar dataKey="total" radius={[8, 8, 0, 0]} fill="#818cf8" />
                <Bar dataKey="spam" radius={[8, 8, 0, 0]} fill="#fb7185" />
                <Bar dataKey="news" radius={[8, 8, 0, 0]} fill="#fbbf24" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm text-slate-600">
            <div className="flex items-center gap-3">
              <span className="w-2.5 h-2.5 rounded-full bg-slate-400" />
              <div>
                <p className="font-semibold text-slate-500 uppercase text-[11px] tracking-wide">
                  Tổng trong khoảng
                </p>
                <p className="text-base font-bold text-slate-900">
                  {rangeTotal.toLocaleString('vi-VN')}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
              <div>
                <p className="font-semibold text-slate-500 uppercase text-[11px] tracking-wide">
                  Tin tức
                </p>
                <p className="text-base font-bold text-slate-900">
                  {rangeNewsTotal.toLocaleString('vi-VN')}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
              <div>
                <p className="font-semibold text-slate-500 uppercase text-[11px] tracking-wide">
                  Spam
                </p>
                <p className="text-base font-bold text-slate-900">
                  {rangeSpamTotal.toLocaleString('vi-VN')}
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Details Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pb-12">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-card p-8 rounded-[2.5rem]"
          >
            <h3 className="text-xl font-bold text-slate-800 mb-6">Chi tiết theo loại</h3>
            <div className="space-y-6">
              <ProgressBar 
                label="Tin tức (news)" 
                value={newsTotal.toLocaleString('vi-VN')} 
                percentage={totalPred ? Math.round((newsTotal / totalPred) * 100) : 0} 
                color="bg-emerald-500" 
              />
              <ProgressBar 
                label="Spam" 
                value={spamTotal.toLocaleString('vi-VN')} 
                percentage={totalPred ? Math.round((spamTotal / totalPred) * 100) : 0} 
                color="bg-rose-500" 
              />
              <ProgressBar 
                label="Tổng dự đoán" 
                value={totalPred.toLocaleString('vi-VN')} 
                percentage={100} 
                color="bg-blue-500" 
              />
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-card p-8 rounded-[2.5rem]"
          >
            <h3 className="text-xl font-bold text-slate-800 mb-6">Độ tin cậy TB</h3>
            <div className="space-y-6">
              <ProgressBar 
                label="Độ tin cậy trung bình" 
                value={`${avgConfPercent}%`} 
                percentage={avgConfPercent || 0} 
                color="bg-indigo-500" 
              />
            </div>
          </motion.div>
        </div>
      </div>

      {/* Floating Action Button */}
      <button
        onClick={fetchDashboardData}
        className="fixed bottom-10 right-10 bg-indigo-600 text-white p-5 rounded-full shadow-2xl shadow-indigo-300 hover:bg-indigo-700 transition-all active:scale-95 z-50 group"
      >
        <RefreshCw className="w-6 h-6 group-active:rotate-180 transition-transform duration-500" />
        <span className="absolute right-full mr-4 top-1/2 -translate-y-1/2 bg-slate-900 text-white text-xs px-3 py-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
          Làm mới Bảng điều khiển
        </span>
      </button>
    </div>
  );
}
