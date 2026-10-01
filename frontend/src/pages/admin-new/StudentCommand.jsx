import React, { useState, useEffect } from 'react';
import { PageHeader, Card, DataTable, Badge, Tabs, Alert } from '../../components/ui/Components';
import { adminAPI, educationAPI, studentLifeAPI } from '../../services/api';

export default function StudentCommand() {
  const [tab, setTab] = useState('overview');
  const [users, setUsers] = useState([]);
  const [universities, setUniversities] = useState([]);
  const [books, setBooks] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    Promise.allSettled([
      adminAPI.users(),
      educationAPI.universities(),
      studentLifeAPI.books(),
      studentLifeAPI.jobs(),
    ]).then(([u, univ, b, j]) => {
      if (u.status === 'fulfilled') {
               const all = Array.isArray(u.value.data) ? u.value.data : u.value.data?.items || [];
        setUsers(all.filter((x) => {
          const roles = Array.isArray(x.roles) ? x.roles : (x.role ? [x.role] : []);
          return roles.map((r) => String(r).toUpperCase()).includes('STUDENT');
        }));
      }
      if (univ.status === 'fulfilled') {
        setUniversities(Array.isArray(univ.value.data) ? univ.value.data : univ.value.data?.items || []);
      }
      if (b.status === 'fulfilled') {
        setBooks(Array.isArray(b.value.data) ? b.value.data : b.value.data?.items || []);
      }
      if (j.status === 'fulfilled') {
        setJobs(Array.isArray(j.value.data) ? j.value.data : j.value.data?.items || []);
      }
      if (u.status === 'rejected') setError(u.reason?.response?.data?.detail || 'Failed to load');
      setLoading(false);
    });
  }, []);

  const totalStudents = users.length;

  return (
    <div className="p-6">
      <PageHeader
        icon="🎓"
        title="Student Command Center"
        subtitle="Students, Universities, Books & Campus Life — Full Control"
        image="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1600&q=80"
      />

      {error && <Alert type="danger" title="API Error">{error}</Alert>}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Total Students" value={totalStudents} icon="👥" color="blue" />
        <Card title="Universities" value={universities.length} icon="🏛️" color="purple" />
        <Card title="Books in Library" value={books.length} icon="📚" color="indigo" />
        <Card title="Part-Time Jobs" value={jobs.length} icon="💼" color="orange" />
      </div>

      <Tabs
        active={tab}
        onChange={setTab}
        tabs={[
          { id: 'overview', label: 'Overview', icon: '📊' },
          { id: 'students', label: 'All Students', icon: '👥', count: totalStudents },
          { id: 'universities', label: 'Universities', icon: '🏛️', count: universities.length },
          { id: 'books', label: 'Books', icon: '📚', count: books.length },
          { id: 'jobs', label: 'Part-Time Jobs', icon: '💼', count: jobs.length },
        ]}
      />

      {/* Overview */}
      {tab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl shadow p-5">
            <h3 className="font-bold mb-3">🌍 Top Universities</h3>
            {universities.slice(0, 5).map((u, i) => (
              <div key={u.id ?? i} className="flex justify-between py-2 border-b last:border-0">
                <span className="text-sm">{u.name}</span>
                <Badge color="blue">{u.city || 'N/A'}</Badge>
              </div>
            ))}
            {universities.length === 0 && <p className="text-sm text-gray-400">No universities yet</p>}
          </div>

          <div className="bg-white rounded-xl shadow p-5">
            <h3 className="font-bold mb-3">📚 Recent Books</h3>
            {books.slice(0, 5).map((b, i) => (
              <div key={b.id ?? i} className="flex justify-between py-2 border-b last:border-0">
                <span className="text-sm">{b.title}</span>
                <Badge color={b.status === 'available' ? 'green' : 'yellow'}>{b.status || 'N/A'}</Badge>
              </div>
            ))}
            {books.length === 0 && <p className="text-sm text-gray-400">No books yet</p>}
          </div>
        </div>
      )}

      {/* Students */}
      {tab === 'students' && (
        <DataTable
          loading={loading}
          empty="No students registered yet"
          columns={[
            { key: 'full_name', label: 'Name', render: (r) => r.full_name || '—' },
            { key: 'email', label: 'Email' },
            { key: 'country', label: 'Country', render: (r) => r.country || '—' },
            { key: 'status', label: 'Status', render: (r) => <Badge color={r.status === 'active' ? 'green' : 'gray'}>{r.status || 'active'}</Badge> },
            { key: 'created_at', label: 'Joined', render: (r) => r.created_at ? new Date(r.created_at).toLocaleDateString() : '—' },
          ]}
          data={users}
        />
      )}

      {/* Universities */}
      {tab === 'universities' && (
        <DataTable
          loading={loading}
          empty="No universities — Education Control se add karo"
          columns={[
            { key: 'name', label: 'University' },
            { key: 'city', label: 'City', render: (r) => r.city || '—' },
            { key: 'country_id', label: 'Country ID', render: (r) => r.country_id || '—' },
            { key: 'website', label: 'Website', render: (r) => r.website ? <a href={r.website} target="_blank" rel="noreferrer" className="text-blue-600 underline">Visit</a> : '—' },
          ]}
          data={universities}
        />
      )}

      {/* Books */}
      {tab === 'books' && (
        <DataTable
          loading={loading}
          empty="No books in library"
          columns={[
            { key: 'title', label: 'Title' },
            { key: 'author', label: 'Author', render: (r) => r.author || '—' },
            { key: 'status', label: 'Status', render: (r) => <Badge color={r.status === 'available' ? 'green' : 'yellow'}>{r.status || 'N/A'}</Badge> },
          ]}
          data={books}
        />
      )}

      {/* Part-Time Jobs */}
      {tab === 'jobs' && (
        <DataTable
          loading={loading}
          empty="No part-time jobs posted"
          columns={[
            { key: 'title', label: 'Job Title' },
            { key: 'company', label: 'Company', render: (r) => r.company || '—' },
            { key: 'city', label: 'City', render: (r) => r.city || '—' },
            { key: 'salary', label: 'Salary', render: (r) => r.salary || '—' },
          ]}
          data={jobs}
        />
      )}
    </div>
  );
}