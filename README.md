# AI Glue — Human Opportunity Operating System

## Features
- Multi-Tenant Manpower + Education Platform
- RBAC, Audit, Security, MFA, Workflow
- Visa, Payment, Notification, Referral

## Setup
1. Copy `.env.example` to `.env` and fill values.
2. Run `pip install -r requirements.txt`
3. Run `python scripts/migrate_db.py`
4. Run `uvicorn main:app --reload`

## Deploy
- Backend: Render (render.yaml)
- Frontend: Vercel (frontend/)

## Testing
- `pytest tests/`