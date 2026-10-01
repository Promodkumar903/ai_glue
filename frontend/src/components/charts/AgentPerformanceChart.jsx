import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const data = [
  { name: 'Placed', value: 42, color: '#10b981' },
  { name: 'Interview', value: 135, color: '#3b82f6' },
  { name: 'Shortlisted', value: 310, color: '#f59e0b' },
  { name: 'Rejected', value: 850, color: '#ef4444' },
];

export default function AgentPerformanceChart() {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border">
      <h3 className="font-semibold text-slate-700 mb-4">🎯 Application Status</h3>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
            {data.map((d, i) => <Cell key={i} fill={d.color} />)}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}