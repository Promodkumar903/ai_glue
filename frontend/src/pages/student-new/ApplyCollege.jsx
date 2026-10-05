import React, { useState, useEffect } from 'react';
import { PageHeader, Card, Dropdown, Button, Alert, Badge, Input } from '../../components/ui/Components';
import { educationAPI, applicationsAPI, aiAPI } from '../../services/api';

const safeArr = (v) => {
  if (Array.isArray(v)) return v;
  if (v && typeof v === 'object') {
    if (Array.isArray(v.items)) return v.items;
    if (Array.isArray(v.data)) return v.data;
  }
  return [];
};
const safeStr = (v, fb = '—') => (v == null || v === '') ? fb : String(v);

export default function ApplyCollege() {
  const [step, setStep] = useState(1);
  const [countries, setCountries] = useState([]);
  const [universities, setUniversities] = useState([]);
  const [courses, setCourses] = useState([]);
  const [seats, setSeats] = useState([]);
  const [aiInfo, setAiInfo] = useState(null);

  const [countryId, setCountryId] = useState('');
  const [customCountry, setCustomCountry] = useState('');   // manual country
  const [univId, setUnivId] = useState('');
  const [courseId, setCourseId] = useState('');
  const [notes, setNotes] = useState('');

  const [msg, setMsg] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState({ c: false, u: false, co: false, s: false, ai: false });
  const [unisFromAI, setUnisFromAI] = useState(false);
  const [coursesFromAI, setCoursesFromAI] = useState(false);

  // Fetch countries from DB
  useEffect(() => {
    setLoading((p) => ({ ...p, c: true }));
    educationAPI.countries()
      .then((r) => setCountries(safeArr(r.data)))
      .catch(() => setCountries([]))
      .finally(() => setLoading((p) => ({ ...p, c: false })));
  }, []);

  // Country changed → fetch universities
  useEffect(() => {
    if (!countryId && !customCountry) return;
    setUnivId(''); setCourses([]); setSeats([]); setAiInfo(null); setUnisFromAI(false);
    setLoading((p) => ({ ...p, u: true }));

    const isCustom = countryId === 'OTHER';

    if (isCustom) {
      // AI se universities
      aiAPI.universitiesByCountry(customCountry)
        .then((r) => {
          const aiUnis = safeArr(r.data?.universities).map((u, i) => ({
            id: `ai-u-${i}-${Date.now()}`,
            name: u.name,
            _ai: true,
            _details: u,
          }));
          setUniversities(aiUnis);
          setUnisFromAI(true);
          setAiInfo(r.data);
        })
        .catch(() => setUniversities([]))
        .finally(() => setLoading((p) => ({ ...p, u: false })));
    } else {
      // DB se universities
      educationAPI.universities(countryId)
        .then((r) => {
          const dbUnis = safeArr(r.data);
          if (dbUnis.length > 0) {
            setUniversities(dbUnis);
            setUnisFromAI(false);
          } else {
            setUniversities([]);
          }
        })
        .catch(() => setUniversities([]))
        .finally(() => setLoading((p) => ({ ...p, u: false })));
    }
  }, [countryId, customCountry]);

  // University changed → fetch courses
  useEffect(() => {
    if (!univId) return;
    setCourseId(''); setSeats([]); setAiInfo(null); setCoursesFromAI(false);
    setLoading((p) => ({ ...p, co: true }));

    const isAiUniv = univId.startsWith('ai-');

    if (isAiUniv) {
      fetchCoursesFromAI();
      return;
    }

    educationAPI.courses(univId)
      .then((r) => {
        const dbCourses = safeArr(r.data);
        if (dbCourses.length > 0) {
          setCourses(dbCourses);
          setCoursesFromAI(false);
          setLoading((p) => ({ ...p, co: false }));
        } else {
          fetchCoursesFromAI();
        }
      })
      .catch(() => fetchCoursesFromAI());
  }, [univId]);

  const fetchCoursesFromAI = async () => {
    setLoading((p) => ({ ...p, ai: true }));
    try {
      const countryName = countryId === 'OTHER'
        ? customCountry
        : countries.find((c) => String(c.id) === String(countryId))?.name || '';
      const univName = universities.find((u) => String(u.id) === String(univId))?.name || '';

      const res = await aiAPI.universityInfo({
        country: countryName,
        university: univName,
        course: '',
      });

      const aiCourses = safeArr(res.data?.courses).map((c, i) => ({
        id: `ai-${i}-${Date.now()}`,
        name: c.name || 'Course',
        _ai: true,
        _details: c,
      }));

      setCourses(aiCourses);
      setAiInfo(res.data);
      setCoursesFromAI(true);
    } catch (e) {
      console.error('AI fetch failed:', e);
      setCourses([]);
    } finally {
      setLoading((p) => ({ ...p, co: false, ai: false }));
    }
  };

  // Course changed → seats (sirf DB courses ke liye)
  useEffect(() => {
    if (!courseId) return;
    if (courseId.startsWith('ai-')) {
      setSeats([]);
      return;
    }
    setLoading((p) => ({ ...p, s: true }));
    educationAPI.intakeSeats(courseId)
      .then((r) => setSeats(safeArr(r.data)))
      .catch(() => setSeats([]))
      .finally(() => setLoading((p) => ({ ...p, s: false })));
  }, [courseId]);

  const handleSubmit = async () => {
    if (!courseId) return;
    setSubmitting(true);
    try {
      await applicationsAPI.create({
        opportunity_id: courseId,
        type: 'COLLEGE',
        notes,
      });
      setMsg({ type: 'success', text: '✅ Application submitted successfully!' });
      setStep(4);
    } catch (e) {
      setMsg({ type: 'danger', text: '❌ ' + (e.response?.data?.detail || e.message) });
    } finally { setSubmitting(false); }
  };

  const selectedCountry = countryId === 'OTHER'
    ? { name: customCountry }
    : countries.find((c) => String(c.id) === String(countryId));
  const selectedUniv = universities.find((u) => String(u.id) === String(univId));
  const selectedCourse = courses.find((c) => String(c.id) === String(courseId));
  const availableSeats = seats.reduce((s, x) => s + (Number(x.total_seats || 0) - Number(x.filled_seats || 0)), 0);

  return (
    <div className="p-6">
      <PageHeader
        icon="🎓"
        title="Apply to College"
        subtitle="Choose country → university → course → apply"
        image="https://images.unsplash.com/photo-1607237138185-eedd9c632b0b?w=1600&q=80"
      />

      {msg && <Alert type={msg.type} onClose={() => setMsg(null)}>{msg.text}</Alert>}

      {/* Progress Steps */}
      <div className="bg-white rounded-xl shadow p-4 mb-6">
        <div className="flex justify-between items-center">
          {['Country', 'University', 'Course', 'Applied'].map((label, i) => (
            <div key={label} className="flex-1 flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                step > i ? 'bg-emerald-500 text-white' : step === i + 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'
              }`}>
                {step > i + 1 ? '✓' : i + 1}
              </div>
              <span className={`ml-2 text-sm ${step >= i + 1 ? 'text-gray-800 font-medium' : 'text-gray-400'}`}>{label}</span>
              {i < 3 && <div className={`flex-1 h-0.5 mx-2 ${step > i + 1 ? 'bg-emerald-500' : 'bg-gray-200'}`} />}
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left: Form */}
        <div className="md:col-span-2 bg-white rounded-xl shadow p-6">
          <Dropdown
            label="1. Select Country"
            value={countryId}
            onChange={(v) => { setCountryId(v); setStep(2); }}
            options={[
              ...countries.map((c) => ({ value: c.id, label: c.name })),
              { value: 'OTHER', label: '🌍 Other (type manually)' },
            ]}
            loading={loading.c}
            placeholder="Choose a country..."
          />

          {countryId === 'OTHER' && (
            <Input
              label="Type country name"
              value={customCountry}
              onChange={setCustomCountry}
              placeholder="e.g. Portugal, Sweden, Japan..."
            />
          )}

          {countryId && (countryId !== 'OTHER' || customCountry) && (
            <>
              <Dropdown
                label="2. Select University"
                value={univId}
                onChange={(v) => { setUnivId(v); setStep(3); }}
                options={universities.map((u) => ({ value: u.id, label: u.name }))}
                loading={loading.u || loading.ai}
                placeholder={loading.ai ? 'AI se universities laa rahe hain...' : unisFromAI ? 'AI se universities' : 'Choose university...'}
              />

              {unisFromAI && (
                <div className="mb-3 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800">
                  ⚡ <strong>AI-generated universities</strong> — verify on official websites.
                </div>
              )}
            </>
          )}

          {univId && (
            <>
              <Dropdown
                label="3. Select Course"
                value={courseId}
                onChange={setCourseId}
                options={courses.map((c) => ({ value: c.id, label: c.name }))}
                loading={loading.co || loading.ai}
                placeholder={loading.ai ? 'AI se courses laa rahe hain...' : coursesFromAI ? 'AI se courses (select karo)' : 'Choose course...'}
              />

              {coursesFromAI && (
                <div className="mb-3 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800">
                  ⚡ <strong>AI-generated courses</strong> — verify before applying.
                </div>
              )}
            </>
          )}

          {courseId && (
            <>
              <Input
                label="Additional Notes (optional)"
                value={notes}
                onChange={setNotes}
                placeholder="Any specific requirements..."
              />
              <div className="flex gap-2 mt-4">
                <Button onClick={handleSubmit} loading={submitting} fullWidth>📨 Submit Application</Button>
                <Button variant="ghost" onClick={() => { setStep(1); setCountryId(''); setCustomCountry(''); setUnivId(''); setCourseId(''); setAiInfo(null); }}>Reset</Button>
              </div>
            </>
          )}

          {aiInfo?.ai_insights && (
            <div className="mt-6 p-4 bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl border border-purple-200">
              <h4 className="font-bold text-purple-900 mb-2 flex items-center gap-2">✨ AI Insights</h4>
              <p className="text-sm text-purple-800 leading-relaxed">{aiInfo.ai_insights}</p>
            </div>
          )}
        </div>

        {/* Right: Summary */}
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="font-bold mb-4">📋 Application Summary</h3>
          <div className="space-y-3 text-sm">
            <div>
              <p className="text-xs text-gray-500">Country</p>
              <p className="font-medium">{safeStr(selectedCountry?.name, 'Not selected')}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">University</p>
              <p className="font-medium">{safeStr(selectedUniv?.name, 'Not selected')}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Course</p>
              <p className="font-medium">{safeStr(selectedCourse?.name, 'Not selected')}</p>
            </div>

            {aiInfo?.university_info && (
              <div className="pt-3 border-t space-y-2">
                <p className="text-xs font-semibold text-gray-500">UNIVERSITY INFO (AI)</p>
                {aiInfo.university_info.ranking && (
                  <p className="text-xs"><span className="text-gray-500">Ranking:</span> {aiInfo.university_info.ranking}</p>
                )}
                {aiInfo.university_info.location && (
                  <p className="text-xs"><span className="text-gray-500">Location:</span> {aiInfo.university_info.location}</p>
                )}
                {aiInfo.university_info.established && (
                  <p className="text-xs"><span className="text-gray-500">Established:</span> {aiInfo.university_info.established}</p>
                )}
              </div>
            )}

            {courseId && seats.length > 0 && (
              <div className="pt-3 border-t">
                <p className="text-xs text-gray-500">Seats Available</p>
                <p className={`text-2xl font-bold ${availableSeats > 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                  {availableSeats}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}