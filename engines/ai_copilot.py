"""
AI Glue Copilot — Tool calling based copilot for agents
"""
import os
import json
import core.db_compat as sqlite3
from groq import Groq
from engines.oie_tools import OIE_TOOLS, execute_oie_tool



TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_students",
            "description": "Search students by name, email, or country.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Name, email, or country to search"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_visa_cases",
            "description": "Get visa cases filtered by status or country.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "APPLIED, APPROVED, REJECTED, DOCS_PENDING, NOT_STARTED, UNDER_REVIEW"},
                    "country": {"type": "string", "description": "Country name"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_dashboard_stats",
            "description": "Overall stats: total visa cases, leads, and status breakdown.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pending_documents",
            "description": "List students whose documents are pending or missing.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_leads",
            "description": "Get agent's leads.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "NEW, CONTACTED, INTERESTED"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_today_leads",
            "description": "Get leads created today. Returns count and list of names.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_today_payments",
            "description": "Get payments received today. Returns total amount and list.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pending_payments",
            "description": "Get all pending payments for this agent.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_daily_summary",
            "description": "Get today's full summary: leads, payments, activities. Use when agent asks 'aaj ka summary do'.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]


def _execute_tool(name, args, agent_id):
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    result = None
    try:
        # --- SEARCH STUDENTS ---
        if name == "search_students":
            q = f"%{args.get('query', '')}%"
            cur.execute("""
                SELECT u.full_name, u.email, v.country, v.visa_type, v.status
                FROM users u
                LEFT JOIN visa_cases v ON v.candidate_id = u.id
                WHERE v.agent_id = ?
                  AND (u.full_name LIKE ? OR u.email LIKE ? OR v.country LIKE ?)
                LIMIT 15
            """, (agent_id, q, q, q))
            rows = cur.fetchall()
            result = [{"name": r[0], "email": r[1], "country": r[2],
                       "visa_type": r[3], "status": r[4]} for r in rows]

        # --- VISA CASES ---
        elif name == "get_visa_cases":
            clauses = ["v.agent_id = ?"]
            params = [agent_id]
            if args.get("status"):
                clauses.append("v.status = ?")
                params.append(args["status"])
            if args.get("country"):
                clauses.append("v.country = ?")
                params.append(args["country"])
            where = " AND ".join(clauses)
            cur.execute(f"""
                SELECT u.full_name, v.country, v.visa_type, v.status
                FROM visa_cases v JOIN users u ON u.id = v.candidate_id
                WHERE {where} LIMIT 50
            """, tuple(params))
            rows = cur.fetchall()
            result = [{"name": r[0], "country": r[1], "visa_type": r[2],
                       "status": r[3]} for r in rows]

        # --- DASHBOARD STATS ---
        elif name == "get_dashboard_stats":
            cur.execute("SELECT COUNT(*) FROM visa_cases WHERE agent_id = ?", (agent_id,))
            total = cur.fetchone()[0]
            cur.execute("""SELECT status, COUNT(*) FROM visa_cases
                           WHERE agent_id = ? GROUP BY status""", (agent_id,))
            by_status = {row[0]: row[1] for row in cur.fetchall()}
            cur.execute("SELECT COUNT(*) FROM leads WHERE agent_id = ?", (agent_id,))
            total_leads = cur.fetchone()[0]
            result = {"total_visa_cases": total, "by_status": by_status,
                      "total_leads": total_leads}

        # --- PENDING DOCUMENTS ---
        elif name == "get_pending_documents":
            cur.execute("""
                SELECT u.full_name, v.country, v.status
                FROM visa_cases v JOIN users u ON u.id = v.candidate_id
                WHERE v.agent_id = ?
                  AND v.status IN ('DOCS_PENDING', 'NOT_STARTED')
                LIMIT 30
            """, (agent_id,))
            rows = cur.fetchall()
            result = [{"name": r[0], "country": r[1], "status": r[2]} for r in rows]

        # --- LEADS ---
        elif name == "get_leads":
            clauses = ["agent_id = ?"]
            params = [agent_id]
            if args.get("status"):
                clauses.append("stage = ?")
                params.append(args["status"])
            where = " AND ".join(clauses)
            cur.execute(f"""SELECT student_name, email, stage FROM leads
                            WHERE {where} LIMIT 30""", tuple(params))
            rows = cur.fetchall()
            result = [{"name": r[0], "email": r[1], "stage": r[2]} for r in rows]

        # --- TODAY LEADS ---
        elif name == "get_today_leads":
            cur.execute("""
                SELECT student_name, email, country, course, stage
                FROM leads
                WHERE agent_id = ? AND DATE(created_at) = DATE('now')
                ORDER BY created_at DESC
            """, (agent_id,))
            rows = cur.fetchall()
            result = {
                "count": len(rows),
                "leads": [{"name": r[0], "email": r[1], "country": r[2],
                           "course": r[3], "stage": r[4]} for r in rows]
            }

        # --- TODAY PAYMENTS ---
        elif name == "get_today_payments":
            cur.execute("""
                SELECT amount, currency, status, payee_type, gateway_ref
                FROM payments
                WHERE payer_id = ? AND DATE(created_at) = DATE('now')
                ORDER BY created_at DESC
            """, (agent_id,))
            rows = cur.fetchall()
            total = sum(float(r[0] or 0) for r in rows if r[2] == 'SUCCESS')
            result = {
                "total_received": total,
                "currency": rows[0][1] if rows else "INR",
                "count": len(rows),
                "payments": [{"amount": float(r[0] or 0), "currency": r[1],
                              "status": r[2], "type": r[3],
                              "ref": r[4]} for r in rows]
            }

        # --- PENDING PAYMENTS ---
        elif name == "get_pending_payments":
            cur.execute("""
                SELECT amount, currency, status, payee_type
                FROM payments
                WHERE payer_id = ? AND status IN ('PENDING', 'PROCESSING', 'INITIATED')
                ORDER BY created_at DESC
                LIMIT 50
            """, (agent_id,))
            rows = cur.fetchall()
            total = sum(float(r[0] or 0) for r in rows)
            result = {
                "total_pending": total,
                "currency": rows[0][1] if rows else "INR",
                "count": len(rows),
                "pending": [{"amount": float(r[0] or 0), "currency": r[1],
                             "status": r[2], "type": r[3]} for r in rows]
            }

        # --- DAILY SUMMARY ---
        elif name == "get_daily_summary":
            cur.execute("""SELECT COUNT(*) FROM leads
                           WHERE agent_id = ? AND DATE(created_at) = DATE('now')""",
                        (agent_id,))
            today_leads = cur.fetchone()[0]

            cur.execute("""SELECT COALESCE(SUM(amount), 0) FROM payments
                           WHERE payer_id = ? AND DATE(created_at) = DATE('now')
                           AND status = 'SUCCESS'""", (agent_id,))
            today_payment = float(cur.fetchone()[0] or 0)

            cur.execute("""SELECT COALESCE(SUM(amount), 0), COUNT(*) FROM payments
                           WHERE payer_id = ? AND status IN ('PENDING', 'PROCESSING', 'INITIATED')""",
                        (agent_id,))
            row = cur.fetchone()
            pending_amount = float(row[0] or 0)
            pending_count = row[1]

            cur.execute("""SELECT COUNT(*) FROM visa_cases
                           WHERE agent_id = ?
                           AND DATE(COALESCE(last_checked_at, created_at)) = DATE('now')""",
                        (agent_id,))
            visa_updates = cur.fetchone()[0]

            cur.execute("""SELECT COUNT(*) FROM leads
                           WHERE agent_id = ? AND stage NOT IN ('LOST', 'CONVERTED')""",
                        (agent_id,))
            active_leads = cur.fetchone()[0]

            result = {
                "date": "today",
                "new_leads_today": today_leads,
                "payments_received_today": today_payment,
                "pending_payment_amount": pending_amount,
                "pending_payment_count": pending_count,
                "visa_updates_today": visa_updates,
                "active_leads_total": active_leads
            }

        else:
            result = {"error": f"Unknown tool: {name}"}

    except Exception as e:
        result = {"error": str(e)}
    finally:
        conn.close()
    return result


def ask_copilot(query, agent_id):
    api_key = os.getenv('GROQ_API_KEY', '')
    if not api_key:
        return {"answer": "GROQ_API_KEY set nahi hai.", "tools_used": []}

    client = Groq(api_key=api_key)

    system_prompt = """You are AI Glue Copilot — assistant for study-abroad agents, students, and job seekers.

Rules:
1. Use tools to fetch REAL data. Never make up information.
2. If a tool returns empty, tell the agent honestly.
3. Answer in Hinglish (Hindi + English mix) — friendly and concise.
4. When listing students, format them cleanly.
5. For counts/stats, use get_dashboard_stats.
6. If agent asks about a specific student, use search_students first.
7. For "aaj ka summary" or daily report, use get_daily_summary.
8. For "aaj ke leads", use get_today_leads.
9. For "aaj ka payment", use get_today_payments.
10. For "pending payment", use get_pending_payments."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    tools_used = []

    for _ in range(5):
        try:
           response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                tools=TOOLS + OIE_TOOLS,
                tool_choice="auto",
                temperature=0.2,
                max_tokens=800,
            )
        except Exception as e:
            return {"answer": f"AI Error: {str(e)}", "tools_used": tools_used}

        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return {"answer": msg.content, "tools_used": tools_used}

        for tc in msg.tool_calls:
            tool_name = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
            except Exception:
                args = {}

            # Try OIE tools first, then fallback to old
            oie_tool_names = [t["function"]["name"] for t in OIE_TOOLS]
            if tool_name in oie_tool_names:
                tool_result = execute_oie_tool(tool_name, args)
            else:
                tool_result = _execute_tool(tool_name, args, agent_id)
            tools_used.append({"tool": tool_name, "args": args})

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(tool_result, default=str)
            })

    return {"answer": "Sorry, jawab nahi de paaya. Dobara try karein.",
            "tools_used": tools_used}