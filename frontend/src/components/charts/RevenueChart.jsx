import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { month: 'Jan', revenue: 1200 },
  { month: 'Feb', revenue: 1900 },
  { month: 'Mar', revenue: 2400 },
  { month: 'Apr', revenue: 2210 },
  { month: 'May', revenue: 3290 },
  { month: 'Jun', revenue: 4100 },
];

export default function RevenueChart() {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border">
      <h3 className="font-semibold text-slate-700 mb-4">📈 Revenue Trend</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} />
          <YAxis stroke="#94a3b8" fontSize={12} />
          <Tooltip />
          <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={3} dot={{ r: 5 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}