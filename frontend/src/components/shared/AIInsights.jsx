import { Sparkles } from 'lucide-react';

export default function AIInsights({ insights = [] }) {
  const defaultInsights = [
    { title: 'Your residence permit expires in 42 days.', action: 'Renew Now', priority: 'high' },
    { title: 'New housing available near TUM campus', action: 'View', priority: 'medium' },
    { title: 'Book required for next semester', action: 'Buy', priority: 'low' },
  ];
  const data = insights.length > 0 ? insights : defaultInsights;

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 shadow-sm">
      <div className="flex items-center gap-2 mb-2">
        <Sparkles className="w-5 h-5 text-blue-600" />
        <h3 className="font-semibold text-blue-800 text-sm">🧠 AI Glue Insights</h3>
      </div>
      <ul className="space-y-2">
        {data.map((item, idx) => (
          <li key={idx} className="flex items-center justify-between text-sm text-gray-700">
            <span className="flex items-center gap-2">
              <span className={`w-1.5 h-1.5 rounded-full ${item.priority === 'high' ? 'bg-red-500' : item.priority === 'medium' ? 'bg-yellow-500' : 'bg-blue-400'}`} />
              {item.title}
            </span>
            {item.action && (
              <button className="text-xs font-medium text-blue-600 hover:underline bg-white px-2 py-1 rounded shadow-sm">
                {item.action}
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}