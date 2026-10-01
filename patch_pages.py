import os, shutil

BASE = r'C:\Users\Administrator\ai_glue\frontend\src'

# --- Backup ---
shutil.copy(os.path.join(BASE, 'App.jsx'), os.path.join(BASE, 'App.jsx.bak_pre_pages'))
print('Backup: App.jsx.bak_pre_pages')

# --- 4 naye pages ---
PAGES = {}

PAGES['pages/student/Education.jsx'] = """import React, { useEffect, useState } from 'react';
import { PageHeader } from '../../components/ui/Components';
import api from '../../services/api';

export default function Education() {
  const [countries, setCountries] = useState([]);
  const [unis, setUnis] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([
      api.get('/education/countries'),
      api.get('/education/universities'),
    ]).then(([c, u]) => {
      if (c.status === 'fulfilled') setCountries(Array.isArray(c.value.data) ? c.value.data : []);
      if (u.status === 'fulfilled') setUnis(Array.isArray(u.value.data) ? u.value.data : []);
      setLoading(false);
    });
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader title="Education" subtitle="Countries and universities for study abroad" />
      {loading ? <div className="text-slate-400 py-10 text-center">Loading...</div> : (
        <>
          <h3 className="font-bold text-slate-700 mb-3">Countries ({countries.length})</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
            {countries.map((c) => (
              <div key={c.id} className="bg-white p-4 rounded-xl border border-slate-200">
                <p className="font-bold text-slate-800">{c.name}</p>
                <p className="text-xs text-slate-500">{c.iso_code}</p>
              </div>
            ))}
          </div>
          <h3 className="font-bold text-slate-700 mb-3">Universities ({unis.length})</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {unis.map((u) => (
              <div key={u.id} className="bg-white p-5 rounded-xl border border-slate-200">
                <p className="font-bold text-slate-800">{u.name}</p>
                {u.ranking_global && <p className="text-xs text-slate-500 mt-1">Rank #{u.ranking_global}</p>}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
"""

PAGES['pages/student/Scholarships.jsx'] = """import React from 'react';
import { PageHeader } from '../../components/ui/Components';

export default function Scholarships() {
  const samples = [
    { name: 'DAAD Scholarship', country: 'Germany', amount: 'Full tuition + stipend' },
    { name: 'Chevening Scholarship', country: 'UK', amount: 'Full tuition' },
    { name: 'Fulbright Program', country: 'USA', amount: 'Full tuition + living' },
    { name: 'Vanier Canada', country: 'Canada', amount: 'CAD 50,000/year' },
    { name: 'Australia Awards', country: 'Australia', amount: 'Full tuition' },
  ];
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader title="Scholarships" subtitle="Funding opportunities for study abroad" />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {samples.map((s, i) => (
          <div key={i} className="bg-white p-5 rounded-xl border border-slate-200">
            <p className="font-bold text-slate-800">{s.name}</p>
            <p className="text-sm text-slate-500 mt-1">{s.country}</p>
            <p className="text-sm text-emerald-600 font-medium mt-2">{s.amount}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
"""

PAGES['pages/job-seeker/Offers.jsx'] = """import React, { useEffect, useState } from 'react';
import { PageHeader } from '../../components/ui/Components';
import api from '../../services/api';

export default function Offers() {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/offers/my')
      .then((r) => setOffers(Array.isArray(r.data) ? r.data : []))
      .catch(() => setOffers([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader title="Job Offers" subtitle="Offers received from employers" />
      {loading ? <div className="text-slate-400 py-10 text-center">Loading...</div> : offers.length === 0 ? (
        <div className="text-center py-10 text-slate-400 bg-white rounded-xl border border-slate-200">
          No offers yet
        </div>
      ) : (
        <div className="space-y-3">
          {offers.map((o) => (
            <div key={o.id} className="bg-white p-5 rounded-xl border border-slate-200">
              <p className="font-bold text-slate-800">{o.position || o.title || 'Offer'}</p>
              <p className="text-sm text-slate-500 mt-1">Status: {o.status}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
"""

PAGES['pages/job-seeker/Deals.jsx'] = """import React, { useEffect, useState } from 'react';
import { PageHeader } from '../../components/ui/Components';
import api from '../../services/api';

export default function Deals() {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/deals/my/deals')
      .then((r) => setDeals(Array.isArray(r.data) ? r.data : []))
      .catch(() => setDeals([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader title="Deals" subtitle="Track your job deals and placements" />
      {loading ? <div className="text-slate-400 py-10 text-center">Loading...</div> : deals.length === 0 ? (
        <div className="text-center py-10 text-slate-400 bg-white rounded-xl border border-slate-200">
          No deals yet
        </div>
      ) : (
        <div className="space-y-3">
          {deals.map((d) => (
            <div key={d.id} className="bg-white p-5 rounded-xl border border-slate-200">
              <p className="font-bold text-slate-800">Deal {d.id?.slice(0, 8)}</p>
              <p className="text-sm text-slate-500 mt-1">Status: {d.status}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
"""

for rel, content in PAGES.items():
    full = os.path.join(BASE, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Created: ' + rel)

# --- App.jsx patch ---
app_path = os.path.join(BASE, 'App.jsx')
with open(app_path, 'r', encoding='utf-8') as f:
    app = f.read()

IMPORTS_ANCHOR = "import StudyAbroad from './pages/study-abroad/StudyAbroad';"
NEW_IMPORTS = [
    "import WorkAbroad from './pages/work-abroad/WorkAbroad';",
    "import TrustDirectory from './pages/trust/TrustDirectory';",
    "import StudentEducation from './pages/student/Education';",
    "import StudentLife from './pages/student/StudentLife';",
    "import StudentJourney from './pages/student/Journey';",
    "import StudentScholarships from './pages/student/Scholarships';",
    "import JobSeekerVacancies from './pages/job-seeker/Vacancies';",
    "import JobSeekerInterviews from './pages/job-seeker/Interviews';",
    "import JobSeekerOffers from './pages/job-seeker/Offers';",
    "import JobSeekerDeals from './pages/job-seeker/Deals';",
    "import JobSeekerAccommodation from './pages/job-seeker/Accommodation';",
]

if IMPORTS_ANCHOR in app:
    missing = [i for i in NEW_IMPORTS if i not in app]
    if missing:
        app = app.replace(IMPORTS_ANCHOR, IMPORTS_ANCHOR + '\n' + '\n'.join(missing))
        print('Added %d imports' % len(missing))

ROUTES_ANCHOR = '<Route path="/study-abroad" element={<StudyAbroad />} />'
NEW_ROUTES = [
    '<Route path="/work-abroad" element={<WorkAbroad />} />',
    '<Route path="/trust" element={<TrustDirectory />} />',
    '<Route path="/student/education" element={<StudentEducation />} />',
    '<Route path="/student/life" element={<StudentLife />} />',
    '<Route path="/student/journey" element={<StudentJourney />} />',
    '<Route path="/student/scholarships" element={<StudentScholarships />} />',
    '<Route path="/job-seeker/vacancies" element={<JobSeekerVacancies />} />',
    '<Route path="/job-seeker/interviews" element={<JobSeekerInterviews />} />',
    '<Route path="/job-seeker/offers" element={<JobSeekerOffers />} />',
    '<Route path="/job-seeker/deals" element={<JobSeekerDeals />} />',
    '<Route path="/job-seeker/accommodation" element={<JobSeekerAccommodation />} />',
]

if ROUTES_ANCHOR in app:
    missing = [r for r in NEW_ROUTES if r not in app]
    if missing:
        app = app.replace(ROUTES_ANCHOR, ROUTES_ANCHOR + '\n        ' + '\n        '.join(missing))
        print('Added %d routes' % len(missing))

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app)

print('DONE - All pages created, App.jsx patched')