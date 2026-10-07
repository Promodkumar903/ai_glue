"""
AI GLUE — CRM Engine
Leads, Documents, Activities, Dashboard
"""
import uuid
from datetime import datetime, timedelta
import core.db_compat as sqlite3


def _now():
    return datetime.utcnow().isoformat()


def _uid():
    return str(uuid.uuid4())


class CRMEngine:

    # ---------------- LEADS ----------------

    @staticmethod
    def create_lead(agent_id, data):
        lead_id = _uid()
        now = _now()
        conn = sqlite3.connect('ai_glue.db')
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO leads (
                id, agent_id, student_name, email, phone, country, course,
                budget, intake, source, stage, priority, notes,
                next_followup, last_contacted, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lead_id, agent_id,
            data.get('student_name'),
            data.get('email'),
            data.get('phone'),
            data.get('country'),
            data.get('course'),
            data.get('budget'),
            data.get('intake'),
            data.get('source', 'manual'),
            data.get('stage', 'NEW'),
            data.get('priority', 'MEDIUM'),
            data.get('notes'),
            data.get('next_followup'),
            None,
            now, now
        ))
        # log activity
        cur.execute("""
            INSERT INTO lead_activities (id, lead_id, activity_type, description, actor_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (_uid(), lead_id, 'CREATED', f"Lead created: {data.get('student_name')}", agent_id, now))
        conn.commit()
        conn.close()
        return {"status": "created", "id": lead_id}

    @staticmethod
    def get_leads(agent_id, filters=None):
        filters = filters or {}
        conn = sqlite3.connect('ai_glue.db')
        cur = conn.cursor()
        q = "SELECT id, agent_id, student_name, email, phone, country, course, budget, intake, source, stage, priority, notes, next_followup, last_contacted, converted_to_user_id, created_at, updated_at FROM leads WHERE agent_id = ?"
        params = [agent_id]
        if filters.get('stage'):
            q += " AND stage = ?"
            params.append(filters['stage'])
        if filters.get('priority'):
            q += " AND priority = ?"
            params.append(filters['priority'])
        if filters.get('country'):
            q += " AND country = ?"
            params.append(filters['country'])
        if filters.get('search'):
            q += " AND (student_name LIKE ? OR email LIKE ? OR phone LIKE ?)"
            s = f"%{filters['search']}%"
            params.extend([s, s, s])
        q += " ORDER BY created_at DESC LIMIT 200"
        cur.execute(q, tuple(params))
        rows = cur.fetchall()
        conn.close()
        cols = ['id','agent_id','student_name','email','phone','country','course','budget','intake','source','stage','priority','notes','next_followup','last_contacted','converted_to_user_id','created_at','updated_at']
        return [dict(zip(cols, r)) for r in rows]

    @staticmethod
    def get_lead(lead_id, agent_id):
        conn = sqlite3.connect('ai_glue.db')
        cur = conn.cursor()
        cur.execute("SELECT id, agent_id, student_name, email, phone, country, course, budget, intake, source, stage, priority, notes, next_followup, last_contacted, converted_to_user_id, created_at, updated_at FROM leads WHERE id = ? AND agent_id = ?", (lead_id, agent_id))
        row = cur.fetchone()
        if not row:
            conn.close()
            return None
        cols = ['id','agent_id','student_name','email','phone','country','course','budget','intake','source','stage','priority','notes','next_followup','last_contacted','converted_to_user_id','created_at','updated_at']
        lead = dict(zip(cols, row))
        # documents
        cur.execute("SELECT id, document_type, document_name, file_url, status, uploaded_at, verified_at, verified_by, rejection_reason FROM lead_documents WHERE lead_id = ?", (lead_id,))
        docs = cur.fetchall()
        dcols = ['id','document_type','document_name','file_url','status','uploaded_at','verified_at','verified_by','rejection_reason']
        lead['documents'] = [dict(zip(dcols, d)) for d in docs]
        # activities
        cur.execute("SELECT id, activity_type, description, actor_id, created_at FROM lead_activities WHERE lead_id = ? ORDER BY created_at DESC LIMIT 50", (lead_id,))
        acts = cur.fetchall()
        acols = ['id','activity_type','description','actor_id','created_at']
        lead['activities'] = [dict(zip(acols, a)) for a in acts]
        conn.close()
        return lead

    @staticmethod
    def update_lead(lead_id, agent_id, data):
        allowed = ['student_name','email','phone','country','course','budget','intake','source','stage','priority','notes','next_followup']
        sets = []
        params = []
        for k in allowed:
            if k in data:
                sets.append(f"{k} = ?")
                params.append(data[k])
        if not sets:
            return {"status": "no_change"}
        sets.append("updated_at = ?")
        params.append(_now())
        params.extend([lead_id, agent_id])
        conn = sqlite3.connect('ai_glue.db')
        cur = conn.cursor()
        cur.execute(f"UPDATE leads SET {', '.join(sets)} WHERE id = ? AND agent_id = ?", tuple(params))
        conn.commit()
        conn.close()
        return {"status": "updated", "id": lead_id}

    @staticmethod
    def change_stage(lead_id, agent_id, new_stage):
        now = _now()
        conn = sqlite3.connect('ai_glue.db')
        cur = conn.cursor()
        cur.execute("SELECT stage, student_name FROM leads WHERE id = ? AND agent_id = ?", (lead_id, agent_id))
        row = cur.fetchone()
        if not row:
            conn.close()
            return {"status": "not_found"}
        old_stage, name = row
        cur.execute("UPDATE leads SET stage = ?, updated_at = ? WHERE id = ?", (new_stage, now, lead_id))
        cur.execute("""
            INSERT INTO lead_activities (id, lead_id, activity_type, description, actor_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (_uid(), lead_id, 'STAGE_CHANGE', f"{old_stage} → {new_stage}", agent_id, now))
        conn.commit()
        conn.close()
        return {"status": "ok", "from": old_stage, "to": new_stage}

    @staticmethod
    def add_note(lead_id, agent_id, note):
        now = _now()
        conn = sqlite3.connect('ai_glue.db')
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO lead_activities (id, lead_id, activity_type, description, actor_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (_uid(), lead_id, 'NOTE', note, agent_id, now))
        cur.execute("UPDATE leads SET last_contacted = ?, updated_at = ? WHERE id = ?", (now, now, lead_id))
        conn.commit()
        conn.close()
        return {"status": "ok"}

    @staticmethod
    def convert_to_student(lead_id, agent_id, user_id):
        now = _now()
        conn = sqlite3.connect('ai_glue.db')
        cur = conn.cursor()
        cur.execute("UPDATE leads SET stage = 'ENROLLED', converted_to_user_id = ?, updated_at = ? WHERE id = ? AND agent_id = ?", (user_id, now, lead_id, agent_id))
        cur.execute("""
            INSERT INTO lead_activities (id, lead_id, activity_type, description, actor_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (_uid(), lead_id, 'CONVERTED', f"Converted to user: {user_id}", agent_id, now))
        conn.commit()
        conn.close()
        return {"status": "converted", "user_id": user_id}

    # ---------------- DOCUMENTS ----------------

    @staticmethod
    def add_document(lead_id, doc_type, doc_name, file_url=None):
        doc_id = _uid()
        now = _now()
        conn = sqlite3.connect('ai_glue.db')
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO lead_documents (id, lead_id, document_type, document_name, file_url, status, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (doc_id, lead_id, doc_type, doc_name, file_url, 'UPLOADED' if file_url else 'MISSING', now if file_url else None))
        conn.commit()
        conn.close()
        return {"status": "ok", "id": doc_id}

    @staticmethod
    def update_document_status(doc_id, status, agent_id, reason=None):
        now = _now()
        conn = sqlite3.connect('ai_glue.db')
        cur = conn.cursor()
        if status == 'VERIFIED':
            cur.execute("UPDATE lead_documents SET status = ?, verified_at = ?, verified_by = ? WHERE id = ?", (status, now, agent_id, doc_id))
        elif status == 'REJECTED':
            cur.execute("UPDATE lead_documents SET status = ?, rejection_reason = ? WHERE id = ?", (status, reason or '', doc_id))
        else:
            cur.execute("UPDATE lead_documents SET status = ? WHERE id = ?", (status, doc_id))
        conn.commit()
        conn.close()
        return {"status": "ok"}

    # ---------------- DASHBOARD ----------------

    @staticmethod
    def get_dashboard(agent_id):
        conn = sqlite3.connect('ai_glue.db')
        cur = conn.cursor()
        # counts by stage
        cur.execute("SELECT stage, COUNT(*) FROM leads WHERE agent_id = ? GROUP BY stage", (agent_id,))
        stages = {row[0]: row[1] for row in cur.fetchall()}
        total = sum(stages.values())
        # today's follow-ups
        today = datetime.utcnow().date().isoformat()
        cur.execute("SELECT id, student_name, phone, country, course, priority, next_followup FROM leads WHERE agent_id = ? AND next_followup LIKE ? ORDER BY next_followup ASC", (agent_id, f"{today}%"))
        followups = []
        for r in cur.fetchall():
            followups.append({
                'id': r[0], 'student_name': r[1], 'phone': r[2],
                'country': r[3], 'course': r[4], 'priority': r[5], 'next_followup': r[6]
            })
        # overdue
        cur.execute("SELECT COUNT(*) FROM leads WHERE agent_id = ? AND next_followup IS NOT NULL AND next_followup < ? AND stage NOT IN ('ENROLLED','LOST')", (agent_id, today))
        overdue = cur.fetchone()[0]
        # docs missing
        cur.execute("""
            SELECT COUNT(DISTINCT l.id) FROM leads l
            JOIN lead_documents d ON d.lead_id = l.id
            WHERE l.agent_id = ? AND d.status = 'MISSING'
        """, (agent_id,))
        docs_missing = cur.fetchone()[0]
        conn.close()
        return {
            'total_leads': total,
            'by_stage': stages,
            'followups_today': followups,
            'followups_today_count': len(followups),
            'overdue_followups': overdue,
            'documents_missing': docs_missing
        }


crm = CRMEngine()