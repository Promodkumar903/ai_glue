import React, { useState, useEffect } from 'react';
import { PageHeader, DataTable, Dropdown, Button, Modal, Input, Card, Alert } from '../../components/ui/Components';
import { educationAPI } from '../../services/api';

export default function EducationControl() {
  const [countries, setCountries] = useState([]);
  const [universities, setUniversities] = useState([]);
  const [courses, setCourses] = useState([]);
  const [seats, setSeats] = useState([]);

  const [countryId, setCountryId] = useState('');
  const [univId, setUnivId] = useState('');
  const [courseId, setCourseId] = useState('');

  const [loading, setLoading] = useState({ c: false, u: false, co: false, s: false });
  const [showAddUniv, setShowAddUniv] = useState(false);
  const [showAddCourse, setShowAddCourse] = useState(false);
  const [showAddSeat, setShowAddSeat] = useState(false);
  const [error, setError] = useState('');

  const [newUniv, setNewUniv] = useState({ name: '', country_id: '', city: '', website: '' });
  const [newCourse, setNewCourse] = useState({ name: '', university_id: '', duration_months: '', level: '' });
  const [newSeat, setNewSeat] = useState({ course_id: '', total_seats: '', intake_year: new Date().getFullYear() });

  // Load Countries
  useEffect(() => {
    setLoading((p) => ({ ...p, c: true }));
    educationAPI.countries()
      .then((r) => setCountries(Array.isArray(r.data) ? r.data : r.data?.items || []))
      .catch((e) => setError(e.response?.data?.detail || 'Failed to load countries'))
      .finally(() => setLoading((p) => ({ ...p, c: false })));
  }, []);

  // Load Universities when country changes
  useEffect(() => {
    setUnivId(''); setCourses([]); setSeats([]);
    setLoading((p) => ({ ...p, u: true }));
    educationAPI.universities(countryId)
      .then((r) => setUniversities(Array.isArray(r.data) ? r.data : r.data?.items || []))
      .catch(() => setUniversities([]))
      .finally(() => setLoading((p) => ({ ...p, u: false })));
  }, [countryId]);

  // Load Courses when university changes
  useEffect(() => {
    setCourseId(''); setSeats([]);
    if (!univId) return;
    setLoading((p) => ({ ...p, co: true }));
    educationAPI.courses(univId)
      .then((r) => setCourses(Array.isArray(r.data) ? r.data : r.data?.items || []))
      .catch(() => setCourses([]))
      .finally(() => setLoading((p) => ({ ...p, co: false })));
  }, [univId]);

  // Load Seats when course changes
  useEffect(() => {
    if (!courseId) return;
    setLoading((p) => ({ ...p, s: true }));
    educationAPI.intakeSeats(courseId)
      .then((r) => setSeats(Array.isArray(r.data) ? r.data : r.data?.items || [r.data]))
      .catch(() => setSeats([]))
      .finally(() => setLoading((p) => ({ ...p, s: false })));
  }, [courseId]);

  const handleAddUniv = async () => {
    try {
      await educationAPI.createUniversity(newUniv);
      setShowAddUniv(false);
      setNewUniv({ name: '', country_id: '', city: '', website: '' });
      if (countryId) educationAPI.universities(countryId).then((r) => setUniversities(r.data));
      alert('✅ University added!');
    } catch (e) { alert('❌ ' + (e.response?.data?.detail || e.message)); }
  };

  const handleAddCourse = async () => {
    try {
      await educationAPI.createCourse(newCourse);
      setShowAddCourse(false);
      setNewCourse({ name: '', university_id: '', duration_months: '', level: '' });
      if (univId) educationAPI.courses(univId).then((r) => setCourses(r.data));
      alert('✅ Course added!');
    } catch (e) { alert('❌ ' + (e.response?.data?.detail || e.message)); }
  };

  const handleAddSeat = async () => {
    try {
      await educationAPI.createIntakeSeat(newSeat);
      setShowAddSeat(false);
      setNewSeat({ course_id: '', total_seats: '', intake_year: new Date().getFullYear() });
      if (courseId) educationAPI.intakeSeats(courseId).then((r) => setSeats([r.data]));
      alert('✅ Seat record added!');
    } catch (e) { alert('❌ ' + (e.response?.data?.detail || e.message)); }
  };

  const totalSeats = seats.reduce((s, x) => s + (Number(x.total_seats) || 0), 0);
  const filledSeats = seats.reduce((s, x) => s + (Number(x.filled_seats) || 0), 0);

  return (
    <div className="p-6">
      <PageHeader
        icon="🎓"
        title="Education Control"
        subtitle="Universities, Courses & Seat Availability — Full Control"
        action={
          <>
            <Button variant="outline" onClick={() => setShowAddUniv(true)}>➕ University</Button>
            <Button variant="outline" onClick={() => setShowAddCourse(true)} disabled={!univId}>➕ Course</Button>
            <Button onClick={() => setShowAddSeat(true)} disabled={!courseId}>➕ Intake Seat</Button>
          </>
        }
      />

      {error && <Alert type="danger" onClose={() => setError('')}>{error}</Alert>}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card title="Countries" value={countries.length} icon="🌍" color="blue" />
        <Card title="Universities" value={universities.length} icon="🏛️" color="purple" />
        <Card title="Courses" value={courses.length} icon="📚" color="indigo" />
        <Card title="Seats (Filled / Total)" value={`${filledSeats} / ${totalSeats}`} icon="🪑" color="orange" />
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow p-4 mb-6">
        <h3 className="font-semibold text-gray-700 mb-3">🔽 Filters — Drill Down</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Dropdown
            label="Country"
            value={countryId}
            onChange={setCountryId}
            options={countries.map((c) => ({ value: c.id, label: c.name }))}
            placeholder="All Countries"
            loading={loading.c}
          />
          <Dropdown
            label="University"
            value={univId}
            onChange={setUnivId}
            options={universities.map((u) => ({ value: u.id, label: u.name }))}
            placeholder={countryId ? 'Select University' : 'Select country first'}
            loading={loading.u}
            disabled={!countryId}
          />
          <Dropdown
            label="Course"
            value={courseId}
            onChange={setCourseId}
            options={courses.map((c) => ({ value: c.id, label: c.name }))}
            placeholder={univId ? 'Select Course' : 'Select university first'}
            loading={loading.co}
            disabled={!univId}
          />
        </div>
      </div>

      {/* Seat Table */}
      <h3 className="text-lg font-bold mb-3">🪑 Seat Availability</h3>
      <DataTable
        loading={loading.s}
        empty="Course select karo to seats dikhengi"
        columns={[
          { key: 'course_name', label: 'Course', render: (r) => r.course_name || courses.find((c) => c.id === r.course_id)?.name || '—' },
          { key: 'total_seats', label: 'Total Seats' },
          { key: 'filled_seats', label: 'Filled' },
          {
            key: 'available_seats',
            label: 'Available',
            render: (r) => {
              const avail = (Number(r.total_seats) || 0) - (Number(r.filled_seats) || 0);
              return (
                <span className={`font-bold ${avail > 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                  {avail}
                </span>
              );
            },
          },
          { key: 'intake_year', label: 'Year' },
        ]}
        data={seats}
      />

      {/* Modal: Add University */}
      <Modal open={showAddUniv} onClose={() => setShowAddUniv(false)} title="Add University">
        <Input label="Name" value={newUniv.name} onChange={(v) => setNewUniv({ ...newUniv, name: v })} required />
        <Dropdown
          label="Country"
          value={newUniv.country_id}
          onChange={(v) => setNewUniv({ ...newUniv, country_id: v })}
          options={countries.map((c) => ({ value: c.id, label: c.name }))}
          required
        />
        <Input label="City" value={newUniv.city} onChange={(v) => setNewUniv({ ...newUniv, city: v })} />
        <Input label="Website" value={newUniv.website} onChange={(v) => setNewUniv({ ...newUniv, website: v })} />
        <div className="flex gap-2 mt-4">
          <Button onClick={handleAddUniv} fullWidth>💾 Save University</Button>
          <Button variant="ghost" onClick={() => setShowAddUniv(false)}>Cancel</Button>
        </div>
      </Modal>

      {/* Modal: Add Course */}
      <Modal open={showAddCourse} onClose={() => setShowAddCourse(false)} title="Add Course">
        <Input label="Course Name" value={newCourse.name} onChange={(v) => setNewCourse({ ...newCourse, name: v })} required />
        <Dropdown
          label="University"
          value={newCourse.university_id || univId}
          onChange={(v) => setNewCourse({ ...newCourse, university_id: v })}
          options={universities.map((u) => ({ value: u.id, label: u.name }))}
          required
        />
        <Input label="Duration (months)" type="number" value={newCourse.duration_months} onChange={(v) => setNewCourse({ ...newCourse, duration_months: v })} />
        <Input label="Level (Bachelor/Master/PhD)" value={newCourse.level} onChange={(v) => setNewCourse({ ...newCourse, level: v })} />
        <div className="flex gap-2 mt-4">
          <Button onClick={handleAddCourse} fullWidth>💾 Save Course</Button>
          <Button variant="ghost" onClick={() => setShowAddCourse(false)}>Cancel</Button>
        </div>
      </Modal>

      {/* Modal: Add Seat */}
      <Modal open={showAddSeat} onClose={() => setShowAddSeat(false)} title="Add Intake Seat">
        <Dropdown
          label="Course"
          value={newSeat.course_id || courseId}
          onChange={(v) => setNewSeat({ ...newSeat, course_id: v })}
          options={courses.map((c) => ({ value: c.id, label: c.name }))}
          required
        />
        <Input label="Total Seats" type="number" value={newSeat.total_seats} onChange={(v) => setNewSeat({ ...newSeat, total_seats: v })} required />
        <Input label="Intake Year" type="number" value={newSeat.intake_year} onChange={(v) => setNewSeat({ ...newSeat, intake_year: v })} />
        <div className="flex gap-2 mt-4">
          <Button onClick={handleAddSeat} fullWidth>💾 Save Seats</Button>
          <Button variant="ghost" onClick={() => setShowAddSeat(false)}>Cancel</Button>
        </div>
      </Modal>
    </div>
  );
}