# AI GLUE — COMPLETE SCOPE MAP
# Service → Sub-Service → Endpoint → Page → Status

## 🎯 LEGEND
✅ = Live (endpoint + page both)
🟡 = Backend ready, page missing
🔴 = Bilkul naya banana hai

---

## 📁 AGENT — LEADS & CRM

| Sub-Service | Endpoint | Frontend Page | Status |
|-------------|----------|---------------|--------|
| Leads (CRM) | GET/POST/PUT /agent/leads | /agent/leads | ✅ |
| Lead Detail | GET /agent/leads/{id} | /agent/leads/:id | ✅ |
| Stage Change | PATCH /agent/leads/{id}/stage | — | ✅ |
| Notes | POST /agent/leads/{id}/note | — | ✅ |
| Follow-ups | GET /agent/followups | /agent/followups | ✅ |
| Applications | GET /agent/applications | /agent/applications | ✅ |
| Candidates | GET /agent/candidates | /agent-new/candidates | ✅ |
| Funnel | GET /agent/funnel | /agent-new/funnel | ✅ |
| Convert Lead → Student | POST /agent/leads/{id}/convert | — | 🟡 (backend ready, UI missing) |
| Team Assignment | — | — | 🔴 |

---

## 📁 AGENT — DOCUMENTS

| Sub-Service | Endpoint | Frontend Page | Status |
|-------------|----------|---------------|--------|
| Document Upload | POST /agent/leads/{id}/documents/upload | LeadDetail | ✅ |
| Document Status | PATCH /agent/documents/{id}/status | LeadDetail | ✅ |
| AI Verify | POST /agent/documents/{id}/ai-verify | LeadDetail | ✅ |
| Document Checker | GET /agent/leads/{id}/document-check | LeadDetail | ✅ |
| Country Requirements | GET /agent/document-checker/countries | — | ✅ |
| Document Vault (all) | — | /student-new/documents | 🟡 |
| Document Expiry Alerts | — | — | 🔴 |

---

## 📁 AGENT — VISA & OFFERS

| Sub-Service | Endpoint | Frontend Page | Status |
|-------------|----------|---------------|--------|
| Visa Tracking | GET /visa/cases | /jobseeker-new/visa | 🟡 |
| Visa Detail | GET /visa/{id} | — | 🟡 |
| Visa Appointments | — | — | 🟡 (schema ready) |
| Visa Rules | — | — | 🟡 (schema ready) |
| Offers | GET /offers | /jobseeker-new/offers | 🟡 |
| Offer Create | POST /offers/create | — | 🟡 |
| Offer Accept | POST /offers/accept | — | 🟡 |
| Contracts | GET /contracts | /employer-new/contracts | 🟡 |

---

## 📁 AGENT — AI SERVICES

| Sub-Service | Endpoint | Frontend Page | Status |
|-------------|----------|---------------|--------|
| AI Orchestration | GET /admin/orchestration | /admin/orchestration | 🟡 |
| Match Job Seeker | POST /admin/match/job-seeker | /admin/match/job-seeker | 🟡 |
| Match Student | POST /admin/match/student | /admin/match/student | 🟡 |
| Match Company | POST /admin/match/company | /admin/match/company | 🟡 |
| AI Copilot | — | — | 🔴 |
| AI Voice Agent | — | — | 🔴 |
| Auto Follow-up AI | — | — | 🔴 |
| AI Chatbot | — | — | 🔴 |

---

## 📁 AGENT — MONEY & GRADE

| Sub-Service | Endpoint | Frontend Page | Status |
|-------------|----------|---------------|--------|
| My Commission | GET /reconciliation/summary | /agent-new/commission | ✅ |
| My Grade | GET /agent/grades/me | /agent/grades | ✅ |
| Grade Leaderboard | GET /agent/grades/leaderboard | /agent/grades | ✅ |
| Referral Link | GET /referral/link/{userId} | /agent-new/referral | ✅ |
| Referral Stats | GET /referral/stats/{userId} | — | 🟡 |
| Deal History | GET /deals/my/deals | — | 🟡 |
| Commission History | — | — | 🟡 |
| Payout Tracking | — | — | 🔴 |

---

## 📁 AGENT — TEAM

| Sub-Service | Endpoint | Frontend Page | Status |
|-------------|----------|---------------|--------|
| My Profile | GET /profile/me | /profile | ✅ |
| Subscription | GET /subscription/{userId} | /my-subscription | 🟡 |
| Sub-Agent Management | — | — | 🔴 |
| Team Performance | — | — | 🔴 |
| Counsellor Assignment | — | — | 🔴 |
| White Label | — | — | 🔴 |

---

## 📁 AGENT — COMMUNICATION

| Sub-Service | Endpoint | Frontend Page | Status |
|-------------|----------|---------------|--------|
| Messages (In-App) | GET /messages | /messages | ✅ |
| Email Composer | POST /communication/messages/send | /admin/email | 🟡 |
| WhatsApp Integration | — | — | 🔴 |
| SMS Gateway | — | — | 🔴 |
| Templates Library | — | — | 🔴 |
| Communication History | — | — | 🔴 |
| Daily Digest (8 PM) | — | — | 🔴 |

---

## 📁 AGENT — EXPLORE

| Sub-Service | Endpoint | Frontend Page | Status |
|-------------|----------|---------------|--------|
| Study Abroad | GET /education/countries | /study-abroad | ✅ |
| Work Abroad | GET /search/opportunities | /work-abroad | ✅ |
| Trust Directory | GET /public/directory | /trust | ✅ |
| University Search | GET /education/universities | — | 🟡 |
| Course Search | GET /education/courses | — | 🟡 |

---

## 📁 BROKER

| Sub-Service | Endpoint | Frontend Page | Status |
|-------------|----------|---------------|--------|
| Dashboard | GET /broker/dashboard/{id} | /broker | ✅ |
| Agent Leaderboard | GET /agent/grades/leaderboard | /broker-new/leaderboard | ✅ |
| Commission | GET /reconciliation/summary | /broker-new/commission | ✅ |
| Clients | GET /broker/clients | /broker-new/clients | ✅ |
| Sub-Agent Management | — | — | 🔴 |
| Team Performance | — | — | 🔴 |
| Revenue Share | — | — | 🔴 |

---

## 📊 SUMMARY — TOTAL SCOPE

| Status | Count | % |
|--------|-------|---|
| ✅ Live | 24 | 38% |
| 🟡 Backend ready, UI missing | 24 | 38% |
| 🔴 Bilkul naya | 15 | 24% |
| **TOTAL** | **63** | **100%** |

---

## 🎯 PRIORITY — Next Features

### Week 1 (High ROI)
1. **Visa Tracking Page** — /jobseeker-new/visa (backend ready)
2. **Offers Management** — /jobseeker-new/offers (backend ready)
3. **Team Management** — sub-agent add/assign (schema ready)
4. **Notifications Page** — bell click → full page
5. **AI Copilot** — chat with data

### Week 2 (Automation)
6. **WhatsApp Integration** — Twilio/Meta API
7. **Email Templates** — auto-send
8. **Daily Digest** — 8 PM summary
9. **Student 360** — aggregate profile
10. **Analytics Dashboard** — business metrics

### Week 3 (Advanced)
11. **AI Voice Agent** — ElevenLabs + Twilio
12. **AI Chatbot** — website + WhatsApp
13. **Auto University Apply** — one-click
14. **White Label** — custom domains
15. **Commission Payout** — automated

---

## 🎯 DATABASE TABLES — FULL INVENTORY (51 tables)

### Core (10)
- tenants, users, user_roles, organizations, organization_members
- countries, universities, cities, campuses, departments

### Education (4)
- courses, intake_seats, opportunities, applications

### Flow (8)
- offers, contracts, payments, visa_cases, visa_appointments, visa_rules, documents, evidence

### Trust (6)
- source_registry, trust_scores, ttl_records, fraud_flags, audit_events, constitution_items

### Business (8)
- deals, commission_events, referral_events, rewards
- subscription_plans, user_subscriptions, scheduled_jobs, connectors

### Content (5)
- cases, application_timeline, tasks, candidate_profiles, candidate_consent

### System (10)
- notifications, messages, contact_shares, password_reset_tokens
- ai_cost_logs, workflow_states, student_life, partner_registry
- agent_grades, grade_history

### Custom (SQLite only)
- leads, lead_documents, lead_activities