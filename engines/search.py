# ============================================================
# AI GLUE v8.0 — SEARCH ENGINE (Case-Insensitive + Partial Match)
# ============================================================

from sqlalchemy import or_, func
from core.database import db, Opportunity
from typing import Optional


class SearchEngine:

    @staticmethod
    def search_opportunities(q: str = None, filters: dict = None, session=None):
        """Search opportunities with case-insensitive partial matching."""
        if session is None:
            session = db.get_session()

        try:
            query = session.query(Opportunity)

            # Text Search — Case Insensitive, Partial Match
            if q:
                q_lower = f"%{q.lower()}%"
                query = query.filter(
                    or_(
                        func.lower(Opportunity.title).like(q_lower),
                        func.lower(Opportunity.description).like(q_lower),
                    )
                )

            # Filters
            if filters:
                if filters.get('type'):
                    query = query.filter(Opportunity.type == filters['type'])
                if filters.get('status'):
                    query = query.filter(Opportunity.status == filters['status'])
                if filters.get('organization_id'):
                    query = query.filter(Opportunity.organization_id == filters['organization_id'])

            # Sort by newest
            query = query.order_by(Opportunity.created_at.desc())

            # Limit
            limit = filters.get('limit', 50) if filters else 50
            results = query.limit(limit).all()

            return results
        finally:
            session.close()


# Singleton
search = SearchEngine()