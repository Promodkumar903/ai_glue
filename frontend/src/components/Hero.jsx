export default function Hero({ title, subtitle, imageUrl, children }) {
  return (
    <div className="relative rounded-2xl overflow-hidden mb-6 shadow-xl">
      {/* Background Image */}
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: `url('${imageUrl}')` }}
      />
      {/* Dark Overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-slate-900/90 via-slate-900/70 to-transparent" />
      
      {/* Content */}
      <div className="relative p-8 md:p-10">
        <h1 className="text-2xl md:text-3xl font-bold text-white">{title}</h1>
        <p className="text-slate-200 mt-2 text-sm md:text-base">{subtitle}</p>
        {children && <div className="mt-4">{children}</div>}
      </div>
    </div>
  );
}