import React, { useEffect, useState } from 'react';

export const Card = ({ title, value, subtitle, icon, color = 'blue', trend, onClick }) => {
  const colors = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-emerald-500 to-emerald-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600',
    red: 'from-red-500 to-red-600',
    indigo: 'from-indigo-500 to-indigo-600',
    pink: 'from-pink-500 to-pink-600',
    teal: 'from-teal-500 to-teal-600',
    gray: 'from-gray-500 to-gray-600',
  };
  return (
    <div onClick={onClick} className={`bg-gradient-to-br ${colors[color]} rounded-xl p-5 text-white shadow-lg transition-all ${onClick ? 'cursor-pointer hover:scale-[1.03] hover:shadow-xl' : ''}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium opacity-80 uppercase tracking-wide truncate">{title}</p>
          <p className="text-2xl sm:text-3xl font-bold mt-2 truncate">{value ?? '—'}</p>
          {subtitle && <p className="text-xs opacity-75 mt-1 truncate">{subtitle}</p>}
          {trend && <p className={`text-xs mt-2 ${trend > 0 ? 'text-green-200' : 'text-red-200'}`}>{trend > 0 ? '▲' : '▼'} {Math.abs(trend)}%</p>}
        </div>
        {icon && <span className="text-3xl sm:text-4xl opacity-70 ml-2">{icon}</span>}
      </div>
    </div>
  );
};

export const DataTable = ({ columns = [], data = [], loading, empty = 'No data found', onRowClick, compact }) => {
  if (loading) return (
    <div className="bg-white rounded-xl shadow p-10 text-center">
      <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p className="mt-3 text-gray-500 text-sm">Loading...</p>
    </div>
  );
  if (!data?.length) return (
    <div className="bg-white rounded-xl shadow p-10 text-center text-gray-400">
      <p className="text-3xl mb-2">📭</p>
      <p className="text-sm">{empty}</p>
    </div>
  );
  return (
    <div className="overflow-x-auto bg-white rounded-xl shadow">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            {columns.map((c) => (
              <th key={c.key} className={`text-left font-semibold text-gray-600 uppercase text-xs tracking-wider ${compact ? 'px-3 py-2' : 'px-4 py-3'}`} style={{ width: c.width }}>{c.label}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {data.map((row, i) => (
            <tr key={row.id ?? i} onClick={onRowClick ? () => onRowClick(row) : undefined} className={`transition ${onRowClick ? 'cursor-pointer hover:bg-blue-50' : 'hover:bg-gray-50'}`}>
              {columns.map((c) => (
                <td key={c.key} className={compact ? 'px-3 py-2' : 'px-4 py-3'}>
                  {c.render ? c.render(row, i) : (row[c.key] ?? '—')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export const Dropdown = ({ label, value, onChange, options = [], placeholder = 'Select...', loading, disabled, required, hint }) => (
  <div className="mb-3">
    {label && <label className="block text-sm font-medium text-gray-700 mb-1">{label} {required && <span className="text-red-500">*</span>}</label>}
    <select value={value ?? ''} onChange={(e) => onChange(e.target.value)} disabled={loading || disabled} required={required} className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:bg-gray-100 disabled:cursor-not-allowed text-sm">
      <option value="">{loading ? '⏳ Loading...' : placeholder}</option>
      {options.map((o, i) => <option key={o.value ?? o.id ?? i} value={o.value ?? o.id}>{o.label ?? o.name ?? String(o)}</option>)}
    </select>
    {hint && <p className="text-xs text-gray-400 mt-1">{hint}</p>}
  </div>
);

export const Input = ({ label, value, onChange, type = 'text', placeholder, required, error, hint, disabled }) => (
  <div className="mb-3">
    {label && <label className="block text-sm font-medium text-gray-700 mb-1">{label} {required && <span className="text-red-500">*</span>}</label>}
    <input type={type} value={value ?? ''} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} required={required} disabled={disabled} className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none text-sm disabled:bg-gray-100 ${error ? 'border-red-500' : 'border-gray-300'}`} />
    {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
    {hint && !error && <p className="text-xs text-gray-400 mt-1">{hint}</p>}
  </div>
);

export const Textarea = ({ label, value, onChange, placeholder, rows = 4, required }) => (
  <div className="mb-3">
    {label && <label className="block text-sm font-medium text-gray-700 mb-1">{label} {required && <span className="text-red-500">*</span>}</label>}
    <textarea value={value ?? ''} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} rows={rows} required={required} className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none text-sm resize-y" />
  </div>
);

export const Button = ({ children, onClick, variant = 'primary', size = 'md', loading, type = 'button', disabled, icon, fullWidth }) => {
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
    success: 'bg-emerald-600 hover:bg-emerald-700 text-white',
    warning: 'bg-amber-500 hover:bg-amber-600 text-white',
    ghost: 'bg-gray-100 hover:bg-gray-200 text-gray-800',
    outline: 'border border-blue-600 text-blue-600 hover:bg-blue-50',
  };
  const sizes = { sm: 'px-3 py-1.5 text-xs', md: 'px-4 py-2 text-sm', lg: 'px-6 py-3 text-base' };
  return (
    <button type={type} onClick={onClick} disabled={loading || disabled} className={`rounded-lg font-medium transition flex items-center justify-center gap-2 ${variants[variant]} ${sizes[size]} ${loading || disabled ? 'opacity-60 cursor-not-allowed' : ''} ${fullWidth ? 'w-full' : ''}`}>
      {loading ? (<><span className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>Please wait...</>) : (<>{icon && <span>{icon}</span>}{children}</>)}
    </button>
  );
};

export const FileUpload = ({ label, onUpload, accept = '*', hint, loading }) => {
  const [fileName, setFileName] = useState('');
  const handleChange = (e) => {
    const file = e.target.files?.[0];
    if (file) { setFileName(file.name); onUpload(file); }
  };
  return (
    <div className="mb-3">
      {label && <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-blue-500 transition">
        <input type="file" accept={accept} onChange={handleChange} disabled={loading} className="hidden" id={`file-${label}`} />
        <label htmlFor={`file-${label}`} className="cursor-pointer">
          <p className="text-3xl mb-1">📎</p>
          <p className="text-sm text-gray-600">{loading ? '⏳ Uploading...' : fileName || 'Click to upload or drag & drop'}</p>
          {hint && <p className="text-xs text-gray-400 mt-1">{hint}</p>}
        </label>
      </div>
    </div>
  );
};

export const Alert = ({ type = 'info', title, children, onClose }) => {
  const styles = {
    info: 'bg-blue-50 border-blue-400 text-blue-800',
    warning: 'bg-amber-50 border-amber-400 text-amber-800',
    danger: 'bg-red-50 border-red-400 text-red-800',
    success: 'bg-emerald-50 border-emerald-400 text-emerald-800',
  };
  const icons = { info: 'ℹ️', warning: '⚠️', danger: '🚨', success: '✅' };
  return (
    <div className={`border-l-4 p-3 rounded-lg mb-3 flex gap-2 items-start ${styles[type]}`}>
      <span className="text-lg">{icons[type]}</span>
      <div className="flex-1">
        {title && <p className="font-semibold text-sm">{title}</p>}
        <div className="text-sm">{children}</div>
      </div>
      {onClose && <button onClick={onClose} className="text-lg opacity-60 hover:opacity-100">✕</button>}
    </div>
  );
};

export const PageHeader = ({ title, subtitle, action, icon, image }) => {
  // ✅ Agar image pass hui hai → Hero jaisa photo banner
  if (image) {
    return (
      <div className="relative rounded-2xl overflow-hidden mb-6 shadow-xl">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url('${image}')` }}
        />
        <div className="absolute inset-0 bg-gradient-to-r from-slate-900/90 via-slate-900/70 to-transparent" />
        <div className="relative p-8 md:p-10">
          <h1 className="text-2xl md:text-3xl font-bold text-white flex items-center gap-2">
            {icon && <span>{icon}</span>}{title}
          </h1>
          {subtitle && <p className="text-slate-200 mt-2 text-sm md:text-base">{subtitle}</p>}
          {action && <div className="mt-4 flex gap-2 flex-wrap">{action}</div>}
        </div>
      </div>
    );
  }

  // ✅ Agar image nahi hai → purana simple design
  return (
    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-6 pb-4 border-b border-gray-200">
      <div>
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          {icon && <span>{icon}</span>}{title}
        </h1>
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
      </div>
      {action && <div className="flex gap-2 flex-wrap">{action}</div>}
    </div>
  );
};

export const Modal = ({ open, onClose, title, children, size = 'md' }) => {
  useEffect(() => {
    if (open) document.body.style.overflow = 'hidden';
    else document.body.style.overflow = 'auto';
    return () => { document.body.style.overflow = 'auto'; };
  }, [open]);
  if (!open) return null;
  const sizes = { sm: 'max-w-md', md: 'max-w-lg', lg: 'max-w-2xl', xl: 'max-w-4xl' };
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className={`bg-white rounded-xl w-full ${sizes[size]} max-h-[90vh] overflow-y-auto shadow-2xl`}>
        <div className="flex justify-between items-center p-4 border-b sticky top-0 bg-white z-10">
          <h2 className="text-lg font-bold text-gray-800">{title}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-red-500 text-2xl leading-none">✕</button>
        </div>
        <div className="p-5">{children}</div>
      </div>
    </div>
  );
};

export const Badge = ({ children, color = 'gray', size = 'md' }) => {
  const colors = {
    gray: 'bg-gray-100 text-gray-700',
    blue: 'bg-blue-100 text-blue-700',
    green: 'bg-emerald-100 text-emerald-700',
    red: 'bg-red-100 text-red-700',
    yellow: 'bg-amber-100 text-amber-700',
    purple: 'bg-purple-100 text-purple-700',
    indigo: 'bg-indigo-100 text-indigo-700',
  };
  const sizes = { sm: 'px-2 py-0.5 text-xs', md: 'px-2.5 py-1 text-xs' };
  return <span className={`inline-block rounded-full font-medium ${colors[color]} ${sizes[size]}`}>{children}</span>;
};

export const EmptyState = ({ icon = '📭', title = 'No data', subtitle, action }) => (
  <div className="text-center py-12 px-4">
    <p className="text-5xl mb-3">{icon}</p>
    <h3 className="text-lg font-semibold text-gray-700">{title}</h3>
    {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
    {action && <div className="mt-4">{action}</div>}
  </div>
);

export const ProgressBar = ({ value = 0, max = 100, color = 'blue', label }) => {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const colors = { blue: 'bg-blue-500', green: 'bg-emerald-500', red: 'bg-red-500', yellow: 'bg-amber-500' };
  return (
    <div>
      {label && <div className="flex justify-between text-xs text-gray-600 mb-1"><span>{label}</span><span>{value}/{max}</span></div>}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div className={`${colors[color]} h-2 rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
};

export const Tabs = ({ tabs = [], active, onChange }) => (
  <div className="border-b border-gray-200 mb-4 overflow-x-auto">
    <div className="flex gap-1 min-w-max">
      {tabs.map((t) => (
        <button key={t.id} onClick={() => onChange(t.id)} className={`px-4 py-2 text-sm font-medium border-b-2 transition whitespace-nowrap ${active === t.id ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>
          {t.icon && <span className="mr-1">{t.icon}</span>}
          {t.label}
          {t.count !== undefined && <span className="ml-2 text-xs bg-gray-100 px-1.5 py-0.5 rounded-full">{t.count}</span>}
        </button>
      ))}
    </div>
  </div>
);

export const SearchBar = ({ value, onChange, placeholder = 'Search...', onSearch }) => (
  <div className="relative mb-3">
    <input type="text" value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} onKeyDown={(e) => e.key === 'Enter' && onSearch?.()} className="w-full border border-gray-300 rounded-lg pl-10 pr-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none text-sm" />
    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
  </div>
);